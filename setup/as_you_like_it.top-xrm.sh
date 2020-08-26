#!/bin/bash -e

# written 2020-01-15 by mza
# last updated 2020-07-23 by mza

# when trying it on ubuntu 20.04:
# E: Unable to locate package python-pip

function install_prerequisites_apt {
	#sudo nice apt -y update
	#sudo nice apt -y upgrade
	sudo nice apt -y install python2 python-pip-whl snmp libsmi2-common erlang-snmp bc python-tk
	# python-imaging-tk
}

function install_prerequisites_yum {
	sudo nice yum -y update
	sudo nice yum -y upgrade
	#sudo nice yum -y install libtool autoconf automake make gcc clang texinfo libusb libusb-devel libusb1 libusb1-devel libusbx libusbx-devel tcl-devel tcl pkgconfig libftdi wget
	#sudo nice yum -y install openocd # version is Open On-Chip Debugger 0.5.0 (2011-12-19-21:28) in SL6.10
	#sudo nice yum -y install openocd # version is Open On-Chip Debugger 0.8.0 (2014-04-29-12:22) in SL7.3 and SL7.5
	# for openocd-0.10.0 release tarball under redhat distros:
	# libusb-devel 0.1 needed to build ARM-OLIMEX-JTAG driver
	# libusb1-devel needed for SL6.10
	# libusbx-devel needed for SL7.5
	# ~2018 git version needs automake>=1.14 and SL7.3 only has 1.13 (SL7.6 has 1.13 also, grumble)
}

function install_prerequisites_pac {
	sudo pacman --needed --noconfirm -Syu
	#sudo pacman --needed --noconfirm -S libtool autoconf automake make gcc clang texinfo libusb tcl pkgconfig libftdi wget
}

declare -i redhat=0 SL6=0 SL7=0 deb=0
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
fi

declare build="${HOME}/build"

mkdir -p $build

declare string=$(which pip)
if [ -z "$string" ]; then
	cd $build
	# from https://linuxize.com/post/how-to-install-pip-on-ubuntu-20.04/
	if [ ! -e "get-pip.py" ]; then
		wget https://bootstrap.pypa.io/get-pip.py --output-document=get-pip.py
	fi
	sudo python2 get-pip.py
	pip2 install pytz
	pip2 install matplotlib # sudo apt install python3-matplotlib
fi

#  File "./xrm.py", line 2585, in xrm_run
#    for carrier in carriers_to_dejuice:
#UnboundLocalError: local variable 'carriers_to_dejuice' referenced before assignment

#    os.path.mkdir(subdir)
#AttributeError: 'module' object has no attribute 'mkdir'

#compile ../../fe/peddump

#    os.mkdir(dir)
#OSError: [Errno 2] No such file or directory: 'data/2020-01-16'

