#!/bin/bash -e

sudo apt install python3-dev python3-rpi.gpio python3-spidev python3-w1thermsensor

if [ ! -e "RPi-Hat-Thermocouple" ]; then
	git clone git@github.com:mikelawrence/RPi-Hat-Thermocouple.git
else
	cd "RPi-Hat-Thermocouple" 
	git pull
fi

sudo apt install python3-picamera

#raspistill -rot 180 --nopreview -o pic.jpg

sudo apt install python-opencv python3-numpy

if [ ! -e "pylepton" ]; then
	git clone git@github.com:groupgets/pylepton.git
else
	cd "pylepton"
	git pull
fi

