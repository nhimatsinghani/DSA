#!/usr/bin/env python3
"""
Solving the Critical Transcendental Equation in Bloom Filter Optimization

This script shows multiple approaches to solve:
(1 - e^(-α)) × ln(1 - e^(-α)) + α × e^(-α) = 0

And proves that the solution is e^(-α) = 1/2, or α = ln(2).
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve, brentq


def section_1_equation_setup():
    """Set up the transcendental equation we need to solve."""
    print("🔍 Solving the Critical Transcendental Equation")
    print("=" * 80)
    print("We derived that the optimal α satisfies:")
    print("(1 - e^(-α)) × ln(1 - e^(-α)) + α × e^(-α) = 0")
    print()
    
    print("This is a transcendental equation - it cannot be solved algebraically.")
    print("We need numerical methods or mathematical insight to find the solution.")
    print()
    
    print("Let's explore multiple approaches to solve this equation:")
    print("1. Substitution method")
    print("2. Numerical root finding")
    print("3. Graphical analysis")
    print("4. Mathematical insight via symmetry")
    print()


def section_2_substitution_method():
    """Use substitution to simplify the equation."""
    print("🎯 Method 1: Substitution Analysis")
    print("=" * 60)
    
    print("Step 1: Make substitution u = e^(-α)")
    print("• Since α > 0, we have 0 < u < 1")
    print("• Also, α = -ln(u)")
    print()
    
    print("Step 2: Substitute into our equation")
    print("Original: (1 - e^(-α)) × ln(1 - e^(-α)) + α × e^(-α) = 0")
    print("Becomes: (1 - u) × ln(1 - u) + (-ln(u)) × u = 0")
    print()
    
    print("Step 3: Rearrange")
    print("(1 - u) × ln(1 - u) - u × ln(u) = 0")
    print("(1 - u) × ln(1 - u) = u × ln(u)")
    print()
    
    print("Step 4: This can be written as")
    print("ln(1 - u)^(1-u) = ln(u^u)")
    print("(1 - u)^(1-u) = u^u")
    print()
    
    print("🔍 Testing u = 1/2:")
    u = 0.5
    left_side = (1 - u) * math.log(1 - u)
    right_side = u * math.log(u)
    
    print(f"Left side: (1 - {u}) × ln(1 - {u}) = {left_side:.6f}")
    print(f"Right side: {u} × ln({u}) = {right_side:.6f}")
    print(f"Difference: {abs(left_side - right_side):.10f}")
    print()
    
    print("✅ Perfect match! So u = 1/2 is indeed the solution.")
    print("Therefore: e^(-α) = 1/2, which gives α = ln(2) ≈ 0.693")


def section_3_numerical_methods():
    """Use numerical methods to find the root."""
    print(f"\n🎯 Method 2: Numerical Root Finding")
    print("=" * 60)
    
    def f(alpha):
        """The function whose root we want to find."""
        exp_neg_alpha = math.exp(-alpha)
        term1 = (1 - exp_neg_alpha) * math.log(1 - exp_neg_alpha)
        term2 = alpha * exp_neg_alpha
        return term1 + term2
    
    print("Define f(α) = (1 - e^(-α)) × ln(1 - e^(-α)) + α × e^(-α)")
    print("We want to find α such that f(α) = 0")
    print()
    
    # Test some values around the expected solution
    test_alphas = [0.5, 0.6, 0.693, 0.7, 0.8]
    print("Testing values around the expected solution:")
    print(f"{'α':<8} {'f(α)':<12} {'Note':<15}")
    print("-" * 35)
    
    for alpha in test_alphas:
        try:
            value = f(alpha)
            note = "← CLOSE TO ZERO" if abs(value) < 0.001 else ""
            print(f"{alpha:<8.3f} {value:<12.6f} {note}")
        except:
            print(f"{alpha:<8.3f} {'undefined':<12} {'domain error'}")
    
    print()
    
    # Use numerical root finding
    try:
        # Using scipy's brentq (bracket method)
        root = brentq(f, 0.1, 1.5)
        print(f"Numerical solution using Brent's method: α = {root:.10f}")
        print(f"ln(2) = {math.log(2):.10f}")
        print(f"Difference: {abs(root - math.log(2)):.12f}")
        print()
        
        # Verify the solution
        print(f"Verification: f({root:.6f}) = {f(root):.2e}")
        
    except Exception as e:
        print(f"Numerical method failed: {e}")


def section_4_graphical_analysis():
    """Visualize the function to understand the root."""
    print(f"\n🎯 Method 3: Graphical Analysis")
    print("=" * 60)
    
    def f(alpha):
        """The function whose root we want to find."""
        if alpha <= 0:
            return float('inf')
        exp_neg_alpha = math.exp(-alpha)
        if exp_neg_alpha >= 1:
            return float('inf')
        try:
            term1 = (1 - exp_neg_alpha) * math.log(1 - exp_neg_alpha)
            term2 = alpha * exp_neg_alpha
            return term1 + term2
        except:
            return float('inf')
    
    # Create range of alpha values
    alphas = np.linspace(0.1, 2.0, 1000)
    f_values = []
    
    for alpha in alphas:
        try:
            f_val = f(alpha)
            if abs(f_val) < 100:  # Avoid extreme values for plotting
                f_values.append(f_val)
            else:
                f_values.append(float('nan'))
        except:
            f_values.append(float('nan'))
    
    # Find where function crosses zero
    zero_crossings = []
    for i in range(len(f_values)-1):
        if not (np.isnan(f_values[i]) or np.isnan(f_values[i+1])):
            if f_values[i] * f_values[i+1] < 0:  # Sign change
                zero_crossings.append(alphas[i])
    
    print("Analysis of f(α) = (1 - e^(-α)) × ln(1 - e^(-α)) + α × e^(-α)")
    print()
    
    if zero_crossings:
        print(f"Zero crossing detected near α ≈ {zero_crossings[0]:.6f}")
        print(f"ln(2) = {math.log(2):.6f}")
        print(f"Difference: {abs(zero_crossings[0] - math.log(2)):.8f}")
    
    try:
        # Create the plot
        plt.figure(figsize=(10, 6))
        
        plt.subplot(1, 2, 1)
        plt.plot(alphas, f_values, 'b-', linewidth=2, label='f(α)')
        plt.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        plt.axvline(x=math.log(2), color='r', linestyle='--', alpha=0.7, label=f'α = ln(2) ≈ {math.log(2):.3f}')
        plt.xlabel('α')
        plt.ylabel('f(α)')
        plt.title('Finding Root of Transcendental Equation')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.ylim(-0.1, 0.1)
        
        # Zoom in around the root
        plt.subplot(1, 2, 2)
        zoom_range = (alphas >= 0.5) & (alphas <= 0.9)
        plt.plot(alphas[zoom_range], np.array(f_values)[zoom_range], 'b-', linewidth=2)
        plt.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        plt.axvline(x=math.log(2), color='r', linestyle='--', alpha=0.7, label=f'α = ln(2)')
        plt.xlabel('α')
        plt.ylabel('f(α)')
        plt.title('Zoomed View Around Root')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('transcendental_equation_analysis.png', dpi=150, bbox_inches='tight')
        print("\nGraphical analysis saved as 'transcendental_equation_analysis.png'")
        
    except ImportError:
        print("Plotting requires matplotlib (already installed)")
    except Exception as e:
        print(f"Plotting failed: {e}")


def section_5_mathematical_insight():
    """Provide mathematical insight into why the solution is α = ln(2)."""
    print(f"\n🎯 Method 4: Mathematical Insight and Symmetry")
    print("=" * 60)
    
    print("The equation (1 - u) × ln(1 - u) = u × ln(u) has a beautiful interpretation:")
    print()
    
    print("🔍 Entropy Connection:")
    print("This equation is related to the entropy function H(p) = -p ln(p)")
    print("We're looking for the point where:")
    print("(1-u) × ln(1-u) = u × ln(u)")
    print()
    
    print("🎯 Symmetry Argument:")
    print("Consider the function g(u) = u × ln(u)")
    print("We want: g(1-u) = g(u)")
    print()
    
    print("Testing u = 1/2:")
    u = 0.5
    g_u = u * math.log(u)
    g_1_minus_u = (1-u) * math.log(1-u)
    
    print(f"g({u}) = {u} × ln({u}) = {g_u:.6f}")
    print(f"g({1-u}) = {1-u} × ln({1-u}) = {g_1_minus_u:.6f}")
    print(f"Equal? {abs(g_u - g_1_minus_u) < 1e-10}")
    print()
    
    print("🎭 The Deeper Meaning:")
    print("At the optimum, the bit array is exactly half full!")
    print("This creates perfect balance in the entropy contributions.")
    print()
    
    print("✨ Physical Interpretation:")
    print("• Each bit has probability 1/2 of being set")
    print("• This maximizes the 'randomness' of the bit pattern")
    print("• It's the most 'efficient' use of the available bits")
    print("• Any deviation from 1/2 increases the false positive rate")


def section_6_verification_and_implications():
    """Verify the solution and discuss implications."""
    print(f"\n🎯 Section 6: Verification and Implications")
    print("=" * 60)
    
    print("🔬 Complete Verification:")
    alpha_optimal = math.log(2)
    exp_neg_alpha = math.exp(-alpha_optimal)
    
    print(f"α_optimal = ln(2) = {alpha_optimal:.10f}")
    print(f"e^(-α_optimal) = e^(-ln(2)) = 1/2 = {exp_neg_alpha:.10f}")
    print()
    
    # Verify the original equation
    term1 = (1 - exp_neg_alpha) * math.log(1 - exp_neg_alpha)
    term2 = alpha_optimal * exp_neg_alpha
    total = term1 + term2
    
    print("Substituting back into the original equation:")
    print("(1 - e^(-α)) × ln(1 - e^(-α)) + α × e^(-α)")
    print(f"= ({1 - exp_neg_alpha:.6f}) × ln({1 - exp_neg_alpha:.6f}) + {alpha_optimal:.6f} × {exp_neg_alpha:.6f}")
    print(f"= {term1:.10f} + {term2:.10f}")
    print(f"= {total:.2e}")
    print()
    
    print("✅ Essentially zero! Our solution is correct.")
    print()
    
    print("🎯 Key Implications:")
    print("1. At optimum: P(bit = 1) = 1 - e^(-α) = 1 - 1/2 = 0.5")
    print("2. The bit array is exactly half full")
    print("3. This gives k_optimal = (m/n) × ln(2) ≈ 0.693 × (m/n)")
    print("4. The constant ln(2) appears because of this fundamental balance")
    print()
    
    print("🌟 The Universal Constants:")
    print(f"• ln(2) ≈ {math.log(2):.6f} (fundamental to optimal k)")
    print(f"• (ln(2))² ≈ {math.log(2)**2:.6f} (fundamental to optimal m)")
    print(f"• 1/((ln(2))²) ≈ {1/(math.log(2)**2):.6f} (bits per element factor)")


def main():
    """Run the complete analysis."""
    section_1_equation_setup()
    section_2_substitution_method()
    section_3_numerical_methods()
    section_4_graphical_analysis()
    section_5_mathematical_insight()
    section_6_verification_and_implications()
    
    print(f"\n✨ Summary: Solving the Transcendental Equation")
    print("=" * 80)
    print("🎓 We showed that the equation:")
    print("   (1 - e^(-α)) × ln(1 - e^(-α)) + α × e^(-α) = 0")
    print()
    print("🎯 Has the solution:")
    print("   e^(-α) = 1/2, therefore α = ln(2)")
    print()
    print("🔍 Using four different approaches:")
    print("   1. Algebraic substitution u = e^(-α)")
    print("   2. Numerical root finding")
    print("   3. Graphical analysis")
    print("   4. Symmetry and entropy arguments")
    print()
    print("🌟 The key insight: At optimum, the bit array is exactly half full!")
    print("   This fundamental balance leads to all the optimal formulas.")


if __name__ == "__main__":
    main() 