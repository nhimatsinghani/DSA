Find the maximum number of riders that can share a single vehicle.

You're given an array of ride requests where each request contains [pickup_time, dropoff_time]. A rider can only share the vehicle if their trip doesn't overlap with others already in the vehicle.

Write a function maxPoolMatches(requests) that returns the maximum number of riders one driver can serve.

Example:

requests = [[1,3], [2,5], [4,7], [8,10]]

Output: 3

// Driver can take [1,3], [4,7], [8,10]

They tried the greedy approach (sort by end time, pick non overlapping) but the interviewer wanted more optimization.

Follow up question they got: What if drivers get paid more for longer rides? How would you maximize earnings instead of ride count?
