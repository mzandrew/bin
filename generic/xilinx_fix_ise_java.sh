#!/bin/bash -e

cd /opt/Xilinx/14.7/ISE_DS/ISE
if [ ! -L "java" ]; then
	sudo mv java java5
	sudo ln -s java6 java
fi
ls -lartd java*

