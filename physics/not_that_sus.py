#!/bin/env python3

# written 2024-11-17 by mza
# last updated 2024-11-21 by mza

# ----------------------------------------------------

# user parameters:
grid_spacing = [ 1.0, 1.0, 1.0 ] # potential source locations grid, in meters
#grid_spacing = [ 0.5, 0.5, 0.5 ] # potential source locations grid, in meters
#grid_spacing = [ 0.25, 0.25, 0.25 ] # potential source locations grid, in meters
#grid_spacing = [ 0.125, 0.125, 0.125 ] # potential source locations grid, in meters

# receiver locations:
receiver_location = []
receiver_location.append([ -0.5, +0.5, +0.0 ])
receiver_location.append([ +0.5, +0.5, +0.0 ])
receiver_location.append([ +0.0, -0.5, +0.0 ])

# "constants":
raw_sample_rate = 44100 # Hz
sample_rate_factor = 32
sample_rate = raw_sample_rate // sample_rate_factor # 1378 Hz
raw_bits_per_sample = 18
bits_per_sample_factor = 6
bits_per_sample = raw_bits_per_sample // bits_per_sample_factor # 3 bits per sample

# sane choices:
minimum_delay_in_samples = 0 # we allow the source to be co-located with the receiver
maximum_delay_in_samples = 1000

# ----------------------------------------------------

import math, copy

x_index = 0; y_index = 1; z_index = 2
xyz_range = range(3)
min_index = 0; max_index = 1

# ----------------------------------------------------

def distance(a, b):
	delta_x = b[x_index] - a[x_index]
	delta_y = b[y_index] - a[y_index]
	delta_z = b[z_index] - a[z_index]
	distance = math.sqrt(delta_x**2 + delta_y**2 + delta_z**2)
	return distance

def find_bounding_box_linear(myarray):
	minmin = copy.deepcopy(myarray[0])
	maxmax = copy.deepcopy(myarray[0])
	for index in range(len(myarray)):
		for xyz in xyz_range:
			if myarray[index][xyz]<minmin[xyz]:
				minmin[xyz] = myarray[index][xyz]
			if maxmax[xyz]<myarray[index][xyz]:
				maxmax[xyz] = myarray[index][xyz]
	#print("min: " + str(minmin))
	#print("max: " + str(maxmax))
	return [ minmin, maxmax ]

def find_bounding_box_xyz(myarray):
	#print(str(myarray))
	x_dimension = len(myarray)
	y_dimension = len(myarray[0])
	z_dimension = len(myarray[0][0])
	#print(str(x_dimension) + " " + str(y_dimension) + " " + str(z_dimension))
	minmin = copy.deepcopy(myarray[0][0][0])
	maxmax = copy.deepcopy(myarray[0][0][0])
	for a in range(x_dimension):
		for b in range(y_dimension):
			for c in range(z_dimension):
				for xyz in xyz_range:
					if myarray[a][b][c][xyz]<minmin[xyz]:
						minmin[xyz] = myarray[a][b][c][xyz]
					if maxmax[xyz]<myarray[a][b][c][xyz]:
						maxmax[xyz] = myarray[a][b][c][xyz]
	#print("min: " + str(minmin))
	#print("max: " + str(maxmax))
	return [ minmin, maxmax ]

# borrowed from generic.py
def dec(number, width=1, pad_with_zeroes=True):
	if pad_with_zeroes:
		return "%0*d" % (width, number)
	else:
		return "%*d" % (width, number)

# ----------------------------------------------------

speed_of_sound = 343 # m/s

distance_per_sample_time = speed_of_sound / sample_rate # m

number_of_receivers = len(receiver_location)
receiver_bounding_box = find_bounding_box_linear(receiver_location)
receiver_extents =  [ receiver_bounding_box[max_index][xyz] - receiver_bounding_box[min_index][xyz] for xyz in xyz_range ]

# potential source locations grid parameters:
grid_center = [ (receiver_bounding_box[max_index][xyz] + receiver_bounding_box[min_index][xyz]) / 2 for xyz in xyz_range ]
grid_quantity = [ int(3 + receiver_extents[xyz] / grid_spacing[xyz]) for xyz in xyz_range ]
grid_quantity[2] = 1 # force z axis flat
number_of_grid_points = grid_quantity[x_index] * grid_quantity[y_index] * grid_quantity[z_index]
grid_location = [[[ [grid_center[x_index]+(i-(grid_quantity[x_index]-1)/2)*grid_spacing[x_index], grid_center[y_index]+(j-(grid_quantity[y_index]-1)/2)*grid_spacing[y_index], grid_center[z_index]+(k-(grid_quantity[z_index]-1)/2)*grid_spacing[z_index]] for k in range(grid_quantity[z_index]) ] for j in range(grid_quantity[y_index]) ] for i in range(grid_quantity[x_index]) ]
grid_bounding_box = find_bounding_box_xyz(grid_location)
grid_delays_in_sample_times = [[[ [] for c in range(grid_quantity[z_index]) ] for b in range(grid_quantity[y_index]) ] for a in range(grid_quantity[x_index]) ]
receiver_delays_in_sample_times = [ [] for index in range(number_of_receivers) ]

print("receiver_location = " + str(receiver_location))
print("receiver_bounding_box = " + str(receiver_bounding_box))

number_of_delays = 0
minimum_instrumented_delay = maximum_delay_in_samples
maximum_instrumented_delay = minimum_delay_in_samples
for a in range(grid_quantity[x_index]):
	for b in range(grid_quantity[y_index]):
		for c in range(grid_quantity[z_index]):
			string = "grid_location[" + str(a) + "][" + str(b) + "][" + str(c) + "] = " + str(grid_location[a][b][c])
			delays = []
			for index in range(number_of_receivers):
				delay_in_sample_times = distance(receiver_location[index], grid_location[a][b][c]) / distance_per_sample_time
				delay_in_sample_times = int(delay_in_sample_times+1)
				if delay_in_sample_times<minimum_delay_in_samples:
					continue
				if maximum_delay_in_samples<delay_in_sample_times:
					continue
				if delay_in_sample_times<minimum_instrumented_delay:
					minimum_instrumented_delay = delay_in_sample_times
				if maximum_instrumented_delay<delay_in_sample_times:
					maximum_instrumented_delay = delay_in_sample_times
				delays.append(delay_in_sample_times)
				receiver_delays_in_sample_times[index].append(delay_in_sample_times)
				#print("delay_in_sample_times[" + str(i) + "][" + str(j) + "][" + str(k) + "]_[" + str(a) + "][" + str(b) + "][" + str(c) + "]: " + str(delay_in_sample_times))
			string += "  delays_in_sample_times[" + str(a) + "][" + str(b) + "][" + str(c) + "] = " + str(delays)
			print(string)
			grid_delays_in_sample_times[a][b][c] = delays
			number_of_delays += len(delays)

#print("speed_of_sound = " + str(speed_of_sound) + " m/s")
print("grid_bounding_box = " + str(grid_bounding_box))
print("grid_center = " + str(grid_center))
print("grid_quantity = " + str(grid_quantity))
print("sample_rate = " + str(sample_rate) + " Hz")
print("bits_per_sample = " + str(bits_per_sample))
print("distance_per_sample_time = " + str(distance_per_sample_time) + " m") # about 7.8 mm (roughly 1/128 of a meter)
print("minimum_instrumented_delay = " + str(minimum_instrumented_delay))
print("maximum_instrumented_delay = " + str(maximum_instrumented_delay))
print("number_of_grid_points / correlators needed = " + str(number_of_grid_points))
print("number_of_receivers / number of taps per correlator needed = " + str(number_of_receivers))
print("total number of delays needed = " + str(number_of_delays))
print("approximate total number of bits needed for samples = " + str(number_of_receivers*bits_per_sample*maximum_instrumented_delay))

max_receiver_delay_in_sample_times = [ 0 for index in range(number_of_receivers) ]
print("receiver delays in sample times:")
for index in range(number_of_receivers):
	grid_number = 0
	for a in range(grid_quantity[x_index]):
		for b in range(grid_quantity[y_index]):
			for c in range(grid_quantity[z_index]):
				if max_receiver_delay_in_sample_times[index]<receiver_delays_in_sample_times[index][grid_number]:
					max_receiver_delay_in_sample_times[index] = receiver_delays_in_sample_times[index][grid_number]
				grid_number += 1
for index in range(number_of_receivers):
	print("receiver " + str(index) + ": " + str(receiver_delays_in_sample_times[index]) + " (qty=" + str(len(receiver_delays_in_sample_times[index])) + "; max=" + str(max_receiver_delay_in_sample_times[index]) + ")")

# ----------------------------------------------------

def verilog_declare_parameter(parameter_name, default_value, end_string):
	string = "\tparameter " + parameter_name + " = " + str(default_value) + end_string
	print(string)

def verilog_instantiate_receiver_pipeline(pipeline_name, pipeline_length_in_subwords, receiver_subword_width):
	string = "\treg [" + str(pipeline_length_in_subwords) + "*" + str(receiver_subword_width) + "-1:0] " + str(pipeline_name) + " = 0;"
	print(string)

def verilog_instantiate_pipeline_contatenator(pipeline_name, pipeline_length_in_subwords, fresh_name, receiver_word_width, receiver_subword_width):
	string = "\talways @(posedge clock) begin\n"
	string += "\t\t" + pipeline_name + " <= { " + pipeline_name + "[(" + str(pipeline_length_in_subwords) + "-1)*" + str(receiver_subword_width) + "-1" + ":0], " + str(fresh_name) + "[" + str(receiver_word_width) + "-1-:" + str(receiver_subword_width) + "] };\n"
	string += "\tend"
	print(string)

def verilog_instantiate_pipeline_delay_tap(delay_tap_name, pipeline_name, pickoff_subword, receiver_subword_width):
	string = "\twire [" + str(receiver_subword_width) + "-1:0] " + str(delay_tap_name) + " = " + str(pipeline_name) + "[" + str(pickoff_subword) + "*" + str(receiver_subword_width) + "-1-:" + str(receiver_subword_width) + "];"
	print(string)

def verilog_instantiate_correlator(correlator_string, tap_strings, grid_string):
	string = "\tcorrelator" + str(number_of_receivers) + " #(.WIDTH(RECEIVER_SUBWORD_WIDTH)) " + str(correlator_string) + " (.clock(clock), "
	for i in range(len(tap_strings)):
		string += ".i" + str(i) + "(" + tap_strings[i] + "), "
	string += ".o(" + str(grid_string) + ")"
	string += ");"
	print(string)

# ----------------------------------------------------

number_of_bits_of_output = bits_per_sample * number_of_receivers
output_port_name = "grid"

print("")
print("module blah #(")
verilog_declare_parameter("RECEIVER_SUBWORD_WIDTH", bits_per_sample, ",")
for index in range(number_of_receivers):
	verilog_declare_parameter("RECEIVER" + dec(index, 1) + "_PIPELINE_LENGTH_IN_SUBWORDS", str(max_receiver_delay_in_sample_times[index]) + "*RECEIVER_SUBWORD_WIDTH", ",")
verilog_declare_parameter("RECEIVER_WORD_WIDTH", raw_bits_per_sample, ",")
verilog_declare_parameter("NUMBER_OF_BITS_OF_OUTPUT", number_of_bits_of_output, "")
print(") (")
print("\tinput clock,")
string = "\tinput [RECEIVER_WORD_WIDTH-1:0]"
for index in range(number_of_receivers):
	receiver_data_word = "receiver" + dec(index, 1) + "_data_word"
	string += " " + str(receiver_data_word) + ","
print(string)
grid_number = 0
string = "\toutput [NUMBER_OF_BITS_OF_OUTPUT-1:0]"
for a in range(grid_quantity[x_index]):
	for b in range(grid_quantity[y_index]):
		for c in range(grid_quantity[z_index]):
			abc_string = "_" + str(a) + "_" + str(b) + "_" + str(c)
			string += " " + str(output_port_name) + abc_string
			if not grid_number==number_of_grid_points-1:
				string += ","
			grid_number += 1
print(string)
#print("\toutput [" + str(number_of_grid_points) + "-1:0] " + str(output_port_name))
print(");")
for index in range(number_of_receivers):
	verilog_instantiate_receiver_pipeline("receiver" + dec(index, 1) + "_pipeline", "RECEIVER" + dec(index, 1) + "_PIPELINE_LENGTH_IN_SUBWORDS", "RECEIVER_SUBWORD_WIDTH")
for index in range(number_of_receivers):
	verilog_instantiate_pipeline_contatenator("receiver" + dec(index, 1) + "_pipeline", "RECEIVER" + dec(index, 1) + "_PIPELINE_LENGTH_IN_SUBWORDS", "receiver" + dec(index, 1) + "_data_word", "RECEIVER_WORD_WIDTH", "RECEIVER_SUBWORD_WIDTH")
grid_number = 0
for a in range(grid_quantity[x_index]):
	for b in range(grid_quantity[y_index]):
		for c in range(grid_quantity[z_index]):
			abc_string = "_" + str(a) + "_" + str(b) + "_" + str(c)
			tap_strings = []
			for index in range(number_of_receivers):
				receiver_number_string = dec(index, 1)
				tap_string = "tap" + receiver_number_string + abc_string
				#tap_string = "tap" + "_" + str(a) + "_" + str(b) + "_" + str(c) + "[" + receiver_number_string + "]"
				tap_strings.append(tap_string)
				receiver_pipeline_string = "receiver" + receiver_number_string + "_pipeline"
				delay = receiver_delays_in_sample_times[index][grid_number]
				verilog_instantiate_pipeline_delay_tap(tap_string, receiver_pipeline_string, delay, "RECEIVER_SUBWORD_WIDTH")
			correlator_string = "correlator" + abc_string
			grid_string = "grid" + abc_string
			verilog_instantiate_correlator(correlator_string, tap_strings, grid_string)
			grid_number += 1
print("endmodule")
print("")

