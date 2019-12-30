#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import datetime
import glob
import shutil
import os
import regex
import subprocess
import sys

ENT_TYPES_PERSON = ['person', 'person:fictional', 'person:group']
ENT_TYPES_LOCATION = ['country', 'country:former', 'settlement', 'watercourse', 'waterarea', 'geo:relief', 'geo:waterfall', 'geo:island', 'geo:peninsula', 'geo:continent']

def get_absolute(interested, basedir = os.getcwd()):
  if not os.path.isabs(interested):
    interested = os.path.join(basedir, interested)
  return interested

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--inputs', nargs = '+', type = str, required = True, help = 'Input file(s) to get subject headings.')
parser.add_argument('-o', '--output_dir', type = str, required = False, default = 'outputs', help = 'Output directory, where subject headings files will be created (if does not exist, it will be created).')
parser.add_argument('-n', '--ner', type = str, required = False, default = 'ner_cz.py', help = 'NER python script path and arguments for NER running (default: %(default)s).')
parser.add_argument('-p', '--preserve-paging', action = 'store_true', help = 'Disable functionality, which tries to remove paging from names in working file (Example: Jan 5 Novak => Jan Novak).')
parser.add_argument('-d', '--preserve-wordbreaking', action = 'store_true', help = 'Disable functionality which tries to remove word breaking from names in working file (Example: Jan No- vak => Jan Novak).')
parser.add_argument('-x', '--preserve-aliases', action = 'store_true', help = 'Disable functionality which ignores of names aliases.')
args = parser.parse_args()

out_dir = get_absolute(args.output_dir)
ner = get_absolute(args.ner)
ner_dir = os.path.dirname(ner)
kb = os.path.join(ner_dir, './KB-HEAD.all')

os.makedirs(out_dir, exist_ok = True)

is_input = False

for in_path in args.inputs:
  for in_file in glob.glob(in_path):
    is_input = True
    in_dir = os.path.dirname(in_file)
    basename = os.path.basename(in_file)
    working_file = os.path.join(out_dir, '.{}.working'.format(basename))
    out_base = os.path.join(out_dir, basename)

    persons = dict()
    locations = dict()      

    if (not args.preserve_paging) or (not args.preserve_wordbreaking):
      with open(in_file, 'r') as f_in:
        with open(working_file, 'w') as f_working:
          for line in f_in:
            if not args.preserve_paging:
              line = regex.sub(r'(\p{Lu}\p{Ll}+)\s+[0-9]+\s+(\p{Lu})', r'\1 \2', line)
            if not args.preserve_wordbreaking:
              line = regex.sub(r'(\p{Lu}\p{Ll}+)(?:-|—)\s+(?!und |and |a )(\p{Ll})', r'\1\2', line)
            f_working.write(line)
    else:
      shutil.copy(in_file, working_file)

    print('{}   [INFO]: processing "{}" ...'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), in_file), flush = True)

    p_ner = subprocess.Popen('python {} -f "{}"'.format(ner, working_file), shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

    for line in p_ner.stdout:
      ln_cols = line.decode().strip('\n').split('\t')
      if len(ln_cols) == 5 and ln_cols[2] == 'kb':
        entity_name = ln_cols[3]
        
        p_kb = subprocess.Popen('sed "1,/^$/ d" "{}" | sed "{}q;d"'.format(kb, ln_cols[4]), shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        ent_cols = p_kb.stdout.read().decode().strip('\n').split('\t')
        ln_ent_type = ent_cols[1]

        if not args.preserve_aliases:
          for alias in ent_cols[4].split('|'):
            if regex.sub(r'#(lang|ntype).*', '', alias) == entity_name and entity_name not in [ent_cols[2], ent_cols[3]]:
              entity_name = None
              break

        if entity_name and ln_ent_type in ENT_TYPES_PERSON:
            persons[entity_name] = 0 if entity_name not in persons else persons[entity_name] + 1
        elif entity_name and ln_ent_type in ENT_TYPES_LOCATION:
          locations[entity_name] = 0 if entity_name not in locations else locations[entity_name] + 1

    if persons:
      with open('{}.600'.format(out_base), 'w') as f:
        f.write('\n'.join([k for k in sorted(persons, key = persons.get, reverse = True)]))
    if locations:
      with open('{}.610'.format(out_base), 'w') as f:
        f.write('\n'.join([k for k in sorted(locations, key = locations.get, reverse = True)]))
    os.remove(working_file)

if not is_input:
  print('No suitable input for processing...', file = sys.stderr, flush = True)
  sys.exit(1)
