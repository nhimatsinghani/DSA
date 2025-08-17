# Description
# Design the basic function of Excel and implement the function of the sum formula.

# Implement the Excel class:

# Excel(int height, char width) Initializes the object with the height and the width of the sheet. The sheet is an integer matrix mat of size height x width with the row index in the range [1, height] and the column index in the range ['A', width]. All the values should be zero initially.
# void set(int row, char column, int val) Changes the value at mat[row][column] to be val.
# int get(int row, char column) Returns the value at mat[row][column].
# int sum(int row, char column, List<String> numbers) Sets the value at mat[row][column] to be the sum of cells represented by numbers and returns the value at mat[row][column]. This sum formula should exist until this cell is overlapped by another value or another sum formula. numbers[i] could be on the format:
# "ColRow" that represents a single cell.
# For example, "F7" represents the cell mat[7]['F'].
# "ColRow1:ColRow2" that represents a range of cells. The range will always be a rectangle where "ColRow1" represent the position of the top-left cell, and "ColRow2" represents the position of the bottom-right cell.
# For example, "B3:F7" represents the cells mat[i][j] for 3 <= i <= 7 and 'B' <= j <= 'F'.
# Note: You could assume that there will not be any circular sum reference.

# For example, mat[1]['A'] == sum(1, "B") and mat[1]['B'] == sum(1, "A").
 

# Example 1:

# Input
# ["Excel", "set", "sum", "set", "get"]
# [[3, "C"], [1, "A", 2], [3, "C", ["A1", "A1:B2"]], [2, "B", 2], [3, "C"]]
# Output
# [null, null, 4, null, 6]

# Explanation
# Excel excel = new Excel(3, "C");
#  // construct a 3*3 2D array with all zero.
#  //   A B C
#  // 1 0 0 0
#  // 2 0 0 0
#  // 3 0 0 0
# excel.set(1, "A", 2);
#  // set mat[1]["A"] to be 2.
#  //   A B C
#  // 1 2 0 0
#  // 2 0 0 0
#  // 3 0 0 0
# excel.sum(3, "C", ["A1", "A1:B2"]); // return 4
#  // set mat[3]["C"] to be the sum of value at mat[1]["A"] and the values sum of the rectangle range whose top-left cell is mat[1]["A"] and bottom-right cell is mat[2]["B"].
#  //   A B C
#  // 1 2 0 0
#  // 2 0 0 0
#  // 3 0 0 4
# excel.set(2, "B", 2);
#  // set mat[2]["B"] to be 2. Note mat[3]["C"] should also be changed.
#  //   A B C
#  // 1 2 0 0
#  // 2 0 2 0
#  // 3 0 0 6
# excel.get(3, "C"); // return 6

"""
SOLUTION EXPLANATION:

The key insight is that this is a dependency tracking problem. When a cell has a sum formula,
it depends on other cells, and when those cells change, the sum cell needs to be recalculated.

REFACTORED DESIGN with Cell class:
1. Cell class encapsulates:
   - value: current computed value  
   - formula: list of referenced ranges/cells (None if regular cell)
   - dependents: set of cells that depend on this cell
   - Methods for managing dependencies and formulas

2. Excel class manages:
   - grid: 2D array of Cell objects
   - Parsing utilities for cell references and ranges
   - Coordination of dependency updates

When a cell value changes (via set() or sum()), we:
1. Update the cell value/formula
2. Recalculate all cells that depend on this cell
3. Recursively update their dependents

Time Complexity:
- get(): O(1)
- set(): O(number of dependent cells)
- sum(): O(number of cells in ranges + number of dependent cells)

Space Complexity: O(height * width + number of formula dependencies)
"""

class Cell:
    """
    Represents a single cell in the Excel spreadsheet.
    Encapsulates value, formula, and dependency tracking.
    """
    
    def __init__(self, value=0):
        """
        Initialize a cell with a value.
        
        Args:
            value: Initial value for the cell (default 0)
        """
        self.value = value
        self.formula = None  # List of ranges/cells if this is a formula cell
        self.dependents = set()  # Set of (row, col) tuples that depend on this cell
    
    def is_formula(self):
        """Check if this cell contains a formula."""
        return self.formula is not None
    
    def set_value(self, val):
        """
        Set a regular value for this cell (clears any existing formula).
        
        Args:
            val: New value to set
        """
        self.value = val
        self.formula = None
    
    def set_formula(self, formula_refs, calculated_value):
        """
        Set a formula for this cell.
        
        Args:
            formula_refs: List of cell/range references
            calculated_value: Pre-calculated sum value
        """
        self.formula = formula_refs
        self.value = calculated_value
    
    def add_dependent(self, row, col):
        """
        Add a cell that depends on this cell.
        
        Args:
            row: Row index of dependent cell
            col: Column index of dependent cell
        """
        self.dependents.add((row, col))
    
    def remove_dependent(self, row, col):
        """
        Remove a dependent cell.
        
        Args:
            row: Row index of dependent cell
            col: Column index of dependent cell
        """
        self.dependents.discard((row, col))
    
    def clear_dependents(self):
        """Clear all dependents of this cell."""
        self.dependents.clear()
    
    def get_dependents(self):
        """Get a copy of the dependents set."""
        return self.dependents.copy()
    
    def __str__(self):
        """String representation for debugging."""
        if self.is_formula():
            return f"Cell(value={self.value}, formula={self.formula}, deps={len(self.dependents)})"
        else:
            return f"Cell(value={self.value}, deps={len(self.dependents)})"


class Excel:
    def __init__(self, height: int, width: str):
        """
        Initialize Excel spreadsheet with given dimensions.
        
        Args:
            height: Number of rows (1-indexed)
            width: Last column letter (e.g., 'C' means columns A, B, C)
        """
        self.height = height
        self.width = ord(width) - ord('A') + 1  # Convert 'C' to 3
        
        # Initialize grid with Cell objects
        self.grid = [[Cell() for _ in range(self.width)] for _ in range(height)]
    
    def _parse_cell(self, cell_str):
        """
        Parse cell string like 'A1' to 0-indexed coordinates.
        
        Args:
            cell_str: Cell reference like 'A1', 'B3', etc.
            
        Returns:
            tuple: (row, col) in 0-indexed format
        """
        col = ord(cell_str[0]) - ord('A')
        row = int(cell_str[1:]) - 1
        return (row, col)
    
    def _parse_range(self, range_str):
        """
        Parse range string like 'A1:B2' to list of cell coordinates.
        
        Args:
            range_str: Either single cell 'A1' or range 'A1:B2'
            
        Returns:
            list: List of (row, col) tuples in 0-indexed format
        """
        if ':' not in range_str:
            # Single cell
            return [self._parse_cell(range_str)]
        
        start_cell, end_cell = range_str.split(':')
        start_row, start_col = self._parse_cell(start_cell)
        end_row, end_col = self._parse_cell(end_cell)
        
        cells = []
        for r in range(start_row, end_row + 1):
            for c in range(start_col, end_col + 1):
                cells.append((r, c))
        return cells
    
    def _get_all_referenced_cells(self, numbers):
        """
        Get all unique cells referenced in the numbers list.
        
        Args:
            numbers: List of cell/range references
            
        Returns:
            set: Set of (row, col) tuples that are referenced
        """
        referenced_cells = set()
        for num_str in numbers:
            cells = self._parse_range(num_str)
            referenced_cells.update(cells)
        return referenced_cells
    
    def _calculate_sum(self, numbers):
        """
        Calculate sum of all cells referenced in numbers list.
        Note: A cell can be counted multiple times if referenced multiple times.
        
        Args:
            numbers: List of cell/range references
            
        Returns:
            int: Sum of all referenced cell values
        """
        total = 0
        for num_str in numbers:
            cells = self._parse_range(num_str)
            for r, c in cells:
                total += self.grid[r][c].value
        return total
    
    def _update_dependencies(self, row, col):
        """
        Recursively update all cells that depend on the given cell.
        
        Args:
            row: Row index (0-indexed)
            col: Column index (0-indexed)
        """
        cell : Cell = self.grid[row][col]
        dependents = cell.get_dependents()
        
        # Update all cells that depend on this cell
        for dep_row, dep_col in dependents:
            dependent_cell = self.grid[dep_row][dep_col]
            if dependent_cell.is_formula():
                # Recalculate the formula
                new_value = self._calculate_sum(dependent_cell.formula)
                dependent_cell.value = new_value
                # Recursively update dependents of this cell
                self._update_dependencies(dep_row, dep_col)
    
    def _remove_cell_dependencies(self, row, col):
        """
        Remove this cell from all its current dependencies.
        Used when a cell formula is being replaced.
        
        Args:
            row: Row index (0-indexed)  
            col: Column index (0-indexed)
        """
        cell = self.grid[row][col]
        if cell.is_formula():
            # Get all cells this cell currently depends on
            referenced_cells = self._get_all_referenced_cells(cell.formula)
            
            # Remove this cell from their dependents lists
            for ref_r, ref_c in referenced_cells:
                referenced_cell = self.grid[ref_r][ref_c]
                referenced_cell.remove_dependent(row, col)
    
    def set(self, row: int, column: str, val: int) -> None:
        """
        Set the value of a cell and update all dependent cells.
        
        Args:
            row: Row number (1-indexed)
            column: Column letter
            val: New value to set
        """
        r = row - 1  # Convert to 0-indexed
        c = ord(column) - ord('A')
        
        # Remove any existing formula dependencies for this cell
        self._remove_cell_dependencies(r, c)
        
        # Set the new value (this clears any formula)
        cell = self.grid[r][c]
        cell.set_value(val)
        
        # Update all cells that depend on this cell
        self._update_dependencies(r, c)
    
    def get(self, row: int, column: str) -> int:
        """
        Get the value of a cell.
        
        Args:
            row: Row number (1-indexed)
            column: Column letter
            
        Returns:
            int: Value at the specified cell
        """
        r = row - 1  # Convert to 0-indexed
        c = ord(column) - ord('A')
        return self.grid[r][c].value
    
    def sum(self, row: int, column: str, numbers) -> int:
        """
        Set a cell to contain a sum formula and return the calculated value.
        
        Args:
            row: Row number (1-indexed)
            column: Column letter  
            numbers: List of cell/range references to sum
            
        Returns:
            int: The calculated sum value
        """
        r = row - 1  # Convert to 0-indexed
        c = ord(column) - ord('A')
        
        # Remove any existing formula dependencies for this cell
        self._remove_cell_dependencies(r, c)
        
        # Calculate the sum
        total = self._calculate_sum(numbers)
        
        # Set up new formula
        cell = self.grid[r][c]
        cell.set_formula(numbers, total)
        
        # Add this cell as dependent of all referenced cells
        referenced_cells = self._get_all_referenced_cells(numbers)
        for ref_r, ref_c in referenced_cells:
            referenced_cell = self.grid[ref_r][ref_c]
            referenced_cell.add_dependent(r, c)
        
        # Update any cells that depend on this cell
        self._update_dependencies(r, c)
        
        return total
    
    def debug_print_grid(self):
        """Print the grid state for debugging."""
        print("\nGrid state:")
        print("  A B C")
        for i in range(self.height):
            row_values = [str(self.grid[i][j].value) for j in range(min(3, self.width))]
            print(f"{i+1} {' '.join(row_values)}")
        
        print("\nFormula cells:")
        for i in range(self.height):
            for j in range(self.width):
                cell = self.grid[i][j]
                if cell.is_formula():
                    col_letter = chr(ord('A') + j)
                    print(f"  {col_letter}{i+1}: {cell.formula} = {cell.value}")


# Test with the provided example
def test_excel():
    """Test the Excel implementation with the provided example."""
    print("Testing Excel implementation with Cell class...")
    
    # Create Excel instance
    excel = Excel(3, "C")
    print("Created 3x3 Excel sheet")
    
    # Test set operation
    excel.set(1, "A", 2)
    print(f"Set A1 = 2, A1 = {excel.get(1, 'A')}")
    
    # Test sum operation
    result = excel.sum(3, "C", ["A1", "A1:B2"])
    print(f"Sum C3 = A1 + A1:B2 = {result}")
    print("Note: A1 is counted twice (once as 'A1', once in 'A1:B2')")
    
    # Test dependency update
    excel.set(2, "B", 2)
    print(f"Set B2 = 2, C3 automatically updated to {excel.get(3, 'C')}")
    
    # Verify final result
    final_result = excel.get(3, "C")
    print(f"Final C3 value: {final_result}")
    
    # Debug print
    excel.debug_print_grid()
    
    print("\n=== Advanced Test ===")
    # Test more complex dependencies
    excel.set(1, "B", 3)
    excel.sum(2, "A", ["A1:B1"])  # A2 = A1 + B1 = 2 + 3 = 5
    excel.sum(2, "C", ["A2", "B2"])  # C2 = A2 + B2 = 5 + 2 = 7
    
    print(f"A2 (sum of A1:B1): {excel.get(2, 'A')}")
    print(f"C2 (sum of A2+B2): {excel.get(2, 'C')}")
    print(f"C3 (should be updated): {excel.get(3, 'C')}")
    
    excel.debug_print_grid()

if __name__ == "__main__":
    test_excel()