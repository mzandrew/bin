#!/usr/bin/python
# written 2015-09-24 by mza

# open invoice pdf file in foxit reader, then save as a txt file

#filename = "2013-12-23.mcmcaster-carr.Receipt 68987523.txt"
filename = "2013-11-19,22,27.mcmaster-carr.txt"

import re # search

lines = []
for line in open(filename):
	line = line.rstrip("\n\r")
	lines.append(line)

in_the_middle_of_processing_a_line_item = 0
for line in lines:
	matches = 0
	#print line
	match = re.search("^[ ]*([0-9]+)[ ]{4,7}([0-9A-Z]+)[ ]{4,7}([., 0-9A-Za-z\"\/-]+)[ ]{4,27}([.0-9]+)[ ]{4,27}([.0-9]+)[ ]{4,27}([.0-9]+)[ ]{4,27}([.0-9]+)[ ]{4,27}([.0-9]+)[ ]*$", line)
	if match:
		matches = matches + 1
		in_the_middle_of_processing_a_line_item = 1
		line_item_number = match.group(1)
		part_number      = match.group(2)
		description      = match.group(3)
		order_quantity   = match.group(4)
		shipped_quantity = match.group(5)
		backordered_quantity = match.group(6)
		unit_price           = match.group(7)
		total_price          = match.group(8)
#		print "[" + string + "]"
#		match = 1
#		description = string
#		while match:
#			match = re.search("^[ ]*(([,0-9A-Za-z\"\/-]+[ ])+)[ ]+(.*)", string)
#			if match:
#				string = match.group(2)
#				print string
#				#description = description + " " + match.group(1)
#			else:
#				description = string
		#print
		#print "[" + description + "]"
		description = re.sub("[ ]{2,}", "", description)
		#print "[" + description + "]"
		#match = re.search("(([,0-9A-Za-z\"\/-]+)[ ])[ ]{4,27}$", description)
		#if match:
		#print "[" + line_item + "] [" + part_number + "] [" + description + "] [" + order_quantity + "] [" + shipped_quantity + "] [" + backordered_quantity + "] [" + unit_price + "] [" + total_price + "]"
	match = re.search("^[ ]*([., 0-9A-Za-z\"\/-]+)[ ]{4,27}(Each|Pack)[ ]{4,47}(Each|Per Pack)[ ]*$", line)
	if match and in_the_middle_of_processing_a_line_item:
		matches = matches + 1
		description = description + " " + match.group(1)
		#string = match.group(1)
		#match = re.search("^(([,0-9A-Za-z\"\/-]+[ ])+)[ ]{2,27}", string)
		#if match:
		#	print "[" + description + "]"
		#match = re.search("(([,0-9A-Za-z\"\/-]+[ ])+)[ ]*(([,0-9A-Za-z\"\/-]+[ ])+)[ ]*", description)
		#match = re.search("(([,0-9A-Za-z\"\/-]+[ ])+)[ ]{2,27}", description)
		#if match:
		#	description = match.group(1)
		#	print "[" + description + "]"
	match = re.search("^$", line)
	if match:
		if (in_the_middle_of_processing_a_line_item >= 1):
			description = re.sub("[ ]{2,}", "", description)
			#print "[" + description + "]"
			print line_item_number + "\t" + order_quantity + "\t" + description + "\t" + part_number + "\tE\t" + unit_price + "\t" + total_price
		matches = matches + 1
		in_the_middle_of_processing_a_line_item = 0
#	if (matches < 1):
#		print "did not process: " + line

