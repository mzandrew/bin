#!/bin/bash -e

# last updated 2020-05-25 by mza

declare package_list_file=""
function make_dpkg_list_if_necessary {
	if [ -z "$package_list_file" ]; then
		package_list_file=$(mktemp)
		LC_ALL=C dpkg --list | awk '{print $2}' > $package_list_file
	fi
}
function check_dpkg {
	# idea stolen from https://gist.github.com/ungureanuvladvictor/9735941
	#LC_ALL=C dpkg --list | awk '{print $2}' | grep "^${pkg}" >/dev/null || deb_pkgs="${deb_pkgs}${pkg} "
	grep "^${pkg}" $package_list_file >/dev/null || deb_pkgs="${deb_pkgs}${pkg} "
}

function install_packages_if_necessary {
	#echo "before: $list"
	unset deb_pkgs
	make_dpkg_list_if_necessary
	for pkg in $list; do
		check_dpkg
	done
	#echo "after: $deb_pkgs"
	if [ "$deb_pkgs" ]; then
		sudo apt-get -y install $deb_pkgs
	fi
}

function install_packages {
	sudo add-apt-repository universe
	sudo add-apt-repository multiverse
	local list="vim git subversion rsync"
	install_packages_if_necessary $list
	list=""
	list="$list vim-gtk3"
	list="$list libcanberra-gtk-module libcanberra-gtk3-module" # to avoid annoying messages when starting gvim
	list="$list firefox"
	list="$list mlocate build-essential openssh-server net-tools nfs-common"
	list="$list dfu-util gcc-arm-none-eabi libnewlib-arm-none-eabi libstdc++-arm-none-eabi-newlib" # tomu
	list="$list synaptic gnuplot ntp meld doublecmd-gtk zip unzip dbus-x11 gimp inkscape xsane"
	list="$list texlive-science" # latex
	list="$list libgsl-dev" # root
	list="$list ffmpeg mplayer" # making/playing videos
	list="$list network-manager-openconnect-gnome" # for VPN
	list="$list tmux"
	#sudo apt -y install root-system # taken out of ubuntu 2018.04 (since 2016.04)
	install_packages_if_necessary $list
	sudo apt -y update
	sudo apt -y upgrade
	# sudo apt -y install virtualbox-guest-utils virtualbox-guest-x11 virtualbox-guest-dkms
	# xpdf no longer available in ubuntu 20.04
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

