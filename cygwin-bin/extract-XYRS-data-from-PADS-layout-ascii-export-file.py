#!/usr/bin/env python
#!/cygdrive/c/Python27/python.exe
# started 2014-12-09 by mza, based upon "move-components-around-in-PADS-layout-ascii-exported-file.carrier-revE.py"
# modified 2014-12-10 (to export directly to an openoffice spreadsheet)
# modified 2015-10-20 (to match RESISTOR@2010 as a part type)
# modified 2016-01-12 (to grab all components at negative or zero Y-coordinates)
#
# this script works on a mentor graphics PADS layout ASCII export file:
# to export your layout, do file->export, format=PADS layout v9.5
# select all, and check expanded attributes for parts, nets

# ImportError: No module named win32com.client
# run this with:
# /cygdrive/c/Python27/python c:/cygwin/home/mza/bin/extract-XYRS-data-from-PADS-layout-ascii-export-file.py the-bicentennial-board.revA.layout.asc

X_unit = 1500000
Y_unit = X_unit
name_regex = "[@A-Z0-9_+-\\\\]" # \\\\ = one literal '\'

import re, sys, argparse, os.path
parser = argparse.ArgumentParser()
parser.add_argument("filename", help="file name to parse")
args = parser.parse_args()

if os.path.isfile(args.filename):
	print "opening \"" + args.filename + "\"..."
else:
	print "ERROR: couldn't find file \"" + args.filename + "\""
	exit(0)

def read_file(filename):
	global lines
	global mode
	lines = []
	mode = 0
	for line in open(filename):
		line = line.rstrip("\n\r")
		lines.append(line)

component = {}

def get_XYRS_of_components():
	global component
	mode = 0
	count = 0
	for line in lines:
		match = re.search("^\*PART\*", line)
		if match:
			mode = 1
		if (mode>=1):
			#print line
			# example line:
			#DAC             AD5686R 66562500 77812500 270.000 U M 0 -1 0 -1 2
			#R2-             RESISTOR@2010 10500000 36000000 0.000 U M 0 -1 0 -1 2
			#match = re.search("^(" + name_regex + "*)[ ]*[A-Z0-9-_'@]* ([0-9-]+) ([0-9-]+) ([\.0-9\-]+) ([UG]) ([NM]) (.*)", line)
			match_count = 0
			match = re.search("^(" + name_regex + "*)[ ]+[\.A-Z0-9-_'@]+[ ]+([0-9-]+)[ ]+([0-9-]+)[ ]+([\.0-9\-]+)[ ]+([UG])[ ]+([NM])[ ]+(.*)", line)
			if match:
				mode = 2
				count = count + 1
				#print "found reference part " + match.group(1)
				X = float(match.group(2)) / X_unit
				Y = float(match.group(3)) / Y_unit
				R = float(match.group(4))
				S = match.group(6)
				#print "original[" + str(i) + "]: " + X + " " + Y + " " + R
				if (S == "N"):
					S = "TOP"
					match_count = match_count + 1
				elif (S == "M"):
					S = "BOTTOM"
					match_count = match_count + 1
				else:
					print "ERROR:  could not parse line: " + line
				component[match.group(1)] = [X, Y, R, S]
			else:
				match = re.search("(VALUE|Part Type|Regular|Ref.Des.|test_point_setting).*", line)
				if match:
					match_count = match_count + 1
			#if match_count == 0:
			#	print "ERROR:  could not parse line: " + line
#		if (mode>=2):
#			print line
		match = re.search("^Part Type", line)
		if match:
			mode = 1
		match = re.search("^\*ROUTE\*", line)
		if match:
			mode = 0
	print "found " + str(count) + " components"

def write_file(filename):
	new_file = open(filename, "w")
	print "writing to file \"" + filename + "\"..."
	line = "REFDES X(mm) Y(mm) R(deg) S"
	new_file.write(line + "\n")
	for comp in sorted(component.keys()):
		[X, Y, R, S] = component[comp]
		line = comp + " " + str(X) + " " + str(Y) + " " + str(R) + " " + S
		new_file.write(line + "\n")

# this critical snippet is from http://stackoverflow.com/questions/17143510/python-win32com-open-openoffice-calc-xls-spreadsheet-through-task-scheduler:
def PropertyValueArray(num):
	'''Creates an openoffice property value array'''
	l = []
	OOcalcManager._FlagAsMethod("Bridge_GetStruct")
	for x in range(num):
		_p = OOcalcManager.Bridge_GetStruct("com.sun.star.beans.PropertyValue")
		_p.Name = ''
		_p.Value = ''
		l.append(_p)
	return l

def SetupOOCalc():
	global OOcalcDoc, OOcalcManager
	from win32com.client import Dispatch
	print "waiting for OOcalc to open..."
	sys.stdout.flush()
	OOcalcManager = Dispatch("com.sun.star.ServiceManager")
	OOcalcDesktop = OOcalcManager.CreateInstance("com.sun.star.frame.Desktop")
	properties = PropertyValueArray(1)
	properties[0].Name = "Hidden"
	properties[0].Value = True
	OOcalcDoc = OOcalcDesktop.loadComponentFromURL("private:factory/scalc", "_blank", 0, properties)
	global oSheet
	oSheet = OOcalcDoc.getSheets().getByIndex(0)

def SetupHeaders():
	oCell = oSheet.GetCellByPosition(0, 0); oCell.setString("REFDES")
	oCell = oSheet.GetCellByPosition(1, 0); oCell.setString("X(mm)")
	oCell = oSheet.GetCellByPosition(2, 0); oCell.setString("Y(mm)")
	oCell = oSheet.GetCellByPosition(3, 0); oCell.setString("R(deg)")
	oCell = oSheet.GetCellByPosition(4, 0); oCell.setString("S")

def generate_spreadsheet(filename):
	SetupOOCalc()
	SetupHeaders()
	j = 0
	print "filling in spreadsheet with XYRS data..."
	sys.stdout.flush()
	for comp in sorted(component.keys()):
		[X, Y, R, S] = component[comp]
		j = j + 1
		oCell = oSheet.GetCellByPosition(0, j); oCell.setString(comp)
		oCell = oSheet.GetCellByPosition(1, j); oCell.setValue(X)
		oCell = oSheet.GetCellByPosition(2, j); oCell.setValue(Y)
		oCell = oSheet.GetCellByPosition(3, j); oCell.setValue(R)
		oCell = oSheet.GetCellByPosition(4, j); oCell.setString(S)
	oSheet.Columns.OptimalWidth = True
	print "writing to file \"" + filename + "\"..."
	properties = PropertyValueArray(1)
	properties[0].Name = "FilterName"
	properties[0].Value = "MS Excel 97"
	OOcalcDoc.storeToURL("file:///C:" + filename, properties)
	OOcalcDoc.dispose()
#setFormula('=SUM(A1:A2)')
#getValue()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

read_file(args.filename)
get_XYRS_of_components()
write_file(args.filename + ".XYRS")
#generate_spreadsheet(args.filename + ".XYRS.xls")

