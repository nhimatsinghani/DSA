#!/usr/bin/env python3
"""
Stock Profit Maximization: Greedy vs Dynamic Programming Analysis

This script demonstrates why a greedy approach fails for the stock profit maximization
problem and shows the correct dynamic programming solution.
"""

from typing import List


def greedy_solution(present: List[int], future: List[int], budget: int) -> int:
    """
    Greedy approach: Always pick stocks with highest profit first.
    This approach FAILS for some cases.
    """
    n = len(present)
    # Create (profit, cost) pairs
    diff = [(future[i] - present[i], present[i]) for i in range(n)]
    
    # Sort by profit descending, then by cost ascending for ties
    diff.sort(key=lambda x: (x[0], -x[1]), reverse=True)
    
    res = 0
    for profit, cost in diff:
        if cost <= budget and profit > 0:
            res += profit
            budget -= cost
    
    return res


def dp_solution(present: List[int], future: List[int], budget: int) -> int:
    """
    Dynamic Programming approach: 0/1 Knapsack solution.
    This gives the correct answer for all cases.
    """
    n = len(present)
    
    # dp[i][w] = maximum profit using first i stocks with budget w
    dp = [[0] * (budget + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        cost = present[i - 1]
        profit = max(0, future[i - 1] - present[i - 1])  # Only consider profitable stocks
        
        for w in range(budget + 1):
            # Don't take current stock
            dp[i][w] = dp[i - 1][w]
            
            # Take current stock if we can afford it
            if w >= cost:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - cost] + profit)
    
    return dp[n][budget]


def analyze_counterexample():
    """
    Demonstrates a case where greedy fails but DP succeeds.
    """
    print("=== COUNTEREXAMPLE ANALYSIS ===")
    print()
    
    # Clear counterexample where greedy definitively fails
    present = [1, 1, 2]
    future = [3, 3, 5] 
    budget = 2
    
    print(f"Present prices: {present}")
    print(f"Future prices:  {future}")
    print(f"Budget: {budget}")
    print()
    
    # Calculate profits for each stock
    profits = [future[i] - present[i] for i in range(len(present))]
    print("Stock analysis:")
    for i in range(len(present)):
        print(f"  Stock {i}: Cost={present[i]}, Profit={profits[i]}, Profit/Cost ratio={profits[i]/present[i]:.2f}")
    print()
    
    print("WHY THIS IS A PERFECT COUNTEREXAMPLE:")
    print("  - Stock 2 has highest individual profit (3)")
    print("  - But stocks 0+1 together give higher profit (2+2=4)")
    print("  - Greedy takes stock 2, gets profit 3")
    print("  - Optimal takes stocks 0+1, gets profit 4")
    print()
    
    # Greedy approach
    greedy_result = greedy_solution(present, future, budget)
    print(f"Greedy solution result: {greedy_result}")
    
    # Show greedy decision process
    diff = [(future[i] - present[i], present[i], i) for i in range(len(present))]
    diff.sort(key=lambda x: (x[0], -x[1]), reverse=True)
    print("Greedy selection process:")
    remaining_budget = budget
    selected_stocks = []
    for profit, cost, idx in diff:
        if cost <= remaining_budget and profit > 0:
            print(f"  ✓ Select Stock {idx}: Cost={cost}, Profit={profit}, Remaining budget={remaining_budget-cost}")
            remaining_budget -= cost
            selected_stocks.append(idx)
        else:
            print(f"  ✗ Skip Stock {idx}: Cost={cost}, Profit={profit}, Not enough budget (need {cost}, have {remaining_budget})")
    print(f"Greedy selected stocks: {selected_stocks}")
    print()
    
    # DP approach
    dp_result = dp_solution(present, future, budget)
    print(f"DP solution result: {dp_result}")
    print()
    
    # Find optimal combination for DP
    print("Checking all possible combinations:")
    max_profit = 0
    best_combination = []
    
    # Check all 2^n combinations
    for mask in range(1 << len(present)):
        total_cost = 0
        total_profit = 0
        combination = []
        
        for i in range(len(present)):
            if mask & (1 << i):
                total_cost += present[i]
                if future[i] > present[i]:  # Only count profitable stocks
                    total_profit += future[i] - present[i]
                combination.append(i)
        
        if total_cost <= budget:
            print(f"  Combination {combination}: Cost={total_cost}, Profit={total_profit}")
            if total_profit > max_profit:
                max_profit = total_profit
                best_combination = combination
    
    print(f"Optimal combination: {best_combination} with profit {max_profit}")
    print()
    
    return greedy_result, dp_result


def explain_why_greedy_fails():
    """
    Explains the fundamental reason why greedy fails.
    """
    print("=== WHY GREEDY FAILS ===")
    print()
    print("1. GREEDY FLAW: Local vs Global Optimality")
    print("   - Greedy makes locally optimal choices (highest profit first)")
    print("   - But local optimality doesn't guarantee global optimality")
    print("   - Taking one high-profit expensive item might prevent taking")
    print("     multiple cheaper items with higher combined profit")
    print()
    
    print("2. BUDGET CONSTRAINT INTERACTION:")
    print("   - The budget constraint creates dependencies between choices")
    print("   - Choosing one expensive stock affects what other stocks we can buy")
    print("   - Greedy doesn't consider these future constraints")
    print()
    
    print("3. KNAPSACK PROBLEM STRUCTURE:")
    print("   - Items: Stocks")
    print("   - Weights: Present prices (costs)")
    print("   - Values: Profits (future - present)")
    print("   - Capacity: Budget")
    print("   - Constraint: Can take each item at most once (0/1 knapsack)")
    print()
    
    print("4. WHY DP WORKS:")
    print("   - Considers ALL possible combinations")
    print("   - Uses optimal substructure: optimal solution contains optimal solutions to subproblems")
    print("   - Handles overlapping subproblems efficiently with memoization")
    print()


def demonstrate_multiple_cases():
    """
    Shows multiple test cases to further illustrate the difference.
    """
    print("=== MULTIPLE TEST CASES ===")
    print()
    
    test_cases = [
        {
            "name": "Case 1: Greedy works - aligned incentives",
            "present": [5, 10, 15],
            "future": [20, 15, 25],
            "budget": 30
        },
        {
            "name": "Case 2: GREEDY FAILS - high profit item vs multiple small profits",
            "present": [1, 1, 2],
            "future": [3, 3, 5],
            "budget": 2
        },
        {
            "name": "Case 3: GREEDY FAILS - expensive item blocks optimal combination",
            "present": [2, 3, 5],
            "future": [5, 7, 11],
            "budget": 5
        },
        {
            "name": "Case 4: GREEDY FAILS - three small vs one big",
            "present": [1, 1, 1, 3],
            "future": [2, 2, 2, 6],
            "budget": 3
        },
    ]
    
    for case in test_cases:
        print(f"{case['name']}:")
        print(f"  Present: {case['present']}")
        print(f"  Future:  {case['future']}")
        print(f"  Budget:  {case['budget']}")
        
        greedy_result = greedy_solution(case['present'], case['future'], case['budget'])
        dp_result = dp_solution(case['present'], case['future'], case['budget'])
        
        print(f"  Greedy result: {greedy_result}")
        print(f"  DP result:     {dp_result}")
        
        if greedy_result == dp_result:
            print("  ✓ Greedy works for this case")
        else:
            print(f"  ✗ Greedy fails! Difference: {dp_result - greedy_result}")
        print()


if __name__ == "__main__":
    print("STOCK PROFIT MAXIMIZATION: GREEDY vs DYNAMIC PROGRAMMING")
    print("=" * 60)
    print()
    
    analyze_counterexample()
    explain_why_greedy_fails()
    demonstrate_multiple_cases()
    
    print("CONCLUSION:")
    print("The greedy approach fails because it makes locally optimal decisions")
    print("without considering the global constraint optimization problem.")
    print("This is fundamentally a 0/1 knapsack problem requiring dynamic programming.") 