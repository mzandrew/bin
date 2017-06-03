#!/bin/bash -e

# instructions taken/modified from an email from Kurtis N. dated 2016-12-16

declare dir="$HOME/build/geant4"
declare tdir="$dir"
if [ -e "/opt/shared/software/geant4" ]; then
	tdir="/opt/shared/software/geant4"
fi
declare deblist="build-essential mesa-utils mercurial"
declare rpmlist="mercurial"
	rpmlist="$rpmlist gcc gcc-c++ make automake autoconf"
declare CMAKE="cmake"
declare MAKE="make -j4"

# check http://geant4.cern.ch/support/download.shtml
declare geant_version_string_a="geant4.10.03.p01" # latest as of 2017-06-02
declare geant_version_string_b="Geant4-10.3.1" # install subdir name

# check https://cmake.org/files/v3.7/
declare cmake_version_string_a="cmake-3.8.2" # latest as of 2017-06-02
declare cmake_version_string_b="cmake-3.8" # install subdir name
declare cmake_version_string_c="v3.8" # download subdir name

# check proj-clhep.web.cern.ch/proj-clhep/clhep23.html
declare clhep_version_string_a="clhep-2.3.4.4" # latest as of 2017-06-02
declare clhep_version_string_b="2.3.4.4" # untar subdir name
declare clhep_version_string_c="CLHEP-2.3.4.4" # install subdir name

declare list_of_things_that_should_be_there_after_complete_installation="/usr/local/share/$geant_version_string_b /usr/local/lib/$geant_version_string_b /usr/local/include/Geant4 /usr/local/include/Inventor /usr/local/bin/soxt-config /usr/local/share/Coin /usr/local/lib/libSoXt.* /usr/local/lib/libCoin* /usr/local/include/CLHEP /usr/local/lib/$clhep_version_string_c /usr/local/doc/$cmake_version_string_b /usr/local/share/$cmake_version_string_b /usr/local/bin/cmake /usr/local/bin/ctest /usr/local/bin/cpack"

declare -i redhat=0 SL6=0 SL7=0 deb=0
if [ -e /etc/redhat-release ]; then
	redhat=1
	set +e
	SL6=$(grep -c "Scientific Linux release 6" /etc/redhat-release)
	SL7=$(grep -c "Scientific Linux release 7" /etc/redhat-release)
	set -e
elif [ -e /etc/debian_version ]; then
	deb=1
else
	echo "what kind of linux is this?"
	exit 1
fi

function show_all_files {
	ls -lart $list_of_things_that_should_be_there_after_complete_installation || /bin/true
}

function download_datasets {
	echo; echo "downloading datasets..."
	cd $dir
	for each in G4NDL.4.5.tar.gz G4EMLOW.6.50.tar.gz G4PhotonEvaporation.4.3.2.tar.gz G4RadioactiveDecay.5.1.1.tar.gz G4NEUTRONXS.1.4.tar.gz G4PII.1.3.tar.gz RealSurface.1.0.tar.gz G4SAIDDATA.1.1.tar.gz G4ABLA.3.0.tar.gz G4ENSDFSTATE.2.1.tar.gz; do
		if [ ! -e $each ]; then
			wget http://geant4.cern.ch/support/source/$each
		fi
	done
}

function install_dataset {
	cd /usr/local/share/$geant_version_string_b/data
	if [ ! -e "$1" ] && [ -e "$tdir/$2" ]; then
		echo "installing $1..."
		sudo tar xzf "$tdir/$2"
	fi
}

function install_datasets {
	echo; echo "installing datasets..."
	sudo mkdir -p /usr/local/share/$geant_version_string_b/data
	sudo chmod -R o+rx /usr/local/share/$geant_version_string_b
	#for each in G4NDL.4.5.tar.gz G4EMLOW.6.50.tar.gz G4PhotonEvaporation.4.3.2.tar.gz G4RadioactiveDecay.5.1.1.tar.gz G4NEUTRONXS.1.4.tar.gz G4PII.1.3.tar.gz RealSurface.1.0.tar.gz G4SAIDDATA.1.1.tar.gz G4ABLA.3.0.tar.gz G4ENSDFSTATE.2.1.tar.gz; do
	install_dataset G4ABLA3.0 G4ABLA.3.0.tar.gz
	install_dataset G4EMLOW6.50 G4EMLOW.6.50.tar.gz
	install_dataset G4ENSDFSTATE2.1 G4ENSDFSTATE.2.1.tar.gz
	install_dataset G4NDL4.5 G4NDL.4.5.tar.gz
	install_dataset G4NEUTRONXS1.4 G4NEUTRONXS.1.4.tar.gz
	install_dataset G4PII1.3 G4PII.1.3.tar.gz
	install_dataset G4SAIDDATA1.1 G4SAIDDATA.1.1.tar.gz
	install_dataset PhotonEvaporation4.3.2 G4PhotonEvaporation.4.3.2.tar.gz
	install_dataset RadioactiveDecay5.1.1 G4RadioactiveDecay.5.1.1.tar.gz
	install_dataset RealSurface1.0 RealSurface.1.0.tar.gz
	sudo chmod -R o+rx /usr/local/share/$geant_version_string_b/data
	ls -lart /usr/local/share/$geant_version_string_b/data
}

function build_and_install_cmake {
	echo; echo "cmake"
	cd $dir
	file="${cmake_version_string_a}.tar.gz"
	if [ ! -e $tdir/$file ]; then
		wget https://cmake.org/files/$cmake_version_string_c/$file
	fi
	if [ ! -e $cmake_version_string_a ]; then
		echo "extracting from $file..."
		tar xzf $file
	fi
	cd $cmake_version_string_a
	./configure
	$MAKE
	if [ $deb -gt 0 ]; then
		sudo apt -y purge cmake cmake-data
	else
		sudo yum -y erase cmake cmake-data
	fi
	sudo make install
	sudo chmod -R o+rx /usr/local/doc/$cmake_version_string_b /usr/local/share/$cmake_version_string_b /usr/local/bin/cmake /usr/local/bin/ctest /usr/local/bin/cpack /usr/local/doc/
	# "/opt/cmake/bin/cmake: cannot execute binary file: Exec format error" means you have the wrong binary downloaded; just do it from source (above)
}

deblist="$deblist qtdeclarative5-dev"
rpmlist="$rpmlist qt5-qtdeclarative-devel"
function build_and_install_clhep {
	echo; echo "clhep"
	file="${clhep_version_string_a}.tgz"
	if [ ! -e $tdir/$file ]; then
		cd $tdir
		wget http://proj-clhep.web.cern.ch/proj-clhep/DISTRIBUTION/tarFiles/$file
	fi
	cd $dir
	if [ ! -e $clhep_version_string_a ]; then
		echo "extracting from $file..."
		tar xzf $tdir/$file
		mv $clhep_version_string_b $clhep_version_string_a
	fi
	cd $dir/$clhep_version_string_a
	mkdir -p build
	cd build
	$CMAKE ../CLHEP
	$MAKE
	sudo make install
	sudo chmod -R o+rx /usr/local/include/CLHEP /usr/local/lib/$clhep_version_string_c
}

function build_and_install_coin {
	echo; echo "coin"
	cd $dir
	if [ ! -e coin ]; then
		if [ -e $tdir/coin.tar ]; then
			echo "extracting from coin..."
			tar xf $tdir/coin.tar
			cd $dir/coin
			hg pull
		else
			hg clone https://bitbucket.org/Coin3D/coin -r CMake
			tar cf $tdir/coin.tar coin
		fi
	fi
	cd $dir/coin
	mkdir -p build
	cd build
	$CMAKE ..
	$MAKE
	sudo make install
	sudo cp ../bin/coin-config /usr/local/bin/
	sudo chmod -R o+rx /usr/local/lib/Coin /usr/local/lib/libCoin*
}

deblist="$deblist dos2unix"
rpmlist="$rpmlist dos2unix"
function build_and_install_coinStandard {
	echo; echo "coinStandard"
	cd $dir
	if [ ! -e coinStandard ]; then
		if [ -e $tdir/coinStandard.tar ]; then
			echo "extracting from coinStandard..."
			tar xf $tdir/coinStandard.tar
			cd $dir/coinStandard
			hg pull
		else
			hg clone https://bitbucket.org/Coin3D/coin coinStandard
			tar cf $tdir/coinStandard.tar coinStandard
		fi
	fi
	cd $dir/coinStandard
	#make[4]: Entering directory '/home/mza/build/geant4/coinStandard/build/src/nodes'
	#Makefile:1157: .deps/SoAlphaTest.Plo: No such file or directory
	#make[4]: *** No rule to make target '.deps/all-nodes-cpp.Po'.  Stop.
	#make[1]: Leaving directory '/home/mza/build/geant4/coinStandard/build'
	#Makefile:1656: recipe for target 'all' failed
	#make: *** [all] Error 2
	# solution is found in post of Volker Enderlein here:
	# https://bitbucket.org/Coin3D/coin/issues/88/failed-installation-of-coin3d-and-soqt
	#find $dir/coinStandard -name "Makefile.*" -exec file {} \; | grep CRLF
	dos2unix -k $dir/coinStandard/src/nodes/Makefile.in
	dos2unix -k $dir/coinStandard/src/nodes/Makefile.am
	mkdir -p build
	cd build
	../configure
	$MAKE
	sudo make install
	sudo mkdir -p /usr/local/share/Coin/conf/
	sudo cp coin-default.cfg /usr/local/share/Coin/conf/
	sudo chmod -R o+rx /usr/local/share/Coin
}

deblist="$deblist libmotif-dev libxpm-dev"
rpmlist="$rpmlist motif-devel libXpm-devel"
function build_and_install_soxt {
	echo; echo "soxt"
	cd $dir
	if [ ! -e $dir/soxt ]; then
		if [ -e $tdir/soxt.tar ]; then
			echo "extracting from soxt.tar..."
			tar xf $tdir/soxt.tar
			cd $dir/soxt
			hg pull
		else
			hg clone https://bitbucket.org/Coin3D/soxt
			tar cf $tdir/soxt.tar soxt
		fi
	fi
	cd $dir/soxt
	mkdir -p build
	cd build
	export LD_RUN_PATH="/usr/local/lib/" # https://bitbucket.org/Coin3D/coin/issues/19/configure-error-could-not-determine-the
	../configure
	$MAKE
	sudo make install
	sudo chmod -R o+rx /usr/local/include/Inventor /usr/local/bin/soxt-config /usr/local/share/Coin/conf/soxt-default.cfg /usr/local/lib/libSoXt.*
}

deblist="$deblist libexpat1-dev libxmu-dev"
rpmlist="$rpmlist expat-devel libXmu-devel"
function build_and_install_geant {
	echo; echo "geant4"
	file="${geant_version_string_a}.tar.gz"
	if [ ! -e $tdir/$file ]; then
		cd $tdir
		wget http://geant4.web.cern.ch/geant4/support/source/$file
	fi
	cd $dir
	if [ ! -e $geant_version_string_a ]; then
		echo "extracting from $file..."
		tar xzf $tdir/$file
	fi
	cd $geant_version_string_a
	mkdir -p build
	cd build
	#export INVENTOR_SOXT_LIBRARY="/usr/local/lib/libSoXt.so"
	#$CMAKE .. -DGEANT4_USE_QT=ON -DGEANT4_USE_INVENTOR=ON -DGEANT4_BUILD_EXAMPLES=ON -DGEANT4_INSTALL_EXAMPLES=ON
	$CMAKE .. -DGEANT4_USE_QT=ON -DGEANT4_USE_INVENTOR=ON
	$MAKE
	sudo make install
	sudo chmod -R o+rx /usr/local/share/$geant_version_string_b /usr/local/lib/$geant_version_string_b
}

function build_and_run_example {
	echo; echo "example"
	cd $dir
	. /usr/local/share/$geant_version_string_b/geant4make/geant4make.sh
	if [ ! -e B1 ]; then
		cp -r /usr/local/share/$geant_version_string_b/examples/basic/B1 .
	fi
	cd B1
	mkdir -p build
	cd build
	$CMAKE ..
	$MAKE
	./exampleB1
}

function clean {
	cd $dir
	rm -rf $clhep_version_string_a/build coin/build coinStandard/build soxt/build $geant_version_string_a/build
}

function realclean {
	cd $dir
	rm -rf $clhep_version_string_a coin coinStandard soxt $geant_version_string_a B1 $cmake_version_string_a
}

function uninstall {
	echo; echo "uninstalling..."
	echo "before:"
	show_all_files
	for each in $clhep_version_string_a/build coin/build coinStandard/build soxt/build $geant_version_string_a/build $cmake_version_string_a; do
		echo "uninstalling $each..."
		if [ -e $dir/$each ]; then
			cd $dir/$each
			sudo make uninstall || echo "can't uninstall from $each"
		else
			echo "can't uninstall from $each"
		fi
	done
	echo "after regular uninstall:"
	show_all_files
}

function hard_uninstall {
	echo "before:"
	show_all_files
	sudo rm -rf $list_of_things_that_should_be_there_after_complete_installation
	echo "after hard uninstall:"
	show_all_files
}

function install_prerequisites {
	if [ $deb -gt 0 ]; then
		sudo apt -y install $deblist
	else
		sudo yum -y install $rpmlist
	fi
}

function uninstall_prerequisites {
	if [ $deb -gt 0 ]; then
		sudo apt -y remove $deblist
	else
		sudo yum -y erase $rpmlist
	fi
}

function install {
	build_and_install_cmake
	if [ ! -e /usr/local/bin/cmake ]; then
		deblist="$deblist $CMAKE"
		rpmlist="$rpmlist $CMAKE"
	fi
	install_prerequisites
	#download_datasets # do this just once and save the files
	install_datasets
	build_and_install_clhep
	build_and_install_coin
	build_and_install_coinStandard
	build_and_install_soxt
	build_and_install_geant
	#geant4.sh
}

if [ $# -gt 0 ]; then
	if [ "$1" = "uninstall" ]; then
		# useful in some situations:
		uninstall
		hard_uninstall
	elif [ "$1" = "uninstall_prerequisites" ]; then
		uninstall_prerequisites
	elif [ "$1" = "clean" ]; then
		clean
	elif [ "$1" = "realclean" ]; then
		realclean
	elif [ "$1" = "status" ]; then
		show_all_files
	elif [ "$1" = "example" ]; then
		# show that it worked:
		build_and_run_example
	else
		install
	fi
else
	install
fi

