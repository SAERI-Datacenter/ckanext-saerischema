# metadata_form_blank.xlsx

The definition of the metadata fields. This was used to create metadata_form_fields.txt and the metadata_form_options files. If you change this spreadsheet you should also change those files.

# metadata_form_to_ckan.sh

Script to read metadata_form_fields.txt and metadata_form_options files and update the CKAN extension files (plugin.py etc) to display and store the metadata fields when a dataset is created/updated/displayed.

# metadata_form_fields.txt

The metadata field names, one per line, tab separated label and description.
Do not change these once you've started populating CKAN otherwise the content of the database will be inconsistent.

# metadata_form_options

These files are used to create the drop-down menus when a new dataset is created. They are one option per line, tab separated id and label.

# Note

There are two fields which re-use the built-in defaults (Description and Tags) but with different names (Abstract and Keywords respectively).
