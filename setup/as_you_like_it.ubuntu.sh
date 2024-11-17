#!/bin/bash -e

# last updated 2024-04-27 by mza

declare -i debian_only=0
#debian_only=1

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
	if [ ${debian_only} -eq 0 ]; then
		sudo add-apt-repository universe
		sudo add-apt-repository multiverse
	fi
	local list="vim git subversion rsync"
	install_packages_if_necessary $list
	list=""
	list="$list vim-gtk3"
	list="$list libcanberra-gtk-module libcanberra-gtk3-module" # to avoid annoying messages when starting gvim
	if [ ${debian_only} -eq 0 ]; then
		list="$list firefox"
	fi
	list="$list plocate build-essential openssh-server net-tools nfs-common"
	list="$list dfu-util gcc-arm-none-eabi libnewlib-arm-none-eabi libstdc++-arm-none-eabi-newlib" # tomu
	list="$list synaptic gnuplot ntp meld doublecmd-gtk zip unzip dbus-x11 gimp inkscape xsane"
	list="$list texlive-science texlive-latex-extra" # latex
	list="$list cups paps" # cups and utf-8 to postscript converter
	list="$list libgsl-dev" # root
	list="$list ffmpeg mplayer" # making/playing videos
	list="$list network-manager-openconnect-gnome" # for VPN
	list="$list tmux minicom"
	list="$list tigervnc-standalone-server tigervnc-viewer"
	#sudo apt -y install root-system # taken out of ubuntu 2018.04 (since 2016.04)
	install_packages_if_necessary $list
	sudo apt -y update
	sudo apt -y upgrade
	# sudo apt -y install virtualbox-guest-utils virtualbox-guest-x11 virtualbox-guest-dkms
	# xpdf no longer available in ubuntu 20.04
	sudo apt-get -y autoremove
	sudo apt-get -y clean
	#echo "consider running these to use the local apt mirror:"
	#echo "	sudo sed -i 's,us.archive.ubuntu.com,mirror.ancl.hawaii.edu/linux,' /etc/apt/sources.list"
	#echo "	sudo sed -i 's,archive.ubuntu.com,mirror.ancl.hawaii.edu/linux,' /etc/apt/sources.list"
	echo "add the following line to /etc/ntp.conf:"
	echo "	pool 192.168.153.1 iburst"
	echo "and to set the local timezone:"
	echo "	dpkg-reconfigure tzdata"
}

function change_apt_sources_list_if_desired {
	echo
	read -p "would you like to exchange us.archive.ubuntu.com with mirror.ancl.hawaii.edu in /etc/apt/sources.list ? (y/n) " -n1 -r
	echo
	if [[ $REPLY =~ ^[yY]$ ]]; then
		sudo sed -i 's,us.archive.ubuntu.com,mirror.ancl.hawaii.edu/linux,' /etc/apt/sources.list
	fi
}

# undo:
#sudo sed -i 's,mirror.ancl.hawaii.edu/linux,us.archive.ubuntu.com,' /etc/apt/sources.list

#change_apt_sources_list_if_desired
install_packages

cd
mkdir -p build

if [ ! -e ~/build/bin ];then
	cd ~/build
	git clone https://github.com/mzandrew/bin.git
fi

