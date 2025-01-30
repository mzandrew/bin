#!/bin/bash -e

# last updated 2025-01-29 by mza

declare filename="actions-taken-to-clean-up-files.txt"
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

mkdir -p "${extracts}"

declare -i wclf_old
if [ ! -e lf-r.original ]; then
	if [ $verbosity -gt 3 ]; then echo; echo "lf-r.original"; fi
	lf > lf-r.original
	wclf_old=$(cat lf-r.original | wc --lines)
else
	if [ $verbosity -gt 3 ]; then echo; echo "lf-r"; fi
	lf > lf-r
	wclf_old=$(cat lf-r | wc --lines)
fi

declare -i du_old
if [ ! -e du-ma1.original ]; then
	if [ $verbosity -gt 3 ]; then echo; echo "du-ma1.original"; fi
	dume
	mv du-ma1 du-ma1.original
	du_old=$(cat du-ma1.original | tail -n1 | awk -e '{ print $1 }')
else
	du_old=$(cat du-ma1 | tail -n1 | awk -e '{ print $1 }')
fi

if [ $verbosity -gt 3 ]; then echo; echo "chmod u+rwx dirs"; fi
find -type d -exec chmod u+rwx --changes {} \; | tee -a ${filename}

if [ $verbosity -gt 3 ]; then echo; echo "sockets"; fi
find -type s -exec rm -v "{}" \; | tee -a ${filename}

if [ $verbosity -gt 3 ]; then echo; echo "links"; fi
find -type l -exec rm -v "{}" \; | tee -a ${filename}

if [ $verbosity -gt 3 ]; then echo; echo "junk dirs and files"; fi
find_type_d_iname junk.tar ".Trash*"
find_type_f_iname junk.tar "*.pcap" "*.pyc" "*.so" "*.o" "*~" "*.bak" "*.exe.stackdump" ".DS_Store" "desktop.ini" "hiberfil.sys" "pagefile.sys" "*.m3u"

#find_type_f_iname language.tar "chinesepod*mp3" "chinesepod*pdf" "chinesepod*mp4"
find_type_f_iname other.tar "*.schbak" "*.sch_bak" "*.symbak" "*.edn" "*.lock" "*.lnk" "*.tmp" "*.dvi" "*.aux" "*.obj" "*.out1" "*.vsd" "*.ll" "*.rep" "*.prm" "*.lst" "ntuser.dat*" "*.txt.gz" "*.hdf5" "*.sys" "*.wdb" "*.itdb" "*.plist" "*.itl" "*.ithmb"
find_type_f_iname data.tar "*.data" "*rawdata.[0-9][0-9][0-9][0-9][0-9]" "*rawdata.[0-9][0-9][0-9][0-9]" "*.rawdata[0-9][0-9][0-9]" "S*CH[0-9]" "PHD_S*CH[0-9]" "*.fiber[0-9]" "*.root" "*.sroot" "*.rawdata" "*.dat" "*.camac" "ccc[0-9]" "ccc" "aaa" "*.dst" "*.dst[0-9]" "*.datafile" "*.spl" "*.prn" "*.ped"
find_type_f_iname executable.tar "*.dll"
find_type_f_iname installers.tar "*.mui" "*.msi" "*.cab" "*.deb" "*.rpm" "*.ex_" "*.dl_" "*.tt_" "*.sc_" "*.os_" "*.gp_" "*.cn_" "*.si_" "*.th_" "*.h2_" "*.tx_" "*.xd_" "*.co_" "*.xs_" "*.xm_" "*.js_" "*.vb_" "*.ht_" "*.mi_" "*.in_" "*.gi_" "*.mo_" "*.ta_" "*.ax_" "*.op_" "*.oc_" "*.lo_" "*.pn_" "*.ma_" "*.wp_" "*.bm_" "*.as_" "*.tb_" "*.lx_" "*.mb_" "*.fo_" "*.hl_" "*.wa_" "*.nl_" "*.tc_" "*.jp_" "*.ac_" "*.le_" "*.ca_" "*.ic_" "*.ms_" "*.wm_" "*.sy_" "*.im_" "*.sw_" "*.di_" "*.ch_"

find_type_f_iname log.tar "*.log" "*.jou" "*.status" "VBox.log.*" "VBoxSVC.log.*" "*.out"
find_type_f_iname firmware-build.tar "*.str" "*.ise_ISE_Backup" "*.restore" "*.mgf" "*.dcp" "*.xsvf" "*.svf" "*.xmsgs" "*.xrpt" "*.vdbl" "*.syr" "*.twr" "*.twx" "*.wdb" "*.ngo" "*.vho" "*.mrp" "*.msd" "*.rpx" "*.rpt" "*.rbd" "*.rbb" "*.ngc" "*.ngd" "*.ncd" "*.ngr" "*.ngm" "*.mcs" "*.mcs.gz" "*.bit" "*.bit.gz" "*.hdf" "*.projectmgr" "*.xbcd" "*.xreport" "par_usage_statistics.html" "*.cmd_log" "*.elf" "*.blc" "*.bld" "*.unroutes" "*.par" "*.bgn" "*.map" "*.drc" "*.cdc" "*.xdl" "*.asdb" "*.cgc" "*.cpj" "*.psr" "*.do" "*.glade" "*_flist.txt" "*_readme.txt" "*_pad.txt" "*.ptwx" "*.ut" "*.tsi" "*.cgp" "*.scr" "*.key" "*_xmdf.tcl"
find_type_f_iname matlab.tar "*.mat" "*.m"
find_type_f_iname geant.tar "*.mac"
find_type_f_iname multiple.tar "*.bin" "*.xml"
find_type_f_iname dotfiles.tar ".gtkrc*" ".kderc*" ".nvidia-settings-rc" ".realplayerrc" ".hxplayerrc" ".dropbox" ".xsession-errors*" ".Xauthority" ".ICEauthority" ".viminfo" ".flexlmrc" ".lesshst" ".recently-used.xbel" ".RapidSVN" ".xscreensaver*" ".xauth*" ".dmrc" ".gtk-bookmarks" ".esd_auth" ".openoffice*" ".rhn-applet.conf" ".mime-types" ".recently-used" "._*"

# occasionally these are useful to include or exclude on a case-by-case basis:
find_type_f_iname executable.tar "*.exe"
find_type_f_iname firmware-build.tar "*.pcf"
find_type_f_iname junk.tar "*.psm"
#find -type f -name "*.pcf" ${action_file} | tee -a ${filename}
#find -type f -name "*.png" ${action_file} | tee -a ${filename} # this line may unintentionally grab useful stuff
#find -type f -name "*.txt" ${action_file} | tee -a ${filename} # this line may unintentionally grab useful stuff, including the file generated by this script...
#find -type f -name "*.csv" ${action_file} | tee -a ${filename} # this line may unintentionally grab useful stuff...
find -type f -wholename "*/coregen/*.pdf" ${action_file} | tee -a ${filename}
find -type f -wholename "*/simulations/*\.raw" ${action_file} | tee -a ${filename}

if [ $verbosity -gt 3 ]; then echo; echo "empty files"; fi
find -type f -empty ${action_emptyfile} | tee -a ${filename}

find_type_d_iname language.tar "language" "anki"
find_type_d_iname OS.tar "Windows" "Program Files" "Program Files (x86)" "ProgramData" "Boot" "System Volume Information" "lost+found"
find_type_d_iname executable.tar "MentorGraphics" "PAD_ES_Evaluation" "MSOCache" "teamviewer" "AlmytaSystems" "Anaconda3"
find_type_d_iname dotfiles.tar ".fltk" ".simvision" ".adobe" ".local" ".metadata" ".gconf" ".gnome2" ".gnome2_private" ".evolution" ".Spotlight-V100" ".nx" ".pki" ".vim" ".rhn-applet" ".nautilus" ".gconfd" ".gstreamer*" ".kde" ".swt" ".dbus" ".java" ".ipython" ".fluxbox" ".fonts*" ".fontconfig" ".rootnb" ".config" ".cache" ".pulse"
find_type_d_iname dotfiles.tar ".Xil" ".Xilinx" ".mozilla" ".cpan" ".gegl*" ".texmf-var" ".gimp*" ".gnome" ".opera" ".mcop" ".compiz" ".rhopenoffice*" ".openoffice*" ".icedteaplugin" ".update-notifier" ".irssi" ".qt" ".nbi" ".filezilla" ".putty" ".matlab" ".metacity" ".Skype" ".scim" ".sunpinyin"
find_type_d_iname dotfiles.tar ".SeeVoghRN" ".install4j" ".netx" ".HDI" ".beagle" ".netbeans*" ".thumbnails" ".macromedia" ".Mathematica" ".wine" ".vscode-server" ".vscode" ".eclipse" ".VirtualBox" ".dropbox.cache"
find_type_d_iname dotfiles.tar "*.anydesk" "*.astropy" "*.gitkraken" "*.hplip" "*.jupyter" "*.nano" "*.remmina" "*.virtualenvs"
find_type_d_iname dotfiles.tar ".chipscope" ".eZuceSRN" ".SeeVogh" ".ezwave" ".iscape" ".oracle*"
find_type_d_iname other.tar "isim" "impact_xdb" "iCDB" "Abisuite" "Application Data" "Temporary Internet Files" "Cookies" "Solidworks Downloads" "lowres" "\$Recycle\.Bin"
find_type_d_iname appdata.tar "appdata" # AppData/Thunderbird contains cached emails...
find_type_d_iname junk.tar "Local Settings" 
find_type_d_iname installers.tar ".yast2"

find_type_f_iname long-tail.tar "*.mui_*" "*.dll_*" "*.exe_*" "*.*_loc" "*._lcr"

find_type_f_iname long-tail.1MB.tar "*.ext2" "*.forward" "*.sf2" "*.examples" "*.hwmop" "*.tvl" "*.11" "*.dwl" "*.sdkproject" "*.849c9593-d756-4e56-8d6e-42412f2a707b" "*.exports" "*.version" "*.er" "*.ident" "*.crc" "*.eld" "*.scf" "*.md5sum" "*.kumacold" "*.9" "*.len" "*.trn" "*.fc" "*.lnp" "*.cgd" "*.loop" "*.isp" "*.64" "*.mgl" "*.xld" "*.metadata" "*.h1k" "*.asa" "*.overrides" "*.mllr" "*.search-ms" "*.dru" "*.metadata-v2" "*.webm" "*.tsstr" "*.jshintrc" "*.mappings" "*.lib~tdc_lib" "*.gitconfig" "*.iml" "*.svn-work" "*.gplt" "*.sed" "*.ogv" "*.dat%" "*.jid" "*.prjpcbstructure" "*.0nv" "*.octave_hist" "*.diz" "*.isim_lau_prj" "*.vbw" "*.hwmdat" "*.thumbnailer" "*.lso" "*.tbr" "*.m3u" "*.ptf" "*.eng" "*.lck" "*.theming" "*.cvsignore" "*.symlog" "*.srn" "*.size" "*.vis" "*.ctypes" "*.belle" "*.thd" "*.u8" "*.dft" "*.dproj" "*.prerm" "*.rnd" "*.g95" "*.svn" "*.xinetd" "*.g4m" "*.hpj" "*.var" "*.m2b" "*.syx" "*.bl-ceem-075_6" "*.bl-ceem-075_4" "*.tfi" "*.bl-ceem-075_5" "*.bl-ceem-075_1" "*.tx5" "*.hdlsourcefiles" "*.yml" "*.aws" "*.bl-ceem-075_3" "*.ic0" "*.scm" "*.xx" "*.tx6" "*.timing" "*._sprj" "*.tx11" "*.dff" "*.preun" "*.bl-ceem-075_2" "*.gtkw" "*.tfd" "*.pub" "*.bkmanifest" "*.tfl" "*.libs" "*.xil_info" "*.scc" "*._prj" "*.mos" "*.tx3" "*.smhist" "*.gnuplot_history" "*.crl" "*.tx7" "*.tx2" "*.lai" "*.minitel12-80" "*.sgicc" "*.htaccess" "*.sdbx" "*.psg" "*.rules" "*.26" "*.cshrc_bes" "*.batch" "*.59" "*.udo" "*.h1c" "*.wdm" "*.ufl" "*.bl-ceem-075_0" "*.dun" "*.pyw" "*.ti" "*.ppc" "*.pyf" "*.camp" "*.pe" "*.geom" "*.tag" "*.null" "*.lpr" "*.tx9" "*.pchmm" "*.att" "*.plc" "*.netbsd" "*.ne12bsd" "*.xdj" "*.amiga" "*.dlt" "*.filter" "*.freebsd4" "*.his" "*.header" "*.freebsd" "*.tx10" "*.stm" "*.cdtproject" "*.set" "*.col" "*.options" "*.dj2" "*.ldo" "*.job" "*.cdf" "*.ctr" "*.ix" "*.library-ms" "*.diff" "*.wxe" "*.fnc" "*.loc" "*.hpuxia64acc" "*.csf" "*.stl" "*.ano" "*.testing_plots_forgaryanderic" "*.sid" "*.frx" "*.vala" "*.oga" "*.tx4" "*.sin" "*.hhp" "*.gmmp" "*.tx1" "*.aff" "*.ibmc" "*.dependencies" "*.atari" "*.acorn" "*.lci" "*.main" "*.sgrd" "*.searchconnector-ms" "*.tsmeas" "*.linuxalphagcc" "*.linuxia64gcc" "*.pfx" "*.post" "*.fdo" "*.bash_profile" "*.xmp" "*.cnf" "*.tx8" "*.translators" "*.sysk" "*.linuxx8664icc" "*.hp700" "*.symcmd" "*.directory" "*.icw" "*.c2" "*.scat" "*.profile" "*.rc2" "*.cmrk" "*.tool" "*.vpi" "*.ifx" "*.inputrc" "*.aix5" "*.xfigrc" "*.end" "*.sunos5" "*.tc3" "*.rxvt" "*.index" "*.rs6000" "*.sunos5v9" "*.cpx" "*.eterm" "*.pol"
find_type_f_iname long-tail.1MB.tar "*.alphacxx6" "*.hpuxacc" "*.mips" "*.fs" "*.pif" "*.translations" "*.vcwin32" "*.planner" "*.mcr" "*.macosxxlc" "*.cst" "*.ldf" "*.macro" "*.bsb" "*.dim" "*.uninstall" "*.vcawin32" "*.trace" "*.linuxkcc" "*.watcom" "*.bc32" "*.oat" "*.sunos" "*.brk" "*.linuxicc" "*.elm" "*.intel" "*.konsole" "*.knr" "*.kdelnk" "*.abl" "*.wdo" "*.ss5" "*.pjh" "*.gko" "*.bor" "*.terms" "*.num" "*.patches" "*.macosxicc" "*.ppr" "*.openbsd" "*.ihh" "*.sm" "*.xrm-ms_690f532f" "*.erf" "*.alias" "*.mrxvt" "*.copyright" "*.solariscc5" "*.setup_spartan3" "*.vbp" "*.hi" "*.example" "*.linuxia64ecc" "*.1st" "*.pls" "*.itf" "*.nlf" "*.layer" "*.adf" "*.user" "*.tmml" "*.ldp" "*.wdr" "*.setup_virtex2" "*.diag" "*.odl" "*.edm" "*.ver" "*.cfi" "*.sam" "*.pao" "*.pdx" "*.hit" "*.hx1" "*.vbproj" "*.stuff" "*.storagerecordindex" "*.rndm" "*.icon" "*.din" "*.scp" "*.lnt" "*.macosx64" "*.rs64" "*.st0" "*.spi" "*.dbc" "*.fon_2e7bdf2f" "*.gp" "*.tft" "*.bxml" "*.code" "*.rlg" "*.nroff" "*.lnx" "*.fon_09ec4cfe" "*.jnlp" "*.fsc" "*.prefs" "*.xbap" "*.setup_virtex2p" "*.fsub" "*.app" "*.std" "*.etd" "*.pac" "*.fonts" "*.dep" "*.wiki" "*.pch++" "*.fon_6087927d" "*.xa" "*.os" "*.blg" "*.b32" "*.pop" "*.edp" "*.policy" "*.rsa" "*.txf" "*.pri" "*.flw" "*.master" "*.defs" "*.gvp" "*.pot"  "*.sco" "*.hpux" "*.emacs" "*.beos" "*.fon_2c83a12b" "*.darwin" "*.cli" "*.sggcc" "*.md1" "*.pdr" "*.aifc" "*.rat" "*.alien" "*.aix" "*.hpgcc" "*.hist" "*.cmp" "*.so9" "*.windows" "*.32sunu" "*.xds" "*.xwbt" "*.64sunu" "*.rootdaemonrc" "*.v2cc" "*.drk" "*.cip" "*.ma" "*.filters" "*.gnome" "*.csd" "*.setup_spartan3e" "*.fish" "*.hpu" "*.lpc" "*.monalisa" "*.sep" "*.linux8664gcc" "*.abt" "*.xterm-new" "*.ss5v9" "*.wpd"
find_type_f_iname long-tail.1MB.tar "*.strokes" "*.wpl" "*.inp" "*.log2" "*.docbook" "*.proof" "*.vams" "*.skew" "*.url" "*.p12" "*.w" "*.plg" "*.gcmmx" "*.selector" "*.php" "*.skn" "*.cdb" "*.applescript" "*.msh" "*.tasks" "*.nav" "*.pcd" "*.wfs" "*.iss" "*.cdmp" "*.bda" "*.xsf" "*.bbl" "*.tsim" "*.solaris" "*.tree" "*.proc" "*.23a" "*.cir" "*.rck" "*.ncl" "*.mic" "*.rtx" "*.apr_lib" "*.egpf" "*.macosx" "*.lin" "*.hp64" "*.bmm" "*.edu" "*.cpc" "*.debian" "*.npl" "*.pff" "*.me" "*.bpf" "*.bkgen" "*.g4mac" "*.mf" "*.epcf" "*.coe" "*.vrg" "*.ssm" "*.lsp" "*.imp" "*.ci" "*.f90" "*.mpd" "*.xrd" "*.nfo" "*.sc" "*.mkshrc" "*.extrep" "*.shp" "*.pc" "*.common" "*.mti" "*.shtml" "*.vhi" "*.includecache" "*.tip" "*.ltp" "*.mozlz4" "*.mimes" "*.fd" "*.security" "*.1op" "*.rb" "*.desktop" "*.twn" "*.cal" "*.tap" "*.template" "*.sth" "*.pdd" "*.sgml" "*.vb" "*.dia" "*.wxr" "*.launch" "*.control" "*.lif" "*.linux" "*.input" "*.cygwin" "*.dcl" "*.ils" "*.empy" "*.sgi" "*.caf" "*.dbf" "*.vms" "*.plt" "*.nn" "*.tplx" "*.vcxproj" "*.mc" "*.rootauthrc" "*.gyd" "*.dpp" "*.vlib" "*.globus" "*.inl" "*.for" "*.gm8" "*.theme" "*.pnx" "*.gm2" "*.drml" "*.apr" "*.mnu" "*.bom" "*.vdbx" "*.xsw" "*.xr" "*.rh" "*.wwd" "*.xu" "*.sln" "*.gbx" "*.pnt" "*.xdw" "*.xw" "*.cdx" "*.depend" "*.dvd" "*.paf" "*.l2" "*.table" "*.xd" "*.tci" "*.mesg" "*.aug" "*.rdf" "*.c#" "*.dbg" "*.pine-debug4" "*.vhx" "*.l3" "*.mcf" "*.pat" "*.xsc" "*.srt" "*.lot" "*.protoinst" "*.dlg" "*.mb" "*.tlx" "*.spec" "*.chk" "*.xs" "*.letter" "*.xc" "*.vert" "*.jsm" "*.fnt" "*.wc" 
find_type_f_iname long-tail.1MB.tar "*.shs" "*.sts" "*.project" "*.igpi" "*.clw" "*.ttl" "*.usg" "*.dxt" "*.stackup" "*.cards" "*.kumac" "*.plot%" "*.vcw" "*.sld" "*.zhtml" "*.internal" "*.la" "*.acr" "*.lof" "*.pwr" "*.dmap" "*.schlog" "*.w32-in" "*.gpf" "*.fe" "*.pbm" "*.pine-debug1" "*.pine-debug2" "*.pine-debug3" "*.schcmd" "*.frag" "*.bpr" "*.egg-info" "*.sample" "*.hhc" "*.cpm" "*.gan" "*.joboptions" "*.gp4" "*.drr" "*.hht" "*.zh" "*.ascx" "*.sim" "*.ndx" "*.pickle" "*.phn" "*.text" "*.pcl" "*.jam" "*.dat_i" "*.name_i" "*.iic" "*.pin" "*.dir" "*.aiff" "*.tspec" "*.env" "*.fsm" "*.mss" "*.wmz" "*.sig" "*.xbn" "*.lines" "*.tbw" "*.gm1" "*.info-23" "*.xn" "*.x" "*.info-15" "*.png_ped_hslb_a" "*.root_hist" "*.drrpreview" "*.setup" "*.emp" "*.auth" "*.stat" "*.25" "*.ps1xml" "*.extreppreview" "*.nt" "*.pinerc" "*.mdp" "*.default" "*.als" "*.dos" "*.bfc" "*.qdb" "*.al" "*.test" "*.ant" "*.mod" "*.npr" "*.rsd" "*.cf" "*.etc" "*.tsp_c999e400" "*.grp" "*.info-13" "*.gg1" "*.info-12" "*.lfp" "*.smp" "*.bdl" "*.pgd" "*.xaw" "*.pck" "*.ssd" "*.rsp" "*.info-17" "*.vhw" "*.info-11" "*.fft" "*.uv2" "*.ru" "*.rst" "*.l1" "*.sk" "*.cov" "*.info-20" "*.upp" "*.22b" "*.info-18" "*.info-19" "*.verify" "*.info-21" "*.info-14" "*.ptxml" "*.ro" "*.script" "*.shortname_i" "*.fgd" "*.schdotpreview" "*.info-10" "*.win32" "*.lo" "*.au" "*.supp" "*.es" "*.info-16" "*.nl" "*.mli" "*.it" "*.mdd" "*.fr" "*.mid" "*.cms" "*.pro" "*.list" "*.gmk" "*.conf" "*.hts" "*.info-9" "*.ntt" "*.mrk" "*.tsp_2d5533f8" "*.info-22" "*.contact" "*.uu" "*.storagedata" "*.info-8" "*.ja" "*.tex#" "*.lua" "*.prf" "*.aw" "*.cw" "*.r2c" "*.ncf" "*.mms" "*.arch" "*.compositefont" "*.entry"
find_type_f_iname long-tail.1MB.tar "*.net" "*.info-7" "*.ld" "*.prb" "*.blf" "*.shortname" "*.name" "*.bix" "*.de" "*.ac" "*.err" "*.psk" "*.wdf" "*.jrl" "*.ko" "*.i" "*.ppf" "*.n" "*.sl" "*.plot" "*.fcdb" "*.jsp" "*.icns" "*.trc" "*.osm" "*.fnd" "*.vcproj" "*.at" "*.hhk" "*.cbk" "*.log#" "*.idl" "*.ldppreview" "*.rvw" "*.csc" "*.epr" "*.onl" "*.mapping" "*.syn" "*.tex%" "*.g3" "*.pfm" "*.vxd" "*.typelib" "*.summary" "*.tsdef" "*.lasse" "*.frm" "*.lmf" "*.perl" "*.pt4" "*.ejp" "*.men" "*.kum" "*.dec" "*.modulemap" "*.tsop" "*.resx" "*.htt" "*.xtu" "*.cs" "*.rgb" "*.suo" "*.psd1" "*.ntpl" "*.comments" "*.y" "*.rootrc" "*.tl" "*.reg" "*.tpa" "*.20" "*.arl" "*.ppm" "*.lic" "*.bib" "*.p" "*.xrc" "*.aap" "*.upf" "*.tsm" "*.gdl" "*.asp" "*.tgf" "*.dtd" "*.tips" "*.dsw" "*.mno" "*.a51" "*.tlb_662648dd" "*.llr" "*.mak" "*.xbm" "*.dsf" "*.ast" "*.jhd" "*.dxpprf" "*.tlu" "*.sf" "*.pre" "*.t" "*.include" "*.rll" "*.unx" "*.config" "*.sir" "*.note" "*.bd" "*.uce" "*.cproject" "*.opj" "*.prt" "*.m51" "*.ctl" "*.tmf" "*.gp3" "*.os2" "*.new" "*.pcx" "*.keystream" "*.bpd" "*.llm" "*.bsm" "*.l4" "*.ld4" "*.amp" "*.log1" "*.th" "*.hsf" "*.rul" "*.gdml" "*.uue" "*.vdo" "*.pnm" "*.utx" "*.dem" "*.values" "*.info-6" "*.pfd" "*.api" "*.gp1" "*.mdi" "*.cmb" "*.wri" "*.dt" "*.rs" "*.pod" "*.drf" "*.debug" "*.asy" "*.rc" "*.mpf" "*.aspx" "*.svn-base" "*.xcd" "*.gsf" "*.xpt" "*.tsmap" "*.gtd" "*.ntrc_log" "*.gp2" "*.opt" "*.vcf" "*.psl" "*.cap" "*.veo" "*.drkcard" "*.make" "*.xst" "*.info-5" "*.10" "*.ac0" "*.reppreview" "*.cah" "*.mif" "*.cmd" "*.mib" "*.bdf"
find_type_f_iname long-tail.1MB.tar "*.xlsm" "*.h1t" "*.ipc" "*.op" "*.hif" "*.mkr" "*.sub" "*.xsd" "*.tpr" "*.mpp" "*.diagpkg" "*.panel" "*.xpr" "*.cmake" "*.db-shm" "*.vhdpreview" "*.ltx" "*.rnc" "*.jpf" "*.cpl_b6a1dbdc" "*.erl" "*.nga" "*.cnt" "*.asd" "*.info-4" "*.targets" "*.mk" "*.pf" "*.mfd" "*.browser" "*.scs" "*.sdbl" "*.tim" "*.ml" "*.cty" "*.info-3" "*.man" "*.ins" "*.ncm" "*.woff2" "*.sw0" "*.info-2" "*.sobecons" "*.xltx" "*.info-1" "*.gbm" "*.bkl" "*.tab" "*.wpc" "*.pcm" "*.guess" "*.mm" "*.prx" "*.va" "*.plo" "*.xlt" "*.pll" "*.md" "*.pex2" "*.csb" "*.ld07" "*.mnl" "*.sb" "*.emf" "*.def" "*.clx" "*.strm" "*.state" "*.bst" "*.vwp" "*.com" "*.dfa" "*.gds2" "*.swp" "*.tf" "*.ext" "*.tlm" "*.vbs" "*.emz" "*.properties" "*.xcf" "*.stx" "*.esn" "*.pedsub_calcfd" "*.toc" "*.wlf" "*.pedsub_hits" "*.cache*" "*.tsp" "*.bas" "*.rle" "*.hdr" "*.oem" "*.outjob" "*.10mar" "*.fra" "*.g2" "*.gpg" "*.tsdb" "*.tm" "*.ps1" "*.drl" "*.eldo53" "*.tbc" "*.cur" "*.8" "*.min" "*.json" "*.ita" "*.orig" "*.zzz" "*.hst" "*.pcbdocpreview" "*.win" "*.pd07" "*.sve" "*.src" "*.dbk" "*.evt" "*.pbxproj" "*.mhs" "*.tch" "*.s2p"

find_type_f_iname long-tail.10MB.tar "*.jsonlz4" "*.gtm" "*.dmc" "*.usb0" "*.pfa" "*.cnv" "*.hwdef" "*.g7l" "*.xraw" "*.ico" "*.dmo" "*.pd4" "*.nld" "*.form" "*.emn" "*.schdot" "*.nlt" "*.rom" "*.dvr-ms" "*.dtx" "*.sty" "*.gtp" "*.wcfg" "*.lng" "*.ocx_38c869db" "*.cbz" "*.fon" "*.gid" "*.ifd" "*.devhelp2" "*.pem" "*.il" "*.lgc" "*.hwh" "*.gir" "*.grc" "*.itk" "*.prjpcb" "*.cls" "*.ipf" "*.cel" "*.jrs" "*.aps" "*.wxform" "*.xwv" "*.pedsub_hitscfd" "*.pt07" "*.mum" "*.acm" "*.chq" "*.rootmap" "*.prj" "*.g6l" "*.deu" "*.csa" "*.ai" "*.regtrans-ms" "*.sql" "*.dcm" "*.crt" "*.l" "*.ime" "*.sav" "*.exsd" "*.tcc" "*.r54265" "*.drv" "*.r53921" "*.old" "*.ads" "*.vh" "*.ndf" "*.ani" "*.r" "*.xsl" "*.bat" "*.zap" "*.r53657" "*.hdx" "*.lis" "*.res" "*.g4" "*.jed" "*.lan" "*.dat#" "*.enu" "*.wmf" "*.vf" "*.xpi" "*.adr" "*.pl" "*.xrm-ms" "*.gtc" "*.gise" "*.ntf" "*.lf-r" "*.ods" "*.g1" "*.pkginfo" "*.lhp" "*.acd" "*.sch_1" "*.xpd" "*.wsp" "*.tfm" "*.msstyles" "*.pfb" "*.ddd" "*.hxx" "*.bkg" "*.mine" "*.gc6" "*.inx" "*.lex" "*.heic" "*.if2" "*.g4l" "*.wma" "*.g5l" "*.adml" "*.msc" "*.pages" "*.gc8" "*.xco" "*.gcc" "*.m4" "*.afm" "*.shx" "*.ind" "*.gc9" "*.gbc" "*.eps#" "*.g2l" "*.dms" "*.cdf-ms" "*.gbk" "*.fmwr" "*.efi" "*.bcc" "*.tui" "*.pptm" "*.whl" "*.gc7" "*.sbr" "*.resources" "*.eco" "*.gtk" "*.vm6" "*.fits" "*.eml" "*.g3l" "*.pad_txt" "*.inc" "*.cmf" "*.vc" "*.gbp" "*.f" "*.hkp" "*.pm" "*.vp" "*.wat" "*.d" "*.nap" "*.amx" "*.adm" "*.vch" "*.gdo" "*.adb" "*.gfl" "*.gwk" "*.mjs" "*.ali" "*.ui" "*.nlp" "*.gc5" "*.sdo" "*.texi" "*.dhp" "*.tax2017" "*.msg" "*.pad" "*.psd" "*.gc4" "*.xtd" "*.btr" "*.dml" "*.gbr" "*.rpo" "*.bpl" "*.6" "*.ncb" "*.sym" "*.cpa" "*.tpl" "*.ax" "*.mfl" "*.sdf" "*.vdf" "*.srp" "*.dvg" "*.xpm" "*.idf" "*.ltl" "*.gc3" "*.hyp" "*.7" "*.mof" "*.lxa" "*.mst" "*.admx" "*.dectest" "*.xda" "*.rtf" "*.cfg" "*.gc2" "*.gdt" "*.less" "*.bcm" "*.art" "*.fdf" "*.idb" "*.upd" "*.pyd" "*.ref" "*.lyt" "*.3" "*.tlb" "*.grd" "*.gd12"

find_type_f_iname long-tail.100MB.tar "*.mnf" "*.pyo" "*.rbf" "*.cxt" "*.easm" "*.in" "*.wld" "*.dcs" "*.axy" "*.po" "*.vdb" "*.prp" "*.enc" "*.lrc" "*.vds" "*.max" "*.5" "*.ts" "*.ntp" "*.cpl" "*.igs" "*.ini" "*.qtx" "*.ibs" "*.hbk" "*.pho" "*.llb" "*.cam" "*.gd3" "*.gd4" "*.gd6" "*.gd11" "*.gd5" "*.gd10" "*.gd2" "*.gd8" "*.gd7" "*.gd9" "*.dsp" "*.manifest" "*.icm" "*.hh" "*.bfd" "*.mdb" "*.msk" "*.rm" "*.schdocpreview" "*.dly" "*.hlt" "*.nls" "*.4" "*.pb" "*.hepevt" "*.xtda" "*.cat" "*.pak" "*.idx" "*.dsn" "*.h1s" "*.did" "*.0" "*.dlm" "*.part" "*.vhf" "*.cio" "*.js" "*.css" "*.ldz" "*.ou" "*.lzp" "*.jsa" "*.asc" "*.tbl" "*.drklog" "*.fst" "*.2" "*.epsi" "*.dra" "*.sd2" "*.sd1" "*.upi" "*.info" "*.tga" "*.am" "*.ilk" "*.gpd" "*.pkg" "*.mo" "*.bre" "*.db-wal" "*.dic" "*.icc" "*.xfd" "*.ppd" "*.wfm" "*.hlp" "*.ocx" "*.etl" "*.pdb" "*.isu" "*.mcm" "*.sd0" "*.xci" "*.inf" "*.vcp" "*.peddiff" "*.ttc" "*.pnf" "*.txt#" "*.chm" "*.odg" "*.elc" "*.dmp" "*.1" "*.swf" "*.spd" "*.vcd" "*.el" "*.imd"
#maybe "*.s" "*.asm" "*.ise"

find_type_f_iname long-tail.1000MB.tar "*.medium" "*.sel" "*.gd1" "*.xcix" "*.apkg" "*.db" "*.psnup" "*.edf" "*.bsd" "*.olb" "*.exp" "*.z" "*.pch" "*.dev" "*.lna" "*.cmc" "*.tsdat" "*.sdb" "*.edb" "*.grf" "*.nph" "*.tdo" "*.a"
# maybe "*.lib"

# occasionally these are useful to include or exclude on a case-by-case basis:
find_type_d_iname svn.tar ".svn" # this line may unintentionally grab useful stuff...
find_type_d_iname git.tar ".git" # this line may unintentionally grab useful stuff...

if [ $verbosity -gt 3 ]; then echo; echo "duplicate files"; fi
echo
lf | duplicate_finder.py
./script_to_remove_all_duplicates_that_are_not_golden.sh

# these are the to-save files:
# csv, jpg, jpeg, png, tif, tiff, gif, txt
#find_type_f_iname asic.tar "*.spc" "*.sp" "*.vdo" "*.vdb" "*.tdb" "*.tdo" "*.edif" "*.tsdat" "*.tsmeas" "*.tsim" "*.tsdb" "*.wmf" "*.tanner" "*.gds" "*.lvs" "*.drc" "*.layout"
#find_type_f_iname asic.tar "*.txt" "*.pdf" "*.pptx" "*.png" "*.xls" # this will grab too much unrelated stuff...
#find_type_f_iname pcb.tar "*.gerber" "*.gto" "*.gbo" "*.gtl" "*.gbl" "*.gts" "*.gbs" "*.pcbdoc" "*.schdoc" "*.schlib" "*.sch" "*.pcb" "*.kicad_pcb" "*.kicad_sch" "*.brd" "*.ln9" "*.ld9" "*.pt9" "*.pd9"
#find_type_f_iname mechanical.tar "*.sldprt" "*.sldasm" "*.dxf" "*.dwg" "*.stp" "*.step"
#find_type_f_iname firmware.tar "*.vhd" "*.vhdl" "*.v" "*.sv" "*.ucf" "*.xdc" "*.xco" "*.xise" "*.gise"
#find_type_f_iname source.tar "*.c" "*.cc" "*.cpp" "*.c++" "*.h" "*.hpp" "*.h++" "*.class" "*.py" "*.pm" "*.sh" "*.s" "*.asm" "*.jar"
#find_type_f_iname presentations.tar "*.odp" "*.ppt" "*.pptx" "*.ps" "*.eps"
#find_type_f_iname documents.tar "*.xls" "*.xlsx" "*.doc" "*.docx" "*.tex"

if [ $verbosity -gt 3 ]; then echo; echo "empty dirs"; fi
find -depth -type d -empty ${action_emptydir} | tee -a ${filename}

if [ $verbosity -gt 3 ]; then echo; echo "adjust timestamps of dirs"; fi
adjust_datestamps_of_dirs_based_on_their_contents

if [ $verbosity -gt 3 ]; then echo; echo "lf-r"; fi
lf > lf-r
declare -i wclf_new=$(cat lf-r | wc --lines)
declare -i wclf_diff=$((wclf_old-wclf_new))
echo "reduced number of files by $wclf_diff (from $wclf_old to $wclf_new)"

if [ $verbosity -gt 3 ]; then echo; echo "du-ma1"; fi
dume
declare -i du_new=$(cat du-ma1 | tail -n1 | awk -e '{ print $1 }')
declare -i du_diff=$((du_old-du_new))
echo "reduced used disk space by $du_diff MB (from $du_old to $du_new)"

