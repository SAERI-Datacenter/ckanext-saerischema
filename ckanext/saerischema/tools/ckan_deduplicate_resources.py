#!/usr/bin/env python

# This program is intended to deduplicate the resources directory
# so that large files are replaced with symbolic links to the real file
# kept on the repository server. Small files are kept.
# eg. /var/lib/ckan/default/resources/143/64a/92-1e38-4653-8fc8-d7aaa2e16518
# It can be run from cron periodically.

from __future__ import print_function
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
resource_dir="/var/lib/ckan/default/resources"
user_agent = 'ckanapiexample/1.0 (+http://example.com/my/website)'
debug = False

# Find a list of all packages
#   Find a list of all their resources
#     Match the resource to the actual file on disk
#     Find the same file on the repo server
#     Create the symbolic link

# -----------------------------------------------------------------------
# Read the CKAN connection configuration
ckan_ip = open("ckan_ip.txt").read().replace('\n','')
api_key = open("ckan_api_key.txt").read().replace('\n','')

# Open the connection to the CKAN server
ckan = RemoteCKAN('http://%s' % ckan_ip, apikey=api_key, user_agent=user_agent)

# -----------------------------------------------------------------------
package_results = ckan.action.package_search(  )
if package_results['count'] < 1:
	print("No datasets found!")
	exit(0)
for package in package_results['results']:
	for resource in package['resources']:
		if re.match(".*_preview.*", resource['name']):
			if debug: print("Ignore preview %s" % resource['name'])
		else:
			if debug: print("Dataset %s has resource %s in %s" % (package['name'], resource['name'], resource['id']))
			dir1=resource['id'][0:3]
			dir2=resource['id'][3:6]
			filename=resource['id'][6:]
			pathname=resource_dir + '/' + dir1 + '/' + dir2 + '/' + filename
			if os.path.isfile(pathname):
				if debug: print(" file %s" % pathname)
				deduplicate(resource['name'], pathname)
			else:
				# resource without a name is not valid so just ignore it
				# otherwise valid resource without file is an error
				if (resource['name']):
					print("Error: resource %s in dataset %s has no file %s" % (resource['name'], package['name'], pathname))
				#pprint.pprint(resource)


# -----------------------------------------------------------------------
# Close and tidy
RemoteCKAN.close(ckan)
exit(0)

# -----------------------------------------------------------------------
def deduplicate(name, file):
	print("ln -sf /repo/%s %s" % (name, file))