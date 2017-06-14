#!/bin/bash -e

declare host=$(hostname)
declare dir=$(dirname $HOME)
declare me=$(basename $HOME)
declare destination="/opt/backup/active/$me/backups/rsynced-repeatedly/$me-$host"
cd $dir
#echo "$host $dir/$me -> $destination"
rsync -a --delete $dir/$me/ $destination

