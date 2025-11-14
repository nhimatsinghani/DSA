"""
Runtime Complexity Analysis - Weighted Interval Scheduling
========================================================

Detailed analysis of time and space complexity for both approaches
in weighted_interval_scheduling.py
"""

def analyze_recursive_approach():
    """
    RECURSIVE WITH MEMOIZATION APPROACH
    ==================================
    
    Time Complexity: O(n²) - SUBOPTIMAL
    Space Complexity: O(n)
    
    Breakdown:
    1. Sorting intervals by end time: O(n log n)
    2. Recursive function solve(i):
       - Called for each index 0 to n-1 (with memoization, each called once)
       - For each call:
         * Skip option: O(1) - just call solve(i+1)
         * Take option: 
           - Find next non-overlapping: O(n) LINEAR SEARCH ← BOTTLENECK!
           - Call solve(next_i): O(1) due to memoization
       - Total for all recursive calls: O(n) calls × O(n) search = O(n²)
    
    Total: O(n log n) + O(n²) = O(n²)
    
    Space:
    - Memoization table: O(n)
    - Recursion stack: O(n) in worst case
    - Total: O(n)
    
    INEFFICIENCY: Linear search for next non-overlapping interval!
    """
    
    print("=== RECURSIVE APPROACH COMPLEXITY ===")
    print("Time: O(n²) - due to linear search")
    print("Space: O(n)")
    print("Bottleneck: Finding next non-overlapping interval")
    print()

def analyze_dp_approach():
    """
    BOTTOM-UP DYNAMIC PROGRAMMING APPROACH
    =====================================
    
    Time Complexity: O(n log n) - OPTIMAL
    Space Complexity: O(n)
    
    Breakdown:
    1. Sorting intervals by end time: O(n log n)
    2. Fill DP table:
       - Loop through n intervals: O(n)
       - For each interval:
         * Don't take option: O(1)
         * Take option:
           - find_latest_non_overlapping_by_end(): O(log n) BINARY SEARCH ← EFFICIENT!
           - Other operations: O(1)
       - Total for DP: O(n) × O(log n) = O(n log n)
    3. Reconstruct solution: O(n log n) - n intervals × O(log n) binary search each
    
    Total: O(n log n) + O(n log n) + O(n log n) = O(n log n)
    
    Space:
    - DP array: O(n)
    - Take array: O(n)
    - Total: O(n)
    
    EFFICIENCY: Binary search for non-overlapping intervals!
    """
    
    print("=== DP APPROACH COMPLEXITY ===")
    print("Time: O(n log n) - optimal for this problem")
    print("Space: O(n)")
    print("Key optimization: Binary search instead of linear search")
    print()

def demonstrate_complexity_difference():
    """Show why binary search vs linear search matters."""
    
    print("=== WHY BINARY SEARCH MATTERS ===")
    print()
    print("For n intervals:")
    print("Linear search: O(n) per lookup")
    print("Binary search: O(log n) per lookup")
    print()
    print("With n lookups total:")
    print("Linear approach: n × O(n) = O(n²)")
    print("Binary approach: n × O(log n) = O(n log n)")
    print()
    
    # Concrete example
    sizes = [10, 100, 1000, 10000]
    import math
    
    print("Concrete numbers:")
    print("n\t\tn²\t\tn log n\t\tSpeedup")
    print("-" * 50)
    
    for n in sizes:
        n_squared = n * n
        n_log_n = n * math.ceil(math.log2(n))
        speedup = n_squared / n_log_n
        print(f"{n}\t\t{n_squared}\t\t{n_log_n}\t\t{speedup:.1f}x")

def optimized_recursive_approach():
    """
    How to optimize the recursive approach to O(n log n)
    """
    
    print("\n=== OPTIMIZING RECURSIVE APPROACH ===")
    print()
    print("CURRENT ISSUE:")
    print("```python")
    print("# Linear search - O(n)")
    print("next_i = i + 1")
    print("while next_i < n and intervals[next_i][0] < intervals[i][1]:")
    print("    next_i += 1")
    print("```")
    print()
    print("OPTIMIZED VERSION:")
    print("```python")
    print("# Binary search - O(log n)")
    print("def find_next_non_overlapping(intervals, i):")
    print("    target_end = intervals[i][1]")
    print("    left, right = i + 1, len(intervals) - 1")
    print("    result = len(intervals)  # If no valid interval found")
    print("    ")
    print("    while left <= right:")
    print("        mid = (left + right) // 2")
    print("        if intervals[mid][0] >= target_end:")
    print("            result = mid")
    print("            right = mid - 1")
    print("        else:")
    print("            left = mid + 1")
    print("    return result")
    print("```")
    print()
    print("With this optimization:")
    print("Recursive approach: O(n log n) - same as DP!")

def space_complexity_details():
    """Detailed space complexity analysis."""
    
    print("\n=== SPACE COMPLEXITY DETAILS ===")
    print()
    print("RECURSIVE APPROACH:")
    print("- Memoization table: O(n) - stores result for each subproblem")
    print("- Recursion stack: O(n) worst case - linear chain of calls")
    print("- Solution reconstruction: O(n) - storing selected intervals")
    print("- Total: O(n)")
    print()
    print("DP APPROACH:")
    print("- DP array: O(n) - stores max earnings for each prefix")
    print("- Take array: O(n) - boolean decisions for reconstruction")
    print("- Solution reconstruction: O(n) - storing selected intervals")
    print("- Total: O(n)")
    print()
    print("Both approaches have the same space complexity!")

def comparison_with_unweighted():
    """Compare complexities with unweighted version."""
    
    print("\n=== COMPARISON WITH UNWEIGHTED VERSION ===")
    print()
    print("UNWEIGHTED (Greedy):")
    print("- Time: O(n log n) - just sorting + linear scan")
    print("- Space: O(1) - no additional data structures needed")
    print()
    print("WEIGHTED (DP):")
    print("- Time: O(n log n) - sorting + DP with binary search")
    print("- Space: O(n) - DP table and memoization")
    print()
    print("KEY INSIGHT:")
    print("Adding weights doesn't change time complexity asymptotically,")
    print("but requires more space and more complex algorithm.")
    print()
    print("GREEDY FAILS FOR WEIGHTED:")
    print("Example: [[1,10], [2,3], [4,5]]")
    print("- Greedy by end time: takes [2,3], [4,5] = 2+2 = $4 earnings")
    print("- Optimal: take [1,10] = $25 earnings")
    print("- Greedy doesn't consider the weight (earnings) of intervals!")

if __name__ == "__main__":
    print("=== COMPLEXITY ANALYSIS: WEIGHTED INTERVAL SCHEDULING ===\n")
    
    analyze_recursive_approach()
    analyze_dp_approach()
    demonstrate_complexity_difference()
    optimized_recursive_approach()
    space_complexity_details()
    comparison_with_unweighted()
    
    print("\n" + "="*60)
    print("SUMMARY:")
    print("✓ DP Approach: O(n log n) time, O(n) space - OPTIMAL")
    print("✗ Current Recursive: O(n²) time, O(n) space - SUBOPTIMAL")
    print("✓ Optimized Recursive: O(n log n) time, O(n) space - OPTIMAL")
    print("="*60)


