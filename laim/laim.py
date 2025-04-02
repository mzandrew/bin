# written 2025-03-13 by mza
# last updated 2025-04-01 by mza

import random, math, copy

dataset = []
hidden = []
weight = []
delta_weight = []
error_sequence = []

rounding_precision = 6
binary_function = False
verbose = False
update_factor = 0.1

def round1d(mylist):
	#print(str(mylist))
	return [ round(y,rounding_precision) for y in mylist ]

def round_weight(mylist):
	#print(str(mylist))
	rounded = []
	for x in mylist:
		rounded_x = []
		for y in x:
			rounded_y = []
			if isinstance(y, list):
				for z in y:
					rounded_y.append(round(z, rounding_precision))
			else:
				rounded_y = round(y, rounding_precision)
			rounded_x.append(rounded_y)
		rounded.append(rounded_x)
	return rounded
	#return [ [ [ round(z,rounding_precision) for z in y ] for y in x ] for x in mylist ]

def empty_weights():
	zeroed = []
	for x in weight:
		zeroed_x = []
		for y in x:
			zeroed_y = []
			if isinstance(y, list):
				for z in y:
					zeroed_y.append(0.0)
			else:
				zeroed_y = 0.0
			zeroed_x.append(zeroed_y)
		zeroed.append(zeroed_x)
	#print("zeroed weights = " + str(zeroed))
	return zeroed

def generate_AND2_datapoints():
	global dataset; dataset = [ (0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 1) ]

def generate_AND3_datapoints():
	global dataset; dataset = [ (0, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (1, 0, 0, 0), (0, 1, 1, 0), (1, 0, 1, 0), (1, 1, 0, 0), (1, 1, 1, 1) ]

def generate_NAND2_datapoints():
	global dataset; dataset = [ (0, 0, 1), (0, 1, 1), (1, 0, 1), (1, 1, 0) ]

def generate_OR2_datapoints():
	global dataset; dataset = [ (0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1) ]

def generate_OR3_datapoints():
	global dataset; dataset = [ (0, 0, 0, 0), (0, 0, 1, 1), (0, 1, 0, 1), (1, 0, 0, 1), (0, 1, 1, 1), (1, 0, 1, 1), (1, 1, 0, 1), (1, 1, 1, 1) ]

def generate_NOR2_datapoints():
	global dataset; dataset = [ (0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 0) ]

def generate_XOR2_datapoints(): # never converges
	global dataset; dataset = [ (0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0) ]

def generate_THERMOMETER4_datapoints(): # never converges completely
	global dataset; dataset = [ (0, 0, 0, 0, 0), (0, 0, 0, 1, 1), (0, 0, 1, 0, 2), (0, 0, 1, 1, 2),
	(0, 1, 0, 0, 3), (0, 1, 0, 1, 3), (0, 1, 1, 0, 3), (0, 1, 1, 1, 3),
	(1, 0, 0, 0, 4), (1, 0, 0, 1, 4), (1, 0, 1, 0, 4), (1, 0, 1, 1, 4),
	(1, 1, 0, 0, 4), (1, 1, 0, 1, 4), (1, 1, 1, 0, 4), (1, 1, 1, 1, 4) ]

def generate_3to8_decoder_datapoints():
	global dataset; dataset = [ (0, 0, 0, 0), (0, 0, 1, 1), (0, 1, 0, 2), (0, 1, 1, 3), (1, 0, 0, 4), (1, 0, 1, 5), (1, 1, 0, 6), (1, 1, 1, 7) ]

def generate_pseudorandom_datapoints(n, offset, input_range):
	print("there are " + str(len(offset)) + " classes")
	print("there are " + str(len(offset[0])) + " inputs")
	global dataset; dataset = []
	for j in range(len(offset)):
		for i in range(n):
			datapoint = []
			for k in range(len(offset[j])):
				if digital_inputs:
					datapoint.append( offset[j][k] + random.randint(input_range[0], input_range[1]) )
				else:
					datapoint.append( offset[j][k] + random.uniform(input_range[0], input_range[1]) )
			datapoint.append(j)
			dataset.append(datapoint)
	print("created " + str(len(dataset)) + " datapoints")

def sigmoid(x): # logistic function
	return 1.0 / (1.0 + math.exp(-x))

def iterate(irange=None):
	#print("dataset: " + str(dataset))
	if irange is None:
		irange = range(len(dataset))
	global weight, delta_weight, hidden
	total_error = 0.0
	#print(str(irange))
	truth = [ datapoint[-1] for datapoint in dataset ]
	#print("truth = " + str(truth))
#	if not len(weight[0][0]) == len(dataset[0]):
#		print("error: dimension of first set of weights (" + str(weight[0]) + ") must be one greater than the number of inputs (" + str(len(dataset[0])-1) + ")")
	print("")
	#print("len(hidden) = " + str(len(hidden)), end='')
	delta_weight = empty_weights()
	for i in irange:
		temp_delta_weight = empty_weights()
		hidden[0] = [ dataset[i][j] for j in range(len(dataset[i])-1) ]
		#print("hidden[0] = " + str(hidden[0]))
		#print("hidden: " + str(hidden))
		for h in range(1, len(hidden)):
			nodes_in_current_layer = len(hidden[h])
			nodes_in_previous_layer = len(hidden[h-1])
			#print("nodes_in_previous_layer = " + str(nodes_in_previous_layer))
			#print("nodes_in_current_layer = " + str(nodes_in_current_layer))
			for c in range(nodes_in_current_layer):
				value = 0.0
				for p in range(nodes_in_previous_layer):
					#print("h = " + str(h) + "; c = " + str(c) + "; p = " + str(p))
					value += weight[h-1][c][p] * hidden[h-1][p]
				value += weight[h-1][-1]
				print("; raw value = " + str(round(value, rounding_precision)), end='')
				if binary_function:
					if value<=0:
						value = 0
					else:
						value = 1
				else:
					value = sigmoid(value)
				print("; final value = " + str(round(value, rounding_precision)), end='')
				hidden[h][c] = value
			#print("hidden[" + str(h) + "] = " + str(hidden[h]))
		print("; hidden: " + str(hidden))
		h = len(hidden) - 1
		#for h in range(len(weight)-1, 0, -1):
		#print("h = " + str(h))
		nodes_in_current_layer = len(hidden[h])
		nodes_in_previous_layer = len(hidden[h-1])
		for c in range(nodes_in_current_layer):
			temp_delta_weight[h-1][-1] = truth[i] - hidden[h][c]
			delta_weight[h-1][-1] += temp_delta_weight[h-1][-1]
			for p in range(nodes_in_previous_layer):
				temp_delta_weight[h-1][c][p] = temp_delta_weight[h-1][-1] * hidden[h-1][p]
				delta_weight[h-1][c][p] += temp_delta_weight[h-1][c][p]
			total_error += sum([ math.fabs(value) for value in temp_delta_weight[h-1][c] ])
		#show_current_weights("new ")
		#print("temp_delta_weight = " + str(temp_delta_weight))
		#print("delta_weight = " + str(delta_weight))
#		for h in range(len(hidden)-1, 0, -1): # backpropagate
	h = len(hidden) - 1 # output layer
	#print("h = " + str(h))
	nodes_in_current_layer = len(hidden[h])
	nodes_in_previous_layer = len(hidden[h-1])
	for c in range(nodes_in_current_layer):
		for p in range(nodes_in_previous_layer):
			weight[h-1][c][p] += update_factor * delta_weight[h-1][c][p]
		weight[h-1][-1] += update_factor * delta_weight[h-1][-1]
#			if verbose:
#				print("datapoint[" + str(c) + "] error in weight = " + str(round(hidden[h][c][len(hidden[h][c])-1],rounding_precision)) + " - " + str(round(value,rounding_precision)) + " = " + str(round(delta_weight[h][len(hidden[h][c])-1],rounding_precision)))
#			for p in range(len(hidden[h][c])-1):
#				delta_weight[h][p] = delta_weight[h][len(hidden[h][c])-1] * hidden[h][c][p]
#				if verbose:
#					print("datapoint[" + str(c) + "] error in weight " + str(p) + " = (" + str(round(hidden[h][c][len(hidden[h][c])-1],rounding_precision)) + " - " + str(round(value,rounding_precision)) + ") * " + str(round(hidden[h][c][p],rounding_precision)) + " = " + str(round(delta_weight[h][p],rounding_precision)))
#	for p in range(len(hidden[h][c])):
	print("error for this iteration = " + str(round(total_error,rounding_precision)))
#, end=' '
	global error_sequence
	error_sequence.append(total_error)
	print("")
	show_current_weights("new ")

def show_datapoints():
	for i in range(len(dataset)):
		print(str(i) + " " + str(dataset[i]))

def set_initial_weights(init):
	print("init = " + str(init))
	global weight; weight = copy.deepcopy(init)
	global delta_weight; delta_weight = empty_weights()
	#global weight; weight = [ [ float(y) for y in x ] for x in init ]
	#print("initial weight: " + str(weight))
	#global delta_weight; delta_weight = [ [ 0.0 for y in x ] for x in init ]
	#print("delta_weight: " + str(delta_weight))
	global hidden; hidden = []; hidden.append([]) # the first empty list is to be replaced by each datapoint in turn
	#hidden.extend([ [ 0.0 for y in range(len(x)-1) ] for x in weight ]); hidden.append([0.0])
	print("init[0] = " + str(init[0]))
	print("len(init[0]) = " + str(len(init[0])))
	for h in range(len(init)):
		hidden.append([ 0.0 for y in range(len(init[h])-1) ])
	#hidden.append([0.0]) # last entry has len==1 to enforce single output node
	#global hidden; hidden = [ [ 0.0 for y in range(len(x)-1) ] for x in weight ]; hidden.insert(0, [])
	#global hidden; hidden = [ [ 0.0 for y in range(len(x)-1) ] for x in weight ]
	#global hidden; hidden = [ [], [0.0] ] # last entry has len==1 to enforce single output node
	print("hidden: " + str(hidden))
	if not len(hidden[-1]) == 1:
		print("error: dimension of output layer (" + str(len(hidden[-1])) + ") must be 1")

def show_current_weights(prefix=""):
	print(prefix + "weights: " + str(round_weight(weight)))

