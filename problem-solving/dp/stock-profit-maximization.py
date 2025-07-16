"""
Stock Profit Maximization - Dynamic Programming Solution

Problem: Given present and future prices of stocks and a budget, maximize profit.
This is a classic 0/1 Knapsack problem where:
- Items = Stocks
- Weights = Present prices (costs)
- Values = Profits (future - present)
- Capacity = Budget
"""

from typing import List


def maximumProfit(present: List[int], future: List[int], budget: int) -> int:
    """
    Correct solution using Dynamic Programming (0/1 Knapsack).
    
    Time Complexity: O(n * budget)
    Space Complexity: O(n * budget)
    """
    n = len(present)
    
    # dp[i][w] = maximum profit using first i stocks with budget w
    dp = [[0] * (budget + 1) for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        cost = present[i - 1]
        profit = max(0, future[i - 1] - present[i - 1])  # Only profitable stocks
        
        for w in range(budget + 1):
            # Option 1: Don't take current stock
            dp[i][w] = dp[i - 1][w]
            
            # Option 2: Take current stock if we can afford it and it's profitable
            if w >= cost and profit > 0:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - cost] + profit)
    
    return dp[n][budget]


def maximumProfitOptimized(present: List[int], future: List[int], budget: int) -> int:
    """
    Space-optimized version using 1D DP array.
    
    Time Complexity: O(n * budget)
    Space Complexity: O(budget)
    """
    n = len(present)
    
    # Only need current and previous row
    dp = [0] * (budget + 1)
    
    for i in range(n):
        cost = present[i]
        profit = max(0, future[i] - present[i])
        
        # Iterate backwards to avoid using updated values
        for w in range(budget, cost - 1, -1):
            if profit > 0:
                dp[w] = max(dp[w], dp[w - cost] + profit)
    
    return dp[budget]


def greedyApproach(present: List[int], future: List[int], budget: int) -> int:
    """
    Greedy approach for comparison - THIS IS INCORRECT for optimal solution.
    """
    n = len(present)
    stocks = [(future[i] - present[i], present[i]) for i in range(n)]
    stocks.sort(key=lambda x: x[0], reverse=True)  # Sort by profit descending
    
    total_profit = 0
    for profit, cost in stocks:
        if cost <= budget and profit > 0:
            total_profit += profit
            budget -= cost
    
    return total_profit


def findOptimalStocks(present: List[int], future: List[int], budget: int) -> List[int]:
    """
    Returns the indices of stocks that should be bought for optimal profit.
    """
    n = len(present)
    dp = [[0] * (budget + 1) for _ in range(n + 1)]
    
    # Fill DP table
    for i in range(1, n + 1):
        cost = present[i - 1]
        profit = max(0, future[i - 1] - present[i - 1])
        
        for w in range(budget + 1):
            dp[i][w] = dp[i - 1][w]
            if w >= cost and profit > 0:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - cost] + profit)
    
    # Backtrack to find which stocks were selected
    selected = []
    w = budget
    for i in range(n, 0, -1):
        cost = present[i - 1]
        profit = max(0, future[i - 1] - present[i - 1])
        
        # If value came from including this stock
        if w >= cost and dp[i][w] == dp[i - 1][w - cost] + profit and dp[i][w] != dp[i - 1][w]:
            selected.append(i - 1)  # Add stock index
            w -= cost
    
    return sorted(selected)


# Test cases
if __name__ == "__main__":
    test_cases = [
        {
            "present": [1, 1, 2],
            "future": [3, 3, 5],
            "budget": 2,
            "description": "Greedy fails: takes stock 2 (profit 3) vs optimal stocks 0,1 (profit 4)"
        },
        {
            "present": [2, 3, 5],
            "future": [5, 7, 11],
            "budget": 5,
            "description": "Greedy fails: expensive stock blocks better combination"
        },
        {
            "present": [5, 4, 6],
            "future": [8, 5, 10],
            "budget": 10,
            "description": "Basic test case"
        }
    ]
    
    for i, case in enumerate(test_cases):
        print(f"Test Case {i + 1}: {case['description']}")
        print(f"Present: {case['present']}")
        print(f"Future:  {case['future']}")
        print(f"Budget:  {case['budget']}")
        
        greedy_result = greedyApproach(case['present'], case['future'], case['budget'])
        dp_result = maximumProfit(case['present'], case['future'], case['budget'])
        dp_optimized = maximumProfitOptimized(case['present'], case['future'], case['budget'])
        optimal_stocks = findOptimalStocks(case['present'], case['future'], case['budget'])
        
        print(f"Greedy result: {greedy_result}")
        print(f"DP result: {dp_result}")
        print(f"DP optimized: {dp_optimized}")
        print(f"Optimal stocks to buy: {optimal_stocks}")
        
        if greedy_result != dp_result:
            print(f"❌ Greedy FAILS by {dp_result - greedy_result}")
        else:
            print("✅ Greedy works for this case")
        print("-" * 50) 