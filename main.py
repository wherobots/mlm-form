from fasthtml.common import *

from src.mlm_form.styles import *
from src.mlm_form.templates import *
from src.mlm_form.validation import *
from src.mlm_form.make_item import *
from stac_model.base import TaskEnum
from stac_model.runtime import AcceleratorEnum
from datetime import datetime
import pystac

app, rt = fast_app(hdrs=(picolink))
tasks = [task.value for task in TaskEnum]

@app.get('/')
def homepage():
    return Body(
        Main(
            Header(
                H1("Machine Learning Model Metadata Form"),
                Nav(
                    A("Asset Form", href="/asset")
                )
            ),
            Section(
                P("Please complete all fields below to describe the machine learning model metadata.")
            ),
            Grid(
                Form(hx_post='/submit', hx_target='#result', hx_trigger="input delay:200ms")(
                    inputTemplate(label="Model Name", name="name", val='', input_type='text'),
                    inputTemplate(label="Architecture", name="architecture", val='', input_type='text'),
                    selectCheckboxTemplate(label="Tasks", options=tasks, name="tasks", canValidateInline=False),
                    inputTemplate(label="Framework", name="framework", val='', input_type='text'),
                    inputTemplate(label="Framework Version", name="framework_version", val='', input_type='text'),
                    inputTemplate(label="Memory Size", name="memory_size", val='', input_type='number'),
                    inputTemplate(label="Total Parameters", name="total_parameters", val='', input_type='number'),
                    inputTemplate(label="Is it pretrained?", name="pretrained", val='', input_type='boolean'),
                    inputTemplate(label="Pretrained source", name="pretrained_source", val='', input_type='text'),
                    inputTemplate(label="Batch size suggestion", name="batch_size_suggestion", val='', input_type='number'),
                    selectEnumTemplate(
                        label="Accelerator",
                        options=[task.value for task in AcceleratorEnum],
                        name="accelerator",
                        error_msg=None,
                        canValidateInline=False
                    ),
                    trueFalseRadioTemplate(label="Accelerator constrained", name="accelerator_constrained"),
                    inputTemplate(label="Accelerator Summary", name="accelerator_summary", val='', input_type='text'),
                    inputTemplate(label="Accelerator Count", name="accelerator_count", val='', input_type='number'),
                    modelInputTemplate(label="MLM Input", name="mlm:input"),
                    inputTemplate(label="MLM Output", name="output", val='', input_type='text'),
                    inputTemplate(label="MLM hyperparameters", name="hyperparameters", val='', input_type='text'),
                ),
                outputTemplate('result')
            ),
            style=main_element_style
        )
    )

### Field Validation Routing ###

@app.post('/shape')
def check_shape(shape_1: int | None, shape_2: int | None, shape_3: int | None, shape_4: int | None):
    shape = [shape_1, shape_2, shape_3, shape_4]
    return inputListTemplate('Shape', 'shape', shape, validate_shape(shape))

@app.post('/name')
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
def submit(session, d: dict):
    session.setdefault('result_d', {})
    d['shape'] = [int(d.pop(f'shape_{i+1}')) if d.get(f'shape_{i+1}') else d.pop(f'shape_{i+1}') for i in range(4)]
    d['dim_order'] = [int(d.pop(f'dim_order_{i+1}')) if d.get(f'dim_order_{i+1}') else d.pop(f'dim_order_{i+1}') for i in range(4)]
    # from the fasthtml discord https://discordapp.com/channels/689892369998676007/1247700012952191049/1273789690691981412
    # this might change past version 0.4.4 it seems pretty hacky
    d['tasks'] = [task for task in tasks if d.pop(task, None)]
    session['result_d'].update(d)
    if all(d.get(key) != '' for key in model_required_keys):
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
        return *[error_template(error) for error in errors.values()], prettyJsonTemplate(session['result_d'])
    return Div("Please fill in all required fields before submitting.", style='color: red;'), prettyJsonTemplate(session['result_d'])

roles = [role for role in model_asset_roles if role not in model_asset_implicit_roles]

@app.get('/asset')
def asset_homepage():
    return Body(
        Main(
            Header(
                H1("Machine Learning Model Metadata Form"),
                Nav(
                    A("MLM Form", href="/")
                )
            ),
            Section(
                P("Please complete all fields below to describe the machine learning model asset.")
            ),
            Grid(
                Form(hx_post='/submit_asset', hx_target='#result', hx_trigger="input delay:200ms")(
                    inputTemplate(label="Title", name="title", val='', input_type='text', canValidateInline=False),
                    inputTemplate(label="URI", name="href", val='', input_type='text', canValidateInline=False),
                    inputTemplate(label="Media Type", name="type", val='', input_type='text', canValidateInline=False),
                    selectCheckboxTemplate(label="Roles", options=roles, name="roles", canValidateInline=False),
                    selectEnumTemplate(
                        label="Artifact Type",
                        options=model_asset_artifact_types,
                        name="mlm:artifact_type",
                        canValidateInline=False
                    ),
                ),
                outputTemplate('result')
            ),
            style=main_element_style
        )
    )

@app.post('/submit_asset')
def submit_asset(session, d: dict):
    session.setdefault('result_d', {})
    d['roles'] = model_asset_implicit_roles + [role for role in roles if d.pop(role, None)]
    session['result_d']['assets']= {}
    session['result_d']['assets'].update(d)
    # pystac doesn't directly support validating an asset, so put the asset inside a
    # dummy item and run the validation on that
    dummy_item = pystac.Item(
        id="example-item",
        geometry={
            "type": "Polygon",
            "coordinates": [
                [[-101.0, 40.0], [-101.0, 41.0], [-100.0, 41.0], [-100.0, 40.0], [-101.0, 40.0]]
            ]
        },
        bbox=[-101.0, 40.0, -100.0, 41.0],
        datetime=datetime.utcnow(),
        properties={}
    )
    dummy_item.assets["example"] = pystac.Asset.from_dict(d)
    try:
        validation_result = pystac.validation.validate(dummy_item)
    except pystac.errors.STACValidationError as e:
        return error_template(e), prettyJsonTemplate(session['result_d'])
    return prettyJsonTemplate(session['result_d'])

serve()