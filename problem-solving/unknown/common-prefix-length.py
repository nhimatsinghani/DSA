"""
Common Prefix Length Problem

Given a string, split it at every possible position to create suffixes.
For each suffix, find the length of common prefix with the original string.
Return the sum of all these lengths.

Example: "abcabcd" 
- Position 0: suffix="abcabcd" → common prefix with "abcabcd" = 7
- Position 1: suffix="bcabcd" → common prefix with "abcabcd" = 0  
- Position 2: suffix="cabcd" → common prefix with "abcabcd" = 0
- Position 3: suffix="abcd" → common prefix with "abcabcd" = 3 ("abc")
- Position 4: suffix="bcd" → common prefix with "abcabcd" = 0
- Position 5: suffix="cd" → common prefix with "abcabcd" = 0
- Position 6: suffix="d" → common prefix with "abcabcd" = 0
Total: 7 + 0 + 0 + 3 + 0 + 0 + 0 = 10

OPTIMIZATION INTUITION AND THINKING PROCESS:

1. **Pattern Recognition**: This problem is asking for prefix-suffix matching at multiple positions.
   This should immediately remind you of string algorithms like KMP, Z-algorithm, or suffix arrays.

2. **Key Insight**: Instead of comparing each suffix with the original string from scratch,
   we can reuse previous computations. If we know that s[i:i+k] matches s[0:k], then
   we might be able to use this information when processing s[i+1:].

3. **Z-Algorithm Connection**: The Z-algorithm computes exactly what we need - for each 
   position i, it finds the length of the longest substring starting from i that matches
   a prefix of the string. This is EXACTLY our problem definition!

4. **The "Z-box" Optimization**: The key insight is maintaining a "window" [l,r] where
   s[l:r+1] matches s[0:r-l+1]. When processing position i:
   - If i is inside this window, we already know s[i:r+1] matches s[i-l:r-l+1]
   - We can use previously computed Z[i-l] to avoid redundant comparisons
   - This amortizes the cost and achieves O(n) complexity

5. **How to Think of Such Optimizations**:
   a) Look for repeated work - Are we computing the same comparisons multiple times?
   b) Can we store and reuse intermediate results?
   c) Is there a sliding window or range where we can maintain some invariant?
   d) Does this problem relate to well-known algorithmic patterns?

6. **General Problem-Solving Strategy**:
   - Brute force first to understand the problem
   - Identify the bottleneck (repeated character comparisons)
   - Look for patterns in the data (prefix matching)
   - Apply known algorithms (Z-algorithm for prefix-suffix problems)
   - Use data structures to avoid redundant work (maintain Z-box window)

RELATED ALGORITHMS:
- KMP Algorithm: Uses failure function for pattern matching
- Suffix Arrays: For multiple string queries  
- Rolling Hash: For fast substring comparisons
- Manacher's Algorithm: For palindrome problems (similar window technique)
"""

def common_prefix_length_bruteforce(s: str) -> int:
    """
    Brute force solution: O(N^2) time complexity
    For each suffix, compare character by character with original string
    """
    n = len(s)
    total = 0
    
    for i in range(n):
        suffix = s[i:]
        # Find common prefix length between suffix and original string
        common_len = 0
        for j in range(min(len(suffix), len(s))):
            if suffix[j] == s[j]:
                common_len += 1
            else:
                break
        total += common_len
    
    return total


def z_algorithm(s: str) -> list[int]:
    """
    Z-algorithm: Compute Z-array where Z[i] is the length of longest 
    substring starting from i that matches a prefix of the string.
    
    Time Complexity: O(N)
    Space Complexity: O(N)
    """
    n = len(s)
    z = [0] * n
    z[0] = n  # The whole string matches itself
    
    l, r = 0, 0  # Z-box boundaries [l, r]
    
    for i in range(1, n):
        if i <= r:
            # i is within current Z-box, use previously computed information
            z[i] = min(r - i + 1, z[i - l])
        
        # Try to extend the match
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        
        # Update Z-box if current match extends beyond previous boundary
        if i + z[i] - 1 > r:
            l, r = i, i + z[i] - 1
    
    return z


def common_prefix_length_optimized(s: str) -> int:
    """
    Optimized solution using Z-algorithm: O(N) time complexity
    
    The Z-algorithm computes exactly what we need: for each position i,
    the length of longest substring starting from i that matches a prefix.
    """
    z_array = z_algorithm(s)
    return sum(z_array)


def demonstrate_solutions():
    """Demonstrate both solutions with examples"""
    test_cases = [
        "abcabcd",
        "aaaa",
        "abcd",
        "abcabc",
        "a"
    ]
    
    print("=== Common Prefix Length Problem ===\n")
    
    for s in test_cases:
        print(f"Input: '{s}'")
        
        # Show the breakdown for better understanding
        print("Breakdown:")
        for i in range(len(s)):
            suffix = s[i:]
            common_len = 0
            for j in range(min(len(suffix), len(s))):
                if suffix[j] == s[j]:
                    common_len += 1
                else:
                    break
            print(f"  Position {i}: suffix='{suffix}' → common prefix length = {common_len}")
        
        result_bf = common_prefix_length_bruteforce(s)
        result_opt = common_prefix_length_optimized(s)
        
        print(f"Brute Force Result: {result_bf}")
        print(f"Optimized Result: {result_opt}")
        print(f"Z-array: {z_algorithm(s)}")
        print(f"Match: {result_bf == result_opt}")
        print("-" * 50)


def explain_z_algorithm_intuition():
    """
    Detailed explanation of Z-algorithm intuition with step-by-step example
    """
    s = "abcabcd"
    print(f"\n=== Z-Algorithm Intuition for '{s}' ===\n")
    
    print("The Z-algorithm maintains a 'Z-box' [l,r] - the rightmost segment that matches a prefix.")
    print("This allows us to reuse previous computations instead of comparing from scratch.\n")
    
    n = len(s)
    z = [0] * n
    z[0] = n
    l, r = 0, 0
    
    print(f"Initial: Z = {z}, l={l}, r={r}")
    print("Z[0] = length of string = 7\n")
    
    for i in range(1, n):
        print(f"Processing position {i} (character '{s[i]}'):")
        
        old_z_i = z[i]
        if i <= r:
            # Case 1: i is within current Z-box
            corresponding_pos = i - l
            z[i] = min(r - i + 1, z[corresponding_pos])
            print(f"  i={i} is within Z-box [l={l}, r={r}]")
            print(f"  Corresponding position in prefix: {corresponding_pos}")
            print(f"  Z[{corresponding_pos}] = {z[corresponding_pos]}")
            print(f"  Distance to end of Z-box: {r - i + 1}")
            print(f"  Initial Z[{i}] = min({r - i + 1}, {z[corresponding_pos]}) = {z[i]}")
        else:
            print(f"  i={i} is outside current Z-box, start from 0")
        
        # Try to extend
        original_z_i = z[i]
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            print(f"    Extending: s[{z[i]}]='{s[z[i]]}' == s[{i + z[i]}]='{s[i + z[i]]}'")
            z[i] += 1
        
        if z[i] != original_z_i:
            print(f"  Extended Z[{i}] from {original_z_i} to {z[i]}")
        
        # Update Z-box if needed
        if i + z[i] - 1 > r:
            old_l, old_r = l, r
            l, r = i, i + z[i] - 1
            print(f"  New Z-box: [{l}, {r}] (was [{old_l}, {old_r}])")
        
        print(f"  Final Z[{i}] = {z[i]}")
        print(f"  Current Z = {z[:i+1] + ['?'] * (n-i-1)}")
        print()
    
    print(f"Final Z-array: {z}")
    print(f"Sum = {sum(z)} (this is our answer!)")


if __name__ == "__main__":
    demonstrate_solutions()
    explain_z_algorithm_intuition()
