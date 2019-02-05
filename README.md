# ckanext-saerischema

This is a CKAN plugin to implement additional metadata fields (schema) specifically for SAERI.
It displays the fields for entering metadata on the dataset create/update page and displays the (non-empty) fields on the dataset display page. Some of the SAERI fields re-use existing CKAN metadata fields (eg. Description which is renamed to Abstract, and Tags which is renamed to Keywords) and the rest are additional. One unique feature is the bounding box which the user enters into the four fields (east, west, north, south) is converted into a GeoJSON format and stored in the CKAN spatial field which allows the user to search for datasets by specifying an area on a map.
See https://docs.ckan.org/en/2.8/extensions/adding-custom-fields.html

## Installation

First activate your virtual environment, then:
```
pip install pyproj
cd /usr/lib/ckan/default/src
git clone https://github.com/SAERI-Datacenter/ckanext-saerischema.git
cd ckanext-saerischema
python setup.py develop
```
then add `saerischema` to the `ckan.plugins` line in your ckan config file and restart the web server with `sudo service apache2 restart`

Now the `restricted` extension needs to be installed:
```
cd /usr/lib/ckan/default/src
git clone https://github.com/EnviDat/ckanext-restricted.git
cd ckanext-restricted
python setup.py develop
pip install -r dev-requirements.txt
```
then add `restricted` to the `ckan.plugins` line in your ckan config file and restart the web server with `sudo service apache2 restart`

See the CKAN documentation for installing the `spatial` plugins.

## Configuration

The `restricted` plugin needs to be able to send emails so please make sure you have configured CKAN appropriately, see
https://docs.ckan.org/en/2.8/maintaining/configuration.html?#email-settings

## Updating

Update your local copy of the schema extention using:
```
cd /usr/lib/ckan/default/src/ckanext-saerischema
git pull
sudo service apache2 restart
```

In the unlikely event that the restricted plugin has been updated then you can update your local copy:
```
cd /usr/lib/ckan/default/src/ckanext-restricted
git pull
sudo service apache2 restart
```

## Customising the schema

Warning: do not modify the schema itself once you have started populating the database. It might work but it might not.

The set of additional fields (i.e. additional to those which CKAN already provides such as Description/Abstract) is listed in the file `ckanext/saerischema/metadata_form_fields.txt` (note: tab separated). The fields will be displayed on the CKAN dataset page in the same order as given in this file.  Each field has a title and a helpful description. Most of the fields are implemented as free-form text entry (i.e. not validated or constrained) but some are implemented as drop-down menus. These menus have values as given in the other txt files in the `ckanext/saerischema` directory. If you edit any of these files you need to re-run the `ckanext/saerischema/metadata_form_to_ckan.sh` script. It is the script which determines which fields are implemented as menus. If you no longer want a menu, or you want to change a field from a plain text entry into a menu, then the script will have to be edited.

*Important note* about the schema. It is usually very important that consistent entries are made into the database for similar/identical items. For example if a dataset is in English then the database should record English, not Inglish, Anglais or anything else, even though they all mean "English". For this reason a drop-down menu is helpful to constrain the entry. The menu description files have the database key and the human-readable description together for each item. Once you have started populating the database do not change the database keys. For example the country code for South Georgia is "GS" so do not store "SG".

There are some HTML files in `ckanext/saerischema/templates/package/snippets` but these should *not* be edited. They have been customised to display certain fields in the correct place on the page but most of the contents are modified automatically by the script described above.

