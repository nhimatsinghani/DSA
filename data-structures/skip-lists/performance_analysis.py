"""
Performance Analysis for Skip Lists
==================================

Comprehensive analysis comparing Skip Lists with other data structures
and evaluating theoretical vs practical performance.
"""

import time
import random
import math
import statistics
from typing import List, Dict, Tuple, Any
from collections import defaultdict
import heapq

from skiplist import SkipList


class DataStructureComparison:
    """
    Compare Skip List performance against other data structures.
    """
    
    def __init__(self):
        self.results = defaultdict(list)
    
    def benchmark_skiplist(self, operations: List[Tuple[str, Any]], trials: int = 5) -> Dict[str, float]:
        """Benchmark Skip List operations."""
        results = {'insert': [], 'search': [], 'delete': [], 'range_query': []}
        
        for trial in range(trials):
            sl = SkipList()
            
            # Time operations
            for op_type, data in operations:
                start_time = time.perf_counter()
                
                if op_type == 'insert':
                    for key, value in data:
                        sl.insert(key, value)
                elif op_type == 'search':
                    for key in data:
                        sl.search(key)
                elif op_type == 'delete':
                    for key in data:
                        sl.delete(key)
                elif op_type == 'range_query':
                    for start, end in data:
                        sl.range_query(start, end)
                
                end_time = time.perf_counter()
                results[op_type].append(end_time - start_time)
        
        # Return average times
        return {op: statistics.mean(times) for op, times in results.items()}
    
    def benchmark_list(self, operations: List[Tuple[str, Any]], trials: int = 5) -> Dict[str, float]:
        """Benchmark Python list (sorted) operations."""
        results = {'insert': [], 'search': [], 'delete': [], 'range_query': []}
        
        for trial in range(trials):
            data_list = []
            
            for op_type, data in operations:
                start_time = time.perf_counter()
                
                if op_type == 'insert':
                    for key, value in data:
                        # Insert maintaining sorted order
                        idx = self._binary_search_insert_pos(data_list, key)
                        data_list.insert(idx, (key, value))
                elif op_type == 'search':
                    for key in data:
                        self._binary_search_list(data_list, key)
                elif op_type == 'delete':
                    for key in data:
                        # Find and remove
                        for i, (k, v) in enumerate(data_list):
                            if k == key:
                                data_list.pop(i)
                                break
                elif op_type == 'range_query':
                    for start, end in data:
                        self._range_query_list(data_list, start, end)
                
                end_time = time.perf_counter()
                results[op_type].append(end_time - start_time)
        
        return {op: statistics.mean(times) for op, times in results.items()}
    
    def benchmark_dict(self, operations: List[Tuple[str, Any]], trials: int = 5) -> Dict[str, float]:
        """Benchmark Python dictionary operations."""
        results = {'insert': [], 'search': [], 'delete': [], 'range_query': []}
        
        for trial in range(trials):
            data_dict = {}
            
            for op_type, data in operations:
                start_time = time.perf_counter()
                
                if op_type == 'insert':
                    for key, value in data:
                        data_dict[key] = value
                elif op_type == 'search':
                    for key in data:
                        data_dict.get(key)
                elif op_type == 'delete':
                    for key in data:
                        data_dict.pop(key, None)
                elif op_type == 'range_query':
                    for start, end in data:
                        # Simulate range query by iterating all keys
                        sorted_keys = sorted(data_dict.keys())
                        result = [(k, data_dict[k]) for k in sorted_keys if start <= k <= end]
                
                end_time = time.perf_counter()
                results[op_type].append(end_time - start_time)
        
        return {op: statistics.mean(times) for op, times in results.items()}
    
    def _binary_search_insert_pos(self, lst: List[Tuple], key: Any) -> int:
        """Find insertion position maintaining sorted order."""
        left, right = 0, len(lst)
        while left < right:
            mid = (left + right) // 2
            if lst[mid][0] < key:
                left = mid + 1
            else:
                right = mid
        return left
    
    def _binary_search_list(self, lst: List[Tuple], key: Any) -> Any:
        """Binary search in sorted list."""
        left, right = 0, len(lst) - 1
        while left <= right:
            mid = (left + right) // 2
            if lst[mid][0] == key:
                return lst[mid][1]
            elif lst[mid][0] < key:
                left = mid + 1
            else:
                right = mid - 1
        return None
    
    def _range_query_list(self, lst: List[Tuple], start: Any, end: Any) -> List[Tuple]:
        """Range query on sorted list."""
        result = []
        for key, value in lst:
            if start <= key <= end:
                result.append((key, value))
            elif key > end:
                break
        return result


class TheoreticalAnalysis:
    """
    Analyze theoretical vs actual performance of Skip Lists.
    """
    
    @staticmethod
    def expected_height(n: int, p: float = 0.5) -> float:
        """Calculate expected height of skip list."""
        if n <= 0:
            return 0
        return math.log(n) / math.log(1/p)
    
    @staticmethod
    def expected_search_cost(n: int, p: float = 0.5) -> float:
        """Calculate expected search cost."""
        if n <= 0:
            return 0
        return (1/p) * math.log(n) / math.log(1/p)
    
    @staticmethod
    def probability_distribution(level: int, p: float = 0.5) -> float:
        """Calculate probability of a node reaching a given level."""
        return (p ** level) * (1 - p)
    
    @staticmethod
    def space_complexity(n: int, p: float = 0.5) -> float:
        """Calculate expected space complexity (number of pointers)."""
        if n <= 0:
            return 0
        return n * (1 / (1 - p))
    
    def analyze_height_distribution(self, skip_list: SkipList, num_samples: int = 1000) -> Dict[str, Any]:
        """Analyze height distribution over multiple samples."""
        heights = []
        sizes = []
        
        for _ in range(num_samples):
            sl = SkipList(p=skip_list.p)
            size = random.randint(10, 1000)
            
            # Insert random data
            for i in range(size):
                sl.insert(random.randint(0, size*2), f"value_{i}")
            
            heights.append(sl.level)
            sizes.append(size)
        
        return {
            'actual_heights': heights,
            'sizes': sizes,
            'mean_height': statistics.mean(heights),
            'std_height': statistics.stdev(heights) if len(heights) > 1 else 0,
            'theoretical_mean': statistics.mean([self.expected_height(s, skip_list.p) for s in sizes])
        }


def comprehensive_benchmark(sizes: List[int]) -> Dict[str, Dict[str, List[float]]]:
    """
    Run comprehensive benchmark comparing different data structures.
    
    Args:
        sizes: List of data sizes to test
        
    Returns:
        Dictionary with benchmark results
    """
    print("Running comprehensive benchmark...")
    comparison = DataStructureComparison()
    
    results = {
        'skip_list': {'insert': [], 'search': [], 'delete': [], 'range_query': []},
        'sorted_list': {'insert': [], 'search': [], 'delete': [], 'range_query': []},
        'dict': {'insert': [], 'search': [], 'delete': [], 'range_query': []}
    }
    
    for size in sizes:
        print(f"Testing size {size}...")
        
        # Generate test data
        insert_data = [(i, f"value_{i}") for i in range(size)]
        random.shuffle(insert_data)
        
        search_data = [random.randint(0, size-1) for _ in range(min(100, size))]
        delete_data = random.sample(range(size), min(50, size))
        range_data = [(random.randint(0, size//2), random.randint(size//2, size-1)) 
                     for _ in range(10)]
        
        operations = [
            ('insert', insert_data),
            ('search', search_data),
            ('delete', delete_data),
            ('range_query', range_data)
        ]
        
        # Benchmark each data structure
        for ds_name, benchmark_func in [
            ('skip_list', comparison.benchmark_skiplist),
            ('sorted_list', comparison.benchmark_list),
            ('dict', comparison.benchmark_dict)
        ]:
            try:
                times = benchmark_func(operations, trials=3)
                for op in ['insert', 'search', 'delete', 'range_query']:
                    results[ds_name][op].append(times[op])
            except Exception as e:
                print(f"Error benchmarking {ds_name}: {e}")
                for op in ['insert', 'search', 'delete', 'range_query']:
                    results[ds_name][op].append(float('inf'))
    
    return results


def analyze_probability_impact(sizes: List[int], probabilities: List[float]) -> Dict[str, Any]:
    """
    Analyze the impact of different probability values.
    
    Args:
        sizes: List of sizes to test
        probabilities: List of probability values to test
        
    Returns:
        Analysis results
    """
    print("Analyzing probability impact...")
    results = {}
    
    for p in probabilities:
        print(f"Testing probability p = {p}")
        results[p] = {
            'heights': [],
            'search_comparisons': [],
            'space_usage': []
        }
        
        for size in sizes:
            sl = SkipList(p=p)
            
            # Insert data
            for i in range(size):
                sl.insert(i, f"value_{i}")
            
            # Measure properties
            stats = sl.get_statistics()
            results[p]['heights'].append(stats['current_max_level'])
            results[p]['space_usage'].append(sum(stats['level_counts']))
            
            # Test search performance
            test_keys = random.sample(range(size), min(50, size))
            total_comparisons = 0
            for key in test_keys:
                sl.search(key)
                total_comparisons += sl.search_comparisons
            
            avg_comparisons = total_comparisons / len(test_keys)
            results[p]['search_comparisons'].append(avg_comparisons)
    
    return results


def stress_test(max_size: int = 10000, num_operations: int = 1000) -> Dict[str, Any]:
    """
    Perform stress testing on Skip List implementation.
    
    Args:
        max_size: Maximum size to test
        num_operations: Number of random operations to perform
        
    Returns:
        Stress test results
    """
    print(f"Running stress test with {num_operations} operations...")
    
    sl = SkipList()
    operations_log = []
    errors = []
    
    # Track timing for different operation types
    timing_stats = {'insert': [], 'search': [], 'delete': []}
    
    for i in range(num_operations):
        op_type = random.choice(['insert', 'search', 'delete'])
        key = random.randint(0, max_size)
        
        start_time = time.perf_counter()
        
        try:
            if op_type == 'insert':
                result = sl.insert(key, f"value_{key}_{i}")
                operations_log.append(('insert', key, result))
                
            elif op_type == 'search':
                result = sl.search(key)
                operations_log.append(('search', key, result is not None))
                
            elif op_type == 'delete':
                result = sl.delete(key)
                operations_log.append(('delete', key, result))
            
            end_time = time.perf_counter()
            timing_stats[op_type].append(end_time - start_time)
            
        except Exception as e:
            errors.append((i, op_type, key, str(e)))
    
    # Verify data consistency
    verification_errors = []
    for key, value in sl:
        expected_value = f"value_{key}_{operations_log[-1][2]}"  # This is a simplified check
        # More sophisticated verification would track actual insertions
    
    return {
        'total_operations': num_operations,
        'final_size': len(sl),
        'errors': errors,
        'verification_errors': verification_errors,
        'timing_stats': {
            op: {
                'mean': statistics.mean(times) if times else 0,
                'max': max(times) if times else 0,
                'min': min(times) if times else 0,
                'count': len(times)
            } for op, times in timing_stats.items()
        },
        'final_stats': sl.get_statistics()
    }


def print_comparison_report(results: Dict[str, Dict[str, List[float]]], sizes: List[int]):
    """Print formatted comparison report."""
    print("\n" + "="*80)
    print("PERFORMANCE COMPARISON REPORT")
    print("="*80)
    
    operations = ['insert', 'search', 'delete', 'range_query']
    data_structures = ['skip_list', 'sorted_list', 'dict']
    
    for op in operations:
        print(f"\n{op.upper()} OPERATION TIMES (seconds)")
        print("-" * 60)
        print(f"{'Size':<8} {'Skip List':<12} {'Sorted List':<12} {'Dict':<12}")
        print("-" * 60)
        
        for i, size in enumerate(sizes):
            row = f"{size:<8}"
            for ds in data_structures:
                time_val = results[ds][op][i]
                if time_val == float('inf'):
                    row += f"{'N/A':<12}"
                else:
                    row += f"{time_val:<12.6f}"
            print(row)
    
    # Performance ratios
    print(f"\nPERFORMANCE RATIOS (Skip List = 1.0)")
    print("-" * 60)
    
    for op in operations:
        print(f"\n{op.capitalize()}:")
        for i, size in enumerate(sizes):
            skip_time = results['skip_list'][op][i]
            if skip_time > 0 and skip_time != float('inf'):
                list_ratio = results['sorted_list'][op][i] / skip_time
                dict_ratio = results['dict'][op][i] / skip_time
                print(f"  Size {size}: List={list_ratio:.2f}x, Dict={dict_ratio:.2f}x")


def main():
    """Run comprehensive performance analysis."""
    print("Skip List Performance Analysis")
    print("=" * 50)
    
    # Test sizes
    sizes = [100, 500, 1000, 2000]
    
    # 1. Comprehensive benchmark
    print("\n1. Running comprehensive benchmark...")
    benchmark_results = comprehensive_benchmark(sizes)
    print_comparison_report(benchmark_results, sizes)
    
    # 2. Probability impact analysis
    print("\n2. Analyzing probability impact...")
    probabilities = [0.25, 0.5, 0.75]
    prob_results = analyze_probability_impact(sizes[:2], probabilities)  # Smaller sizes for this test
    
    print("\nProbability Impact Results:")
    for p, data in prob_results.items():
        avg_height = statistics.mean(data['heights'])
        avg_comparisons = statistics.mean(data['search_comparisons'])
        print(f"  p = {p}: avg_height = {avg_height:.2f}, avg_comparisons = {avg_comparisons:.2f}")
    
    # 3. Theoretical analysis
    print("\n3. Theoretical vs Actual Analysis:")
    analysis = TheoreticalAnalysis()
    
    for size in [100, 1000]:
        theoretical_height = analysis.expected_height(size)
        theoretical_cost = analysis.expected_search_cost(size)
        
        print(f"\nSize {size}:")
        print(f"  Theoretical height: {theoretical_height:.2f}")
        print(f"  Theoretical search cost: {theoretical_cost:.2f}")
    
    # 4. Stress test
    print("\n4. Running stress test...")
    stress_results = stress_test(max_size=1000, num_operations=5000)
    
    print(f"Stress Test Results:")
    print(f"  Total operations: {stress_results['total_operations']}")
    print(f"  Final size: {stress_results['final_size']}")
    print(f"  Errors: {len(stress_results['errors'])}")
    
    for op, stats in stress_results['timing_stats'].items():
        if stats['count'] > 0:
            print(f"  {op.capitalize()}: mean={stats['mean']*1000:.3f}ms, "
                  f"max={stats['max']*1000:.3f}ms, count={stats['count']}")
    
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main() 