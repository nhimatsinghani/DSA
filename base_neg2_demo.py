#!/usr/bin/env python3
"""
Base -2 Conversion Algorithm Explanation and Demo
================================================

This script demonstrates how to convert integers to base -2 representation.
In base -2, place values are powers of -2: 1, -2, 4, -8, 16, -32, ...
"""

def baseNeg2_original(n: int) -> str:
    """Original algorithm from the problem"""
    if n == 0:
        return "0"
    
    a = ""
    while n != 0:
        r = n % 2
        a = str(r) + a
        n = -(n // 2)
    return a


def baseNeg2_with_trace(n: int) -> str:
    """Same algorithm but with detailed step-by-step tracing"""
    print(f"\nConverting {n} to base -2:")
    print("=" * 40)
    
    if n == 0:
        print("Special case: n = 0, return '0'")
        return "0"
    
    original_n = n
    a = ""
    step = 1
    
    print("Place values in base -2: ..., 16, -8, 4, -2, 1")
    print("Algorithm: repeatedly take n%2 and update n = -(n//2)")
    print()
    
    while n != 0:
        r = n % 2
        old_a = a
        a = str(r) + a
        old_n = n
        n = -(n // 2)
        
        print(f"Step {step}:")
        print(f"  n = {old_n}")
        print(f"  r = {old_n} % 2 = {r}")
        print(f"  result = '{r}' + '{old_a}' = '{a}'")
        print(f"  new n = -({old_n} // 2) = {n}")
        print()
        step += 1
    
    print(f"Final result: '{a}'")
    
    # Verify the result
    verify_base_neg2(original_n, a)
    return a


def verify_base_neg2(original: int, base_neg2_str: str):
    """Verify that the base -2 representation is correct"""
    print(f"Verification for {original} = '{base_neg2_str}' in base -2:")
    
    total = 0
    for i, digit in enumerate(reversed(base_neg2_str)):
        place_value = (-2) ** i
        contribution = int(digit) * place_value
        total += contribution
        print(f"  Position {i}: {digit} × {place_value} = {contribution}")
    
    print(f"  Total: {total}")
    print(f"  ✓ Correct!" if total == original else f"  ✗ Error! Expected {original}")
    print()


def baseNeg2_simplified(n: int) -> str:
    """
    Simplified version with clear comments explaining each step
    
    The algorithm works by repeatedly:
    1. Extract the least significant bit (n % 2)
    2. Prepend it to our result string
    3. Update n by dividing by -2 (which is -(n // 2))
    """
    # Handle the special case
    if n == 0:
        return "0"
    
    result = ""
    
    while n != 0:
        # Get the remainder when dividing by 2 (always 0 or 1)
        bit = n % 2
        
        # Prepend this bit to our result
        result = str(bit) + result
        
        # Key insight: divide by -2, not +2
        # This is equivalent to -(n // 2)
        n = -(n // 2)
    
    return result


def demonstrate_multiple_examples():
    """Test the algorithm with various examples"""
    test_cases = [0, 1, 2, 3, 4, 5, 6, 10, -1, -2, -3]
    
    print("COMPREHENSIVE EXAMPLES")
    print("=" * 60)
    
    for num in test_cases:
        print(f"\nExample: Converting {num} to base -2")
        print("-" * 30)
        result = baseNeg2_with_trace(num)
        print(f"Result: {num} in base -2 is '{result}'")


if __name__ == "__main__":
    print("BASE -2 CONVERSION ALGORITHM EXPLANATION")
    print("=" * 50)
    
    print("\nWhat is Base -2?")
    print("In base -2, each position represents a power of -2:")
    print("Position:  ... 4   3   2   1   0")
    print("Value:     ... 16 -8   4  -2   1")
    print()
    
    # Start with a simple example
    print("Let's trace through converting 6 to base -2:")
    baseNeg2_with_trace(6)
    
    print("\n" + "="*60)
    print("COMPARING IMPLEMENTATIONS")
    print("="*60)
    
    test_num = 6
    orig_result = baseNeg2_original(test_num)
    simp_result = baseNeg2_simplified(test_num)
    
    print(f"Original algorithm result for {test_num}: '{orig_result}'")
    print(f"Simplified algorithm result for {test_num}: '{simp_result}'")
    print(f"Results match: {orig_result == simp_result}")
    
    # Ask user if they want to see more examples
    print(f"\nWould you like to see more examples? The script can demonstrate")
    print(f"conversions for: 0, 1, 2, 3, 4, 5, 6, 10, -1, -2, -3") 