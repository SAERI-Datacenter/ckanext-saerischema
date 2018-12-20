# Tools

Some tools to assist with the schema and creation of datasets/resources.

## ckan_add_dataset.py

Run this program to create all the datasets defined in the CSV file `metadata_FK_export181112_new.csv`

It will only do the first one, until you uncomment the `break` line after `ckan_add_dataset_from_csv_dict`
It requires that all of the organisations have already been created.
For that you will need to have run `ckan_add_organisations.py` from the `tools` part of `saeritheme`
(included in the theme plugin because it provides all of the organisation logos).
