

from typing import List
from collections import defaultdict
class Solution : 
    def merge_accounts(self, accounts : List[List[str]]):
        # 1 -> John
        # 2 -> John
        # 3 -> Mary
        # 4 -> John
        #john@email.com -> ["John"]
        
        id_to_name_map = {}


        email_to_id_map = defaultdict(list)
        counter=1
        for account in accounts : 
            name = account[0]
            id_to_name_map[counter] = name

            for email in account[1:]:
                email_to_id_map[email].append(counter)

            counter+=1

        # print("Id to Name map : ", id_to_name_map)
        # print("Email to id map : ", email_to_id_map)

        total_accounts = counter-1

        ##union find begins
        parent = [i for i in range(total_accounts+1)] #1-indexed accounts

        rank = [1] * (total_accounts+1)
        
        def find(n) : 
            while parent[n] != n:
                parent[n] = parent[parent[n]] # path compression
                n = parent[n]

            return n
        
        def union(n1,n2):

            parent1, parent2 = find(n1), find(n2)

            if parent1 == parent2:
                return


            if rank[parent1] > rank[parent2]:
                parent[parent2] = parent1
                rank[parent1] += rank[parent2]
            else:
                parent[parent1] = parent2
                rank[parent2] += rank[parent1]

            
            return

        id_to_emails_map = defaultdict(list)

        for email, ids in email_to_id_map.items():
            first = ids[0]
            for other_id in ids[1:]:
                union(first, other_id)
        
        for email, ids in email_to_id_map.items():
            owner_id = find(ids[0])

            id_to_emails_map[owner_id].append(email)

        # print("Id to emails map : ", id_to_emails_map)
        result = []
        for id, emails in id_to_emails_map.items():
            details = []
            details.append(id_to_name_map[id])
            for email in sorted(emails):
                details.append(email)

            result.append(details)


        print("Final Merged Details  : ", result )
        return result




def test():
    sol = Solution()



    accounts = [
        ["John", "john@email.com", "johns@email.com"],
        ["John", "johns@email.com", "johncena@email.com"],
        ["Mary", "mary@email.com"],
        ["John", "jhonny@mail.com"]
    ]
    merged_accounts = sol.merge_accounts(accounts)

    assert len(merged_accounts) == 3


    accounts = [
        ["John", "john@email.com", "johns@email.com"],
        ["John", "johns@email.com", "johncena@email.com"],
        ["John", "mary@email.com"],
        ["John", "jhonny@mail.com", "johns@email.com"]
    ]
    merged_accounts = sol.merge_accounts(accounts)

    assert len(merged_accounts) == 2


if __name__== "__main__":
    test()