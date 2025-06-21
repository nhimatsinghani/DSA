



def get_max_consecutive_ones_with_k_flips(input, k)-> int:


    result = -1


    windowZeroes = 0
    windowL = 0
    for i, char in enumerate(input):
        if char == "0":
            windowZeroes+=1

        
        while windowZeroes > k : 
            if input[windowL] == "0":
                windowZeroes -=1

            windowL+=1
        
        result = max(i-windowL+1, result)
    

    return result


def test_max_consecutive_ones_with_k_flips():
    k = 2
    input = "11100011110"
    res = get_max_consecutive_ones_with_k_flips(input, k)
    print("Expected : 6 , Actual : " + str(res))
    assert res == 6

    k = 2
    input = "1110001111001111"
    res = get_max_consecutive_ones_with_k_flips(input, k)
    print("Expected : 10 , Actual : " + str(res))
    assert res == 10


    k = 0
    input = "11100011110"
    res = get_max_consecutive_ones_with_k_flips(input, k)
    print("Expected : 4 , Actual : " + str(res))
    assert res == 4


if __name__=="__main__":
    test_max_consecutive_ones_with_k_flips()