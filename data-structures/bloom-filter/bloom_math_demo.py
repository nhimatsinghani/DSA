#!/usr/bin/env python3
"""
Mathematical Foundation of Bloom Filters: Step-by-Step Derivation

This script demonstrates the mathematical reasoning behind the false positive
probability formula and optimal parameter selection.
"""

import math
from bloomfilter import BloomFilter


def demonstrate_single_bit_probability():
    """Demonstrate the probability that a single bit remains 0."""
    print("🎯 Step 1: Single Bit Probability")
    print("=" * 60)
    
    print("When we add an element with k hash functions:")
    print("- Each hash function targets one bit position")
    print("- Probability that a specific bit is NOT set by one hash = (m-1)/m")
    print("- With k hash functions: P(bit stays 0) = ((m-1)/m)^k")
    print()
    
    # Demonstrate with concrete numbers
    m = 1000  # bit array size
    k = 3     # hash functions
    
    prob_not_set_single = (m-1)/m
    prob_not_set_k = prob_not_set_single ** k
    
    print(f"Example with m={m}, k={k}:")
    print(f"  P(bit not set by 1 hash) = {m-1}/{m} = {prob_not_set_single:.6f}")
    print(f"  P(bit not set by {k} hashes) = {prob_not_set_single:.6f}^{k} = {prob_not_set_k:.6f}")
    
    # For large m, (m-1)/m ≈ 1 - 1/m ≈ e^(-1/m)
    approximation = math.exp(-1/m) ** k
    print(f"  Approximation using e^(-1/m): {approximation:.6f}")
    print(f"  Difference: {abs(prob_not_set_k - approximation):.8f}")


def demonstrate_multiple_elements():
    """Show what happens when we add multiple elements."""
    print(f"\n🎯 Step 2: Multiple Elements")
    print("=" * 60)
    
    print("After adding n elements:")
    print("- Each element performs k hash operations")
    print("- Total hash operations = n × k")
    print("- P(specific bit stays 0) = ((m-1)/m)^(n×k)")
    print()
    
    m = 1000
    k = 3
    n_values = [1, 10, 50, 100, 200]
    
    print(f"Example with m={m}, k={k}:")
    print(f"{'Elements (n)':<12} {'Hash Ops':<10} {'P(bit=0)':<12} {'P(bit=1)':<12}")
    print("-" * 50)
    
    for n in n_values:
        total_hashes = n * k
        prob_bit_zero = ((m-1)/m) ** total_hashes
        prob_bit_one = 1 - prob_bit_zero
        
        print(f"{n:<12} {total_hashes:<10} {prob_bit_zero:<12.6f} {prob_bit_one:<12.6f}")
    
    print(f"\nFor large m, we can approximate:")
    print(f"P(bit = 0) ≈ e^(-kn/m)")
    print(f"P(bit = 1) ≈ 1 - e^(-kn/m)")


def demonstrate_false_positive_derivation():
    """Derive the false positive probability formula."""
    print(f"\n🎯 Step 3: False Positive Probability Derivation")
    print("=" * 60)
    
    print("False Positive occurs when:")
    print("- We query an element NOT in the set")
    print("- But ALL k bits that would be set by this element are already 1")
    print("- This happens due to other elements setting those bits")
    print()
    
    print("Mathematical derivation:")
    print("1. P(single bit = 1) = 1 - e^(-kn/m)")
    print("2. P(all k bits = 1) = [P(single bit = 1)]^k")
    print("3. P(false positive) = [1 - e^(-kn/m)]^k")
    print()
    
    # Demonstrate with real numbers
    m = 1000
    k = 7
    
    print(f"Example with m={m}, k={k}:")
    print(f"{'Elements (n)':<12} {'P(bit=1)':<12} {'P(false pos)':<15} {'Actual Test':<12}")
    print("-" * 60)
    
    for n in [50, 100, 200, 300, 500]:
        # Theoretical calculation
        p_bit_one = 1 - math.exp(-k * n / m)
        p_false_pos = p_bit_one ** k
        
        # Empirical test
        bf = BloomFilter(capacity=n*2, bit_array_size=m, num_hash_functions=k)
        for i in range(n):
            bf.add(f"element_{i}")
        
        # Test false positive rate
        false_positives = 0
        test_count = 1000
        for i in range(test_count):
            result = bf.query(f"test_{i}")
            if result['result'] == "POSSIBLY_IN_SET":
                false_positives += 1
        
        actual_fp_rate = false_positives / test_count
        
        print(f"{n:<12} {p_bit_one:<12.6f} {p_false_pos:<15.6f} {actual_fp_rate:<12.6f}")


def demonstrate_optimal_parameters():
    """Show how to find optimal m and k values."""
    print(f"\n🎯 Step 4: Optimal Parameter Selection")
    print("=" * 60)
    
    print("Given desired false positive rate p and expected elements n:")
    print("We want to minimize memory usage while achieving target error rate.")
    print()
    
    print("Mathematical optimization:")
    print("1. Start with: p = (1 - e^(-kn/m))^k")
    print("2. Take logarithm: ln(p) = k × ln(1 - e^(-kn/m))")
    print("3. For optimal k, take derivative and set to 0")
    print("4. Result: k_optimal = (m/n) × ln(2)")
    print("5. Substituting back: m = -n × ln(p) / (ln(2))²")
    print()
    
    # Demonstrate parameter calculation
    n = 1000  # expected elements
    target_errors = [0.01, 0.001, 0.0001]
    
    print(f"For n = {n} elements:")
    print(f"{'Target Error':<15} {'Optimal m':<12} {'Optimal k':<12} {'Memory (KB)':<12} {'Actual Error':<12}")
    print("-" * 75)
    
    for p in target_errors:
        # Calculate optimal parameters
        m_optimal = int(-n * math.log(p) / (math.log(2) ** 2))
        k_optimal = int((m_optimal / n) * math.log(2))
        k_optimal = max(1, k_optimal)  # At least 1 hash function
        
        # Calculate actual error rate with these parameters
        actual_error = (1 - math.exp(-k_optimal * n / m_optimal)) ** k_optimal
        memory_kb = (m_optimal + 7) // 8 / 1024  # Convert bits to KB
        
        print(f"{p:<15.4f} {m_optimal:<12} {k_optimal:<12} {memory_kb:<12.2f} {actual_error:<12.6f}")


def demonstrate_parameter_sensitivity():
    """Show how parameters affect performance."""
    print(f"\n🎯 Step 5: Parameter Sensitivity Analysis")
    print("=" * 60)
    
    n = 1000
    target_error = 0.01
    
    # Optimal parameters
    m_opt = int(-n * math.log(target_error) / (math.log(2) ** 2))
    k_opt = int((m_opt / n) * math.log(2))
    
    print(f"Optimal parameters for n={n}, target_error={target_error}:")
    print(f"  m_optimal = {m_opt}")
    print(f"  k_optimal = {k_opt}")
    print()
    
    # Test different k values with optimal m
    print("Effect of varying k (with optimal m):")
    print(f"{'k value':<10} {'Error Rate':<12} {'Memory Efficiency':<18}")
    print("-" * 45)
    
    for k in range(1, 15):
        error_rate = (1 - math.exp(-k * n / m_opt)) ** k
        efficiency = k / k_opt  # Relative to optimal
        
        marker = " ← OPTIMAL" if k == k_opt else ""
        print(f"{k:<10} {error_rate:<12.6f} {efficiency:<18.3f}{marker}")
    
    print(f"\nEffect of varying m (with optimal k):")
    print(f"{'m value':<10} {'Error Rate':<12} {'Memory Ratio':<15}")
    print("-" * 40)
    
    for ratio in [0.5, 0.7, 0.85, 1.0, 1.2, 1.5, 2.0]:
        m = int(m_opt * ratio)
        error_rate = (1 - math.exp(-k_opt * n / m)) ** k_opt
        
        marker = " ← OPTIMAL" if ratio == 1.0 else ""
        print(f"{m:<10} {error_rate:<12.6f} {ratio:<15.2f}{marker}")


def main():
    """Run all mathematical demonstrations."""
    print("📚 Bloom Filter Mathematics: Complete Derivation")
    print("=" * 80)
    print("This demonstrates the mathematical foundation behind Bloom filters,")
    print("from basic probability to optimal parameter selection.")
    print()
    
    demonstrate_single_bit_probability()
    demonstrate_multiple_elements()
    demonstrate_false_positive_derivation()
    demonstrate_optimal_parameters()
    demonstrate_parameter_sensitivity()
    
    print(f"\n✨ Mathematical Summary:")
    print(f"• False Positive Rate: P(fp) = (1 - e^(-kn/m))^k")
    print(f"• Optimal Memory: m = -n × ln(p) / (ln(2))²")
    print(f"• Optimal Hash Functions: k = (m/n) × ln(2)")
    print(f"• Memory Efficiency: ~9.6 bits per element for 1% error")
    print(f"• Space Complexity: O(n) - linear with elements!")


if __name__ == "__main__":
    main() 