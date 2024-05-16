import csv
import logging
import os
from ckantoolkit import h

all_helpers = {}

log = logging.getLogger(__name__)

def helper(fn):
    """
    collect helper functions into ckanext.scheming.all_helpers dict
    """
    all_helpers[fn.__name__] = fn
    return fn


options_cache = {}
"""
cached options dictionary containing the cached options from the respective csv file. 
"""

field_file_map = {
    'saeri_region': 'metadata_form_options_region.txt',
    'saeri_topic_category': 'metadata_form_options_topic_category.txt',
    'saeri_use_constraints': 'metadata_form_options_use_constraints.txt',
    'saeri_status': 'metadata_form_options_status.txt',  # is this used?
    'saeri_responsible_party_role': 'metadata_form_options_resp_party_role.txt',
    'saeri_access_limitations': 'metadata_form_options_access_limitations.txt',
    'saeri_contact_consent': 'metadata_form_options_contact_consent.txt',
}
"""
dict containing the map of option fields names to their respective csv files.
"""


@helper
def saerischema_get_labeler_for_facet(facet, schema_type='dataset'):
    """
    
    :param schema_type: type of scheming schema to use, defaults to 'dataset'
    :param facet: the facet requiring a labeler  
    :return: a labeler function for scheming files or None if no field was not a scheming field or a choices field
    """
    log.info(h.scheming_get_dataset_schema('dataset'))
    scheming_field = h.scheming_field_by_name(h.scheming_get_dataset_schema(schema_type)['dataset_fields'], facet)

    # Not a scheming field don't create a labeler and use the default
    if scheming_field is None:
        return None

    choices = h.scheming_field_choices(scheming_field)

    # Not a choices field, don't create a labeler and use the default
    if choices is None:
        return None

    def get_label_for_field(field):
        return h.scheming_choices_label(choices, field['name'])

    return get_label_for_field


@helper
def saerischema_csv_choices(field):
    """
    Loads option fields from a csv file mapped using the field_name. If there are no configured options
    an error is logged but not raised and no options are returned.
    """

    log.debug('saerischema_csv_choices: field=%s', field)
    field_name = field.get('field_name')
    file_path = field_file_map.get(field_name)
    if field_name is not None and options_cache.get(field_name) is None:
        if file_path is not None:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            region_file_path = os.path.join(dir_path, file_path)
            if not os.path.exists(region_file_path):
                log.error(f"saerischema_csv_choices file is missing for field=%s filename=%s", field_name, file_path)
            else:
                log.debug(f"saerischema_csv_choices field={field}")
                log.info(region_file_path)
                region_file = open(region_file_path)
                region_file_reader = csv.reader(region_file, delimiter='\t')
                options_cache[field_name] = [{
                    'value': r[0],
                    'label': r[1]
                } for r in region_file_reader]
    else:
        log.error(f'saerischema_csv_choices field is missing for field=%s', field_name)

    return options_cache.get(field_name, [])
