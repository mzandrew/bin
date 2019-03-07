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

