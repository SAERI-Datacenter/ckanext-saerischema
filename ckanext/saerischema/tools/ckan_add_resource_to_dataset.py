#!/usr/bin/env python
# 1.00 arb Fri 22 Mar 00:31:40 GMT 2019 - first version
# Upload a resource to a dataset.
# NOTE: requires that the 'jq' package has been installed into the OS.
# NOTE: requires that the 'gdal-bin' package and 'python-gdal' packages have been installed.
# NOTE: requires the file to be deleted: /usr/lib/ckan/default/lib/python2.7/no-global-site-packages.txt
#  so that inside the virtualenv we can still access dist-packages provided by python-gdal.
#
# If file is a zipped shapefile then render a preview image using shp2png or gdal_rasterize
# If file is a geotiff then render a preview image using gdal_translate
# If file is a geopackage then gdal_rasterize or translate? XXX not yet implemented
# Usage: -d dataset_name  -f filename -t filetype [-r restriction [-u user,user]]
# See below for details.
# See below for configuration options.
# eg.
# ./ckan_add_resource_to_dataset.py -d test-dataset-6-title -f contours_2010.zip -t Shape
# ./ckan_add_resource_to_dataset.py -d test-dataset-6-title -f Montserrat_MBES_2m.tiff -t GeoTIFF
# To speed up:
# cp contours_2010_preview.geojson Montserrat_MBES_2m_preview.jpg /tmp
# ./ckan_add_resource_to_dataset.py -d cetacean-photo-id-original-from-doke-focal-survey-genetic-nov-2016-aug-2018 -f contours_2010.zip -t Shape
# ./ckan_add_resource_to_dataset.py -d cetacean-photo-id-original-from-doke-focal-survey-genetic-nov-2016-aug-2018 -f Montserrat_MBES_2m.tiff -t GeoTIFF

import urllib2
import urllib
import json
import pprint    # for pprint.pprint
import csv       # for csv.DictReader
import re        # for re.sub() and re.match()
import getopt    # for command line arguments
import zipfile   # for handling zipped shapefiles
from osgeo import gdal # to get dimensions of geotiff (if this errors, remove /usr/lib/ckan/default/lib/python2.7/no-global-site-packages.txt)
from osgeo import ogr  # to get SRS of a shapefile
from ckanapi import RemoteCKAN
# import our tools from the parent directory
import sys,os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import saerickan

# Configuration
# The default SRS if a Shapefile has None is Montserrat
# The default is to simplify Shapefiles into GeoJSON previews using 500m steps
shp_default_srs = 'epsg:2004'
shp_simplify_meters = 500

# The default value for all resources is public
restricted_to = 'public'
restricted_to_allowable_values = ('public', 'registered', 'any_organization', 'same_organization', 'only_allowed_users')
tmp_dir = "/tmp/" # must have trailing slash

# -----------------------------------------------------------------------
# MAIN

dataset_name = file_name = file_type = restricted_key = allowed_users = ''
preview_file_name = ''
dummy_url = 'dummy-value-for-ckan-pre-2.6'
user_agent = 'ckanapiexample/1.0 (+http://example.com/my/website)'
usage = '-d dataset_name -f filename_to_upload -t type_of_file [-r restriction [-u allowed_users]]\n-r is public, registered, any_organization, same_organization, only_allowed_users\n-u is a comma-separated list of usernames\n'
options = 'd:f:t:r:u:'

try:
    opts, args = getopt.getopt(sys.argv[1:], options)
except getopt.GetoptError:
    print("usage: %s %s" % (sys.argv[0], usage))
    sys.exit(1)
for opt,arg in opts:
	if opt == '-d':
		dataset_name = arg
	if opt == '-f':
		file_name = arg
	if opt == '-t':
		file_type = arg
	if opt == '-r':
		restricted_to = arg
		if restricted_to not in restricted_to_allowable_values:
			print("usage: %s" % usage)
			sys.exit(1)
	if opt == '-u':
		allowed_users = arg

# Test for mandatory arguments
if dataset_name == '' or file_name == '' or file_type == '':
    print("usage: %s" % usage)
    sys.exit(1)

# Define the access control (public or restricted)
if restricted_to != '':
	# Wrong, should not have "restricted": first
	# restricted_key = '"restricted" : "{\\\"allowed_users\\\": \\\"%s\\\", \\\"level\\\": \\\"%s\\\"}"' % (allowed_users, restricted_to)
	restricted_key = '{"allowed_users": "%s", "level": "%s"}' % (allowed_users, restricted_to)
	print("Restriction = %s" % restricted_key)


# -----------------------------------------------------------------------
# Read the CKAN connection configuration
ckan_ip = open("ckan_ip.txt").read().replace('\n','')
api_key = open("ckan_api_key.txt").read().replace('\n','')

# Open the connection to the CKAN server
ckan = RemoteCKAN('http://%s' % ckan_ip, apikey=api_key, user_agent=user_agent)


# -----------------------------------------------------------------------
# Create preview images if required
gdal_cmd = ''

# Check for a shapefile inside a zip archive
if re.match(".*\\.[Zz][Ii][Pp]$", file_name):
	unzip=zipfile.ZipFile(file_name)
	for zipped_name in unzip.namelist():
		if re.match(".*\\.shp$", zipped_name):
			# replace filename extension with _preview.geojson
			preview_file_name = tmp_dir + re.sub("\\.[^\\.]*$", "_preview.geojson", os.path.basename(file_name))
			preview_file_type = 'GeoJSON'
			print("Creating preview %s for SHAPE %s" % (preview_file_name, file_name))
			# Determine the source SRS, if undefined assume epsg:2004 (Montserrat)
			ogr_driver = ogr.GetDriverByName("ESRI Shapefile")
			ogr_data = ogr_driver.Open("/vsizip/%s" % file_name, 0)
			if ogr_data.GetLayer().GetSpatialRef():
				ogr_cmd_srs = ''
			else:
				ogr_cmd_srs = '-s_srs ' + shp_default_srs
			# Create a GDAL command line to convert to GeoJSON and simplify the vectors
			gdal_cmd = "ogr2ogr -f geojson -simplify %s %s -t_srs WGS84  /vsistdout/  /vsizip/%s | jq 'del(.crs)' > %s" % (shp_simplify_meters, ogr_cmd_srs, file_name, preview_file_name)

# Check for a GeoTIFF image
if re.match(".*\\.[Tt][Ii][Ff]+$", file_name):
	# replace filename extension with _preview.geojson
	preview_file_name = tmp_dir + re.sub("\\.[^\\.]*$", "_preview.jpg", os.path.basename(file_name))
	preview_file_type = 'JPEG'
	print("Creating preview %s for TIFF %s" % (preview_file_name, file_name))
	gtif = gdal.Open(file_name)
	# reduce the size to less than 1024 but keep the aspect ratio
	gtif_scale = max(gtif.RasterXSize, gtif.RasterYSize) / 1024.0
	gtif_new_X = int(gtif.RasterXSize / gtif_scale)
	gtif_new_Y = int(gtif.RasterYSize / gtif_scale)
	print("size %d x %d -> %d x %d" % (gtif.RasterXSize, gtif.RasterYSize, gtif_new_X, gtif_new_Y))
	# GDAL facilities are available directly in python as of gdal 2.1 but we are on 1.11
	# so we use a command line instead
	gdal_cmd = "gdal_translate -ot JPEG -scale -outsize %d %d  %s  %s" % (gtif_new_X, gtif_new_Y, file_name, preview_file_name)

# Run the command to create the preview file
if gdal_cmd and not os.path.isfile(preview_file_name):
	os.remove(preview_file_name) if os.path.exists(preview_file_name) else None
	print("Running GDAL to create preview...")
	print("  %s" % gdal_cmd)
	os.system(gdal_cmd)


# -----------------------------------------------------------------------
# Create the resource
# See http://docs.ckan.org/en/latest/api/index.html#ckan.logic.action.create.resource_create
print("Uploading the resource")
resource_name = os.path.basename(file_name)
resource_desc = file_type
result = ckan.action.resource_create(package_id=dataset_name, name=resource_name, description=resource_desc, url=dummy_url, format=file_type, restricted=restricted_key, upload=open(file_name, 'rb'))
#pprint.pprint(result)


# -----------------------------------------------------------------------
# Upload the preview image too
print("Uploading the preview")
resource_name = os.path.basename(preview_file_name)
resource_desc = preview_file_type
result = ckan.action.resource_create(package_id=dataset_name, name=resource_name, description=resource_desc, url=dummy_url, format=preview_file_type, restricted=restricted_key, upload=open(preview_file_name, 'rb'))
#pprint.pprint(result)


# -----------------------------------------------------------------------
# Close and tidy
RemoteCKAN.close(ckan)
os.remove(preview_file_name) if os.path.exists(preview_file_name) else None
exit(0)
