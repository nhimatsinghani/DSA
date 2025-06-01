#!/usr/bin/env python3
"""
Simple Bloom Filter Demonstration

This script provides a quick overview of Bloom filter functionality
and key concepts.
"""

from bloomfilter import BloomFilter


def demonstrate_basic_operations():
    """Demonstrate basic add and query operations."""
    print("🌸 Basic Bloom Filter Operations")
    print("=" * 50)
    
    # Create a Bloom filter
    bf = BloomFilter(capacity=100, error_rate=0.05)
    
    print(f"Created Bloom filter:")
    print(f"  Capacity: {bf.capacity}")
    print(f"  Error rate: {bf.desired_error_rate}")
    print(f"  Bit array size: {bf.bit_array_size}")
    print(f"  Hash functions: {bf.num_hash_functions}")
    print(f"  Memory usage: {bf.get_statistics()['configuration']['memory_bytes']} bytes")
    
    # Add some fruits
    fruits = ["apple", "banana", "cherry", "date", "elderberry"]
    
    print(f"\nAdding fruits: {fruits}")
    for fruit in fruits:
        details = bf.add(fruit)
        print(f"  Added '{fruit}': hash positions {details['hash_positions']}")
    
    # Query fruits (should all be positive)
    print(f"\nQuerying added fruits:")
    for fruit in fruits:
        result = bf.query(fruit)
        print(f"  '{fruit}': {result['result']}")
    
    # Query fruits not added (should be negative or false positive)
    other_fruits = ["grape", "kiwi", "lemon", "mango", "orange"]
    print(f"\nQuerying non-added fruits:")
    false_positives = 0
    
    for fruit in other_fruits:
        result = bf.query(fruit)
        status = result['result']
        if status == "POSSIBLY_IN_SET":
            false_positives += 1
            print(f"  '{fruit}': {status} ⚠️ (FALSE POSITIVE)")
        else:
            print(f"  '{fruit}': {status} ✅")
    
    print(f"\nFalse positives found: {false_positives}/{len(other_fruits)}")


def demonstrate_parameter_effects():
    """Show how different parameters affect performance."""
    print(f"\n📊 Parameter Effects Demonstration")
    print("=" * 50)
    
    capacities = [100, 1000, 10000]
    error_rates = [0.01, 0.1]
    
    print(f"{'Capacity':<10} {'Error Rate':<12} {'Bit Array':<12} {'Hash Funcs':<12} {'Memory (KB)':<12}")
    print("-" * 70)
    
    for capacity in capacities:
        for error_rate in error_rates:
            bf = BloomFilter(capacity=capacity, error_rate=error_rate)
            stats = bf.get_statistics()
            memory_kb = stats['configuration']['memory_bytes'] / 1024
            
            print(f"{capacity:<10} {error_rate:<12.3f} {bf.bit_array_size:<12} "
                  f"{bf.num_hash_functions:<12} {memory_kb:<12.2f}")


def demonstrate_false_positive_rates():
    """Show actual vs theoretical false positive rates."""
    print(f"\n🎯 False Positive Rate Analysis")
    print("=" * 50)
    
    bf = BloomFilter(capacity=100, error_rate=0.1)
    
    # Add elements
    for i in range(100):
        bf.add(f"element_{i}")
    
    # Test many non-added elements
    false_positives = 0
    total_tests = 1000
    
    for i in range(total_tests):
        result = bf.query(f"test_element_{i}")
        if result['result'] == "POSSIBLY_IN_SET":
            false_positives += 1
    
    actual_fp_rate = false_positives / total_tests
    theoretical_fp_rate = bf.theoretical_fp_rate
    
    print(f"Theoretical false positive rate: {theoretical_fp_rate:.4f}")
    print(f"Actual false positive rate: {actual_fp_rate:.4f}")
    print(f"Difference: {abs(actual_fp_rate - theoretical_fp_rate):.4f}")
    print(f"False positives found: {false_positives}/{total_tests}")


def demonstrate_memory_efficiency():
    """Show memory efficiency compared to storing actual data."""
    print(f"\n💾 Memory Efficiency Demonstration")
    print("=" * 50)
    
    # Simulate storing different data types
    scenarios = [
        ("URLs", 50, "https://example.com/page_"),
        ("Email addresses", 30, "user@example.com"),
        ("Product IDs", 20, "PROD_12345_"),
        ("User IDs", 8, "12345678")
    ]
    
    capacity = 10000
    error_rate = 0.01
    
    print(f"Storing {capacity:,} items:")
    print(f"{'Data Type':<20} {'Avg Size':<12} {'Traditional':<15} {'Bloom Filter':<15} {'Savings':<10}")
    print("-" * 80)
    
    for data_type, avg_size, example in scenarios:
        traditional_memory = capacity * avg_size
        
        bf = BloomFilter(capacity=capacity, error_rate=error_rate)
        bloom_memory = bf.get_statistics()['configuration']['memory_bytes']
        
        savings = (1 - bloom_memory / traditional_memory) * 100
        
        print(f"{data_type:<20} {avg_size:<12} {traditional_memory/1024:<15.1f} "
              f"{bloom_memory/1024:<15.1f} {savings:<10.1f}%")


def demonstrate_union_operations():
    """Show union operations between Bloom filters."""
    print(f"\n🔗 Union Operations Demonstration")
    print("=" * 50)
    
    # Create two Bloom filters
    bf1 = BloomFilter(capacity=50, error_rate=0.1)
    bf2 = BloomFilter(capacity=50, error_rate=0.1)
    
    # Add different sets of data
    set1 = [f"user_{i}" for i in range(25)]
    set2 = [f"user_{i}" for i in range(15, 40)]  # Some overlap
    
    for item in set1:
        bf1.add(item)
    for item in set2:
        bf2.add(item)
    
    print(f"Set 1: {len(set1)} items")
    print(f"Set 2: {len(set2)} items")
    print(f"Actual union: {len(set(set1) | set(set2))} items")
    
    # Create union
    union_bf = bf1.union(bf2)
    
    print(f"\nUnion Bloom filter created")
    print(f"Elements from Set 1 in union: {sum(1 for item in set1 if item in union_bf)}")
    print(f"Elements from Set 2 in union: {sum(1 for item in set2 if item in union_bf)}")
    
    # Test some elements not in either set
    test_items = [f"user_{i}" for i in range(50, 60)]
    false_positives = sum(1 for item in test_items if item in union_bf)
    print(f"False positives in union: {false_positives}/{len(test_items)}")


def main():
    """Run all demonstrations."""
    print("Bloom Filter Interactive Demonstration")
    print("=" * 60)
    print("This script demonstrates key Bloom filter concepts")
    print("with interactive examples and analysis.")
    print()
    
    demonstrate_basic_operations()
    demonstrate_parameter_effects()
    demonstrate_false_positive_rates()
    demonstrate_memory_efficiency()
    demonstrate_union_operations()
    
    print(f"\n✨ Key Takeaways:")
    print("1. No false negatives - perfect recall")
    print("2. Tunable false positive rates")
    print("3. Massive memory savings (90%+ typical)")
    print("4. Fast O(k) operations")
    print("5. Ideal for pre-filtering expensive operations")
    
    print(f"\n🔬 Try running:")
    print("  python test_bloomfilter.py --examples  # Educational tests")
    print("  python examples.py                     # Real-world examples")


if __name__ == "__main__":
    main() 