1100\. Final Standings
----------------------

Time limit: 1.0 second  
Memory limit: 16 MB  

Old contest software uses bubble sort for generating final standings. But now, there are too many teams and that software works too slow. You are asked to write a program, which generates exactly the same final standings as old software, but fast.

### Input

The first line of input contains only integer 1 < _N_ ≤ 150000 — number of teams. Each of the next _N_ lines contains two integers 1 ≤ _ID_ ≤ 107 and 0 ≤ _M_ ≤ 100. _ID_ — unique number of team, _M_ — number of solved problems.

### Output

Output should contain _N_ lines with two integers _ID_ and _M_ on each. Lines should be sorted by _M_ in descending order as produced by bubble sort (see below).

### Sample

| <div style="width:290px">input</div> | <div style="width:290px">output</div> |
|--------------------------------------|---------------------------------------|
| 8                                    | 3 5                                   |  
| 1 2                                  | 26 4                                  | 
| 16 3                                 | 22 4                                  | 
| 11 2                                 | 16 3                                  | 
| 20 3                                 | 20 3                                  | 
| 3 5                                  | 1 2                                   |  
| 26 4                                 | 11 2                                  | 
| 7 1                                  | 7 1                                   | 
| 22 4                                 |                                       | 

### Notes

Bubble sort works following way:  
`while (exists A[i] and A[i+1] such as A[i] < A[i+1]) do`  
   `Swap(A[i], A[i+1]);`
