#!/bin/bash -e

function install_packages {
	sudo apt -y install vim vim-gtk firefox
	sudo apt -y install mlocate git subversion rsync build-essential
	sudo apt -y update
	sudo apt -y upgrade
# sudo apt -y install virtualbox-guest-utils virtualbox-guest-x11 virtualbox-guest-dkms
	sudo apt autoremove
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
ln -s ../build/bin/generic
ln -s ../build/bin/setup
ln -s ../build/bin/repo
ln -s ../build/bin/physics

cat >> ~/.bashrc <<HERE
if [ -e $HOME/build/bin/nofizbin/bashrc ]; then
	. $HOME/build/bin/nofizbin/bashrc
fi
HERE

