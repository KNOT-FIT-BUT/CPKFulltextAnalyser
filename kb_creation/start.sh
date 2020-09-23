#!/bin/sh

# Project: nkp_authorities
# Author: Pavel Raur, xraurp00@stud.fit.vutbr.cz
# Description: automatic kb creation

# get wikipedia KB
curl -O http://athena3.fit.vutbr.cz/kb/KBstatsMetrics.all || echo "Failed to get KBstatsMetrics.all, old version will be used if already present in comparison folder!" >&2

if [ -f KBstatsMetrics.all ] && [ -r KBstatsMetrics.all ]; then
	# get person entities from kb
	awk -F'\t' '{ if($2=="person") print }' KBstatsMetrics.all > PERSONS
	# get artists entities from kb
	awk -F'\t' '{ if($2=="person+artist") print }' KBstatsMetrics.all > ARTISTS
	# get geographical entities
	awk -F'\t' '{ if($2=="location") print }' KBstatsMetrics.all > LOCATIONS
else
	echo "KBstatsMerics.all is not accessible!" >&2
	exit 1
fi

# get nkp persons entities
if [ -f ../persons.tsv ] && [ -r ../persons.tsv ]; then
	cp ../persons.tsv ./NKP
else
	if [ ! -f NKP ] || [ ! -r NKP ]; then
		echo "NKP persons KB missing or unreadable!" >&2
		exit 1
	fi
	echo "Failed to get new NKP persons KB, old version will be used!" >&2
fi
# get nkp geographical entities
if [ -f ../geo.tsv ] && [ -r ../geo.tsv ]; then
	cp ../geo.tsv ./GEO
else
	if [ ! -f GEO ] || [ ! -r GEO ]; then
		echo "NKP geographical locations KB is missing or unreadable!" >&2
		exit 1
	fi
	echo "Failed to get new NKP geographical locations KB, old version will be used!" >&2
fi

# create persons kb
# output file is personsKB.tsv
../CPKLinkedOpenDataLinker/NER/KnowBase/kb_compare.py --first=PERSONS --second=NKP --rel_conf=nkp_persons_rel.conf --output_conf=personsKB_output.conf --output=personsKB --id_prefix=p --other_output_conf=personsKB_other_output.conf --treshold=2

# add artists to person kb
# output file is KB.tsv
../CPKLinkedOpenDataLinker/NER/KnowBase/kb_compare.py --first=ARTISTS --second=personsKB --rel_conf=nkp_artists_rel.conf --output_conf=KB_output.conf --output=KB.tsv --id_prefix=p --other_output_conf=KB_other_output.conf --treshold=2

# create geo kb
../CPKLinkedOpenDataLinker/NER/KnowBase/kb_compare.py --first=LOCATIONS --second=GEO --rel_conf=nkp_geo_rel.conf --output_conf=geoKB_output.conf --output=geoKB.tsv --id_prefix=l --other_output_conf=geoKB_other_output.conf --treshold=2

# Get person entities with added link
awk -F'\t' '{ if($18!="" && $19!="") print }' KB.tsv | awk -F'\t' '{ if($8~"https?:\/\/.+\.wikipedi(a|e)\.org\/wiki\/.*") print }' > entitiesWithAddedWikipediaLink.tsv

# Get geo entities with added link
awk -F'\t' '{ if($12!="" && $13!="") print }' geoKB.tsv | awk -F'\t' '{ if($11~"https?:\/\/.+\.wikipedi(a|e)\.org\/wiki\/.*") print }' > geoEntitiesWithAddedWikipediaLink.tsv
