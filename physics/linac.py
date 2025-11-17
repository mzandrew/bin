#!/usr/bin/env python3

# written 2025-09-10 by mza

#RF = 200.e6
#RF = 1.3e9
RF = 508887500.
N = 100000
maximum_total_energy = 7.e9
#maximum_total_energy = 4.e9
initial_kinetic_energy = 0.
#initial_kinetic_energy = 1.e6
electron_rest_energy = 511000.
proton_rest_energy = 938.e6
incremental_kinetic_energy = 100.e3
c = 3.e8

import math

def half_period():
	tau = 1./RF
	return tau/2.

def v_over_c(gamma):
	v_c = math.sqrt(1.-gamma**-2)
	return v_c

#def accelerating_cavity(energy):
def drift_cavity(total_energy):
	gamma = total_energy/electron_rest_energy
	#gamma = total_energy/proton_rest_energy
	v_c = v_over_c(gamma)
	length = v_c * c * half_period()
	return (gamma, v_c, length)

total_energy = electron_rest_energy + initial_kinetic_energy
#total_energy = proton_rest_energy + initial_kinetic_energy
for i in range(1, N+1):
	total_energy += incremental_kinetic_energy
	if maximum_total_energy<total_energy:
		break
	(gamma, v_c, length) = drift_cavity(total_energy)
	print("total_energy=%.1f MeV; gamma=%.1f; v/c=%.1f %%; drift%d=%.1f cm" % (total_energy/1.e6, gamma, 100.*v_c, i, 100.*length))

