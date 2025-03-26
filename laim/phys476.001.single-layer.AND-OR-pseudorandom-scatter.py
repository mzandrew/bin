#!/usr/bin/env python3

# written 2025-03-13 by mza
# last updated 2025-03-24 by mza

# i is usually the index over the number of datapoints
# j is usually the index over the number of classes
# k is usually the index over the number of inputs

import laim
import random

epochs = 1000000
stochastic_iterations_per_epoch = 1
random.seed(7)

if (0):
	laim.binary_function = True
	laim.generate_AND2_datapoints() # [1, 1, -2]
	#generate_NAND2_datapoints() # [-1, -1, 2]
	#generate_OR2_datapoints() # [1, 1, -1]
	#generate_NOR2_datapoints() # [-1, -1, 0]
	#generate_XOR2_datapoints() # cannot!
	#laim.set_initial_weights([0, 0, 0])
	laim.set_initial_weights([1, 1, -2])
	#laim.set_initial_weights([21.047039, 21.047036, -31.738792]) # for sigmoid function
elif (1):
	laim.binary_function = True
	laim.generate_AND3_datapoints() # [1, 1, 1, -3] [42, 42, 42, -100]
	#generate_OR3_datapoints() # [1, 1, 1, -1]
	#generate_3to8_decoder_datapoints(); laim.binary_function = False # [4, 2, 1, 0]
	laim.set_initial_weights([1, 1, 1, -3])
	#laim.set_initial_weights([0, 0, 0, 0])
	#laim.set_initial_weights([42, 42, 42, -100])
	#laim.set_initial_weights([41.716, 41.716, 41.716, -100.306]) # for sigmoid function [error less than 1 part in 10^6]
elif (0):
	laim.generate_THERMOMETER4_datapoints(); laim.binary_function = False # not satisfactory
	laim.set_initial_weights([0, 0, 0, 0, 0])
else:
	laim.digital_inputs = False; laim.generate_pseudorandom_datapoints(100, ((-3,-3), (+3,+3)), (-1,+1)) # [1, 1, 0]
	#laim.set_initial_weights([0, 0, 0])
	laim.set_initial_weights([3.472162, 3.487299, -0.066604]) # for sigmoid function
laim.show_datapoints()
laim.show_current_weights()
if (1):
	for epoch in range(epochs):
		print("iteration " + str(epoch), end=' ')
		laim.iterate()
else: # stochastic
	random.seed()
	for epoch in range(epochs):
		print("\niteration " + str(epoch))
		for i in range(len(dataset)):
			laim.iterate([random.randint(0, len(dataset)-1) for l in range(stochastic_iterations_per_epoch)])
print("\nerror sequence: " + str(laim.myround(laim.error_sequence)))
laim.show_current_weights("final ")

