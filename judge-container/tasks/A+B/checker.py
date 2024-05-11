import sys

try:
	f1 = sys.argv[1]
	f2 = sys.argv[2]
	
	

	f1 = open(sys.argv[1], "r").read()
	f2 = open(sys.argv[2], "r").read()

	if float(f2) == sum(map(float, f1.split())):
		print(True)
	else:
		print(False)
except Exception as e:
	print(False)
