#!/bin/sh

# Project: nkp_authorities
# Author: Pavel Raur, xraurp00@stud.fit.vutbr.cz
# Description: automatic conversion and kb creation from downloaded files

# create tsv from xml files
python3 parseXML.py -f records/*.xml -o nkp_authorities_kb.tsv

# change working directory
cd kb_creation

# start merging wikipedia and nkp kbs
sh start.sh

