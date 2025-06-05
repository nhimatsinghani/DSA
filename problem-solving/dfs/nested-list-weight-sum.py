from typing import List, Union


class NestedInteger:
    """
    This is the interface that allows for creating nested lists.
    You should not implement it, or speculate about its implementation
    """
    
    def __init__(self, value=None):
        """
        If value is not specified, initializes an empty list.
        Otherwise initializes a single integer equal to value.
        """
        if value is None:
            self._list = []
            self._integer = None
        else:
            self._integer = value
            self._list = None
    
    def isInteger(self) -> bool:
        """
        @return True if this NestedInteger holds a single integer, rather than a nested list.
        """
        return self._integer is not None
    
    def add(self, elem):
        """
        Set this NestedInteger to hold a nested list and adds a nested integer elem to it.
        """
        if self._list is None:
            self._list = []
            self._integer = None
        self._list.append(elem)
    
    def setInteger(self, value: int):
        """
        Set this NestedInteger to hold a single integer equal to value.
        """
        self._integer = value
        self._list = None
    
    def getInteger(self) -> int:
        """
        @return the single integer that this NestedInteger holds, if it holds a single integer
        Return None if this NestedInteger holds a nested list
        """
        return self._integer
    
    def getList(self) -> List['NestedInteger']:
        """
        @return the nested list that this NestedInteger holds, if it holds a nested list
        Return None if this NestedInteger holds a single integer
        """
        return self._list


class Solution:
    def depthSum(self, nestedList: List[NestedInteger]) -> int:
        """
        Given a nested list of integers, return the sum of all integers in the list weighted by their depth.
        Each element is either an integer, or a list -- whose elements may also be integers or other lists.
        
        The depth of an integer is the number of lists that it is inside of.
        For example, the nested list [1,[2,2],[[3],2],1] has each integer's value set to its depth.
        
        Args:
            nestedList: List[NestedInteger] - The nested list of integers
            
        Returns:
            int - The sum of each integer multiplied by its depth
        """
        
        result = 0
        for item in nestedList:
            result+=self.getSum(item, 1)

        return result

    def getSum(self, item:NestedInteger, layer:int) -> int:
        if item.getInteger(): 
            return layer * item.getInteger()

        result = 0
        for ele in item.getList():
            result += self.getSum(ele, layer+1)

        return result
    


def build_nested_list_from_array(arr: List[Union[int, List]]) -> List[NestedInteger]:
    """Helper function to build NestedInteger list from array representation."""
    result = []
    
    for item in arr:
        if isinstance(item, int):
            result.append(NestedInteger(item))
        elif isinstance(item, list):
            nested = NestedInteger()
            for sub_item in build_nested_list_from_array(item):
                nested.add(sub_item)
            result.append(nested)
    
    return result


def nested_list_to_string(nested_list: List[NestedInteger]) -> str:
    """Helper function to convert NestedInteger list back to string representation."""
    def nested_to_array(nested: NestedInteger):
        if nested.isInteger():
            return nested.getInteger()
        else:
            return [nested_to_array(item) for item in nested.getList()]
    
    return str([nested_to_array(item) for item in nested_list])


def test_nested_list_weight_sum():
    """Test cases for nested list weight sum."""
    solution = Solution()
    
    # Test Case 1: [[1,1],2,[1,1]]
    print("Test Case 1:")
    nested_list1 = build_nested_list_from_array([[1, 1], 2, [1, 1]])
    result1 = solution.depthSum(nested_list1)
    expected1 = 10  # (1*2 + 1*2) + (2*1) + (1*2 + 1*2) = 4 + 2 + 4 = 10
    print(f"Input: [[1,1],2,[1,1]]")
    print(f"Expected: {expected1}")
    print(f"Got:      {result1}")
    print(f"Explanation: (1*2 + 1*2) + (2*1) + (1*2 + 1*2) = 4 + 2 + 4 = 10")
    print(f"Passed:   {result1 == expected1}")
    print()
    
    # Test Case 2: [1,[4,[6]]]
    print("Test Case 2:")
    nested_list2 = build_nested_list_from_array([1, [4, [6]]])
    result2 = solution.depthSum(nested_list2)
    expected2 = 27  # 1*1 + 4*2 + 6*3 = 1 + 8 + 18 = 27
    print(f"Input: [1,[4,[6]]]")
    print(f"Expected: {expected2}")
    print(f"Got:      {result2}")
    print(f"Explanation: 1*1 + 4*2 + 6*3 = 1 + 8 + 18 = 27")
    print(f"Passed:   {result2 == expected2}")
    print()
    
    # Test Case 3: Empty list
    print("Test Case 3:")
    nested_list3 = build_nested_list_from_array([])
    result3 = solution.depthSum(nested_list3)
    expected3 = 0
    print(f"Input: []")
    print(f"Expected: {expected3}")
    print(f"Got:      {result3}")
    print(f"Passed:   {result3 == expected3}")
    print()
    
    # Test Case 4: Single integer
    print("Test Case 4:")
    nested_list4 = build_nested_list_from_array([5])
    result4 = solution.depthSum(nested_list4)
    expected4 = 5  # 5*1 = 5
    print(f"Input: [5]")
    print(f"Expected: {expected4}")
    print(f"Got:      {result4}")
    print(f"Explanation: 5*1 = 5")
    print(f"Passed:   {result4 == expected4}")
    print()
    
    # Test Case 5: Deeply nested
    print("Test Case 5:")
    nested_list5 = build_nested_list_from_array([1, [2, [3, [4]]]])
    result5 = solution.depthSum(nested_list5)
    expected5 = 30  # 1*1 + 2*2 + 3*3 + 4*4 = 1 + 4 + 9 + 16 = 30
    print(f"Input: [1,[2,[3,[4]]]]")
    print(f"Expected: {expected5}")
    print(f"Got:      {result5}")
    print(f"Explanation: 1*1 + 2*2 + 3*3 + 4*4 = 1 + 4 + 9 + 16 = 30")
    print(f"Passed:   {result5 == expected5}")
    print()
    
    # Test Case 6: Multiple nested lists at same level
    print("Test Case 6:")
    nested_list6 = build_nested_list_from_array([[1, 2], [3, 4]])
    result6 = solution.depthSum(nested_list6)
    expected6 = 20  # (1*2 + 2*2) + (3*2 + 4*2) = 6 + 14 = 20
    print(f"Input: [[1,2],[3,4]]")
    print(f"Expected: {expected6}")
    print(f"Got:      {result6}")
    print(f"Explanation: (1*2 + 2*2) + (3*2 + 4*2) = 6 + 14 = 20")
    print(f"Passed:   {result6 == expected6}")
    print()


if __name__ == "__main__":
    print("Nested List Weight Sum Test Cases")
    print("=" * 40)
    test_nested_list_weight_sum()
    
    print("\nProblem Understanding:")
    print("- Each integer's contribution = value * depth")
    print("- Depth starts at 1 for outermost level")
    print("- Depth increases by 1 for each nested level")
    print("- Sum all contributions")
    print("\nExample breakdown for [1,[4,[6]]]:")
    print("- 1 is at depth 1 → contribution: 1 * 1 = 1")
    print("- 4 is at depth 2 → contribution: 4 * 2 = 8") 
    print("- 6 is at depth 3 → contribution: 6 * 3 = 18")
    print("- Total: 1 + 8 + 18 = 27")
