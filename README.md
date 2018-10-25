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
