#!/bin/bash -e

function install_packages {
	sudo add-apt-repository universe
	sudo add-apt-repository multiverse
	sudo apt -y install vim vim-gtk3 firefox
	sudo apt -y install mlocate git rsync build-essential openssh-server net-tools nfs-common
	sudo apt -y install dfu-util gcc-arm-none-eabi libnewlib-arm-none-eabi libstdc++-arm-none-eabi-newlib # tomu
	sudo apt -y install subversion synaptic gnuplot ntp meld doublecmd-gtk zip unzip dbus-x11 xpdf gimp inkscape sane
	#sudo apt -y install root-system # taken out of ubuntu 2018.04 (since 2016.04)
	sudo apt -y update
	sudo apt -y upgrade
	# sudo apt -y install virtualbox-guest-utils virtualbox-guest-x11 virtualbox-guest-dkms
	sudo apt-get -y autoremove
	sudo apt-get -y clean
	echo "consider running these to use the local apt mirror:"
	echo "	sudo sed -i 's,us.archive.ubuntu.com,mirror.ancl.hawaii.edu/linux,' /etc/apt/sources.list"
	echo "	sudo sed -i 's,archive.ubuntu.com,mirror.ancl.hawaii.edu/linux,' /etc/apt/sources.list"
	echo "add the following line to /etc/ntp.conf:"
	echo "	pool 192.168.153.1 iburst"
	echo "and to set the local timezone:"
	echo "	dpkg-reconfigure tzdata"
}

install_packages

cd
mkdir -p build

if [ ! -e ~/build/bin ];then
	cd ~/build
	git clone https://github.com/mzandrew/bin.git
fi

cd
mkdir -p bin

cd ~/bin
if [ ! -e generic ]; then ln -s ../build/bin/generic; fi
if [ ! -e setup   ]; then ln -s ../build/bin/setup; fi
if [ ! -e repo    ]; then ln -s ../build/bin/repo; fi
if [ ! -e physics ]; then ln -s ../build/bin/physics; fi

cat >> ~/.bashrc <<HERE

if [ -e $HOME/build/bin/nofizbin/bashrc ]; then
	. $HOME/build/bin/nofizbin/bashrc
fi

HERE

