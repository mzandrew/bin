#!/bin/bash -e

. /opt/Xilinx/14.7/ISE_DS/settings64.sh 1>/dev/null 2>&1
cd ~/build/hdl/ise-projects
ise 1>/dev/null 2>&1 &

