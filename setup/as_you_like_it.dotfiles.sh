#!/bin/bash -e

declare source="$HOME/build/bin/nofizbin"
cd

if [ ! -e tmp ]; then
	mkdir tmp
fi

if [ ! -e .vimrc ]; then
	ln -s $source/.vimrc
fi

if [ ! -e .tmux.conf ]; then
	ln -s $source/.tmux.conf
fi

cd
mkdir -p bin

cd ~/bin
if [ ! -e generic ]; then ln -s ../build/bin/generic; fi
if [ ! -e setup   ]; then ln -s ../build/bin/setup; fi
if [ ! -e repo    ]; then ln -s ../build/bin/repo; fi
if [ ! -e physics ]; then ln -s ../build/bin/physics; fi

if [ ! -e ~/.bashrc ]; then
	touch ~/.bashrc
fi
declare -i count=$(grep -c nofizbin ~/.bashrc)
if [ $count -lt 1 ]; then
cat >> ~/.bashrc <<HERE

if [ -e $HOME/build/bin/nofizbin/bashrc ]; then
	. $HOME/build/bin/nofizbin/bashrc
fi

HERE
fi

