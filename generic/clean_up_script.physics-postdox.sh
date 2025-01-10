#!/bin/bash -e

find -type f -name "*rawdata.[0-9][0-9][0-9][0-9][0-9]" -exec rm {} \;
find -type f -name "*rawdata.[0-9][0-9][0-9][0-9]" -exec rm {} \;
find -type f -name "*.rawdata[0-9][0-9][0-9]" -exec rm {} \;
find -type f -name "*.pyc" -exec rm {} \;
find -type f -name "*.so" -exec rm {} \;
find -type f -name "*.o" -exec rm {} \;
find -type f -name "*.rawdata" -exec rm {} \;
find -type f -name "*.log" -exec rm {} \;
find -type f -name "*.jou" -exec rm {} \;
find -type f -name "*.dat" -exec rm {} \;
find -type f -name "*.camac" -exec rm {} \;
find -type f -name "*.status" -exec rm {} \;
find -type f -name "*~" -exec rm {} \;
find -type f -name "ccc" -exec rm {} \;
find -type f -name "*.bin" -exec rm {} \;
find -type f -name "*.mcs" -exec rm {} \;
find -type f -name "*.bit" -exec rm {} \;
find -type f -name "*.hdf" -exec rm {} \;
find -type f -name "*.xml" -exec rm {} \;
find -type f -name "*.elf" -exec rm {} \;
find -depth -type d -name ".metadata" -exec rm -rf {} \;
find -depth -type d -name "isim" -exec rm -rf {} \;
find -depth -type d -name ".svn" -exec rm -rf {} \;
find -depth -type d -name ".git" -exec rm -rf {} \;
find -depth -type d -empty -exec rmdir {} \;

