from collections import defaultdict, deque
from typing import Tuple


def get_alien_dictionary_order(input : list[str])-> str:
    ##prepare the adjacency list

    adj_list : dict = create_adjacency_list(input)

    print("Adjacency List  : ", adj_list)

    ## perform DFS..
    return get_order_util(adj_list)


def get_order_util(adj_list:dict[list]) -> str:


    stack = deque()


    global_visited = set()

    for char in list(adj_list.keys()):

        if char in global_visited:
            continue
        
        visited = set()
        is_cycle = perform_dfs(char, adj_list, stack, visited, global_visited)

        if is_cycle:
            print("Found a circular dependency of characters while processing for character : ", char)
            return ""


    result = []
    while(len(stack) != 0):
        result.append(stack.popleft())
    # result.reverse()
    return "".join(result)


def perform_dfs(char:str, adj_list, stack:deque, visited : set, global_visited: set) -> bool:

    if char in visited:
        return True

    visited.add(char)

    for neighbor in adj_list[char]:

        is_cycle = perform_dfs(neighbor, adj_list, stack, visited, global_visited)

        if is_cycle:
            return True
    
    if char not in global_visited:
        stack.appendleft(char)
    global_visited.add(char)
    visited.remove(char)

    return False

def create_adjacency_list(words : list[str]) -> dict:
    
    result = defaultdict(list)

    prev_word = words[0]

    for word in words[1:]:
        before_char, after_char = get_differing_char(prev_word, word)
        if before_char == None or after_char == None:
            continue
        result[before_char].append(after_char)
        prev_word = word

    
    return result

def get_differing_char(word1:str, word2 : str) -> Tuple[str, str] : 
    for i in range(len(word1)):

        if i+1 > len(word2):
            return None, None

        if word1[i] != word2[i]:
            return word1[i], word2[i]

    
    return None, None



def test_alien_dictionary():
    
    input = ["wrt", "wrf", "er", "ett", "rftt"]
    result = get_alien_dictionary_order(input)
    print("result : ",  result)
    assert result == "wertf"



if __name__ == "__main__":
    test_alien_dictionary()