import sys

try:
	f1 = int(open(sys.argv[1], "r").read())
	f2 = int(open(sys.argv[2], "r").read())
	incr = 1 if f1 > 0 else -1
	if sum([i for i in range(1, f1 + incr, incr)]) == f2:
		print(True)
	else:
		print(False)
except Exception as e:
	print(False)
