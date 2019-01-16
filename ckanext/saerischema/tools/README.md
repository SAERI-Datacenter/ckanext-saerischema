# Tools

Some tools to assist with the schema and creation of datasets/resources.

## Installation

You will need to source your virtual environment and run `pip install pyproj` first (this is documented in the plugin README).

You MUST edit the scripts and change the `ckan_ip` to the IP address (or name), and port if necessary, of the CKAN server; it may simply be `localhost`.

You MUST edit the `api_key` to be the one for your system administrator account, or one which has permission to create datasets. The API key can be found once logged into CKAN on your profile page (it's at the bottom of the left-hand column).

You MUST edit the `csv_filename` to be imported if using that (and ensure the file is up-to-date!). Once complete, remove the actual file from the git repository as it's not public data.

## ckan_add_dataset.py

Run this program to create all the datasets defined in the CSV file `metadata_FK_export190107_arb.csv`

It will only do the first one, until you edit `only_add_first_entry` from True to False.

It requires that all of the organisations have already been created.
For that you will need to have run `ckan_add_organisations.py` from
the `tools` part of `saeritheme` (included in the theme plugin because
it provides all of the organisation logos).
