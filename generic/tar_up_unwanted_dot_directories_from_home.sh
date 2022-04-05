# keepers: .bash_history .bashrc .cddb .gaim .purple .purple2 .gnupg .ssh .subversion .profile .mozilla-thunderbird .thunderbird .fluxbox

for each in \
	.chromium-score .gimp-2.6 .googleearth .gtkpod .loki .orca .tomboy .webcamrc .bitpim .cups \
	.gpscorrelaterc .hp48 .lyrics .tangogps .tomboy.log .xfigrc .a2dp .bitpim-files .fltk .gnuplot_history \
	.gpsdrive .hplip .screenlets .texmf-var .blender .gdbtkinit .gnuplot-wxt .gqview .hugin \
	.openoffice.org .sqlite_history .vimtmpswp .chromium .gegl-0.0 .google .gtkdiskfree2 .java \
	.opera .tlkgames .webcamd \
	.a2dprc .adobe .asoundrc .audacious .audacity1.3-mza .audacity-data .azureus \
	.bash_logout .beagle \
	.cache .checkgmail .coccinella .config .covers .cvspass \
	.drirc .dbus .dbus-keyrings .dmrc \
	.eaglerc .easytag .esd_auth .evolution \
	.fontconfig .fonts \
	.gconf .gconfd .gEDA .gentoo-history .gentoorc .gftp .ggz .gimp-2.2 .gimp-2.4 .gizmo .gizmo-cache .gksu.lock .gmpc .gnokii-errors .gnome .gnome2 .gnome2_private .gnome_private .grip .grip-oggenc .gstreamer-0.10 .gtk-bookmarks .gtkrc-1.2-gnome2 .gtwitter .gxine .gpxgoogle \
	.hotkeys .hwdb \
	.ICEauthority .icons .inkscape \
	.jtag \
	.kde .kino-history .kinorc .kicad .kicad_common \
	.lesshst .liferea .liferea_1.2 .liferea_1.4 .local .lircrc \
	.macromedia .mcop .mcoprc .metacity .minirc.dfl .mozilla .mplayer .multisync .mythtv .mutella \
	.nautilus \
	.OpenCity .openoffice.org2 .opensync \
	.profile .pulse .pulse-cookie \
	.qdvdauthor .qemu_history .qemu-launcher .qt .qgis \
	.recently-used .recently-used.xbel \
	.sane .Skype .sudo_as_admin_successful .synaptic \
	.themes \
	.unison .update-manager-core .update-notifier \
	.viminfo .vlc .vmware \
	.w3m .wapi .wine \
	.Xauthority .xine .xsession-errors; \
do
	if [ -e "$each" ]; then
		echo $each
		tar -rf unwanted_dot_files.tar "$each" --remove-files
	fi
done

