class Solution {
    public List<List<String>> partition(String s) {

        List<List<String>> result=new ArrayList<>();
        List<String> part=new ArrayList<>();

        dfs(s,0,result,part);
        return result;
    }

    private void dfs(String s,int index,List<List<String>> result,List<String> part)
    {
        //base condition
        if(index>=s.length())
        {
            result.add(new ArrayList<>(part));
            return;
        }

        for(int i=index;i<s.length();i++)
        {
            if(isPalindrome(s,index,i))
            {   part.add(s.substring(index,i+1));
                dfs(s,i+1,result,part);
                part.remove(part.size()-1);
            }
        }

    }

    private boolean isPalindrome(String s, int left,int right )
    {
        while(left<right)
        {
            if(s.charAt(left)==s.charAt(right))
            {
                left++;
                right--;
            }
            else
            {
                return false;
            }
        }
        return true;
    }
}