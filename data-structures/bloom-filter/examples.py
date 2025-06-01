"""
Real-world examples demonstrating Bloom Filter applications.

This file contains practical examples showing how Bloom filters can be used
in various scenarios like web caching, database optimization, network security,
and distributed systems.
"""

import random
import time
import string
from bloomfilter import BloomFilter


def example_web_cache_optimization():
    """
    Example: Web Cache Optimization
    
    Demonstrates how Bloom filters can prevent expensive cache misses
    by quickly checking if a URL might be cached.
    """
    print("=" * 60)
    print("EXAMPLE 1: Web Cache Optimization")
    print("=" * 60)
    
    # Simulate a web cache with 10,000 cached URLs
    cache_capacity = 10000
    cache_bloom = BloomFilter(capacity=cache_capacity, error_rate=0.01)
    
    # Simulate cached URLs
    cached_urls = []
    for i in range(cache_capacity):
        url = f"https://example.com/page_{i}"
        cached_urls.append(url)
        cache_bloom.add(url)
    
    print(f"Simulated web cache with {cache_capacity:,} URLs")
    print(f"Bloom filter memory usage: {cache_bloom.get_statistics()['configuration']['memory_bytes']:,} bytes")
    
    # Compare memory usage
    estimated_url_memory = cache_capacity * 50  # Assume 50 bytes per URL
    memory_savings = (1 - cache_bloom.get_statistics()['configuration']['memory_bytes'] / estimated_url_memory) * 100
    print(f"Memory savings vs storing URLs: {memory_savings:.1f}%")
    
    # Simulate web requests
    print(f"\nSimulating web requests:")
    
    cache_hits = 0
    cache_misses = 0
    false_positives = 0
    bloom_checks = 0
    
    # Test requests
    for i in range(1000):
        if i < 500:
            # 50% requests for cached content
            url = random.choice(cached_urls)
            expected_in_cache = True
        else:
            # 50% requests for new content
            url = f"https://example.com/new_page_{i}"
            expected_in_cache = False
        
        bloom_checks += 1
        bloom_result = cache_bloom.query(url)
        
        if bloom_result['result'] == "POSSIBLY_IN_SET":
            if expected_in_cache:
                cache_hits += 1
            else:
                false_positives += 1
                # In real system, this would trigger expensive cache lookup
        else:
            cache_misses += 1
            # Definitely not in cache, can skip expensive lookup
    
    print(f"  Total requests: 1000")
    print(f"  Bloom filter checks: {bloom_checks}")
    print(f"  Cache hits avoided: {cache_misses}")
    print(f"  False positives: {false_positives}")
    print(f"  False positive rate: {false_positives/bloom_checks:.3f}")
    print(f"  Expensive lookups saved: {cache_misses - false_positives}")


def example_database_query_optimization():
    """
    Example: Database Query Optimization
    
    Shows how Bloom filters can optimize database joins by filtering
    out rows that definitely won't match.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Database Query Optimization")
    print("=" * 60)
    
    # Simulate two database tables for a join operation
    table_a_size = 100000
    table_b_size = 50000
    join_selectivity = 0.1  # 10% of rows will actually join
    
    print(f"Simulating database join:")
    print(f"  Table A: {table_a_size:,} rows")
    print(f"  Table B: {table_b_size:,} rows")
    print(f"  Expected join selectivity: {join_selectivity:.1%}")
    
    # Create Bloom filter for smaller table (Table B)
    bloom_filter = BloomFilter(capacity=table_b_size, error_rate=0.01)
    
    # Simulate Table B keys
    table_b_keys = set()
    for i in range(table_b_size):
        # Create some overlap with Table A for realistic join
        if random.random() < join_selectivity:
            key = f"key_{i % (table_a_size // 10)}"  # Create overlapping keys
        else:
            key = f"b_key_{i}"
        table_b_keys.add(key)
        bloom_filter.add(key)
    
    print(f"\nBloom filter for Table B:")
    stats = bloom_filter.get_statistics()
    print(f"  Memory usage: {stats['configuration']['memory_bytes']:,} bytes")
    print(f"  Theoretical false positive rate: {stats['performance']['theoretical_fp_rate']:.4f}")
    
    # Simulate join operation with Bloom filter optimization
    start_time = time.time()
    
    bloom_filtered_rows = 0
    potential_matches = 0
    actual_matches = 0
    false_positives = 0
    
    # Process Table A rows
    for i in range(table_a_size):
        table_a_key = f"key_{i}"
        
        # Check Bloom filter first
        bloom_result = bloom_filter.query(table_a_key)
        
        if bloom_result['result'] == "DEFINITELY_NOT_IN_SET":
            bloom_filtered_rows += 1
            # Skip expensive database lookup
        else:
            potential_matches += 1
            # In real system, would perform expensive join lookup
            if table_a_key in table_b_keys:
                actual_matches += 1
            else:
                false_positives += 1
    
    processing_time = time.time() - start_time
    
    print(f"\nJoin optimization results:")
    print(f"  Processing time: {processing_time:.3f} seconds")
    print(f"  Rows filtered by Bloom filter: {bloom_filtered_rows:,}")
    print(f"  Potential matches: {potential_matches:,}")
    print(f"  Actual matches: {actual_matches:,}")
    print(f"  False positives: {false_positives:,}")
    print(f"  Rows saved from expensive lookup: {bloom_filtered_rows:,}")
    print(f"  Join efficiency improvement: {bloom_filtered_rows/table_a_size:.1%}")


def example_network_security_blacklist():
    """
    Example: Network Security - IP Blacklist
    
    Demonstrates using Bloom filters for fast IP address blacklist checking
    in network security applications.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Network Security - IP Blacklist")
    print("=" * 60)
    
    # Simulate a blacklist with malicious IP addresses
    blacklist_size = 1000000  # 1M malicious IPs
    blacklist_bloom = BloomFilter(capacity=blacklist_size, error_rate=0.001)  # Low error rate for security
    
    print(f"Creating IP blacklist with {blacklist_size:,} malicious IPs")
    
    # Generate blacklisted IPs
    blacklisted_ips = set()
    for i in range(blacklist_size):
        # Generate realistic IP addresses
        ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"
        blacklisted_ips.add(ip)
        blacklist_bloom.add(ip)
    
    stats = blacklist_bloom.get_statistics()
    print(f"Bloom filter configuration:")
    print(f"  Memory usage: {stats['configuration']['memory_bytes']/1024:.1f} KB")
    print(f"  Theoretical false positive rate: {stats['performance']['theoretical_fp_rate']:.6f}")
    print(f"  Hash functions: {stats['configuration']['num_hash_functions']}")
    
    # Simulate network traffic analysis
    print(f"\nAnalyzing network traffic:")
    
    legitimate_traffic = 0
    blocked_traffic = 0
    false_positive_blocks = 0
    total_packets = 100000
    
    start_time = time.time()
    
    for i in range(total_packets):
        # Simulate network packet with source IP
        if random.random() < 0.001:  # 0.1% malicious traffic
            source_ip = random.choice(list(blacklisted_ips))
            is_actually_malicious = True
        else:
            # Generate legitimate IP
            source_ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"
            is_actually_malicious = source_ip in blacklisted_ips
        
        # Check against Bloom filter
        bloom_result = blacklist_bloom.query(source_ip)
        
        if bloom_result['result'] == "POSSIBLY_IN_SET":
            blocked_traffic += 1
            if not is_actually_malicious:
                false_positive_blocks += 1
        else:
            legitimate_traffic += 1
    
    processing_time = time.time() - start_time
    
    print(f"  Packets analyzed: {total_packets:,}")
    print(f"  Processing time: {processing_time:.3f} seconds")
    print(f"  Packets per second: {total_packets/processing_time:,.0f}")
    print(f"  Legitimate traffic: {legitimate_traffic:,}")
    print(f"  Blocked traffic: {blocked_traffic:,}")
    print(f"  False positive blocks: {false_positive_blocks:,}")
    print(f"  False positive rate: {false_positive_blocks/total_packets:.6f}")
    
    # Compare with traditional approach
    traditional_memory = blacklist_size * 15  # Assume 15 bytes per IP string
    print(f"\nMemory comparison:")
    print(f"  Bloom filter: {stats['configuration']['memory_bytes']/1024:.1f} KB")
    print(f"  Traditional set: {traditional_memory/1024:.1f} KB")
    print(f"  Memory savings: {(1 - stats['configuration']['memory_bytes']/traditional_memory)*100:.1f}%")


def example_distributed_duplicate_detection():
    """
    Example: Distributed Systems - Duplicate Detection
    
    Shows how Bloom filters can detect duplicates across distributed systems
    before expensive operations.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Distributed Duplicate Detection")
    print("=" * 60)
    
    # Simulate distributed system with multiple nodes
    num_nodes = 5
    elements_per_node = 20000
    
    print(f"Simulating distributed system with {num_nodes} nodes")
    print(f"Each node processes ~{elements_per_node:,} elements")
    
    # Each node maintains its own Bloom filter
    node_filters = []
    node_data = []
    
    for node_id in range(num_nodes):
        bf = BloomFilter(capacity=elements_per_node, error_rate=0.01)
        node_filters.append(bf)
        
        # Generate data for this node (with some overlap between nodes)
        node_elements = set()
        for i in range(elements_per_node):
            # Create some overlap between nodes for realistic duplicate detection
            if random.random() < 0.1:  # 10% overlap
                element = f"shared_element_{random.randint(1, 1000)}"
            else:
                element = f"node_{node_id}_element_{i}"
            
            node_elements.add(element)
            bf.add(element)
        
        node_data.append(node_elements)
        print(f"  Node {node_id}: {len(node_elements):,} unique elements")
    
    # Simulate checking for duplicates before expensive operations
    print(f"\nTesting duplicate detection across nodes:")
    
    total_checks = 0
    bloom_filtered = 0
    actual_duplicates = 0
    false_positives = 0
    
    # Test elements from each node against other nodes
    for source_node in range(num_nodes):
        elements_to_test = random.sample(list(node_data[source_node]), 1000)
        
        for element in elements_to_test:
            total_checks += 1
            
            # Check against all other nodes' Bloom filters
            found_in_bloom = False
            actually_duplicate = False
            
            for target_node in range(num_nodes):
                if target_node == source_node:
                    continue
                    
                bloom_result = node_filters[target_node].query(element)
                if bloom_result['result'] == "POSSIBLY_IN_SET":
                    found_in_bloom = True
                    if element in node_data[target_node]:
                        actually_duplicate = True
                    break
            
            if found_in_bloom:
                if actually_duplicate:
                    actual_duplicates += 1
                else:
                    false_positives += 1
            else:
                bloom_filtered += 1
    
    print(f"  Total duplicate checks: {total_checks:,}")
    print(f"  Filtered by Bloom filters: {bloom_filtered:,}")
    print(f"  Actual duplicates found: {actual_duplicates:,}")
    print(f"  False positives: {false_positives:,}")
    print(f"  Expensive operations avoided: {bloom_filtered:,}")
    print(f"  Efficiency improvement: {bloom_filtered/total_checks:.1%}")
    
    # Show memory usage
    total_memory = sum(bf.get_statistics()['configuration']['memory_bytes'] for bf in node_filters)
    print(f"\nTotal Bloom filter memory across all nodes: {total_memory/1024:.1f} KB")


def example_content_recommendation():
    """
    Example: Content Recommendation System
    
    Demonstrates using Bloom filters to quickly filter content
    a user has already seen before expensive recommendation calculations.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Content Recommendation System")
    print("=" * 60)
    
    # Simulate user interaction history
    num_users = 10000
    content_items = 1000000
    avg_items_per_user = 500
    
    print(f"Simulating recommendation system:")
    print(f"  Users: {num_users:,}")
    print(f"  Content items: {content_items:,}")
    print(f"  Average items viewed per user: {avg_items_per_user}")
    
    # Create Bloom filter for a specific user's viewed content
    user_id = 12345
    user_bloom = BloomFilter(capacity=avg_items_per_user * 2, error_rate=0.01)
    
    # Simulate user's viewing history
    viewed_content = set()
    for _ in range(avg_items_per_user):
        content_id = f"content_{random.randint(1, content_items)}"
        viewed_content.add(content_id)
        user_bloom.add(content_id)
    
    print(f"\nUser {user_id} profile:")
    print(f"  Content items viewed: {len(viewed_content):,}")
    stats = user_bloom.get_statistics()
    print(f"  Bloom filter memory: {stats['configuration']['memory_bytes']} bytes")
    print(f"  Fill ratio: {stats['performance']['fill_ratio']:.3f}")
    
    # Simulate recommendation generation
    print(f"\nGenerating recommendations:")
    
    candidate_items = 10000  # Items to consider for recommendation
    filtered_by_bloom = 0
    potential_recommendations = 0
    false_positive_filters = 0
    
    start_time = time.time()
    
    recommendations = []
    for _ in range(candidate_items):
        content_id = f"content_{random.randint(1, content_items)}"
        
        # Quick Bloom filter check
        bloom_result = user_bloom.query(content_id)
        
        if bloom_result['result'] == "DEFINITELY_NOT_IN_SET":
            # User definitely hasn't seen this, safe to recommend
            filtered_by_bloom += 1
            # In real system, would run expensive ML recommendation scoring
            recommendations.append(content_id)
        else:
            # User might have seen this
            potential_recommendations += 1
            if content_id not in viewed_content:
                # False positive - would be filtered unnecessarily
                false_positive_filters += 1
                recommendations.append(content_id)
    
    processing_time = time.time() - start_time
    
    print(f"  Candidate items processed: {candidate_items:,}")
    print(f"  Processing time: {processing_time:.3f} seconds")
    print(f"  Items filtered by Bloom filter: {filtered_by_bloom:,}")
    print(f"  Items requiring expensive check: {potential_recommendations:,}")
    print(f"  False positive filters: {false_positive_filters:,}")
    print(f"  Final recommendations: {len(recommendations):,}")
    print(f"  Computational savings: {filtered_by_bloom/candidate_items:.1%}")


def main():
    """Run all examples."""
    print("Bloom Filter Real-World Applications")
    print("=" * 60)
    print("This script demonstrates practical applications of Bloom filters")
    print("in web caching, databases, security, distributed systems,")
    print("and recommendation systems.")
    print()
    
    # Run all examples
    example_web_cache_optimization()
    example_database_query_optimization()
    example_network_security_blacklist()
    example_distributed_duplicate_detection()
    example_content_recommendation()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print("\nKey Benefits Demonstrated:")
    print("1. Massive memory savings (90%+ in many cases)")
    print("2. Fast membership testing (O(k) per query)")
    print("3. No false negatives (perfect recall)")
    print("4. Tunable false positive rates")
    print("5. Excellent for pre-filtering expensive operations")


if __name__ == "__main__":
    main() 