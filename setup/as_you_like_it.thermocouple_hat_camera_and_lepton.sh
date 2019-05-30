#!/bin/bash -e

cd
mkdir -p build
cd ${HOME}/build

sudo apt install -y python3-dev python3-rpi.gpio python3-spidev python3-w1thermsensor i2c-tools

if [ ! -e "RPi-Hat-Thermocouple" ]; then
	#git clone git@github.com:mikelawrence/RPi-Hat-Thermocouple.git
	git clone https://github.com/mikelawrence/RPi-Hat-Thermocouple.git
else
	cd "RPi-Hat-Thermocouple" 
	git pull
fi

sudo apt install -y python3-picamera

#raspistill -rot 180 --nopreview -o pic.jpg

sudo apt install -y python-opencv python3-numpy

cd ${HOME}/build

if [ ! -e "pylepton" ]; then
	#git clone git@github.com:groupgets/pylepton.git
	git clone https://github.com/groupgets/pylepton.git
else
	cd "pylepton"
	git pull
fi

sudo apt install -y ffmpeg gnuplot

# recommended for high radiation environments:
sudo apt install -y watchdog
sudo systemctl enable watchdog
sudo systemctl start watchdog

cat <<here

# change the following in system.conf:

CrashReboot=yes
RuntimeWatchdogSec=15
ShutdownWatchdogSec=15

here
sleep 3
sudo vim /etc/systemd/system.conf
echo "now reboot for the systemd configuration to take effect"

