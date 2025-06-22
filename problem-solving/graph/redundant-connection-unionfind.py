

from typing import List

class Solution : 
    def findRedundantConnection(self, edges:List[List[int]])-> List[int]:
        parent = [i for i in range(len(edges) + 1)]
        rank = [1] * (len(edges)+1)
        


        def find(n)->int: #find the parent of node n

            while parent[n] != n:
                n = parent[n]
            
            return n
        
        def union(n1, n2) -> bool : #return if we were able to do a union or they were already the same

            parent1, parent2 = find(n1), find(n2)

            if parent1 == parent2:
                # This means that they are already part of the same connected component, And this union will create a ccycle. Hence, this is the redundant edge
                return False
            

            if rank[parent1] > rank[parent2]:
                parent[parent2] = parent1
                rank[parent1] += rank[parent2]
            else : 
                parent[parent1] = parent2
                rank[parent2] += rank[parent1]

            return True
        

        for edge in edges:
            if not union(edge[0], edge[1]):
                return edge
            
        return [-1, -1]

def test_find_redundant_connection():
    solution = Solution()


    edges = [[1,2],[1,3],[2,3]]
    result = solution.findRedundantConnection(edges)

    print("Expected : [2,3], Actual : ", result)
    assert result == [2,3]


if __name__ == "__main__":
    test_find_redundant_connection()
