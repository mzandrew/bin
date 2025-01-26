#!/bin/bash -e

# last updated 2025-01-17 by mza

declare filename="actions-taken-to-clean-up-files.txt"
declare action_file="-exec rm -fv {} ;"
declare action_dirtree="-exec rm -rfv {} ;"
declare action_emptyfile="-exec rm -fv {} ;"
declare action_emptydir="-exec rmdir -v {} ;"
declare -i verbosity=4

if [ ! -e lf-r.original ]; then
	if [ $verbosity -gt 3 ]; then echo; echo "lf-r.original"; fi
	lf > lf-r.original
fi
if [ ! -e du-ma1.original ]; then
	if [ $verbosity -gt 3 ]; then echo; echo "du-ma1.original"; fi
	dume
	mv du-ma1 du-ma1.original
fi

if [ $verbosity -gt 3 ]; then echo; echo "chmod u+rwx dirs"; fi
find -type d -exec chmod u+rwx --changes {} \; | tee -a ${filename}

if [ $verbosity -gt 3 ]; then echo; echo "superfluous files"; fi
find -type f -name "*rawdata.[0-9][0-9][0-9][0-9][0-9]" ${action_file} | tee -a ${filename}
find -type f -name "*rawdata.[0-9][0-9][0-9][0-9]" ${action_file} | tee -a ${filename}
find -type f -name "*.rawdata[0-9][0-9][0-9]" ${action_file} | tee -a ${filename}
find -type f -name "S*CH[0-9]" ${action_file} | tee -a ${filename}
find -type f -name "PHD_S*CH[0-9]" ${action_file} | tee -a ${filename}
find -type f -name "*.fiber[0-9]" ${action_file} | tee -a ${filename}
find -type f -name "*.hdf5" ${action_file} | tee -a ${filename}
find -type f -name "*.sroot" ${action_file} | tee -a ${filename}
find -type f -name "*.root" ${action_file} | tee -a ${filename}
find -type f -name "*.pcap" ${action_file} | tee -a ${filename}
find -type f -name "*.pyc" ${action_file} | tee -a ${filename}
find -type f -name "*.so" ${action_file} | tee -a ${filename}
find -type f -name "*.o" ${action_file} | tee -a ${filename}
find -type f -name "*.rawdata" ${action_file} | tee -a ${filename}
find -type f -name "*.log" ${action_file} | tee -a ${filename}
find -type f -name "*.jou" ${action_file} | tee -a ${filename}
find -type f -name "*.str" ${action_file} | tee -a ${filename}
find -type f -name "*.dat" ${action_file} | tee -a ${filename}
find -type f -name "*.camac" ${action_file} | tee -a ${filename}
find -type f -name "*.status" ${action_file} | tee -a ${filename}
find -type f -name "*~" ${action_file} | tee -a ${filename}
find -type f -name "*.bak" ${action_file} | tee -a ${filename}
find -type f -name "ccc[0-9]" ${action_file} | tee -a ${filename}
find -type f -name "ccc" ${action_file} | tee -a ${filename}
find -type f -name "aaa" ${action_file} | tee -a ${filename}
find -type f -name "*.restore" ${action_file} | tee -a ${filename}
find -type f -name "*.ise_ISE_Backup" ${action_file} | tee -a ${filename}
find -type f -name "*.mgf" ${action_file} | tee -a ${filename}
find -type f -name "*.dcp" ${action_file} | tee -a ${filename}
find -type f -name "*.txt.gz" ${action_file} | tee -a ${filename}
find -type f -name "*.xsvf" ${action_file} | tee -a ${filename}
find -type f -name "*.xmsgs" ${action_file} | tee -a ${filename}
find -type f -name "*.xrpt" ${action_file} | tee -a ${filename}
find -type f -name "*.vdbl" ${action_file} | tee -a ${filename}
find -type f -name "*.schbak" ${action_file} | tee -a ${filename}
find -type f -name "*.sch_bak" ${action_file} | tee -a ${filename}
find -type f -name "*.cmd_log" ${action_file} | tee -a ${filename}
find -type f -name "*.mac" ${action_file} | tee -a ${filename} # geant4
find -type f -name "*.edn" ${action_file} | tee -a ${filename}
find -type f -name "*.syr" ${action_file} | tee -a ${filename}
find -type f -name "*.twr" ${action_file} | tee -a ${filename}
find -type f -name "*.twx" ${action_file} | tee -a ${filename}
find -type f -name "*.wdb" ${action_file} | tee -a ${filename}
find -type f -name "*.ngo" ${action_file} | tee -a ${filename}
find -type f -name "*.vho" ${action_file} | tee -a ${filename}
find -type f -name "*.rbb" ${action_file} | tee -a ${filename}
find -type f -name "*.mrp" ${action_file} | tee -a ${filename}
find -type f -name "*.msd" ${action_file} | tee -a ${filename}
find -type f -name "*.rpx" ${action_file} | tee -a ${filename}
find -type f -name "*.rpt" ${action_file} | tee -a ${filename}
find -type f -name "*.rbd" ${action_file} | tee -a ${filename}
find -type f -name "*.ngc" ${action_file} | tee -a ${filename}
find -type f -name "*.ncd" ${action_file} | tee -a ${filename}
find -type f -name "*.ngd" ${action_file} | tee -a ${filename}
find -type f -name "*.ngr" ${action_file} | tee -a ${filename}
find -type f -name "*.ngm" ${action_file} | tee -a ${filename}
find -type f -name "*.bin" ${action_file} | tee -a ${filename}
find -type f -name "*.mcs" ${action_file} | tee -a ${filename}
find -type f -name "*.mcs.gz" ${action_file} | tee -a ${filename}
find -type f -name "*.bit" ${action_file} | tee -a ${filename}
find -type f -name "*.bit.gz" ${action_file} | tee -a ${filename}
find -type f -name "*.hdf" ${action_file} | tee -a ${filename}
find -type f -name "*.projectmgr" ${action_file} | tee -a ${filename}
find -type f -name "*.xbcd" ${action_file} | tee -a ${filename}
find -type f -name "*.svf" ${action_file} | tee -a ${filename}
find -type f -name "*.xreport" ${action_file} | tee -a ${filename}
find -type f -name "par_usage_statistics.html" ${action_file} | tee -a ${filename}
find -type f -name "*.xml" ${action_file} | tee -a ${filename}
find -type f -name "*.symbak" ${action_file} | tee -a ${filename}
find -type f -name "*.elf" ${action_file} | tee -a ${filename}
find -type f -name "*.exe.stackdump" ${action_file} | tee -a ${filename}
find -type f -name "*.dll" ${action_file} | tee -a ${filename}
find -type f -name "*.mui" ${action_file} | tee -a ${filename}
find -type f -name "*.msi" ${action_file} | tee -a ${filename}
find -type f -name "*.cab" ${action_file} | tee -a ${filename}
find -type f -name "*.lock" ${action_file} | tee -a ${filename}
find -type f -name "*.lnk" ${action_file} | tee -a ${filename}
find -type f -name "*.tmp" ${action_file} | tee -a ${filename}
find -type f -name "*.dvi" ${action_file} | tee -a ${filename}
find -type f -name "*.aux" ${action_file} | tee -a ${filename}
find -type f -name "*.obj" ${action_file} | tee -a ${filename}
find -type f -name "*.out1" ${action_file} | tee -a ${filename}
find -type f -name "*.vsd" ${action_file} | tee -a ${filename}
find -type f -name "*.ll" ${action_file} | tee -a ${filename}
find -type f -name "*.rep" ${action_file} | tee -a ${filename}
find -type f -name "*.prm" ${action_file} | tee -a ${filename}
find -type f -name "*.lst" ${action_file} | tee -a ${filename}
find -type f -name "*.dst" ${action_file} | tee -a ${filename}
find -type f -name "*.dst[0-9]" ${action_file} | tee -a ${filename}
find -type f -name "VBox.log.*" ${action_file} | tee -a ${filename}
find -type f -name "VBoxSVC.log.*" ${action_file} | tee -a ${filename}
find -type f -name "NTUSER.DAT*" ${action_file} | tee -a ${filename}
find -type f -name ".gtkrc*" ${action_file} | tee -a ${filename}
find -type f -name ".kderc*" ${action_file} | tee -a ${filename}
find -type f -name ".nvidia-settings-rc" ${action_file} | tee -a ${filename}
find -type f -name ".realplayerrc" ${action_file} | tee -a ${filename}
find -type f -name ".hxplayerrc" ${action_file} | tee -a ${filename}
find -type f -name ".dropbox" ${action_file} | tee -a ${filename}
find -type f -name ".xsession-errors*" ${action_file} | tee -a ${filename}
find -type f -name ".Xauthority" ${action_file} | tee -a ${filename}
find -type f -name ".ICEauthority" ${action_file} | tee -a ${filename}
find -type f -name ".viminfo" ${action_file} | tee -a ${filename}
find -type f -name ".flexlmrc" ${action_file} | tee -a ${filename}
find -type f -name ".lesshst" ${action_file} | tee -a ${filename}
find -type f -name ".recently-used.xbel" ${action_file} | tee -a ${filename}
find -type f -name ".RapidSVN" ${action_file} | tee -a ${filename}
find -type f -name ".xscreensaver*" ${action_file} | tee -a ${filename}
find -type f -name ".xauth*" ${action_file} | tee -a ${filename}
find -type f -name ".dmrc" ${action_file} | tee -a ${filename}
find -type f -name ".gtk-bookmarks" ${action_file} | tee -a ${filename}
find -type f -name ".esd_auth" ${action_file} | tee -a ${filename}
find -type f -name ".DS_Store" ${action_file} | tee -a ${filename}
find -type f -name ".openoffice*" ${action_file} | tee -a ${filename}
find -type f -name ".rhn-applet.conf" ${action_file} | tee -a ${filename}
find -type f -name ".mime-types" ${action_file} | tee -a ${filename}
find -type f -name ".recently-used" ${action_file} | tee -a ${filename}
find -type f -name "._*" ${action_file} | tee -a ${filename}

# occasionally these are useful to include or exclude on a case-by-case basis:
find -type f -name "*.exe" ${action_file} | tee -a ${filename}
#find -type f -name "*.pcf" ${action_file} | tee -a ${filename}
#find -type f -name "*.edif" ${action_file} | tee -a ${filename}
#find -type f -name "*.png" ${action_file} | tee -a ${filename} # this line may unintentionally delete useful stuff
#find -type f -name "*.txt" ${action_file} | tee -a ${filename} # this line may unintentionally delete useful stuff, including the file generated by this script...
#find -type f -name "*.csv" ${action_file} | tee -a ${filename} # this line may unintentionally delete useful stuff...
find -type f -wholename "*/coregen/*.pdf" ${action_file} | tee -a ${filename}
find -type f -wholename "*/simulations/*\.raw" ${action_file} | tee -a ${filename}

if [ $verbosity -gt 3 ]; then echo; echo "empty files"; fi
find -type f -empty ${action_emptyfile} | tee -a ${filename}

if [ $verbosity -gt 3 ]; then echo; echo "superfluous dirs"; fi
find -depth -type d -name ".fltk" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".simvision" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".adobe" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".local" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".metadata" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name "isim" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".gconf" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".gnome2" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".gnome2_private" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".evolution" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".Trash" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".Trash-*" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".Spotlight-V100" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".nx" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".pki" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".vim" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".rhn-applet" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".nautilus" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".gconfd" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".gstreamer*" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".kde" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".swt" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".dbus" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".java" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".ipython" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".fluxbox" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".fonts*" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".fontconfig" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".rootnb" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".config" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".cache" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".pulse" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".Xil" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".Xilinx" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".mozilla" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".cpan" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".gegl*" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".texmf-var" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".gimp*" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".gnome" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".opera" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".mcop" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".compiz" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".rhopenoffice*" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".openoffice*" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".icedteaplugin" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".update-notifier" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".irssi" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".qt" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".nbi" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".filezilla" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".putty" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".matlab" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".metacity" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".Skype" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".scim" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".sunpinyin" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".SeeVoghRN" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".install4j" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".netx" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".HDI" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".beagle" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".netbeans*" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".thumbnails" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".macromedia" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name "iCDB" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".Mathematica" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".wine" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".vscode-server" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".vscode" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".eclipse" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".VirtualBox" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name ".dropbox.cache" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name "Abisuite" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name "Application Data" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name "Temporary Internet Files" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name "\$Recycle\.Bin" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name "Cookies" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name "Solidworks Downloads" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name "impact_xdb" ${action_dirtree} | tee -a ${filename}
find -depth -type d -name "lowres" ${action_dirtree} | tee -a ${filename}
find -depth -type d -wholename "*/AppData/LocalLow" ${action_dirtree} | tee -a ${filename}
find -depth -type d -wholename "*/AppData/Local" ${action_dirtree} | tee -a ${filename}
find -depth -type d -wholename "*/Local Settings/Temp" ${action_dirtree} | tee -a ${filename}

# occasionally these are useful to include or exclude on a case-by-case basis:
find -depth -type d -wholename "*/AppData/Roaming" ${action_dirtree} | tee -a ${filename} # AppData/Thunderbird contains cached emails...
#find -depth -type d -name ".svn" ${action_dirtree} | tee -a ${filename} # this line may unintentionally delete useful stuff...
#find -depth -type d -name ".git" ${action_dirtree} | tee -a ${filename} # this line may unintentionally delete useful stuff...

if [ $verbosity -gt 3 ]; then echo; echo "duplicate files"; fi
echo
lf | duplicate_finder.py
./script_to_remove_all_duplicates_that_are_not_golden.sh

if [ $verbosity -gt 3 ]; then echo; echo "empty dirs"; fi
find -depth -type d -empty ${action_emptydir} | tee -a ${filename}

if [ $verbosity -gt 3 ]; then echo; echo "adjust timestamps of dirs"; fi
adjust_datestamps_of_dirs_based_on_their_contents

if [ $verbosity -gt 3 ]; then echo; echo "lf-r"; fi
lf > lf-r
if [ $verbosity -gt 3 ]; then echo; echo "du-ma1"; fi
dume

