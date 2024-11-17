#!/bin/env python3

# written 2024-11-17 by mza
# last updated 2024-11-17 by mza

import math

speed_of_sound = 343 # m/s
sample_rate = 44100 # 1/s
distance_per_sample_time = speed_of_sound / sample_rate # m
minimum_delay_in_samples = 1
maximum_delay_in_samples = 1000

x_index = 2; y_index = 1; z_index = 0

# receiver grid parameters:
receiver_center_x = 0
receiver_center_y = 0
receiver_center_z = 0
receiver_spacing_x = 1.0
receiver_spacing_y = 1.0
receiver_spacing_z = 1.0
receiver_quantity_x = 2
receiver_quantity_y = 2
receiver_quantity_z = 1
#receiver_bounding_box = []
number_of_receivers = receiver_quantity_x * receiver_quantity_y * receiver_quantity_z

# potential source locations grid parameters:
grid_center_x = receiver_center_x
grid_center_y = receiver_center_y
grid_center_z = receiver_center_z
grid_spacing_x = 1
grid_spacing_y = 1
grid_spacing_z = 1
grid_quantity_x = int(1 + (receiver_quantity_x) / grid_spacing_x)
grid_quantity_y = int(1 + (receiver_quantity_y) / grid_spacing_y)
grid_quantity_z = 1 # int(1 + (receiver_quantity_z) / grid_spacing_z)
number_of_grid_points = grid_quantity_x * grid_quantity_y * grid_quantity_z

def distance(a, b):
	delta_x = b[x_index] - a[x_index]
	delta_y = b[y_index] - a[y_index]
	delta_z = b[z_index] - a[z_index]
	distance = math.sqrt(delta_x**2 + delta_y**2 + delta_z**2)
	return distance

receiver_location = [[[ (receiver_center_x+(i-(receiver_quantity_x-1)/2)*receiver_spacing_x,receiver_center_y+(j-(receiver_quantity_y-1)/2)*receiver_spacing_y,receiver_center_z+(k-(receiver_quantity_z-1)/2)*receiver_spacing_z) for k in range(receiver_quantity_z) ] for j in range(receiver_quantity_y) ] for i in range(receiver_quantity_x) ]
grid_location = [[[ (grid_center_x+(i-(grid_quantity_x-1)/2)*grid_spacing_x,grid_center_y+(j-(grid_quantity_y-1)/2)*grid_spacing_y,grid_center_z+(k-(grid_quantity_z-1)/2)*grid_spacing_z) for k in range(grid_quantity_z) ] for j in range(grid_quantity_y) ] for i in range(grid_quantity_x) ]
grid_delays_in_sample_times = [[[ [] for c in range(grid_quantity_z) ] for b in range(grid_quantity_y) ] for a in range(grid_quantity_x) ]
#delay_in_sample_times = [[[[[[ 0 for k in range(grid_quantity_z) ] for j in range(grid_quantity_y) ] for i in range(grid_quantity_x) ]
#delay_in_sample_times = [[[[[[ 0 for k in range(receiver_quantity_z) ] for j in range(receiver_quantity_y) ] for i in range(receiver_quantity_x) ] for c in range(grid_quantity_z) ] for b in range(grid_quantity_y) ] for a in range(grid_quantity_x) ]

print("speed_of_sound: " + str(speed_of_sound) + " m/s")
print("sample_rate: " + str(sample_rate) + " Hz")
print("distance_per_sample_time: " + str(distance_per_sample_time) + " m") # about 7.8 mm (roughly 1/128 of a meter)
print("grid_quantity = " + str((grid_quantity_x, grid_quantity_y, grid_quantity_z)))
print("number_of_grid_points = " + str(number_of_grid_points))
print("number_of_receivers = " + str(number_of_receivers))

for i in range(receiver_quantity_x):
	for j in range(receiver_quantity_y):
		for k in range(receiver_quantity_z):
			print("receiver_location[" + str(i) + "][" + str(j) + "][" + str(k) + "]: " + str(receiver_location[i][j][k]))

number_of_delays = 0
for a in range(grid_quantity_x):
	for b in range(grid_quantity_y):
		for c in range(grid_quantity_z):
			print("grid_location[" + str(a) + "][" + str(b) + "][" + str(c) + "]: " + str(grid_location[a][b][c]))
			delays = []
			for i in range(receiver_quantity_x):
				for j in range(receiver_quantity_y):
					for k in range(receiver_quantity_z):
						delay_in_sample_times = distance(receiver_location[i][j][k], grid_location[a][b][c]) / distance_per_sample_time
						delay_in_sample_times = int(delay_in_sample_times)
						if delay_in_sample_times<minimum_delay_in_samples:
							continue
						if maximum_delay_in_samples<delay_in_sample_times:
							continue
						delays.append(delay_in_sample_times)
						#print("delay_in_sample_times[" + str(i) + "][" + str(j) + "][" + str(k) + "]_[" + str(a) + "][" + str(b) + "][" + str(c) + "]: " + str(delay_in_sample_times))
			print("grid_delays_in_sample_times[" + str(a) + "][" + str(b) + "][" + str(c) + "]: " + str(delays))
			grid_delays_in_sample_times[a][b][c] = delays
			number_of_delays += len(delays)
print("total number of delays needed: " + str(number_of_delays))

import sys; sys.exit(0)
for index in range(len(receiver.keys())):
	print("receiver[" + str(index) + "] location: " + str(receiver[index][0]))
	print("receiver[" + str(index) + "] delays: " + str(receiver[index][0]))

receiver = {}
index = 0
for i in range(receiver_quantity_x):
	for j in range(receiver_quantity_y):
		for k in range(receiver_quantity_z):
			delays = ()
			for other_index in range(number_of_receivers):
				delays.append(distance(receiver_location[i][j][k], receiver_location[a][b][c]) / distance_per_sample_time)
			receiver[index] = (receiver_location[i][j][k], 5)
			index = index + 1

