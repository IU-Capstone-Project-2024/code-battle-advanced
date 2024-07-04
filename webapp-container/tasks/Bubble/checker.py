import sys

try:
	with open(sys.argv[1]) as f:
		N = int(f.readline())
		data = []
		for i in range(0, N):
			line = f.readline().split(' ')
			data.append((int(line[0]), int(line[1])))
	for i in range(0, len(data)-1):
		for j in range(0, len(data)-1-i):
			if data[j][1] < data[j+1][1]:
				tmp = data[j+1]
				data[j+1] = data[j]
				data[j] = tmp
				ok = False

	with open(sys.argv[2], 'r') as f:
		check = []
		for line in f.readlines():
			tup = line.split(' ')
			check.append((int(tup[0]), int(tup[1])))
		# Checking
		if len(check) != len(data):
			print(False)
			exit(0)
		for i in range(len(check)):
			if check[i] != data[i]:
				print(False)
				exit(0)
		print(True)
except Exception as e:
	print(e)
