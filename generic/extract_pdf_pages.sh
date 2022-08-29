#!/bin/bash -e

# written 2022-08-23 by mza

declare inputfile="$1"
shift

declare string=""
declare pagestring=""
for page; do
	pagestring="page${page}.pdf"
	gs -dNOPAUSE -dQUIET -dBATCH -sDEVICE=pdfwrite -sOutputFile=$pagestring -dFirstPage=$page -dLastPage=$page $inputfile
	string="$string $pagestring"
done
gs -dNOPAUSE -dQUIET -dBATCH -sDEVICE=pdfwrite -sOutputFile=pages.pdf $string

