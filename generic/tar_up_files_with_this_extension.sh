#!/bin/bash -e

# written 2025-01-17 by mza
# last updated 2025-01-29 by mza

for ext; do
	echo "${ext}"
	tarfile="${ext}.tar"
	lfrfile="${ext}.tar.lf-r"
	find . -type d \( -name "proc" -o -name "dev" -o -name "\.svn" -o -name "\.git" -o -name "\@eaDir" \) -prune -o -type f -iname "*.${ext}" -printf "%TY-%Tm-%Td+%TH:%TM %12s %p\n" | sort -k 1n,1 | tee -a "${lfrfile}"
	find -type f -iname "*.${ext}" -print0 | tar -rf "${tarfile}" --remove-files --null -T -
	ls -lart "${tarfile}" "${lfrfile}"
done

