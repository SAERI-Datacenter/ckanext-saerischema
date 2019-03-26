#!/usr/bin/env python

# This program is intended to deduplicate the resources directory
# so that large files are replaced with symbolic links to the real file
# kept on the repository server. Small files are kept.
# eg. /var/lib/ckan/default/resources/143/64a/92-1e38-4653-8fc8-d7aaa2e16518
# It can be run from cron periodically.
# NOTE: if running from cron you will need to ensure ckan_ip and ckan_api_key
# files are accessible.
# You will need to use the force option otherwise it does nothing for safety.

from __future__ import print_function
import urllib2
import urllib
import json
import pprint    # for pprint.pprint
import csv       # for csv.DictReader
import re        # for re.sub() and re.match()
import getopt    # for command line arguments
import zipfile   # for handling zipped shapefiles
import fnmatch   # for find_files
from osgeo import gdal # to get dimensions of geotiff (if this errors, remove /usr/lib/ckan/default/lib/python2.7/no-global-site-packages.txt)
from osgeo import ogr  # to get SRS of a shapefile
from ckanapi import RemoteCKAN
# import our tools from the parent directory
import sys,os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import saerickan

# Configuration
resource_dir="/var/lib/ckan/default/resources" # see ckan.storage_path in production.ini
repo_dir = '/mnt/datastore'
user_agent = 'ckanapiexample/1.0 (+http://example.com/my/website)'
debug = False
force = False

# Find a list of all packages
#   Find a list of all their resources
#     Match the resource to the actual file on disk
#     Find the same file on the repo server
#     Create the symbolic link


# -----------------------------------------------------------------------
# return a list of files matching the simple pattern, eg. '*.jpg'
def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


# -----------------------------------------------------------------------
# Deduplicate by deleting the file and making it a symbolic link
# name is the filename in the repo, file is the local resource file.

def deduplicate(name, file):
	# Find the file in the repo
	# Make sure it's the same file size
	# and same contents
	# Remove the local file and replace with a symbolic link
	if debug: print("Trying to dedup %s" % name)
	for filename in find_files(repo_dir, name):
		if debug: print("Found %s in %s" % (name, filename))
		# identical ?
		if os.path.getsize(file) == os.path.getsize(filename):
			cmd = "ln -sf '%s' '%s'" % (os.path.join(repo_dir, name), file)
			if debug: print("Identical so deduplicate with command %s" % cmd)
			if force:
				os.system(cmd)
			else:
				print(cmd)


# -----------------------------------------------------------------------
# MAIN

usage = "usage: [-r repo_dir] [-f]\n" \
	"-r is the root directory of the repository\n" \
	"-f must be given to actually force the deduplication otherwise only info is printed\n"
options = "d:f:r:"

try:
    opts, args = getopt.getopt(sys.argv[1:], options)
except getopt.GetoptError:
    print("usage: %s %s" % (sys.argv[0], usage))
    sys.exit(1)
for opt,arg in opts:
	if opt == '-d':
		debug = True
	if opt == '-r':
		repo_dir = arg
	if opt == '-f':
		force = True

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
			dir1 = resource['id'][0:3]
			dir2 = resource['id'][3:6]
			filename = resource['id'][6:]
			pathname = os.path.join(resource_dir, dir1, dir2, filename)
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
