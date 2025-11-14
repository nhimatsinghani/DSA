"""
Part A: Basic Hierarchical Organization - Closest Common Parent Group Finder

Problem Statement:
- Hierarchical organization structure (tree-like)
- Each group can have multiple subgroups
- Each employee belongs to exactly one group
- Find closest common parent group for a set of target employees

Approach: Lowest Common Ancestor (LCA) in Tree
1. Build parent pointers for navigation
2. For each target employee, find path from their group to root
3. Find the first common group in these paths (LCA)

Time Complexity: O(n + h*k) where n=groups, h=height, k=target employees
Space Complexity: O(n + h*k) for parent pointers and paths
"""

from typing import Dict, List, Set, Optional
from collections import defaultdict, deque


class Group:
    """Represents a group in the organizational hierarchy"""
    
    def __init__(self, group_id: str, name: str):
        self.group_id = group_id
        self.name = name
        self.subgroups: List['Group'] = []
        self.employees: Set[str] = set()
        self.parent: Optional['Group'] = None
    
    def add_subgroup(self, subgroup: 'Group'):
        """Add a subgroup to this group"""
        self.subgroups.append(subgroup)
        subgroup.parent = self
    
    def add_employee(self, employee_id: str):
        """Add an employee to this group"""
        self.employees.add(employee_id)
    
    def __repr__(self):
        return f"Group({self.group_id}: {self.name})"


class HierarchicalOrganization:
    """Manages the hierarchical organization structure"""
    
    def __init__(self, root_group: Group):
        self.root = root_group
        self.employee_to_group: Dict[str, Group] = {}
        self.groups: Dict[str, Group] = {}
        self._build_mappings()
    
    def _build_mappings(self):
        """Build employee-to-group and group mappings using DFS"""
        stack = [self.root]
        
        while stack:
            group = stack.pop()
            self.groups[group.group_id] = group
            
            # Map all employees in this group
            for employee in group.employees:
                self.employee_to_group[employee] = group
            
            # Add subgroups to stack for processing
            stack.extend(group.subgroups)
    
    def get_path_to_root(self, group: Group) -> List[Group]:
        """Get path from group to root (bottom-up)"""
        path = []
        current = group
        
        while current:
            path.append(current)
            current = current.parent
        
        return path
    
    def find_closest_common_group(self, employee_ids: List[str]) -> Optional[Group]:
        """
        Find the closest common parent group for target employees
        
        Algorithm:
        1. Get the group for each employee
        2. Find path from each group to root
        3. Find the deepest common group in all paths (LCA)
        
        Args:
            employee_ids: List of target employee IDs
            
        Returns:
            Group: Closest common parent group, or None if no common group
        """
        if not employee_ids:
            return None
        
        # Step 1: Get groups for each employee
        employee_groups = []
        for emp_id in employee_ids:
            if emp_id not in self.employee_to_group:
                raise ValueError(f"Employee {emp_id} not found in organization")
            employee_groups.append(self.employee_to_group[emp_id])
        
        # Step 2: Get paths to root for each group
        paths = [self.get_path_to_root(group) for group in employee_groups]
        
        # Step 3: Find LCA using path intersection
        return self._find_lca_from_paths(paths)
    
    def _find_lca_from_paths(self, paths: List[List[Group]]) -> Optional[Group]:
        """
        Find LCA from multiple paths to root
        
        Strategy: Start from root (end of paths) and go down until divergence
        """
        if not paths:
            return None
        
        # Reverse paths to start from root
        reversed_paths = [path[::-1] for path in paths]
        
        # Find minimum path length
        min_length = min(len(path) for path in reversed_paths)
        
        # Find the deepest common group
        lca = None
        for i in range(min_length):
            # Check if all paths have the same group at position i
            current_group = reversed_paths[0][i]
            if all(path[i] == current_group for path in reversed_paths):
                lca = current_group
            else:
                break
        
        return lca
    
    def add_group(self, parent_group_id: str, new_group: Group):
        """Add a new group to the hierarchy"""
        if parent_group_id not in self.groups:
            raise ValueError(f"Parent group {parent_group_id} not found")
        
        parent = self.groups[parent_group_id]
        parent.add_subgroup(new_group)
        self.groups[new_group.group_id] = new_group
    
    def add_employee_to_group(self, group_id: str, employee_id: str):
        """Add an employee to a specific group"""
        if group_id not in self.groups:
            raise ValueError(f"Group {group_id} not found")
        
        # Remove from previous group if exists
        if employee_id in self.employee_to_group:
            old_group = self.employee_to_group[employee_id]
            old_group.employees.remove(employee_id)
        
        # Add to new group
        group = self.groups[group_id]
        group.add_employee(employee_id)
        self.employee_to_group[employee_id] = group
    
    def print_hierarchy(self, group: Group = None, level: int = 0):
        """Print the organization hierarchy"""
        if group is None:
            group = self.root
        
        indent = "  " * level
        employees_str = f" (Employees: {sorted(group.employees)})" if group.employees else ""
        print(f"{indent}{group.name}{employees_str}")
        
        for subgroup in group.subgroups:
            self.print_hierarchy(subgroup, level + 1)


def create_sample_organization() -> HierarchicalOrganization:
    """Create a sample organization for testing"""
    
    # Create hierarchy: Company > Engineering > [Backend, Frontend] > Teams
    company = Group("company", "Atlassian")
    
    # Level 1: Departments
    engineering = Group("eng", "Engineering")
    marketing = Group("mkt", "Marketing")
    
    # Level 2: Engineering subdivisions
    backend_eng = Group("backend", "Backend Engineering")
    frontend_eng = Group("frontend", "Frontend Engineering")
    devops = Group("devops", "DevOps")
    
    # Level 3: Teams
    search_team = Group("search", "Search Team")
    api_team = Group("api", "API Team")
    ui_team = Group("ui", "UI Team")
    mobile_team = Group("mobile", "Mobile Team")
    
    # Build hierarchy
    company.add_subgroup(engineering)
    company.add_subgroup(marketing)
    
    engineering.add_subgroup(backend_eng)
    engineering.add_subgroup(frontend_eng)
    engineering.add_subgroup(devops)
    
    backend_eng.add_subgroup(search_team)
    backend_eng.add_subgroup(api_team)
    frontend_eng.add_subgroup(ui_team)
    frontend_eng.add_subgroup(mobile_team)
    
    # Add employees
    search_team.add_employee("emp1")
    search_team.add_employee("emp2")
    api_team.add_employee("emp3")
    api_team.add_employee("emp4")
    ui_team.add_employee("emp5")
    ui_team.add_employee("emp6")
    mobile_team.add_employee("emp7")
    devops.add_employee("emp8")
    marketing.add_employee("emp9")
    marketing.add_employee("emp10")
    
    return HierarchicalOrganization(company)


def create_uneven_depth_organization() -> HierarchicalOrganization:
    """Create an organization with uneven depths to test LCA logic"""
    
    # Create hierarchy with intentionally uneven depths
    company = Group("company", "TechCorp")
    
    # Level 1
    engineering = Group("eng", "Engineering")
    company.add_subgroup(engineering)
    
    # Level 2 - Backend has deeper nesting, Frontend is shallow
    backend = Group("backend", "Backend Engineering")
    frontend = Group("frontend", "Frontend Engineering") 
    engineering.add_subgroup(backend)
    engineering.add_subgroup(frontend)
    
    # Level 3 - Only backend goes deeper
    backend_services = Group("services", "Backend Services")
    backend.add_subgroup(backend_services)
    
    # Level 4 - Even deeper for some backend employees
    auth_service = Group("auth", "Authentication Service")
    backend_services.add_subgroup(auth_service)
    
    # Level 5 - Deepest level
    auth_core = Group("auth_core", "Auth Core Team")
    auth_service.add_subgroup(auth_core)
    
    # Add employees at different depths
    # Depth 5: Very deep employee
    auth_core.add_employee("deep_emp1")
    auth_core.add_employee("deep_emp2")
    
    # Depth 4: Moderately deep employee  
    auth_service.add_employee("mid_deep_emp1")
    
    # Depth 3: Medium depth employee
    backend_services.add_employee("medium_emp1")
    
    # Depth 2: Shallow employee (same level as departments)
    backend.add_employee("shallow_backend_emp1")
    frontend.add_employee("shallow_frontend_emp1")
    
    # Depth 1: Very shallow employee (department level)
    engineering.add_employee("very_shallow_emp1")
    
    return HierarchicalOrganization(company)


def demonstrate_part_a():
    """Demonstrate Part A functionality with examples"""
    
    print("=== Part A: Hierarchical Organization - Closest Common Group ===\n")
    
    # Create sample organization
    org = create_sample_organization()
    
    print("Organization Hierarchy:")
    org.print_hierarchy()
    print()
    
    # Test cases
    test_cases = [
        (["emp1", "emp2"], "Same team (Search Team)"),
        (["emp1", "emp3"], "Different teams, same department (Backend Engineering)"),
        (["emp1", "emp5"], "Different departments (Engineering)"),
        (["emp1", "emp9"], "Different top-level departments (Company)"),
        (["emp3", "emp4", "emp8"], "Mixed: teams + department level (Engineering)"),
        (["emp5", "emp6", "emp7"], "Different frontend teams (Frontend Engineering)"),
    ]
    
    for employee_ids, description in test_cases:
        try:
            common_group = org.find_closest_common_group(employee_ids)
            print(f"Employees: {employee_ids}")
            print(f"Context: {description}")
            print(f"Closest Common Group: {common_group.name} ({common_group.group_id})")
            
            # Show the reasoning
            print("Employee locations:")
            for emp_id in employee_ids:
                emp_group = org.employee_to_group[emp_id]
                path = org.get_path_to_root(emp_group)
                path_names = " -> ".join([g.name for g in reversed(path)])
                print(f"  {emp_id}: {path_names}")
            
            print("-" * 60)
        
        except Exception as e:
            print(f"Error for {employee_ids}: {e}")
            print("-" * 60)
    
    print("\n" + "=" * 80)
    print("=== TESTING UNEVEN DEPTH SCENARIOS ===")
    print("=" * 80 + "\n")
    
    # Test with uneven depths
    uneven_org = create_uneven_depth_organization()
    
    print("Uneven Depth Organization Hierarchy:")
    uneven_org.print_hierarchy()
    print()
    
    # Test cases with varying depths
    uneven_test_cases = [
        (["deep_emp1", "deep_emp2"], "Same deep team (depth 5)"),
        (["deep_emp1", "mid_deep_emp1"], "Deep vs mid-deep (depths 5 & 4) → Auth Service"),
        (["deep_emp1", "medium_emp1"], "Deep vs medium (depths 5 & 3) → Backend Services"), 
        (["deep_emp1", "shallow_backend_emp1"], "Deep vs shallow backend (depths 5 & 2) → Backend Engineering"),
        (["deep_emp1", "shallow_frontend_emp1"], "Deep backend vs shallow frontend (depths 5 & 2) → Engineering"),
        (["deep_emp1", "very_shallow_emp1"], "Very deep vs very shallow (depths 5 & 1) → Engineering"),
        (["medium_emp1", "shallow_frontend_emp1", "very_shallow_emp1"], "Multi-depth: 3, 2, 1 → Engineering"),
    ]
    
    print("UNEVEN DEPTH TEST RESULTS:")
    print("-" * 60)
    
    for employee_ids, description in uneven_test_cases:
        try:
            common_group = uneven_org.find_closest_common_group(employee_ids)
            print(f"Employees: {employee_ids}")
            print(f"Context: {description}")
            print(f"Closest Common Group: {common_group.name} ({common_group.group_id})")
            
            # Show the reasoning with path lengths
            print("Employee locations & path lengths:")
            for emp_id in employee_ids:
                emp_group = uneven_org.employee_to_group[emp_id]
                path = uneven_org.get_path_to_root(emp_group)
                path_names = " -> ".join([g.name for g in reversed(path)])
                print(f"  {emp_id}: {path_names} (depth: {len(path)})")
            
            print("-" * 60)
        
        except Exception as e:
            print(f"Error for {employee_ids}: {e}")
            print("-" * 60)


if __name__ == "__main__":
    demonstrate_part_a()
