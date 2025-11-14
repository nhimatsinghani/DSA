# Genetic Algorithms (GA): A Practical, Beginner‑Friendly Walkthrough

> **Audience:** Engineers and students who know basic Python and want a hands‑on introduction to Genetic Algorithms for search & optimization.  
> **Goal:** Give you the intuition, the prerequisites, and runnable examples—from “Hello, World” up to slightly more complex problems—so you can start applying GAs today.

---

## 1) What is a Genetic Algorithm?

A **Genetic Algorithm (GA)** is a population‑based metaheuristic inspired by biological evolution. You maintain a population of **candidate solutions** (individuals). Each has a **fitness** score (how good it is). Over many **generations**, individuals are chosen by **selection**, mixed via **crossover**, and randomly perturbed via **mutation**. Good traits survive and spread; bad traits fade out—ideally converging to a high‑quality solution.

**Key properties**

- **Black‑box friendly:** Works when you can *compute* a fitness score but don’t have gradients or a closed‑form solution.  
- **Flexible encodings:** Binary strings, integers, floating‑point vectors, permutations, trees…  
- **Anytime optimization:** Often yields useful solutions even if you stop early.  
- **Parallelizable:** Individuals evaluate independently.

**When to consider GAs**

- The search space is **non‑convex, discontinuous, noisy**, or has many local optima.  
- You need to **optimize discrete structures** (feature sets, schedules, routing permutations).  
- You have **hard constraints** that are easier to enforce by encoding or repair than by calculus.  
- You want a robust, gradient‑free optimizer or a quick baseline for tough spaces.

**When *not* to use**

- You have a smooth, convex objective with easy gradients → use gradient‑based or convex optimization.  
- You need exact guarantees (e.g., proofs of optimality) under tight constraints.  
- Evaluation is extremely expensive and population methods are unaffordable (unless you can cache/surrogate/parallelize).

---

## 2) Prerequisites (What to know before diving in)

- **Python basics**: functions, lists, random numbers, classes.  
- **Math comfort** (light): probability intuition, simple algebra, working with objective functions.  
- **Problem modeling**: you should be able to define *what a solution looks like* and *how to score it (fitness)*.  
- **Reproducibility basics**: random seeds, logging, and plotting/printing progress.

Nice‑to‑haves: some exposure to optimization, combinatorics, and NumPy.

---

## 3) Core Concepts at a Glance

- **Chromosome / Genome**: The data structure encoding a solution (e.g., a list of floats or 0/1 bits).  
- **Population**: A list of chromosomes.  
- **Fitness Function**: Maps a chromosome → score (higher is better in this guide).  
- **Selection**: Preferentially pick better individuals (roulette, tournament, rank, etc.).  
- **Crossover (Recombination)**: Combine two parents to create one or more children.  
- **Mutation**: Randomly perturb genes to maintain diversity.  
- **Elitism**: Copy the best few unchanged to the next generation.  
- **Termination**: Max generations, time budget, convergence, or target fitness.

**Canonical GA loop (pseudocode)**

```text
initialize population P
evaluate fitness of P
repeat until termination:
    P' = []
    if elitism: copy top-k from P to P'
    while |P'| < population_size:
        parent1 = select(P)
        parent2 = select(P)
        child1, child2 = crossover(parent1, parent2)   # sometimes one child
        mutate(child1); mutate(child2)
        evaluate fitness(child1); evaluate fitness(child2)
        add to P'
    P = P'
return best individual in P
```

---

## 4) What you need to start using GAs (Tooling & Setup)

- **Language**: Python 3.9+ recommended.  
- **Standard library only** is enough for basic GAs (we’ll show pure‑Python examples).  
- **Optional libraries** for productivity:  
  - **NumPy** for vector math and faster fitness evaluation.  
  - **PyGAD** or **DEAP** for full‑featured GA operators, selection schemes, and utilities.
- **Execution**: Any Python environment (local, Colab, or a notebook).  
- **Compute**: Populations of 50–500 are common; parallelism helps if fitness is expensive.

---

## 5) Strategy & Design Choices

- **Encoding** drives everything. Choose a genome that naturally enforces constraints (e.g., permutation encoding for routing).  
- **Fitness shaping**: Penalize constraint violations; normalize/scale scores if needed.  
- **Selection pressure**: Tournament size or selection scheme controls exploration‑exploitation balance.  
- **Crossover & mutation rates**: Typical starting points:  
  - Crossover probability `pc ≈ 0.6–0.9`  
  - Mutation probability `pm ≈ 1/num_genes` for bit/perm encodings (or a small Gaussian noise for floats).  
- **Elitism**: Keep 1–5% best to avoid regression.  
- **Diversity**: Watch for premature convergence; increase mutation, use diversity‑aware selection, or restart.

---

## 6) “Hello, World”: Evolving a Target String

**Task:** Evolve a 12‑character string to match `"HELLO WORLD!"`.  
**Encoding:** List of characters from an allowed alphabet.  
**Fitness:** Negative Hamming distance (the fewer mismatches, the higher the score).

```python
import random
import string
from typing import List

random.seed(42)

TARGET = "HELLO WORLD!"
ALPHABET = string.ascii_uppercase + " !?."  # allowed characters

def random_individual() -> List[str]:
    return [random.choice(ALPHABET) for _ in range(len(TARGET))]

def fitness(ind: List[str]) -> int:
    return sum(1 for g, t in zip(ind, TARGET) if g == t)  # matches count

def tournament_select(pop, k=3):
    return max(random.sample(pop, k), key=lambda x: x["fit"])

def one_point_crossover(a: List[str], b: List[str]):
    if len(a) < 2: return a[:], b[:]
    cut = random.randint(1, len(a) - 1)
    return a[:cut] + b[cut:], b[:cut] + a[cut:]

def mutate(ind: List[str], pm=0.05):
    for i in range(len(ind)):
        if random.random() < pm:
            ind[i] = random.choice(ALPHABET)

def run_ga(pop_size=200, generations=200, pc=0.9, pm=0.02, elitism=2):
    # initialize
    pop = [{"genome": random_individual(), "fit": None} for _ in range(pop_size)]
    for p in pop: p["fit"] = fitness(p["genome"])

    for gen in range(generations):
        pop.sort(key=lambda x: x["fit"], reverse=True)
        best = pop[0]
        if gen % 10 == 0 or best["fit"] == len(TARGET):
            print(f"gen {gen:03d} | best fitness={best['fit']:02d} | {''.join(best['genome'])}")
        if best["fit"] == len(TARGET):
            break

        new_pop = pop[:elitism]  # elitism (copy best few)
        while len(new_pop) < pop_size:
            p1 = tournament_select(pop)
            p2 = tournament_select(pop)
            c1, c2 = p1["genome"][:], p2["genome"][:]
            if random.random() < pc:
                c1, c2 = one_point_crossover(c1, c2)
            mutate(c1, pm); mutate(c2, pm)
            new_pop.append({"genome": c1, "fit": fitness(c1)})
            if len(new_pop) < pop_size:
                new_pop.append({"genome": c2, "fit": fitness(c2)})
        pop = new_pop

    pop.sort(key=lambda x: x["fit"], reverse=True)
    return pop[0]

if __name__ == "__main__":
    best = run_ga()
    print("Best:", ''.join(best["genome"]), "fitness:", best["fit"])
```

**What you’ll see:** The best string gradually acquires correct letters until it exactly matches the target (or gets very close).

---

## 7) Simple Continuous Optimization: Maximize a 1‑D Function

**Task:** Maximize `f(x) = x * sin(x)` on `[0, 10]`.  
**Encoding:** Single real value `x` (float).  
**Crossover:** Blend crossover (BLX‑α like).  
**Mutation:** Add small Gaussian noise and clamp to bounds.

```python
import random
import math

random.seed(123)

LOW, HIGH = 0.0, 10.0

def random_float():
    return random.uniform(LOW, HIGH)

def fitness_real(x: float) -> float:
    return x * math.sin(x)

def blend_crossover(a: float, b: float, alpha=0.5) -> tuple[float, float]:
    low, high = min(a, b), max(a, b)
    spread = high - low
    left = low - alpha * spread
    right = high + alpha * spread
    return (random.uniform(left, right), random.uniform(left, right))

def mutate_real(x: float, sigma=0.2):
    x += random.gauss(0, sigma)
    return max(LOW, min(HIGH, x))

def run_ga_real(pop_size=60, generations=80, pc=0.9, pm=0.2, elitism=2):
    pop = [{"x": random_float(), "fit": None} for _ in range(pop_size)]
    for p in pop: p["fit"] = fitness_real(p["x"])

    for gen in range(generations):
        pop.sort(key=lambda p: p["fit"], reverse=True)
        best = pop[0]
        if gen % 10 == 0:
            print(f"gen {gen:03d} | best x={best['x']:.4f} f={best['fit']:.4f}")
        new_pop = pop[:elitism]
        while len(new_pop) < pop_size:
            p1 = max(random.sample(pop, 3), key=lambda p: p["fit"])
            p2 = max(random.sample(pop, 3), key=lambda p: p["fit"])
            c1, c2 = p1["x"], p2["x"]
            if random.random() < pc:
                c1, c2 = blend_crossover(c1, c2, alpha=0.5)
            if random.random() < pm: c1 = mutate_real(c1, 0.25)
            if random.random() < pm: c2 = mutate_real(c2, 0.25)
            new_pop.append({"x": c1, "fit": fitness_real(c1)})
            if len(new_pop) < pop_size:
                new_pop.append({"x": c2, "fit": fitness_real(c2)})
        pop = new_pop
    pop.sort(key=lambda p: p["fit"], reverse=True)
    return pop[0]

if __name__ == "__main__":
    best = run_ga_real()
    print(f"Best x={best['x']:.5f}, f={best['fit']:.5f}")
```

**Notes**: You can extend to `n`‑dimensional vectors by making `x` a list of floats and mutating each gene with Gaussian noise.

---

## 8) Classic Discrete Optimization: 0/1 Knapsack

**Task:** Choose items to maximize total value without exceeding a weight limit.  
**Encoding:** Bitstring where `1` = take item, `0` = skip item.  
**Fitness:** Total value minus a penalty if weight exceeds capacity.

```python
import random
from typing import List, Tuple

random.seed(7)

# (value, weight)
ITEMS: List[Tuple[int, int]] = [
    (10, 5), (6, 4), (7, 3), (18, 9), (3, 1), (14, 8), (9, 6), (5, 3), (20, 12), (11, 7)
]
CAPACITY = 24

def rand_individual(n: int):
    return [random.randint(0, 1) for _ in range(n)]

def eval_knapsack(bits: List[int]) -> float:
    value = sum(v for (v, w), b in zip(ITEMS, bits) if b)
    weight = sum(w for (v, w), b in zip(ITEMS, bits) if b)
    if weight <= CAPACITY: return value
    # penalty proportional to overflow
    overflow = weight - CAPACITY
    return value - 5 * overflow

def two_point_crossover(a: List[int], b: List[int]):
    n = len(a)
    i, j = sorted(random.sample(range(n), 2))
    c1 = a[:i] + b[i:j] + a[j:]
    c2 = b[:i] + a[i:j] + b[j:]
    return c1, c2

def mutate_bits(bits: List[int], pm=0.02):
    for i in range(len(bits)):
        if random.random() < pm:
            bits[i] ^= 1

def run_knapsack_ga(pop_size=120, generations=120, pc=0.85, pm=0.02, elitism=2):
    n = len(ITEMS)
    pop = [{"x": rand_individual(n)} for _ in range(pop_size)]
    for p in pop: p["fit"] = eval_knapsack(p["x"])

    for gen in range(generations):
        pop.sort(key=lambda p: p["fit"], reverse=True)
        best = pop[0]
        if gen % 10 == 0:
            sel_weight = sum(w for (v, w), b in zip(ITEMS, best["x"]) if b)
            print(f"gen {gen:03d} | best value={best['fit']:.2f} weight={sel_weight}")
        new_pop = pop[:elitism]
        while len(new_pop) < pop_size:
            p1 = max(random.sample(pop, 3), key=lambda p: p["fit"])
            p2 = max(random.sample(pop, 3), key=lambda p: p["fit"])
            c1, c2 = p1["x"][:], p2["x"][:]
            if random.random() < pc:
                c1, c2 = two_point_crossover(c1, c2)
            mutate_bits(c1, pm); mutate_bits(c2, pm)
            child1 = {"x": c1}; child1["fit"] = eval_knapsack(child1["x"])
            child2 = {"x": c2}; child2["fit"] = eval_knapsack(child2["x"])
            new_pop.append(child1)
            if len(new_pop) < pop_size:
                new_pop.append(child2)
        pop = new_pop
    pop.sort(key=lambda p: p["fit"], reverse=True)
    return pop[0]

if __name__ == "__main__":
    best = run_knapsack_ga()
    print("Best value:", best["fit"])
    print("Chosen items:", [i for i,b in enumerate(best["x"]) if b])
```

**Extensions**: Change the penalty rule, add multiple constraints, or try **repair operators** that flip bits until capacity is met.

---

## 9) A “Slightly More Complex” Example Outline: Tiny TSP (Permutation GA)

The **Traveling Salesperson Problem** seeks the shortest tour visiting each city exactly once. Use a **permutation encoding** (each genome is an ordering of cities). Mutations like **swap**, **insert**, or **scramble** are common; crossovers like **Order Crossover (OX)** preserve relative order. Full code is longer, but here’s the essence:

```python
# Sketch only (not full code):
# genome: [2, 0, 3, 1, 4, ...]  # permutation of city indices

def tour_length(order, dist):
    return sum(dist[order[i]][order[(i+1)%len(order)]] for i in range(len(order)))

def ox_crossover(a, b):
    # choose segment [i:j) from a, preserve order of remaining from b
    pass  # implement standard OX

def swap_mutation(order, pm=0.1):
    if random.random() < pm:
        i, j = random.sample(range(len(order)), 2)
        order[i], order[j] = order[j], order[i]
```

For a production TSP GA, use good crossovers (PMX/OX/ERX), diversity maintenance, and occasionally local search (2‑opt) as a mutation/repair step (a **memetic** GA).

---

## 10) Using a Library (PyGAD) for Hyperparameter Search (Bonus)

GA is handy for searching hyperparameters when grid/random search is too wide and gradients aren’t available.

```python
# pip install pygad
import numpy as np
import pygad

# Example: tune 3 hyperparams to maximize a synthetic score
def fitness_func(solution, solution_idx):
    lr, dropout, width = solution
    # pretend-score: you would train/validate a model here
    score = -(lr-0.01)**2 - (dropout-0.2)**2 - ((width-128)/128)**2
    return float(score)

ga = pygad.GA(num_generations=30,
              num_parents_mating=8,
              fitness_func=fitness_func,
              sol_per_pop=20,
              num_genes=3,
              init_range_low=[1e-4, 0.0,   16],
              init_range_high=[1e-1, 0.6, 512],
              mutation_type="random",
              mutation_percent_genes=33,
              crossover_type="single_point")

ga.run()
solution, solution_fitness, _ = ga.best_solution()
print("Best:", solution, "fitness:", solution_fitness)
```

---

## 11) Practical Tips & Pitfalls

- **Scale population & generations to your budget.** If fitness is cheap, increase both. If expensive, use smaller populations and stronger selection.  
- **Track progress.** Print/plot best & mean fitness; stop if stagnating and restart with diversity.  
- **Constraint handling.** Prefer **feasible encodings**; second best: **repairs**; last resort: penalties tuned carefully.  
- **Premature convergence.** Increase mutation, use niching/speciation (fitness sharing), lower selection pressure, or random immigrants.  
- **Seeding.** Start with a few hand‑crafted or heuristic solutions if available.  
- **Reproducibility.** Fix `random.seed`; log parameters and best solutions.  
- **Parallelize evaluations** if fitness dominates runtime.

---

## 12) Frequently Asked Questions (FAQ)

**Q: How do I pick `pc` and `pm`?**  
Start with `pc = 0.7–0.9`, `pm = 1/num_genes` for binary/permutation encodings or small Gaussian noise for floats; tune empirically.

**Q: Should I maximize or minimize fitness?**  
Pick one convention (this guide uses maximize). For minimization, negate the objective or convert to score = `-cost`.

**Q: Can I combine GA with local search?**  
Yes—**memetic algorithms** often improve convergence: occasionally apply hill‑climbing or 2‑opt to offspring.

**Q: How big should the population be?**  
Rule‑of‑thumb: 25–200 for small problems; more for harder landscapes. Balance with evaluation cost.

---

## 13) Checklist: From Idea to Working GA

1. **Define encoding** that naturally respects constraints.  
2. **Write the fitness function** (fast, deterministic if possible).  
3. **Choose operators** (selection, crossover, mutation) that fit the encoding.  
4. **Start with sensible defaults** (`pc`, `pm`, population).  
5. **Instrument & log** (best/mean fitness, diversity).  
6. **Tune & iterate** (rates, operator mix, penalties/repairs).  
7. **Validate** on new instances / seeds.

---

## 14) Further Directions

- **Advanced operators** (SBX, differential variation, ERX/PMX/OX2).  
- **Niching/speciation** (crowding, fitness sharing).  
- **Multi‑objective GAs** (NSGA‑II/III) for trade‑offs (e.g., accuracy vs. latency).  
- **Surrogate modeling** for expensive objectives.  
- **Co‑evolution**, **island models**, and distributed GAs.

---

## 15) License

This guide and code snippets are provided for educational use. Feel free to reuse with attribution.

---

*Happy evolving!* 🧬