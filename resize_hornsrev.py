with open("coordinates.dat", "r") as small:
	with open("horns_rev_5MW_layout.dat", "w") as big:
		for line in small:
			cols = line.split()
			big.write("{} {}\n".format(float(cols[0]) * 63.0 / 40.0 + 423974.0 * (1.0 - 63.0/40.0), float(cols[1]) * 63.0 / 40.0 + 6151447.0 * (1.0 - 63.0/40.0)))
