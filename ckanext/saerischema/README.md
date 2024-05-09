# Modifying the schema

The dataset schema is managed using the [scheming](https://github.com/ckan/ckanext-scheming) plugin. to enable this schema
the plugin `scheming_datasets` must be installed and added to `ckan.plugins`. `scheming.dataset_schemas` must also be set to the 
location of the saerischema.yml file e.g.
```scheming.dataset_schemas = ckanext.saerischema:/usr/lib/ckan/default/src/ckanext-saeritheme/ckanext/saerischema/saerischema.yml```

The SAERI schema uses custom presets for some field types. For these fields to work, the custom presets must be added to the 
ckan configuration 

`scheming.presets = ckanext.scheming:presets.json ckanext.saerischema:/usr/lib/ckan/default/src/ckanext-saerischema/ckanext/saerischema/presets.json`


## Option Fields
All option fields are controlled using csv files to simplify the customization of the options in different environments. to add a new option field
1. create a new csv file in the directory `ckanext/saerischema`
2. register the file in `field_file_map` in helpers.py where the key is the field name
3. add the field to `saerischema.yml` using the same field name and enabling the saerischema_csv_choices helper.
```yaml
  field_name: saeri_responsible_party_role
  label: Responsible Party Role
  display_snippet: display_redacted.html
  preset: select
  choices_helper: saerischema_csv_choices
  ```

### Adding internal fields
An internal field is a dataset field which can only be viewed by logged-in users. Any field can be marked as internal by
setting the display_snippet of that field to `display_internal.html` e.g. 
```yaml
  field_name: saeri_contact_consent
  label: Contact Consent
  display_snippet: display_internal.html
  help_text: "Whether contact details may be published"
  preset: select
  choices_helper: saerischema_csv_choices
```

### Adding restricted fields
A restricted field is a dataset field which can only be viewed by logged-in users or if the contact as allowed consent. 
Any field can be marked as internal by setting the display_snippet of that field to `display_redacted.html` e.g. 
```yaml
  field_name: saeri_responsible_party_role
  label: Responsible Party Role
  display_snippet: display_redacted.html
  preset: select
  choices_helper: saerischema_csv_choices
```

To add additional Spatial Reference Systems please edit `saerickan.py`

The plugin MUST have access to the list of topic categories so that it can map to CKAN groups.
The `saerickan.py` script is hard-coded to use `/usr/lib/ckan/default/src/ckanext-saeritheme/ckanext/saeritheme/tools/topic_categories.csv`
This is the default location as used in the theme plugin but the administrator must NOTE this dependency.

## metadata_form_blank.xlsx

The definition of the metadata fields. This was used to create metadata_form_fields.txt and the metadata_form_options files. If you change this spreadsheet you should also change those files.

## metadata_form_options_*.txt

These files are used to create the drop-down menus when a new dataset is created. They are one option per line, tab separated id and label.

# Technical details

`package_basic_fields.html` is hiding the blocks `package_basic_fields_description` and `package_basic_fields_tags` then adding what would have been their contents in a different place on the page.

It uses macros which are defined in `/usr/lib/ckan/default/src/ckan/ckan/templates-bs2/macros/form.html` to create the input elements. It does not (yet) use `form.select` for the drop-down menus, instead it builds them itself. It checks the `data` variable to see which option needs to be selected based on the current value of the field from the dataset, eg. `data['saeri_region'] == "FK"`. Other variables it could use are `pkg` or `c.user` or `c.userobj` or `app_globals`, eg. `app_globals.site_url`. 

The allowed values for Spatial Reference System (SRS/CRS) are defined in the `saerickan.py` script.

The mapping from topic_category to ckan group is done by intercepting calls to package_create and package_update. It reads the `topic_categories.csv` file as described above.

# To do

Convert the Contact Consent from 0 or 1 into words Hidden or Shown.

# Debugging

First make the log files readable `sudo chmod go+r /var/log/apache2/*`

Now check the end of the file `/var/log/apache2/ckan_default.error.log`
if the error is not in the last few lines then go further back,
and it might be immediately before the line `CGI Variables`
(note: which is before `WSGI Variables`).

## Turn on debug:

You can set `debug = true` in the config file but you will probably need to edit
the `ckan_default.conf` file, see below. Once done and apache restarted you can
load a page and see a debug section in the footer to display information about
how the page was constructed. A better way to debug is to run a test server, not
apache, using paster, see below.

Change `debug = true` and `ckan.site_url` to have the debug port number.

```
crudini --set --inplace $ini DEFAULT debug true
crudini --set --inplace $ini app:main ckan.site_url http://172.16.92.142:5000
```

Edit /etc/apache2/sites-enabled/ckan_default.conf
and remove `processes=2 threads=15` from the line
`WSGIDaemonProcess ckan_default display-name=ckan_default processes=2 threads=15`

Now you can start a debug web server using
```
cd /usr/lib/ckan/default/src/ckan
paster serve /etc/ckan/default/production.ini
```
and connect to it by pointing your web browser at port :5000

## Turn off debug:

```
crudini --set --inplace $ini DEFAULT debug false
crudini --set --inplace $ini app:main ckan.site_url http://172.16.92.142
```

Edit /etc/apache2/sites-enabled/ckan_default.conf
and replace the line
`WSGIDaemonProcess ckan_default display-name=ckan_default processes=2 threads=15`

## Debugging the code

```
import pdb
pdb.set_trace() # at the place where you want a breakpoint
```
or
```
import ipdb
ipdb.set_trace() # at the place where you want a breakpoint
```

You will need the paster serve console open.
It will display a URL where you can see the stacktrace, variables, and run commands.

