#!/bin/bash -e

function install_packages {
	sudo apt -y install vim vim-gtk firefox
	sudo apt -y install mlocate git subversion rsync build-essential
	sudo apt -y update
	sudo apt -y upgrade
# sudo apt -y install virtualbox-guest-utils virtualbox-guest-x11 virtualbox-guest-dkms
	sudo apt-get autoremove
	sudo apt-get clean
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

