#!/usr/bin/env python
# 1.00 arb Sun 24 Mar 22:02:15 GMT 2019
# Read a CSV file of metadata, look in the column 'original_title _dataportal'
# and find the files referenced within. If Shapefile then create a zip archive.
# Then determine if the files are restricted in any way.
# Then upload using the script  ckan_add_resource_to_dataset.py

import urllib2
import urllib
import json
import pprint    # for pprint.pprint
import csv       # for csv.DictReader
import re        # for re.sub() and re.match()
import getopt    # for command line arguments
import zipfile   # to zip shapefiles
# import our tools from the parent directory
import sys,os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import saerickan

# Configuration
csv_filename = 'new_montserrat_metadata_form_filled_V4IM.csv'
upload_prog = './ckan_add_resource_to_dataset.py'
repo_dir = '.'
tmp_dir = "/tmp"
file_srs = ''
file_restriction = ''
file_allowed_users = ''
only_add_first_entry = True
shape_file_extension_list = [
	'shp', 'shx', 'dbf', 'sbn', 'sbx', 'atx',
	'fbn', 'fbx', 'ain', 'aih', 'ixs', 'mxs', 'prj', 'xml', 'cpg']
default_allowed_users='saeri,ilaria,arb'
default_restriction_method = 'only_allowed_users'

# Parse command-line parameters
usage = '-c metadata.csv -r repo_dir [-s srs]\n' \
	'-c is the metadata CSV file\n' \
	'-r is the root directory of the data repository\n' \
	'-s is the SRS if the shapefile has none, eg. epsg:2004\n'
options = 'c:r:s:'

try:
    opts, args = getopt.getopt(sys.argv[1:], options)
except getopt.GetoptError:
    print("usage: %s %s" % (sys.argv[0], usage))
    sys.exit(1)
for opt,arg in opts:
	if opt == '-c':
		csv_filename = arg
	if opt == '-r':
		repo_dir = arg
	if opt == 's':
		file_srs = arg

# Read in the CSV file
fp = open(csv_filename)
reader = csv.DictReader(fp)

# Process each row
for row in reader:
	if not row['original_title _dataportal']:
		continue
	print(row)

	# Determine the file(s) to be uploaded
	file_name = repo_dir + row['original_title _dataportal']
	(file_basename, file_ext) = os.path.splitext(file_name)
	file_type = file_ext.upper()
	if file_type == 'JPG':
		file_type = 'JPEG'

	if not os.path.isfile(file_name):
		print("File not found for %s -  %s" % (row['title'], file_name))
		file_name = os.path.basename(file_name)
		if not os.path.isfile(file_name):
			# not even found in current directory
			continue

	# See if Shapefiles need to be zipped
	zip_file_name = ''
	if re.match(".*\\.[Ss][Hh][Pp]$", file_name): # ie. *.shp
		# Remove .shp and look for all other related files
		(file_basename, file_ext) = os.path.splitext(file_name)
		files_to_zip = []
		for ext in shape_file_extension_list:
			if os.path.isfile(file_basename + '.' + ext):
				files_to_zip.append(file_basename + '.' + ext)
		#print(files_to_zip)
		# A temporary zip file is created from the shapefile basename
		zip_file_name = tmp_dir + '/' + os.path.basename(file_basename) + '.zip'
		zip = zipfile.ZipFile(zip_file_name, mode = 'w', compression = zipfile.ZIP_DEFLATED, allowZip64 = True)
		for fn in files_to_zip:
			zip.write(fn, os.path.basename(fn))
		#print(zip_file_name)
		file_name = zip_file_name
		file_type = 'Shapefile'

	if re.match(".*\\.[Tt][Ii][Ff]+$", file_name): # ie. *.tif or *.tiff
		file_type = 'GeoTIFF'

	# We need to collect the following information:
	# filename, dataset name, type, srs, restriction
	#upload_to_ckan(dataset_name, file_name, file_type, file_srs, restriction, allowed_users)
	dataset_name = saerickan.saerickan_name_from_title(row['title'])

	# Determine if resource is restricted
	if row['limitations_access']:
		# Only if it's exactly 'open access' is it truly open
		if re.match("^[\s]*open access[\s]*$", row['limitations_access'], flags=re.IGNORECASE):
			file_restriction = ''
			file_allowed_users = ''
		else:
			file_restriction = default_restriction_method
			file_allowed_users = default_allowed_users
	else:
		print("Warning: no limitations_access column in CSV file")

	cmd = "%s -d '%s' -f '%s'" % (upload_prog, dataset_name, file_name)
	if file_srs:
		cmd += " -s '%s'" % file_srs
	if file_restriction:
		cmd += " -r '%s'" % file_restriction
	if file_allowed_users:
		cmd += " -a '%s'" % file_allowed_users
	print(cmd)

	if zip_file_name:
		print("remove zip %s" % zip_file_name)
		os.unlink(zip_file_name)

	# Stop after the first row?
	if only_add_first_entry:
		break

# Close
fp.close()

exit(0)
