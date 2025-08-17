"""
Skip List Visualization Tools
============================

Tools for visualizing Skip List structure, operations, and performance.
"""

from skiplist import SkipList
import random
import time
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple, Dict


class SkipListVisualizer:
    """
    Visualizer for Skip List structure and operations.
    """
    
    def __init__(self, skip_list: SkipList):
        self.skip_list = skip_list
    
    def print_structure(self, show_pointers: bool = False):
        """
        Print a visual representation of the skip list structure.
        
        Args:
            show_pointers: Whether to show pointer connections
        """
        if self.skip_list.size == 0:
            print("Empty Skip List")
            return
        
        print(f"Skip List Structure (size={self.skip_list.size}):")
        print("=" * 80)
        
        # Collect all nodes at each level
        levels_data = {}
        current = self.skip_list.header.forward[0]
        
        while current is not None:
            for level in range(len(current.forward)):
                if level not in levels_data:
                    levels_data[level] = []
                if level < len(current.forward):
                    levels_data[level].append(current)
            current = current.forward[0]
        
        # Print level by level from top to bottom
        max_level = max(levels_data.keys()) if levels_data else 0
        
        for level in range(max_level, -1, -1):
            level_str = f"Level {level:2d}: HEAD"
            
            if level in levels_data:
                for node in levels_data[level]:
                    if show_pointers:
                        level_str += " -> " + str(node.key)
                    else:
                        level_str += f" -> {node.key}"
                level_str += " -> NULL"
            else:
                level_str += " -> NULL"
            
            print(level_str)
        
        print("=" * 80)
    
    def animate_search(self, key, delay: float = 1.0):
        """
        Animate the search process step by step.
        
        Args:
            key: Key to search for
            delay: Delay between steps in seconds
        """
        print(f"\nAnimated Search for key: {key}")
        print("=" * 50)
        
        current = self.skip_list.header
        path = []
        comparisons = 0
        
        # Traverse from highest level to lowest
        for level in range(self.skip_list.level, -1, -1):
            print(f"\n--- Level {level} ---")
            
            # Move right at current level
            while (current.forward[level] is not None and 
                   current.forward[level].key < key):
                current = current.forward[level]
                comparisons += 1
                path.append((level, current.key if current.key is not None else "HEAD"))
                
                print(f"Move right to node {current.key}: {current.key} < {key}")
                time.sleep(delay)
            
            # Check if we can move right
            next_node = current.forward[level]
            if next_node is not None:
                comparisons += 1
                print(f"Cannot move right: {next_node.key} >= {key}")
            else:
                print("Cannot move right: reached end of level")
            
            if level > 0:
                print(f"Drop down to level {level - 1}")
                time.sleep(delay)
        
        # Final check at level 0
        current = current.forward[0]
        comparisons += 1
        
        if current is not None and current.key == key:
            print(f"\n🎯 FOUND! Key {key} with value: {current.value}")
        else:
            print(f"\n❌ NOT FOUND! Key {key} does not exist")
        
        print(f"\nSearch completed with {comparisons} comparisons")
        print(f"Search path: {' -> '.join([f'L{l}:{k}' for l, k in path])}")
    
    def show_level_distribution(self):
        """Show the distribution of nodes across levels."""
        if self.skip_list.size == 0:
            print("No data to display - skip list is empty")
            return
        
        stats = self.skip_list.get_statistics()
        level_counts = stats['level_counts']
        
        print(f"\nLevel Distribution:")
        print("-" * 40)
        
        max_count = max(level_counts) if level_counts else 0
        scale = 50 / max_count if max_count > 0 else 1
        
        for level, count in enumerate(level_counts):
            bar_length = int(count * scale)
            bar = "█" * bar_length
            percentage = (count / stats['size']) * 100
            
            print(f"Level {level:2d}: {count:4d} nodes ({percentage:5.1f}%) {bar}")
        
        print("-" * 40)
        print(f"Total levels: {len(level_counts)}")
        print(f"Average node level: {stats['average_node_level']:.2f}")
        print(f"Expected height: {stats['expected_height']:.2f}")


def benchmark_operations(sizes: List[int], num_trials: int = 5) -> Dict[str, List[float]]:
    """
    Benchmark Skip List operations across different sizes.
    
    Args:
        sizes: List of sizes to test
        num_trials: Number of trials per size
        
    Returns:
        Dictionary with timing results
    """
    results = {
        'sizes': sizes,
        'insert_times': [],
        'search_times': [],
        'delete_times': [],
        'insert_comparisons': [],
        'search_comparisons': [],
        'delete_comparisons': []
    }
    
    for size in sizes:
        print(f"Benchmarking size {size}...")
        
        insert_times = []
        search_times = []
        delete_times = []
        insert_comps = []
        search_comps = []
        delete_comps = []
        
        for trial in range(num_trials):
            # Create skip list and test data
            sl = SkipList()
            test_keys = list(range(size))
            random.shuffle(test_keys)
            
            # Benchmark insertions
            start_time = time.perf_counter()
            total_insert_comps = 0
            
            for key in test_keys:
                sl.insert(key, f"value_{key}")
                total_insert_comps += sl.insert_comparisons
            
            insert_time = time.perf_counter() - start_time
            insert_times.append(insert_time)
            insert_comps.append(total_insert_comps / size)
            
            # Benchmark searches
            search_keys = random.sample(test_keys, min(100, size))
            start_time = time.perf_counter()
            total_search_comps = 0
            
            for key in search_keys:
                sl.search(key)
                total_search_comps += sl.search_comparisons
            
            search_time = time.perf_counter() - start_time
            search_times.append(search_time / len(search_keys))
            search_comps.append(total_search_comps / len(search_keys))
            
            # Benchmark deletions
            delete_keys = random.sample(test_keys, min(50, size))
            start_time = time.perf_counter()
            total_delete_comps = 0
            
            for key in delete_keys:
                sl.delete(key)
                total_delete_comps += sl.delete_comparisons
            
            delete_time = time.perf_counter() - start_time
            delete_times.append(delete_time / len(delete_keys))
            delete_comps.append(total_delete_comps / len(delete_keys))
        
        # Average across trials
        results['insert_times'].append(np.mean(insert_times))
        results['search_times'].append(np.mean(search_times))
        results['delete_times'].append(np.mean(delete_times))
        results['insert_comparisons'].append(np.mean(insert_comps))
        results['search_comparisons'].append(np.mean(search_comps))
        results['delete_comparisons'].append(np.mean(delete_comps))
    
    return results


def plot_performance_analysis(results: Dict[str, List[float]]):
    """Plot performance analysis results."""
    sizes = results['sizes']
    
    # Create subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Skip List Performance Analysis', fontsize=16)
    
    # Plot 1: Operation Times
    ax1.loglog(sizes, results['insert_times'], 'bo-', label='Insert', markersize=6)
    ax1.loglog(sizes, results['search_times'], 'ro-', label='Search', markersize=6)
    ax1.loglog(sizes, results['delete_times'], 'go-', label='Delete', markersize=6)
    
    # Add theoretical O(log n) line
    theoretical_logn = [np.log2(s) * results['search_times'][0] / np.log2(sizes[0]) 
                       for s in sizes]
    ax1.loglog(sizes, theoretical_logn, 'k--', alpha=0.5, label='O(log n)')
    
    ax1.set_xlabel('Skip List Size')
    ax1.set_ylabel('Time per Operation (seconds)')
    ax1.set_title('Operation Times vs Size')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Comparisons
    ax2.semilogx(sizes, results['insert_comparisons'], 'bo-', label='Insert', markersize=6)
    ax2.semilogx(sizes, results['search_comparisons'], 'ro-', label='Search', markersize=6)
    ax2.semilogx(sizes, results['delete_comparisons'], 'go-', label='Delete', markersize=6)
    
    # Add theoretical O(log n) line for comparisons
    theoretical_comps = [np.log2(s) for s in sizes]
    ax2.semilogx(sizes, theoretical_comps, 'k--', alpha=0.5, label='log₂(n)')
    
    ax2.set_xlabel('Skip List Size')
    ax2.set_ylabel('Average Comparisons per Operation')
    ax2.set_title('Comparisons vs Size')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Search Time Scaling
    ax3.loglog(sizes, results['search_times'], 'ro-', markersize=8, linewidth=2)
    
    # Fit scaling behavior
    log_sizes = np.log(sizes)
    log_times = np.log(results['search_times'])
    slope, intercept = np.polyfit(log_sizes, log_times, 1)
    
    fitted_times = np.exp(intercept) * np.power(sizes, slope)
    ax3.loglog(sizes, fitted_times, 'r--', alpha=0.7, 
              label=f'Fitted: O(n^{slope:.2f})')
    
    ax3.set_xlabel('Skip List Size')
    ax3.set_ylabel('Search Time (seconds)')
    ax3.set_title(f'Search Time Scaling')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Efficiency Comparison
    theoretical_search = [np.log2(s) for s in sizes]
    efficiency = [actual / theoretical for actual, theoretical 
                 in zip(results['search_comparisons'], theoretical_search)]
    
    ax4.semilogx(sizes, efficiency, 'mo-', markersize=6, linewidth=2)
    ax4.axhline(y=1, color='k', linestyle='--', alpha=0.5, label='Theoretical Optimal')
    
    ax4.set_xlabel('Skip List Size')
    ax4.set_ylabel('Actual/Theoretical Comparisons')
    ax4.set_title('Search Efficiency (Lower is Better)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def compare_probability_effects():
    """Compare the effect of different probability values."""
    probabilities = [0.25, 0.5, 0.75]
    size = 1000
    colors = ['blue', 'red', 'green']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('Effect of Probability Parameter on Skip List Performance', fontsize=14)
    
    for i, p in enumerate(probabilities):
        # Create skip list with specific probability
        sl = SkipList(p=p)
        for j in range(size):
            sl.insert(j, f"value_{j}")
        
        stats = sl.get_statistics()
        
        # Plot level distribution
        level_counts = stats['level_counts']
        levels = list(range(len(level_counts)))
        
        ax1.bar([l + i*0.25 for l in levels], level_counts, 
               width=0.25, alpha=0.7, color=colors[i], 
               label=f'p = {p}')
    
    ax1.set_xlabel('Level')
    ax1.set_ylabel('Number of Nodes')
    ax1.set_title('Node Distribution by Level')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Performance comparison
    search_results = []
    for p in probabilities:
        sl = SkipList(p=p)
        for j in range(size):
            sl.insert(j, f"value_{j}")
        
        # Test search performance
        test_keys = random.sample(range(size), 100)
        total_comparisons = 0
        
        for key in test_keys:
            sl.search(key)
            total_comparisons += sl.search_comparisons
        
        avg_comparisons = total_comparisons / len(test_keys)
        search_results.append(avg_comparisons)
    
    ax2.bar(range(len(probabilities)), search_results, color=colors, alpha=0.7)
    ax2.set_xticks(range(len(probabilities)))
    ax2.set_xticklabels([f'p = {p}' for p in probabilities])
    ax2.set_ylabel('Average Search Comparisons')
    ax2.set_title('Search Performance by Probability')
    ax2.grid(True, alpha=0.3)
    
    # Add theoretical line
    theoretical = [np.log2(size)] * len(probabilities)
    ax2.plot(range(len(probabilities)), theoretical, 'k--', 
            label='Theoretical log₂(n)', linewidth=2)
    ax2.legend()
    
    plt.tight_layout()
    plt.show()


def demo_visualization():
    """Demonstrate visualization capabilities."""
    print("Skip List Visualization Demo")
    print("=" * 50)
    
    # Create a skip list with some data
    sl = SkipList(max_level=4, p=0.5)
    data = [10, 5, 15, 3, 7, 12, 18, 1, 6, 9, 14, 20]
    
    print("Inserting data:", data)
    for key in data:
        sl.insert(key, f"value_{key}")
    
    # Visualize structure
    visualizer = SkipListVisualizer(sl)
    print("\nSkip List Structure:")
    visualizer.print_structure()
    
    # Show level distribution
    visualizer.show_level_distribution()
    
    # Animate a search (with short delay for demo)
    print("\nAnimated search demonstration:")
    visualizer.animate_search(7, delay=0.5)


def run_performance_benchmark():
    """Run comprehensive performance benchmark."""
    print("\nRunning Performance Benchmark...")
    print("This may take a few minutes...")
    
    sizes = [100, 500, 1000, 2000, 5000]
    results = benchmark_operations(sizes, num_trials=3)
    
    print("\nBenchmark Results:")
    print("-" * 60)
    print(f"{'Size':<8} {'Insert(ms)':<12} {'Search(μs)':<12} {'Delete(μs)':<12}")
    print("-" * 60)
    
    for i, size in enumerate(sizes):
        insert_ms = results['insert_times'][i] * 1000
        search_us = results['search_times'][i] * 1000000
        delete_us = results['delete_times'][i] * 1000000
        
        print(f"{size:<8} {insert_ms:<12.3f} {search_us:<12.3f} {delete_us:<12.3f}")
    
    # Plot results if matplotlib is available
    try:
        plot_performance_analysis(results)
        compare_probability_effects()
    except ImportError:
        print("Matplotlib not available - skipping plots")


if __name__ == "__main__":
    # Run visualization demo
    demo_visualization()
    
    # Ask user if they want to run benchmark
    response = input("\nRun performance benchmark? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        run_performance_benchmark()
    else:
        print("Skipping performance benchmark") 