# 1.01 arb Mon  3 Sep 17:31:01 BST 2018 - added SAERI metadata functions
#          but not implemented the actual schema yet.
# See: http://docs.ckan.org/en/2.8/extensions/adding-custom-fields.ht

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


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

    # The create_package_schema() function is used whenever a new dataset
    # is created, we'll want update the default schema and insert our
    # custom field here. We will fetch the default schema defined in
    # default_create_package_schema() by running
    # create_package_schema()'s super function and update it.

    def create_package_schema(self):
        # let's grab the default schema in our plugin
        schema = super(SaerischemaPlugin, self).create_package_schema()
        # our custom field
        schema.update({
            'saeri_metadata_1': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
        })
        return schema

    # The CKAN schema is a dictionary where the key is the name of the field
    # and the value is a list of validators and converters.
    # Here we have a validator to tell CKAN to not raise a validation error
    # if the value is missing and a converter to convert the value to and save
    # as an extra. We will want to change the update_package_schema() function
    # with the same update code.

    def update_package_schema(self):
        schema = super(SaerischemaPlugin, self).update_package_schema()
        # our custom field
        schema.update({
            'saeri_metadata_1': [toolkit.get_validator('ignore_missing'),
                                 toolkit.get_converter('convert_to_extras')]
        })
        return schema

    # The show_package_schema() is used when the package_show() action is called
    # We want the default_show_package_schema to be updated to include our
    # custom field. This time, instead of converting to an extras field,
    # we want our field to be converted from an extras field.
    # So we want to use the convert_from_extras() converter.

    def show_package_schema(self):
        schema = super(SaerischemaPlugin, self).show_package_schema()
        schema.update({
            'saeri_metadata_1': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
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
