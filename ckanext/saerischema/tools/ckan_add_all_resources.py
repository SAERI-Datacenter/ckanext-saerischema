#!/usr/bin/env python
# 1.00 arb Sun 24 Mar 22:02:15 GMT 2019
# Read a CSV file of metadata, look in the column 'original_title _dataportal'
# and find the files referenced within. If Shapefile then create a zip archive.
# Then determine if the files are restricted in any way.
# Then upload using the script  ckan_add_resource_to_dataset.py

from __future__ import print_function
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
column_name_containing_resource_path = 'original_title _dataportal'
default_allowed_users='saeri,ilaria,arb'
default_restriction_method = 'only_allowed_users'
repo_dir = '/mnt/datastore'
tmp_dir = "/tmp"
file_srs = ''
file_restriction = ''
file_allowed_users = ''
only_add_first_entry = False
debug = True

# When zipping a shapefile include all associated files with these extensions
shape_file_extension_list = [
	'shp', 'shx', 'dbf', 'sbn', 'sbx', 'atx',
	'fbn', 'fbx', 'ain', 'aih', 'ixs', 'mxs', 'prj', 'xml', 'cpg']

# Map file extension (WITH dot) to CKAN type
# Only list the ones which aren't simply the same as the file extension
file_ext_to_type_map = {
	'tif'  : 'GeoTIFF',
	'tiff' : 'GeoTIFF',
	'jpg'  : 'JPEG',
}

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
	if not row[column_name_containing_resource_path]:
		continue
	#print(row)

	# Determine the file(s) to be uploaded
	# NOTE: file_name is full path, file_basename is full path without ext, file_ext has dot removed
	file_name = os.path.join(repo_dir, row[column_name_containing_resource_path])
	(file_basename, file_ext) = os.path.splitext(file_name)
	file_ext = file_ext.replace('.', '') # remove the dot

	# Map a range of other file extensions to CKAN file types
	# File type as given to CKAN shall be uppercase unless it's a word
	if file_ext.lower() in file_ext_to_type_map:
		file_type = file_ext_to_type_map[file_ext.lower()]
	else:
		file_type = file_ext.upper()

	if not os.path.isfile(file_name):
		file_name = os.path.basename(file_name)
		if not os.path.isfile(file_name):
			# not even found in current directory
			print("File not found %s - for dataset %s" % (file_name, row['title']))
			continue

	# See if Shapefiles need to be zipped
	zip_file_name = ''
	if file_ext.lower() == 'shp':
		# Remove .shp and look for all other related files
		files_to_zip = []
		for ext in shape_file_extension_list:
			if os.path.isfile(file_basename + '.' + ext):
				files_to_zip.append(file_basename + '.' + ext)
		# A temporary zip file is created from the shapefile basename
		zip_file_name = os.path.join(tmp_dir, os.path.basename(file_basename) + '.zip')
		if debug: print("Zipping %s from %s" % (zip_file_name, files_to_zip))
		zip = zipfile.ZipFile(zip_file_name, mode = 'w', compression = zipfile.ZIP_DEFLATED, allowZip64 = True)
		for fn in files_to_zip:
			zip.write(fn, os.path.basename(fn))
		file_name = zip_file_name
		file_type = 'Shapefile'

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

	cmd = "%s -d '%s' -f '%s' -t '%s'" % (upload_prog, dataset_name, file_name, file_type)
	if file_srs:
		cmd += " -s '%s'" % file_srs
	if file_restriction:
		cmd += " -r '%s'" % file_restriction
	if file_allowed_users:
		cmd += " -u '%s'" % file_allowed_users
	if debug: print("Running %s" % cmd)
	rc = os.system(cmd)
	if rc > 0:
		print("ERROR %d uploading '%s' to '%s' with command %s" % (rc, file_name, dataset_name, cmd), file=sys.stderr)
		exit(1)

	if zip_file_name:
		#print("remove zip %s" % zip_file_name)
		os.unlink(zip_file_name)

	# Stop after the first row?
	if only_add_first_entry:
		break

# Close
fp.close()

exit(0)
