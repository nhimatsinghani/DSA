

from typing import List, Tuple
from collections import defaultdict
from heapq import heappop, heapify, heappush
class Solution : 

    def getNetworkDelayTime(self, times : List[List[int]], n:int, k:int)->int:
        
        heap : List[Tuple[int,int]] = []

        source = k

        adj_list = self.create_adj_list(times, n)


        visited = set()
        res = 100000
        ## len(visited) == n

        print("Adj List : ", adj_list)
        #add immediate neighbours of node k
        for neighbor_item in adj_list[k]:
            neighbor = neighbor_item[0]
            weight = neighbor_item[1]

            heappush(heap, (weight, neighbor))
        
        visited.add(k)

        print("Initial Heap state : ", heap)
        while heap:
            
            weight, node = heappop(heap)

            visited.add(node)

            if len(visited) == n:
                res = min(res, weight)

            for neighbor_item in adj_list[node]:

                neighbor = neighbor_item[0]
                weight_neighbor = neighbor_item[1]

                if neighbor in visited:
                    continue
                    
                heappush(heap, (weight+weight_neighbor, neighbor))

            print("Heap state : ", heap)
        
        return res
    
    def create_adj_list(self, times: List[List[int]], n:int) -> dict:
        res = defaultdict(list)
        for edge in times:
            from_node = edge[0]
            to_node = edge[1]
            weight = edge[2]

            res[from_node].append((to_node, weight))

        return res

    






def test_get_network_delay_time():

    solution = Solution()


    times = [[2,1,1], [2,3,1], [3,4,1]]
    n,k = 4,2
    result = solution.getNetworkDelayTime(times, n, k)
    print("Expected : 2, Actual : " + str(result))
    assert result == 2

    times = [[1,2,4], [1,3,1], [3,4,1], [4,2,1]]
    n,k = 4,1
    result = solution.getNetworkDelayTime(times, n, k)
    print("Expected : 3, Actual : " + str(result))

    assert result == 3




if __name__== "__main__":
    test_get_network_delay_time()