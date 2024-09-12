from stac_model.input import InputStructure, MLMStatistic, ModelInput
from stac_model.output import MLMClassification, ModelOutput, ModelResult
from stac_model.schema import MLModelProperties
from pydantic import TypeAdapter, ValidationError

# TODO try to get these from pystac...
model_asset_roles = ['mlm:model', 'mlm:weights', 'mlm:checkpoint']
model_asset_implicit_roles = ['mlm:model']
model_asset_artifact_types = ['torch.save', 'torch.jit.script', 'torch.export', 'torch.compile']

# possibly fraught to use these keys in all inputs, ideally the input would
# be aware of both the schema and key name that it's operating on.
# in practice, model assets don't have any required keys so this works fine.
model_required_keys = [
    'name',
    'framework',
    'framework_version',
    'accelerator',
    'mlm:input',
]

def create_validation_function(model_class, field_name, user_friendly_message):
    def validation_function(value):
        error = validate_single_field(model_class, field_name, value)
        if error:
            return f'{user_friendly_message}\n{error}'
        return None
    return validation_function

def validate_single_field(model_class, field_name, value):
    field_info = model_class.model_fields[field_name]
    adapter = TypeAdapter(field_info.annotation)
    try:
        adapter.validate_python(value)
        return None  # Return None if validation passes
    except ValidationError as e:
        return humanize_validation_error(e)  # Return error message if validation fails

def humanize_validation_error(validation_error):
    messages = [e['msg'] for e in validation_error.errors()]
    return '\n'.join(list(dict.fromkeys(messages)))