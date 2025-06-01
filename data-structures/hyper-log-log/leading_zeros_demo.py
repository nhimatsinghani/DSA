#!/usr/bin/env python3
"""
Mathematical demonstration of leading zeros analysis in HyperLogLog.

This script demonstrates the probability theory behind leading zeros
and how it relates to cardinality estimation.
"""

import random
import math
from collections import defaultdict
from hyperloglog import HyperLogLog


def demonstrate_leading_zeros_probability():
    """Demonstrate the probability distribution of leading zeros."""
    print("🎲 Leading Zeros Probability Demonstration")
    print("=" * 60)
    
    # Generate many random binary strings and count leading zeros
    num_samples = 100000
    leading_zero_counts = defaultdict(int)
    
    print(f"Analyzing {num_samples:,} random 32-bit integers...")
    
    for _ in range(num_samples):
        # Generate random 32-bit integer
        random_int = random.randint(0, 2**32 - 1)
        
        # Count leading zeros
        if random_int == 0:
            leading_zeros = 32
        else:
            leading_zeros = 0
            for i in range(31, -1, -1):
                if (random_int >> i) & 1:
                    break
                leading_zeros += 1
        
        leading_zero_counts[leading_zeros] += 1
    
    print(f"\n{'Leading Zeros':<15} {'Count':<10} {'Observed %':<12} {'Theoretical %':<15} {'Ratio':<10}")
    print("-" * 70)
    
    for k in range(min(10, max(leading_zero_counts.keys()) + 1)):
        count = leading_zero_counts[k]
        observed_prob = count / num_samples
        theoretical_prob = 2 ** (-(k+1))  # P(exactly k leading zeros)
        ratio = observed_prob / theoretical_prob if theoretical_prob > 0 else 0
        
        print(f"{k:<15} {count:<10} {observed_prob:<12.4f} {theoretical_prob:<15.4f} {ratio:<10.2f}")


def demonstrate_maximum_leading_zeros():
    """Demonstrate how maximum leading zeros relates to set size."""
    print(f"\n🔢 Maximum Leading Zeros vs Set Size")
    print("=" * 60)
    
    print("This demonstrates E[max leading zeros] ≈ log₂(n)")
    print()
    
    set_sizes = [10, 50, 100, 500, 1000, 5000, 10000, 50000]
    
    print(f"{'Set Size':<10} {'Max LZ':<8} {'log₂(n)':<10} {'Difference':<12} {'Estimate':<12}")
    print("-" * 60)
    
    for n in set_sizes:
        # Generate n distinct random numbers and find max leading zeros
        random_numbers = set()
        while len(random_numbers) < n:
            random_numbers.add(random.randint(1, 2**32 - 1))  # Avoid 0
        
        max_leading_zeros = 0
        for num in random_numbers:
            leading_zeros = 0
            for i in range(31, -1, -1):
                if (num >> i) & 1:
                    break
                leading_zeros += 1
            max_leading_zeros = max(max_leading_zeros, leading_zeros)
        
        theoretical = math.log2(n)
        difference = abs(max_leading_zeros - theoretical)
        estimate = 2 ** max_leading_zeros
        
        print(f"{n:<10} {max_leading_zeros:<8} {theoretical:<10.2f} {difference:<12.2f} {estimate:<12.0f}")


def demonstrate_variance_problem():
    """Demonstrate why single maximum has high variance."""
    print(f"\n📊 Variance Problem with Single Maximum")
    print("=" * 60)
    
    true_cardinality = 1000
    num_trials = 20
    
    print(f"Estimating cardinality of {true_cardinality} elements using single maximum:")
    print(f"Running {num_trials} trials...\n")
    
    estimates = []
    
    print(f"{'Trial':<8} {'Max LZ':<8} {'Estimate':<12} {'Error':<10}")
    print("-" * 40)
    
    for trial in range(num_trials):
        # Generate unique numbers
        numbers = set()
        while len(numbers) < true_cardinality:
            numbers.add(random.randint(1, 2**32 - 1))
        
        # Find maximum leading zeros
        max_leading_zeros = 0
        for num in numbers:
            leading_zeros = 0
            for i in range(31, -1, -1):
                if (num >> i) & 1:
                    break
                leading_zeros += 1
            max_leading_zeros = max(max_leading_zeros, leading_zeros)
        
        estimate = 2 ** max_leading_zeros
        error = abs(estimate - true_cardinality) / true_cardinality
        estimates.append(estimate)
        
        print(f"{trial+1:<8} {max_leading_zeros:<8} {estimate:<12.0f} {error:<10.2%}")
    
    # Calculate statistics
    mean_estimate = sum(estimates) / len(estimates)
    variance = sum((e - mean_estimate)**2 for e in estimates) / len(estimates)
    std_dev = math.sqrt(variance)
    
    print(f"\nResults:")
    print(f"  True cardinality: {true_cardinality}")
    print(f"  Mean estimate: {mean_estimate:.0f}")
    print(f"  Standard deviation: {std_dev:.0f}")
    print(f"  Coefficient of variation: {std_dev/mean_estimate:.2%}")
    print(f"  This high variance is why HyperLogLog uses multiple buckets!")


def demonstrate_bucket_variance_reduction():
    """Show how multiple buckets reduce variance."""
    print(f"\n🪣 Variance Reduction with Multiple Buckets")
    print("=" * 60)
    
    true_cardinality = 1000
    num_trials = 20
    precision = 6  # 64 buckets
    
    print(f"Comparing single maximum vs HyperLogLog with {2**precision} buckets:")
    print(f"Running {num_trials} trials...\n")
    
    single_estimates = []
    hll_estimates = []
    
    print(f"{'Trial':<8} {'Single Max':<12} {'HyperLogLog':<12} {'Single Error':<12} {'HLL Error':<12}")
    print("-" * 65)
    
    for trial in range(num_trials):
        # Single maximum approach
        numbers = set()
        while len(numbers) < true_cardinality:
            numbers.add(random.randint(1, 2**32 - 1))
        
        max_leading_zeros = 0
        for num in numbers:
            leading_zeros = 0
            for i in range(31, -1, -1):
                if (num >> i) & 1:
                    break
                leading_zeros += 1
            max_leading_zeros = max(max_leading_zeros, leading_zeros)
        
        single_estimate = 2 ** max_leading_zeros
        single_error = abs(single_estimate - true_cardinality) / true_cardinality
        
        # HyperLogLog approach
        hll = HyperLogLog(precision=precision)
        for num in numbers:
            hll.add(str(num))
        
        hll_result = hll.estimate_cardinality()
        hll_estimate = hll_result['estimated_cardinality']
        hll_error = abs(hll_estimate - true_cardinality) / true_cardinality
        
        single_estimates.append(single_estimate)
        hll_estimates.append(hll_estimate)
        
        print(f"{trial+1:<8} {single_estimate:<12.0f} {hll_estimate:<12.0f} {single_error:<12.2%} {hll_error:<12.2%}")
    
    # Calculate statistics
    single_mean = sum(single_estimates) / len(single_estimates)
    single_std = math.sqrt(sum((e - single_mean)**2 for e in single_estimates) / len(single_estimates))
    
    hll_mean = sum(hll_estimates) / len(hll_estimates)
    hll_std = math.sqrt(sum((e - hll_mean)**2 for e in hll_estimates) / len(hll_estimates))
    
    print(f"\nComparison Results:")
    print(f"  True cardinality: {true_cardinality}")
    print(f"  Single Maximum:")
    print(f"    Mean: {single_mean:.0f}")
    print(f"    Std Dev: {single_std:.0f}")
    print(f"    CV: {single_std/single_mean:.2%}")
    print(f"  HyperLogLog:")
    print(f"    Mean: {hll_mean:.0f}")
    print(f"    Std Dev: {hll_std:.0f}")
    print(f"    CV: {hll_std/hll_mean:.2%}")
    print(f"  Variance reduction: {(single_std/hll_std):.1f}x")


def demonstrate_mathematical_derivation():
    """Show the mathematical derivation step by step."""
    print(f"\n📐 Mathematical Derivation")
    print("=" * 60)
    
    print("Step-by-step mathematical foundation:")
    print()
    
    print("1. Basic Probability:")
    print("   P(exactly k leading zeros) = 2^(-(k+1))")
    print("   This is because:")
    print("   - First k bits must be 0: probability = (1/2)^k")
    print("   - Next bit must be 1: probability = (1/2)")
    print("   - Combined: (1/2)^k × (1/2) = 2^(-(k+1))")
    print()
    
    print("2. Cumulative Probability:")
    print("   P(≤ k leading zeros) = 1 - 2^(-k)")
    print("   This sums the geometric series: Σ(i=0 to k) 2^(-(i+1))")
    print()
    
    print("3. Maximum of n values:")
    print("   P(max ≤ k) = [P(≤ k leading zeros)]^n = (1 - 2^(-k))^n")
    print()
    
    print("4. Expected maximum:")
    print("   E[max] = Σ(k=1 to ∞) P(max ≥ k)")
    print("   E[max] = Σ(k=1 to ∞) [1 - (1 - 2^(-k))^n]")
    print("   For large n: E[max] ≈ log₂(n)")
    print()
    
    print("5. Cardinality estimation:")
    print("   If max leading zeros = k, then n ≈ 2^k")
    print("   This inverts the relationship E[max] ≈ log₂(n)")
    print()
    
    print("6. Variance reduction:")
    print("   Single maximum has high variance")
    print("   HyperLogLog uses m buckets and harmonic mean:")
    print("   estimate = α × m² / Σ(2^(-bucket_max[i]))")
    print("   This reduces standard error to ≈ 1.04/√m")


def main():
    """Run all demonstrations."""
    print("🔍 Leading Zeros Analysis: Mathematical Foundation")
    print("This demonstrates the probability theory behind HyperLogLog")
    print()
    
    demonstrate_leading_zeros_probability()
    demonstrate_maximum_leading_zeros()
    demonstrate_variance_problem()
    demonstrate_bucket_variance_reduction()
    demonstrate_mathematical_derivation()
    
    print(f"\n✨ Key Insights:")
    print(f"1. Leading zeros follow geometric distribution")
    print(f"2. Maximum leading zeros ≈ log₂(cardinality)")  
    print(f"3. Single maximum has high variance")
    print(f"4. Multiple buckets + harmonic mean reduce variance")
    print(f"5. Final error rate: ≈ 1.04/√(number of buckets)")


if __name__ == "__main__":
    main() 