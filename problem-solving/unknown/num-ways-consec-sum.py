"""
Number of ways to write an integer as a sum of two or more consecutive positive integers.

Intuition / Number theory:
- Any representation of n as a sum of k consecutive positive integers (k \ge 1) looks like:
    n = m + (m+1) + ... + (m+k-1) = k(2m + k - 1) / 2
  Rearranging gives 2n = k(2m + k - 1). For fixed k, m is an integer iff k divides 2n
  and the parity aligns so that (2m + k - 1) is an integer of the same parity as k.
- A classic result: the number of representations of n as consecutive positive integers
  with length k \ge 1 equals the number of odd divisors of n.
- If we require k \ge 2 (two or more terms), subtract the trivial 1-term representation.

Therefore:
  ways(n, k \ge 2) = (# of odd divisors of n) - 1

Algorithm:
1) Remove all factors of 2 from n to get its odd component.
2) Count divisors of the odd component using prime factorization: if
   odd_n = \prod p_i^{e_i}, then #odd_divisors = \prod (e_i + 1).
3) Answer is max(#odd_divisors - 1, 0).

Complexity: O(\sqrt{n}) for the factorization step.
"""

from typing import List, Tuple


def count_odd_divisors(n: int) -> int:
    """Return the number of odd divisors of n.

    This strips out all factors of 2, then counts divisors of the remaining odd part
    via prime factorization.
    """
    if n <= 0:
        return 0

    # Remove all factors of 2 to leave only the odd component
    while n % 2 == 0:
        n //= 2

    odd_divisors_count = 1
    factor = 3
    while factor * factor <= n:
        exponent = 0
        while n % factor == 0:
            n //= factor
            exponent += 1
        if exponent > 0:
            odd_divisors_count *= (exponent + 1)
        factor += 2

    # If what's left is > 1, it is an odd prime, contributing exponent 1
    if n > 1:
        odd_divisors_count *= 2

    return odd_divisors_count


def count_consecutive_sum_ways(n: int) -> int:
    """Return the number of ways to write n as a sum of two or more consecutive positive integers.

    Follows the result: ways = (# of odd divisors of n) - 1, floored at 0.
    """
    if n <= 2:
        return 0
    odd_divisors = count_odd_divisors(n)
    ways = odd_divisors - 1
    return ways if ways > 0 else 0


def find_representations(n: int) -> List[Tuple[int, int]]:
    """Enumerate representations of n as sums of consecutive positive integers with length >= 2.

    Returns a list of (start, length) pairs, where start is the first term (m) and
    length is k (>= 2). This is primarily for verification and demonstration.
    """
    if n <= 2:
        return []

    representations: List[Tuple[int, int]] = []

    # For a given length k, the sum is: n = k*m + k*(k-1)/2  -> m = (n - k*(k-1)/2)/k
    # We only need to try k up to where the minimal sum exceeds n.
    # Minimal sum for length k is 1 + 2 + ... + k = k*(k+1)/2.
    # When k*(k+1)/2 > n, longer lengths are impossible.
    k = 2
    while k * (k + 1) // 2 <= n:
        numerator = n - k * (k - 1) // 2
        if numerator > 0 and numerator % k == 0:
            start = numerator // k
            if start >= 1:
                representations.append((start, k))
        k += 1

    return representations


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        # Quick demo
        demo_values = [1, 2, 3, 5, 8, 9, 15, 21, 25, 100]
        for value in demo_values:
            ways = count_consecutive_sum_ways(value)
            reps = find_representations(value)
            print(f"n={value}: ways={ways}, representations={reps}")
    else:
        for arg in sys.argv[1:]:
            try:
                n_value = int(arg)
            except ValueError:
                print(f"Skipping non-integer argument: {arg}")
                continue
            ways = count_consecutive_sum_ways(n_value)
            reps = find_representations(n_value)
            print(f"n={n_value}: ways={ways}, representations={reps}")
