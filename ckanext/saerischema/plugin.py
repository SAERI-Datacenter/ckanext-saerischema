# 1.08 arb Wed 20 Mar 17:22:28 GMT 2019 - convert_bbox_to_spatial handles datasets without srs
# 1.07 arb Wed Jan 23 11:18:58 GMT 2019 - added two validators to handle 'restricted' field of resource metadata
# 1.06 arb Mon Jan 21 15:50:00 GMT 2019 - added mime type for GeoJSON
# 1.05 arb Thu Jan 17 17:23:23 GMT 2019 - added level and allowed_users for restricted plugin
# 1.04 arb Thu 17 Jan 09:57:17 GMT 2019 - use saerickan_convert_bbox_to_geojson to perform the conversion.
#      Add convert_bbox_to_spatial validator to spatial field.
# 1.03 arb - create spatial extra
# 1.02 arb Tue 23 Oct 18:08:18 BST 2018 - added metadata, added logging, removed unused class.
# 1.01 arb Mon  3 Sep 17:31:01 BST 2018 - added SAERI metadata functions but not implemented the actual schema yet.

# This plugin extends the default CKAN schema with new metadata fields.
# It also contains code to update the 'spatial' metadata with a
# GeoJSON value that is calculated from the N,S,W,E extents entered.
# It also extends the default CKAN schema for resources to add the
# fields required by the 'restricted' plugin allowing for resources
# to be restricted to certain users.

# See the documentation:
# http://docs.ckan.org/en/2.8/extensions/adding-custom-fields.html
# The convert_to/from_extras code is here:
# /usr/lib/ckan/default/src/ckan/ckan/logic/converters.py
# Adding resource metadata:
# https://docs.ckan.org/en/2.8/extensions/adding-custom-fields.html#adding-custom-fields-to-resources
# For adding a mime type:
# https://docs.ckan.org/en/2.8/maintaining/filestore.html#filestore-api
# GeoJSON mimetype: https://tools.ietf.org/html/rfc7946

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.plugins.toolkit import Invalid
import logging
import mimetypes
import saerickan

# Doesn't work (is ignored): logging.basicConfig(filename="/tmp/ckan_debug.log", level=logging.DEBUG) # XXX arb ???
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Our validator converts the bounding box values into a spatial extra
# It takes the values from saeri_north/south/east/west and creates a
# GeoJSON string which is placed into the extra called 'spatial'.
# 1 param (value) return value, or it can be converted if you wish
# 2 param (value, context) likewise. nb can raise(Invalid) if you wish.
# 4 param (key, flattened_data, errors, context) return None as it can
#  update stuff
# See https://docs.ckan.org/en/2.8/extensions/adding-custom-fields.html#custom-validators

# flattened_data for a dataset may look like this:
#   ('extras', 27, 'key'): 'saeri_west_longitude',
#   ('saeri_west_longitude',): u'-11',
# the resources of the dataset are like this:
# eg. to get the id of the first (0) resource:
#   ('resources', 0, 'id'): u'b96f04cb-00ab-48aa-8f85-4243e29ffa73',
# the extras are like this:
#   ('__extras',): {
#     'num_resources': 1,
#     'metadata_modified': '2019-01-23T12:59:53.892922',
#      organization': { 'title':'My Organisation' }
#   }

def SaerischemaPlugin_validator_convert_bbox_to_spatial(key, flattened_data, errors, context):
    log.debug("SaerischemaPlugin convert_bbox_to_spatial")
    log.debug("SaerischemaPlugin flattened_data is %s" % (str(flattened_data)))

    # Lookup the entered values (warning: might not be validated/converted yet)
    # in case we are given a dataset without our values we return empty
    try:
        srs = flattened_data[('saeri_spatial_reference_system',)]
        n = flattened_data[('saeri_north_latitude',)]
        s = flattened_data[('saeri_south_latitude',)]
        w = flattened_data[('saeri_west_longitude',)]
        e = flattened_data[('saeri_east_longitude',)]
    except:
        srs = n = s = w = e = ''

    # Construct GeoJSON format from bounding box
    # eg. '{ "type": "Polygon", "coordinates": [[ [ -59.26,-51.94 ], [ -57.62,-51.94 ], [ -57.62,-51.16 ], [ -59.26,-51.16 ], [ -59.26,-51.94 ] ]] }'
    geojson = saerickan.saerickan_convert_bbox_to_geojson(srs, n, s, w, e)

    log.debug("SaerischemaPlugin SRS %s" % (srs))
    log.debug("SaerischemaPlugin N %s" % (n))
    log.debug("SaerischemaPlugin S %s" % (s))
    log.debug("SaerischemaPlugin W %s" % (w))
    log.debug("SaerischemaPlugin E %s" % (e))
    log.debug("SaerischemaPlugin GeoJSON %s" % (geojson))

    # check if spatial exists first
    # what to do if it does?
    if ('spatial',) in flattened_data:
        log.debug("SaerischemaPlugin existing spatial (will be overwritten) was %s" % (flattened_data[('spatial',)]))

    # Give the spatial extra the new GeoJSON value.
    flattened_data[('spatial',)] = geojson


def SaerischemaPlugin_validator_convert_level_to_restricted(key, flattened_data, errors, context):
    log.debug("SaerischemaPlugin_validator_convert_level_to_restricted flattened_data is %s" % (str(flattened_data)))
    lv = flattened_data[('resources', 0, 'level')]
    au = flattened_data[('resources', 0, 'allowed_users')]
    #rr = flattened_data[('restricted',)]
    #log.debug("XXX level is %s" % lv)
    #log.debug("XXX restricted is %s" % rr)
    #log.debug("XXX level is %s" % lv)
    #log.debug("XXX users is %s" % au)
    json = '{\"allowed_users\": \"%s\", \"level\": \"%s\"}' % (au, lv)
    log.debug("SaerischemaPlugin_validator_convert_level_to_restricted setting restricted to %s" % json)
    flattened_data[('resources', 0, 'restricted')] = json


def SaerischemaPlugin_validator_convert_level_from_restricted(key, flattened_data, errors, context):
    log.debug("SaerischemaPlugin_validator_convert_level_from_restricted flattened_data is %s" % (str(flattened_data)))


# ---------------------------------------------------------------------
# Our class contains the additional schema elements required for our metadata

class SaerischemaPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IValidators) # for get_validators function
    #plugins.implements(plugins.ITemplateHelpers) # for get_helpers function

    log.debug("SaerischemaPlugin created")


    # Return the list of validators which we supply (functions must be global)
    def get_validators(self):
        log.debug("SaerischemaPlugin get_validators returning 3 incl bbox and level")
        return { 'convert_bbox_to_spatial':  SaerischemaPlugin_validator_convert_bbox_to_spatial,
            'convert_level_to_restricted':   SaerischemaPlugin_validator_convert_level_to_restricted,
            'convert_level_from_restricted': SaerischemaPlugin_validator_convert_level_from_restricted }


    # Helper function to prevent duplicated code
    # Caller from create_package_schema and update_package_schema.
    def _modify_package_schema(self, schema):
        log.debug("SaerischemaPlugin _modify_package_schema called")

        schema.update({
            # SAERISCHEMA_UPDATE_START
            'saeri_region': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_language': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_topic_category': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_temporal_extent_start': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_temporal_extent_end': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_dataset_reference_date': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_lineage': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_west_longitude': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_south_latitude': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_east_longitude': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_north_latitude': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_spatial_reference_system': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_responsible_organisation_name': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_contact_mail_address': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_responsible_party_role': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_access_limitations': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_use_constraints': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_data_format': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_update_frequency': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_accuracy': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_resource_type': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_original_title': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_metadata_date': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_metadata_point_of_contact': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_contact_consent': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_unique_resource_id': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_research_permit_application_id': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            # SAERISCHEMA_UPDATE_END
        })
        # Add two fields to the resource schema for the restricted plugin
        log.debug("SaerischemaPlugin _modify_package_schema adding restricted to resources schema")
        schema['resources'].update({
            'level': [ toolkit.get_validator('ignore_missing'), toolkit.get_validator('convert_level_to_restricted') ]
            ,'allowed_users': [ toolkit.get_validator('ignore_missing') ]
            ,'restricted': [ toolkit.get_validator('ignore_missing') ]
        })
        # If the schema doesn't already have a 'spatial' extra then add it now
        if not 'spatial' in schema:
            log.debug("SaerischemaPlugin _modify_package_schema adding spatial to schema")
            schema.update({'spatial': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_bbox_to_spatial'),
                                 toolkit.get_converter('convert_to_extras')]})
        return schema

    # The create_package_schema() function is used whenever a new dataset
    # is created, we'll want update the default schema and insert our
    # custom field here. We will fetch the default schema defined in
    # default_create_package_schema() by running
    # create_package_schema()'s super function and update it.

    def create_package_schema(self):
        log.debug("SaerischemaPlugin create_package_schema called")
        # get the default schema in our plugin
        schema = super(SaerischemaPlugin, self).create_package_schema()
        # add our custom fields
        schema = self._modify_package_schema(schema)
        return schema

    # The CKAN schema is a dictionary where the key is the name of the field
    # and the value is a list of validators and converters.
    # Here we have a validator to tell CKAN to not raise a validation error
    # if the value is missing and a converter to convert the value to and save
    # as an extra. We will want to change the update_package_schema() function
    # with the same update code.

    def update_package_schema(self):
        log.debug("SaerischemaPlugin update_package_schema called")
        schema = super(SaerischemaPlugin, self).update_package_schema()
        # add our custom fields
        schema = self._modify_package_schema(schema)
        return schema

    # The show_package_schema() is used when the package_show() action is called
    # We want the default_show_package_schema to be updated to include our
    # custom fields. This time, instead of converting to an extras field,
    # we want our field to be converted from an extras field.
    # So we want to use the convert_from_extras() converter.

    def show_package_schema(self):
        log.debug("SaerischemaPlugin show_package_schema called")
        schema = super(SaerischemaPlugin, self).show_package_schema()
        #log.debug("SaerischemaPlugin schema before = {}".format(str(schema)))
        schema.update({
            # SAERISCHEMA_SHOW_START
            'saeri_region': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_language': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_topic_category': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_temporal_extent_start': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_temporal_extent_end': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_dataset_reference_date': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_lineage': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_west_longitude': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_south_latitude': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_east_longitude': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_north_latitude': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_spatial_reference_system': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_responsible_organisation_name': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_contact_mail_address': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_responsible_party_role': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_access_limitations': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_use_constraints': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_data_format': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_update_frequency': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_accuracy': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_resource_type': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_original_title': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_metadata_date': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_metadata_point_of_contact': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_contact_consent': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_unique_resource_id': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_research_permit_application_id': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            # SAERISCHEMA_SHOW_END
        })
        # Add two fields to the resource schema for the restricted plugin
        # XXX no use of convert_from_restricted at this stage
        log.debug("SaerischemaPlugin show_package_schema adding restricted to resources schema")
        schema['resources'].update({
            'level': [ toolkit.get_validator('ignore_missing') ]
            ,'allowed_users': [ toolkit.get_validator('ignore_missing') ]
            ,'restricted': [ toolkit.get_validator('ignore_missing') ]
        })
        # If the schema doesn't already have a 'spatial' extra then add it now
        if not 'spatial' in schema:
            log.debug("SaerischemaPlugin show_package_schema adding spatial to schema")
            schema.update({'spatial': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('convert_bbox_to_spatial'), # XXX should this be here???
                            toolkit.get_validator('ignore_missing')]})
        return schema

    # The package_types() function defines a list of dataset types that this
    # plugin handles. Each dataset has a field containing its type.
    # Plugins can register to handle specific types of dataset and ignore others.
    # Since our plugin is not for any specific type of dataset and we want our
    # plugin to be the default handler, we update the plugin code to contain:

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []

    # In order for our new field to be visible on the CKAN front-end, we need to
    # update the templates.
    # Make the plugin implement the IConfigurer interface.
    # This interface allows to implement a function update_config() that
    # allows us to update the CKAN config, in our case we want to add an
    # additional location for CKAN to look for templates:

    def update_config(self, config):
        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
        toolkit.add_resource('fanstatic', 'saerischema')
        mimetypes.add_type('application/geo+json', '.geojson') # As per RFC, not application/json
        log.debug("SaerischemaPlugin update_config called")
