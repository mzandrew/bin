#!/usr/bin/env python
# written 2018-10-10 by mza
# last updated 2018-10-10 by mza

# usage:
# wget https://www.xilinx.com/support/packagefiles/s6packages/6slx9tqg144pkg.txt
# cat 6slx9tqg144pkg.txt | xilinx_csv_converter.py > 6slx9tqg144pkg.csv
# import csv in PADS part editor's "pins" tab

import re

filename = "/dev/stdin"
lines = []
for line in open(filename):
	line = line.rstrip("\n\r")
	lines.append(line)

print "Pin Group,Number,Name,Type,Swap,Seq."
banked_pins = []
for line in lines:
	#match = re.search("^([^,]+),([^,]+),([^,]+),([^,]+)", line)
	match = re.search("^P([0-9]+)[ \t]+([^ ]+)[ \t]+([^ ]+)[ \t]+([^ ]+)", line)
	if match:
		pin = int(match.group(1))
		pinname = "P%03d" % pin
		bank   = match.group(2) + "_"
		if bank == "NA_":
			bank = ""
		bufio2 = match.group(3) + "_"
		if bufio2 == "NA_":
			bufio2 = ""
		#bank = ""
		name   = match.group(4) + "_"
		match = re.search("^(PROGRAM_B|DONE|CMPCS|SUSPEND|VCCO)", name)
		if match:
			name = match.group(1) + "_"
		extra2 = ""
		match = re.search("^IO_L([0-9]+)([PN])_(.+)_$", name)
		if match:
			pair = int(match.group(1))
			pn = match.group(2)
			extra1 = match.group(3)
			name = "%02d%c_" % (pair, pn)
			match = re.search("^([GV][^_]+)_([0-9]+)$", extra1)
			if match:
				extra2 = "_" + match.group(1)
		new_pin_name = name + bank + bufio2 + pinname + extra2
		banked_pins.append([bank, pin, new_pin_name])

#i = 0
		#i = i + 1
		#print "Gate-A" + "," + str(pin) + "," + new_pin_name + "," + "Undefined" + "," + "0" + "," + str(i)
for banked_pin in banked_pins:
	[bank, pin, new_pin_name] = banked_pin
	if bank == "0_":
		print "Gate-A" + "," + str(pin) + "," + new_pin_name + "," + "Undefined" + "," + "0" + "," + ""
	elif bank == "1_":
		print "Gate-B" + "," + str(pin) + "," + new_pin_name + "," + "Undefined" + "," + "0" + "," + ""
	elif bank == "2_":
		print "Gate-C" + "," + str(pin) + "," + new_pin_name + "," + "Undefined" + "," + "0" + "," + ""
	elif bank == "3_":
		print "Gate-D" + "," + str(pin) + "," + new_pin_name + "," + "Undefined" + "," + "0" + "," + ""
	elif bank == "":
		print "Gate-E" + "," + str(pin) + "," + new_pin_name + "," + "Undefined" + "," + "0" + "," + ""
#	else:
#		print "Gate-F" + "," + str(pin) + "," + new_pin_name + "," + "Undefined" + "," + "0" + "," + ""

