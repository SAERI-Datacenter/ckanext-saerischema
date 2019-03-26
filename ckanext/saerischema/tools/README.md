# Tools

Some tools to assist with the schema and creation of datasets/resources.

## Installation

You MUST source your virtual environment and run `pip install pyproj` first (this is documented in the plugin README).

You SHOULD edit the `csv_filename` to be imported if using that (and ensure the file is up-to-date!). Once complete, remove the actual file from the git repository as it's not public data.

You SHOULD edit the `ignore_incomplete_datasets` config in the file to decide whether to import Incomplete datasets (those with Status 0).

You MUST create two files: `ckan_ip.txt` contains the IP address of your CKAN server, or it may be the name `localhost`, and `ckan_api_key.txt` contains the API key of your sysadmin account (or an account which has sufficient permissions). The API key can be found once logged into CKAN on your profile page (it's at the bottom of the left-hand column).
These values were hard-coded into the scripts which caused problems so they are now read from config files.

You MUST install the GDAL and JQ packages into your operating system if you want to use the `ckan_add_resource_to_dataset.py` script.
On Ubuntu this can be done with
`sudo apt-get install gdal-bin python-gdal jq` but an additional step is required afterwards.
Delete (or rename) the file `/usr/lib/ckan/default/lib/python2.7/no-global-site-packages.txt`
otherwise the python-gdal programs will not be available inside the ckan virtualenv.


## metadata_read_test.py

Run this program to display the column names from the metadata CSV file.
Give a filename parameter to use a different CSV file.
Give a column name parameter after the filename parameter to display the content of the named column.
For example to print a list of the number of times each unique "limitations_access" occurs:
```
./metadata_read_test.py '' limitations_access | sort | uniq -c | sort -n
```
The filename is given as the empty string so it uses the built-in default filename.

## ckan_add_dataset.py

Run this program to create all the datasets defined in the CSV file `metadata_FK_export190127.csv`
To use a different CSV file specify it as the first parameter.

Edit the file and check that `only_add_first_entry` is False otherwise it will only add the first one (for testing).

Run `./ckan_add_dataset.py` inside the tools directory. To use a different CSV file run `./ckan_add_dataset.py file.csv`

It requires that all of the organisations have already been created.
For that you will need to have run `ckan_add_organisations.py` from
the `tools` part of `saeritheme` (included in the theme plugin because
it provides all of the organisation logos).

It requires that all of the themes (groups) have already been created.
For that you will need to have run `ckan_add_groups.py` from
the `tools` part of `saeritheme` (included in the theme plugin because
it provides all of the theme logos).

If a dataset already exists then it will be updated so it is safe to run this program more than once.

Note that the first 100 characters of the dataset title is the unique key for the dataset.
You cannot give two datasets the same title, it must be unique, so make sure all rows have different titles (within the first 100 characters).

## ckan_delete_dataset.py

Run this program to delete all recently-added datasets.
This is intended to allow you to delete datasets which were added mistakenly or during testing, but keep all older ones.
The cut-off date is configured inside the code so you will need to edit it.

Run `./ckan_delete_dataset.py` inside the tools directory.

## ckan_add_resource_to_dataset.py

Run this program to upload one file to a dataset.
You need to specify the filename and the dataset name, but the dataset name must be the name which you can see in the URL of a dataset, eg. `falkland-dolphin-sightings` which won't be the same name that you gave in the CSV file when uploading (the dataset name has no spaces).
You also need to specify the file type. This is important and should be specified carefully. Always use the same filetype for the same type of files and be consistent, eg. don't use a mixture of SHP, Shape, Shapefile, ESRI for shapefiles; pick one word and stick with it.
You can also optionally specify if the resource is to be restricted. (See the documentation of the restricted plugin for details.)
https://github.com/SAERI-Datacenter/ckanext-restricted

Run `./ckan_add_resource_to_dataset.py -d dataset-name -f file_name -t type_of_file [-s srs] [-r restriction [-u allowed_users]]`

The -s option, if given, takes the name of a SRS to be used if the shapefile has no SRS. The default is `epsg:2004` (which is suitable for Montserrat).

The -r option, if given, takes one of the values: public, registered, any_organization, same_organization, only_allowed_users.

The -u option, if given, is a comma-separated list of usernames, without any spaces.

The program has an additional feature, to create preview images for those file types which ckan cannot preview itself.
A GeoTIFF file is converted into a reduced-resolution JPEG and both are uploaded. The maximum dimension will be 1000 pixels.
A ShapeFile is converted into a reduced-resolution GeoJSON file and both are uploaded. The minimum distance between points will be 500m.
(Both of these parameters can be configured within the script.)
The preview images will be uploaded with the same file name as the original but with \_preview inserted.
GeoJSON files can then be previewed via the GeoJSON tab (the MapViewer tab does not handle all GeoJSON formats).

## ckan_add_all_resources.py

Run this program to upload all resources files to all datasets.

Run `./ckan_add_all_resources.py usage
* -c metadata.csv
* -r [repo_dir] default is /mnt/datastore
* [-s srs]
* -c is the metadata CSV file
* -r is the root directory of the data repository, default is /mnt/datastore
* -s is the SRS if the shapefile has none, eg. epsg:2004, default is epsg:2004`

It reads the metadata CSV file and for each row it gets the dataset name from the `title` column and the filename from the `original_title _dataportal` column.
The dataset name is converted to ckan format, i.e. without spaces, lowercase, less than 100 characters, and is looked up in the ckan database to find the dataset id.
The file will be uploaded as a resource to that dataset.
The filename is appended to the repository directory, default `/mnt/datastore` but can be changed with -r.
If the filename is a Shapefile, i.e. ends in .shp, then this program will find all the associated files that go with it and zip them up into a temporary archive and upload that.
This program then calls the `ckan_add_resource_to_dataset.py` program to do the work of uploading the resource (and creating and uploading a suitable preview image if necessary).

## ckan_deduplicate_resources.py

Run this program to reduce the size of the CKAN VM by exchanging uploaded resource files (eg. large GeoTIFF images) with a symbolic link (a pointer) to the actual resource kept in the Data Repository VM.
It could be run from cron to perform the task automatically, see below.

Run `./ckan_deduplicate_resources.py
* [-r repo_dir] is the root directory of the repository, default /mnt/datastore
* [-f] must be given to actually force the deduplication otherwise only info is printed`

## ckan_create_auto_preview.py

Run this program to automatically create preview images for geospatial datasets such as GeoTIFF and Shapefile.
To have it run automatically it should be run from cron.
It searches all the datasets in CKAN, finds out which resource files they have, filters out those which can have a preview created, ignores those which already have a preview, and then it calls the `ckan_create_preview_from_resource.py` script to create and upload the preview.

## ckan_create_preview_from_resource.py

Run this program to create a preview image for a resource which already exists in CKAN.
Instead of extracting and downloading the source image from the CKAN web server it finds the local file on disk in order to run faster.

## Note on running programs from cron

Programs to be run from cron must be run inside the ckan virtual environment.
Use a wrapper script such as `cron_wrapper.sh` like this:

`/usr/lib/ckan/default/src/ckanext-saerischema/ckanext/saerischema/tools/cron_wrapper.sh /usr/lib/ckan/default/src/ckanext-saerischema/ckanext/saerischema/tools/ckan_deduplicate_resources.py`

NOTE: Some scripts may require access to config files such as ckan_ip.txt, XXX this needs to be fixed.