#!/bin/bash -e

#sudo useradd mza
#sudo usermod mza -a -G sudo

sudo apt -y install vim vim-gtk
sudo apt -y install mlocate git subversion rsync build-essential
# sudo apt -y install virtualbox-guest-utils virtualbox-guest-x11 virtualbox-guest-dkms
sudo apt -y update
sudo apt -y upgrade

sudo apt -y install firefox

cd
mkdir -p build

#cd ~/build
#git clone https://github.com/mzandrew/bin.git

cd
mkdir -p bin

cd ~/bin
ln -s ../build/bin/generic

cat >> ~/.bashrc <<HERE
if [ -e $HOME/build/bin/nofizbin/bashrc ]; then
	. $HOME/build/bin/nofizbin/bashrc
fi
HERE

