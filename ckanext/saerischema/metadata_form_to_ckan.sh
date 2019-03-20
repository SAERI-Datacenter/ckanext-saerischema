#!/bin/bash
# 1.06 arb Wed 20 Mar 22:45:35 GMT 2019 - additional_info now displays the description instead of the label
# 1.05 arb Wed 20 Mar 17:21:13 GMT 2019 - topic category added back in
# 1,04 arb Tue 29 Jan 11:44:09 GMT 2019 - change Hidden logic so sysadmin always allowed even if consent field absent
# 1.03 arb Sat 26 Jan 23:33:44 GMT 2019 - hide more contact details:
#      saeri_metadata_point_of_contact
#      saeri_responsible_organisation_name
#      saeri_contact_mail_address
#      saeri_responsible_party_role
# 1.02 arb Wed 16 Jan 11:27:55 GMT 2019 - only show research permit id to sysadmin
#      and only show contact details if consent given or if sysadmin.
# 1.01 arb Fri 14 Dec 16:08:50 GMT 2018 - ensure the correct menu entry is selected

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
# We add code into plugin.py which updates the ckan schema to hold our additional fields.

echo "Updating plugin.py"
comma=""
cat $file_input | while IFS="	" read label description; do
	# Convert the label into an identifier, no spaces, lowercase, saeri_ prefix
	ident=`echo $label | sed -e 's/^/saeri_/' -e 's/ /_/g' | tr '[:upper:]' '[:lower:]'`
	#echo "$ident = $label"

	# The update function converts TO extras
	echo "            ${comma}'${ident}': [toolkit.get_validator('ignore_missing'),"      >> ${file_plugin_update}
	echo "                                 toolkit.get_converter('convert_to_extras')]"   >> ${file_plugin_update}

	# The show function converts FROM extras
	echo "            ${comma}'${ident}': [toolkit.get_converter('convert_from_extras')," >> ${file_plugin_show}
	echo "                            toolkit.get_validator('ignore_missing')]"           >> ${file_plugin_show}

	comma="," # subsequent lines are separated by a comma in the schema dictionary
done

# Apply the changes to plugin.py by replacing everything between the lines START and END.
# Do it in two places, once in the update function and once in the show function.
sed -i.bak '/SAERISCHEMA_UPDATE_START/,/SAERISCHEMA_UPDATE_END/!b;//!d;/SAERISCHEMA_UPDATE_START/r '${file_plugin_update} ${file_plugin}
sed -i.bck '/SAERISCHEMA_SHOW_START/,/SAERISCHEMA_SHOW_END/!b;//!d;/SAERISCHEMA_SHOW_START/r       '${file_plugin_show}   ${file_plugin}

# ----------------------------------------------------------------------
# additional_info.html
# The input file must be tab-separated Label Description
# This file displays the additional fields from our schema.

read_options_file_for_additional_info()
{
	options_input_file="$1"    # read optionvalue<tab>optiontext lines from this file
	options_output_file="$2"   # append to this file
	options_id="$3"            # The HTML form name, eg. saeri_topic_category
	echo "Creating display options for $options_id"

	firstline=1
	cat "${options_input_file}" | while IFS="	" read label description; do
		# What we want to end up with looks like this:
		# {% if pkg_dict.saeri_use_constraints == "openbut" %} Open, but something...
        # {% elif pkg_dict.saeri_use_constraints == "restricted" %} Restricted...
        # {% else %}
        # {{ pkg_dict.saeri_use_constraints }}
        # {% endif %}
        if [ $firstline -eq 1 ]; then
            firstline=0
            echo '      {% if pkg_dict.'${options_id}' == "'"${label}"'" %} '"${description}" >> ${options_output_file}
        else
            echo '      {% elif pkg_dict.'${options_id}' == "'"${label}"'" %} '"${description}" >> ${options_output_file}
        fi
	done
	echo '      {% else %}'                     >> ${options_output_file}
	echo '      {{ pkg_dict.'${options_id}' }}' >> ${options_output_file}
	echo '      {% endif %}'                    >> ${options_output_file}
}

echo "Updating additional_info.html"
cat $file_input | while IFS="	" read label description; do
	# Convert the label into an identifier, no spaces, lowercase, saeri_ prefix
	ident=`echo $label | sed -e 's/^/saeri_/' -e 's/ /_/g' | tr '[:upper:]' '[:lower:]'`
	#echo "$ident = $label"

    echo '  {% if pkg_dict.'${ident}' %}'                                         >> ${file_addinfo_update}
	echo '    <tr>'                                                               >> ${file_addinfo_update}
	echo '      <th scope="row" class="dataset-label">{{ _("'${label}'") }}</th>' >> ${file_addinfo_update}

	# Change the value of certain fields.
	# If the item is saeri_research_permit_application_id then it is hidden unless sysadmin
	echo '      <td class="dataset-details">'  >> ${file_addinfo_update}
	if [ $ident == "saeri_research_permit_application_id" ]; then
		echo '      {% if c.userobj.sysadmin %}{{ pkg_dict.'${ident}' }}' >> ${file_addinfo_update}
		echo '      {% else %}<i>Hidden (internal use only)</i>'          >> ${file_addinfo_update}
		echo '      {% endif %}'                                          >> ${file_addinfo_update}
	# If the item is contact details then it is hidden without consent
	elif [ $ident == "saeri_metadata_point_of_contact" \
		-o $ident == "saeri_responsible_organisation_name" \
		-o $ident == "saeri_contact_mail_address" \
		-o $ident == "saeri_responsible_party_role" ]; then
		echo '      {% if c.userobj.sysadmin or ( pkg_dict.saeri_contact_consent and pkg_dict.saeri_contact_consent == 1 ) %}{{ pkg_dict.'${ident}' }}'   >> ${file_addinfo_update}
		echo '      {% else %}<i>Hidden (personal data protection)</i>'   >> ${file_addinfo_update}
		echo '      {% endif %}</td>'       >> ${file_addinfo_update}
	# The following all require the value to be translated from the database value to a human-readable value
	elif [ "$label" == "Region" ]; then
		read_options_file_for_additional_info "metadata_form_options_region.txt" "${file_addinfo_update}" "$ident"
	# Responsible Party Role might need multiple values so don't constrain it with a drop-down menu
	#elif [ "$label" == "Responsible Party Role" ]; then
	#	read_options_file_for_additional_info "metadata_form_options_resp_party_role.txt" "${file_addinfo_update}"
	elif [ "$label" == "Access Limitations" ]; then
		read_options_file_for_additional_info "metadata_form_options_access_limitations.txt" "${file_addinfo_update}" "$ident"
	# Status is no longer included because we don't import Incomplete records
	#elif [ "$label" == "Status" ]; then
	#	read_options_file_for_additional_info "metadata_form_options_status.txt" "${file_addinfo_update}"
	# Topic category is included again even though we use ckan 'groups'
	elif [ "$label" == "Topic Category" ]; then
		read_options_file_for_additional_info "metadata_form_options_topic_category.txt" "${file_addinfo_update}" "$ident"
	elif [ "$label" == "Use Constraints" ]; then
		read_options_file_for_additional_info "metadata_form_options_use_constraints.txt" "${file_addinfo_update}" "$ident"
	elif [ "$label" == "Contact Consent" ]; then
		read_options_file_for_additional_info "metadata_form_options_contact_consent.txt" "${file_addinfo_update}" "$ident"
	# All other fields are shown but some may need to be translated
	# from the database value to a human value via the options file.
	else
		echo '        {{ pkg_dict.'${ident}' }}'     >> ${file_addinfo_update}
	fi
	echo '      </td>'                         >> ${file_addinfo_update}

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
read_options_file_for_package_basic_fields()
{
	options_input_file="$1"    # read optionvalue<tab>optiontext lines from this file
	options_output_file="$2"   # append to this file
	options_id="$3"            # The HTML form name, eg. saeri_topic_category
	options_title="$4"         # The dropdown title, eg. "Topic Category"
	echo "Creating drop-down menu for $options_title"

	# There is a macro called form.select but we don't yet use it (XXX)
	#echo "  {{ form.select('${options_id}', label=_('${options_title}'), id='field-${options_id}', value=data.${options_id}, error=errors.${options_id}, classes=['control-medium']) }}" >> "${options_output_file}"

	echo '<div class="form-group control-medium">' >> "${options_output_file}"
	echo '  <label for="field-'${options_id}'" class="control-label">'${options_title}'</label>' >> "${options_output_file}"
	echo '  <div class="controls">' >> "${options_output_file}"
	echo '    <select id="field-'${options_id}'" name="'${options_id}'" data-module="autocomplete">' >> "${options_output_file}"

	cat "${options_input_file}" | while IFS="	" read label description; do
		# The quotes are complex here but what we want to end with is:
		# <option value="done" {{ "selected " if "done" == data['saeri_status'] }} >Status</option>
		echo '      <option value="'${label}'" {{ "selected " if "'${label}'" == data['"'"${options_id}"'"'] }} >'${description}'</option>' >> "${options_output_file}"
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
	# Actually there is but we haven't migrated to use it yet.
	if [ "$label" == "Region" ]; then
		read_options_file_for_package_basic_fields "metadata_form_options_region.txt" "${file_basicfields_update}" "$ident" "$label"
	# Responsible Party Role might need multiple values so don't constrain it with a drop-down menu
	#elif [ "$label" == "Responsible Party Role" ]; then
	#	read_options_file_for_package_basic_fields "metadata_form_options_resp_party_role.txt" "${file_basicfields_update}" "$ident" "$label"
	elif [ "$label" == "Access Limitations" ]; then
		read_options_file_for_package_basic_fields "metadata_form_options_access_limitations.txt" "${file_basicfields_update}" "$ident" "$label"
	# Status is no longer included because we don't import Incomplete records
	#elif [ "$label" == "Status" ]; then
	#	read_options_file_for_package_basic_fields "metadata_form_options_status.txt" "${file_basicfields_update}" "$ident" "$label"
	# Topic category is included again even though we use ckan 'groups'
	elif [ "$label" == "Topic Category" ]; then
		read_options_file_for_package_basic_fields "metadata_form_options_topic_category.txt" "${file_basicfields_update}" "$ident" "$label"
	elif [ "$label" == "Use Constraints" ]; then
		read_options_file_for_package_basic_fields "metadata_form_options_use_constraints.txt" "${file_basicfields_update}" "$ident" "$label"
	elif [ "$label" == "Contact Consent" ]; then
		read_options_file_for_package_basic_fields "metadata_form_options_contact_consent.txt" "${file_basicfields_update}" "$ident" "$label"
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
