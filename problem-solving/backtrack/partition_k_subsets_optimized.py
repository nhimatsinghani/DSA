from typing import List

class Solution:
    def canPartitionKSubsets(self, nums: List[int], k: int) -> bool:
        total = sum(nums)
        
        if total % k != 0:
            return False
        
        target_sum = total // k
        
        # Early exit: if any number is larger than target, impossible
        if any(num > target_sum for num in nums):
            return False
        
        # Sort in descending order for better pruning
        nums.sort(reverse=True)
        
        # Early exit: if largest number equals target, it must go alone
        if nums[0] == target_sum:
            return self.canPartitionKSubsets(nums[1:], k - 1)
        
        subset_sums = [0] * k
        
        def backtrack(i):
            # Base case: all numbers placed
            if i == len(nums):
                return True  # All sums must be target_sum by construction
            
            # OPTIMIZATION 1: Skip equivalent empty subsets
            # If we have multiple empty subsets, only try the first one
            seen_sums = set()
            
            for subset_index in range(k):
                current_sum = subset_sums[subset_index]
                
                # Skip if we've already tried this sum configuration
                if current_sum in seen_sums:
                    continue
                seen_sums.add(current_sum)
                
                # OPTIMIZATION 2: Early exit if number doesn't fit
                if current_sum + nums[i] > target_sum:
                    continue
                
                # OPTIMIZATION 3: Greedy choice for exact fits
                if current_sum + nums[i] == target_sum:
                    subset_sums[subset_index] += nums[i]
                    if backtrack(i + 1):
                        return True
                    subset_sums[subset_index] -= nums[i]
                    # If exact fit doesn't work, no point trying other subsets
                    break
                
                # Regular placement
                subset_sums[subset_index] += nums[i]
                
                if backtrack(i + 1):
                    return True
                
                subset_sums[subset_index] -= nums[i]
                
                # OPTIMIZATION 4: If first subset can't work, others won't either
                # (only applies when current subset is empty)
                if current_sum == 0:
                    break
            
            return False
        
        return backtrack(0)

# Alternative approach: Start from subsets instead of numbers
class SolutionAlternative:
    def canPartitionKSubsets(self, nums: List[int], k: int) -> bool:
        total = sum(nums)
        
        if total % k != 0:
            return False
        
        target = total // k
        nums.sort(reverse=True)
        
        if nums[0] > target:
            return False
        
        used = [False] * len(nums)
        
        def fillSubset(subset_num, current_sum, start_idx):
            if subset_num == k:
                return True
            
            if current_sum == target:
                return fillSubset(subset_num + 1, 0, 0)
            
            for i in range(start_idx, len(nums)):
                if used[i] or current_sum + nums[i] > target:
                    continue
                
                used[i] = True
                if fillSubset(subset_num, current_sum + nums[i], i + 1):
                    return True
                used[i] = False
                
                # If we can't place the first number in this subset,
                # we can't form this subset at all
                if current_sum == 0:
                    break
            
            return False
        
        return fillSubset(0, 0, 0) 