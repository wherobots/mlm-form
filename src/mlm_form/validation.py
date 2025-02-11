from stac_model.input import InputStructure, MLMStatistic, ModelInput
from stac_model.output import MLMClassification, ModelOutput, ModelResult
from stac_model.schema import MLModelProperties
from pydantic import TypeAdapter, ValidationError

# TODO try to get these from schema itself, or pydantic
model_asset_roles = ['mlm:model', 'mlm:weights', 'mlm:checkpoint']
model_asset_implicit_roles = ['mlm:model']
model_asset_artifact_types = ['torch.save', 'torch.jit.save', 'torch.export.save', 'tf.keras.Model.save', 'tf.keras.Model.save_weights', 'tf.keras.Model.export']
datatypes = ['int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32',
             'uint64', 'float16', 'float32', 'float64', 'cint16', 'cint32',
             'cfloat32', 'cfloat64', 'other']
# TODO drop down or enter your own input field for fields where we recommend common choices but want to provide flexibility
common_ml_frameworks = ["PyTorch", "TensorFlow", "scikit-learn", "Hugging Face", "Keras", "JAX"]

# possibly fraught to use these keys in all inputs, ideally the input would
# be aware of both the schema and key name that it's operating on.
# in practice, model assets don't have any required keys so this works fine.
model_required_keys = [
    'model_name',
    'framework',
    'framework_version',
    'accelerator',
    'accelerator_constrained',
    'accelerator_count',
    'mlm:input',
    'tasks',
    'pretrained',
    'batch_size_suggestion',
    'mlm_input_name',
    'mlm_input_bands',
    'mlm_input_shape',
    'mlm_input_dim_order',
    'mlm_input_norm_by_channel',
    'mlm_input_norm_type',
    'mlm_input_resize_type',
    'mlm_input_data_type',
    'mlm_output_name',
    'mlm_output_shape',
    'mlm_output_dim_order',
    'mlm_output_classes',
    'mlm_output_data_type',
    "href",
    "mlm:artifact_type",

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