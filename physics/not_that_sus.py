#!/bin/env python3

# written 2024-11-17 by mza
# last updated 2024-12-01 by mza

# ----------------------------------------------------

# user parameters:
grid_spacing = [ 1.0, 1.0, 1.0 ] # potential source locations grid, in meters
#grid_spacing = [ 0.5, 0.5, 0.5 ] # potential source locations grid, in meters
#grid_spacing = [ 0.25, 0.25, 0.25 ] # potential source locations grid, in meters
#grid_spacing = [ 0.125, 0.125, 0.125 ] # potential source locations grid, in meters

# receiver locations:
receiver_location = []
if 0: # original
	receiver_location.append([ -0.5, +0.5, +0.0 ])
	receiver_location.append([ +0.5, +0.5, +0.0 ])
	receiver_location.append([ +0.0, -0.5, +0.0 ])
elif 1: # "T" shape
	receiver_location.append([ -0.5, +0.0, +0.0 ])
	receiver_location.append([ +0.5, +0.0, +0.0 ])
	receiver_location.append([ +0.0, -0.5, +0.0 ])

# "constants":
raw_sample_rate = 44100 # Hz
sample_rate_factor = 32
sample_rate = raw_sample_rate // sample_rate_factor
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
max_max_receiver_delay_in_sample_times = 0
for index in range(number_of_receivers):
	print("receiver " + str(index) + ": " + str(receiver_delays_in_sample_times[index]) + " (qty=" + str(len(receiver_delays_in_sample_times[index])) + "; max=" + str(max_receiver_delay_in_sample_times[index]) + ")")
	if max_max_receiver_delay_in_sample_times<max_receiver_delay_in_sample_times[index]:
		max_max_receiver_delay_in_sample_times = max_receiver_delay_in_sample_times[index]

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
print("module pipeline_correlator3 #(");
print("\tparameter WIDTH = 3,");
print("\tparameter NUMBER_OF_INPUTS = 3,");
print("\tparameter NUMBER_OF_BITS_OF_OUTPUT = NUMBER_OF_INPUTS * WIDTH");
print(") (");
print("\tinput clock,");
print("\tinput [WIDTH-1:0] i0, i1, i2,");
print("\toutput reg [NUMBER_OF_BITS_OF_OUTPUT-1:0] o = 0");
print(");");
print("\treg [WIDTH-1:0] i0_old0 = 0, i1_old0 = 0, i2_old0 = 0, i2_old1 = 0;");
print("\treg [NUMBER_OF_BITS_OF_OUTPUT-1:0] o_old1 = 0, o_old2 = 0;");
print("\talways @(posedge clock) begin");
print("\t\ti0_old0 <= i0; i1_old0 <= i1; i2_old0 <= i2;");
print("\t\ti2_old1 <= i2_old0;");
print("\t\to_old1 <= i0_old0 * i1_old0;");
print("\t\to_old2 <= o_old1 * i2_old1;");
print("\t\to <= o_old2;");
print("\tend");
print("endmodule");

print("")
print("module instant_correlator3 #(");
print("\tparameter WIDTH = 3,");
print("\tparameter NUMBER_OF_INPUTS = 3,");
print("\tparameter NUMBER_OF_BITS_OF_OUTPUT = NUMBER_OF_INPUTS * WIDTH");
print(") (");
print("\tinput clock,");
print("\tinput [WIDTH-1:0] i0, i1, i2,");
print("\toutput reg [NUMBER_OF_BITS_OF_OUTPUT-1:0] o = 0");
print(");");
print("\talways @(posedge clock) begin");
print("\t\to <= i0 * i1 * i2;");
print("\tend");
print("endmodule");

print("")
print("module correlator3 #(");
print("\tparameter WIDTH = 3,");
print("\tparameter NUMBER_OF_INPUTS = 3,");
print("\tparameter NUMBER_OF_BITS_OF_OUTPUT = NUMBER_OF_INPUTS * WIDTH,");
print("\tparameter PIPELINED = 1");
print(") (");
print("\tinput clock,");
print("\tinput [WIDTH-1:0] i0, i1, i2,");
print("\toutput [NUMBER_OF_BITS_OF_OUTPUT-1:0] o");
print(");");
print("\tif (PIPELINED) begin");
print("\t\tpipeline_correlator3 #(.WIDTH(WIDTH)) pipeco (.clock(clock), .i0(i0), .i1(i1), .i2(i2), .o(o));");
print("\tend else begin");
print("\t\tinstant_correlator3 #(.WIDTH(WIDTH)) insta (.clock(clock), .i0(i0), .i1(i1), .i2(i2), .o(o));");
print("\tend");
print("endmodule");

print("")
print("module sus #(")
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

# ----------------------------------------------------

testbench_clock_period = 1
testbench_clock_half_period = testbench_clock_period / 2
#stimulus_amplitude = 2**3-1
stimulus_amplitude = 1

print("module sus_tb #(")
verilog_declare_parameter("PERIOD", 1.0, ",")
verilog_declare_parameter("P", "PERIOD", ",")
verilog_declare_parameter("HALF_PERIOD", "PERIOD/2", ",")
verilog_declare_parameter("NUMBER_OF_BITS_OF_OUTPUT", number_of_bits_of_output, ",")
verilog_declare_parameter("WAVEFORM_LENGTH", 7, ",")
verilog_declare_parameter("PIPELINE_PICKOFF", 2*max_max_receiver_delay_in_sample_times, "")
print(");")
print("\treg clock = 0;");
#print("\twire [8:0] grid_0_0_0;");
string = "\twire [NUMBER_OF_BITS_OF_OUTPUT-1:0] "
grid_number = 0
for a in range(grid_quantity[x_index]):
	for b in range(grid_quantity[y_index]):
		for c in range(grid_quantity[z_index]):
			abc_string = "_" + str(a) + "_" + str(b) + "_" + str(c)
			if not grid_number==0:
				string += ", "
			string += "grid" + abc_string
			grid_number += 1
string += ";"
print(string)
print("\twire [14:0] zeroes = 0;");
print("\treg [2:0] r0 [PIPELINE_PICKOFF:0];");
print("\treg [2:0] r1 [PIPELINE_PICKOFF:0];");
print("\treg [2:0] r2 [PIPELINE_PICKOFF:0];");
print("\twire [17:0] receiver0_data_word = { r0[PIPELINE_PICKOFF], zeroes };");
print("\twire [17:0] receiver1_data_word = { r1[PIPELINE_PICKOFF], zeroes };");
print("\twire [17:0] receiver2_data_word = { r2[PIPELINE_PICKOFF], zeroes };");
print("\twire [2:0] waveform_a [WAVEFORM_LENGTH-1:0] = { 3'd0, 3'd1, 3'd2, 3'd3, 3'd2, 3'd1, 3'd0 }; // triangle 3");
print("\twire [2:0] waveform_b [WAVEFORM_LENGTH-1:0] = { 3'd0, 3'd0, 3'd1, 3'd2, 3'd1, 3'd0, 3'd0 }; // triangle 2");
print("\twire [2:0] waveform_c [WAVEFORM_LENGTH-1:0] = { 3'd0, 3'd0, 3'd2, 3'd3, 3'd2, 3'd0, 3'd0 }; // truncated triangle 3");
print("\treg stim = 0;")
print("\tsus mysus (.clock(clock),");
print("\t\t.receiver0_data_word(receiver0_data_word), .receiver1_data_word(receiver1_data_word), .receiver2_data_word(receiver2_data_word),");
string = "\t\t"
grid_number = 0
for a in range(grid_quantity[x_index]):
	for b in range(grid_quantity[y_index]):
		for c in range(grid_quantity[z_index]):
			abc_string = "_" + str(a) + "_" + str(b) + "_" + str(c)
			if not grid_number==0:
				string += ", "
			string += ".grid" + abc_string + "(grid" + abc_string + ")"
			grid_number += 1
string += ");"
print(string)
print("\talways begin");
print("\t\t#" + str(testbench_clock_half_period) + "; clock <= ~clock;");
print("\tend");
print("\tinteger i;");
print("\talways @(posedge clock) begin");
print("\t\tfor (i=1; i<=PIPELINE_PICKOFF; i=i+1) begin");
print("\t\t\tr0[i] <= r0[i-1];");
print("\t\t\tr1[i] <= r1[i-1];");
print("\t\t\tr2[i] <= r2[i-1];");
print("\t\tend");
print("\t\tr0[0] <= 0;");
print("\t\tr1[0] <= 0;");
print("\t\tr2[0] <= 0;");
print("\tend");
print("\tinitial begin");
if 0:
	delay_between_grid_stimuli = 2 * testbench_clock_period * max_max_receiver_delay_in_sample_times;
	for a in range(grid_quantity[x_index]):
		for b in range(grid_quantity[y_index]):
			for c in range(grid_quantity[z_index]):
				string = "\t\t#" + str(delay_between_grid_stimuli) + "; stim<=1; #1; stim<=0;"
				delays = grid_delays_in_sample_times[a][b][c]
				min_delay = max_max_receiver_delay_in_sample_times
				max_delay = 0
				delay_set = set()
				for delay in delays:
					delay_set.add(delay)
					if delay<min_delay:
						min_delay = delay
					if max_delay<delay:
						max_delay = delay
				indexed_delays = []
				for delay in sorted(delay_set, reverse=True):
					list_of_receiver_indices = []
					for i in range(len(delays)):
						if delay==delays[i]:
							list_of_receiver_indices.append(i)
					indexed_delays.append([ testbench_clock_period * delay, list_of_receiver_indices ])
				#print(indexed_delays)
				#indexed_delays = [ [ testbench_clock_period * delays[i], i ] for i in range(len(delays)) ]
				#sorted_delays = sorted(indexed_delays, reverse=True)
				previous_delay = indexed_delays[0][0] + testbench_clock_period
				#print(sorted_delays)
				#print(delay_set)
				for delay in indexed_delays:
					this_delay = previous_delay - delay[0] - testbench_clock_period
					string += " #" + str(this_delay) + ";"
					for i in range(len(delay[1])):
						string += " r" + str(delay[1][i]) + "<=" + str(stimulus_amplitude) + ";"
					string += " #" + str(testbench_clock_period) + "; r0<=0;r1<=0;r2<=0;"
					previous_delay = delay[0]
				abc_string = "_" + str(a) + "_" + str(b) + "_" + str(c)
				string += " // grid" + abc_string
				print(string)
else:
	delay_between_grid_stimuli = 4 * testbench_clock_period * max_max_receiver_delay_in_sample_times
	print("\t\tfor (i=0; i<=PIPELINE_PICKOFF; i=i+1) begin");
	print("\t\t\tr0[i] <= 0;");
	print("\t\t\tr1[i] <= 0;");
	print("\t\t\tr2[i] <= 0;");
	print("\t\tend");
	for a in range(grid_quantity[x_index]):
		for b in range(grid_quantity[y_index]):
			for c in range(grid_quantity[z_index]):
				abc_string = "_" + str(a) + "_" + str(b) + "_" + str(c)
				string = "\t\t#(" + str(delay_between_grid_stimuli) + "*P); stim<=1; #P; stim<=0; #P; "
				delays = grid_delays_in_sample_times[a][b][c]
				string += "for (i=0; i<WAVEFORM_LENGTH; i=i+1) begin r0[" + str(grid_delays_in_sample_times[a][b][c][0]) + "+i] <= waveform_a[WAVEFORM_LENGTH-i-1]; r1[" + str(grid_delays_in_sample_times[a][b][c][1]) + "+i] <= waveform_b[WAVEFORM_LENGTH-i-1]; r2[" + str(grid_delays_in_sample_times[a][b][c][2]) + "+i] <= waveform_c[WAVEFORM_LENGTH-i-1]; end // grid" + abc_string
				print(string)

print("\t\t#100; $finish;");
print("\tend");
print("endmodule")
print("")

# ----------------------------------------------------

