"""
Find the K-th Character in String Game I - Bit Manipulation O(log k) Solution

Problem Understanding:
- Start with string "a"
- In each operation, append the string to itself, but with each character incremented by 1
- Round 0: "a"
- Round 1: "a" + "b" = "ab"  
- Round 2: "ab" + "bc" = "abbc"
- Round 3: "abbc" + "bccg" = "abbcbccg"
- Find the k-th character (1-indexed)

Key Insight: The string length doubles each round, so after n rounds we have 2^n characters.
We can determine which "generation" of characters the k-th position belongs to by looking at 
the binary representation of k-1 (converting to 0-indexed).

Bit Manipulation Approach:
Each bit in the binary representation of (k-1) tells us:
- 0: Take from the "original" part of that level
- 1: Take from the "incremented" part of that level

MATHEMATICAL INTUITION:
The key insight is that this problem creates a RECURSIVE BINARY TREE structure where:
- Each level represents a generation of string building
- Each position's "transformation history" is encoded in its binary representation
- The number of 1s = number of times the character was incremented
"""

def explainMathematicalIntuition():
    """
    Explain the mathematical reasoning behind why binary representation works
    """
    print("MATHEMATICAL INTUITION: Why Binary Representation Works")
    print("=" * 60)
    
    print("\n1. RECURSIVE STRUCTURE ANALYSIS:")
    print("-" * 40)
    print("At each round, we have: NEW_STRING = OLD_STRING + INCREMENT(OLD_STRING)")
    print("This creates a binary tree-like structure where each character has a 'history'")
    
    print("\n2. POSITION-TO-PATH MAPPING:")
    print("-" * 40)
    print("Each position in the final string corresponds to a unique path through the tree.")
    print("The binary representation of the position encodes this path!")
    
    print("\nLet's trace how position 5 (0-indexed: 4) gets its value:")
    print("Position 4 in binary: 100")
    print("Reading right-to-left (least significant bit first):")
    print("  Bit 0 = 0: At level 0, take from 'original' part")
    print("  Bit 1 = 0: At level 1, take from 'original' part") 
    print("  Bit 2 = 1: At level 2, take from 'incremented' part")
    print("  Total increments = number of 1s = 1")
    print("  Result: 'a' + 1 increment = 'b'")


def visualizeRecursiveStructure():
    """
    Visualize how the recursive structure maps to binary representation
    """
    print("\n3. RECURSIVE TREE VISUALIZATION:")
    print("-" * 40)
    
    print("Round 0: a")
    print("Round 1: a|b  (original|incremented)")
    print("Round 2: ab|bc (original|incremented)")
    print("Round 3: abbc|bccg (original|incremented)")
    
    print("\nPosition mapping (0-indexed):")
    positions = [
        (0, "000", "a", "original→original→original"),
        (1, "001", "b", "original→original→incremented"), 
        (2, "010", "b", "original→incremented→original"),
        (3, "011", "c", "original→incremented→incremented"),
        (4, "100", "b", "incremented→original→original"),
        (5, "101", "c", "incremented→original→incremented"),
        (6, "110", "c", "incremented→incremented→original"),
        (7, "111", "d", "incremented→incremented→incremented")
    ]
    
    for pos, binary, char, path in positions:
        ones_count = binary.count('1')
        print(f"Position {pos}: {binary} → '{char}' (path: {path}, increments: {ones_count})")


def proveTheorem():
    """
    Mathematical proof of why the algorithm works
    """
    print("\n4. MATHEMATICAL PROOF:")
    print("-" * 40)
    
    print("THEOREM: For position k (0-indexed), the character value is:")
    print("character = 'a' + (number of 1s in binary representation of k)")
    
    print("\nPROOF BY INDUCTION:")
    print("Base case (k=0): binary=0, no 1s, character='a' ✓")
    print("Base case (k=1): binary=1, one 1, character='b' ✓")
    
    print("\nInductive step:")
    print("Assume theorem holds for all positions < 2^n")
    print("For any position k in range [2^n, 2^(n+1)):")
    print("- k can be written as k = 2^n + j where j < 2^n")
    print("- Binary of k = '1' + binary(j)")
    print("- Number of 1s in k = 1 + (number of 1s in j)")
    print("- Character at k = character at j + 1 increment")
    print("- By inductive hypothesis: character = 'a' + (1s in j) + 1")
    print("- This equals 'a' + (1s in k) ✓")


def demonstrateRecursivePattern():
    """
    Show the recursive pattern that creates the binary structure
    """
    print("\n5. THE RECURSIVE PATTERN:")
    print("-" * 40)
    
    def build_string_recursive(rounds):
        if rounds == 0:
            return "a"
        
        prev = build_string_recursive(rounds - 1)
        incremented = ''.join(chr(ord(c) + 1) for c in prev)
        return prev + incremented
    
    def analyze_string(s, round_num):
        print(f"Round {round_num}: '{s}'")
        if len(s) > 1:
            mid = len(s) // 2
            original = s[:mid]
            incremented = s[mid:]
            print(f"  Original part: '{original}'")
            print(f"  Incremented part: '{incremented}'")
            print(f"  Each char in incremented = corresponding char in original + 1")
    
    for i in range(4):
        s = build_string_recursive(i)
        analyze_string(s, i)
        print()


def explainBitPositionMeaning():
    """
    Explain what each bit position represents
    """
    print("6. WHAT EACH BIT POSITION MEANS:")
    print("-" * 40)
    
    print("For position k with binary representation b_n b_(n-1) ... b_1 b_0:")
    print("- b_0 (rightmost): Did we take incremented part in round 1?")
    print("- b_1: Did we take incremented part in round 2?") 
    print("- b_i: Did we take incremented part in round (i+1)?")
    print("- Each '1' bit adds exactly 1 to the character value")
    print("- Total increments = sum of all bits = number of 1s")
    
    print("\nExample: Position 6 (binary: 110)")
    print("- b_0 = 0: Original part in round 1 → no increment")
    print("- b_1 = 1: Incremented part in round 2 → +1 increment") 
    print("- b_2 = 1: Incremented part in round 3 → +1 increment")
    print("- Total: 0 + 1 + 1 = 2 increments")
    print("- Character: 'a' + 2 = 'c'")


def kthCharacter(k):
    """
    Find the k-th character using bit manipulation - O(log k) time, O(1) space
    
    Args:
        k (int): 1-indexed position of character to find
        
    Returns:
        str: The k-th character
    """
    # Convert to 0-indexed
    k -= 1
    
    # Start with 'a' (ASCII value 97)
    result = ord('a')
    
    # Process each bit of k from right to left
    # Each bit represents a "generation" of the string construction
    while k > 0:
        # If the least significant bit is 1, it means we're in the "incremented" part
        if k & 1:
            result += 1
        
        # Right shift to process the next bit
        k >>= 1
    
    return chr(result)


def kthCharacterVerbose(k):
    """
    Verbose version with step-by-step explanation for learning
    """
    print(f"Finding {k}-th character (1-indexed)")
    
    # Convert to 0-indexed
    k_zero_indexed = k - 1
    print(f"0-indexed position: {k_zero_indexed}")
    print(f"Binary representation of {k_zero_indexed}: {bin(k_zero_indexed)}")
    
    result = ord('a')
    current_char = chr(result)
    print(f"Starting with: '{current_char}' (ASCII {result})")
    
    temp_k = k_zero_indexed
    generation = 0
    
    while temp_k > 0:
        bit = temp_k & 1
        print(f"Generation {generation}: bit = {bit}")
        
        if bit == 1:
            result += 1
            print(f"  Bit is 1 -> increment character: '{chr(result)}' (ASCII {result})")
        else:
            print(f"  Bit is 0 -> keep character: '{chr(result)}' (ASCII {result})")
        
        temp_k >>= 1
        generation += 1
    
    final_char = chr(result)
    print(f"Final result: '{final_char}'")
    return final_char


def demonstrateStringGeneration(rounds=4):
    """
    Demonstrate how the string is built to understand the pattern
    """
    print("String Generation Process:")
    print("=" * 40)
    
    strings = ["a"]
    print(f"Round 0: '{strings[0]}'")
    
    for i in range(1, rounds + 1):
        prev = strings[-1]
        # Increment each character in the previous string
        incremented = ''.join(chr(ord(c) + 1) for c in prev)
        new_string = prev + incremented
        strings.append(new_string)
        print(f"Round {i}: '{new_string}' (length: {len(new_string)})")
    
    return strings


def explainBitManipulation():
    """
    Explain the bit manipulation approach with examples
    """
    print("\nBit Manipulation Explanation:")
    print("=" * 40)
    
    examples = [1, 2, 3, 4, 5, 6, 7, 8]
    
    for k in examples:
        print(f"\nExample: k = {k}")
        k_zero = k - 1
        binary = bin(k_zero)[2:]  # Remove '0b' prefix
        print(f"  k-1 = {k_zero}, binary = {binary}")
        
        result = ord('a')
        print(f"  Start with 'a' (ASCII {result})")
        
        # Process bits from right to left
        for i, bit in enumerate(reversed(binary)):
            if bit == '1':
                result += 1
                print(f"  Bit {i} (from right) = 1 -> increment to '{chr(result)}'")
            else:
                print(f"  Bit {i} (from right) = 0 -> keep '{chr(result)}'")
        
        final_result = kthCharacter(k)
        print(f"  Final result: '{final_result}'")


if __name__ == "__main__":
    # Mathematical intuition explanation
    explainMathematicalIntuition()
    visualizeRecursiveStructure()
    proveTheorem()
    demonstrateRecursivePattern()
    explainBitPositionMeaning()
    
    print("\n" + "=" * 60)
    print("PRACTICAL EXAMPLES")
    print("=" * 60)
    
    # Demonstrate string generation
    strings = demonstrateStringGeneration(3)
    
    print("\n" + "=" * 50)
    print("TESTING EXAMPLES")
    print("=" * 50)
    
    # Test examples
    test_cases = [1, 2, 3, 4, 5, 6, 7, 8]
    
    for k in test_cases:
        result = kthCharacter(k)
        print(f"k = {k}: '{result}'")
    
    print("\n" + "=" * 50)
    print("DETAILED BIT MANIPULATION EXPLANATION")
    print("=" * 50)
    explainBitManipulation()
    
    print("\n" + "=" * 50)
    print("VERBOSE EXAMPLE")
    print("=" * 50)
    kthCharacterVerbose(5)
