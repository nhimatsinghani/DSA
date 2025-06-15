from typing import List
from collections import deque
#monotonically decreasing queue


def get_sliding_window_max(input : List[int], k : int ) -> List[int]:

    result = []

    q = deque()

    l,r = 0,0

    while r <len(input):

        #keep popping from q if last element is smaller than incoming ele
        while len(q) > 0  and q[-1] < input[r]: #makes sure q is decreasing order so that max is first element
            q.pop()

        
        q.append(r)

        if len(q) > 0 and l > q[0]:
            q.popleft()
        
        if r + 1 >= k:
            result.append(input[q[0]])
            l+=1

        r+=1

    return result



def test_sliding_window_max():
    
    input = [1,3,-1,-3,5,3,6,7]
    k = 3
    result = get_sliding_window_max(input, k)
    print("result : ",  result)
    assert result == [3,3,5,5,6,7]




if __name__ == "__main__":
    test_sliding_window_max()