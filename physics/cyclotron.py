#!/usr/bin/env python3

# written 2025-09-10 by mza

import math

electron_mass = 9.11e-31 # kg
proton_mass = 1.67e-27 # kg
energy = 1.6e-16 # J
magnetic_field = 1. # kg/A/s^2
electron_charge = 1.6e-19 # C

def radius(energy, mass, charge, magnetic_field):
	r = math.sqrt(2*energy*mass)/(charge*magnetic_field)
	return r

def omega(mass, charge, magnetic_field):
	o = 2.*math.pi*charge*magnetic_field/mass
	return o

print("electron: r=%.1f mm" % (1000*radius(energy, electron_mass, electron_charge, magnetic_field)))
print("proton: r=%.1f mm" % (1000*radius(energy, proton_mass, electron_charge, magnetic_field)))

print("electron: f=%.1f MHz" % (omega(electron_mass, electron_charge, magnetic_field)/1.e6))
print("proton: f=%.1f MHz" % (omega(proton_mass, electron_charge, magnetic_field)/1.e6))

