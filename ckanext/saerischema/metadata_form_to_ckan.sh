#!/bin/bash

# Three files to update:
#   plugin.py
#   templates/package/snippets/additional_info.html
#   templates/package/snippets/package_basic_fields.html

# Input file contains one line for each metadata item
file_input="metadata_form_fields.txt"
if [ ! -f $file_input ]; then echo ERROR: no such file $file_input >&2; exit 1; fi

# For testing locally:
#file_plugin="metadata_form_test_plugin.txt"
#file_addinfo="metadata_form_test_additional_info.txt"
#file_basicfields="metadata_form_test_package_basic_fields.txt"

# For use within the extension:
file_plugin="plugin.py"
file_addinfo="templates/package/snippets/additional_info.html"
file_basicfields="templates/package/snippets/package_basic_fields.html"

if [ ! -f $file_plugin ]; then echo ERROR: no such file $file_plugin   >&2; exit 1; fi
if [ ! -f $file_addinfo ]; then echo ERROR: no such file $file_addinfo >&2; exit 1; fi
if [ ! -f $file_basicfields ]; then echo ERROR: no such file $file_basicfields >&2; exit 1; fi

# ----------------------------------------------------------------------
# Create empty temporary files into which we place the new information

file_plugin_update="metadata_form_plugin_update.txt"
rm -f $file_plugin_update
touch $file_plugin_update

file_plugin_show="metadata_form_plugin_show.txt"
rm -f $file_plugin_show
touch $file_plugin_show

file_addinfo_update="metadata_form_additional_info.txt"
rm -f $file_addinfo_update
touch $file_addinfo_update

file_basicfields_update="metadata_form_basic_fields.txt"
rm -f $file_basicfields_update
touch $file_basicfields_update

# ----------------------------------------------------------------------
# plugin.py

echo "Updating plugin.py"
comma=""
cat $file_input | while read line; do
	label="$line"
	ident=`echo $label | sed -e 's/^/saeri_/' -e 's/ /_/g' | tr '[:upper:]' '[:lower:]'`
	#echo "$ident = $label"

	echo "            ${comma}'${ident}': [toolkit.get_validator('ignore_missing'),"      >> ${file_plugin_update}
	echo "                                 toolkit.get_converter('convert_to_extras')]"   >> ${file_plugin_update}

	echo "            ${comma}'${ident}': [toolkit.get_converter('convert_from_extras')," >> ${file_plugin_show}
	echo "                            toolkit.get_validator('ignore_missing')]"           >> ${file_plugin_show}

	comma="," # subsequent lines are separated by a comma in the schema dictionary
done

sed -i.bak '/SAERISCHEMA_UPDATE_START/,/SAERISCHEMA_UPDATE_END/!b;//!d;/SAERISCHEMA_UPDATE_START/r '${file_plugin_update} ${file_plugin}
sed -i.bck '/SAERISCHEMA_SHOW_START/,/SAERISCHEMA_SHOW_END/!b;//!d;/SAERISCHEMA_SHOW_START/r       '${file_plugin_show}   ${file_plugin}

# ----------------------------------------------------------------------
# additional_info.html

echo "Updating additional_info.html"
cat $file_input | while read line; do
	label="$line"
	ident=`echo $label | sed -e 's/^/saeri_/' -e 's/ /_/g' | tr '[:upper:]' '[:lower:]'`
	#echo "$ident = $label"

    echo '  {% if pkg_dict.'${ident}' %}'                                         >> ${file_addinfo_update}
	echo '    <tr>'                                                               >> ${file_addinfo_update}
	echo '      <th scope="row" class="dataset-label">{{ _("'${label}'") }}</th>' >> ${file_addinfo_update}
	echo '      <td class="dataset-details">{{ pkg_dict.'${ident}' }}</td>'       >> ${file_addinfo_update}
	echo '    </tr>'                                                              >> ${file_addinfo_update}
	echo '  {% endif %}'                                                          >> ${file_addinfo_update}

done

sed -i.bak '/SAERISCHEMA_ADDINFO_START/,/SAERISCHEMA_ADDINFO_END/!b;//!d;/SAERISCHEMA_ADDINFO_START/r '${file_addinfo_update} ${file_addinfo}

# ----------------------------------------------------------------------
# package_basic_fields.html

echo "Updating package_basic_fields.html"
cat $file_input | while read line; do
	label="$line"
	ident=`echo $label | sed -e 's/^/saeri_/' -e 's/ /_/g' | tr '[:upper:]' '[:lower:]'`
	#echo "$ident = $label"

	echo "  {{ form.input('${ident}', label=_('${label}'), id='field-${ident}', placeholder=_('${ident} placeholder'), value=data.${ident}, error=errors.${ident}, classes=['control-medium']) }}" >> ${file_basicfields_update}

done

sed -i.bak '/SAERISCHEMA_BASICFIELDS_START/,/SAERISCHEMA_BASICFIELDS_END/!b;//!d;/SAERISCHEMA_BASICFIELDS_START/r '${file_basicfields_update} ${file_basicfields}

# ----------------------------------------------------------------------
# Clean up

rm -f $file_plugin_update
rm -f $file_plugin_show
rm -f $file_addinfo_update
rm -f $file_basicfields_update

echo "Finished"
