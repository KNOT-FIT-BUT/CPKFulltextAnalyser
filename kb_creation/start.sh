#!/bin/sh

# Project: nkp_authorities
# Author: Pavel Raur, xraurp00@stud.fit.vutbr.cz
# Description: automatic kb creation

# get wikipedia KB
curl -O http://athena3.fit.vutbr.cz/kb/KBstatsMetrics.all || echo "Failed to get KBstatsMetrics.all, old version will be used if already present in comparison folder!" >&2

if [ -f KBstatsMetrics.all ] && [ -r KBstatsMetrics.all ]; then
	# get person entities from kb
	awk -F'\t' '{ if($2~"person:?") print }' KBstatsMetrics.all > PERSONS
else
	echo "KBstatsMerics.all is not accessible! Exiting!" >&2
fi

# get nkp kb
if [ -f ../nkp_authorities_kb.tsv ] && [ -r ../nkp_authorities_kb.tsv ]; then
	cp ../nkp_authorities_kb.tsv ./NKP
else
	echo "Failed to get nkp_authorities_kb.tsv, old version will be used if already present in comparison folder!" >&2
fi

# create kb
# output file is KB.tsv
../CPKLinkedOpenDataLinker/NER/KnowBase/kb_compare.py --first=PERSONS --second=NKP --rel_conf=nkp_persons_rel.conf --output_conf=KB_output.conf --output=KB.tsv --id_prefix=p --other_output_conf=KB_other_output.conf --treshold=2

awk -F'\t' '{ if($18!="" && $19!="") print }' KB.tsv | awk -F'\t' '{ if($8~"https?:\/\/.+\.wikipedi(a|e)\.org\/wiki\/.*") print }' > entitiesWithAddedWikipediaLink.tsv

