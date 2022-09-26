#!/bin/bash -e

# written 2022-09-21 by mza
# last updated 2022-09-21 by mza

alias soffice.exe="/cygdrive/c/Program\ Files/LibreOffice/program/soffice.exe"
soffice="/cygdrive/c/Program\ Files/LibreOffice/program/soffice.exe"

for each in *.ppsx; do
	new=$(echo $each | sed -e "s,\.ppsx$,\.pdf,")
	if [ ! -e "$new" ] || [ "$each" -nt "$new" ]; then
		echo "$each"
		eval "$soffice" --headless --convert-to pdf "$each"
		if [ -e "$new" ]; then
			touch "$new" --reference="$each"
		else
			echo "error creating $new"
		fi
	fi
done

