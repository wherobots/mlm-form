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

# Validation functions generated using the factory function
validate_model_name = create_validation_function(MLModelProperties, "name", "Please enter a valid model name.")
validate_architecture = create_validation_function(MLModelProperties, "architecture", "Please enter a valid model architecture.")
validate_tasks = create_validation_function(MLModelProperties, "tasks", "Please enter a valid set of tasks.")
validate_framework = create_validation_function(MLModelProperties, "framework", "Please enter a valid framework.")
validate_framework_version = create_validation_function(MLModelProperties, "framework_version", "Please enter a valid framework version.")
validate_accelerator = create_validation_function(MLModelProperties, "accelerator", "Please enter a valid accelerator.")
validate_accelerator_constrained = create_validation_function(MLModelProperties, "accelerator_constrained", "Please enter a valid boolean value for accelerator_constrained.")
validate_accelerator_summary = create_validation_function(MLModelProperties, "accelerator_summary", "Please enter a valid accelerator summary.")
validate_memory_size = create_validation_function(MLModelProperties, "memory_size", "Please enter a valid memory size.")
validate_pretrained = create_validation_function(MLModelProperties, "pretrained", "Please enter a valid boolean value for pretrained.")
validate_pretrained_source = create_validation_function(MLModelProperties, "pretrained_source", "Please enter a valid pretrained source.")
validate_total_parameters = create_validation_function(MLModelProperties, "total_parameters", "Please enter a valid total number of parameters.")

validate_output_name = create_validation_function(ModelOutput, "name", "Please enter a valid output name.")
validate_output_tasks = create_validation_function(ModelOutput, "tasks", "Please enter a valid set of tasks.")

validate_input_name = create_validation_function(ModelInput, "name", "Please enter a valid input name.")
validate_input_bands = create_validation_function(ModelInput, "bands", "Please enter a valid list of band names.")
validate_norm_by_channel = create_validation_function(ModelInput, "norm_by_channel", "Please enter a valid boolean value for norm_by_channel.")
validate_norm_type = create_validation_function(ModelInput, "norm_type", "Please enter a valid normalization type.")
validate_resize_type = create_validation_function(ModelInput, "resize_type", "Please enter a valid resize type.")

validate_shape = create_validation_function(InputStructure, "shape", "Please enter a valid shape list of integers.")
validate_dim_order = create_validation_function(InputStructure, "dim_order", "Please enter a valid dimension order list of strings.")
validate_data_type = create_validation_function(InputStructure, "data_type", "Please enter a valid data type.")

validate_statistic_mean = create_validation_function(MLMStatistic, "mean", "Please enter a valid mean value.")
validate_statistic_stddev = create_validation_function(MLMStatistic, "stddev", "Please enter a valid standard deviation value.")

validate_class_value = create_validation_function(MLMClassification, "value", "Please enter a valid class value.")
validate_class_name = create_validation_function(MLMClassification, "name", "Please enter a valid class name.")

validate_result_shape = create_validation_function(ModelResult, "shape", "Please enter a valid result shape list of integers.")
validate_result_dim_order = create_validation_function(ModelResult, "dim_order", "Please enter a valid result dimension order list of strings.")
validate_result_data_type = create_validation_function(ModelResult, "data_type", "Please enter a valid result data type.")