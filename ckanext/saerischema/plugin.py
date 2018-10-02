# 1.01 arb Mon  3 Sep 17:31:01 BST 2018 - added SAERI metadata functions
#          but not implemented the actual schema yet.
# See: http://docs.ckan.org/en/2.8/extensions/adding-custom-fields.ht

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.plugins.toolkit import Invalid


class SaerischemaPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'saerischema')

class SaerischemaPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)
    #plugins.implements(plugins.ITemplateHelpers) # for get_helpers function

    # Helper function to prevent duplicated code
    # Caller from create_package_schema and update_package_schema.
    def _modify_package_schema(self, schema):
        schema.update({
            # SAERISCHEMA_UPDATE_START
            'saeri_region': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_organisation': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_title': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_language': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_abstract': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_topic_category': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_keyword': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            ,'saeri_temporal_extent': [toolkit.get_validator('ignore_missing'),
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
            ,'saeri_status': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
            # SAERISCHEMA_UPDATE_END
        })
        return schema
    # The create_package_schema() function is used whenever a new dataset
    # is created, we'll want update the default schema and insert our
    # custom field here. We will fetch the default schema defined in
    # default_create_package_schema() by running
    # create_package_schema()'s super function and update it.

    def create_package_schema(self):
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
        schema = super(SaerischemaPlugin, self).show_package_schema()
        schema.update({
            # SAERISCHEMA_SHOW_START
            'saeri_region': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_organisation': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_title': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_language': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_abstract': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_topic_category': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_keyword': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            ,'saeri_temporal_extent': [toolkit.get_converter('convert_from_extras'),
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
            ,'saeri_status': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
            # SAERISCHEMA_SHOW_END
        })
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
# Make the plugin implement the IConfigurer interface:

    # This interface allows to implement a function update_config() that
    # allows us to update the CKAN config, in our case we want to add an
    # additional location for CKAN to look for templates:

    def update_config(self, config):
        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        toolkit.add_template_directory(config, 'templates')
