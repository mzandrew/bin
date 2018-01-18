#!/bin/bash -e

cd /
ln -s /cygdrive/c/mza/

cd
ln -s /mza/build/

if [ ! -e ~/build/apt-cyg ];then
	cd ~/build
	git clone https://github.com/ilatypov/apt-cyg.git
	cd ~/build/apt-cyg
	install apt-cyg /bin
fi

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
ln -s ../build/bin/cygwin

cat >> ~/.bashrc <<HERE

if [ -e $HOME/build/bin/nofizbin/bashrc ]; then
	. $HOME/build/bin/nofizbin/bashrc
fi

HERE

python2 -m ensurepip

apt-cyg install rsync openssh gvim subversion git xinit inkscape xterm

