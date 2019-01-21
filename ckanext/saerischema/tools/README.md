# Tools

Some tools to assist with the schema and creation of datasets/resources.

## Installation

You will need to source your virtual environment and run `pip install pyproj` first (this is documented in the plugin README).

You MUST edit the scripts and change the `ckan_ip` to the IP address (or name), and port if necessary, of the CKAN server; it may simply be `localhost`.

You MUST edit the `api_key` to be the one for your system administrator account, or one which has permission to create datasets. The API key can be found once logged into CKAN on your profile page (it's at the bottom of the left-hand column).

You MUST edit the `csv_filename` to be imported if using that (and ensure the file is up-to-date!). Once complete, remove the actual file from the git repository as it's not public data.

## ckan_add_dataset.py

Run this program to create all the datasets defined in the CSV file `metadata_FK_export190107_arb2.csv`

Edit the file and check that `only_add_first_entry` is False otherwise it will only add the first one (for testing).

Run `./ckan_add_dataset.py` inside the tools directory.

It requires that all of the organisations have already been created.
For that you will need to have run `ckan_add_organisations.py` from
the `tools` part of `saeritheme` (included in the theme plugin because
it provides all of the organisation logos).

If a dataset already exists then it will be updated so it is safe to run this program more than once.

Note that the first 100 characters of the dataset title is the unique key for the dataset.
You cannot give two datasets the same title, it must be unique, so make sure all rows have different titles (within the first 100 characters).
