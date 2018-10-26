# ckanext-saerischema

See https://docs.ckan.org/en/2.8/extensions/adding-custom-fields.html

## Installation

first activate your virtual environment
```
cd /usr/lib/ckan/default/src
git clone https://github.com/SAERI-Datacenter/ckanext-saerischema.git
cd ckanext-saerischema
python setup.py develop
```
then add `saerischema` to the `ckan.plugins` line in your ckan config file and restart the web server with sudo service apache2 restart

## Updating

```
cd /usr/lib/ckan/default/src/ckanext-saerischema
git pull
sudo service apache2 restart
```

## Customisation of the metadata schema - additional info

A script runs the customisation of the metadata schema. Within the script there are instruction for CKAN to consider the new fields of the metadata schema and to adopt a drop down menu for some of the metadata fields.
The script is the metadata_form_to_ckan.sh file in ckanext-saerischema/ckanext/saerischema/
The fileds of the metadata schema and their order is in the txt file called metadata_form_fields
The files that are "feeding" the drop down menu are the other txt files referring to region, status, responsible party role, access limitation, use constraint and topic category.

