"""
Part D: Single-Level Organization - Flat Group Structure

Problem Statement:
- Company consists of single level of groups with no subgroups
- Each group has a set of employees
- Find common group(s) for target employees

Key Simplifications from Parts A & B:
1. No hierarchy - flat structure eliminates tree/graph traversal
2. No parent-child relationships between groups
3. No shared group inheritance - each group is independent

Intuition & Algorithm: Set Intersection Approach
===============================================

Since there's no hierarchy, "closest common group" becomes:
"Which group(s) contain ALL target employees?"

This transforms the problem into a simple set intersection:
1. **Group Membership Check**: For each group, check if it contains ALL target employees
2. **Multiple Solutions**: If multiple groups qualify, apply tie-breaking strategy
3. **No Solution**: If no group contains all employees, no common group exists

Tie-Breaking Strategies:
- **Smallest Group**: Choose group with fewest total employees (most specific)
- **Alphabetical**: Choose lexicographically first group name (deterministic)
- **First Found**: Choose first group encountered (implementation-dependent)
- **All Groups**: Return all qualifying groups (let caller decide)

Time Complexity: O(G × k) where G=number of groups, k=target employees
Space Complexity: O(G + E) where E=total employees across all groups

Example:
```
Groups:
- Marketing: {emp1, emp2, emp3, emp5}
- Sales: {emp1, emp4}  
- Engineering: {emp1, emp2, emp6, emp7}
- Leadership: {emp1, emp2, emp3, emp4, emp5, emp6, emp7}

Target: [emp1, emp2]
Common Groups: Marketing, Engineering, Leadership
Smallest: Marketing (4 employees)
```

Edge Cases:
- Employee not in any group → Error
- Single employee → Any group containing that employee
- No common group → None/empty result
- Employee in multiple groups → Consider all memberships
"""

from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict


class FlatGroup:
    """Represents a simple group in flat organization structure"""
    
    def __init__(self, group_id: str, name: str):
        self.group_id = group_id
        self.name = name
        self.employees: Set[str] = set()
    
    def add_employee(self, employee_id: str):
        """Add an employee to this group"""
        self.employees.add(employee_id)
    
    def remove_employee(self, employee_id: str):
        """Remove an employee from this group"""
        self.employees.discard(employee_id)
    
    def contains_all_employees(self, employee_ids: List[str]) -> bool:
        """Check if this group contains all specified employees"""
        return all(emp_id in self.employees for emp_id in employee_ids)
    
    def __repr__(self):
        return f"FlatGroup({self.group_id}: {self.name}, {len(self.employees)} employees)"
    
    def __hash__(self):
        return hash(self.group_id)
    
    def __eq__(self, other):
        return isinstance(other, FlatGroup) and self.group_id == other.group_id


class SingleLevelOrganization:
    """Manages flat organization structure with no hierarchy"""
    
    def __init__(self):
        self.groups: Dict[str, FlatGroup] = {}
        self.employee_to_groups: Dict[str, Set[FlatGroup]] = defaultdict(set)
    
    def add_group(self, group: FlatGroup):
        """Add a group to the organization"""
        self.groups[group.group_id] = group
        
        # Update employee mappings
        for employee_id in group.employees:
            self.employee_to_groups[employee_id].add(group)
    
    def add_employee_to_group(self, group_id: str, employee_id: str):
        """Add an employee to a specific group"""
        if group_id not in self.groups:
            raise ValueError(f"Group {group_id} not found")
        
        group = self.groups[group_id]
        group.add_employee(employee_id)
        self.employee_to_groups[employee_id].add(group)
    
    def remove_employee_from_group(self, group_id: str, employee_id: str):
        """Remove an employee from a specific group"""
        if group_id not in self.groups:
            raise ValueError(f"Group {group_id} not found")
        
        group = self.groups[group_id]
        group.remove_employee(employee_id)
        self.employee_to_groups[employee_id].discard(group)
    
    def find_common_groups(self, employee_ids: List[str]) -> List[FlatGroup]:
        """
        Find all groups that contain ALL target employees
        
        Args:
            employee_ids: List of target employee IDs
            
        Returns:
            List[FlatGroup]: All groups containing all target employees
        """
        if not employee_ids:
            return []
        
        # Validate all employees exist
        for emp_id in employee_ids:
            if emp_id not in self.employee_to_groups:
                raise ValueError(f"Employee {emp_id} not found in organization")
        
        # Find groups containing all employees
        common_groups = []
        for group in self.groups.values():
            if group.contains_all_employees(employee_ids):
                common_groups.append(group)
        
        return common_groups
    
    def find_closest_common_group_smallest(self, employee_ids: List[str]) -> Optional[FlatGroup]:
        """
        Find closest common group using 'smallest group' strategy
        
        Rationale: Smallest group is most specific/closest to the employees
        """
        common_groups = self.find_common_groups(employee_ids)
        
        if not common_groups:
            return None
        
        # Return group with minimum number of employees
        return min(common_groups, key=lambda g: len(g.employees))
    
    def find_closest_common_group_alphabetical(self, employee_ids: List[str]) -> Optional[FlatGroup]:
        """
        Find closest common group using alphabetical strategy
        
        Rationale: Deterministic, reproducible selection
        """
        common_groups = self.find_common_groups(employee_ids)
        
        if not common_groups:
            return None
        
        # Return lexicographically first group name
        return min(common_groups, key=lambda g: g.name)
    
    def find_closest_common_group_first_found(self, employee_ids: List[str]) -> Optional[FlatGroup]:
        """
        Find closest common group using 'first found' strategy
        
        Rationale: Fastest execution, implementation-dependent order
        """
        if not employee_ids:
            return None
        
        # Validate all employees exist
        for emp_id in employee_ids:
            if emp_id not in self.employee_to_groups:
                raise ValueError(f"Employee {emp_id} not found in organization")
        
        # Return first group that contains all employees
        for group in self.groups.values():
            if group.contains_all_employees(employee_ids):
                return group
        
        return None
    
    def get_employee_group_memberships(self, employee_id: str) -> Set[FlatGroup]:
        """Get all groups an employee belongs to"""
        return self.employee_to_groups.get(employee_id, set())
    
    def print_organization(self):
        """Print the flat organization structure"""
        print("Single-Level Organization Structure:")
        print("=" * 50)
        
        for group_id, group in sorted(self.groups.items()):
            employees = sorted(group.employees)
            print(f"Group: {group.name} ({group_id})")
            print(f"  Employees ({len(employees)}): {employees}")
            print()
    
    def get_organization_stats(self) -> Dict[str, int]:
        """Get statistics about the organization"""
        total_employees = len(self.employee_to_groups)
        total_groups = len(self.groups)
        
        # Calculate employees per group distribution
        group_sizes = [len(group.employees) for group in self.groups.values()]
        avg_group_size = sum(group_sizes) / total_groups if total_groups > 0 else 0
        
        # Calculate group memberships per employee
        memberships = [len(groups) for groups in self.employee_to_groups.values()]
        avg_memberships = sum(memberships) / total_employees if total_employees > 0 else 0
        
        return {
            'total_groups': total_groups,
            'total_employees': total_employees,
            'avg_group_size': round(avg_group_size, 2),
            'avg_employee_memberships': round(avg_memberships, 2),
            'max_group_size': max(group_sizes) if group_sizes else 0,
            'min_group_size': min(group_sizes) if group_sizes else 0,
        }


def create_sample_flat_organization() -> SingleLevelOrganization:
    """Create a sample flat organization for testing"""
    
    org = SingleLevelOrganization()
    
    # Create groups
    marketing = FlatGroup("marketing", "Marketing")
    sales = FlatGroup("sales", "Sales") 
    engineering = FlatGroup("engineering", "Engineering")
    leadership = FlatGroup("leadership", "Leadership")
    product = FlatGroup("product", "Product")
    design = FlatGroup("design", "Design")
    
    # Add employees to groups (some employees in multiple groups)
    
    # Marketing team
    marketing.add_employee("emp1")
    marketing.add_employee("emp2") 
    marketing.add_employee("emp3")
    marketing.add_employee("emp5")
    
    # Sales team
    sales.add_employee("emp1")  # emp1 in both marketing and sales
    sales.add_employee("emp4")
    sales.add_employee("emp9")
    
    # Engineering team
    engineering.add_employee("emp1")  # emp1 in marketing, sales, engineering
    engineering.add_employee("emp2")  # emp2 in marketing, engineering  
    engineering.add_employee("emp6")
    engineering.add_employee("emp7")
    engineering.add_employee("emp8")
    
    # Leadership (contains members from other teams)
    leadership.add_employee("emp1")
    leadership.add_employee("emp2")
    leadership.add_employee("emp3")
    leadership.add_employee("emp4")
    leadership.add_employee("emp5")
    leadership.add_employee("emp6")
    leadership.add_employee("emp7")
    
    # Product team (smaller, focused)
    product.add_employee("emp2")
    product.add_employee("emp5")
    product.add_employee("emp10")
    
    # Design team (very small)
    design.add_employee("emp5")
    design.add_employee("emp11")
    
    # Add groups to organization
    for group in [marketing, sales, engineering, leadership, product, design]:
        org.add_group(group)
    
    return org


def demonstrate_part_d():
    """Demonstrate Part D functionality with flat organization"""
    
    print("=== Part D: Single-Level Organization - Flat Group Structure ===\n")
    
    # Create sample organization
    org = create_sample_flat_organization()
    
    print("Flat Organization Structure:")
    org.print_organization()
    
    # Show organization statistics
    stats = org.get_organization_stats()
    print("Organization Statistics:")
    for key, value in stats.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    print()
    
    # Test cases for different scenarios
    test_cases = [
        (["emp1"], "Single employee (multi-group member)"),
        (["emp11"], "Single employee (single group)"),
        (["emp1", "emp2"], "Two employees with multiple common groups"),
        (["emp2", "emp5"], "Two employees with fewer common groups"),
        (["emp1", "emp2", "emp3"], "Three employees"),
        (["emp6", "emp7"], "Engineering-only employees"),
        (["emp1", "emp8"], "Cross-group employees"),
        (["emp1", "emp2", "emp3", "emp4", "emp5"], "Many employees"),
        (["emp2", "emp11"], "Employees with no common group"),
    ]
    
    print("SINGLE-LEVEL ORGANIZATION TEST RESULTS:")
    print("=" * 60)
    
    for employee_ids, description in test_cases:
        try:
            # Show all common groups
            common_groups = org.find_common_groups(employee_ids)
            
            # Show different tie-breaking strategies
            smallest = org.find_closest_common_group_smallest(employee_ids)
            alphabetical = org.find_closest_common_group_alphabetical(employee_ids)
            first_found = org.find_closest_common_group_first_found(employee_ids)
            
            print(f"Employees: {employee_ids}")
            print(f"Context: {description}")
            
            if common_groups:
                print(f"All Common Groups ({len(common_groups)}): {[g.name for g in common_groups]}")
                print("Strategy Results:")
                print(f"  Smallest Group: {smallest.name} ({len(smallest.employees)} employees)")
                print(f"  Alphabetical: {alphabetical.name}")
                print(f"  First Found: {first_found.name}")
            else:
                print("No common groups found")
            
            # Show employee group memberships
            print("Employee group memberships:")
            for emp_id in employee_ids:
                groups = org.get_employee_group_memberships(emp_id)
                group_names = [g.name for g in groups]
                print(f"  {emp_id}: {group_names}")
            
            print("-" * 60)
        
        except Exception as e:
            print(f"Error for {employee_ids}: {e}")
            print("-" * 60)


if __name__ == "__main__":
    demonstrate_part_d()
