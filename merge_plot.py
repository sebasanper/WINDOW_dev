from numpy import sqrt

def rss(a, b):
	return 10.0*(1.0-sqrt(((10.0-a)/10.0)**2.0+((10.0-b)/10.0)**2.0))

def maxi(a,b):
	return min(a, b)

def suma(a,b):
	return 10.0*(1.0-((10.0-a)/10.0+(10.0-b)/10.0))

def mult(a,b):
	if a == 10.0 and b < 10.0:
		return b
	elif a < 10.0 and b == 10.0:
		return a
	else:
		return 10.0*(1.0-((10.0-a)/10.0*(10.0-b)/10.0))


with open("jensen.dat", "r") as inp:
	ju = []
	for line in inp:
		cols = line.split()

		ju.append(float(cols[2]))


jen = [[0 for _ in range(240)] for _ in range(1600)]

for x in range(1600-1):
	for y in range(240):
		# if y <= 120:
			jen[x][y] = ju[x*240+y]


jen2 = [[0 for _ in range(240)] for _ in range(1600)]

for x in range(1600-1):
	for y in range(240):
		jen2[x][y] = ju[(x*240+(240-y))]
		# jen2[x][y] = ju[x*240+y]

import copy
jen4 = copy.deepcopy(jen2)

y_disp2 = 120
x_disp = 400

y_disp = 240 - y_disp2

for x in range(1600-1):
	for y in range(240):
		if y + y_disp < 240:
			jen2[x][y] = jen4[x][y+y_disp]
		else:
			jen2[x][y] = 10.0

jen3 = copy.deepcopy(jen2)


for x in range(1600-1):
	for y in range(240):
		if x > x_disp:
			jen2[x][y] = jen3[x-x_disp][y]
		else:
			jen2[x][y] = 10.0

with open("merge_all_jensen.dat", "w") as out:
	for x in range(1600):
		for y in range(240):

				a = jen[x][y]
				b = jen2[x][y]

				m1 = rss(a, b)
				m2 = maxi(a, b)
				m3 = suma(a, b)
				m4 = mult(a, b)
				out.write("{} {} {} {} {} {} {} {}\n".format(x, y, a, b, m1, m2, m3, m4))
