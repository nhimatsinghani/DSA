"""
Rolling Hash Solution for Repeated DNA Sequences
==============================================

Problem Statement:
The DNA sequence is composed of a series of nucleotides abbreviated as 'A', 'C', 'G', and 'T'.
Given a string s that represents a DNA sequence, return all the 10-letter-long sequences 
(substrings) that occur more than once in a DNA molecule.

Example:
Input: s = "AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT"
Output: ["AAAAACCCCC","CCCCCAAAAA"]

Rolling Hash Approach:
=====================

The key insight is to use a rolling hash to efficiently compute hash values for all 10-letter
substrings without recalculating from scratch each time.

Algorithm Overview:
1. Map each nucleotide to a number: A=0, C=1, G=2, T=3
2. Treat each 10-letter sequence as a base-4 number
3. Use sliding window with rolling hash to compute hash for each position
4. Track frequency of each hash value
5. Return substrings that appear more than once

Mathematical Foundation:
-----------------------
For a sequence like "ACGT", the hash would be:
hash = A*4³ + C*4² + G*4¹ + T*4⁰ = 0*64 + 1*16 + 2*4 + 3*1 = 27

For rolling hash when sliding window:
- Add new character: hash = hash * 4 + new_char_value
- Remove old character: hash = hash - old_char_value * 4^(window_size-1)

Time Complexity: O(n) where n is length of string
Space Complexity: O(n) for storing hash counts and results

Detailed Step-by-Step Example:
=============================
Let's trace through "AAAAACCCCC" (first 10 chars of example):

Position 0: A -> hash = 0*4^0 = 0
Position 1: AA -> hash = 0*4^1 + 0*4^0 = 0  
Position 2: AAA -> hash = 0*4^2 + 0*4^1 + 0*4^0 = 0
...
Position 9: AAAAACCCCC -> hash = 0*4^9 + 0*4^8 + ... + 1*4^1 + 1*4^0 = 5

When sliding to next window "AAAAACCCCCA":
- Add new 'A': hash = hash * 4 + 0 = 5 * 4 + 0 = 20
- Remove old 'A': hash = hash - 0 * 4^9 = 20 - 0 = 20

This demonstrates how rolling hash avoids recalculating the entire hash.
"""

from collections import defaultdict

class Solution(object):
    def getVal(self, c):
        """
        Maps nucleotides to integers for base-4 representation.
        
        Args:
            c (str): Single nucleotide character
            
        Returns:
            int: Mapped value (A=0, C=1, G=2, T=3)
        """
        if c == 'A': return 0
        if c == 'C': return 1
        if c == 'G': return 2
        return 3  # T

    def findRepeatedDnaSequences(self, s):
        """
        Finds all 10-letter DNA sequences that occur more than once using rolling hash.
        
        Args:
            s (str): DNA sequence string
            
        Returns:
            List[str]: List of repeated 10-letter sequences
            
        Algorithm Breakdown:
        1. Initialize hash counter and result list
        2. Compute rolling hash for sliding 10-letter window
        3. For each position >= 9 (complete 10-letter window):
           a. Increment count for current hash
           b. If count becomes 2, add substring to result
           c. Remove leftmost character from hash for next iteration
        """
        n = len(s)
        if n < 10:
            return []
            
        cnt = defaultdict(int)  # Hash value -> count mapping
        ans = []                # Result list for repeated sequences
        
        dnaHash = 0            # Rolling hash value
        POWN1 = 4 ** 9         # 4^9 = power to remove leftmost character
        
        # Process each character in the string
        for i in range(n):
            # Add current character to rolling hash
            # Equivalent to: hash = hash * base + new_digit
            dnaHash = dnaHash * 4 + self.getVal(s[i])
            
            # Process complete 10-letter windows (i >= 9)
            if i >= 9:
                # Increment count for this hash value
                cnt[dnaHash] += 1
                
                # If this is the second occurrence, add to result
                if cnt[dnaHash] == 2:
                    ans.append(s[i-9:i+1])  # Extract 10-letter substring
                
                # Remove leftmost character for next iteration
                # Subtract: leftmost_char * 4^9 to remove its contribution
                dnaHash -= POWN1 * self.getVal(s[i-9])

        return ans


def demonstrate_solution():
    """
    Demonstrates the solution with examples and detailed tracing.
    """
    solution = Solution()
    
    # Test case 1: Given example
    test1 = "AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT"
    result1 = solution.findRepeatedDnaSequences(test1)
    print(f"Input: {test1}")
    print(f"Output: {result1}")
    print(f"Expected: ['AAAAACCCCC', 'CCCCCAAAAA']")
    print()
    
    # Test case 2: Simple case
    test2 = "AAAAAAAAAAAAA"  # All A's
    result2 = solution.findRepeatedDnaSequences(test2)
    print(f"Input: {test2}")
    print(f"Output: {result2}")
    print(f"Expected: ['AAAAAAAAAA'] (appears 4 times)")
    print()
    
    # Test case 3: No repeats
    test3 = "ACGTACGTAC"
    result3 = solution.findRepeatedDnaSequences(test3)
    print(f"Input: {test3}")
    print(f"Output: {result3}")
    print(f"Expected: [] (no 10-letter repeats)")
    print()


def trace_rolling_hash_example():
    """
    Traces through rolling hash calculation for educational purposes.
    """
    s = "AAAAACCCCC"
    solution = Solution()
    
    print("Rolling Hash Trace for 'AAAAACCCCC':")
    print("=" * 50)
    
    dnaHash = 0
    POWN1 = 4 ** 9
    
    for i in range(len(s)):
        old_hash = dnaHash
        char_val = solution.getVal(s[i])
        dnaHash = dnaHash * 4 + char_val
        
        print(f"Position {i}: char='{s[i]}' (val={char_val})")
        print(f"  Hash update: {old_hash} * 4 + {char_val} = {dnaHash}")
        
        if i >= 9:
            substring = s[i-9:i+1]
            print(f"  Complete window: '{substring}' -> hash = {dnaHash}")
            
            if i < len(s) - 1:  # Not the last iteration
                remove_char = s[i-9]
                remove_val = solution.getVal(remove_char)
                new_hash = dnaHash - POWN1 * remove_val
                print(f"  Remove '{remove_char}' (val={remove_val}): {dnaHash} - {POWN1}*{remove_val} = {new_hash}")
                dnaHash = new_hash
        print()


if __name__ == "__main__":
    print("Rolling Hash Solution for Repeated DNA Sequences")
    print("=" * 60)
    print()
    
    # Run demonstrations
    demonstrate_solution()
    
    print("\nDetailed Hash Calculation Trace:")
    print("=" * 60)
    trace_rolling_hash_example()
    
    print("\nKey Insights:")
    print("=" * 60)
    print("1. Rolling hash avoids O(n²) substring comparisons")
    print("2. Base-4 encoding naturally fits DNA's 4-nucleotide alphabet")
    print("3. Hash collisions are rare for 10-character strings in base-4")
    print("4. Time complexity: O(n), Space complexity: O(n)")
    print("5. Alternative: use bit manipulation with 2 bits per nucleotide")
