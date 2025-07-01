

from typing import List

class Solution:
    def searchRange(self, nums: List[int], target: int) -> List[int]:
        

        #binary search

        start_index = -1
        end_index = -1

        if len(nums) == 0 : 
            return [-1,-1]


        
        l,r = 0, len(nums)-1
        val_index = -1
        while l <= r: 
            m = l + (r-l)//2

            if nums[m] < target:
                l = m+1
            elif nums[m] > target : 
                r = m-1
            else : 
                val_index = m
                break
        
        if val_index == -1:
            return [-1,-1]

        print("Val index : ", val_index)
        
        l,r = 0, val_index
        while l<=r :
            m = l + (r-l)//2

            if nums[m] != target : 
                l = m+1
            else :
                start_index = m
                r = m-1
        
        
        l,r = val_index, len(nums)-1
        while l<=r :
            m = l + (r-l)//2

            if nums[m] != target : 
                r = m-1
            else:
                end_index = m
                l = m+1

        print("Start index : ", start_index, "... End Index : ", end_index)
        return [start_index, end_index]


def test():
    sol = Solution()

    input = [5,7,7,8,8]
    target=8
    res = sol.searchRange(input, target)
    print("Expected : [3,4], Actual : ", res)
    assert res == [3,4]

    input = [5,7,7,8,8,8,8,8,10, 15,23]
    target=8
    res = sol.searchRange(input, target)
    print("Expected : [3,7], Actual : ", res)
    assert res == [3,7]

    input = [5,7,7,8,8,8,8,8,10, 15,23]
    target=9
    res = sol.searchRange(input, target)
    print("Expected : [-1, -1], Actual : ", res)
    assert res == [-1, -1]



if __name__== "__main__":
    test()