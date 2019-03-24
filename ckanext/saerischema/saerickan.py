#!/usr/bin/env python
# 1.04 arb Sat 23 Mar 01:57:23 GMT 2019 - added saerickan_map_topic_category_to_group
# 1.03 arb                              - added Montserrat SRS
# 1.02 arb Thu 17 Jan 09:27:57 GMT 2019 - added logging
# 1.01 arb Fri 21 Dec 11:08:41 GMT 2018 - handle case when only bottom,left is provided
# 1.00 arb Thu 20 Dec 13:46:04 GMT 2018

# Functions for SAERI's CKAN installation
# Requires pip install pyproj

# GeoJSON is:
# { "type": "Point", "coordinates": [-3.145,53.078] }
# { "type": "Polygon", "coordinates": [[[2.05827, 49.8625],[2.05827, 55.7447], [-6.41736, 55.7447], [-6.41736, 49.8625], [2.05827, 49.8625]]] }
# NB. WKT is: POLYGON((lon lat, lon2 lat2, lon3 lat3, lon4 lat4, lon lat))
# Note that the first and last are the same point.

from pyproj import Proj
import csv       # for csv.DictReader
import sys,os
import logging
import ckan.plugins.toolkit as toolkit # for get_action

# Configuration:
# Define the location of the CSV file which maps topic_category to group name and description
# This will be used in ckan_add_dataset.py, and in saerischema plugin
# when updating a dataset to add it to the appropriate groups based on topic_category.
#group_csv_filename="../../../../ckanext-saeritheme/ckanext/saeritheme/tools/topic_categories.csv"
group_csv_filename="/usr/lib/ckan/default/src/ckanext-saeritheme/ckanext/saeritheme/tools/topic_categories.csv"

# Doesn't work (is ignored): logging.basicConfig(filename="/tmp/ckan_debug.log", level=logging.DEBUG) # XXX arb ???
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# This converts the float arguments describing a bounding box
# into a GeoJSON string for a polygon.
# NB. polygon is closed, i.e. last point is same as first point.
# Input coordinates must be WGS84 latitude and longitude
# because GeoJSON does not have projected coordinate systems.

def saerickan_convert_latlon_bbox_to_geojson(n,s,w,e):
    # Construct GeoJSON format from bounding box
    # eg. '{ "type": "Polygon", "coordinates": [[ [ -59.26,-51.94 ], [ -57.62,-51.94 ], [ -57.62,-51.16 ], [ -59.26,-51.16 ], [ -59.26,-51.94 ] ]] }'
    geojson = '{ "type": "Polygon", "coordinates": [ [ '
    geojson += '[ %f, %f ], ' % (w,n)
    geojson += '[ %f, %f ], ' % (e,n)
    geojson += '[ %f, %f ], ' % (e,s)
    geojson += '[ %f, %f ], ' % (w,s)
    geojson += '[ %f, %f ] '  % (w,n)
    geojson += '] ] }'
    return geojson

# ---------------------------------------------------------------------
# This converts the string arguments describing a bounding box
# into a GeoJSON string for a polygon.
# NB. polygon is closed, i.e. last point is same as first point.
# Input coordinates are relative to given spatial reference system.
# Only certain SRS are recognised right now, see code for details.
# Returns the empty string if conversion fails.

def saerickan_convert_bbox_to_geojson(srs,top,bottom,left,right):
    src_proj = None

    log.debug("saerickan_convert_bbox_to_geojson SRS %s" % (srs))
    log.debug("saerickan_convert_bbox_to_geojson N %s" % (top))
    log.debug("saerickan_convert_bbox_to_geojson S %s" % (bottom))
    log.debug("saerickan_convert_bbox_to_geojson W %s" % (left))
    log.debug("saerickan_convert_bbox_to_geojson E %s" % (right))

    # An explicit NULL is ok, no coordinates are provided
    if top == 'NULL' and bottom == 'NULL' and left == 'NULL' and right == 'NULL':
    	log.debug("saerickan_convert_bbox_to_geojson all NULL")
        return ''

    # Try to convert the string to floating point numbers
    try:
        top=float(top)
        bottom=float(bottom)
        left=float(left)
        right=float(right)
    except:
        # Any non-digit is bad:
        log.error("saerickan_convert_bbox_to_geojson: ERROR in digits %s %s %s %s %s" % (srs,top,bottom,left,right))
        return ''

    # All zeros is OK:
    if top == 0 and bottom == 0 and left == 0 and right == 0:
        log.debug("saerickan_convert_bbox_to_geojson all zero")
        return ''

    # If only one corner is given then we could make a Point not a Polygon
    # but we make a Polygon because in reality most data relates to an area.
    if top == 0 and right == 0 and bottom != 0 and left != 0:
    	top = bottom
    	right = left
    # Otherwise any zero is bad:
    elif top == 0 or bottom == 0 or left == 0 or right == 0:
        log.error("saerickan_convert_bbox_to_geojson ERROR zero in %s %s %s %s %s" % (srs,top,bottom,left,right))
        return ''

    if srs == 'WGS84' or srs == 'WGS84 ':
        # Out of range is bad:
        if top < -90 or top > 90 or bottom < -90 or bottom > 90:
            log.error("saerickan_convert_bbox_to_geojson ERROR out of range1 in %s %s %s %s %s" % (srs,top,bottom,left,right))
            return ''
        if left < -180 or left > 180 or right < -180 or right > 180:
            log.error("saerickan_convert_bbox_to_geojson ERROR out of range2 in %s %s %s %s %s" % (srs,top,bottom,left,right))
            return ''
        return saerickan_convert_latlon_bbox_to_geojson(top,bottom,left,right)
    elif srs == 'UTM 21S WGS84': # 112 of these
        src_proj = Proj(init='epsg:32721')
    elif srs == 'UTM 28S WGS84': # 1 of this
        src_proj = Proj(init='epsg:32728')
    elif srs == 'World Mercator WGS84 Datum': # 1 of this
        src_proj = Proj(init='epsg:3395')
    elif srs == 'TM CM 60W': # 9 of these
        src_proj = Proj(init='epsg:6703')
    elif srs == 'Montserrat 1958 British West Indies Grid': # Montserrat
        src_proj = Proj(init='epsg:2004')
    else:
        log.error("saerickan_convert_bbox_to_geojson ERROR unknown SRS %s" % srs)
        return ''

    # Try to transform the coordinates to lat,lon
    if src_proj:
        try:
            tl_lon,tl_lat = src_proj(left, top, inverse=True)
            br_lon,br_lat = src_proj(right, bottom, inverse=True)
            # Check if the result is out of range:
            if tl_lat < -90 or tl_lat > 90:
                log.error("saerickan_convert_bbox_to_geojson ERROR %s >90 in %s %s %s %s %s" % (tl_lat,srs,top,bottom,left,right))
                return ''
            if br_lat < -90 or br_lat > 90:
                log.error("saerickan_convert_bbox_to_geojson ERROR %s >90 in %s %s %s %s %s" % (br_lat,srs,top,bottom,left,right))
                return ''
            if tl_lon < -180 or tl_lon > 180:
                log.error("saerickan_convert_bbox_to_geojson ERROR %s >180 in %s %s %s %s %s" % (tl_lon,srs,top,bottom,left,right))
                return ''
            if br_lon < -180 or br_lon > 180:
                log.error("saerickan_convert_bbox_to_geojson ERROR %s >180 in %s %s %s %s %s" % (br_lon,srs,top,bottom,left,right))
                return ''
            if tl_lon == 0 or tl_lat == 0 or br_lon == 0 or br_lat == 0:
                log.error("saerickan_convert_bbox_to_geojson ERROR zero(s) in %s %s %s %s %s" % (srs,top,bottom,left,right))
                return ''
            # Convert to GeoJSON
            geojson = saerickan_convert_latlon_bbox_to_geojson(tl_lat, br_lat, tl_lon, br_lon)
            log.debug("saerickan_convert_bbox_to_geojson GeoJSON %s" % (geojson))
            return geojson
        except:
            # The Proj call failed to transform the coordinates
            log.debug("saerickan_convert_bbox_to_geojson Proj failed to transform coordinates")
            return ''

    # No projection could be identified
    log.debug("saerickan_convert_bbox_to_geojson projection could not be identified")
    return ''


# -----------------------------------------------------------------------
# Read the group definition CSV file to map from
# our topic_category column to a group (theme) name.
# The topic_category column is in the csvname column in this CSV.
# CSV is:
# csvname,group,title,description,logo
# Returns a dictionary.
# XXX this code also exists inside saeritheme/ckan_add_dataset.py

# We keep a 'global' copy so that we don't have to keep reading the CSV file 
topic_category_to_group_dict = {}

def saerickan_create_mapping_topic_category_to_group():
    global topic_category_to_group_dict
    if len(topic_category_to_group_dict) > 0:
        return topic_category_to_group_dict
    group_csv_fp = open(group_csv_filename)
    group_csv_reader = csv.DictReader(group_csv_fp)
    for group_row in group_csv_reader:
        topic_category_to_group_dict[group_row['csvname']] = group_row['group']
    group_csv_fp.close()
    return topic_category_to_group_dict

# ---------------------------------------------------------------------
# Convert the topic_category string into a matching group object

def saerickan_map_topic_category_to_group(context, topic_category):
    # Read CSV from theme plugin
    topic_category_to_group_dict = saerickan_create_mapping_topic_category_to_group()
 
    # Convert topic_category to group name using CSV info
    group_name = topic_category_to_group_dict[topic_category]
 
    # Convert group name to group id using a validator, doesn't work
    #return ckan.logic.converters.convert_group_name_or_id_to_id(group_name)
 
    # Convert group name to group object by looking it up in ckan database
    #log.error("XXX topic_category = %s" % topic_category)
    #log.error("XXX group_name = %s" % group_name)
    group = toolkit.get_action("group_show")(context, {'id':group_name})
    #log.error("XXX group id = %s" % group['id'])
    #log.error("XXX group = %s" % str(group))
    return(group)


# ---------------------------------------------------------------------
# Main program for testing
# Usage: SRS N S W E
# where SRS is one of "WGS84" (for lat,lon coords), or "UTM 21S WGS84" for metres.

if __name__ == "__main__":
    import sys
    from ckanapi import RemoteCKAN
    logging.basicConfig(stream=sys.stdout, level=0)
    # Read the configuration
    ckan_ip = open("ckan_ip.txt").read().replace('\n','')
    api_key = open("ckan_api_key.txt").read().replace('\n','')
    # Open the connection to the CKAN server
    ckan = RemoteCKAN('http://%s' % ckan_ip, apikey=api_key, user_agent='user_agent')

    print(saerickan_map_topic_category_to_group('biota'))
    #print(saerickan_convert_bbox_to_geojson(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]))
