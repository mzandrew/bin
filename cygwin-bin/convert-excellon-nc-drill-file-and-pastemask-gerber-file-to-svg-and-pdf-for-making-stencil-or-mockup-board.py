#!/usr/bin/env python
# started 2015-09-08 by mza
# updated 2015-09-28
# updated 2017-11-07
# last updated 2019-12-03

# todo:
# generalize a bunch of hard-coded things (see "fixme" items in code below)
# add another, mirrored layer for the laser cutter
# get it to read altium output drill files
# get it to output gerber files
# get it to read copper layers (this already works, but the files are big/clunky)
# read in border shapes as closed shapes so they can be filled
# set origin to be the middle of the panel/stencil, build at origin and do explicit rotations/translations to final destination

# from http://stackoverflow.com/questions/3144089/expand-python-search-path-to-other-source :
from os.path import dirname
import sys
sys.path.append(dirname(__file__) + "/../lib")

from DebugInfoWarningError import info, debug, debug2, warning, error, set_verbosity
set_verbosity(3)
try:
	import svgwrite # pip install svgwrite
except:
	import pip # python2 -m ensurepip
	pip.main(['install', '--user', 'svgwrite'])
	print "please try running this script again"
	sys.exit(2)
	#import svgwrite # pip install svgwrite
import re # used for search
import math # used for sqrt, ceil, floor
import subprocess # call

# input filenames:
bottom_pastemask_filename = "assembly/bottom-pastemask.GBP"
top_pastemask_filename = "assembly/top-pastemask.GTP"
board_outline_filename = "fab/board-outline.GKO"
#board_outline_filename = "IDL_15_23_A.GM1" # altium board outline gerber
#stencil_filename = "zelflex-stencil.QR_362x480.GBX"
drill_filename = "fab/drill-through.DRL"
#drill_filename = "IDL_15_23_A-Plated.TXT" # altium drill
# output filenames:
base_filename = "stencil"
svg_filename = base_filename + ".svg"
pdf_filename = base_filename + ".pdf"
eps_filename = base_filename + ".eps"
dxf_filename = base_filename + ".dxf"

# parameters of our laser:
#dpi = 1000
dpi = 500
#dpi = 333
#dpi = 250
laser_stroke_width = 25.4/dpi
#info(str(laser_stroke_width))
stroke_length = 2.0 * laser_stroke_width
#stroke_length = 0.2032 # 0.2032 mm = 8 mils; twice the line spacing of the laser in 250 dpi mode

# variable definition:
board_width = 777.7
board_height = 666.6
x_offset = 77.7
y_offset = 66.6

# user input:
distance_between_board_edge_and_rows_of_half_moons = 5.0 + 5.0 # mm
number_of_horizontal_instances = 1
number_of_vertical_instances = 1
fill_protoboard = 0 # this overrides the above if == 1
panel_frame_thickness = 14.92 # mm - overall border thickness
#panel_tab_length = 7.0 # mm
#panel_tab_width = 2.0 # mm
x_gap_between_instances_of_boards = 20.0 # mm
y_gap_between_instances_of_boards = 20.0 # mm
stencil_half_moon_location = "EastWest"
#stencil_half_moon_location = "NorthSouth"
number_of_extra_half_moons_per_side = 0

# make sure the laser cut line is not cut off of the pdf:
#x_offset = x_offset - laser_stroke_width/2.0
#y_offset = y_offset - laser_stroke_width/2.0
#panel_width  = panel_width  + laser_stroke_width
#panel_height = panel_height + laser_stroke_width

# properties of our stenciling system:
# zelflex-stencil:QR_362x480.GBX:
stencil_hole_grid_pitch = 20.0 # mm
pitch_of_half_moons = 12.0 # mm
height_of_stubs                 = 0.100 # mm (snug fit)
width_of_half_moon              = 3.000 # mm (snug fit)
radius_of_half_moon_arc_segment = width_of_half_moon / 2.0
height_of_half_moon             = radius_of_half_moon_arc_segment + height_of_stubs

vertical_instance = 0
horizontal_instance = 0
id = 0
panel_width = 680.6
panel_height = 680.7

#https://github.com/curtacircuitos/pcb-tools
#import gerber
#from gerber.render import GerberSvgContext
#board_outline = gerber.read(board_outline_filename)
#nc_drill = gerber.read('ncdrill.DRD')
#nc_drill = gerber.read('drill.DRL') # this nc drill parser refuses to read our PADS-generated, excellon-like files, so rolling our own...
#ctx = GerberSvgContext()
#board_outline.render(ctx, "board_outline.svg") # doesn't handle a simple board well, so once again, rolling our own...

def add_layer(parent_object, new_layer_name, new_layer_id_prefix = ""):
	global id
	id = id + 1
	new_layer_object = parent_object.add(svgwrite.container.Group(debug=False))
	parent_object.get_xml()
	new_layer_object['id'] = new_layer_id_prefix + str(id)
	new_layer_object['inkscape:groupmode']='layer'
	new_layer_object['inkscape:label'] = new_layer_name
	return new_layer_object

def add_group(parent_object, new_group_id_prefix = "", color="#000000", stroke_width=laser_stroke_width):
	global id
	id = id + 1
	new_group_object = parent_object.add(svg.g(id=new_group_id_prefix + str(id)))
	new_group_object.stroke(color=color, width=stroke_width, miterlimit=4, opacity=1)
	new_group_object.dasharray("none")
	new_group_object.fill("none")
	return new_group_object

def parse_drill_file(filename):
	info("parsing drill file \"" + filename + "\"...")
	# altium's drill file format specification looks like:
	# ;FILE_FORMAT=4:3
	# METRIC,LZ
	lines = []
	for line in open(filename):
		line = line.rstrip("\n\r")
		lines.append(line)
	global tool
	tool = {}
	for line in lines:
		#debug(line)
		match = re.search("^T[0-9]+C([\.0-9]*)F.*$", line)
		if match:
			diameter = match.group(1)
			tool[diameter] = []
			#debug(diameter)
		match = re.search("^X([0-9]*)Y([0-9]*)$", line)
		if match:
			x = match.group(1)
			y = match.group(2)
			x = +int(x)/1000.0 # fixme
			y = -int(y)/1000.0 # fixme
			location = (x, y)
			tool[diameter].append(location)

def add_hole(drill_centers_group, drill_extents_group, x, y, radius):
	drill_extents_group.add(svg.circle( (x, y), radius, fill="none" ))
	drill_centers_group.add(svg.line( (x-stroke_length/2.0, y), (x+stroke_length/2.0, y) ))

def add_holes_to_panel_frame():
	panel_mounting_holes_layer = add_layer(svg, "panel mounting holes")
	drill_extents_group = add_group(panel_mounting_holes_layer)
	drill_centers_group = add_group(panel_mounting_holes_layer, color="#ff0000")
	radius = 25.4 * 0.150 / 2.0 # hole for a #6-32 machine screw
	# (0,0) here corresponds to the (left,middle) of the panel
	x0 = 0
	y0 = 0
	x1 = x0 + panel_frame_thickness / 2.0
	x2 = x0 + panel_width - panel_frame_thickness / 2.0
	n = int(math.floor(panel_height / stencil_hole_grid_pitch)/2.0)
	for instance in range(-n, n+1):
		y = y0 + instance * stencil_hole_grid_pitch
		add_hole(drill_centers_group, drill_extents_group, x1, y, radius)
		add_hole(drill_centers_group, drill_extents_group, x2, y, radius)
		#info(str(x1-panel_frame_thickness) + "," + str(y+panel_height/2.0) + " " + str(x2-panel_frame_thickness) + "," + str(y+panel_height/2.0))
	panel_mounting_holes_layer.translate(0.0,+panel_height/2.0)

epsilon = 0.001
def generate_drill_layers(which_ones = "all"):
	debug("creating svg from drill file info...")
	layer_name_string = "drill holes"
	layer_name_string = layer_name_string + "(" + str(horizontal_instance) + "," + str(vertical_instance) + ")"
	global drill_layer
	drill_layer = add_layer(board_layer, layer_name_string)
	drill_extents = add_layer(drill_layer, "drill extents")
	drill_centers = add_layer(drill_layer, "drill centers")
	for diameter in tool:
		#info(str(tool[diameter]))
		#info(str(diameter))
		if which_ones == "all":
			do_this_one = "yes"
		else:
			do_this_one = "no"
			for size in which_ones:
				if abs(float(size) - float(diameter)) < epsilon:
					do_this_one = "yes"
		if do_this_one == "yes":
			#info("doing this one")
			drill_centers_layer = add_layer(drill_centers, str(diameter))
			drill_extents_layer = add_layer(drill_extents, str(diameter))
			drill_centers_group = add_group(drill_centers_layer, color="#ff0000")
			drill_extents_group = add_group(drill_extents_layer)
			#debug(diameter + ":")
			for location in tool[diameter]:
				special_diameter = 6.05
				#special_diameter = 7.112
				#special_diameter = 0.062 * 25.4
				#radius = float(diameter) / 2.0
				radius = float(special_diameter) / 2.0
				(x, y) = location
				debug("(" + str(x) + "," + str(y) + ") ",)
				drill_centers_group.add(svg.line( (x-stroke_length/2.0, y), (x+stroke_length/2.0, y) ))
				drill_extents_group.add(svg.circle( (x, y), radius, fill="none" ))
#	special_diameter = 5.0
#	for i in range(1, 5):
#		if i==1:
#			(x, y) = (85.0 - 15.4, -85.0 + 15.4)
#		if i==2:
#			(x, y) = (115.0 + 15.4, -85.0 + 15.4)
#		if i==3:
#			(x, y) = (115.0 + 15.4, -115.0 - 15.4)
#		if i==4:
#			(x, y) = (85.0 - 15.4, -115.0 - 15.4)
#		radius = float(special_diameter) / 2.0
#		drill_centers_group.add(svg.line( (x-stroke_length/2.0, y), (x+stroke_length/2.0, y) ))
#		drill_extents_group.add(svg.circle( (x, y), radius, fill="none" ))
	#drill_layer.translate(-x_offset+horizontal_instance*board_width+horizontal_instance*x_gap_between_instances_of_boards, +y_offset+panel_height-vertical_instance*board_height-vertical_instance*y_gap_between_instances_of_boards)
	drill_layer.translate(-x_offset,+y_offset)
	drill_layer.translate(+horizontal_instance*board_width,+panel_height-vertical_instance*board_height)
	drill_layer.translate(+horizontal_instance*x_gap_between_instances_of_boards,-vertical_instance*y_gap_between_instances_of_boards)

def parse_gerber(filename):
	info("parsing gerber file \"" + filename + "\"...")
	#global layer_width
	#global layer_height
	#layer_width = 0.0
	#layer_height = 0.0
	#global units
	#global zero_suppression_mode
	#global coordinate_mode
	#global layer_polarity
	#global x_format
	#global y_format
	#global number_of_digits
	#global ratio
	global decimal_places # fixme - a bit funny if this changes between gerbers we're reading
	zero_suppression_mode = "leading"
	coordinate_mode = "absolute"
	layer_polarity = "dark"
	x_format = "55"
	y_format = "55"
	#units = "mm"
	lines = []
	for line in open(filename):
		line = line.rstrip("\n\r")
		lines.append(line)
	gerber_instructions = []
	global apertures
	apertures = {}
	aperture = "00"
	matched_units = 0
	matched_format = 0
	set_ratio = 0
	#gerber_instructions.append("hi there")
	for line in lines:
		matches = 0
		match = re.search("^%MO([IM][NM])\*%$", line)
		if match:
			matches = matches + 1
			if (match.group(1) == "IN"):
				#debug("set units to inches: " + line)
				ratio = 1000.0 / 25.4 / 1.55 # fixme/todo: 1.55 is a magic number here
			else:
				#debug("set units to mm: " + line)
				ratio = 1.0
			matched_units = 1
		match = re.search("^%FS([LTD])([AI])X([0-9][0-9])Y([0-9][0-9])\*%$", line)
		if match:
			matches = matches + 1
			debug2("set format: " + line)
			if (match.group(1) == "L"):
				zero_suppression_mode = "leading"
			else:
				zero_suppression_mode = "trailing"
			if (match.group(2) == "A"):
				coordinate_mode = "absolute"
			else:
				coordinate_mode = "incremental"
			x_format = match.group(3)
			y_format = match.group(4)
			decimal_places = int(x_format[1])
			number_of_digits = int(x_format[0]) + int(x_format[1])
			number_of_digits = number_of_digits + 1 # some gerber files output 7 digits for "24" format...
			#decimal_places = decimal_places + 1
			debug("number of digits to use for coordinates = " + str(number_of_digits))
			matched_format = 1
		match = re.search("^%AM(.*)\*$", line) # AM = aperture macro definition
		if match:
			matches = matches + 1
			warning("ignoring aperture macro \"" + match.group(1) + "\"")
		match = re.search("^([$0-9]*),", line) # aperture macro definition continuation
		if match:
			matches = matches + 1
		match = re.search("^%AD(.*)\*$", line) # AD = aperture macro instantiation
		if match:
			matches = matches + 1
			error("aperture instantiation \"" + match.group(1) + "\" ignored - this part needs to be coded")
		match = re.search("^%ADD([0-9]+)C,([.0-9]+)\*%$", line) # %ADD010C,0.0254*%
		if match:
			matches = matches + 1
			#aperture_length = len(match.group(1))
			ap = int(match.group(1))
			apertures[ap] = ("C", float(match.group(2)), float(match.group(2)))
			debug("aperture definition: " + line)
		match = re.search("^%ADD([0-9]+)R,([.0-9]+)X([.0-9]+)\*%$", line) # %ADD028R,2.6X1.6*% or %ADD34R,0.0138X0.0472*% or %ADD368R,0.01969X0.04331*% (means that aperture #368 is a rectangle 0.01969 * 0.04331)
		if match:
			matches = matches + 1
			ap = int(match.group(1))
			apertures[ap] = ("R", float(match.group(2)), float(match.group(3)))
			debug("aperture definition: " + line)
		match = re.search("^%ADD([0-9]+)O,([.0-9]+)X([.0-9]+)\*%$", line) # %ADD11O,0.0138X0.0669*%
		if match:
			matches = matches + 1
			ap = int(match.group(1))
			apertures[ap] = ("O", float(match.group(2)), float(match.group(3)))
			debug("aperture definition: " + line)
		match = re.search("^%LN([a-zA-Z0-9]+)\*%$", line)
		if match:
			matches = matches + 1
			gerber_instructions.append("setlayer" + match.group(1))
		match = re.search("^(G0[1-3])\*$", line)
		if match:
			matches = matches + 1
			gerber_instructions.append(match.group(1))
		match = re.search("^(G0[1-3][XY].*)\*$", line)
		if match:
			matches = matches + 1
			gerber_instructions.append(match.group(1))
		match = re.search("^([XY].*)\*$", line)
		if match:
			matches = matches + 1
			#debug(line)
			gerber_instructions.append(match.group(1))
		#match = re.search("^(G54D)([0-9]+)\*$", line)
		match = re.search("^(G54D)([0-9]+)\*$", line)
		if match:
			matches = matches + 1
			debug2("aperture selection: " + match.group(2))
			gerber_instructions.append(match.group(1) + match.group(2))
			#debug(match.group(1))
		match = re.search("^%LP([DC])\*%$", line)
		if match:
			# this unfortunately only grabs the last instance...
			matches = matches + 1
			if (match.group(1) == "D"):
				layer_polarity = "dark"
			else:
				layer_polarity = "clear"
		match = re.search("^%IPNEG\*%$", line) # %IPNEG% = reverse whole layer
		if match:
			matches = matches + 1
			# do something here for this...
		match = re.search("^%IPPOS\*%$", line) # %IPPOS% = whole layer normal
		if match:
			matches = matches + 1
		match = re.search("^G04.*$", line)
		if match:
			matches = matches + 1
		match = re.search("^%$", line)
		if match:
			matches = matches + 1
		match = re.search("^\*$", line)
		if match:
			matches = matches + 1
		match = re.search("^G74\*$", line)
		if match:
			warning("cannot handle single quadrant G74 mode")
			matches = matches + 1
			#exit()
		match = re.search("^G75\*$", line) # multi-quadrant mode
		if match:
			matches = matches + 1
		match = re.search("^$", line)
		if match:
			matches = matches + 1
		match = re.search("^M02\*$", line) # M02* = end of job
		if match:
			matches = matches + 1
		match = re.search("^%IN(.*)\*%$", line) # IN = image name
		if match:
			matches = matches + 1
			debug2("ignoring image name \"" + match.group(1) + "\"")
		if (matches == 0):
			warning("did not parse \"" + line + "\"")
		if (set_ratio == 0) and (matched_units == 1) and (matched_format == 1):
			ratio = ratio / (10.0**int(decimal_places))
			debug("ratio = " + str(ratio))
			gerber_instructions.append("setratio" + str(ratio))
			set_ratio = 1
	if (matched_format == 0):
		error("did not find format line", 2)
	for aperture in apertures:
		(CROP, w, h) = apertures[aperture]
		debug2("aperture[" + str(aperture) + "]: " + CROP + " " + str(w) + " " + str(h))
	#debug("units: " + units)
	debug("x_format: " + x_format)
	debug("y_format: " + y_format)
	debug("layer_polarity: " + layer_polarity)
	debug("zero_suppression_mode: " + zero_suppression_mode)
	debug("coordinate_mode: " + coordinate_mode)
	return gerber_instructions

def get_extents_of_gerber_instructions(gerber_instructions):
	x_min = 799.1
	y_min = 799.2
	x_max = 799.3
	y_max = 799.4
	x_min_candidate = 799.5
	y_min_candidate = 799.6
	x_max_candidate = 799.7
	y_max_candidate = 799.8
	first_time_through_x = 1
	first_time_through_y = 1
	x_old = 0.0
	y_old = 0.0
	x_string = "0"
	y_string = "0"
	i_string = "0"
	d_string = "02" # pen up
	x = 0.0
	y = 0.0
	i = 0.0
	j = 0.0
	aperture = "00"
	mode = "linear"
	ratio = 5.0
	for instruction in gerber_instructions:
		debug2("instruction: " + instruction)
		match = re.search("^setratio([.0-9]*[e]*[-0-9]*)$", instruction)
		if match:
			ratio = float(match.group(1))
			debug2("found ratio: " + str(ratio))
		match = re.search("^G54D([0-9]+)$", instruction) # "G54D22" means follow the goto X,Y instructions after this line, and flash the D22 aperture every time we get a D03 ("flash aperture") command
		if match:
			debug2("aperture selection: " + match.group(1))
			aperture = int(match.group(1))
			if not aperture in apertures.keys():
				error("can't find aperture #" + str(aperture), 4)
			(CROP, w, h) = apertures[aperture]
			w = 25.4 * w # fixme/todo:  magic number here
			h = 25.4 * h # fixme/todo:  magic number here
			debug2("aperture[" + str(aperture) + "]: " + CROP + " " + str(w) + " " + str(h))
			d_string = "04" # skip doing anything this pass through the following code
		match = re.search("^G(0[0-3])(.*)$", instruction)
		if match:
			instruction = match.group(2)
			#debug2("remaining instruction: " + instruction)
			if (match.group(1) == "01"):
				mode = "linear"
				debug2("mode = linear")
			elif (match.group(1) == "02"):
				mode = "cc_arc"
				debug2("mode = cc arc")
			elif (match.group(1) == "03"):
				mode = "cw_arc"
				debug2("mode = cw arc")
			else:
				error("?", 3)
		match = 1
		while match:
			match = re.search("^([XYIJ])([-0-9]{1,10})(.*)$", instruction)
			if match:
				instruction = match.group(3)
				#debug2("remaining instruction: " + instruction)
				if (match.group(1) == "X"):
					x_string = match.group(2)
					x = +int(x_string) * ratio
					if first_time_through_x:
						x_min = x
						x_max = x
						x_min_candidate = x
						x_max_candidate = x
						first_time_through_x = 0
					if x < x_min_candidate:
						x_min_candidate = x
					if x_max_candidate < x:
						x_max_candidate = x
					#print (x, x_min, x_max)
				elif (match.group(1) == "Y"):
					y_string = match.group(2)
					y = +int(y_string) * ratio
					if first_time_through_y:
						y_min = y
						y_max = y
						y_min_candidate = y
						y_max_candidate = y
						first_time_through_y = 0
					if y < y_min_candidate:
						y_min_candidate = y
					if y_max_candidate < y:
						y_max_candidate = y
					#print (y, y_min, y_max)
				elif (match.group(1) == "I"):
					i_string = match.group(2)
					i = +int(i_string) * ratio
				elif (match.group(1) == "J"):
					j_string = match.group(2)
					j = +int(j_string) * ratio
		match = re.search("^D(0[1-3])$", instruction)
		if match:
			d_string = match.group(1)
		if (d_string == "01"): # pen down
			debug2(" " + x_string + " " + y_string + " " + d_string)
			if (mode == "linear"):
				x_min = x_min_candidate
				y_min = y_min_candidate
				x_max = x_max_candidate
				y_max = y_max_candidate
				debug2("nothing")
				#group.add(svg.line( (x_old,y_old), (x,y) ))
			else:
				radius = math.sqrt(i**2+j**2)
				delta_x = x - x_old
				delta_y = y - y_old
				x_center = x_old + i
				y_center = y_old + j
				debug2("old(" + str(x_old) + "," + str(y_old) + ") -> xy(" + str(x) + "," + str(y) + ") -> ij(" + str(i) + "," + str(j) + ") -> center(" + str(x_center) + "," + str(y_center) + ")")
				if (mode == "cc_arc"):
					string = "M {0},{1} a {2},{2} 0 0,0 {3},{4}".format(x_old, y_old, radius, delta_x, delta_y)
				elif (mode == "cw_arc"):
					string = "M {0},{1} a {2},{2} 0 0,1 {3},{4}".format(x_old, y_old, radius, delta_x, delta_y)
				else:
					error("?", 4)
				debug2(string)
				debug2("nothing")
				#group.add(svg.path(d=string, fill="none"))
		elif (d_string == "02"):
			pass
		elif (d_string == "03"):
			if (aperture == 0):
				warning("unhandled D03 flash operation")
			else:
				t = laser_stroke_width / 2.0
				#x = x / 1.5
				#y = y / 1.5
				debug2("flashing aperture[" + str(aperture) + "]: " + CROP + " " + str(w) + " " + str(h) + " at (" + str(x) + "," + str(y) + ")")
				if (CROP == "R"):
					debug2("nothing")
					#group.add(svg.rect( (x-w/2.0+t,y-h/2.0+t), (w-2*t,h-2*t) ))
		elif (d_string == "04"):
			pass # silently fall thorough, otherwise G54D commands trigger output the first pass through
		else:
			error("unknown d string", 5)
		x_old = x
		y_old = y
	#print (x_min, y_min, x_max, y_max)
	return (x_min, y_min, x_max-x_min, y_max-y_min) # x_offset, y_offset, width, height

def draw_gerber_layer(parent_object, gerber_instructions, layer_name, color = "#000000", stroke_width = laser_stroke_width):
	layer = add_layer(parent_object, layer_name)
	overall_layer = layer
	group = add_group(layer, color=color, stroke_width=stroke_width)
	#group.stroke(color=color, width=float(stroke_width), miterlimit=4, opacity=1)
	#group.dasharray("none")
	#group.fill("none")
	debug2("instructions:")
	x = 0
	y = 0
	x_old = 0
	y_old = 0
	x_string = "0"
	y_string = "0"
	i_string = "0"
	d_string = "02" # pen up
	i = 0
	j = 0
	aperture = "00"
	mode = "linear"
	ratio = 5.0
	for instruction in gerber_instructions:
		debug2("instruction: " + instruction)
		match = re.search("^setratio([.0-9]*[e]*[-0-9]*)$", instruction)
		if match:
			ratio = float(match.group(1))
			debug2("found ratio: " + str(ratio))
		match = re.search("^setlayer(.*)$", instruction)
		if match:
			layer_name = match.group(1)
			layer = add_layer(overall_layer, layer_name)
			group = add_group(layer, color=color, stroke_width=stroke_width)
		match = re.search("^G54D([0-9]+)$", instruction) # "G54D22" means follow the goto X,Y instructions after this line, and flash the D22 aperture every time we get a D03 ("flash aperture") command
		if match:
			debug2("aperture selection: " + match.group(1))
			aperture = int(match.group(1))
			if not aperture in apertures.keys():
				error("can't find aperture #" + str(aperture), 4)
			(CROP, w, h) = apertures[aperture]
			w = 25.4 * w # fixme/todo:  magic number here
			h = 25.4 * h # fixme/todo:  magic number here
			debug2("aperture[" + str(aperture) + "]: " + CROP + " " + str(w) + " " + str(h))
			d_string = "04" # skip doing anything this pass through the following code
		match = re.search("^G(0[0-3])(.*)$", instruction)
		if match:
			instruction = match.group(2)
			#debug2("remaining instruction: " + instruction)
			if (match.group(1) == "01"):
				mode = "linear"
				debug2("mode = linear")
			elif (match.group(1) == "02"):
				mode = "cc_arc"
				debug2("mode = cc arc")
			elif (match.group(1) == "03"):
				mode = "cw_arc"
				debug2("mode = cw arc")
			else:
				error("?", 3)
		match = 1
		while match:
			#match = re.search("^([XYIJ])([-0-9]{1," + str(number_of_digits) + "})(.*)$", instruction)
			match = re.search("^([XYIJ])([-0-9]{1,10})(.*)$", instruction)
			if match:
				instruction = match.group(3)
				#debug2("remaining instruction: " + instruction)
				if (match.group(1) == "X"):
					x_string = match.group(2)
					x = +int(x_string) * ratio
				elif (match.group(1) == "Y"):
					y_string = match.group(2)
					y = +int(y_string) * ratio
				elif (match.group(1) == "I"):
					i_string = match.group(2)
					i = +int(i_string) * ratio
				elif (match.group(1) == "J"):
					j_string = match.group(2)
					j = +int(j_string) * ratio
		match = re.search("^D(0[1-3])$", instruction)
		if match:
			d_string = match.group(1)
		if (d_string == "01"): # pen down
			debug2(" " + x_string + " " + y_string + " " + d_string)
			if (mode == "linear"):
				group.add(svg.line( (x_old,y_old), (x,y) ))
				#debug("(" + str(x_old) + "," + str(y_old) + ") -> (" + str(x) + "," + str(y) + ") with pen down")
			else:
				# PADS: "G03X58250I-3315J-5D01*" or "G03X201969Y117031I0J-1969D01*"
				# altium: "G03*", then "X-1778Y-10160I2540J0D01*"
				radius = math.sqrt(i**2+j**2)
				delta_x = x - x_old
				delta_y = y - y_old
				x_center = x_old + i
				y_center = y_old + j
				debug2("old(" + str(x_old) + "," + str(y_old) + ") -> xy(" + str(x) + "," + str(y) + ") -> ij(" + str(i) + "," + str(j) + ") -> center(" + str(x_center) + "," + str(y_center) + ")")
				#debug("(x,y,i,j) = (" + str(x) + "," + str(y) + "," + str(i) + "," + str(j) + ")")
				if (mode == "cc_arc"):
					#debug("cw arc here")
					# from http://stackoverflow.com/questions/25019441/arc-pie-cut-in-svgwrite
					# dwg.path(d="M {0},{1} l {2},{3} a {4},{4} 0 0,0 {5},{6} z".format(start_x, start_y, m0, n0, radius, m1, n1),
					# M=moveto, L=lineto, a=arc?, z=close path
					# a: (rx ry x-axis-rotation large-arc-flag sweep-flag x y)
					string = "M {0},{1} a {2},{2} 0 0,0 {3},{4}".format(x_old, y_old, radius, delta_x, delta_y)
				elif (mode == "cw_arc"):
					string = "M {0},{1} a {2},{2} 0 0,1 {3},{4}".format(x_old, y_old, radius, delta_x, delta_y)
				else:
					error("?", 4)
				#group.add(svg.circle( (x_center,y_center), radius, fill="none" ))
				#group.add(svg.line( (x_old, y_old), (x, y) ))
				debug2(string)
				group.add(svg.path(d=string, fill="none"))
		elif (d_string == "02"):
			pass
			# maybe change to a new group here?
		elif (d_string == "03"):
			if (aperture == 0):
				warning("unhandled D03 flash operation")
			else:
				t = laser_stroke_width / 2.0
				#x = x / 1.5
				#y = y / 1.5
				debug2("flashing aperture[" + str(aperture) + "]: " + CROP + " " + str(w) + " " + str(h) + " at (" + str(x) + "," + str(y) + ")")
				if (CROP == "R"):
					group.add(svg.rect( (x-w/2.0+t,y-h/2.0+t), (w-2*t,h-2*t) ))
				# should add a special case here for O (oval) and make a rectangle and two half-circles
		elif (d_string == "04"):
			pass # silently fall thorough, otherwise G54D commands trigger output the first pass through
		else:
			error("unknown d string", 5)
		x_old = x
		y_old = y
	return overall_layer

def generate_half_moon(x, y, direction = +1):
	direction = int(direction)
	factor = 10.0**int(decimal_places)
	debug(str(factor))
	if (stencil_half_moon_location == "NorthSouth"):
		eii = +1.0
		eij = +0.0
	else:
		eii = +0.0
		eij = +1.0
	x = x - width_of_half_moon / 2.0
	y = y + height_of_stubs * direction
	gerber_instructions.append("G01X" + str(int(factor*(eii*x+eij*y))) + "Y" + str(int(factor*(eii*y+eij*x))) + "D02")
	y = y - height_of_stubs * direction
	gerber_instructions.append("G01X" + str(int(factor*(eii*x+eij*y))) + "Y" + str(int(factor*(eii*y+eij*x))) + "D01")
	x = x + width_of_half_moon
	gerber_instructions.append("G01X" + str(int(factor*(eii*x+eij*y))) + "Y" + str(int(factor*(eii*y+eij*x))) + "D01")
	y = y + height_of_stubs * direction
	gerber_instructions.append("G01X" + str(int(factor*(eii*x+eij*y))) + "Y" + str(int(factor*(eii*y+eij*x))) + "D01")
	if (direction < 0):
		if (stencil_half_moon_location == "NorthSouth"):
			string = "G02"
		else:
			string = "G03"
	else:
		if (stencil_half_moon_location == "NorthSouth"):
			string = "G03"
		else:
			string = "G02"
	x_new = x - width_of_half_moon
	gerber_instructions.append(string + "X" + str(int(factor*(eii*x_new+eij*y))) + "Y" + str(int(factor*(eii*y+eij*x_new))) + "I" + str(int(-factor*eii*radius_of_half_moon_arc_segment)) + "J" + str(int(-factor*eij*radius_of_half_moon_arc_segment)) + "D01")

def generate_stencil_layer():
	#stencil_half_moon_location = "NorthSouth" or "EastWest"
	if (stencil_half_moon_location == "NorthSouth"):
		pw = panel_width
		ph = panel_height
	else:
		pw = panel_height
		ph = panel_width
	global gerber_instructions
	gerber_instructions = []
	ratio = 1.0 / (10.0**int(decimal_places))
	gerber_instructions.append("setratio" + str(ratio))
	n = int(math.ceil(pw / pitch_of_half_moons))
	n = n + number_of_extra_half_moons_per_side
	n = 2*int(math.ceil(n/2.0)) # ensure it's even to center the stencil on the stencil holder
	stencil_border_extra_width_on_each_side = pitch_of_half_moons - width_of_half_moon - 0.5 # mm
	global stencil_border_extra_height_on_each_side
	stencil_border_extra_height_on_each_side = 3.75 # mm
	global stencil_width
	global stencil_height
	stencil_width = (n - 1) * pitch_of_half_moons + width_of_half_moon + 2.0 * stencil_border_extra_width_on_each_side + laser_stroke_width
	stencil_height = ph + 2.0 * distance_between_board_edge_and_rows_of_half_moons + 2.0 * stencil_border_extra_height_on_each_side + laser_stroke_width
	debug("stencil \"width\" = " + str(stencil_width))
	debug("stencil \"height\" = " + str(stencil_height))
	if (stencil_width > 310.0) or (stencil_height > 370.0):
		warning("stencil will not fit on stencil holder")
	global stencil_border_x
	global stencil_border_y
	stencil_border_x = (pw - stencil_width) / 2.0
	stencil_border_y = (ph - stencil_height) / 2.0
	#gerber_instructions.append("setlayerNorth")
	x = pw / 2.0 - (n-1) * pitch_of_half_moons / 2.0
	y = -distance_between_board_edge_and_rows_of_half_moons 
	for i in range(0, n):
		generate_half_moon(x, y, +1)
		x = x + pitch_of_half_moons
	#gerber_instructions.append("setlayerSouth")
	x = pw / 2.0 - (n-1) * pitch_of_half_moons / 2.0
	y = ph + distance_between_board_edge_and_rows_of_half_moons 
	for i in range(0, n):
		generate_half_moon(x, y, -1)
		x = x + pitch_of_half_moons
	return gerber_instructions

def draw_stencil_layer():
	global stencil_layer
	stencil_layer = draw_gerber_layer(svg, stencil_instructions, "stencil", "#ff0000")
	# border to cut out stencil:
	group = add_group(stencil_layer, color="#ff0000")
	if (stencil_half_moon_location == "NorthSouth"):
		x = stencil_border_x
		y = stencil_border_y
		w = stencil_width
		h = stencil_height
	else:
		x = stencil_border_y
		y = stencil_border_x
		w = stencil_height
		h = stencil_width
	group.add(svg.rect( (x,y), (w,h) ))
	# border for pdf export to laser:
	group = add_group(stencil_layer, color="#ffffff")
	global extra_stencil_border
	extra_stencil_border = 2.0 # mm
	x = x - extra_stencil_border
	y = y - extra_stencil_border
	w = w + 2.0 * extra_stencil_border
	h = h + 2.0 * extra_stencil_border
	group.add(svg.rect( (x,y), (w,h) ))
	global overall_border
	overall_border = {}
	overall_border["minx"] = x
	overall_border["miny"] = y #- stencil_border_extra_height_on_each_side + 1.0
	overall_border["width"] = w
	overall_border["height"] = h #- 2 * stencil_border_extra_height_on_each_side
	#stencil_layer.translate(-x_offset, -y_offset)

def draw_top_pastemask_layer():
	global apertures
	apertures = top_pastemask_apertures
	layer_name_string = "top pastemask"
	layer_name_string = layer_name_string + "(" + str(horizontal_instance) + "," + str(vertical_instance) + ")"
	top_pastemask_layer = draw_gerber_layer(stencil_layer, top_pastemask_instructions, layer_name_string, "#ff0000")
	top_pastemask_layer.scale(1, -1)
	#top_pastemask_layer.translate(-x_offset+horizontal_instance*board_width+horizontal_instance*x_gap_between_instances_of_boards, -y_offset-panel_height+vertical_instance*board_height+vertical_instance*y_gap_between_instances_of_boards)
	top_pastemask_layer.translate(-x_offset,-y_offset-panel_height)
	top_pastemask_layer.translate(+horizontal_instance*board_width,+vertical_instance*board_height)
	top_pastemask_layer.translate(+horizontal_instance*x_gap_between_instances_of_boards,+vertical_instance*y_gap_between_instances_of_boards)

def draw_bottom_pastemask_layer():
	global apertures
	apertures = bottom_pastemask_apertures
	layer_name_string = "bottom pastemask"
	layer_name_string = layer_name_string + "(" + str(horizontal_instance) + "," + str(vertical_instance) + ")"
	bottom_pastemask_layer = draw_gerber_layer(stencil_layer, bottom_pastemask_instructions, layer_name_string, "#ff0000")
	bottom_pastemask_layer.scale(1, -1)
	#bottom_pastemask_layer.translate(-x_offset+horizontal_instance*board_width+horizontal_instance*x_gap_between_instances_of_boards, -y_offset-panel_height+vertical_instance*board_height+vertical_instance*y_gap_between_instances_of_boards)
	bottom_pastemask_layer.translate(-x_offset,-y_offset-panel_height)
	bottom_pastemask_layer.translate(+horizontal_instance*board_width,+vertical_instance*board_height)
	bottom_pastemask_layer.translate(+horizontal_instance*x_gap_between_instances_of_boards,+vertical_instance*y_gap_between_instances_of_boards)

def draw_pastemask_layer():
	try:
		draw_top_pastemask_layer()
	except:
		pass
	try:
		draw_bottom_pastemask_layer()
	except:
		pass

def setup_board_layer():
	global board_layer
	layer_name_string = "board"
	layer_name_string = layer_name_string + "(" + str(horizontal_instance) + "," + str(vertical_instance) + ")"
	board_layer = add_layer(boards_layer, layer_name_string)
	layer_name_string = "board outline"
	layer_name_string = layer_name_string + "(" + str(horizontal_instance) + "," + str(vertical_instance) + ")"

def draw_board_outline_layer():
	#info("drawing board outline gerber layer...")
	global apertures
	apertures = board_outline_apertures
	outline_layer = draw_gerber_layer(board_layer, board_outline_instructions, layer_name_string, "#ff0000")
	#outline_layer.translate(-x_offset, -y_offset)
	outline_layer.scale(1, -1)
	#outline_layer.translate(-x_offset+horizontal_instance*board_width+horizontal_instance*x_gap_between_instances_of_boards, -y_offset-panel_height+vertical_instance*board_height+vertical_instance*y_gap_between_instances_of_boards)
	outline_layer.translate(-x_offset, -y_offset-panel_height)
	outline_layer.translate(+horizontal_instance*board_width,+vertical_instance*board_height)
	outline_layer.translate(+horizontal_instance*x_gap_between_instances_of_boards,+vertical_instance*y_gap_between_instances_of_boards)

def draw_protoboard_outline_layer():
	geex_layer = add_layer(svg, "geex", "geex01")
	geex_group = add_group(geex_layer, "geex02", color="#555555")
	#geex_group.add(svg.rect( (0,board_height-150), (150,150) ))
	#geex_group.add(svg.rect( (0,0), (150,150) ))
	geex_group.add(svg.rect( (laser_stroke_width/2.0,laser_stroke_width/2.0), (protoboard_width-laser_stroke_width,protoboard_height-laser_stroke_width) ))

def save_svg_file():
	info("writing svg file \"" + svg_filename + "\"...")
	if 1==0:
		svg.viewbox(width=panel_width, height=panel_height)
	else:
		#svg.viewbox(width=stencil_width, height=stencil_height)
		#svg.viewbox(minx=stencil_border_x-extra_stencil_border, miny=stencil_border_y-extra_stencil_border, width=stencil_width+2*extra_stencil_border, height=stencil_height+2*extra_stencil_border)
		#svg.viewbox(minx=stencil_border_x-extra_stencil_border/2, miny=stencil_border_y-extra_stencil_border/2, width=stencil_width, height=stencil_height)
		svg.viewbox(minx=overall_border["minx"], miny=overall_border["miny"], width=overall_border["width"], height=overall_border["height"])
	#svg.size(width=str(panel_width) + "mm", height=str(panel_height) + "mm")
	#svg.save()
	# from https://bitbucket.org/mozman/svgwrite/issues/18/adding-namespaces:
	import xml.etree.ElementTree
	xml_content = svg.get_xml()
	xml_content.attrib['xmlns:inkscape']='http://www.inkscape.org/namespaces/inkscape'
	if 1==0:
		xml_content.attrib['width']=str(panel_width) + "mm"
		xml_content.attrib['height']=str(panel_height) + "mm"
	else:
		xml_content.attrib['width']=str(overall_border["width"]) + "mm"
		xml_content.attrib['height']=str(overall_border["height"]) + "mm"
	#xml_content.attrib['units']="mm"
	#xml_content.attrib['inkscape:window-width']="1200"
	#xml_content.attrib['inkscape:window-height']="800"
	##xml_content.attrib['height']=str(panel_height) + "mm"
#	xml_content.attrib['inkscape:document-units']="mm" # this is ignored by inkscape 0.91 r13725
	with open(svg_filename, 'wb') as fd:
		fd.write(xml.etree.ElementTree.tostring(xml_content))

def generate_pdf():
	info("converting svg file to pdf...")
	#/cygdrive/c/Program\ Files/Inkscape/inkscape.exe drill1.svg --export-pdf="blah.pdf"
	#cd /usr/local/bin
	#ln -s /cygdrive/c/Program\ Files/Inkscape/inkscape.exe
	try:
		subprocess.call(["inkscape", svg_filename, "--export-pdf=" + pdf_filename])
	except:
		print "can't run inkscape:"
		print "install apt-cyg - see https://github.com/ilatypov/apt-cyg"
		print "apt-cyg install inkscape"
		print "then please try running this script again"

def generate_eps_and_dxf():
# from https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Other_2D_formats
	info("converting svg file to eps...")
	subprocess.call(["inkscape", svg_filename, "--export-eps=" + eps_filename])
	info("converting eps file to dxf...")
	# pstoedit.exe -f "dxf:-polyaslines -mm" the-bicentennial-board.eps the-bicentennial-board.dxf
	# pstoedit.exe -f dxf:-polyaslines\ -mm the-bicentennial-board.eps the-bicentennial-board.dxf
	subprocess.call(["pstoedit", "-q", "-f", "dxf:-polyaslines -mm", eps_filename, dxf_filename])
	info("in solidworks, open dxf file, choose import as 2d sketch, select mm")

def try_making_a_tiled_object():
	info("trying to make a tiled object")
	tilly = svg.defs.add(svg.g(id='tilly'))
	tilly.add(svg.circle( (0,0), 5, fill="#00ff00" ))
	blah = svg.use(tilly, insert=(10,10))
	svg.add(blah)

parse_drill_file(drill_filename) # stores info in "tool"
board_outline_instructions = parse_gerber(board_outline_filename)
board_outline_apertures = apertures
(x_offset, y_offset, board_width, board_height) = get_extents_of_gerber_instructions(board_outline_instructions)
#info((board_width, board_height))
#info((x_offset, y_offset))
try:
	top_pastemask_instructions = parse_gerber(top_pastemask_filename)
	top_pastemask_apertures = apertures
except:
	warning("can't find top pastemask file")
try:
	bottom_pastemask_instructions = parse_gerber(bottom_pastemask_filename)
	bottom_pastemask_apertures = apertures
except:
	warning("can't find bottom pastemask file")

protoboard_width  = 151 # should measure this width each time so that the mirror-image ends up in the right place
protoboard_height = 151
if (fill_protoboard == 1):
	number_of_horizontal_instances = int(math.floor(protoboard_width  / board_width))
	number_of_vertical_instances   = int(math.floor(protoboard_height / board_height))
	if (number_of_horizontal_instances < 1) or (number_of_vertical_instances < 1):
		error("can't fit board on panel", 6)
	panel_width = number_of_horizontal_instances * board_width
	panel_height = number_of_vertical_instances * board_height
	panel_width  = panel_width  + (number_of_horizontal_instances - 1) * x_gap_between_instances_of_boards 
	panel_height = panel_height + (number_of_horizontal_instances - 1) * y_gap_between_instances_of_boards 
	extra_x_offset = (protoboard_width  - panel_width ) / 2.0
	extra_y_offset = (protoboard_height - panel_height) / 2.0
	panel_width  = protoboard_width
	panel_height = protoboard_height
else:
	#extra_x_offset = x_gap_between_instances_of_boards # or 0.0/whatever
	#extra_y_offset = y_gap_between_instances_of_boards # or 0.0/whatever
	extra_x_offset = panel_frame_thickness # + panel_tab_length
	extra_y_offset = panel_frame_thickness
	panel_width = number_of_horizontal_instances * board_width + 2.0 * extra_x_offset
	panel_height = number_of_vertical_instances * board_height + 2.0 * extra_y_offset
	panel_width  = panel_width  + (number_of_horizontal_instances - 1) * x_gap_between_instances_of_boards 
	panel_height = panel_height + (number_of_vertical_instances   - 1) * y_gap_between_instances_of_boards 
x_offset = x_offset - extra_x_offset
y_offset = y_offset - extra_y_offset
#info((x_offset, y_offset))

#svg = svgwrite.Drawing(svg_filename, profile='tiny')
#svg = svgwrite.Drawing(size=(str(panel_width) + "mm", str(panel_height) + "mm"))
svg = svgwrite.Drawing()
stencil_instructions = generate_stencil_layer()
#stencil_instructions = parse_gerber(stencil_filename)

layer_name_string = "board"
boards_layer = add_layer(svg, layer_name_string)
draw_stencil_layer()
for horizontal_instance in range(0, number_of_horizontal_instances):
	for vertical_instance in range(0, number_of_vertical_instances):
		setup_board_layer()
		#draw_board_outline_layer()
		#generate_drill_layers([6.05]) # 6mm clearance hole
		generate_drill_layers([3.81]) # 6-32 clearance hole
		#generate_drill_layers([0.062*25.4]) # SMA vertical center hole
		draw_pastemask_layer()
if (fill_protoboard == 1):
	draw_protoboard_outline_layer()
info("")
string = "stencil will be "
string += str(int(overall_border["width"]+0.5)/10.0) + " cm x "
string += str(int(overall_border["height"]+0.5)/10.0) + " cm"
string += " and should be printed at " + str(dpi) + " dpi"
info(string)
info("")
#add_holes_to_panel_frame()
save_svg_file()
generate_pdf()
#generate_eps_and_dxf()

#try_making_a_tiled_object()

