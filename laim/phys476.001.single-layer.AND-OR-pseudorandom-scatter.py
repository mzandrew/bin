#!/usr/bin/env python3

# written 2025-03-13 by mza
# last updated 2025-03-16 by mza

# i is usually the index over the number of datapoints
# j is usually the index over the number of classes
# k is usually the index over the number of inputs

import random, math
dataset = []

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

def show_datapoints():
	for i in range(len(dataset)):
		print(str(i) + " " + str(dataset[i]))

def set_initial_weights(init):
	global weight; weight = init
	global delta_weight; delta_weight = [ 0 for k in range(len(init)) ]

def show_current_weights(prefix=""):
	print(prefix + "weights: " + str(myround(weight)))

def sigmoid(x): # logistic function
	return 1.0 / (1.0 + math.exp(-x))

def iterate(irange=None):
	if irange is None:
		irange = range(len(dataset))
	global weight, delta_weight
	total_error = 0
	#print(str(irange))
	for i in irange:
		y = 0
		for k in range(len(dataset[i])-1):
			y += weight[k] * dataset[i][k]
		y += weight[len(dataset[i])-1]
		if binary_function:
			if y<=0:
				y = 0
			else:
				y = 1
		else:
			y = sigmoid(y)
		delta_weight[len(dataset[i])-1] = dataset[i][len(dataset[i])-1] - y
		if verbose:
			print("datapoint[" + str(i) + "] error in weight = " + str(round(dataset[i][len(dataset[i])-1],rounding_precision)) + " - " + str(round(y,rounding_precision)) + " = " + str(round(delta_weight[len(dataset[i])-1],rounding_precision)))
		for k in range(len(dataset[i])-1):
			delta_weight[k] = delta_weight[len(dataset[i])-1] * dataset[i][k]
			if verbose:
				print("datapoint[" + str(i) + "] error in weight " + str(k) + " = (" + str(round(dataset[i][len(dataset[i])-1],rounding_precision)) + " - " + str(round(y,rounding_precision)) + ") * " + str(round(dataset[i][k],rounding_precision)) + " = " + str(round(delta_weight[k],rounding_precision)))
		for k in range(len(dataset[i])):
			weight[k] += update_factor * delta_weight[k]
		total_error += sum([math.fabs(delta_weight[l]) for l in range(len(delta_weight))])
	print("overall error = " + str(round(total_error,rounding_precision)), end=' ')
	global error_sequence
	error_sequence.append(total_error)
	show_current_weights("new ")

def myround(mylist):
	return [round(mylist[l],rounding_precision) for l in range(len(mylist))]

verbose = False
epochs = 1000000
stochastic_iterations_per_epoch = 1
rounding_precision = 6
update_factor = 0.1
random.seed(7)
binary_function = False

if (0):
	generate_AND2_datapoints() # [1, 1, -2]
	#generate_NAND2_datapoints() # [-1, -1, 2]
	#generate_OR2_datapoints() # [1, 1, -1]
	#generate_NOR2_datapoints() # [-1, -1, 0]
	#generate_XOR2_datapoints() # cannot!
	set_initial_weights([0, 0, 0])
elif (1):
	generate_AND3_datapoints() # [1, 1, 1, -3] [42, 42, 42, -100]
	#generate_OR3_datapoints() # [1, 1, 1, -1]
	#generate_3to8_decoder_datapoints(); binary_function = False # [4, 2, 1, 0]
	#set_initial_weights([0, 0, 0, 0])
	#set_initial_weights([20.637, 20.637, 20.637, -52.006])
	#set_initial_weights([21.18, 21.18, 21.18, -53.364])
	#set_initial_weights([21.607, 21.607, 21.607, -54.43])
	#set_initial_weights([42.677, 42.677, 42.677, -98.934])
	#set_initial_weights([42.495743, 42.495743, 42.495743, -99.205885])
	#set_initial_weights([42.385718, 42.385718, 42.385718, -99.370923])
	#set_initial_weights([42, 42, 42, -100])
	#set_initial_weights([41.882655, 41.882655, 41.882655, -100.056017])
	#set_initial_weights([41.866303, 41.866303, 41.866303, -100.080545])
	#set_initial_weights([41.86, 41.86, 41.86, -100.09])
	#set_initial_weights([41.844863, 41.844863, 41.844863, -100.112706])
	#set_initial_weights([41.688821, 41.688821, 41.688821, -100.09677])
	set_initial_weights([41.725986, 41.725986, 41.725986, -100.291027]) # after 20M iterations, error less than 1 part in 10^6
elif (0):
	generate_THERMOMETER4_datapoints(); binary_function = False # not satisfactory
	set_initial_weights([0, 0, 0, 0, 0])
else:
	digital_inputs = False; generate_pseudorandom_datapoints(100, ((-3,-3), (+3,+3)), (-1,+1)) # [1, 1, 0]
	set_initial_weights([0, 0, 0])
show_datapoints()
show_current_weights()
error_sequence = []
if (1):
	for epoch in range(epochs):
		print("iteration " + str(epoch), end=' ')
		iterate()
else: # stochastic
	random.seed()
	for epoch in range(epochs):
		print("\niteration " + str(epoch))
		for i in range(len(dataset)):
			iterate([random.randint(0, len(dataset)-1) for l in range(stochastic_iterations_per_epoch)])
print("\nerror sequence: " + str(myround(error_sequence)))
show_current_weights("final ")

