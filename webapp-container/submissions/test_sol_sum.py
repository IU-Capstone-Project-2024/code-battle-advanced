n = int(input())

if n <= 0:
  print(1 - (abs(n) + 1) * (abs(n)) // 2)
else:
  print((abs(n) + 1) * (abs(n)) // 2)
