#!/bin/bash -e

declare bashrc=$(readlink -f "$(dirname $0)/../nofizbin/bashrc")
. $bashrc

cd
mkdir -p build
cd build

export url="https://www.phys.hawaii.edu/repos/belle2/itop/electronics"
interactive "svn checkout $url uh-svn-repo" "checkout UH svn repo"

# personal:
interactive "git clone https://github.com/mzandrew/jabberwocky-oscilloscope.git"
interactive "git clone https://github.com/mzandrew/opengallery.git"
interactive "git clone https://github.com/mzandrew/arm7-oled-clock.git"

# work:
interactive "git clone https://github.com/mzandrew/idlab-scrod.git"
interactive "git clone https://github.com/mzandrew/idlab-daq.git"
interactive "git clone https://github.com/mzandrew/idlab-general.git"
interactive "git clone https://github.com/mzandrew/idlab-hardware.git"
interactive "git clone https://github.com/mzandrew/perl_motor_controller.git"

#both:
interactive "git clone https://github.com/mzandrew/bin.git"

