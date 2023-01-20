#!/bin/bash -e

# written 2017-11 by mza
# based on instructions posted at http://www.clifford.at/icestorm/
# last updated 2022-06-18 by mza

declare build="$HOME/build"
declare -i np=$(grep -c "^processor" /proc/cpuinfo)
declare -i j=$((np-1))
#if [ $j -gt $np ]; then
#	j=1
#	echo "dropping j to 1"
#fi
echo "j=$j"

function get_source_if_necessary {
	cd $build
	if [ ! -e icestorm ]; then
		git clone https://github.com/cliffordwolf/icestorm.git icestorm
	fi
	if [ ! -e arachne-pnr ]; then
		git clone https://github.com/cseed/arachne-pnr.git arachne-pnr
	fi
	#if [ ! -e nextpnr ]; then
	#	git clone https://github.com/YosysHQ/nextpnr.git
	#fi
	if [ ! -e yosys ]; then
		git clone https://github.com/cliffordwolf/yosys.git yosys
	fi
	#if [ ! -e yosys-plugins ]; then
	#	git clone https://github.com/cliffordwolf/yosys-plugins.git
	#fi
	#if [ ! -e vhd2vl ]; then
	#	git clone https://github.com/ldoolitt/vhd2vl.git
	#fi
	#if [ ! -e netlistsvg ]; then
	#	# needs npm
	#	git clone https://github.com/nturley/netlistsvg
	#fi
	#if [ ! -e ice40_viewer ]; then
	#	git clone https://github.com/knielsen/ice40_viewer.git
	#fi
	#if [ ! -e swapforth ]; then
	#	# needs gforth
	#	git clone https://github.com/jamesbowman/swapforth.git
	#fi
	#if [ ! -e myhdl ]; then
	#	git clone https://github.com/myhdl/myhdl.git
	#fi
	#if [ ! -e apio ]; then
	#	git clone https://github.com/FPGAwars/apio.git
	#fi
	#pip install -U apio
	#if [ ! -e icestudio ]; then
	#	git clone https://github.com/FPGAwars/icestudio.git
	#fi
}

function fix_permissions {
	sudo find ${@} -type d -exec chmod --changes 0755 {} + -o -type f -exec chmod --changes 0644 {} +
}

function fix_script_permissions {
	sudo find "${@}" -exec chmod --changes 0755 {} +
}

# adapted from https://github.com/mzandrew/bin/blob/master/generic/lf
declare DATESTAMP='%TY-%Tm-%Td+%TH:%TM'
declare USERGROUP='%7u:%-7g'
declare PERMISSIONS='%M'
declare SIZE='%12s'
declare BASE="$DATESTAMP $USERGROUP $PERMISSIONS $SIZE %p"
declare REGULAR_FILE_STRING="$BASE\n"
declare REGULAR_DIR_STRING="$BASE/\n"
declare SYMLINK_STRING="$BASE -> %l\n"
function list_files {
	find "${@}" \
		-type d \( -name "proc" -o -name "dev" -o -name "\.svn" -o -name "\.git" \) -prune \
		-o -type d -printf "$REGULAR_DIR_STRING" \
		-o -type l -printf "$SYMLINK_STRING" \
		-o         -printf "$REGULAR_FILE_STRING" \
		| sort -k 1n,1
		
}

function install_prerequisites_apt {
	sudo apt -y install build-essential clang clang-format bison flex libreadline-dev \
		gawk tcl-dev libffi-dev git mercurial graphviz \
		xdot pkg-config python python3 python3-dev python3-pip libftdi-dev gforth iverilog gtkwave \
		libboost-all-dev libboost-python-dev zlib1g-dev \
		cmake libeigen3-dev \
		xclip
	sudo apt -y install qt5-default || /bin/true
	sudo apt -y install npm || sudo apt -y install bb-npm-installer
}

function install_prerequisites_yum {
	sudo yum -y install make automake gcc gcc-c++ kernel-devel clang bison \
		flex readline-devel gawk tcl-devel libffi-devel git mercurial \
		graphviz python-xdot pkgconfig python python34 libftdi-devel npm
}

function install_prerequisites_pac {
	sudo pacman --needed --noconfirm -S make automake gcc clang bison \
		flex readline gawk tcl git mercurial \
		graphviz pkgconfig python python3 libftdi npm
}

function install_prerequisites_ipkg {
	sudo ipkg install libftdi python3 make gcc bison flex readline gawk tcl git libffi pkgconfig automake libc-dev
	# not available:
	# libftdi-devel
	# clang
}

declare -i redhat=0 SL6=0 SL7=0 deb=0 arch=0 ipkg=0
if [ -e /etc/redhat-release ]; then
	redhat=1
	set +e
	SL6=$(grep -c "Scientific Linux release 6" /etc/redhat-release)
	SL7=$(grep -c "Scientific Linux release 7" /etc/redhat-release)
	set -e
elif [ -e /etc/debian_version ]; then
	deb=1
elif [ -e /etc/arch-release ]; then
	arch=1
elif [ -e /opt/bin/ipkg ]; then
	ipkg=1
else
	echo "what kind of linux is this?"
	exit 1
fi
if [ $deb -gt 0 ]; then
	install_prerequisites_apt
elif [ $redhat -gt 0 ]; then
	install_prerequisites_yum
elif [ $arch -gt 0 ]; then
	install_prerequisites_pac
elif [ $ipkg -gt 0 ]; then
	install_prerequisites_ipkg
fi

function do_icestorm {
	echo; echo "icestorm"
	# sudo yum -y install python34 libftdi-devel
	cd $build/icestorm
	git pull
	nice make -k -j$j
	if [ $? -ne 0 ]; then return; fi
	sudo nice make install
	fix_permissions /usr/local/share/icebox
	fix_script_permissions /usr/local/bin/ice*
	#list_files /usr/local/bin/ice* /usr/local/share/icebox
}

function do_icestudio {
	echo; echo "icestudio"
	# sudo yum -y install python34 libftdi-devel
	cd $build/icestudio
	git pull
	#nice make -k -j$j
	#if [ $? -ne 0 ]; then return; fi
	#sudo nice make install
	nice npm install
	#fix_permissions /usr/local/share/icebox
	#fix_script_permissions /usr/local/bin/ice*
	#list_files /usr/local/bin/ice* /usr/local/share/icebox
}

function do_arachne_pnr {
	echo; echo "arachne-pnr"
	cd $build/arachne-pnr
	git pull
	nice make -k -j$j
	if [ $? -ne 0 ]; then return; fi
	sudo nice make install
	fix_permissions /usr/local/share/arachne-pnr
	fix_script_permissions /usr/local/bin/arachne*
	#list_files /usr/local/bin/arachne* /usr/local/share/arachne-pnr
}

function do_nextpnr {
	# needs python3.5
	echo; echo "nextpnr"
	cd $build/nextpnr
	git pull
	nice cmake -DARCH=ice40 .
	nice make -k -j$j
	if [ $? -ne 0 ]; then return; fi
	sudo nice make install
	echo "nextpnr-ice40 --json blinky.json --pcf blinky.pcf --asc blinky.asc --gui"
#	fix_permissions /usr/local/share/arachne-pnr
#	fix_script_permissions /usr/local/bin/arachne*
	#list_files /usr/local/bin/arachne* /usr/local/share/arachne-pnr
}

function do_yosys {
	echo; echo "yosys"
	# sudo yum -y install clang tcl-devel bison flex
	cd $build/yosys
	git pull
	nice make config-gcc
	nice make -k -j$j
	if [ $? -ne 0 ]; then return; fi
	# to work around a bison version problem, comment out 2 lines in:
	# ~/build/yosys/frontends/verilog/verilog_parser.y like so:
	#//%define parse.error verbose
	#//%define parse.lac full
	sudo nice make install
	fix_permissions /usr/local/share/yosys/
	fix_script_permissions /usr/local/bin/yosys*
	#list_files /usr/local/bin/yosys* /usr/local/share/yosys
}

function do_yosys_plugins {
	echo; echo "yosys-plugins"
	cd $build/yosys-plugins
	git pull
	cd $build/yosys-plugins/vhdl
	nice make -k -j$j
	if [ $? -ne 0 ]; then return; fi
	sudo nice make install
	fix_permissions /usr/local/share/yosys/plugins/
	list_files /usr/local/share/yosys/plugins
}

function do_vhdl2vl {
	echo; echo "vhd2vl"
	cd $build/vhd2vl
	git pull
	nice make -k -j$j
	if [ $? -ne 0 ]; then return; fi
	sudo cp src/vhd2vl /usr/local/bin/
	#sudo chown root /usr/local/bin/vhd2vl 
	fix_script_permissions /usr/local/bin/vhd2vl
	list_files /usr/local/bin/vhd2vl 
}

function do_netlistsvg {
	# Error: Method Not Allowed
	echo; echo "netlistsvg"
	cd $build/netlistsvg
	git pull
	nice npm install
	# not clear what the best way to install this is...
}

function do_ice40_viewer {
	echo; echo "ice40_viewer"
	cd $build/ice40_viewer
	git pull
	#./iceview_html.py -s firefox ../hdl/verilog/work/mza-test003.double-dabble.txt ../output.html
	# not clear what the best way to install this is...
}

function do_swapforth {
	echo; echo "swapforth"
	cd $build/swapforth
	git pull
	cd j1a/icestorm
	nice make -k -j$j
	if [ $? -ne 0 ]; then return; fi
}

declare udev_rulefile="/etc/udev/rules.d/53-lattice-ftdi.rules"
function check_udev_rule {
	if [ ! -e "$udev_rulefile" ]; then
		echo "ATTRS{idVendor}==\"0403\", ATTRS{idProduct}==\"6010\", MODE=\"0666\", GROUP=\"plugdev\", TAG+=\"uaccess\"" | sudo tee "$udev_rulefile"
		fix_permissions "$udev_rulefile"
	fi
	list_files "$udev_rulefile"
}

get_source_if_necessary
set +e
do_icestorm
do_arachne_pnr
#do_nextpnr
do_yosys
#do_icestudio
#do_yosys_plugins
#do_vhdl2vl
#do_netlistsvg
#do_ice40_viewer
#do_swapforth
set -e
echo
check_udev_rule 
echo
list_files /usr/local/bin/ice* /usr/local/share/icebox /usr/local/bin/arachne* /usr/local/share/arachne-pnr /usr/local/bin/yosys* /usr/local/share/yosys "$udev_rulefile" /usr/local/bin/vhd2vl /usr/local/share/yosys/plugins

# yosys -p "synth_ice40 -blif rot.blif" rot.v
# arachne-pnr -d 1k -p rot.pcf rot.blif -o rot.asc
# icepack rot.asc rot.bin
# iceprog rot.bin
# sudo iceprog rot.bin

# or use makefile posted here:
# https://raw.githubusercontent.com/mzandrew/bin/master/nofizbin/verilog-icestorm-arachnepnr-yosys.makefile

