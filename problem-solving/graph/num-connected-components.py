from typing import List

class Solution:
    def get_num_connected_components(self, edges: List[List[int]], n:int) -> int:
        parent = [i for i in range(n)]

        rank = [1] * n

        def find(n)->int:
            
            while n != parent[n]:
                parent[n] = parent[parent[n]]
                n = parent[n]

            return n
        
        def union(n1, n2):
            
            parent1, parent2 = find(n1), find(n2)

            if parent1 == parent2 : 
                return
            
            if rank[parent1] > rank[parent2]:
                parent[parent2] = parent1
                rank[parent1] += rank[parent2]

            else : 
                parent[parent1] = parent2
                rank[parent2] += rank[parent1]

        for edge in edges : 
            union(edge[0], edge[1])

        for i in range(n):
            find(i)
        
        print("Parents : ", parent)
        print("Ranks : ", rank)

        return len(set(parent))


def test_get_num_connected_components():

    sol = Solution()


    n = 5
    edges = [[0,1], [1,2], [3,4]]

    res = sol.get_num_connected_components(edges, n)
    print("Expected : 2, Actual : ", res)
    assert res == 2


    n = 5
    edges = [[0,1], [1,2], [3,4], [2,3]]
    res = sol.get_num_connected_components(edges, n)
    print("Expected : 1, Actual : ", res)
    assert res == 1

    n = 5
    edges = [[0,1], [1,2], [3,4], [2,4]]
    res = sol.get_num_connected_components(edges, n)
    print("Expected : 1, Actual : ", res)
    assert res == 1


    n = 7
    edges = [[0,1], [1,2], [3,4], [2,4], [5,6]]
    res = sol.get_num_connected_components(edges, n)
    print("Expected : 1, Actual : ", res)
    assert res == 2




if __name__=="__main__":
    test_get_num_connected_components()