#!/bin/bash -e

# last updated 2025-02-02 by mza

declare filename="actions-taken-to-clean-up-files"
declare action_file="-exec rm -fv {} ;"
declare action_emptyfile="-exec rm -fv {} ;"
declare action_emptydir="-exec rmdir -v {} ;"
declare -i verbosity=4
declare extracts="extracts"

function find_type_f_iname {
	tarfile="${extracts}/${1}"
	shift
	for spec; do
		echo "${tarfile} ${spec}"
		find -type f -iname "${spec}" -print0 | tar rvf "${tarfile}" --remove-files --null -T - | tee -a ${filename}
	done
}

function find_type_d_iname {
	tarfile="${extracts}/${1}"
	shift
	for spec; do
		echo "${tarfile} ${spec}"
		find -type d -iname "${spec}" -print0 | tar rvf "${tarfile}" --remove-files --null -T - | tee -a ${filename}
	done
}

if [ -e "${filename}.txt" ]; then
	if [ -e "${filename}" ]; then
		cat "${filename}.txt" >> "${filename}" && rm "${filename}.txt"
	else
		mv "${filename}.txt" "${filename}"
	fi
fi
mkdir -p "${extracts}"
declare -i wclf_old
declare -i du_old

function initial_lfr {
	if [ ! -e lf-r.original ]; then
		if [ $verbosity -gt 3 ]; then echo; echo "lf-r.original"; fi
		lf > lf-r.original
		wclf_old=$(cat lf-r.original | wc --lines)
	else
		if [ $verbosity -gt 3 ]; then echo; echo "lf-r"; fi
		lf > lf-r
		wclf_old=$(cat lf-r | wc --lines)
	fi
}

function initial_duma {
	if [ ! -e du-ma1.original ]; then
		if [ $verbosity -gt 3 ]; then echo; echo "du-ma1.original"; fi
		dume
		mv du-ma1 du-ma1.original
		du_old=$(cat du-ma1.original | tail -n1 | awk -e '{ print $1 }')
	else
		if [ $verbosity -gt 3 ]; then echo; echo "du --ma=0"; fi
		du_old=$(du --ma=0 --block-size=1000000 | awk -e '{ print $1 }')
	fi
}

function chmod_dirs {
	if [ $verbosity -gt 3 ]; then echo; echo "chmod u+rwx dirs"; fi
	find -type d -exec chmod u+rwx --changes {} \; | tee -a ${filename}
}

function sockets {
	if [ $verbosity -gt 3 ]; then echo; echo "sockets"; fi
	find -type s -exec rm -v "{}" \; | tee -a ${filename}
}

function links {
	if [ $verbosity -gt 3 ]; then echo; echo "links"; fi
	find -type l -exec rm -v "{}" \; | tee -a ${filename}
}

#if [ $verbosity -gt 3 ]; then echo; echo "junk dirs and files"; fi
function junk {
	find_type_d_iname junk.tar ".Trash*"
	find_type_f_iname junk.tar "*.swp" "*.tmp" "*~" "*.bak" "*.so" "*.o" "*.sys" "*.schbak" "*.sch_bak" "*.symbak" "*.edn" "*.lock" "*.lnk" "*.cls" "*.dvi" "*.aux" "*.obj" "*.out1" "*.vsd" "*.ll" "*.rep" "*.prm" "*.lst" "ntuser.dat*" "*.pcap" "*.pyc" "*.exe.stackdump" ".DS_Store" "desktop.ini" "hiberfil.sys" "pagefile.sys" "*.m3u" "*.ovpn" "*.filepart" "*.edata"
	find_type_f_iname other.tar "*.wdb" "*.itdb" "*.plist" "*.itl" "*.ithmb"
find_type_f_iname data.tar "*.data" "*.root" "*.sroot" "*.rawdata" "*.dat" "*.hdf5" "*.usb0" "*rawdata.[0-9][0-9][0-9][0-9][0-9]" "*rawdata.[0-9][0-9][0-9][0-9]" "*.rawdata[0-9][0-9][0-9]" "S*CH[0-9]" "PHD_S*CH[0-9]" "*.fiber[0-9]" "*.camac" "*.cmc" "ccc[0-9]" "ccc" "aaa" "*.dst" "*.dst[0-9]" "*.datafile" "*.spl" "*.prn" "*.wxform" "*.ped"
	find_type_f_iname executable.tar "*.dll" "*.aps" "*.ncb" "*.sbr" "*.idb" "*.xpm" "*.res" "*.icon" "*.ico" "*.hex"
	find_type_f_iname installers.tar "*.mui" "*.msi" "*.cab" "*.deb" "*.rpm" "*.ex_" "*.dl_" "*.tt_" "*.sc_" "*.os_" "*.gp_" "*.cn_" "*.si_" "*.th_" "*.h2_" "*.tx_" "*.xd_" "*.co_" "*.xs_" "*.xm_" "*.js_" "*.vb_" "*.ht_" "*.mi_" "*.in_" "*.gi_" "*.mo_" "*.ta_" "*.ax_" "*.op_" "*.oc_" "*.lo_" "*.pn_" "*.ma_" "*.wp_" "*.bm_" "*.as_" "*.tb_" "*.lx_" "*.mb_" "*.fo_" "*.hl_" "*.wa_" "*.nl_" "*.tc_" "*.jp_" "*.ac_" "*.le_" "*.ca_" "*.ic_" "*.ms_" "*.wm_" "*.sy_" "*.im_" "*.sw_" "*.di_" "*.ch_" "*.bundle" "*AppImage" "*.manpages" "*.lic" "*.octave_packages"
	find_type_f_iname log.tar "*.log" "*.jou" "*.status" "VBox.log.*" "VBoxSVC.log.*" "*.out"
	find_type_d_iname firmware-build.tar "__projnav" "xst" "_ngo[0-9]" "impl_1"
	find_type_f_iname firmware-build.tar "*.vf" "*.xwv" "*.srp" "*.ndf" "*.ref" "*.str" "*.ise_ISE_Backup" "*.restore" "*.mgf" "*.dcp" "*.xsvf" "*.svf" "*.xmsgs" "*.xrpt" "*.vdbl" "*.syr" "*.twr" "*.twx" "*.wdb" "*.ngo" "*.vho" "*.mrp" "*.msd" "*.rpx" "*.rpt" "*.rbd" "*.rbb" "*.ngc" "*.ngd" "*.ncd" "*.ngr" "*.ngm" "*.mcs" "*.mcs.gz" "*.bit" "*.bit.gz" "*.hdf" "*.projectmgr" "*.xbcd" "*.xreport" "par_usage_statistics.html" "*.cmd_log" "*.elf" "*.blc" "*.bld" "*.unroutes" "*.par" "*.bgn" "*.map" "*.drc" "*.cdc" "*.xdl" "*.asdb" "*.cgc" "*.cpj" "*.psr" "*.do" "*.glade" "*_flist.txt" "*_readme.txt" "*_pad.txt" "*.ptwx" "*.ut" "*.tsi" "*.cgp" "*.scr" "*.key" "*_xmdf.tcl" "*.asy" "*.summary.html" "*.envsettings.html" "*.tcl" "*.pad_txt" "*.xst" "_impact.cmd" "*.sig"
	find_type_f_iname matlab.tar "*.mat" "*.m" "*.asv"
	find_type_f_iname geant.tar "*.mac"
	find_type_f_iname multiple.tar "*.bin" "*.xml"
	find_type_f_iname dotfiles.tar ".gtkrc*" ".kderc*" ".nvidia-settings-rc" ".realplayerrc" ".hxplayerrc" ".dropbox" ".xsession-errors*" ".Xauthority" ".ICEauthority" ".viminfo" ".flexlmrc" ".lesshst" ".recently-used.xbel" ".RapidSVN" ".xscreensaver*" ".xauth*" ".dmrc" ".gtk-bookmarks" ".esd_auth" ".openoffice*" ".rhn-applet.conf" ".mime-types" ".recently-used" "._*"
	find_type_d_iname OS.tar "Windows" "Program Files" "Program Files (x86)" "ProgramData" "Boot" "System Volume Information" "lost+found"
	find_type_d_iname executable.tar "MentorGraphics" "PAD_ES_Evaluation" "MSOCache" "teamviewer" "AlmytaSystems" "Anaconda3"
	find_type_d_iname dotfiles.tar ".fltk" ".simvision" ".adobe" ".local" ".metadata" ".gconf" ".gnome2" ".gnome2_private" ".evolution" ".Spotlight-V100" ".nx" ".pki" ".vim" ".rhn-applet" ".nautilus" ".gconfd" ".gstreamer*" ".kde" ".swt" ".dbus" ".java" ".ipython" ".fluxbox" ".fonts*" ".fontconfig" ".rootnb" ".config" ".cache" ".pulse"
	find_type_d_iname dotfiles.tar ".Xil" ".Xilinx" ".mozilla" ".cpan" ".gegl*" ".texmf-var" ".gimp*" ".gnome" ".opera" ".mcop" ".compiz" ".rhopenoffice*" ".openoffice*" ".icedteaplugin" ".update-notifier" ".irssi" ".qt" ".nbi" ".filezilla" ".putty" ".matlab" ".metacity" ".Skype" ".scim" ".sunpinyin"
	find_type_d_iname dotfiles.tar ".SeeVoghRN" ".install4j" ".netx" ".HDI" ".beagle" ".netbeans*" ".thumbnails" ".macromedia" ".Mathematica" ".wine" ".vscode-server" ".vscode" ".eclipse" ".VirtualBox" ".dropbox.cache"
	find_type_d_iname dotfiles.tar "*.anydesk" "*.astropy" "*.gitkraken" "*.hplip" "*.jupyter" "*.nano" "*.remmina" "*.virtualenvs"
	find_type_d_iname dotfiles.tar ".chipscope" ".eZuceSRN" ".SeeVogh" ".ezwave" ".iscape" ".oracle*" "Old Firefox Data"
	find_type_d_iname other.tar "isim" "impact_xdb" "iCDB" "Abisuite" "Application Data" "Temporary Internet Files" "Cookies" "Solidworks Downloads" "lowres" "\$Recycle\.Bin"
	find_type_d_iname appdata.tar "appdata" # AppData/Thunderbird contains cached emails...
	find_type_d_iname junk.tar "Local Settings"
	find_type_d_iname installers.tar ".yast2" "Modelsim_install"
	find_type_d_iname pcb-output.tar "gerber"
	find_type_f_iname pcb-output.tar "*.gerber" "*.g2" "*.gko" "*.gto" "*.gbo" "*.gtl" "*.gbl" "*.gts" "*.gbs" "*.gpt" "*.gbc" "*.gbk" "*.gtp" "*.gbp" "*.g2l" "*.g3l" "*.g4" "*.g4l" "*.g5l" "*.g6l" "*.g7l" "*.gbr" "*.gdo" "*.gtc" "*.gtk" "*.gbm" "*.gtm" "*.art" "*.gc2" "*.gc3" "*.gc4" "*.gc5" "*.gc6" "*.gc7" "*.gc8" "*.gc9" "*.gwk" "*.tx[0-9]" "*.tx1[0-9]" "*.drl" "*.prjpcbstructure" "*.ldp" "*.pcbdocpreview"
	# occasionally these are useful to include or exclude on a case-by-case basis:
	find_type_f_iname executable.tar "*.exe"
	find_type_f_iname firmware-build.tar "*.pcf"
	find_type_f_iname junk.tar "*.psm"
	find -type f -wholename "*/coregen/*.pdf" ${action_file} | tee -a ${filename}
	find -type f -wholename "*/simulations/*\.raw" ${action_file} | tee -a ${filename}
	find_type_f_iname java.tar "*.java"
	find_type_f_iname pde.tar "*.pde"
	find_type_f_iname svu.tar "*.svu"
	find_type_f_iname net.tar "*.net"
}

function empty_files {
	if [ $verbosity -gt 3 ]; then echo; echo "empty files"; fi
	find -type f -empty ${action_emptyfile} | tee -a ${filename}
}

function long_tail {
	find_type_f_iname long-tail.tar "*.mui_*" "*.dll_*" "*.exe_*" "*.*_loc" "*._lcr" "*._prj" "*._sprj"
	find_type_f_iname long-tail.09.tar "*.0nv" "*.10mar" "*.11" "*.11013" "*.117087" "*.14227" "*.1672" "*.17050" "*.1st" "*.20768" "*.22240" "*.24499" "*.26" "*.26974" "*.27076" "*.29235" "*.31528" "*.32sunu" "*.3gp" "*.44665" "*.5766" "*.59" "*.64" "*.64sunu" "*.670" "*.8" "*.849c9593-d756-4e56-8d6e-42412f2a707b" "*.9" "*.3" "*.6" "*.7" "*.0" "*.1" "*.2" "*.4" "*.5"
	find_type_f_iname long-tail.a.tar "*.abl" "*.abt" "*.acorn" "*.adf" "*.ael" "*.aff" "*.aifc" "*.aix" "*.aix5" "*.alc" "*.alias" "*.alien" "*.alphacxx6" "*.amiga" "*.ano" "*.ap" "*.api_description" "*.app" "*.asa" "*.asd" "*.ashx" "*.assuralastrun" "*.atari" "*.atf" "*.att" "*.aws" "*.acd" "*.acm" "*.adb" "*.adm" "*.adml" "*.admx" "*.adr" "*.ads" "*.afm" "*.ai" "*.ali" "*.amx" "*.ani" "*.ax"
	find_type_f_iname long-tail.b.tar "*.b32" "*.bas" "*.bash_profile" "*.batch" "*.bc32" "*.belle" "*.beos" "*.bkl" "*.bkmanifest" "*.bkpcc" "*.bl-ceem-075_0" "*.bl-ceem-075_1" "*.bl-ceem-075_2" "*.bl-ceem-075_3" "*.bl-ceem-075_4" "*.bl-ceem-075_5" "*.bl-ceem-075_6" "*.blg" "*.bof" "*.bor" "*.box" "*.boxl" "*.brk" "*.browser" "*.bsb" "*.bst" "*.bxml" "*.bat" "*.bcc" "*.bcm" "*.bkg" "*.bpl" "*.btr"
	find_type_f_iname long-tail.c.tar "*.c2" "*.c32" "*.cache*" "*.camp" "*.ccl" "*.cd" "*.cdf" "*.cdslck" "*.cdtproject" "*.cfi" "*.cgd" "*.cip" "*.cli" "*.clips" "*.clx" "*.cmake" "*.cmp" "*.cmrk" "*.cnf" "*.cnt" "*.code" "*.col" "*.com" "*.conn" "*.copyright" "*.cpl_b6a1dbdc" "*.cproj" "*.cps" "*.cpx" "*.crc" "*.crl" "*.csb" "*.csd" "*.csf" "*.cshrc_bes" "*.csm" "*.csproj" "*.cst" "*.csv#" "*.ctr" "*.cty" "*.ctypes" "*.cur" "*.cvcounter" "*.cvsignore" "*.cyfx" "*.cbz" "*.cdf-ms" "*.cel" "*.chq" "*.cmf" "*.cnv" "*.cpa" "*.crt" "*.csa"
	find_type_f_iname long-tail.d.tar "*.darwin" "*.dat%" "*.db-shm" "*.dbc" "*.dbk" "*.dds" "*.def" "*.defs" "*.den" "*.dep" "*.dependencies" "*.dev2" "*.df2" "*.dfa" "*.dff" "*.dft" "*.diag" "*.diagpkg" "*.dictionary" "*.diff" "*.dim" "*.din" "*.directory" "*.dirs" "*.diz" "*.dj2" "*.dlt" "*.dnv" "*.dot" "*.down" "*.dox" "*.dproj" "*.drk" "*.dru" "*.dsk" "*.dun" "*.dvc" "*.dwl" "*.dat#" "*.dcm" "*.ddd" "*.dectest" "*.deu" "*.devhelp2" "*.dmc" "*.dml" "*.dmo" "*.dms" "*.drv" "*.dtx" "*.dvg" "*.dvr-ms"
	find_type_f_iname long-tail.e.tar "*.edm" "*.edp" "*.eld" "*.eldo53" "*.elm" "*.emacs" "*.emf" "*.emz" "*.end" "*.eng" "*.er" "*.erc" "*.erf" "*.erl" "*.erx" "*.esn" "*.etd" "*.eterm" "*.evt" "*.ex" "*.example" "*.examples" "*.exports" "*.ext" "*.ext2" "*.efi" "*.eml" "*.emn" "*.enu" "*.eps#" "*.exsd"
	find_type_f_iname long-tail.f.tar "*.fc" "*.fdo" "*.fdt" "*.fdx" "*.filter" "*.filters" "*.fish" "*.flt" "*.flw" "*.fnc" "*.fnm" "*.fon_09ec4cfe" "*.fon_2c83a12b" "*.fon_2e7bdf2f" "*.fon_6087927d" "*.fonts" "*.footer" "*.forward" "*.fra" "*.freebsd" "*.freebsd4" "*.frq" "*.frx" "*.fs" "*.fsc" "*.fsub" "*.fdf" "*.fits" "*.fmwr" "*.fon" "*.form"
	find_type_f_iname long-tail.g.tar "*.g" "*.g4m" "*.g95" "*.geom" "*.gmmp" "*.gnome" "*.gnuplot_history" "*.gp" "*.gpg" "*.gplt" "*.gtkw" "*.guess" "*.gvp" "*.g1" "*.gcc" "*.gdt" "*.gid" "*.gir" "*.grc" "*.grd"
	find_type_f_iname long-tail.h.tar "*.h1c" "*.h1k" "*.h1t" "*.h2m" "*.hdlsourcefiles" "*.hdr" "*.header" "*.hgignore" "*.hhp" "*.hi" "*.hif" "*.his" "*.hist" "*.history" "*.hit" "*.hp700" "*.hpgcc" "*.hpj" "*.hpreview" "*.hpu" "*.hpux" "*.hpuxacc" "*.hpuxia64acc" "*.hst" "*.htaccess" "*.hwmdat" "*.hwmop" "*.hx1" "*.hdx" "*.heic" "*.hkp" "*.hwdef" "*.hwh" "*.hxx" "*.hyp"
	find_type_f_iname long-tail.i.tar "*.ibmc" "*.ic0" "*.ics" "*.icw" "*.ident" "*.ifx" "*.ihh" "*.ilc" "*.iml" "*.index" "*.info-1" "*.info-2" "*.info-3" "*.info-4" "*.init-script" "*.inpfiles" "*.inputrc" "*.ins" "*.install" "*.intel" "*.ipc" "*.ipv6" "*.ipx" "*.isim_lau_prj" "*.isp" "*.ita" "*.itb" "*.itcl" "*.itf" "*.ith" "*.ix" "*.idf" "*.if2" "*.ifd" "*.ime" "*.ind" "*.inx" "*.itk"
	find_type_f_iname long-tail.j.tar "*.jid" "*.jnlp" "*.job" "*.jpf" "*.jshintrc" "*.jrs" "*.jsonlz4"
	find_type_f_iname long-tail.k.tar "*.kdelnk" "*.knr" "*.konsole" "*.kumacold"
	find_type_f_iname long-tail.l.tar "*.lai" "*.layer" "*.layerprf" "*.lci" "*.lck" "*.lcvdplfile" "*.ld07" "*.ldb" "*.ldf" "*.ldo" "*.lds" "*.len" "*.ler" "*.library-ms" "*.libs" "*.lib~conc_intfc_lib" "*.lib~ft2u_lib" "*.lib~klm_scrod_tb" "*.lib~tdc_fifo_lib" "*.lib~tdc_lib" "*.lib~time_order_lib" "*.linux8664gcc" "*.linuxalphagcc" "*.linuxia64ecc" "*.linuxia64gcc" "*.linuxicc" "*.linuxkcc" "*.linuxx8664icc" "*.lk" "*.lnn" "*.lnp" "*.lnt" "*.lnx" "*.lnx8664" "*.loaded_0" "*.loaded_2" "*.loc" "*.loop" "*.lpc" "*.lpr" "*.lrs" "*.lso" "*.ltx" "*.lan" "*.less" "*.lex" "*.lgc" "*.lhp" "*.lis" "*.lng" "*.ltl" "*.lxa" "*.lyt"
	find_type_f_iname long-tail.m.tar "*.m2b" "*.m3u" "*.ma" "*.macosx64" "*.macosxicc" "*.macosxxlc" "*.macro" "*.main" "*.man" "*.mappings" "*.marks" "*.master" "*.mcr" "*.md1" "*.md5" "*.md5sum" "*.mem" "*.metadata" "*.metadata-v2" "*.mfd" "*.mgl" "*.mhs" "*.min" "*.minitel12-80" "*.mips" "*.mkr" "*.ml" "*.mllr" "*.mm" "*.mnl" "*.monalisa" "*.mos" "*.mpp" "*.mrxvt" "*.mta" "*.m4" "*.mfl" "*.mine" "*.mjs" "*.mof" "*.msc" "*.msg" "*.msstyles" "*.mst" "*.mum"
	find_type_f_iname long-tail.n.tar "*.ncm" "*.ne12bsd" "*.netbsd" "*.nga" "*.nht" "*.nky" "*.nlf" "*.npz" "*.nrc" "*.nrm" "*.nroff" "*.nsh" "*.nsi" "*.nuand" "*.null" "*.num" "*.nap" "*.nld" "*.nlp" "*.nlt" "*.ntf"
	find_type_f_iname long-tail.o.tar "*.oat" "*.octave_hist" "*.odl" "*.oem" "*.oga" "*.ogv" "*.omf" "*.op" "*.openbsd" "*.options" "*.orig" "*.os" "*.otf" "*.outjob" "*.overrides" "*.ocx_38c869db" "*.old"
	find_type_f_iname long-tail.p.tar "*.pac" "*.panel" "*.pao" "*.pas" "*.patches" "*.pbxproj" "*.pch++" "*.pchmm" "*.pcm" "*.pd07" "*.pdr" "*.pdx" "*.pe" "*.pedsub_calcfd" "*.pedsub_hits" "*.pex2" "*.pf" "*.pfx" "*.pif" "*.pjh" "*.planner" "*.plc" "*.pll" "*.plo" "*.pls" "*.pol" "*.policy" "*.pop" "*.post" "*.pot" "*.ppc" "*.ppk" "*.ppr" "*.prefs" "*.prerm" "*.preun" "*.pri" "*.profile" "*.properties" "*.prx" "*.ps1" "*.psg" "*.ptf" "*.pts" "*.pulse-cookie" "*.pyf" "*.pyw" "*.pages" "*.pd4" "*.pedsub_hitscfd" "*.pem" "*.pfa" "*.pfb" "*.pkginfo" "*.pm" "*.pptm" "*.psd" "*.pt07" "*.pyd"
	find_type_f_iname long-tail.q.tar "*.qbo" "*.qfx" "*.qip"
	find_type_f_iname long-tail.r.tar "*.r506" "*.r507" "*.rat" "*.rc2" "*.rcx_cmd" "*.rdp" "*.rdsn" "*.rec" "*.repl" "*.rj45" "*.rle" "*.rlg" "*.rnc" "*.rnd" "*.rndm" "*.rootdaemonrc" "*.rs6000" "*.rs64" "*.rsa" "*.rsf" "*.rules" "*.run" "*.rwsp" "*.rxvt" "*.r" "*.r53657" "*.r53921" "*.r54265" "*.regtrans-ms" "*.resources" "*.rom" "*.rootmap" "*.rpo"
	find_type_f_iname long-tail.s.tar "*.s2p" "*.s3p" "*.s4p" "*.s5p" "*.sam" "*.save" "*.sb" "*.scat" "*.scc" "*.scf" "*.scheme" "*.scm" "*.sco" "*.scp" "*.scs" "*.scv" "*.sdbl" "*.sdbx" "*.sdc" "*.sdkproject" "*.search-ms" "*.searchconnector-ms" "*.sed" "*.sep" "*.service" "*.set" "*.settings" "*.setup_spartan3" "*.setup_spartan3e" "*.setup_virtex2" "*.setup_virtex2p" "*.sf2" "*.sggcc" "*.sgicc" "*.sgrd" "*.shl" "*.sid" "*.simnetlistrunfile" "*.sin" "*.size" "*.skin" "*.skp" "*.sm" "*.smhist" "*.snn" "*.so9" "*.sobecons" "*.solariscc5" "*.spi" "*.sr" "*.src" "*.srn" "*.ss5" "*.ss5v9" "*.st0" "*.state" "*.std" "*.stm" "*.storagerecordindex" "*.strm" "*.stuff" "*.stx" "*.sub" "*.subst" "*.sunos" "*.sunos5" "*.sunos5v9" "*.sva" "*.sve" "*.svi" "*.sw0" "*.symcmd" "*.symlog" "*.sysdef" "*.sysk" "*.syx" "*.sch_1" "*.schdot" "*.sdf" "*.sdo" "*.shx" "*.sql"
	find_type_f_iname long-tail.t.tar "*.tab" "*.tag" "*.targets" "*.tbc" "*.tbr" "*.tc3" "*.tch" "*.tech" "*.terms" "*.testing_plots_forgaryanderic" "*.tf" "*.tfd" "*.tfi" "*.tfl" "*.tft" "*.thd" "*.theming" "*.thmx" "*.thumbnailer" "*.ti" "*.tii" "*.tim" "*.timing" "*.tis" "*.tlm" "*.tm" "*.tmml" "*.toc" "*.tool" "*.top" "*.tpr" "*.trace" "*.trans" "*.translations" "*.translators" "*.transr" "*.trm" "*.trn" "*.tsp" "*.tsstr" "*.tvl" "*.txf" "*.tcc" "*.texi" "*.tfm" "*.tlb" "*.tui"
	find_type_f_iname long-tail.u.tar "*.u8" "*.udo" "*.ufl" "*.uninstall" "*.up" "*.upgrade_log" "*.user" "*.ui" "*.upd"
	find_type_f_iname long-tail.v.tar "*.v20140221-1700" "*.v2cc" "*.va" "*.vala" "*.var" "*.vars" "*.vbp" "*.vbproj" "*.vbs" "*.vbw" "*.vcawin32" "*.vcwin32" "*.ver" "*.version" "*.versionsbackup" "*.vis" "*.vlogifrc" "*.vlr" "*.vpi" "*.vwp" "*.vc" "*.vch" "*.vdf" "*.vp"
	find_type_f_iname long-tail.w.tar "*.watcom" "*.wdm" "*.wdo" "*.wdr" "*.webm" "*.wiki" "*.win" "*.windows" "*.wlf" "*.woff2" "*.wpc" "*.wpd" "*.wsw" "*.wxe" "*.wxl" "*.wat" "*.whl" "*.wma" "*.wmf" "*.wsp"
	find_type_f_iname long-tail.x.tar "*.xa" "*.xaml" "*.xbap" "*.xcf" "*.xcn" "*.xdj" "*.xds" "*.xfigrc" "*.xil_info" "*.xinetd" "*.xld" "*.xlsm" "*.xlt" "*.xltx" "*.xmp" "*.xps" "*.xrf" "*.xrm-ms_690f532f" "*.xsd" "*.xslt" "*.xterm-new" "*.xul" "*.xwbt" "*.xx" "*.xy" "*.xda" "*.xpd" "*.xraw" "*.xrm-ms" "*.xsl" "*.xtd"
	find_type_f_iname long-tail.y.tar "*.yml"
	find_type_f_iname long-tail.z.tar "*.zzz"
	find_type_f_iname long-tail.100MB.tar "*.am" "*.asc" "*.axy" "*.bfd" "*.bre" "*.cam" "*.cat" "*.chm" "*.cio" "*.cpl" "*.css" "*.cxt" "*.db-wal" "*.dcs" "*.dic" "*.did" "*.dlm" "*.dly" "*.dmp" "*.dra" "*.drklog" "*.dsn" "*.dsp" "*.easm" "*.el" "*.elc" "*.enc" "*.epsi" "*.etl" "*.fst" "*.gpd" "*.h1s" "*.hbk" "*.hepevt" "*.hlp" "*.hlt" "*.ibs" "*.icc" "*.icm" "*.idx" "*.igs" "*.ilk" "*.imd" "*.in" "*.inf" "*.info" "*.ini" "*.isu" "*.js" "*.jsa" "*.ldz" "*.llb" "*.lrc" "*.lzp" "*.manifest" "*.max" "*.mcm" "*.mdb" "*.mnf" "*.mo" "*.msk" "*.nls" "*.ntp" "*.ocx" "*.odg" "*.ou" "*.pak" "*.part" "*.pb" "*.pdb" "*.peddiff" "*.pho" "*.pkg" "*.pnf" "*.po" "*.ppd" "*.prp" "*.pyo" "*.qtx" "*.rbf" "*.rm" "*.schdocpreview" "*.sd0" "*.sd1" "*.sd2" "*.spd" "*.swf" "*.tbl" "*.tga" "*.ts" "*.ttc" "*.txt#" "*.upi" "*.vcd" "*.vcp" "*.vdb" "*.vds" "*.vhf" "*.wfm" "*.wld" "*.xci" "*.xfd" "*.xtda"
	find_type_f_iname long-tail.1000MB.tar "*.medium" "*.sel" "*.xcix" "*.apkg" "*.db" "*.psnup" "*.edf" "*.bsd" "*.olb" "*.exp" "*.z" "*.pch" "*.dev" "*.lna" "*.tsdat" "*.sdb" "*.edb" "*.grf" "*.nph" "*.tdo" "*.a"
}

function svn_git {
	# occasionally these are useful to include or exclude on a case-by-case basis:
	find_type_d_iname svn.tar ".svn" "*.svn-work" # this line may unintentionally grab useful stuff...
	find_type_d_iname git.tar ".git" ".gitignore" "*.gitconfig" ".gitattributes" # this line may unintentionally grab useful stuff...
}

function duplicate_finder {
	if [ $verbosity -gt 3 ]; then echo; echo "duplicate files"; fi
	echo
	lf | duplicate_finder.py
	./script_to_remove_all_duplicates_that_are_not_golden.sh
}

function keepers {
	find_type_d_iname asic.tar "CustomIC"
	find_type_f_iname asic.tar "*.spc" "*.sp" "*.vdo" "*.vdb" "*.tdb" "*.tdo" "*.edif" "*.tsdat" "*.tsmeas" "*.tsim" "*.tsdb" "*.wmf" "*.tanner" "*.gds" "*.gds2" "*.lvs" "*.drc" "*.layout" "*.oalib" "*.citi" "*.oa" "*.oa-" "*.dm" "netlist" "map" "control" "*.template"
	find_type_d_iname asic.tar "graph_shared"
	#find_type_f_iname asic.tar "*.txt" "*.pdf" "*.pptx" "*.png" "*.xls" # this will grab too much unrelated stuff...
	find_type_f_iname PDK.tar "*.pl" "*.l" "*.sav" "*.il" "*.inc" "*.cfg" "*.zap"
	find_type_f_iname pcb.tar "*.d" "*.pcbdoc" "*.schdoc" "*.schlib" "*.sch" "*.pcb" "*.pcblib" "*.kicad_pcb" "*.kicad_sch" "*.brd" "*.ln9" "*.ld9" "*.pt9" "*.pd9" "*.prjpcb"
	find_type_f_iname mechanical.tar "*.sldprt" "*.sldasm" "*.dxf" "*.dwg" "*.stp" "*.step" "*.stl" "*.slddrw" "*.iges"
	find_type_f_iname firmware.tar "*.vhd" "*.vhdl" "*.vh" "*.v" "*.sv" "*.ucf" "*.xdc" "*.xco" "*.ise" "*.xise" "*.gise" "*.bd" "*.xpr" "*.wcfg" "*.mk" "*.gfl" "*.dhp" "*.ipf" "*.pad" "*.pl" "*.tpl" "*.eco" "*.xpi" "*.prj" "*.vm6" "*.jed" "*.sym"
	find_type_f_iname source.tar "*.c" "*.cc" "*.cpp" "*.cxx" "*.c++" "*.h" "*.hh" "*.hpp" "*.hxx" "*.h++" "*.class" "*.py" "*.pm" "*.sh" "*.s" "*.asm" "*.jar" "*.s" "*.p" "*.rst" "*.ino" "*.sh" "*.csh"
	find_type_f_iname presentations.tar "*.odp" "*.ppt" "*.pptx" "*.ps" "*.eps" "*.fig" "*.svg"
	find_type_f_iname documents.tar "*.xls" "*.xlsx" "*.doc" "*.docx" "*.tex"
	find_type_f_iname google-docs.tar "*.gdoc" "*.gslides" "*.gsheet"
	find_type_f_iname kek-firmware.tar "*.hsprogs" "*.bitfiles"
	find_type_d_iname kek-firmware.tar "ft2u" "b2tt" "hslb" "ttrx"
	find_type_f_iname txt.tar "*.txt"
	find_type_f_iname json.tar "*.json"
	find_type_f_iname csv.tar "*.csv"
	find_type_f_iname pdf.tar "*.pdf"
	find_type_f_iname php.tar "*.php"
	find_type_f_iname html.tar "*.htm" "*.html"
	find_type_f_iname image.tar "*.jpg" "*.jpeg" "*.png" "*.tif" "*.tiff" "*.gif" "*.bmp"
	find_type_f_iname audio.tar "*.ogg" "*.mp3" "*.aac" "*.wma" "*.amr" "*.aax" "*.smea" "*.wav"
	find_type_f_iname video.tar "*.avi" "*.mov" "*.mpg" "*.mp4" "*.mkv" "*.wmv" "*.flv" "*.3gp" "*.mpeg"
}

# "*.md"
# "*.pub"
# "*.tcal" "*.mplstyle"
# "*.gd1[0-9]" "*.gd[0-9]"
# geant-or-physics-analysis.tar "*.inc" "*.sty" "*.f"
#find_type_f_iname language.tar "chinesepod*mp3" "chinesepod*pdf" "chinesepod*mp4"
#find_type_d_iname language.tar "language" "anki"
#"*.txt.gz"
#"*.s" "*.asm" "*.ise"
#"*.lib"

function empty_dirs {
	if [ $verbosity -gt 3 ]; then echo; echo "empty dirs"; fi
	find -depth -type d -empty ${action_emptydir} | tee -a ${filename}
}

function adjust_datestamps {
	if [ $verbosity -gt 3 ]; then echo; echo "adjust timestamps of dirs"; fi
	adjust_datestamps_of_dirs_based_on_their_contents
}

function final_lfr {
	if [ $verbosity -gt 3 ]; then echo; echo "lf-r"; fi
	lf > lf-r
	declare -i wclf_new=$(cat lf-r | wc --lines)
	declare -i wclf_diff=$((wclf_old-wclf_new))
	echo "reduced number of files by $wclf_diff (from $wclf_old to $wclf_new)"
}

function final_duma {
	if [ $verbosity -gt 3 ]; then echo; echo "du-ma1"; fi
	dume
	declare -i du_new=$(cat du-ma1 | tail -n1 | awk -e '{ print $1 }')
	declare -i du_diff=$((du_old-du_new))
	echo "reduced used disk space by $du_diff MB (from $du_old to $du_new)"
}

initial_lfr
initial_duma
chmod_dirs
sockets
links
junk
empty_files
long_tail
svn_git
duplicate_finder
keepers
empty_dirs
adjust_datestamps
final_lfr
final_duma

