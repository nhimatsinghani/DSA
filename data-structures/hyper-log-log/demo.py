#!/usr/bin/env python3
"""
Simple HyperLogLog demonstration script.

This script provides a quick introduction to HyperLogLog functionality
with easy-to-understand examples.
"""

from hyperloglog import HyperLogLog
import random
import string

def basic_demo():
    """Basic HyperLogLog demonstration."""
    print("🔍 HyperLogLog Basic Demo")
    print("=" * 50)
    
    # Create a HyperLogLog with precision 10 (1024 buckets)
    hll = HyperLogLog(precision=10)
    
    print("Adding 10,000 unique elements...")
    
    # Add unique elements
    for i in range(10000):
        hll.add(f"element_{i}")
    
    # Get estimate
    result = hll.estimate_cardinality()
    
    print(f"\n📊 Results:")
    print(f"   Actual count: 10,000")
    print(f"   Estimated count: {result['estimated_cardinality']:,}")
    print(f"   Error: {abs(result['estimated_cardinality'] - 10000) / 10000:.2%}")
    print(f"   Memory used: {hll.get_bucket_analysis()['memory_usage_bytes']:,} bytes")
    
    # Compare with exact counting memory
    exact_memory = 10000 * 20  # Assume 20 bytes per element
    memory_savings = (1 - hll.get_bucket_analysis()['memory_usage_bytes'] / exact_memory) * 100
    print(f"   Memory savings vs exact: {memory_savings:.1f}%")

def detailed_demo():
    """Detailed demonstration showing internal workings."""
    print("\n🔬 Detailed Internal Workings Demo")
    print("=" * 50)
    
    # Create small HyperLogLog for easier visualization
    hll = HyperLogLog(precision=4)  # Only 16 buckets
    
    print("Adding 5 elements with detailed analysis:")
    
    elements = ["apple", "banana", "cherry", "date", "elderberry"]
    
    for element in elements:
        details = hll.add(element)
        print(f"\n🔸 Element: '{element}'")
        print(f"   Hash: {details['hash_value']}")
        print(f"   Bucket: {details['bucket_index']} (binary: {details['bucket_bits']})")
        print(f"   Rank: {details['rank']}")
        print(f"   Updated bucket: {details['bucket_updated']}")
    
    # Show final state
    estimate = hll.estimate_cardinality()
    print(f"\n📈 Final Results:")
    print(f"   Actual elements: {len(elements)}")
    print(f"   Estimated: {estimate['estimated_cardinality']}")
    
    # Show non-zero buckets
    analysis = hll.get_bucket_analysis()
    print(f"   Buckets used: {analysis['bucket_count'] - analysis['rank_distribution'][0]}/{analysis['bucket_count']}")

def precision_comparison():
    """Compare different precision levels."""
    print("\n⚖️ Precision Comparison Demo")
    print("=" * 50)
    
    true_count = 50000
    precisions = [6, 8, 10, 12]
    
    print(f"Estimating {true_count:,} unique elements with different precisions:")
    print()
    print(f"{'Precision':<10} {'Buckets':<8} {'Estimate':<10} {'Error':<8} {'Memory':<10}")
    print("-" * 60)
    
    for precision in precisions:
        hll = HyperLogLog(precision=precision)
        
        # Add elements
        for i in range(true_count):
            hll.add(f"item_{i}")
        
        estimate = hll.estimate_cardinality()
        error = abs(estimate['estimated_cardinality'] - true_count) / true_count
        memory = hll.get_bucket_analysis()['memory_usage_bytes']
        
        print(f"{precision:<10} {hll.bucket_count:<8} {estimate['estimated_cardinality']:<10,} "
              f"{error:<8.2%} {memory:<10} bytes")

def merge_demo():
    """Demonstrate merging functionality."""
    print("\n🤝 Merge Demonstration")
    print("=" * 50)
    
    # Create two HyperLogLogs for different data sets
    hll1 = HyperLogLog(precision=10)
    hll2 = HyperLogLog(precision=10)
    
    print("Creating two separate datasets...")
    
    # Dataset 1: users from region A
    for i in range(10000):
        hll1.add(f"region_a_user_{i}")
    
    # Dataset 2: users from region B (with some overlap)
    for i in range(5000, 15000):  # 5000 overlap
        hll2.add(f"region_b_user_{i}")
    
    # Get individual estimates
    est1 = hll1.estimate_cardinality()
    est2 = hll2.estimate_cardinality()
    
    print(f"   Region A users: ~{est1['estimated_cardinality']:,}")
    print(f"   Region B users: ~{est2['estimated_cardinality']:,}")
    
    # Merge them
    merged = hll1.merge(hll2)
    merged_est = merged.estimate_cardinality()
    
    print(f"   Total unique users (merged): ~{merged_est['estimated_cardinality']:,}")
    print(f"   Expected (15,000): actual unique users")
    
    error = abs(merged_est['estimated_cardinality'] - 15000) / 15000
    print(f"   Merge accuracy: {100-error*100:.1f}%")

def streaming_demo():
    """Simulate streaming data processing."""
    print("\n🌊 Streaming Data Demo")
    print("=" * 50)
    
    hll = HyperLogLog(precision=12)
    
    print("Simulating real-time data stream...")
    print(f"{'Batch':<8} {'Elements':<12} {'Unique Est.':<12} {'Memory':<10}")
    print("-" * 50)
    
    total_elements = 0
    batch_size = 10000
    
    for batch in range(1, 11):
        # Simulate batch of data with some duplicates
        for _ in range(batch_size):
            # 70% new users, 30% returning users
            if random.random() < 0.7:
                user_id = f"user_{total_elements + random.randint(1, batch_size//2)}"
            else:
                user_id = f"user_{random.randint(1, total_elements)}"
            
            hll.add(user_id)
        
        total_elements += batch_size
        estimate = hll.estimate_cardinality()
        memory_kb = hll.get_bucket_analysis()['memory_usage_bytes'] / 1024
        
        print(f"{batch:<8} {total_elements:<12,} {estimate['estimated_cardinality']:<12,} {memory_kb:<10.1f}KB")

def main():
    """Run all demonstrations."""
    print("🎯 HyperLogLog Interactive Demo")
    print("This demo showcases the capabilities of the HyperLogLog data structure")
    print()
    
    try:
        basic_demo()
        detailed_demo()
        precision_comparison()
        merge_demo()
        streaming_demo()
        
        print("\n🎉 Demo completed!")
        print("\nTo learn more:")
        print("   📖 Read README.md for detailed explanations")
        print("   🧪 Run test_hyperloglog.py for comprehensive tests")
        print("   🌍 Run examples.py for real-world scenarios")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")

if __name__ == "__main__":
    main() 