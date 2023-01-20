#!/bin/bash -e

declare host=$(hostname)
declare dir=$(dirname $HOME)
declare me=$(basename $HOME)
declare destination="/opt/backup/active/$me/backups/rsynced-repeatedly/$me-$host"
cd $dir
#echo "$host:$dir/$me -> $destination"
rsync -a --exclude="/.mozilla/" --exclude="/.cache/" --exclude="/.local/" --delete --delete-excluded $dir/$me/ $destination/

# do "crontab -e" and then add a line for this script (and then uncomment it):
# m  h   dom mon dow command
#  0    5   *   *   *   backup_this_host_to_nas.sh

