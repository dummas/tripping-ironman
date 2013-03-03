def data_to_array ( file_to_read ):
	tmp = []
	for line in file_to_read:
		if len(line.split()) is not 0:
			tmp.append([ float(line.split()[0]), float(line.split()[1]), float(line.split()[2]) ])
			
	return tmp
