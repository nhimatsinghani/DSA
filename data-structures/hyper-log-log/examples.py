"""
Real-world examples demonstrating HyperLogLog usage.

This file contains practical examples showing how HyperLogLog can be used
in various scenarios like web analytics, database query optimization,
and distributed system cardinality estimation.
"""

import random
import time
from datetime import datetime, timedelta
from hyperloglog import HyperLogLog


def example_web_analytics():
    """
    Example: Web Analytics - Unique Visitor Counting
    
    Demonstrates how HyperLogLog can be used to count unique visitors
    to a website with minimal memory usage.
    """
    print("=" * 60)
    print("EXAMPLE 1: Web Analytics - Unique Visitor Counting")
    print("=" * 60)
    
    # Simulate a high-traffic website
    hll_daily = HyperLogLog(precision=12)  # For daily unique visitors
    hll_weekly = HyperLogLog(precision=12)  # For weekly unique visitors
    
    # Simulate user IDs (in real world, these would be user cookies/IDs)
    total_page_views = 100000
    unique_users = 25000
    
    print(f"Simulating {total_page_views:,} page views from {unique_users:,} unique users...")
    
    # Generate realistic traffic patterns
    user_ids = [f"user_{i:06d}" for i in range(unique_users)]
    
    start_time = time.time()
    
    # Simulate page views (some users visit multiple times)
    for _ in range(total_page_views):
        # 80% of traffic comes from 20% of users (Pareto principle)
        if random.random() < 0.8:
            user_id = random.choice(user_ids[:int(unique_users * 0.2)])
        else:
            user_id = random.choice(user_ids)
        
        hll_daily.add(user_id)
        hll_weekly.add(user_id)
    
    processing_time = time.time() - start_time
    
    # Get estimates
    daily_estimate = hll_daily.estimate_cardinality()
    weekly_estimate = hll_weekly.estimate_cardinality()
    
    print(f"\nProcessing completed in {processing_time:.2f} seconds")
    print(f"\nDaily Unique Visitors:")
    print(f"  Actual: {unique_users:,}")
    print(f"  Estimated: {daily_estimate['estimated_cardinality']:,}")
    print(f"  Error: {abs(daily_estimate['estimated_cardinality'] - unique_users) / unique_users:.2%}")
    print(f"  Memory usage: {hll_daily.get_bucket_analysis()['memory_usage_bytes']:,} bytes")
    
    # Compare with exact counting (simulation)
    exact_memory = unique_users * 20  # Assume 20 bytes per user ID
    print(f"  Exact counting would need: {exact_memory:,} bytes")
    print(f"  Memory savings: {(1 - hll_daily.get_bucket_analysis()['memory_usage_bytes'] / exact_memory):.1%}")


def example_database_optimization():
    """
    Example: Database Query Optimization
    
    Shows how HyperLogLog can help database optimizers estimate
    the number of distinct values in a column.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Database Query Optimization")
    print("=" * 60)
    
    # Simulate a database table with different column cardinalities
    tables = {
        'users': {
            'user_id': HyperLogLog(precision=14),      # High cardinality
            'country': HyperLogLog(precision=8),       # Low cardinality 
            'age': HyperLogLog(precision=10),          # Medium cardinality
            'email_domain': HyperLogLog(precision=10)  # Medium cardinality
        }
    }
    
    # Simulate database records
    countries = ['US', 'UK', 'CA', 'DE', 'FR', 'JP', 'AU', 'BR', 'IN', 'CN']
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'company.com', 'university.edu']
    
    num_records = 1000000
    print(f"Analyzing {num_records:,} database records...")
    
    start_time = time.time()
    
    for i in range(num_records):
        user_id = f"user_{i:07d}"
        country = random.choice(countries)
        age = random.randint(18, 80)
        email_domain = random.choice(domains) if random.random() < 0.7 else f"domain_{random.randint(1, 1000)}.com"
        
        tables['users']['user_id'].add(user_id)
        tables['users']['country'].add(country)
        tables['users']['age'].add(age)
        tables['users']['email_domain'].add(email_domain)
    
    processing_time = time.time() - start_time
    
    print(f"Analysis completed in {processing_time:.2f} seconds")
    print(f"\nCardinality estimates for 'users' table:")
    print(f"{'Column':<15} {'Cardinality':<12} {'Memory (bytes)':<15} {'Selectivity':<12}")
    print("-" * 60)
    
    for column, hll in tables['users'].items():
        estimate = hll.estimate_cardinality()
        memory_usage = hll.get_bucket_analysis()['memory_usage_bytes']
        selectivity = estimate['estimated_cardinality'] / num_records
        
        print(f"{column:<15} {estimate['estimated_cardinality']:<12,} {memory_usage:<15,} {selectivity:<12.4f}")
    
    print(f"\nQuery optimization insights:")
    print(f"- user_id: Perfect for primary key (high cardinality)")
    print(f"- country: Good for partitioning (low cardinality)")
    print(f"- age: Suitable for range queries (medium cardinality)")
    print(f"- email_domain: Consider indexing (medium cardinality)")


def example_distributed_systems():
    """
    Example: Distributed Systems - Merging Estimates
    
    Demonstrates how HyperLogLog can be used in distributed systems
    to combine cardinality estimates from multiple nodes.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Distributed Systems - Merging Estimates")
    print("=" * 60)
    
    # Simulate multiple servers/nodes
    num_nodes = 5
    precision = 12
    
    print(f"Simulating {num_nodes} distributed nodes...")
    
    # Each node maintains its own HyperLogLog
    node_hlls = [HyperLogLog(precision=precision) for _ in range(num_nodes)]
    
    # Simulate data distribution across nodes
    total_unique_elements = 50000
    all_elements = [f"element_{i:06d}" for i in range(total_unique_elements)]
    
    # Distribute elements across nodes (with some overlap)
    elements_per_node = total_unique_elements // 2  # Overlap for realistic scenario
    
    for node_id, hll in enumerate(node_hlls):
        print(f"Processing node {node_id + 1}...")
        
        # Each node gets a random subset of elements
        node_elements = random.sample(all_elements, elements_per_node)
        
        for element in node_elements:
            hll.add(element)
        
        estimate = hll.estimate_cardinality()
        print(f"  Node {node_id + 1} local estimate: {estimate['estimated_cardinality']:,}")
    
    # Merge all node estimates
    print(f"\nMerging estimates from all nodes...")
    merged_hll = node_hlls[0]
    
    for i in range(1, num_nodes):
        merged_hll = merged_hll.merge(node_hlls[i])
    
    final_estimate = merged_hll.estimate_cardinality()
    
    print(f"\nResults:")
    print(f"  Actual unique elements: {total_unique_elements:,}")
    print(f"  Merged estimate: {final_estimate['estimated_cardinality']:,}")
    print(f"  Error: {abs(final_estimate['estimated_cardinality'] - total_unique_elements) / total_unique_elements:.2%}")
    print(f"  Total memory across all nodes: {num_nodes * merged_hll.get_bucket_analysis()['memory_usage_bytes']:,} bytes")


def example_streaming_data():
    """
    Example: Streaming Data Analysis
    
    Shows HyperLogLog performance with continuous data streams.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Streaming Data Analysis")
    print("=" * 60)
    
    # Simulate real-time data stream
    hll_stream = HyperLogLog(precision=12)
    
    # Simulate different types of streaming events
    event_types = ['page_view', 'login', 'purchase', 'search', 'click']
    
    print("Simulating real-time data stream...")
    print("Timestamp        | Event Type | Unique Users | Memory Usage")
    print("-" * 65)
    
    batch_size = 10000
    num_batches = 10
    
    for batch in range(num_batches):
        start_time = time.time()
        
        # Process a batch of events
        for _ in range(batch_size):
            user_id = f"user_{random.randint(1, 20000):06d}"  # 20K possible users
            event_type = random.choice(event_types)
            
            # In real systems, you'd stream actual events
            event_data = f"{user_id}_{event_type}"
            hll_stream.add(user_id)  # Count unique users
        
        processing_time = time.time() - start_time
        estimate = hll_stream.estimate_cardinality()
        memory_kb = hll_stream.get_bucket_analysis()['memory_usage_bytes'] / 1024
        
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"{timestamp} | Batch {batch+1:2d}   | {estimate['estimated_cardinality']:10,} | {memory_kb:8.2f} KB")
        
        time.sleep(0.1)  # Simulate real-time delay
    
    print(f"\nStream processing completed!")
    print(f"Final unique user estimate: {estimate['estimated_cardinality']:,}")


def example_accuracy_analysis():
    """
    Example: Accuracy Analysis Across Different Scenarios
    
    Comprehensive analysis of HyperLogLog accuracy under various conditions.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Accuracy Analysis")
    print("=" * 60)
    
    # Test different scenarios
    scenarios = [
        {"name": "Small Dataset", "size": 1000, "precision": 10},
        {"name": "Medium Dataset", "size": 50000, "precision": 12},
        {"name": "Large Dataset", "size": 1000000, "precision": 14},
        {"name": "Very Large Dataset", "size": 10000000, "precision": 16}
    ]
    
    print(f"{'Scenario':<20} {'Size':<12} {'Precision':<10} {'Estimate':<12} {'Error':<8} {'Memory':<10}")
    print("-" * 80)
    
    for scenario in scenarios:
        hll = HyperLogLog(precision=scenario["precision"])
        
        # Add unique elements
        for i in range(scenario["size"]):
            hll.add(f"element_{i:08d}")
        
        estimate = hll.estimate_cardinality()
        estimated_cardinality = estimate['estimated_cardinality']
        error = abs(estimated_cardinality - scenario["size"]) / scenario["size"]
        memory_kb = hll.get_bucket_analysis()['memory_usage_bytes'] / 1024
        
        print(f"{scenario['name']:<20} {scenario['size']:<12,} {scenario['precision']:<10} "
              f"{estimated_cardinality:<12,} {error:<8.2%} {memory_kb:<10.1f}KB")


def main():
    """Run all examples."""
    print("HyperLogLog Real-World Examples")
    print("=" * 60)
    print("This script demonstrates practical applications of HyperLogLog")
    print("in various scenarios including web analytics, databases,")
    print("distributed systems, and streaming data analysis.")
    print()
    
    # Run all examples
    example_web_analytics()
    example_database_optimization()
    example_distributed_systems()
    example_streaming_data()
    example_accuracy_analysis()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main() 