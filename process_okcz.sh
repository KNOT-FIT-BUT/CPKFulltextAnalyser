#!/bin/bash

# Predzpracovani vstupniho souboru

preprocess_data () {
	sed -e 's/^[ \t]*//' okcz_toc.xml > okcz_toc_preprocessed.xml

	if [ ! -d split/ ]; then
		mkdir split/
	fi

	if [ ! -d processed/ ]; then
		mkdir processed/
	fi

	# Rozdeleni souboru na casti, kazda obsahuje jednu obalku

	cd split ; csplit ../okcz_toc_preprocessed.xml '%^<obalkyknih%1' '/^<\/book/1' '{*}' ; cd ..

	# Prevod obsahu souboru do puvodni vizualni podoby

	ls split > list
	cat list | while read -r line; do sed -n 's:.*<toc>\(.*\)</toc>.*:\1:p' split/"$line" | sed 's/\\r\\n/\n/g;s/\\n/\n/g' > processed/"$line"; done
}

# Zpracovani vsech zaznamu z okcz_toc.xml

process_all_data () {

	if [ ! -d final/ ]; then
		mkdir final/
	fi

	# Serazeni seznamu souboru podle poctu nalezenych jmen

	if [ ! -f list.sorted ]; then
		cut -f1 -d: occurences* | LC_ALL=C sort | LC_ALL=C uniq -c | sort -rn | sed -e 's/^[[:blank:]]*\([[:digit:]]*\)[[:blank:]]split\/\([[:alnum:] ]*\)/\2/' > list.sorted
	fi

	# Zpracovani jednotlivych souboru s parametry -s a -a

	cat list.sorted | while read -r line; do
		if [ ! -f final/"$line" ]; then	
			declare -A FILE_NAMES
			declare AUTHOR
			get_local_ids $line
			print_ids "$line" > final/"$line"
			print_records "$line" >> final/"$line"
			print_author "$line" >> final/"$line"
			analyze_book "$line" >> final/"$line"
			unset FILE_NAMES
			unset AUTHOR
		fi
	done
}

# Vyhledavani krestnich jmen v zaznamech obalek knih

find_names () {
	screen -d -m -S occ0 bash -c 'find split -name xx0* | xargs grep -o -f names >> occurences0' &
	screen -d -m -S occ1 bash -c 'find split -name xx1* | xargs grep -o -f names >> occurences1' &
	screen -d -m -S occ2 bash -c 'find split -name xx2* | xargs grep -o -f names >> occurences2' &
	screen -d -m -S occ3 bash -c 'find split -name xx3* | xargs grep -o -f names >> occurences3' &
	screen -d -m -S occ4 bash -c 'find split -name xx4* | xargs grep -o -f names >> occurences4' &
	screen -d -m -S occ5 bash -c 'find split -name xx5* | xargs grep -o -f names >> occurences5' &
	screen -d -m -S occ6 bash -c 'find split -name xx6* | xargs grep -o -f names >> occurences6' &
	screen -d -m -S occ7 bash -c 'find split -name xx7* | xargs grep -o -f names >> occurences7' &
	screen -d -m -S occ8 bash -c 'find split -name xx8* | xargs grep -o -f names >> occurences8' &
	screen -d -m -S occ9 bash -c 'find split -name xx9* | xargs grep -o -f names >> occurences9' &
}

# Zobrazeni zaznamu s nejvyssi cetnosti krestnich jmen

print_files_with_names () {
	cut -f1 -d: occurences* | LC_ALL=C sort | LC_ALL=C uniq -c | sort -rn | sed -e 's/^[[:blank:]]*\([[:digit:]]*\)[[:blank:]]split\/\([[:alnum:] ]*\)/\2\t\1/'
}

# Filtrovani a prevod formatu ID, ulozeni do pomocnych souboru
# CBN (015), ISBN (020), OCLC (035)

preprocess_ids () {
	grep -P "^[^\s]*\s(015|020|035)\s" export_mzk.mrc > export_mzk.ids
	grep -P "^[^\s]*\s(015|020|035)\s" export_nkp.mrc > export_nkp.ids

	grep -P "^[^\s]*\s015\s" export_mzk.ids | grep "\$\$acnb" | sed -e 's/^\(.*\)\s015\s*L\s\$\$acnb\([0-9]*\)\([^0-9].*\|$\)/\1 \2/g' > export_mzk.ids.cnb
	grep -P "^[^\s]*\s015\s" export_nkp.ids | grep "\$\$acnb" | sed -e 's/^\(.*\)\s015\s*L\s\$\$acnb\([0-9]*\)\([^0-9].*\|$\)/\1 \2/g' > export_nkp.ids.cnb
	grep -P "^[^\s]*\s020\s" export_mzk.ids | grep "\$\$a" | tr -d '-' | sed -e 's/^\(.*\)\s020\s*L\s\$\$a\([X0-9 ]*\)\([^X0-9 ].*\|$\)/\1-\2/g' | tr -d ' '| tr '-' ' ' > export_mzk.ids.isbn
	grep -P "^[^\s]*\s020\s" export_nkp.ids | grep "\$\$a" | tr -d '-' | sed -e 's/^\(.*\)\s020\s*L\s\$\$a\([X0-9 ]*\)\([^X0-9 ].*\|$\)/\1-\2/g' | tr -d ' '| tr '-' ' ' > export_nkp.ids.isbn
	grep -P "^[^\s]*\s035\s" export_mzk.ids | grep "\$\$a" | tr -d '-' | sed -e 's/^\(.*\)\s035\s*L\s\$\$a(OCoLC)\([0-9]*\)\([^0-9].*\|$\)/\1 \2/g' > export_mzk.ids.oclc
	grep -P "^[^\s]*\s035\s" export_nkp.ids | grep "\$\$a" | tr -d '-' | sed -e 's/^\(.*\)\s035\s*L\s\$\$a(OCoLC)\([0-9]*\)\([^0-9].*\|$\)/\1 \2/g' > export_nkp.ids.oclc
}

# Ziskani lokalnich ID na zaklade CNB, ISBN a OCLC

get_local_ids () {
	CNB=`grep '<cnb>' split/$1 | sed -e 's/<cnb>\(cnb\)\?\(.*\)<\/cnb>/\2/g'`
	ISBN=`grep '<ean13>' split/$1 | sed -e 's/<ean13>\(.*\)<\/ean13>/\1/g'`
	OCLC=`grep '<oclc>' split/$1 | sed -e 's/<oclc>\((OCoLC)\)\?\(.*\)<\/oclc>/\2/g'`

	CNB_MATCH=""
	ISBN_MATCH=""
	OCLC_MATCH=""

	# Ziskani vsech ID pro dany zaznam z obalek knih

	if [ ! -z "$CNB" ];
	then
		CNB_MATCH=`grep "$CNB$" *.cnb`
	fi

	if [ ! -z "$ISBN" ];
	then
		ISBN_MATCH=`grep "$ISBN$" *.isbn`
	fi

	if [ ! -z "$OCLC" ];
	then
		OCLC_MATCH=`grep "$OCLC$" *.oclc`
	fi

	# Vyhledani ziskanych ID v pomocnych souborech

	DOTS=`echo "$CNB_MATCH $ISBN_MATCH $OCLC_MATCH" | grep -o "[^ :]*:[^ :]*"`

	IFS=' ' read -r -a ARR <<< `echo $DOTS | sed -E -e 's/[[:blank:]]+/ /g'`
	
	for STRING in "${ARR[@]}"
	do
		FILE_NAME=`echo $STRING | grep -o "^[^ :]*ids" | sed 's/\.ids/\.mrc/g'`
		FILE_NAMES[$FILE_NAME]=""
	done

	for STRING in "${ARR[@]}"
	do
		FILE_NAME=`echo $STRING | grep -o "^[^ :]*ids" | sed 's/\.ids/\.mrc/g'`
		ID_NAME=`echo $STRING | grep -o "[^ :]*$"`
		FILE_NAMES[$FILE_NAME]="${FILE_NAMES[$FILE_NAME]} $ID_NAME"
	done

	# Odstranovani duplicitnich ID

	for KEY in "${!FILE_NAMES[@]}"
	do
		UNIQUE=`echo ${FILE_NAMES[$KEY]} | sed 's/^ //g' | tr ' ' '\n' | sort -u`
		FILE_NAMES[$KEY]="$UNIQUE"
	done
}

# Funkce pro vypis nalezenych lokalnich ID

print_ids () {
	echo "=== ID zaznamu v souboru okcz_toc.xml ==="
	BOOK_ID=`grep '<book_id>' split/$1 | sed -e 's/<book_id>\(.*\)<\/book_id>/\1/g'`
	echo "$BOOK_ID"
	for KEY in "${!FILE_NAMES[@]}"
	do
		echo "=== Odpovidajici ID zaznamu v souboru $KEY ==="
		echo "${FILE_NAMES[$KEY]}"
	done
}

# Funkce pro vypis zaznamu ve formatu MARC21 pro dany zaznam z obalek knih

print_records () {
	for KEY in "${!FILE_NAMES[@]}"
	do
		echo "=== Odpovidajici zaznam v souboru $KEY ==="
		grep "^${FILE_NAMES[$KEY]}" $KEY
	done
}

# Funkce pro vypis jmena autora dane knihy.

print_author () {
	for KEY in "${!FILE_NAMES[@]}"
	do	
		AUTHOR=`grep "^${FILE_NAMES[$KEY]}" $KEY | grep -P "^[^\s]*\s(100)" | sed -e 's/^.*\s100[0-9]\?\s*L\s\$\$a\([[:alpha:] ,]*\)\$\$.*/\1/g' | sed 's/,$//' | sed -e 's/\([[:alpha:]]*\), \([[:alpha:]]*\)/\2 \1/'`
		if [ ! -z "$AUTHOR" ];
		then
			echo "=== Jmeno autora v souboru $KEY ==="
			echo "$AUTHOR"
		fi
	done
}

# Funkce pro analyzu obsahu knihy, na vystup vypise nalezena jmena.

analyze_book () {
	echo "=== Nejvyznamnejsi nalezena jmena ==="
	grep -o -f names "split/$1" | sed 's/$/\( [[:upper:]][[:lower:]]+| [[:upper:]]\\.\)\{1,2\}/g' | sort -u > tmp_grep_$1
	grep -E -o -f tmp_grep_$1 "split/$1" | grep -v "^$AUTHOR" | LC_ALL=C sort | LC_ALL=C uniq -c | sort -nr | sed -e 's/^[[:blank:]]*\([[:digit:]]*\)[[:blank:]]\([[:alnum:] \.]*\)/\2\t\1/'
#	grep -E -o -f tmp_grep_$1 "split/$1" | LC_ALL=C sort | LC_ALL=C uniq -c | sort -nr | sed -e 's/^[[:blank:]]*\([[:digit:]]*\)[[:blank:]]\([[:alnum:] \.]*\)/\2\t\1/'
	rm tmp_grep_$1
}

# Funkce pro tisk napovedy

help_function () {
   echo "Usage: $0 [ -h | -p | -m | -s FILE_NAME | -a FILE_NAME | -r | -x]"
   echo -e "\t-h Vypise tuto napovedu."
   echo -e "\t-p Provede predzpracovani dat. Muze trvat nekolik hodin."
   echo -e "\t-m Vypise seznam nazvu souboru razenych dle cetnosti vyskytu jmen."
   echo -e "\t-s FILE_NAME Vypise nalezene MARC21 zaznamy pro zaznam v souboru FILE_NAME."
   echo -e "\t-a FILE_NAME Vypise nalezena jmena z obsahu knihy pro zaznam v souboru FILE_NAME."
   echo -e "\t-r Smaze docasne predzpracovane soubory."
   echo -e "\t-x Hromadne zpracovani vsech zaznamu z okcz_toc.xml."
   exit 1
}

# Hlavni vetev programu

while getopts "pms:ha:rx" opt
do
	case "$opt" in
		p)
			preprocess_data
			find_names
			preprocess_ids
			;;
		m)
			print_files_with_names
			;;
		s)
			declare -A FILE_NAMES
			get_local_ids "$OPTARG"
			print_ids "$OPTARG"
			print_records "$OPTARG"
			unset FILE_NAMES
			;;
		h)
			help_function
			;;
		a)
			declare -A FILE_NAMES
			declare AUTHOR
			get_local_ids "$OPTARG"
			print_author "$OPTARG"
			analyze_book "$OPTARG"
			unset FILE_NAMES
			unset AUTHOR
			;;
		r)
			rm list list.sorted
			rm okcz_toc_preprocessed.xml
			rm export_*ids*
			rm occurences*
			rm -r processed/
			rm -r split/
			;;
		x)
			process_all_data
			;;
		?)
			help_function
	esac
done

shift $((OPTIND-1))

