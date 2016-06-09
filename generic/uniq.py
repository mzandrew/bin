#!/usr/bin/env python
# started 2016-02-29 by mza

lines = []
for line in open("/dev/stdin"):
	line = line.rstrip("\n\r")
	lines.append(line)

unique = []

import re
for new in lines:
	#print "[new]" + new
	matched = 0
	for old in unique:
		#print "[old]" + old
		match = re.search("^" + old + "$", new)
		if match:
			matched = 1
			#print "matched " + old + " " + new
	if not matched:
		unique.append(new)

for old in unique:
	print old

