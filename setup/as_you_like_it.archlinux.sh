#!/bin/bash -e

cd
mkdir -p build # for development

cd
cd build
git clone https://github.com/mzandrew/bin.git

cd
mkdir -p bin
cd bin
ln -s ../build/bin/generic

cd
cat >> .bashrc <<HERE
if [ -e $HOME/build/bin/nofizbin/bashrc ]; then
	. $HOME/build/bin/nofizbin/bashrc
fi
HERE

cd
mkdir -p tmp # for vim swap files

cd
ln -s build/bin/nofizbin/.vimrc

which git 2>&1 > /dev/null
if [ $? -eq 0 ]; then
	git config --global user.name mzandrew
	echo "git config --global user.email blah@org"
	#git config --global push.default simple
fi

#sudo pacman --noconfirm -Qyyu
sudo pacman --noconfirm -S gvim firefox imagemagick git openssh rsync subversion wget zip mlocate gpm xterm

