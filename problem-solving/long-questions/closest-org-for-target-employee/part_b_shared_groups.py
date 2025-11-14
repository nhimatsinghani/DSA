"""
Part B: Shared Groups/Employees Organization - Single Closest Common Group

Problem Statement:
- Groups can be shared across different parts of the organization (graph structure)
- Employees can belong to multiple groups  
- Find ONE closest common group when multiple common groups exist

Key Differences from Part A:
1. Graph structure instead of tree (groups can have multiple parents)
2. Employees belong to multiple groups (many-to-many relationship)
3. Need strategy to pick ONE closest group among multiple candidates

Intuition & Algorithm: Multi-Source BFS Approach
================================================================

Why not LCA? 
- LCA assumes tree structure with single parent per node
- With shared groups, we have a graph with cycles and multiple paths
- Need distance-based definition of "closest"

Our Approach: Multi-Source BFS
1. **Start Points**: For each target employee, find ALL groups they belong to
2. **Simultaneous BFS**: Start BFS from all these starting groups simultaneously  
3. **Convergence Detection**: Track which groups are reachable from each employee
4. **First Common Group**: The first group reached by ALL employees' BFS is closest

Why This Works:
- **Distance-based**: Naturally finds group with minimum distance to farthest employee
- **Unambiguous**: First convergence point gives deterministic result
- **Handles Sharing**: Works with any graph topology (cycles, multiple parents)

Time Complexity: O(V + E + k*V) where V=groups, E=connections, k=target employees
Space Complexity: O(V + E + k*V) for graph storage and BFS state

Example Visualization:
```
    Root
   /  |  \\
  A    B  C  
 / \\  /|\\ |
E1 E2 E3 E4 E5

If E1 and E3 are targets:
- E1 starts BFS from {A} → A, Root
- E3 starts BFS from {B, C} → B, C, Root  
- First common group reached: Root (closest common group)
```
"""

from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict, deque


class SharedGroup:
    """Represents a group that can be shared across organization"""
    
    def __init__(self, group_id: str, name: str):
        self.group_id = group_id
        self.name = name
        self.parent_groups: Set['SharedGroup'] = set()  # Multiple parents allowed
        self.child_groups: Set['SharedGroup'] = set()   # Multiple children
        self.employees: Set[str] = set()
    
    def add_parent_group(self, parent: 'SharedGroup'):
        """Add a parent group (bidirectional relationship)"""
        self.parent_groups.add(parent)
        parent.child_groups.add(self)
    
    def add_child_group(self, child: 'SharedGroup'):
        """Add a child group (bidirectional relationship)"""
        self.child_groups.add(child)
        child.parent_groups.add(self)
    
    def add_employee(self, employee_id: str):
        """Add an employee to this group"""
        self.employees.add(employee_id)
    
    def remove_employee(self, employee_id: str):
        """Remove an employee from this group"""
        self.employees.discard(employee_id)
    
    def __repr__(self):
        return f"SharedGroup({self.group_id}: {self.name})"
    
    def __hash__(self):
        return hash(self.group_id)
    
    def __eq__(self, other):
        return isinstance(other, SharedGroup) and self.group_id == other.group_id


class SharedOrganization:
    """Manages organization with shared groups and employees"""
    
    def __init__(self):
        self.groups: Dict[str, SharedGroup] = {}
        self.employee_to_groups: Dict[str, Set[SharedGroup]] = defaultdict(set)
    
    def add_group(self, group: SharedGroup):
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
    
    def create_shared_relationship(self, parent_id: str, child_id: str):
        """Create parent-child relationship between groups"""
        if parent_id not in self.groups or child_id not in self.groups:
            raise ValueError("One or both groups not found")
        
        parent = self.groups[parent_id]
        child = self.groups[child_id]
        parent.add_child_group(child)
    
    def find_closest_common_group(self, employee_ids: List[str]) -> Optional[SharedGroup]:
        """
        Find the closest common group using Multi-Source BFS
        
        Algorithm:
        1. Collect all starting groups (groups containing target employees)
        2. Run BFS from each employee's groups simultaneously
        3. Track which groups are reached by each employee's BFS
        4. Return first group reached by ALL employees
        
        Args:
            employee_ids: List of target employee IDs
            
        Returns:
            SharedGroup: Closest common group, or None if no common group exists
        """
        if not employee_ids:
            return None
        
        # Step 1: Collect starting groups for each employee
        employee_start_groups = {}
        for emp_id in employee_ids:
            if emp_id not in self.employee_to_groups:
                raise ValueError(f"Employee {emp_id} not found in organization")
            
            start_groups = self.employee_to_groups[emp_id]
            if not start_groups:
                raise ValueError(f"Employee {emp_id} doesn't belong to any group")
            
            employee_start_groups[emp_id] = start_groups
        
        # Step 2: Run multi-source BFS
        return self._multi_source_bfs(employee_start_groups)
    
    def _multi_source_bfs(self, employee_start_groups: Dict[str, Set[SharedGroup]]) -> Optional[SharedGroup]:
        """
        Multi-source BFS to find first common group
        
        Strategy:
        - Maintain separate BFS queue for each employee
        - Track distance and visited groups per employee  
        - At each level, check if any group is reached by ALL employees
        - Return first such group (minimum distance to farthest employee)
        """
        num_employees = len(employee_start_groups)
        employee_ids = list(employee_start_groups.keys())
        
        # Initialize BFS state for each employee
        bfs_queues = {}
        visited_by_employee = {}
        distance_by_employee = {}
        
        for emp_id in employee_ids:
            bfs_queues[emp_id] = deque()
            visited_by_employee[emp_id] = set()
            distance_by_employee[emp_id] = {}
            
            # Add starting groups to queue
            for group in employee_start_groups[emp_id]:
                bfs_queues[emp_id].append((group, 0))
                visited_by_employee[emp_id].add(group)
                distance_by_employee[emp_id][group] = 0
        
        # Track groups reached by number of employees
        group_reach_count = defaultdict(set)  # group -> set of employees that reached it
        
        # Initial check: any group already common to all employees?
        for emp_id in employee_ids:
            for group in employee_start_groups[emp_id]:
                group_reach_count[group].add(emp_id)
                if len(group_reach_count[group]) == num_employees:
                    return group
        
        # BFS level by level
        max_distance = 0
        while any(bfs_queues.values()):
            max_distance += 1
            
            # Process one level for each employee
            for emp_id in employee_ids:
                if not bfs_queues[emp_id]:
                    continue
                
                current_level_size = len(bfs_queues[emp_id])
                
                for _ in range(current_level_size):
                    current_group, distance = bfs_queues[emp_id].popleft()
                    
                    # Explore parent groups
                    for parent_group in current_group.parent_groups:
                        if parent_group not in visited_by_employee[emp_id]:
                            new_distance = distance + 1
                            bfs_queues[emp_id].append((parent_group, new_distance))
                            visited_by_employee[emp_id].add(parent_group)
                            distance_by_employee[emp_id][parent_group] = new_distance
                            
                            # Track convergence
                            group_reach_count[parent_group].add(emp_id)
                            if len(group_reach_count[parent_group]) == num_employees:
                                return parent_group
            
            # Prevent infinite loops in case of cycles without convergence
            if max_distance > len(self.groups):
                break
        
        return None
    
    def get_paths_to_group(self, employee_id: str, target_group: SharedGroup) -> List[List[SharedGroup]]:
        """
        Find all paths from employee's groups to target group (for debugging)
        """
        if employee_id not in self.employee_to_groups:
            return []
        
        all_paths = []
        start_groups = self.employee_to_groups[employee_id]
        
        for start_group in start_groups:
            paths = self._find_paths_bfs(start_group, target_group)
            all_paths.extend(paths)
        
        return all_paths
    
    def _find_paths_bfs(self, start: SharedGroup, target: SharedGroup) -> List[List[SharedGroup]]:
        """Find all shortest paths between two groups"""
        if start == target:
            return [[start]]
        
        queue = deque([(start, [start])])
        visited = {start}
        paths = []
        target_distance = float('inf')
        
        while queue:
            current_group, path = queue.popleft()
            
            if len(path) > target_distance:
                break
            
            for parent_group in current_group.parent_groups:
                new_path = path + [parent_group]
                
                if parent_group == target:
                    if len(new_path) <= target_distance:
                        if len(new_path) < target_distance:
                            paths = []  # Found shorter path, clear previous
                            target_distance = len(new_path)
                        paths.append(new_path)
                elif parent_group not in visited:
                    visited.add(parent_group)
                    queue.append((parent_group, new_path))
        
        return paths
    
    def print_organization_graph(self):
        """Print the organization structure showing shared relationships"""
        print("Organization Graph Structure:")
        print("=" * 40)
        
        for group_id, group in self.groups.items():
            parents = [p.name for p in group.parent_groups]
            children = [c.name for c in group.child_groups]
            employees = sorted(group.employees)
            
            print(f"Group: {group.name} ({group_id})")
            print(f"  Parents: {parents if parents else 'None'}")
            print(f"  Children: {children if children else 'None'}")  
            print(f"  Employees: {employees if employees else 'None'}")
            print()


def create_shared_organization_example() -> SharedOrganization:
    """Create an organization with shared groups for testing"""
    
    org = SharedOrganization()
    
    # Create groups
    company = SharedGroup("company", "TechCorp")
    
    # Level 1: Main divisions
    engineering = SharedGroup("eng", "Engineering")
    product = SharedGroup("product", "Product")
    operations = SharedGroup("ops", "Operations")
    
    # Level 2: Shared teams (this creates the graph structure)
    backend = SharedGroup("backend", "Backend Development")
    frontend = SharedGroup("frontend", "Frontend Development") 
    devops = SharedGroup("devops", "DevOps")
    mobile = SharedGroup("mobile", "Mobile Development")
    
    # Level 3: Specialized teams
    api_team = SharedGroup("api", "API Team")
    ui_team = SharedGroup("ui", "UI Team")
    
    # Add groups to organization
    for group in [company, engineering, product, operations, backend, 
                  frontend, devops, mobile, api_team, ui_team]:
        org.add_group(group)
    
    # Create hierarchy relationships  
    company.add_child_group(engineering)
    company.add_child_group(product)
    company.add_child_group(operations)
    
    # Shared relationships: backend belongs to both Engineering and Operations
    engineering.add_child_group(backend)
    operations.add_child_group(backend)  # SHARED!
    
    # Frontend belongs to both Engineering and Product
    engineering.add_child_group(frontend)
    product.add_child_group(frontend)    # SHARED!
    
    # DevOps belongs to all three main divisions
    engineering.add_child_group(devops)
    operations.add_child_group(devops)   # SHARED!
    product.add_child_group(devops)      # SHARED!
    
    # Mobile only under Product
    product.add_child_group(mobile)
    
    # Specialized teams
    backend.add_child_group(api_team)
    frontend.add_child_group(ui_team)
    
    # Add employees with multiple group memberships
    
    # Backend employees
    org.add_employee_to_group("backend", "be_emp1")
    org.add_employee_to_group("backend", "be_emp2") 
    org.add_employee_to_group("api", "be_emp3")
    
    # Frontend employees  
    org.add_employee_to_group("frontend", "fe_emp1")
    org.add_employee_to_group("ui", "fe_emp2")
    org.add_employee_to_group("ui", "fe_emp3")
    
    # Mobile employees
    org.add_employee_to_group("mobile", "mobile_emp1")
    org.add_employee_to_group("mobile", "mobile_emp2")
    
    # DevOps employees (belong to multiple groups!)
    org.add_employee_to_group("devops", "devops_emp1")
    org.add_employee_to_group("devops", "devops_emp2")
    # DevOps employees also help with backend
    org.add_employee_to_group("backend", "devops_emp1")  # SHARED EMPLOYEE!
    
    # Product employees
    org.add_employee_to_group("product", "product_emp1")
    # Product employee also works with frontend
    org.add_employee_to_group("frontend", "product_emp1")  # SHARED EMPLOYEE!
    
    return org


def demonstrate_part_b():
    """Demonstrate Part B functionality with shared groups/employees"""
    
    print("=== Part B: Shared Groups Organization - Single Closest Common Group ===\n")
    
    # Create shared organization
    org = create_shared_organization_example()
    
    print("Shared Organization Structure:")
    org.print_organization_graph()
    
    # Test cases demonstrating shared group scenarios
    test_cases = [
        (["be_emp1", "be_emp2"], "Same backend team"),
        (["be_emp1", "fe_emp1"], "Backend vs Frontend (both under Engineering)"),
        (["be_emp3", "fe_emp2"], "API team vs UI team"),
        (["devops_emp1", "be_emp1"], "Shared employee (DevOps+Backend) vs Backend-only"),
        (["product_emp1", "fe_emp1"], "Shared employee (Product+Frontend) vs Frontend-only"),
        (["devops_emp1", "mobile_emp1"], "DevOps (multiple parents) vs Mobile"),
        (["be_emp1", "fe_emp1", "mobile_emp1"], "Three different divisions"),
        (["devops_emp2", "product_emp1", "be_emp3"], "Complex multi-shared scenario"),
    ]
    
    print("SHARED GROUP TEST RESULTS:")
    print("=" * 60)
    
    for employee_ids, description in test_cases:
        try:
            common_group = org.find_closest_common_group(employee_ids)
            print(f"Employees: {employee_ids}")
            print(f"Context: {description}")
            
            if common_group:
                print(f"Closest Common Group: {common_group.name} ({common_group.group_id})")
                
                # Show employee group memberships
                print("Employee group memberships:")
                for emp_id in employee_ids:
                    groups = org.employee_to_groups[emp_id]
                    group_names = [g.name for g in groups]
                    print(f"  {emp_id}: {group_names}")
                
                # Show reasoning with paths
                print("Sample paths to common group:")
                for emp_id in employee_ids[:2]:  # Show first 2 for brevity
                    paths = org.get_paths_to_group(emp_id, common_group)
                    if paths:
                        path_names = " -> ".join([g.name for g in paths[0]])
                        print(f"  {emp_id}: {path_names}")
            else:
                print("No common group found!")
            
            print("-" * 60)
        
        except Exception as e:
            print(f"Error for {employee_ids}: {e}")
            print("-" * 60)


if __name__ == "__main__":
    demonstrate_part_b()
