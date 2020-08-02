#!/bin/bash -e

# written 2019-06-27 by mza
# last updated 2020-07-19 by mza
# the build dir is about 3GB after the build

# when trying it on ubuntu 20.04:
# E: Package 'libpython-dev' has no installation candidate

declare filename="root_v6.16.00.source.tar.gz"
declare dirname="root-6.16.00"

declare -i j=2
declare -i np=$(grep -c "^processor" /proc/cpuinfo)
if [ $j -gt $np ] || [ -e /etc/rpi-issue ]; then
	j=1
	echo "dropping j to 1"
fi

declare -i MiB=1024

function add_swap_if_necessary {
	if [ ! -e /swap ]; then
		echo "generating $MiB MiB /swap file..."
		sudo dd if=/dev/zero of=/swap bs=$((1024*1024)) count=$MiB
		sudo chmod 600 /swap
		sudo mkswap /swap
		# this happens after the "exit 0" line, so is useless:
		#sudo sed -ie '/swapon/{h;s/.*/swapon \/swap/};${x;/^$/{s/.*/swapon \/swap/;H};x}' /etc/rc.local
		#echo "fix /etc/rc.local to do \"swapon /swap\" before the exit 0!"
	fi
	sudo swapon /swap || /bin/true
}

function install_prerequisites_apt {
	sudo nice apt -y install git dpkg-dev make g++ gcc binutils libx11-dev libxpm-dev libxft-dev libxext-dev python-dev gfortran cmake libfftw3-dev libjpeg-dev libgif-dev libtiff-dev libcfitsio-dev libxml2-dev uuid-dev davix-dev libpythia8-dev libgfal2-dev libgl2ps-dev libpcre2-dev liblz4-dev libgsl-dev libssl-dev libgfal2-dev libtbb-dev gsl-bin libpython2.7-dev
	# libcblas-dev libcblas3
	# Enabled support for:  asimage astiff builtin_afterimage builtin_clang builtin_ftgl builtin_glew builtin_llvm builtin_tbb builtin_vdt builtin_xxhash clad cling cxx11 davix exceptions explicitlink fftw3 fitsio gdml http imt mathmore opengl pch pythia8 python roofit shared ssl thread tmva tmva-cpu tmva-pymva vdt x11 xft xml
}

function install_prerequisites_yum {
	sudo nice yum -y update
	sudo nice yum -y upgrade
#	sudo nice yum -y install
}

function install_prerequisites_pac {
	sudo pacman --needed --noconfirm -Syu
#	sudo pacman --needed --noconfirm -S
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

#add_swap_if_necessary
declare build="${HOME}/build"
cd
mkdir -p $build
cd $build
if [ ! -e $build/$dirname ]; then
	if [ ! -e $filename ]; then
		declare url="https://root.cern/download/$filename"
		wget $url
	fi
	tar xzf $filename
fi
cd $build/$dirname
#if [ -e obj ]; then
#	rm -rf obj
#fi
if [ ! -e obj ]; then
	mkdir obj
	cd obj
	cmake ..
else
	cd obj
fi
time nice make -j$j
sudo nice make install
sudo find /usr/local/etc -type d -exec chmod --changes 755 {} \; -o -type f -exec chmod --changes 644 {} \;

