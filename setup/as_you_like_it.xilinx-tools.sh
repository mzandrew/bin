#!/bin/bash

# written 2023 by mza
# last updated 2023-03-08 by mza

function install_prerequisites_apt {
	sudo nice apt -y install libtinfo6 libtinfo5 libtinfo-dev
}

install_prerequisites_apt

