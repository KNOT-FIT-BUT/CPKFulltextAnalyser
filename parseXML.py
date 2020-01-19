#!/usr/bin/env python3
# encoding UTF-8

# Author: Pavel Raur
# Project: nkp_authorities
# Description: creates tsv file from extracted xml files

import re
import time
import sys
import argparse
import xml.etree.ElementTree as ET
import urllib.parse as urlparse

# NAMESPACES - xml namespaces used in nkp xml files
NS = {
	'default' : 'http://www.openarchives.org/OAI/2.0/',
	'marc'    : 'http://www.loc.gov/MARC21/slim'
}

# parses arguments and returns them as target_var.argument_name
# for example '--file' argument is returned as target_var.file
def getArgs():
	argparser = argparse.ArgumentParser(
		description='Parses data from nkp XML files.'
		)
	argparser.add_argument('-f', '--input_files',
		help='XML files to parse.',
		nargs='+',
		required=True)
	argparser.add_argument('-o', '--output_file',
		help='TSV output file.',
		type=argparse.FileType('w'),
		required=True)
	return argparser.parse_args()

# generate tsv line
def writeEntityToTsvFile(entity, file):
	# add tab after each field
	for i in range(0, len(entity)-1):
		file.write(entity[i] + '\t')
	# add newline after last field
	file.write(entity[-1] + '\n')


# Modify name to match wikipedia format
def generateName(nameType, name, number, title):
	if nameType == '3': # Family name
		return name
	
	# nameType == '0' or '1'
	# information about type is sometimes missing,
	# this part checks format and modifies it for
	# compatibility with wikipedia format

	# Remove comma from number and add space in front of it
	if number != '':
		number = " " + (number[:-1] if number[-1] == ',' else number)
	# check if name is in format: surename, name,
	# remove commas and switch order
	tmp = name.split(', ')
	# split returns 1 element if there is no comma with space after it
	if len(tmp) > 1:
		name = (tmp[-1][:-1] if tmp[-1][-1] == ',' else tmp[-1]) + " " + tmp[0]

	# add space after the title
	if title != "":
		title += " "

	return title + name + number

# Generates field with multiple values, separated with '|'
def generateMultipleValueField(*args):
	# result is like 'arg1|arg2|arg3'
	# join all args that are not empty string
	return '|'.join(arg for arg in args if arg)

# changes format of the date from DD-MM-YYYY to YYYY-MM-DD
# this is for compatibility with wikipedia kb
def correctDateFormat(date):
	if not date: # empty input
		return ''

	date = date.split('.') # '23. 8. 1992' -> ['23'][' 8'][' 1992']

	for i in range(0, len(date)):
		# remove all whitespaces in fron and arter each number
		date[i] = date[i].strip() # ['23'][' 8'][' 1992'] -> ['23']['8']['1992']

		# add 0 in front of 1 digit number:
		# ['23']['8']['1992'] -> ['23']['08']['1992']
		if len(date[i]) == 1:
			date[i] = '0' + date[i]

	# DD.MM.YYYY -> YYYY-MM-DD
	if len(date) == 3: # ['23']['08']['1992'] -> '1992-08-23'
		return date[2] + '-' + date[1] + '-' + date[0]

	# Year only: YYYY -> YYYY-??-??
	elif len(date) == 1: # ['1992'] -> '1992-??-??'
		return date[0] + '-??-??'
	
	else: # bad format
		return ''

# Parses date of birth and death from datafield 100 - d
# returns tuple (date of birth, date of death)
def getDateFrom100(fieldValue):
	if not fieldValue:
		return '',''
	# not date of birth/death
	if re.search("činný|Činný", fieldValue):
		return '',''
	
	fieldValue = fieldValue.split('-', 1)

	# if split fails because there is only one of the dates
	if len(fieldValue) == 1:
		# search for birth
		if re.search("(N|n)arozen[ýá]?|(N|n)ar\.", fieldValue[0]):
			# append empty death
			fieldValue.append("")
		# search for death
		elif re.search("(Z|z)emřela?|(Ú|ú)mrtí", fieldValue[0]):
			# add it as second field and clear first field = birth/death
			fieldValue.append(fieldValue[0])
			fieldValue[0] = ""
		# cannot determine - return empty
		else:
			return '',''
	# extract date
	# if there is no value, AttribudeError is cautched
	# and emptystring is assigned
	try: # birth
		fieldValue[0] = re.search("[0-9]{4}", fieldValue[0]).group()
	except AttributeError:
		fieldValue[0] = ""
	try: # death
		fieldValue[1] = re.search("[0-9]{4}", fieldValue[1]).group()
	except AttributeError:
		fieldValue[1] = ""
	return fieldValue[0], fieldValue[1]


# Parses date of birth and death from datafield 678 - a
# returns tuple (date of birth, date of death)
def getDateFrom678(fieldValue):
	if not fieldValue:
		return '',''

	try:
		birth = re.search("((N|n)arozen[ýá]?|(N|n)ar\.)\s?([0-9]{1,2}\.\s?[0-9]{1,2}\.\s?[0-9]{4}|[0-9]{4})", fieldValue).group()
		birth = re.search("([0-9]{1,2}\.\s?[0-9]{1,2}\.\s?[0-9]{4}|[0-9]{4})", birth).group()
	except AttributeError:
		birth = ""

	try:
		death = re.search("((Z|z)emřela?|(Ú|ú)mrtí)\s?([0-9]{1,2}\.\s?[0-9]{1,2}\.\s?[0-9]{4}|[0-9]{4})", fieldValue).group()
		death = re.search("([0-9]{1,2}\.\s?[0-9]{1,2}\.\s?[0-9]{4}|[0-9]{4})", death).group()
	except AttributeError:
		death = ""

	return birth, death

# Converts url to readable form
#  and changes http to https if its wikipedia url
def fixURL(url):
	if not url:
		return ""

	url = urlparse.unquote(url)

	if re.match("http:\/\/.+\.wikipedi(a|e)\.org\/wiki\/.*", url):
		url = re.sub("http:", "https:", url)

	return url


# parse target nkp_authorities xml file
# returns tuple: number of parsed entities and error value
# error value = 0 if success else 1
def parseFile(input_file, output_file):
	counter = 0 # counter of parsed entities
	corrupted = 0 # corrupted records
	try:
		xmlTree = ET.parse(input_file) # process xml file
		root = xmlTree.getroot() # get xml root element
	except:
		sys.stderr.write("Failed to process XML file: " + input_file.name + "\n")
		return counter, corrupted, 1

	try:
		# stores all records from ListRecords element
		records = root.find('default:ListRecords', NS).findall('default:record', NS)

		# parse each record
		for record in records:

			# stores currently parsed entity data
			# field description / documentation:
			# https://autority.nkp.cz/jmenne-autority/metodicke-materialy/metodika-jmena-cvicne-2
			# 0 ID (controlfield 001 - entity control number)
			# 1 Date of birth (datafield 046 - subfield f)
			# 2 Date of death (datafield 046 - subfield g)
			#     inforations are usually missing in datafield 046,
			#     these fields can store date too, but must be parsed
			#     from text:
			#     (datafield 100 - subfield d)
			#     (datafield 678 - subfield a)
			tmpDate  = [ '','' ]
			tmpDate2 = ""
			tmpDate3 = ""
			# 3 Name (
			#     (datafield 100)
			#nameType = "" # (tag ind1)
			#name     = "" # (subfield a)
			#number   = "" # (subfield b)
			#     (datafield 368)
			#title    = "" # (subfield d) - title is not used, its not
			#                               compatible with wikipedia format
			# )
			# 4 Other designation (datafield 368 - subfield c) (Multiple)
			# 5 Place of birth (datafield 370 - subfield a)
			# 6 Place of death (datafield 370 - subfield b)
			# 7 Related countries (datafield 370 - subfield c) (Multiple)
			# 8 Related places (datafield 370 - subfield f) (Multiple)
			# 9 Field of activity (datafield 372 - subfield a) (Multiple)
			# 10 Gender (datafield 375 - subfield a)
			# 11 Other name (
			#     (datafield 400)
			#nameType = "" # (tag ind1)
			#name     = "" # (subfield a)
			#number   = "" # (subfield b)
			# ) (Multiple)
			# 12 general note (datafield 678 - subfield a)
			# 13 link (datafield 856 - subfield u) (Multiple)
			# 14 Affiliation (datafield 373 - subfield a) (Multiple)
			# 15 Profession (datafield 374 - subfield a) (Multiple)

			# Entity instance initialization - default values are empty strings
			entity = [ '','','','','','','','','','','','','','','','' ]
			
			# stores relevant record data (from elements: metadata - record)
			try:
				data = record.find('default:metadata', NS).find('marc:record', NS)

				controlfields = data.findall('marc:controlfield', NS)
				datafields = data.findall('marc:datafield', NS)

			except AttributeError as e:
				sys.stderr.write("Corrupted record found!\n")
				corrupted += 1
				continue

			# === BEGINING OF DATA EXTRACTION ===

			# 0 ID
			for controlfield in controlfields:
				if controlfield.attrib['tag'] == '001':
					entity[0] = controlfield.text

			for datafield in datafields:
				# 1 Date of birth
				# 2 Date of death
				if datafield.attrib['tag'] == '046':
					for subfield in datafield:
						# 1
						if subfield.attrib['code'] == 'f':
							tmpDate[0] = subfield.text
						# 2
						if subfield.attrib['code'] == 'g':
							tmpDate[1] = subfield.text

				# 3 Name - nameType, name, number
				# 1, 2 alternative
				if datafield.attrib['tag'] == '100':

					# clearing temp variables from previous iterations
					nameType = ""
					name     = ""
					number   = ""

					nameType = datafield.attrib['ind1']
					for subfield in datafield:

						if subfield.attrib['code'] == 'a':
							name = subfield.text

						if subfield.attrib['code'] == 'b':
							number = subfield.text
						# 1, 2
						if subfield.attrib['code'] == 'd':
							tmpDate2 = subfield.text

					# 3
					entity[3] = generateName(nameType, name, number, "")

				# 3 Name - title
				# 4 Other designation
				if datafield.attrib['tag'] == '368':
					for subfield in datafield:
						# 4
						if subfield.attrib['code'] == 'c':
							entity[4] = generateMultipleValueField(
								entity[4], subfield.text)
						
						# Title is not used
						# 3
						#if subfield.attrib['code'] == 'd':
						#	title = subfield.text

				# 5 Place of birth
				# 6 Place of death
				# 7 Related countries
				# 8 Related places
				if datafield.attrib['tag'] == '370':
					for subfield in datafield:
						# 5
						if subfield.attrib['code'] == 'a':
							entity[5] = subfield.text
						# 6
						if subfield.attrib['code'] == 'b':
							entity[6] = subfield.text
						# 7
						if subfield.attrib['code'] == 'c':
							entity[7] = generateMultipleValueField(
								entity[7], subfield.text)
						# 8
						if subfield.attrib['code'] == 'f':
							entity[8] = generateMultipleValueField(
								entity[8], subfield.text)

				# 9 Field of activity
				if datafield.attrib['tag'] == '372':
					for subfield in datafield:
						if subfield.attrib['code'] == 'a':
							entity[9] = generateMultipleValueField(
								entity[9], subfield.text)

				# 14 Affiliation
				if datafield.attrib['tag'] == '373':
					for subfield in datafield:
						if subfield.attrib['code'] == 'a':
							entity[14] = generateMultipleValueField(
								entity[14], subfield.text)
				# 15 Profession
				if datafield.attrib['tag'] == '374':
					for subfield in datafield:
						if subfield.attrib['code'] == 'a':
							entity[15] = generateMultipleValueField(
								entity[15], subfield.text)

				# 10 Gender
				if datafield.attrib['tag'] == '375':
					for subfield in datafield:
						if subfield.attrib['code'] == 'a':
							entity[10] = subfield.text

				# 11 Other name
				if datafield.attrib['tag'] == '400':

					# clearing temp variables from previous iterations
					nameType = ""
					name     = ""
					number   = ""

					nameType = datafield.attrib['ind1']
					for subfield in datafield:

						if subfield.attrib['code'] == 'a':
							name = subfield.text

						if subfield.attrib['code'] == 'b':
							number = subfield.text

					entity[11] = generateMultipleValueField(
						entity[11], generateName(nameType, name, number, ""))

				# 12 General note
				if datafield.attrib['tag'] == '678':
					for subfield in datafield:
						if subfield.attrib['code'] == 'a':
							entity[12] = subfield.text

				# 13 link
				if datafield.attrib['tag'] == '856':
					for subfield in datafield:
						if subfield.attrib['code'] == 'u':
							entity[13] = fixURL(subfield.text)

			# (for datafield in datafields:) -- END
			
			# 1, 2, Date of birth, Date of Death
			# Get date from general note
			# only this field contains full date in format DD.MM.YYYY
			# so it is used as first option
			tmpDate3 = getDateFrom678(entity[12])
			entity[1] = correctDateFormat(tmpDate3[0])
			entity[2] = correctDateFormat(tmpDate3[1])

			# Alternative - get date from name field 100 - year only
			tmpDate2 = getDateFrom100(tmpDate2)
			if not entity[1]:
				entity[1] = correctDateFormat(tmpDate2[0])
			if not entity[2]:
				entity[2] = correctDateFormat(tmpDate2[1])

			# Alternative 2 - get date form 046 field - year only
			if not entity[1]:
				entity[1] = correctDateFormat(tmpDate[0])
			if not entity[2]:
				entity[2] = correctDateFormat(tmpDate[1])

			# Creates tsv output
			writeEntityToTsvFile(entity, output_file)
			counter += 1
			# (for record in records:) -- END


	except TypeError as e:
		sys.stderr.write("Parsing error: " + str(e) + "\n")
		return counter, corrupted, 1

	return counter, corrupted, 0

def main():
	entityCounter = 0 # total number of extracted entities
	corruptedEntityCounter = 0 # total number of bad entities
	cor = 0 # used to store number of corrupted entities in current file
	err = 0 # used to store error code of parseFile function
	num = 0 # used to store number of entities parsed from current file
	numberOfFiles = 0 # processed files counter

	args = getArgs() # get arguments in format args.argument_name
	output = args.output_file # output file

	corrupedFiles = [] # files that cannot be parsed
	damagedFiles = [] # contains bad entities but can be parsed

	timestamp1 = time.time()
	print("Begining of extraction: " + time.ctime(timestamp1))

	for filename in args.input_files:
		numberOfFiles += 1

		try:
			file = open(filename, "r")
		except:
			sys.stderr.write("Failed to open XML file: " + filename + "\n")
			corruptedFiles.append(filename)
		else:
			# parse the file
			num, cor, err = parseFile(file, output)
			entityCounter += num
			corruptedEntityCounter += cor

			if err: # warning about bad files
				corrupedFiles.append(filename)
				sys.stderr.write("File cannot be parsed properly: "
					+ str(file.name) + "\n"
					+ str(num) + " entities form file parsed!\n")

			elif cor: # warning about demaged files
				damagedFiles.append(filename)
				sys.stderr.write("File contains " + str(cor) + " corruped entities: "
					+ str(file.name) + "\n"
					+ str(num) + " entities from file parsed!\n")

			file.close()
	# (for file in args.input_files:)

	timestamp2 = time.time()

	print("End of extraction: " + time.ctime(timestamp2))
	print("Number of parsed entities: " + str(entityCounter))
	print("Number of files parsed: " + str(numberOfFiles))
	print("Total time: " + str(round(timestamp2-timestamp1, 2)) + "s")

	if corrupedFiles: # prints corrupted file list
		print("Corrupted files: " + str(len(corrupedFiles)) + " :")
		for f in corrupedFiles:
			print(f)

	if damagedFiles: # prints list of files with damaged entities
		print("Files with corruped entities: " + str(len(damagedFiles)) + " :")
		for f in damagedFiles:
			print(f)

	return 0

if __name__ == "__main__":
	sys.exit(main())