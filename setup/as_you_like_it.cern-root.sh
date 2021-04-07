#!/bin/bash -e

# written 2019-06-27 by mza
# last updated 2021-04-06 by mza
# the build dir is about 3GB after the build

# when trying it on ubuntu 20.04:
# E: Package 'libpython-dev' has no installation candidate

declare filename="root_v6.22.00.source.tar.gz"
declare dirname="root-6.22.00"

declare -i j=2
declare -i np=$(grep -c "^processor" /proc/cpuinfo)
if [ $j -gt $np ] || [ -e /etc/rpi-issue ]; then
	j=1
	echo "dropping j to 1"
fi

declare -i MiB=1024

function add_swap_if_necessary {
	if [ ! -e /swap ]; then
		echo "generating $MiB MiB /swap file..."
		sudo dd if=/dev/zero of=/swap bs=$((1024*1024)) count=$MiB
		sudo chmod 600 /swap
		sudo mkswap /swap
		# this happens after the "exit 0" line, so is useless:
		#sudo sed -ie '/swapon/{h;s/.*/swapon \/swap/};${x;/^$/{s/.*/swapon \/swap/;H};x}' /etc/rc.local
		#echo "fix /etc/rc.local to do \"swapon /swap\" before the exit 0!"
	fi
	sudo swapon /swap || /bin/true
}

# https://root.cern.ch/build-prerequisites

function install_prerequisites_apt {
	#sudo nice apt -y install git dpkg-dev make g++ gcc binutils libx11-dev libxpm-dev libxft-dev libxext-dev python-dev gfortran libfftw3-dev libjpeg-dev libgif-dev libtiff-dev libcfitsio-dev libxml2-dev uuid-dev davix-dev libpythia8-dev libgfal2-dev libgl2ps-dev libpcre2-dev liblz4-dev libgsl-dev libssl-dev libgfal2-dev libtbb-dev gsl-bin libpython-dev
	#sudo nice apt -y install "cmake>=3.6"
	sudo nice apt -y install git dpkg-dev make g++ gcc binutils libx11-dev libxpm-dev libxft-dev libxext-dev python-dev python3-dev gfortran cmake libfftw3-dev libjpeg-dev libgif-dev libtiff-dev libcfitsio-dev libxml2-dev uuid-dev davix-dev libpythia8-dev libgfal2-dev libgl2ps-dev libpcre2-dev liblz4-dev libgsl-dev libssl-dev libgfal2-dev libtbb-dev gsl-bin libpython2.7-dev
	# libcblas-dev libcblas3
	# Enabled support for:  asimage astiff builtin_afterimage builtin_clang builtin_ftgl builtin_glew builtin_llvm builtin_tbb builtin_vdt builtin_xxhash clad cling cxx11 davix exceptions explicitlink fftw3 fitsio gdml http imt mathmore opengl pch pythia8 python roofit shared ssl thread tmva tmva-cpu tmva-pymva vdt x11 xft xml
}

function install_prerequisites_yum {
	sudo nice yum -y update
	sudo nice yum -y upgrade
	sudo nice yum -y install git cmake gcc-c++ gcc binutils libX11-devel libXpm-devel libXft-devel libXext-devel gcc-gfortran openssl-devel pcre-devel mesa-libGL-devel mesa-libGLU-devel glew-devel ftgl-devel mysql-devel fftw-devel cfitsio-devel graphviz-devel avahi-compat-libdns_sd-devel python-devel libxml2-devel
	# libldap-dev gsl-static
}

function install_prerequisites_pac {
	sudo pacman --needed --noconfirm -Syu
#	sudo pacman --needed --noconfirm -S
}

declare -i redhat=0 SL6=0 SL7=0 deb=0
if [ -e /etc/redhat-release ]; then
	redhat=1
	set +e
	SL6=$(grep -c "Scientific Linux release 6" /etc/redhat-release)
	SL7=$(grep -c "Scientific Linux release 7" /etc/redhat-release)
	set -e
elif [ -e /etc/debian_version ]; then
	deb=1
elif [ -e /etc/arch-release ]; then
	arch=1
else
	echo "what kind of linux is this?"
	exit 1
fi
if [ $deb -gt 0 ]; then
	install_prerequisites_apt
elif [ $redhat -gt 0 ]; then
	install_prerequisites_yum
elif [ $arch -gt 0 ]; then
	install_prerequisites_pac
fi

#add_swap_if_necessary
declare build="${HOME}/build"
cd
mkdir -p $build
cd $build

function build_and_install_cmake_from_source {
	sudo apt -y remove cmake cmake-data
	if [ ! -d "cmake" ]; then
		if [ ! -e "cmake-3.15.5.tar.gz" ]; then
			wget https://github.com/Kitware/CMake/releases/download/v3.15.5/cmake-3.15.5.tar.gz
		fi
		tar -xzf "cmake-3.15.5.tar.gz"
	fi
	cd "cmake-3.15.5"
	nice ./configure
	nice gmake
	sudo make install
	sudo chmod o+rx /usr/local/share/cmake-3.15
}

# this mostly uninstalls any old versions of cern root:
if [ -e /usr/local/bin/thisroot.sh ]; then
	echo "existing install of CERN ROOT found.  removing..."
	cd /usr/local/bin
	sudo mkdir -p junk
	for each in root* thisroot* setxrd* proofserv* memprobe rmkdepend genreflex xpdtest hadd hist2workspace; do
		if [ -e "$each" ]; then
			sudo mv $each junk/
		fi
	done
	sudo rm -rf junk
	#ls -lart
#fi
#sudo touch /usr/local/lib/ROOT.py
#if [ -e /usr/local/lib/ROOT.py ]; then
	cd /usr/local/lib
	sudo mkdir -p junk
	for each in ROOT.py* libROOT* libPyROOT* libVMC* libPyMVA* _pythonization* cppyy.py* cmdLineUtils* libCore* libThread* libRint* libJupyROOT* libImt* *.pcm *.rootmap cppyy_backend cppyy ROOT JupyROOT JsMVA libXrd* libFTGL* libCore* libCling* libNew* libcppyy_backend* libJupyROOT* libRint.so libcomplexDict.so libmap2Dict.so libforward_listDict.so libvectorDict.so libdequeDict.so libvalarrayDict.so libmultimap2Dict.so libmultimapDict.so liblistDict.so libsetDict.so libmultisetDict.so libunordered* libmapDict.so libThread.so libcppyy* libImt.so libRIO.so libNet.so libXMLParser.so libMathCore.so libROOTVecOps.so libXMLIO.so libROOTTPython.so libSrvAuth.so libMultiProc.so libFFTW.so libRootAuth.so libSQLIO.so libNetx.so libRDAVIX.so libNetxNG.so libGX11.so libMatrix.so libRCsg.so libMathMore.so libGenVector.so libTree.so libSmatrix.so libPhysics.so libQuadp.so libROOTPythonizations* libProof.so libHist.so libFoam.so libGraf.so libSpectrum.so libUnfold.so libGeom.so libPostscript.so libGX11TTF.so libRHTTP.so libASImage.so libGdml.so libHtml.so libMinuit.so libFumili.so libGpad.so libGraf3d.so libGui.so libHistPainter.so libSpectrumPainter.so libRHTTPSniff.so libFITSIO.so libASImageGui.so libX3d.so libEG.so libGuiBld.so libGuiHtml.so libRecorder.so libSessionViewer.so libGeomPainter.so libRooFitCore.so libEGPythia8.so libTreePlayer.so libGed.so libMLP.so libSPlot.so libRooFit.so libFitPanel.so libROOTDataFrame.so libProofPlayer.so libTreeViewer.so libRooFitMore.so libGeomBuilder.so libRooStats.so libRGL.so libProofDraw.so libProofBench.so libHistFactory.so libGviz3d.so libTMVA.so libGenetic.so libEve.so libTMVAGui.so; do
		if [ -e "$each" ]; then
			sudo mv $each junk/
		fi
	done
	sudo rm -rf junk
	#ls -lart
	echo "...done"
fi

if [ ! -e $build/$dirname ]; then
	if [ ! -e $filename ]; then
		declare url="https://root.cern/download/$filename"
		wget $url
	fi
	tar xzf $filename
fi
cd $build/$dirname
#if [ -e obj ]; then
#	rm -rf obj
#fi
if [ ! -e obj ]; then
	mkdir obj
	cd obj
	cmake ..
else
	cd obj
fi
time nice make -j$j
sudo nice make install
sudo find /usr/local/etc -type d -exec chmod --changes 755 {} \; -o -type f -exec chmod --changes 644 {} \;

cat <<DOC

to test your installation:

. /usr/local/bin/thisroot.sh
root
.q

python2
import ROOT
ctrl-d

python3
import ROOT
ctrl-d
DOC

