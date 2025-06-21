"""
LeetCode 378: Kth Smallest Element in a Sorted Matrix
Binary Search Solution - O(n * log(max - min)) Time Complexity

Problem:
Given an n x n matrix where each row and column is sorted in ascending order,
find the kth smallest element in the matrix.

Key Insight:
Instead of searching positions, we binary search on the VALUE RANGE.
We count how many elements are ≤ mid and adjust our search accordingly.

Example:
matrix = [[1,  5,  9],
          [10, 11, 13], 
          [12, 13, 15]], k = 8
Output: 13

Strategy:
1. Binary search on values from matrix[0][0] to matrix[n-1][n-1]
2. For each mid value, count elements ≤ mid using matrix properties
3. Adjust search range based on count vs k
"""


def kth_smallest(matrix, k):
    """
    Find the kth smallest element in a sorted matrix using binary search.
    
    Time Complexity: O(n * log(max - min))
    - Binary search: O(log(max - min)) iterations
    - Count function: O(n) per iteration
    
    Space Complexity: O(1)
    
    Args:
        matrix: List[List[int]] - n x n matrix with sorted rows and columns
        k: int - find kth smallest element (1-indexed)
    
    Returns:
        int - the kth smallest element
    """
    n = len(matrix)
    
    # Set up binary search range on VALUES, not indices
    low = matrix[0][0]      # smallest possible value
    high = matrix[n-1][n-1] # largest possible value
    
    # Binary search on the answer
    # The binary search is finding the smallest value such that there are at least k elements ≤ that value. For such a "jump point" to exist, that value must actually be present in the matrix. If it weren't present, there would be no jump in the count function, and we couldn't satisfy our invariant.
    # This is the beautiful guarantee that makes this algorithm work: the binary search converges to an actual element in the matrix, not just any value in the range.
    while low < high:
        mid = low + (high - low) // 2
        
        # Count how many elements are ≤ mid
        count = count_less_equal(matrix, mid)
        
        if count < k:
            # Need a larger value, search right half
            low = mid + 1
        else:
            # Current value might be answer, search left half
            high = mid
    
    return low


def count_less_equal(matrix, target):
    """
    Count elements ≤ target in sorted matrix.
    
    Uses the key property: start from bottom-left corner
    - If matrix[i][j] ≤ target: all elements above are also ≤ target
    - If matrix[i][j] > target: move up to find smaller elements
    
    Time Complexity: O(n) - each step moves either up or right
    Space Complexity: O(1)
    
    Args:
        matrix: List[List[int]] - sorted matrix
        target: int - value to compare against
    
    Returns:
        int - count of elements ≤ target
    """
    n = len(matrix)
    count = 0
    
    # Start from bottom-left corner
    i, j = n - 1, 0
    
    while i >= 0 and j < n:
        if matrix[i][j] <= target:
            # All elements above in this column are ≤ target
            count += (i + 1)  # Add entire column above and including current
            j += 1            # Move right to potentially larger elements
        else:
            # Current element > target, move up to smaller elements
            i -= 1
    
    return count


def demonstrate_algorithm():
    """
    Demonstrate the algorithm with step-by-step execution.
    """
    matrix = [
        [ 1,  5,  9],
        [10, 11, 13], 
        [12, 13, 15]
    ]
    k = 8
    
    print("=== Kth Smallest Element in Sorted Matrix ===")
    print(f"Matrix:")
    for row in matrix:
        print(f"  {row}")
    print(f"k = {k}")
    print()
    
    n = len(matrix)
    low = matrix[0][0]
    high = matrix[n-1][n-1]
    iteration = 1
    
    print(f"Initial range: [{low}, {high}]")
    print()
    
    while low < high:
        mid = low + (high - low) // 2
        count = count_less_equal(matrix, mid)
        
        print(f"Iteration {iteration}:")
        print(f"  Range: [{low}, {high}]")
        print(f"  Mid: {mid}")
        print(f"  Elements ≤ {mid}: {count}")
        
        if count < k:
            print(f"  Count {count} < k {k}, search right half")
            low = mid + 1
        else:
            print(f"  Count {count} ≥ k {k}, search left half")
            high = mid
            
        print(f"  New range: [{low}, {high}]")
        print()
        iteration += 1
    
    result = low
    print(f"Final answer: {result}")
    print(f"Verification: {result} is the {k}th smallest element")
    
    # Verify by flattening and sorting
    flat = []
    for row in matrix:
        flat.extend(row)
    flat.sort()
    print(f"Sorted elements: {flat}")
    print(f"8th element (0-indexed 7): {flat[k-1]}")


def demonstrate_counting():
    """
    Demonstrate the counting algorithm step by step.
    """
    matrix = [
        [ 1,  5,  9],
        [10, 11, 13], 
        [12, 13, 15]
    ]
    target = 11
    
    print("=== Counting Elements ≤ Target ===")
    print(f"Matrix:")
    for i, row in enumerate(matrix):
        print(f"  Row {i}: {row}")
    print(f"Target: {target}")
    print()
    
    n = len(matrix)
    count = 0
    i, j = n - 1, 0  # Start from bottom-left
    step = 1
    
    print("Starting from bottom-left corner:")
    print(f"Position: ({i}, {j}), Value: {matrix[i][j]}")
    print()
    
    while i >= 0 and j < n:
        current = matrix[i][j]
        print(f"Step {step}: Position ({i}, {j}), Value: {current}")
        
        if current <= target:
            added = i + 1
            count += added
            print(f"  {current} ≤ {target}: Add {added} elements (column above), move right")
            print(f"  Running count: {count}")
            j += 1
        else:
            print(f"  {current} > {target}: Move up")
            i -= 1
        
        print()
        step += 1
    
    print(f"Final count: {count} elements ≤ {target}")


def explain_why_low_exists():
    """
    Detailed explanation of why low is guaranteed to exist in the matrix
    when the binary search terminates.
    """
    matrix = [
        [ 1,  5,  9],
        [10, 11, 13], 
        [12, 13, 15]
    ]
    k = 8
    
    print("=== Why 'low' is Guaranteed to Exist in Matrix ===")
    print(f"Matrix: {matrix}")
    print(f"k = {k}")
    print()
    
    # Flatten and sort to see the actual elements
    flat = []
    for row in matrix:
        flat.extend(row)
    flat.sort()
    print(f"All elements sorted: {flat}")
    print(f"The {k}th smallest (1-indexed) is: {flat[k-1]}")
    print()
    
    # Show counts for values around the answer
    answer = flat[k-1]
    print("Let's examine counts around the answer:")
    
    for value in range(answer - 2, answer + 3):
        count = count_less_equal(matrix, value)
        exists = value in flat
        status = "✓" if exists else "✗"
        print(f"  count({value}) = {count} | exists in matrix: {status}")
    
    print()
    print("Key observations:")
    print(f"1. count({answer - 1}) = {count_less_equal(matrix, answer - 1)} < {k}")
    print(f"2. count({answer}) = {count_less_equal(matrix, answer)} ≥ {k}")
    print(f"3. {answer} exists in matrix: ✓")
    print()
    print("If the answer didn't exist in the matrix, we'd have:")
    print(f"   count(answer) = count(answer-1), violating our invariant!")


def demonstrate_invariant():
    """
    Show how the invariant is maintained throughout the algorithm.
    """
    matrix = [
        [ 1,  5,  9],
        [10, 11, 13], 
        [12, 13, 15]
    ]
    k = 8
    
    print("=== Demonstrating the Invariant ===")
    print(f"Matrix: {matrix}")
    print(f"k = {k}")
    print()
    print("Invariant: count(low-1) < k ≤ count(high)")
    print()
    
    n = len(matrix)
    low = matrix[0][0]
    high = matrix[n-1][n-1]
    iteration = 1
    
    while low < high:
        mid = low + (high - low) // 2
        count = count_less_equal(matrix, mid)
        
        print(f"Iteration {iteration}:")
        print(f"  Range: [{low}, {high}]")
        print(f"  Mid: {mid}")
        print(f"  count({mid}) = {count}")
        
        # Check invariant
        count_low_minus_1 = count_less_equal(matrix, low - 1) if low > matrix[0][0] else 0
        count_high = count_less_equal(matrix, high)
        
        print(f"  Invariant check:")
        print(f"    count({low-1}) = {count_low_minus_1} < {k} ✓")
        print(f"    count({high}) = {count_high} ≥ {k} ✓" if count_high >= k else f"    count({high}) = {count_high} < {k} ✗")
        
        if count < k:
            print(f"  count({mid}) < {k}, so answer > {mid}")
            print(f"  New low = {mid + 1}")
            low = mid + 1
        else:
            print(f"  count({mid}) ≥ {k}, so answer ≤ {mid}")
            print(f"  New high = {mid}")
            high = mid
        
        print()
        iteration += 1
    
    print(f"Final: low = high = {low}")
    print(f"count({low-1}) = {count_less_equal(matrix, low-1)} < {k}")
    print(f"count({low}) = {count_less_equal(matrix, low)} ≥ {k}")
    
    # Verify it exists
    flat = []
    for row in matrix:
        flat.extend(row)
    exists = low in flat
    print(f"{low} exists in matrix: {'✓' if exists else '✗'}")


# Test cases
def test_kth_smallest():
    """Test the algorithm with various cases."""
    
    test_cases = [
        {
            'matrix': [[1, 5, 9], [10, 11, 13], [12, 13, 15]],
            'k': 8,
            'expected': 13
        },
        {
            'matrix': [[-5]],
            'k': 1,
            'expected': -5
        },
        {
            'matrix': [[1, 2], [1, 3]],
            'k': 2,
            'expected': 1
        },
        {
            'matrix': [[1, 3, 5], [6, 7, 12], [11, 14, 14]],
            'k': 6,
            'expected': 11
        }
    ]
    
    print("=== Testing Kth Smallest Algorithm ===")
    for i, test in enumerate(test_cases):
        matrix = test['matrix']
        k = test['k']
        expected = test['expected']
        result = kth_smallest(matrix, k)
        
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"Test {i+1}: {status}")
        print(f"  Matrix: {matrix}")
        print(f"  k: {k}")
        print(f"  Expected: {expected}, Got: {result}")
        print()


if __name__ == "__main__":
    # Run demonstrations and tests
    demonstrate_algorithm()
    print("\n" + "="*50 + "\n")
    demonstrate_counting()
    print("\n" + "="*50 + "\n")
    explain_why_low_exists()
    print("\n" + "="*50 + "\n")
    demonstrate_invariant()
    print("\n" + "="*50 + "\n")
    test_kth_smallest()
