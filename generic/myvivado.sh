#!/bin/bash -e

#. /opt/Xilinx/Vivado/2014.4/settings64.sh 1>/dev/null 2>&1
. /opt/Xilinx/Vivado/2022.2/settings64.sh 1>/dev/null 2>&1
cd ~/build/hdl/vivado-projects
vivado 1>/dev/null 2>&1 &

