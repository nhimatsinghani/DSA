

def get_minimum_window_substring(s,t) -> str:
    
    countT = {}
    window = {}

    for char in t:
        countT[char] = 1 + countT.get(char, 0)
    
    resL, resR = -1, -1
    resLen = 10000000000


    ###sliding window logic
    have, need = 0, len(countT)
    l = 0
    for i, char in enumerate(s):
        
        window[char] = 1 + window.get(char, 0)

        if char in t and window[char] == countT[char]:
            have+=1
        
        while have == need : 
            if i-l+1 <resLen:
                resR = i
                resL = l
                resLen = i-l+1

            window[s[l]] -=1
            if s[l] in t and window[s[l]] < countT[s[l]]:
                have -=1

            l+=1


    return s[resL:resR+1] if resL != -1 else ""



def test_minimum_window_substring():

    s = "ADOBECODEBANC"
    t = "ABC"

    result = get_minimum_window_substring(s,t)
    print("Expected : BANC, Actual : " + result)
    assert result == "BANC"

    s = "ADOBECODEBANCX"
    t = "ABCDX"
    result = get_minimum_window_substring(s,t)
    print("Expected : DEBANCX, Actual : " + result)

    assert result == "DEBANCX"



if __name__ == "__main__":
    test_minimum_window_substring()