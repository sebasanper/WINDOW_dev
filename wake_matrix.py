with open("jensen_mat.dat", "w") as out:
	with open("jensen.dat", "r") as inp:
		i = 0
		for line in inp:
			cols = line.split()
			i += 1
			out.write("{} ".format(float(cols[2])))
			if i % 240 == 0:
				out.write("\n")
