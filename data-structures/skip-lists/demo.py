"""
Skip List Interactive Demo
=========================

Interactive demonstration of Skip List operations and features.
"""

from skiplist import SkipList, create_skip_list_from_list
import random
import time


def demo_basic_operations():
    """Demonstrate basic Skip List operations."""
    print("\n" + "="*60)
    print("DEMO 1: Basic Operations")
    print("="*60)
    
    # Create a skip list
    sl = SkipList(max_level=4, p=0.5)
    print("Created Skip List with max_level=4, p=0.5")
    
    # Insert some data
    data = [
        (10, "ten"), (20, "twenty"), (5, "five"), (15, "fifteen"),
        (25, "twenty-five"), (1, "one"), (30, "thirty")
    ]
    
    print("\nInserting data:")
    for key, value in data:
        inserted = sl.insert(key, value)
        print(f"  Insert {key}:{value} -> {'New' if inserted else 'Updated'}")
    
    print(f"\nSkip List size: {len(sl)}")
    sl.display()
    
    # Search operations
    print("\nSearch Operations:")
    test_keys = [1, 15, 100, 20]
    for key in test_keys:
        start_time = time.perf_counter()
        result = sl.search(key)
        end_time = time.perf_counter()
        print(f"  Search {key}: {result} (comparisons: {sl.search_comparisons}, "
              f"time: {(end_time - start_time) * 1000:.3f}ms)")
    
    # Range queries
    print("\nRange Queries:")
    ranges = [(5, 20), (1, 10), (25, 50)]
    for start, end in ranges:
        result = sl.range_query(start, end)
        print(f"  Range [{start}, {end}]: {result}")
    
    # Delete operations
    print("\nDelete Operations:")
    delete_keys = [15, 100, 5]
    for key in delete_keys:
        deleted = sl.delete(key)
        print(f"  Delete {key}: {'Success' if deleted else 'Not found'}")
    
    print("\nAfter deletions:")
    sl.display(show_levels=False)


def demo_performance_comparison():
    """Demonstrate performance characteristics."""
    print("\n" + "="*60)
    print("DEMO 2: Performance Analysis")
    print("="*60)
    
    # Test with different sizes
    sizes = [100, 1000, 5000]
    
    for size in sizes:
        print(f"\nTesting with {size} elements:")
        
        # Create skip list and insert random data
        sl = SkipList()
        data = [(random.randint(1, size * 2), f"value_{i}") for i in range(size)]
        
        # Time insertions
        start_time = time.perf_counter()
        for key, value in data:
            sl.insert(key, value)
        insert_time = time.perf_counter() - start_time
        
        # Test search performance
        search_keys = [random.choice(data)[0] for _ in range(100)]
        start_time = time.perf_counter()
        total_comparisons = 0
        
        for key in search_keys:
            sl.search(key)
            total_comparisons += sl.search_comparisons
        
        search_time = time.perf_counter() - start_time
        avg_comparisons = total_comparisons / len(search_keys)
        
        # Get statistics
        stats = sl.get_statistics()
        
        print(f"  Insert time: {insert_time:.4f}s ({insert_time/size*1000:.3f}ms per element)")
        print(f"  Search time: {search_time:.4f}s ({search_time/len(search_keys)*1000:.3f}ms per search)")
        print(f"  Average comparisons per search: {avg_comparisons:.2f}")
        print(f"  Current max level: {stats['current_max_level']}")
        print(f"  Expected height: {stats['expected_height']:.2f}")
        print(f"  Average node level: {stats['average_node_level']:.2f}")


def demo_probability_effects():
    """Demonstrate the effect of different probability values."""
    print("\n" + "="*60)
    print("DEMO 3: Probability Effects")
    print("="*60)
    
    # Test different probability values
    probabilities = [0.25, 0.5, 0.75]
    size = 1000
    
    # Generate consistent data
    data = [(i, f"value_{i}") for i in range(1, size + 1)]
    
    for p in probabilities:
        print(f"\nTesting with probability p = {p}:")
        
        sl = SkipList(max_level=16, p=p)
        
        # Insert data
        for key, value in data:
            sl.insert(key, value)
        
        # Test search performance
        search_keys = [random.randint(1, size) for _ in range(100)]
        total_comparisons = 0
        
        for key in search_keys:
            sl.search(key)
            total_comparisons += sl.search_comparisons
        
        avg_comparisons = total_comparisons / len(search_keys)
        stats = sl.get_statistics()
        
        print(f"  Max level reached: {stats['current_max_level']}")
        print(f"  Expected height: {stats['expected_height']:.2f}")
        print(f"  Average comparisons: {avg_comparisons:.2f}")
        print(f"  Average node level: {stats['average_node_level']:.2f}")


def demo_range_queries():
    """Demonstrate range query capabilities."""
    print("\n" + "="*60)
    print("DEMO 4: Range Query Capabilities")
    print("="*60)
    
    # Create skip list with student scores
    students = [
        (95, "Alice"), (87, "Bob"), (92, "Charlie"), (78, "David"),
        (85, "Eve"), (91, "Frank"), (88, "Grace"), (76, "Henry"),
        (93, "Iris"), (82, "Jack"), (89, "Kate"), (94, "Liam")
    ]
    
    sl = create_skip_list_from_list(students)
    
    print("Student Scores:")
    for score, name in sl:
        print(f"  {score}: {name}")
    
    print("\nRange Queries (Grade Ranges):")
    
    # Different grade ranges
    ranges = [
        (90, 100, "A grades (90-100)"),
        (80, 89, "B grades (80-89)"),
        (70, 79, "C grades (70-79)"),
        (85, 95, "High performers (85-95)")
    ]
    
    for start, end, description in ranges:
        result = sl.range_query(start, end)
        print(f"  {description}: {len(result)} students")
        for score, name in result:
            print(f"    {score}: {name}")
        print()


def demo_real_world_scenario():
    """Demonstrate a real-world scenario: Event scheduling."""
    print("\n" + "="*60)
    print("DEMO 5: Real-world Scenario - Event Scheduler")
    print("="*60)
    
    # Create an event scheduler using skip list
    scheduler = SkipList()
    
    # Add events (timestamp, event_description)
    events = [
        (900, "Team standup meeting"),
        (1030, "Code review session"),
        (1200, "Lunch break"),
        (1400, "Architecture discussion"),
        (1500, "Sprint planning"),
        (1630, "Client demo"),
        (920, "Coffee with mentor"),
        (1315, "One-on-one with manager"),
        (1045, "Bug triage"),
    ]
    
    print("Adding events to scheduler:")
    for time, event in events:
        scheduler.insert(time, event)
        # Convert to readable time
        hours = time // 100
        minutes = time % 100
        print(f"  {hours:02d}:{minutes:02d} - {event}")
    
    print(f"\nScheduled {len(scheduler)} events")
    
    # Display schedule in chronological order
    print("\nDaily Schedule:")
    for time, event in scheduler:
        hours = time // 100
        minutes = time % 100
        print(f"  {hours:02d}:{minutes:02d} - {event}")
    
    # Find events in specific time ranges
    print("\nMorning meetings (9:00 AM - 12:00 PM):")
    morning_events = scheduler.range_query(900, 1200)
    for time, event in morning_events:
        hours = time // 100
        minutes = time % 100
        print(f"  {hours:02d}:{minutes:02d} - {event}")
    
    # Cancel an event
    print(f"\nCancelling 10:45 AM event: {scheduler.delete(1045)}")
    
    # Add urgent meeting
    scheduler.insert(1000, "URGENT: Production issue meeting")
    print("Added urgent meeting at 10:00 AM")
    
    print("\nUpdated morning schedule:")
    morning_events = scheduler.range_query(900, 1200)
    for time, event in morning_events:
        hours = time // 100
        minutes = time % 100
        print(f"  {hours:02d}:{minutes:02d} - {event}")


def demo_statistics_analysis():
    """Demonstrate statistical analysis of Skip List structure."""
    print("\n" + "="*60)
    print("DEMO 6: Statistical Analysis")
    print("="*60)
    
    # Create skip list with many elements
    sl = SkipList(max_level=10, p=0.5)
    
    # Insert random data
    size = 2000
    data = [(random.randint(1, size * 2), f"item_{i}") for i in range(size)]
    
    for key, value in data:
        sl.insert(key, value)
    
    stats = sl.get_statistics()
    
    print(f"Skip List with {size} elements:")
    print(f"  Size: {stats['size']}")
    print(f"  Current max level: {stats['current_max_level']}")
    print(f"  Max possible level: {stats['max_possible_level']}")
    print(f"  Probability: {stats['probability']}")
    print(f"  Expected height: {stats['expected_height']:.2f}")
    print(f"  Average node level: {stats['average_node_level']:.2f}")
    
    print("\nLevel distribution:")
    level_counts = stats['level_counts']
    for level, count in enumerate(level_counts):
        percentage = (count / stats['size']) * 100
        bar = "█" * int(percentage // 2)
        print(f"  Level {level:2d}: {count:4d} nodes ({percentage:5.1f}%) {bar}")
    
    # Theoretical vs actual comparison
    print(f"\nTheoretical vs Actual:")
    theoretical_avg_level = 1 / (1 - stats['probability'])
    print(f"  Theoretical avg level: {theoretical_avg_level:.2f}")
    print(f"  Actual avg level: {stats['average_node_level']:.2f}")
    print(f"  Efficiency ratio: {theoretical_avg_level / stats['average_node_level']:.2f}")


def interactive_demo():
    """Interactive demo allowing user input."""
    print("\n" + "="*60)
    print("INTERACTIVE DEMO")
    print("="*60)
    
    sl = SkipList()
    
    while True:
        print("\nOptions:")
        print("1. Insert key-value pair")
        print("2. Search for key")
        print("3. Delete key")
        print("4. Range query")
        print("5. Display skip list")
        print("6. Show statistics")
        print("7. Clear skip list")
        print("0. Exit")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            try:
                key = int(input("Enter key (integer): "))
                value = input("Enter value: ")
                inserted = sl.insert(key, value)
                print(f"{'Inserted' if inserted else 'Updated'} {key}:{value}")
            except ValueError:
                print("Please enter a valid integer for key")
        elif choice == '2':
            try:
                key = int(input("Enter key to search: "))
                result = sl.search(key)
                if result is not None:
                    print(f"Found: {key} -> {result} (comparisons: {sl.search_comparisons})")
                else:
                    print(f"Key {key} not found (comparisons: {sl.search_comparisons})")
            except ValueError:
                print("Please enter a valid integer")
        elif choice == '3':
            try:
                key = int(input("Enter key to delete: "))
                deleted = sl.delete(key)
                print(f"{'Deleted' if deleted else 'Key not found'}: {key}")
            except ValueError:
                print("Please enter a valid integer")
        elif choice == '4':
            try:
                start = int(input("Enter start key: "))
                end = int(input("Enter end key: "))
                result = sl.range_query(start, end)
                print(f"Range [{start}, {end}]: {result}")
            except ValueError:
                print("Please enter valid integers")
        elif choice == '5':
            if len(sl) == 0:
                print("Skip list is empty")
            else:
                sl.display()
        elif choice == '6':
            stats = sl.get_statistics()
            print("Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
        elif choice == '7':
            sl.clear()
            print("Skip list cleared")
        else:
            print("Invalid choice")


def main():
    """Main demo function."""
    print("Skip List Comprehensive Demo")
    print("=" * 60)
    
    demos = [
        ("Basic Operations", demo_basic_operations),
        ("Performance Analysis", demo_performance_comparison),
        ("Probability Effects", demo_probability_effects),
        ("Range Queries", demo_range_queries),
        ("Real-world Scenario", demo_real_world_scenario),
        ("Statistical Analysis", demo_statistics_analysis),
        ("Interactive Demo", interactive_demo)
    ]
    
    while True:
        print("\nAvailable Demos:")
        for i, (name, _) in enumerate(demos, 1):
            print(f"{i}. {name}")
        print("0. Exit")
        
        try:
            choice = int(input("\nSelect a demo (0-7): "))
            if choice == 0:
                print("Thanks for exploring Skip Lists!")
                break
            elif 1 <= choice <= len(demos):
                demos[choice - 1][1]()
            else:
                print("Invalid choice")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    main() 