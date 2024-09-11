from fasthtml.common import *

from src.mlm_form.styles import *
from src.mlm_form.templates import *
from src.mlm_form.validation import *
from src.mlm_form.make_item import construct_ml_model_properties, create_pystac_item
from stac_model.runtime import AcceleratorEnum
from datetime import datetime
import pystac
import copy

app, rt = fast_app(hdrs=(picolink))

@app.get('/')
def homepage(session):
    
    return Body(
        Main(
            Header(
                H1("Machine Learning Model Metadata Form"),
                Nav(
                    A("Asset Form", href="/asset")
                )
            ),
            Section(
                P("Please complete all fields below to describe the machine learning model metadata."),
                Button("Clear Form", hx_post='/clear_form',
                       style="margin-top: 20px;", hx_target="#result", hx_swap="innerHTML")
            ),
            Grid(
                session_form(session, submitOnLoad=True),
                outputTemplate()
            ),
            style=main_element_style
        )
    )

@app.post('/clear_form')
def clear_form(session):
    session.clear()
    return session_form(session)

### Field Validation Routing ###

@app.post('/mlm_input_shape')
def check_shape(shape_1: int | None, shape_2: int | None, shape_3: int | None, shape_4: int | None):
    shape = [shape_1, shape_2, shape_3, shape_4]
    return inputListTemplate('Shape', 'shape', shape, validate_shape(shape))

@app.post('/mlm_output_shape')
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

@app.post('/accelerator_summary')
def check_accelerator_summary(accelerator_summary: str | None):
    return inputTemplate("Accelerator Summary", "accelerator_summary", accelerator_summary, validate_accelerator_summary(accelerator_summary))

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
    # this handles empty strings on submit and the fact that we have to manually collate list values
    d['mlm_input_shape'] = [int(d.pop(f'mlm_input_shape_{i+1}')) if d.get(f'mlm_input_shape_{i+1}') else d.pop(f'mlm_input_shape_{i+1}') for i in range(4)]
    d['mlm_output_shape'] = [int(d.pop(f'mlm_output_shape_{i+1}')) if d.get(f'mlm_output_shape_{i+1}') else d.pop(f'mlm_output_shape_{i+1}') for i in range(4)]
    d['mlm_input_dim_order'] = [d.pop(f'mlm_input_dim_order_{i+1}') if d.get(f'mlm_input_dim_order_{i+1}') else d.pop(f'mlm_input_dim_order_{i+1}') for i in range(4)]
    d['mlm_output_dim_order'] = [d.pop(f'mlm_output_dim_order_{i+1}') if d.get(f'mlm_output_dim_order_{i+1}') else d.pop(f'mlm_output_dim_order_{i+1}') for i in range(4)]
    d['mlm_output_classes'] = [item.strip() for item in d.get('mlm_output_classes', '').split(',')]
    # from the fasthtml discord https://discordapp.com/channels/689892369998676007/1247700012952191049/1273789690691981412
    # this might change past version 0.4.4 it seems pretty hacky
    d['tasks'] = [task for task in tasks if d.pop(task, None)]
    # d['mlm:output_tasks'] = [task for task in tasks if d.pop(task, None)]
    session['form_format_d'].update(d)
    return Div("Please fill in all required fields before submitting.", style='color: red;'), prettyJsonTemplate(session['form_format_d'])

roles = [role for role in model_asset_roles if role not in model_asset_implicit_roles]

# helper function to render out the session form
# because of the `hx_swap_oob`, this snippet can be returned by any handler and will update the form
# see https://htmx.org/examples/update-other-content/#oob
#
# `submitOnLoad` should be set to true for the initial page load so that the form will
# auto-submit to populate the results if there is saved state in the session
def session_form(session, submitOnLoad=False):
    session.setdefault('stac_format_d', {})
    session.setdefault('form_format_d', {})
    result = session.get('form_format_d', {})
    trigger = "input delay:200ms, load" if submitOnLoad and result else "input delay:200ms"
    session_form = Form(hx_post='/submit', hx_target='#result', hx_trigger=trigger, id="session_form", hx_swap_oob="#session_form")(
                    inputTemplate(label="Model Name", name="model_name", val='', input_type='text'),
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
                    inputTemplate(label="MLM hyperparameters", name="hyperparameters", val='', input_type='text'),
                    modelInputTemplate(label="MLM Input", name="mlm_input"),
                    modelOutputTemplate(label="MLM Output", name="mlm_output"),
                )
    fill_form(session_form, result)
    return session_form

def session_asset_form(session, submitOnLoad=False):
    session.setdefault('stac_format_d', {})
    session.setdefault('form_format_d', {})
    session['stac_format_d'].setdefault('assets', {})
    session['form_format_d'].setdefault('assets', {})
    result = session['form_format_d'].get('assets', {})
    trigger = "input delay:200ms, load" if submitOnLoad and result else "input delay:200ms"
    session_asset_form = Form(hx_post='/submit_asset', hx_target='#result', hx_trigger=trigger, id="session_asset_form", hx_swap_oob="#session_asset_form")(
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
                )
    fill_form(session_asset_form, result)
    return session_asset_form

@app.get('/asset')
def asset_homepage(session):
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
                session_asset_form(session, submitOnLoad=True),
                outputTemplate()
            ),
            style=main_element_style
        )
    )

@app.post('/submit_asset')
def submit_asset(session, d: dict):
    d['roles'] = model_asset_implicit_roles + [role for role in roles if d.pop(role, None)]
    d['type'] = d.pop('type')
    session['form_format_d']['assets'].update(d)
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
        return error_template(e), prettyJsonTemplate(session['form_format_d'])
    return prettyJsonTemplate(session['form_format_d'])

serve()