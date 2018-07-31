#!/bin/bash -e

# instructions taken/modified from an email from Kurtis N. dated 2016-12-16

declare dir="$HOME/build/geant4"
declare tdir="$dir"
if [ -e "/opt/shared/software/geant4" ]; then
	tdir="/opt/shared/software/geant4"
fi
declare archlist="mesa glu mercurial dos2unix openmotif qt4"
declare deblist="build-essential mesa-utils mercurial"
declare rpmlist="mercurial"
	rpmlist="$rpmlist gcc gcc-c++ make automake autoconf"
declare CMAKE="cmake"
declare -i numcores=$(($(cat /proc/cpuinfo | grep '^processor' | tail -n1 | awk '{print $3}')+1))
declare MAKE="make -j$numcores"

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

declare list_of_things_that_should_be_there_after_complete_installation="
	/usr/local/include/Geant4
	/usr/local/include/Inventor
	/usr/local/include/CLHEP
	/usr/local/share/aclocal/cmake.m4
	/usr/local/share/aclocal/coin.m4
	/usr/local/share/aclocal/soxt.m4
	/usr/local/share/$geant_version_string_b
	/usr/local/share/$cmake_version_string_b
	/usr/local/share/Coin
	/usr/local/share/man/man1/coin-config.1
	/usr/local/share/man/man1/soxt-config.1
	/usr/local/lib/libSoXt.*
	/usr/local/lib/libCoin*
	/usr/local/lib/libCLHEP*
	/usr/local/lib/Coin
	/usr/local/lib/$clhep_version_string_c
	/usr/local/lib/libG4*
	/usr/local/lib/$geant_version_string_b 
	/usr/local/lib64/$geant_version_string_b 
	/usr/local/lib64/libG4*
	/usr/local/doc/$cmake_version_string_b
	/usr/local/bin/soxt-config
	/usr/local/bin/clhep-config
	/usr/local/bin/Vector-config
	/usr/local/bin/Utility-config
	/usr/local/bin/Units-config
	/usr/local/bin/RefCount-config
	/usr/local/bin/RandomObjects-config
	/usr/local/bin/Random-config
	/usr/local/bin/Matrix-config
	/usr/local/bin/Geometry-config
	/usr/local/bin/GenericFunctions-config
	/usr/local/bin/Exceptions-config
	/usr/local/bin/Evaluator-config
	/usr/local/bin/Cast-config
	/usr/local/bin/geant4.sh
	/usr/local/bin/geant4.csh
	/usr/local/bin/geant4-config
	/usr/local/bin/coin-config
	/usr/local/bin/cmake
	/usr/local/bin/ctest
	/usr/local/bin/cpack"

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

function fix_permissions {
	for each; do
		if [ -e "$each" ]; then
			sudo find "$each" -type d -exec chmod 755 --changes {} \+ -o -type f -exec chmod +r --changes {} \+
		fi
	done
}

function fix_ownership {
	for each; do
		if [ -e "$each" ]; then
			sudo chown -R --reference=$dir $each
		fi
	done
}

function show_all_installed_files {
	echo; echo "searching for installed files..."
	#ls -lart $list_of_things_that_should_be_there_after_complete_installation || /bin/true
	local REGULAR_FILE_STRING='%TY-%Tm-%Td+%TH:%TM %12s %p\n'
	local REGULAR_DIR_STRING='%TY-%Tm-%Td+%TH:%TM %12s %p/\n'
	local SYMLINK_STRING='%TY-%Tm-%Td+%TH:%TM %12s %p -> %l\n'
	local list=""
	for each in $list_of_things_that_should_be_there_after_complete_installation; do
		if [ -e "$each" ]; then
			list="$list $each"
		fi
	done
	if [ ! -z "$list" ]; then
		find $list \
			   -type d -printf "$REGULAR_DIR_STRING" \
			-o -type l -printf "$SYMLINK_STRING" \
			-o         -printf "$REGULAR_FILE_STRING" \
			| sort -k 1n,1 > $dir/geant4-and-friends.find
		du $list -s > $dir/geant4-and-friends.du
		wc $dir/geant4-and-friends.find | awk '{print $1" files installed"}'
	else
		echo "no installed files found"
		rm -f $dir/geant4-and-friends.find $dir/geant4-and-friends.du
	fi
}

function look_for_installed_files {
	# this function is mainly to test that we found everything that gets installed (when writing this script)
	sudo updatedb
	#cmake 
	#locate coin soxt geant g4 clhep | grep -v '^/home\|^/opt/Xilinx\|bitcoin\|g48\|mpeg4\|sg4\|g4[05]0\|docg4\|Dialog4\|dialog4\|config4\|geant3\|working4\|typing4\|pidgin\|pkg4\|g4_makedist\|dg460\|bash-completion' | sort > $dir/geant4-and-friends.locate
	show_all_installed_files
}

function download_datasets {
	echo; echo "downloading datasets..."
	cd $dir
	for each in G4NDL.4.5.tar.gz G4EMLOW.6.50.tar.gz G4PhotonEvaporation.4.3.2.tar.gz G4RadioactiveDecay.5.1.1.tar.gz G4NEUTRONXS.1.4.tar.gz G4PII.1.3.tar.gz RealSurface.1.0.tar.gz G4SAIDDATA.1.1.tar.gz G4ABLA.3.0.tar.gz G4ENSDFSTATE.2.1.tar.gz; do
	#for each in G4NDL.4.5.tar.gz; do
	#for each in G4ENSDFSTATE.2.1.tar.gz; do
		if [ ! -e $each ]; then
			wget http://geant4.cern.ch/support/source/$each
		fi
	done
}

function install_dataset {
	cd /usr/local/share/$geant_version_string_b/data
	if [ ! -e "$1" ] && [ -e "$tdir/$2" ]; then
		echo "installing $1..."
		#sudo tar xzf "$tdir/$2"
		cat "$tdir/$2" | sudo tar xz
		sudo chown -R root:root "$1"
	fi
}

function install_datasets {
	echo; echo "installing datasets..."
	sudo mkdir -p /usr/local/share/$geant_version_string_b/data
	fix_permissions /usr/local/share/$geant_version_string_b
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
	fix_permissions /usr/local/share/$geant_version_string_b/data
	ls -lart /usr/local/share/$geant_version_string_b/data
}

function build_and_install_cmake {
	echo; echo "cmake"
	cd $dir
	file="${cmake_version_string_a}.tar.gz"
	if [ ! -e $tdir/$file ]; then
		cd $tdir
		wget https://cmake.org/files/$cmake_version_string_c/$file
	fi
	if [ ! -e $cmake_version_string_a ]; then
		echo "extracting from $file..."
		tar xzf $tdir/$file
	fi
	cd $cmake_version_string_a
	if [ ! -e Makefile ]; then
		./configure
	else
		echo "cmake already configured"
	fi
	if [ ! -e Source/libCMakeLib.a ] || [ ! -e bin/cmake ] || [ ! -e bin/ctest ]; then
		$MAKE
	else
		echo "cmake already built"
	fi
	if [ $deb -gt 0 ]; then
		sudo apt -y purge cmake cmake-data
	elif [ $arch -gt 0 ]; then
		:
	else
		sudo yum -y erase cmake cmake-data
	fi
	if [ ! -e /usr/local/bin/cmake ]; then
		sudo make install --quiet --no-print-directory
	else
		echo "cmake already installed"
	fi
	fix_ownership install_manifest.txt CMakeFiles/uninstall.dir/depend.make CMakeFiles/uninstall.dir/depend.internal
	fix_permissions /usr/local/doc/$cmake_version_string_b /usr/local/share/$cmake_version_string_b /usr/local/bin/cmake /usr/local/bin/ctest /usr/local/bin/cpack /usr/local/doc/ /usr/local/share/aclocal /usr/local/share/aclocal/cmake.m4
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
		tar xf $tdir/$file
		mv $clhep_version_string_b $clhep_version_string_a
	fi
	cd $dir/$clhep_version_string_a
	mkdir -p build
	cd build
	if [ ! -e Makefile ]; then
		$CMAKE ../CLHEP
	else
		echo "clhep already cmake'd"
	fi
	if [ ! -e lib/lib${clhep_version_string_c}.so ] || [ ! -e Random/test/testInstanceRestore ]; then
		$MAKE
	else
		echo "clhep already built"
	fi
	if [ ! -e /usr/local/lib/libCLHEP.so ]; then
		sudo make install --quiet --no-print-directory
	else
		echo "clhep already installed"
	fi
	fix_ownership install_manifest.txt
	fix_permissions /usr/local/include/CLHEP /usr/local/lib/$clhep_version_string_c
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
	if [ ! -e Makefile ]; then
		$CMAKE ..
	else
		echo "coin already cmake'd"
	fi
	if [ ! -e src/libCoin.so ]; then
		$MAKE
	else
		echo "coin already built"
	fi
	if [ ! -e /usr/local/lib/libCoin.so ]; then
		sudo make install --quiet --no-print-directory
	else
		echo "coin already installed"
	fi
	fix_ownership install_manifest.txt
	sudo cp ../bin/coin-config /usr/local/bin/
	fix_permissions /usr/local/lib/Coin /usr/local/lib/libCoin*
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
	if [ ! -e Makefile ]; then
		../configure
	else
		echo "coinStandard already configured"
	fi
	if [ ! -e src/libCoin.la ]; then
		$MAKE
	else
		echo "coinStandard already built"
	fi
	if [ ! -e /usr/local/lib/libCoin.la ]; then
		sudo make install --quiet --no-print-directory
	else
		echo "coinStandard already installed"
	fi
	sudo mkdir -p /usr/local/share/Coin/conf/
	sudo cp coin-default.cfg /usr/local/share/Coin/conf/
	fix_ownership .
	#$src/libCoin.la src/navigation/SoScXMLNavigation.lo src/navigation/libnavigation.la src/navigation/.deps/SoScXMLNavigation.Plo src/navigation/.libs/SoScXMLNavigation.o src/navigation/.libs/libnavigation.a src/navigation/.libs/libnavigation.la src/.libs/libCoin.so.80.0.0 src/.libs/libCoin.so.80 src/.libs/libCoin.so src/.libs/libCoin.lai src/.libs/libCoin.la
	fix_permissions /usr/local/share/Coin /usr/local/share/aclocal/coin.m4
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
	if [ ! -e Makefile ]; then
		../configure
	else
		echo "soxt already configured"
	fi
	if [ ! -e soxt-config ] || [ ! -e src/Inventor/Xt/libSoXt.la ]; then
		$MAKE
	else
		echo "soxt already built"
	fi
	if [ ! -e /usr/local/bin/soxt-config ]; then
		sudo make install --quiet --no-print-directory
	else
		echo "soxt already installed"
	fi
	fix_ownership .
	fix_permissions /usr/local/include/Inventor /usr/local/bin/soxt-config /usr/local/share/Coin/conf/soxt-default.cfg /usr/local/lib/libSoXt.* /usr/local/share/aclocal/soxt.m4
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
	if [ ! -e Makefile ]; then
		$CMAKE .. -DGEANT4_USE_QT=ON -DGEANT4_USE_INVENTOR=ON
	else
		echo "geant4 already cmake'd"
	fi
	if [ ! -e source/physics_lists/CMakeFiles/G4physicslists.dir/lists/src/G4PhysListRegistry.cc.o ] || [ ! -e source/visualization/OpenInventor/CMakeFiles/G4OpenInventor.dir/src/G4OpenInventorXtExtended.cc.o ] || [ ! -e BuildProducts/lib64/libG4OpenGL.so ]; then
		$MAKE
	else
		echo "geant4 already built"
	fi
	if [ ! -e /usr/local/bin/geant4.sh ] || [ ! -e /usr/local/bin/geant4-config ]; then
		sudo make install --quiet --no-print-directory
	else
		echo "geant4 already installed"
	fi
	fix_ownership .
	fix_permissions /usr/local/share/$geant_version_string_b
	fix_permissions /usr/local/lib64
	if [ -e /usr/local/lib/$geant_version_string_b ]; then
		fix_permissions /usr/local/lib/$geant_version_string_b
	elif [ -e /usr/local/lib64/$geant_version_string_b ]; then
		fix_permissions /usr/local/lib64/$geant_version_string_b
	fi
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
	#echo "before:"
	#show_all_installed_files
	for each in $clhep_version_string_a/build coin/build coinStandard/build soxt/build $geant_version_string_a/build $cmake_version_string_a; do
		echo "uninstalling $each..."
		if [ -e $dir/$each ]; then
			cd $dir/$each
			sudo make uninstall || echo "can't uninstall from $each"
		else
			echo "can't uninstall from $each"
		fi
	done
	echo "uninstall done"
	#echo "after regular uninstall:"
	#show_all_installed_files
	look_for_installed_files
	echo "try \"$0 hard_uninstall\" if that didn't uninstall everything"
}

function hard_uninstall {
	echo; echo "hard uninstalling..."
	#echo "before:"
	#show_all_installed_files
	sudo rm -rf $list_of_things_that_should_be_there_after_complete_installation
	echo "hard uninstall done"
	#echo "after hard uninstall:"
	#show_all_installed_files
	look_for_installed_files
}

function install_prerequisites {
	if [ $deb -gt 0 ]; then
		sudo apt -y install $deblist
	elif [ $arch -gt 0 ]; then
		sudo pacman --needed --noconfirm -S $archlist
	else
		sudo yum -y install $rpmlist
	fi
}

function uninstall_prerequisites {
	if [ $deb -gt 0 ]; then
		sudo apt -y remove $deblist
	elif [ $arch -gt 0 ]; then
		:
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
	look_for_installed_files
}

mkdir -p $dir

if [ $# -gt 0 ]; then
	if [ "$1" = "install" ]; then
		install
	elif [ "$1" = "uninstall" ]; then
		# useful in some situations:
		uninstall
	elif [ "$1" = "hard_uninstall" ]; then
		hard_uninstall
	elif [ "$1" = "uninstall_prerequisites" ]; then
		uninstall_prerequisites
	elif [ "$1" = "clean" ]; then
		clean
	elif [ "$1" = "realclean" ]; then
		realclean
	elif [ "$1" = "status" ]; then
		show_all_installed_files
	elif [ "$1" = "example" ]; then
		# show that it worked:
		build_and_run_example
	else
		echo "unknown directive $1"
		exit 1
	fi
else
	install
fi

