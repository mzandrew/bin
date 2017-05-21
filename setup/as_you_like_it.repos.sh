#!/bin/bash -e

export url="https://www.phys.hawaii.edu/repos/belle2/itop/electronics"
cd
mkdir -p build
cd build
svn checkout $url uh-svn-repo

