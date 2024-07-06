import sys

def input():
    return sys.stdin.readline().rstrip()

def print(*a, sep=" ", end="\n"):
    sys.stdout.write(sep.join([str(i) for i in a]) + end)

n = int(input())
a = [tuple(map(int, input().split())) for i in range(n)]
a.sort(key=lambda x: x[1], reverse=True)
for i in a:
    print(*i)
