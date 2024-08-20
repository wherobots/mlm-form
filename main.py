from fasthtml.common import *

from src.mlm_form.templates import inputListTemplate, inputTemplate, selectEnumTemplate, selectCheckboxTemplate
from src.mlm_form.validation import *
from stac_model.base import TaskEnum
from stac_model.runtime import AcceleratorEnum

app, rt = fast_app(hdrs=(picolink))
tasks = [task.value for task in TaskEnum]

@app.get('/')
def homepage():
    return Body(
            Main(
                Section(
                H2("Machine Learning Model Metadata Form"),
                P("Please complete all fields below to describe the machine learning model metadata."))),
        Grid(
        Form(hx_post='/submit', hx_target='#result', hx_trigger="input delay:200ms")(
            inputTemplate(label="Model Name", name="model_name", val=None, input_type='text'),
            inputTemplate(label="Architecture", name="architecture", val=None, input_type='text'),
            selectCheckboxTemplate(label="Tasks", options=tasks,  name="tasks"),
            inputTemplate(label="Framework", name="framework", val=None, input_type='text'),
            inputTemplate(label="Framework Version", name="framework_version", val=None, input_type='text'),
            inputTemplate(label="Memory Size", name="memory_size", val=None, input_type='number'),
            inputTemplate(label="Total Parameters", name="total_parameters", val=None, input_type='number'),
            inputTemplate(label="Is it pretrained?", name="pretrained", val=None, input_type='boolean'),
            inputTemplate(label="Pretrained source", name="pretrained_source", val=None, input_type='text'),
            inputTemplate(label="Batch size suggestion", name="batch_size_suggestion", val=None, input_type='number'),
            selectEnumTemplate(label="Accelerator", options=[task.value for task in AcceleratorEnum],  name="accelerator", error_msg=None),
            inputTemplate(label="Accelerator constrained", name="accelerator_constrained", val=None, input_type='boolean'),
            inputTemplate(label="Accelerator Summary", name="accelerator_summary", val=None, input_type='text'),
            inputTemplate(label="Accelerator Count", name="accelerator_count", val=None, input_type='number'),
            inputTemplate(label="MLM Input", name="mlm_input", val=None, input_type='text'),
            inputTemplate(label="MLM Output", name="mlm_output", val=None, input_type='text'),
            inputTemplate(label="MLM hyperparameters", name="hyperparameters", val=None, input_type='text'),
            inputListTemplate(label="Shape", name="shape", error_msg=None, input_type='number'),
        ),
        Div(id="result"),
    ))

### Field Validation Routing ###

@app.post('/shape')
def check_shape(shape_1: int | None, shape_2: int | None, shape_3: int | None, shape_4: int | None):
    shape = [shape_1, shape_2, shape_3, shape_4]
    return inputListTemplate('Shape', 'shape', shape, validate_shape(shape))

@app.post('/model_name')
def check_model_name(model_name: str | None):
    return inputTemplate("Model Name", "model_name", model_name, validate_model_name(model_name))

@app.post('/architecture')
def check_architecture(architecture: str | None):
    return inputTemplate("Architecture", "architecture", architecture, validate_architecture(architecture))

@app.post('/framework')
def check_framework(framework: str | None):
    return inputTemplate("Framework", "framework", framework, validate_framework(framework))

@app.post('/framework_version')
def check_framework_version(framework_version: str | None):
    return inputTemplate("Framework Version", "framework_version", framework_version, validate_framework_version(framework_version))

@app.post('/accelerator')
def check_accelerator(accelerator: str | None):
    return inputTemplate("Accelerator", "accelerator", accelerator, validate_accelerator(accelerator))

@app.post('/accelerator_summary')
def check_accelerator_summary(accelerator_summary: str | None):
    return inputTemplate("Accelerator Summary", "accelerator_summary", accelerator_summary, validate_accelerator_summary(accelerator_summary))

@app.post('/file_size')
def check_file_size(file_size: int | None):
    return inputTemplate("File Size", "file_size", file_size, validate_file_size(file_size))

@app.post('/memory_size')
def check_memory_size(memory_size: int | None):
    return inputTemplate("Memory Size", "memory_size", memory_size, validate_memory_size(memory_size))

@app.post('/pretrained_source')
def check_pretrained_source(pretrained_source: str | None):
    return inputTemplate("Pretrained Source", "pretrained_source", pretrained_source, validate_pretrained_source(pretrained_source))

@app.post('/total_parameters')
def check_total_parameters(total_parameters: int | None):
    return inputTemplate("Total Parameters", "total_parameters", total_parameters, validate_total_parameters(total_parameters))

@app.post('/submit')
def submit(d: dict):
    d['shape'] = [int(d.pop(f'shape_{i+1}')) if d.get(f'shape_{i+1}') else d.pop(f'shape_{i+1}') for i in range(4)]
    [task.value for task in TaskEnum]
    # from the fasthtml discord https://discordapp.com/channels/689892369998676007/1247700012952191049/1273789690691981412
    # this might change past version 0.4.4 it seems pretty hacky
    d['tasks'] = [task for task in tasks if d.pop(task, None)]
    required_keys = [
        'shape',
        'model_name',
        'architecture',
        'framework',
        'framework_version',
        'accelerator',
        'accelerator_summary',
        'file_size',
        'memory_size',
        'pretrained_source',
        'total_parameters'
    ]
    if all(d.get(key) != '' for key in required_keys):
        errors = {
            'shape': validate_shape(d['shape']),
            'model_name': validate_model_name(d.get('model_name')),
            'architecture': validate_architecture(d.get('architecture')),
            'framework': validate_framework(d.get('framework')),
            'framework_version': validate_framework_version(d.get('framework_version')),
            'accelerator': validate_accelerator(d.get('accelerator')),
            'accelerator_summary': validate_accelerator_summary(d.get('accelerator_summary')),
            'file_size': validate_file_size(d.get('file_size')),
            'memory_size': validate_memory_size(d.get('memory_size')),
            'pretrained_source': validate_pretrained_source(d.get('pretrained_source')),
            'total_parameters': validate_total_parameters(d.get('total_parameters')),
        }

        errors = {k: v for k, v in errors.items() if v is not None}

        return *[Div(error, style='color: red;') for error in errors.values()], d

    return Div("Please fill in all required fields before submitting.", style='color: red;'), d

serve()