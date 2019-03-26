#/usr/bin/env python
# 1.00 arb Tue 26 Mar 19:29:34 GMT 2019

# automatically create preview images for geospatial datasets such as GeoTIFF and Shapefile
# intended to be run from cron.
# search all the datasets in CKAN,
# find out which resource files they have,
# filter out those which can have a preview created,
# ignore those which already have a preview,
# call the ckan_create_preview_from_resource.py script to create and upload the preview.

