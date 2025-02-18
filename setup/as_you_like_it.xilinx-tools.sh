#!/bin/bash

# written 2023 by mza
# last updated 2025-02-10 by mza

function install_prerequisites_apt {
	sudo nice apt -y install libtinfo6 libtinfo-dev
	cd /lib/x86_64-linux-gnu
	sudo ln -s libtinfo.so.6 libtinfo.so.5
}

install_prerequisites_apt

