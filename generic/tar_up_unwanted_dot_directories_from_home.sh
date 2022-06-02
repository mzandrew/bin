#!/bin/bash -e

# keepers: .bash_history .bashrc .cddb .gaim .purple .purple2 .gnupg .ssh .subversion .profile .mozilla-thunderbird .thunderbird .fluxbox

for each in \
	.npm .cmake \
	.gnash .printer-groups.xml .pki .swp .ps .gtk-custom-papers .KoalaNext .eagle .mm3d \
	.openshot .camstream .install4j .libquicktime_codecs .videoporama .winff .DownloadManager .easyMP3Gain .dvdcss \
	.chromium-score .gimp-2.6 .googleearth .gtkpod .loki .orca .tomboy .webcamrc .bitpim .cups \
	.gpscorrelaterc .hp48 .lyrics .tangogps .tomboy.log .xfigrc .a2dp .bitpim-files .fltk .gnuplot_history \
	.gpsdrive .hplip .screenlets .texmf-var .blender .gdbtkinit .gnuplot-wxt .gqview .hugin \
	.openoffice.org .sqlite_history .vimtmpswp .chromium .gegl-0.0 .google .gtkdiskfree2 .java \
	.opera .tlkgames .webcamd \
	.a2dprc .adobe .asoundrc .audacious .audacity1.3-mza .audacity-data .azureus \
	.bash_logout .beagle .bitmap2component .blabel.conf \
	.cache .checkgmail .coccinella .config .covers .cvspass .cpan .cvpcb .compiz .compiz-1 \
	.drirc .dbus .dbus-keyrings .dmrc \
	.eaglerc .easytag .esd_auth .evolution .eeschema \
	.fontconfig .fonts .FBReader \
	.gconf .gconfd .gEDA .gentoo-history .gentoorc .gftp .ggz .gimp-2.2 .gimp-2.4 .gizmo .grip-lame \
	.gizmo-cache .gksu.lock .gmpc .gnokii-errors .gnome .gnome2 .gnome2_private \
	.gnome_private .grip .grip-oggenc .gstreamer-0.10 .gtk-bookmarks .gtkrc-1.2-gnome2 \
	.gtwitter .gxine .gpxgoogle .grassrc6 .gerbview .gphoto .gvfs \
	.goutputstream-* \
	.hotkeys .hwdb .hedgewars \
	.ICEauthority .icons .inkscape .icedtea \
	.jtag \
	.kde .kino-history .kinorc .kicad .kicad_common \
	.lesshst .liferea .liferea_1.2 .liferea_1.4 .liferea_1.6 .liferea_1.8 .local .lircrc .lyx \
	.macromedia .mcop .mcoprc .metacity .minirc.dfl .mozilla .mplayer .multisync .mythtv .mutella .mission-control .makerware-license-accepted \
	.nautilus .netrc .nvidia .nvidia-settings-rc .nv \
	.OpenCity .openoffice.org2 .opensync .octave_hist \
	.profile .pulse .pulse-cookie .pcb .pcbnew \
	.qdvdauthor .qemu_history .qemu-launcher .qt .qgis \
	.recently-used .recently-used.xbel .ripperXrc .root_hist \
	.sane .Skype .sudo_as_admin_successful .synaptic .shotwell \
	.themes .thumbnails \
	.unison .update-manager-core .update-notifier \
	.vim .viminfo .vlc .vmware .VirtualBox \
	.w3m .wapi .wine \
	.Xauthority .xine .xsession-errors .xsession-errors.old .xinput.d .Xilinx ; \
do
	if [ -e "$each" ]; then
		echo $each
		tar -rf unwanted_dot_files.tar "$each" --remove-files
	fi
done

