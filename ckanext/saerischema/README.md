# Modifying the schema

Run `./metadata_form_to_ckan.sh` to update the schema.
It can be run more than once safely.

It reads the input file `metadata_form_fields.txt` which describes the additional fields in the schema (see below for file format).

It updates the content inside `plugin.py` (adding code to create the schema fields),
`templates/package/snippets/additional_info.html` (displaying the fields on the dataset page), and
`templates/package/snippets/package_basic_fields.html` (editing fields on the dataset create/update page).

It handles these schema fields as special cases: `Region`, `Responsible Party Role`, `Access Limitations`, `Status`, `Topic Category`, `Use Constraints`, `Contact Consent`. They all require a drop-down menu, so the list of options to put in each menu has to be defined somewhere. The respective files are metadata_form_options...txt (eg. `metadata_form_options_region.txt`).

To add additional Spatial Reference Systems please edit `saerickan.oy`

## metadata_form_blank.xlsx

The definition of the metadata fields. This was used to create metadata_form_fields.txt and the metadata_form_options files. If you change this spreadsheet you should also change those files.

## metadata_form_to_ckan.sh

Script to read metadata_form_fields.txt and metadata_form_options files and update the CKAN extension files (plugin.py etc) to display and store the metadata fields when a dataset is created/updated/displayed. The updated files are plugin.py, templates/package/snippets/additional_info.html, templates/package/snippets/package_basic_fields.html, templates/package/snippets/package_metadata_fields.html. The original files are in /usr/lib/ckan/default/src/ckan/ckan/templates/package/snippets.

## metadata_form_fields.txt

The metadata field names, one per line, tab separated label and description.
Do not change these once you've started populating CKAN otherwise the content of the database will be inconsistent.
Note that Title, Keyword and Abstract have been removed because CKAN already has these built in.

## metadata_form_options_*.txt

These files are used to create the drop-down menus when a new dataset is created. They are one option per line, tab separated id and label.

# Note

There are two fields which re-use the built-in defaults (Description and Tags) but with different names (Abstract and Keywords respectively).
They are "commented out" in package_basic_fields.html and then the code is copied from the original and reimplemented (with the new label) inside the package_basic_fields_custom block but at the top instead of at the bottom.

# Technical details

`package_basic_fields.html` is hiding the blocks `package_basic_fields_description` and `package_basic_fields_tags` then adding what would have been their contents in a different place on the page.

It uses macros which are defined in `/usr/lib/ckan/default/src/ckan/ckan/templates-bs2/macros/form.html` to create the input elements. It does not (yet) use `form.select` for the drop-down menus, instead it builds them itself. It checks the `data` variable to see which option needs to be selected based on the current value of the field from the dataset, eg. `data['saeri_region'] == "FK"`. Other variables it could use are `pkg` or `c.user` or `c.userobj` or `app_globals`, eg. `app_globals.site_url`. 

The `metadata_form_to_ckan.sh` script creates the `additional_info.html` file which is used to display the dataset contents.
It handles two fields slightly differently: contact details and research permit application id should be hidden by default.
Conact details are only visible if consent has been given. In both cases the values will be shown to sysadmin users.

The allowed values for Spatial Reference System (SRS/CRS) are defined in the `saerickan.py` script.

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

