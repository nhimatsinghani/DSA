



class Solution:
    def lengthOfLongestSubstringTwoDistinct(self, s : str)-> int:

        window = {}

        l = 0
        res = -1

        #ccaabbb
        #window  a -> 2, b -> 3
        #l: 2
        #res : 5
        
        for index, char in enumerate(s):
            # if len(window) < 2 or (len(window == 2) and char in window):
            window[char] = 1 + window.get(char, 0)

            while len(window) > 2:
                window[s[l]] -= 1

                if window[s[l]] == 0:
                    del window[s[l]]
                
                l+=1
            
            res = max(res, index-l+1)
        
        return res



def test():
    sol = Solution()

    input = "eceba"
    res = sol.lengthOfLongestSubstringTwoDistinct(input)
    print("Expected : 3, Actual : ", res)
    assert res == 3

    input = "ccaabbb"
    res = sol.lengthOfLongestSubstringTwoDistinct(input)
    print("Expected : 5, Actual : ", res)
    assert res == 5


    input = "ccccaabbb"
    res = sol.lengthOfLongestSubstringTwoDistinct(input)
    print("Expected : 6, Actual : ", res)
    assert res == 6



if __name__ == "__main__":
    test()