#!/bin/bash -e

# from https://wiki.archlinux.org/index.php/Xilinx_ISE_WebPACK
cd /opt/Xilinx/14.7/ISE_DS/ISE
if [ ! -L "java" ]; then
	sudo mv java java5
	sudo ln -s java6 java
fi
ls -lartd java*

