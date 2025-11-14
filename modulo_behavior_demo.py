#!/usr/bin/env python3
"""
Python Modulo Operator Behavior in Base -2 Conversion
=====================================================

This script demonstrates why the remainder in base -2 conversion
is never negative in Python.
"""

def demonstrate_python_modulo():
    """Show how Python's modulo operator works with negative numbers"""
    print("PYTHON MODULO OPERATOR BEHAVIOR")
    print("=" * 50)
    print("In Python: a % b always has the same sign as b (the divisor)")
    print("Since we use n % 2, and 2 is positive, result is always 0 or 1")
    print()
    
    # Test various numbers
    test_numbers = [5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5, -6]
    
    print("Number | n % 2 | n // 2 | -(n // 2)")
    print("-" * 40)
    
    for n in test_numbers:
        remainder = n % 2
        floor_div = n // 2
        neg_floor_div = -(n // 2)
        print(f"{n:6d} | {remainder:5d} | {floor_div:6d} | {neg_floor_div:8d}")
    
    print()
    print("Key observations:")
    print("1. n % 2 is ALWAYS 0 or 1, never negative")
    print("2. This is true even when n is negative")
    print("3. Python's // operator does floor division (rounds down)")


def compare_with_other_languages():
    """Show how this differs from other programming languages"""
    print("\nCOMPARISON WITH OTHER LANGUAGES")
    print("=" * 50)
    print("In some languages (C, Java, etc.), remainder has same sign as dividend:")
    print()
    print("Language | -5 % 2 | Python equivalent")
    print("-" * 40)
    print("C/Java   |     -1 | Use: n - 2 * (n // 2) = -5 - 2*(-3) = 1") 
    print("Python   |      1 | Direct: -5 % 2 = 1")
    print()
    print("Python's behavior is actually MORE convenient for base conversion!")


def demonstrate_algorithm_with_negative_numbers():
    """Show the base -2 algorithm working with negative numbers"""
    print("\nBASE -2 CONVERSION WITH NEGATIVE NUMBERS")
    print("=" * 50)
    
    def trace_conversion(n):
        print(f"\nTracing conversion of {n} to base -2:")
        print("-" * 30)
        
        if n == 0:
            return "0"
        
        original_n = n
        result = ""
        step = 1
        
        while n != 0:
            remainder = n % 2
            old_n = n
            n = -(n // 2)
            result = str(remainder) + result
            
            print(f"Step {step}: n={old_n}, r={old_n}%2={remainder}, new_n=-({old_n}//2)={n}, result='{result}'")
            step += 1
        
        # Verify
        print(f"\nVerification: '{result}' in base -2 equals {original_n}")
        total = sum(int(digit) * ((-2) ** i) for i, digit in enumerate(reversed(result)))
        print(f"Calculation: {' + '.join(f'{digit}×{(-2)**i}' for i, digit in enumerate(reversed(result)))} = {total}")
        print(f"✓ Correct!" if total == original_n else f"✗ Error!")
        
        return result
    
    # Test with negative numbers
    for num in [-1, -2, -3, -5]:
        trace_conversion(num)


def why_this_matters():
    """Explain why Python's modulo behavior is crucial for the algorithm"""
    print("\nWHY THIS MATTERS FOR THE ALGORITHM")
    print("=" * 50)
    print("1. Base -2 uses only digits 0 and 1 (binary digits)")
    print("2. If remainder could be negative, we'd need to handle -1 digits")
    print("3. Python's modulo ensures we always get 0 or 1")
    print("4. The -(n//2) step handles the 'negative base' part")
    print("5. This combination makes the algorithm elegant and correct")


if __name__ == "__main__":
    demonstrate_python_modulo()
    compare_with_other_languages()
    demonstrate_algorithm_with_negative_numbers()
    why_this_matters() 