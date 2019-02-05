#!/usr/bin/env python2
#
# Sample program to extract columns from the metadata file
# so that the values can be checked for consistency.
# Usage:
# ./metadata_read_test.py  # will display the column names from the CSV file
# ./metadata_read_test.py filename # use the given filename instead of the filename below
# ./metadata_read_test.py filename columnname # display the content of the named column
# ./metadata_read_test.py '' columnname # ditto but without needing to specify the filename

import csv
import sys

filename="metadata_FK_export190127.csv"
column_to_display=''

if len(sys.argv) > 1:
	if len(sys.argv[1]) > 1:
		filename = sys.argv[1]
if len(sys.argv) > 2:
	column_to_display = sys.argv[2]

fp = open(filename)
reader = csv.DictReader(fp)

if not column_to_display:
	print(reader.fieldnames)

for row in reader:
	# To show the keywords, split by comma, printed one per line
	#keywords = row['keywords']
	#keywords_list = keywords.split(',')
	#for k in keywords_list:
	#	print(k)
	# To show the status (0/1) and name
	#print("%s %s" % (row['status'] , row['title']))
	# To show the limitations_access
	if column_to_display:
		print(row[column_to_display])
exit(0)
