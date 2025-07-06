"""
LeetCode 2611: Mice and Cheese
https://leetcode.com/problems/mice-and-cheese/description/

Problem:
There are two mice and n types of cheese, each type of cheese should be eaten by exactly one mouse.
- First mouse gets reward1[i] if it eats cheese i
- Second mouse gets reward2[i] if it eats cheese i  
- First mouse must eat exactly k types of cheese
- Return the maximum points you can achieve

THE KEY INTUITION:
================

Think of it as a SUBSTITUTION problem rather than a selection problem!

1. BASELINE ASSUMPTION: Let the second mouse eat ALL the cheese initially
   - Total reward = sum(reward2)

2. NOW THE QUESTION BECOMES: Which k pieces should we "substitute" by giving them to the first mouse?
   - For each piece i, if we switch it from mouse2 to mouse1:
   - We LOSE: reward2[i] 
   - We GAIN: reward1[i]
   - NET CHANGE: reward1[i] - reward2[i]

3. TO MAXIMIZE TOTAL: Pick the k pieces with the LARGEST net positive changes
   - Use a heap/sorting to find k maximum (reward1[i] - reward2[i]) values

This transforms a complex optimization problem into a simple "pick k best substitutions" problem!

GENERALIZATION TO OTHER PROBLEMS:
================================
This pattern applies when you have:
- Resource allocation between two entities
- Fixed constraints (exactly k items to one entity)
- Need to maximize total benefit

The key insight: Start with one complete allocation, then find the best "swaps" to make.
"""

from typing import List
import heapq


def mice_and_cheese_optimal(reward1: List[int], reward2: List[int], k: int) -> int:
    """
    Optimal O(n log k) solution using min-heap
    
    Args:
        reward1: rewards for first mouse
        reward2: rewards for second mouse  
        k: number of pieces first mouse must eat
    
    Returns:
        Maximum total reward achievable
    """
    # Step 1: Start with baseline - second mouse eats everything
    total_reward = sum(reward2)
    
    # Step 2: Calculate net benefit of giving each piece to first mouse
    # Use min-heap to track k largest benefits efficiently
    heap = []
    
    for i in range(len(reward1)):
        benefit = reward1[i] - reward2[i]
        
        if len(heap) < k:
            heapq.heappush(heap, benefit)
        elif benefit > heap[0]:  # Better than worst in our top-k
            heapq.heapreplace(heap, benefit)
    
    # Step 3: Add the k best substitutions to baseline
    total_reward += sum(heap)
    
    return total_reward


def mice_and_cheese_sorting(reward1: List[int], reward2: List[int], k: int) -> int:
    """
    Alternative O(n log n) solution using sorting - easier to understand
    """
    # Step 1: Baseline assumption
    total_reward = sum(reward2)
    
    # Step 2: Calculate all benefits and sort to find k largest  
    benefits = []
    for i in range(len(reward1)):
        benefit = reward1[i] - reward2[i]
        benefits.append(benefit)
    
    # Step 3: Sort and take k largest benefits
    benefits.sort(reverse=True)  # Largest first
    total_reward += sum(benefits[:k])
    
    return total_reward


def demonstrate_intuition():
    """
    Let's trace through an example to see the intuition in action
    """
    reward1 = [1, 1, 3, 4]
    reward2 = [4, 4, 1, 1] 
    k = 2
    
    print("=== MICE AND CHEESE INTUITION DEMO ===")
    print(f"reward1 = {reward1}")
    print(f"reward2 = {reward2}")
    print(f"k = {k} (first mouse eats {k} pieces)")
    print()
    
    # Step 1: Baseline
    baseline = sum(reward2)
    print(f"Step 1 - Baseline (mouse2 eats all): {baseline}")
    print()
    
    # Step 2: Calculate substitution benefits
    print("Step 2 - Substitution analysis:")
    benefits = []
    for i in range(len(reward1)):
        benefit = reward1[i] - reward2[i]
        benefits.append((benefit, i))
        print(f"  Piece {i}: Give to mouse1 → gain {reward1[i]}, lose {reward2[i]} = net {benefit:+d}")
    print()
    
    # Step 3: Pick best substitutions
    benefits.sort(reverse=True, key=lambda x: x[0])
    print(f"Step 3 - Best {k} substitutions:")
    total_benefit = 0
    for i in range(k):
        benefit, piece_idx = benefits[i]
        total_benefit += benefit
        print(f"  Give piece {piece_idx} to mouse1: {benefit:+d}")
    print()
    
    final_reward = baseline + total_benefit
    print(f"Final calculation: {baseline} + {total_benefit} = {final_reward}")
    print()
    
    # Verify with our functions
    result1 = mice_and_cheese_optimal(reward1, reward2, k)
    result2 = mice_and_cheese_sorting(reward1, reward2, k)
    print(f"Verification - Heap solution: {result1}")
    print(f"Verification - Sort solution: {result2}")


def pattern_recognition_examples():
    """
    Examples of other problems that use the same substitution thinking pattern
    """
    print("\n=== SIMILAR PROBLEM PATTERNS ===")
    
    print("1. TASK ASSIGNMENT:")
    print("   - Assign k tasks to worker A, rest to worker B")
    print("   - Same logic: baseline all to B, substitute k best to A")
    print()
    
    print("2. STOCK TRADING:")
    print("   - Choose k stocks to buy, rest to sell")
    print("   - Baseline: sell all, substitute k best as buys")
    print()
    
    print("3. RESOURCE ALLOCATION:")
    print("   - Allocate k items to high-priority, rest to low-priority")
    print("   - Baseline: all low-priority, substitute k best to high-priority")
    print()
    
    print("KEY PATTERN RECOGNITION:")
    print("- Two entities competing for resources")
    print("- Fixed allocation constraint (exactly k items)")
    print("- Different values for each entity")
    print("- Goal: maximize total value")
    print("→ Use substitution thinking!")


if __name__ == "__main__":
    demonstrate_intuition()
    pattern_recognition_examples()
