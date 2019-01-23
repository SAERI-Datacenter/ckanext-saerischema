# Tools

Some tools to assist with the schema and creation of datasets/resources.

## Installation

You will need to source your virtual environment and run `pip install pyproj` first (this is documented in the plugin README).

You MUST edit the `csv_filename` to be imported if using that (and ensure the file is up-to-date!). Once complete, remove the actual file from the git repository as it's not public data.

You MUST create two files: `ckan_ip.txt` contains the IP address of your CKAN server, or it may be the name `localhost`, and `ckan_api_key.txt` contains the API key of your sysadmin account (or an account which has sufficient permissions). The API key can be found once logged into CKAN on your profile page (it's at the bottom of the left-hand column).
These values were hard-coded into the scripts which caused problems so they are now read from config files.

## ckan_add_dataset.py

Run this program to create all the datasets defined in the CSV file `metadata_FK_export190122.csv`

Edit the file and check that `only_add_first_entry` is False otherwise it will only add the first one (for testing).

Run `./ckan_add_dataset.py` inside the tools directory.

It requires that all of the organisations have already been created.
For that you will need to have run `ckan_add_organisations.py` from
the `tools` part of `saeritheme` (included in the theme plugin because
it provides all of the organisation logos).

If a dataset already exists then it will be updated so it is safe to run this program more than once.

Note that the first 100 characters of the dataset title is the unique key for the dataset.
You cannot give two datasets the same title, it must be unique, so make sure all rows have different titles (within the first 100 characters).

## ckan_delete_dataset.py

Run this program to delete all recently-added datasets.
This is intended to allow you to delete datasets which were added mistakenly or during testing, but keep all older ones.
The cut-off date is configured inside the code so you will need to edit it.

Run `./ckan_delete_dataset.py` inside the tools directory.
