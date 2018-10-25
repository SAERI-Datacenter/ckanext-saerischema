#!/bin/bash

# This script reads the metadata*txt files and updates the CKAN
# metadata entry form and the CKAN dataset display page to handle
# the extra metadata required for SAERI. It only needs to be run
# once you edit the metadata*txt files. It updates:
#   plugin.py
#   templates/package/snippets/additional_info.html
#   templates/package/snippets/package_basic_fields.html

# Input file contains one line for each metadata item
file_input="metadata_form_fields.txt"
if [ ! -f $file_input ]; then echo ERROR: no such file $file_input >&2; exit 1; fi

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
# The input file must be tab-separated Label Description

echo "Updating plugin.py"
comma=""
cat $file_input | while IFS="	" read label description; do
	# Convert the label into an identifier, no spaces, lowercase, saeri_ prefix
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
# The input file must be tab-separated Label Description

echo "Updating additional_info.html"
cat $file_input | while IFS="	" read label description; do
	# Convert the label into an identifier, no spaces, lowercase, saeri_ prefix
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
# The input file must be tab-separated Label Description
# where the Description will be used as the placeholder

# This function reads tab-separated options from a file and
# appends <option> statements to the given filename.
read_options_file()
{
	options_input_file="$1"    # read optionvalue<tab>optiontext lines from this file
	options_output_file="$2"   # append to this file
	options_id="$3"            # The HTML form name, eg. field-saeri_topic_category
	options_title="$4"         # The dropdown title, eg. "Topic Category"
	echo "Creating drop-down menu for $options_title"

	echo '<div class="form-group control-medium">' >> "${options_output_file}"
	echo '  <label for="field-'${options_id}'" class="control-label">'${options_title}'</label>' >> "${options_output_file}"
	echo '  <div class="controls">' >> "${options_output_file}"
	echo '    <select id="field-'${options_id}'" name="'${options_id}'" data-module="autocomplete">' >> "${options_output_file}"

	cat "${options_input_file}" | while IFS="	" read label description; do
		echo '      <option value="'${label}'">'${description}'</option>' >> "${options_output_file}"
	done

	echo '    </select>' >> "${options_output_file}"
	echo '  </div>'      >> "${options_output_file}"
	echo '</div>'        >> "${options_output_file}"
}

echo "Updating package_basic_fields.html"
cat $file_input | while IFS="	" read label description; do
	# Convert the label into an identifier, no spaces, lowercase, saeri_ prefix
	ident=`echo $label | sed -e 's/^/saeri_/' -e 's/ /_/g' | tr '[:upper:]' '[:lower:]'`
	#echo "$ident = $label"

	# We normally use the "form.input" macro defined in ckan/templates/macros/form.html
	# but there is no macro for dropdown menus so we use our own function defined above.
	if [ "$label" == "Region" ]; then
		read_options_file "metadata_form_options_region.txt" "${file_basicfields_update}" "$ident" "$label"
	# Responsible Party Role might need multiple values so don't constrain it with a drop-down menu
	#elif [ "$label" == "Responsible Party Role" ]; then
	#	read_options_file "metadata_form_options_resp_party_role.txt" "${file_basicfields_update}" "$ident" "$label"
	elif [ "$label" == "Access Limitations" ]; then
		read_options_file "metadata_form_options_access_limitations.txt" "${file_basicfields_update}" "$ident" "$label"
	elif [ "$label" == "Status" ]; then
		read_options_file "metadata_form_options_status.txt" "${file_basicfields_update}" "$ident" "$label"
	elif [ "$label" == "Topic Category" ]; then
		read_options_file "metadata_form_options_topic_category.txt" "${file_basicfields_update}" "$ident" "$label"
	elif [ "$label" == "Use Constraints" ]; then
		read_options_file "metadata_form_options_use_constraints.txt" "${file_basicfields_update}" "$ident" "$label"
	else
		echo "  {{ form.input('${ident}', label=_('${label}'), id='field-${ident}', placeholder=_('${description}'), value=data.${ident}, error=errors.${ident}, classes=['control-medium']) }}" >> ${file_basicfields_update}
	fi
done

sed -i.bak '/SAERISCHEMA_BASICFIELDS_START/,/SAERISCHEMA_BASICFIELDS_END/!b;//!d;/SAERISCHEMA_BASICFIELDS_START/r '${file_basicfields_update} ${file_basicfields}

# ----------------------------------------------------------------------
# Clean up

rm -f $file_plugin_update
rm -f $file_plugin_show
rm -f $file_addinfo_update
rm -f $file_basicfields_update

echo "Finished"
