from fasthtml.common import *

from src.mlm_form.styles import *
from src.mlm_form.templates import *
from src.mlm_form.validation import *
from src.mlm_form.make_item import construct_ml_model_properties, construct_assets, create_pystac_item
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

def form_format_to_stac_format_input(d):
    # TODO for some reason the enum and checkbox template don't set default empty values
    d['mlm_input_norm_type'] = d.get('mlm_input_norm_type')
    d['mlm_input_resize_type'] = d.get('mlm_input_resize_type')
    d['mlm_input_data_type'] = d.get('mlm_input_data_type')
    d['mlm_output_data_type'] = d.get('mlm_output_data_type')
    d['accelerator'] = d.get('accelerator')
    d['accelerator_constrained'] = d.get('accelerator_constrained')
    # this handles empty strings on submit and the fact that we have to manually collate list values
    d['mlm_input_shape'] = [int(d.pop(f'mlm_input_shape_{i+1}')) if d.get(f'mlm_input_shape_{i+1}') else d.pop(f'mlm_input_shape_{i+1}') for i in range(4)]
    d['mlm_output_shape'] = [int(d.pop(f'mlm_output_shape_{i+1}')) if d.get(f'mlm_output_shape_{i+1}') else d.pop(f'mlm_output_shape_{i+1}') for i in range(4)]
    # TODO need to raise error to user if dim values aren't unique.
    # need to raise and prettify any error from pystac validation
    d['mlm_input_dim_order'] = [d.pop(f'mlm_input_dim_order_{i+1}') if d.get(f'mlm_input_dim_order_{i+1}') else d.pop(f'mlm_input_dim_order_{i+1}') for i in range(4)]
    d['mlm_output_dim_order'] = [d.pop(f'mlm_output_dim_order_{i+1}') if d.get(f'mlm_output_dim_order_{i+1}') else d.pop(f'mlm_output_dim_order_{i+1}') for i in range(4)]
    d['mlm_output_classes'] = [item.strip() for item in d.get('mlm_output_classes', '').split(',')]
    d['mlm_input_mean'] = [float(item.strip()) if item != '' else [''] for item in d.get('mlm_input_mean', '').split(',')]
    d['mlm_input_std'] = [float(item.strip()) if item != '' else [''] for item in d.get('mlm_input_std', '').split(',')]
    d['mlm_input_bands'] = [item.strip() if item != '' else [''] for item in d.get('mlm_input_bands', '').split(',')]
    # from the fasthtml discord https://discordapp.com/channels/689892369998676007/1247700012952191049/1273789690691981412
    # this might change past version 0.4.4 it seems pretty hacky
    d['tasks'] = [task for task in tasks if d.pop(task, None)]
    # d['mlm:output_tasks'] = [task for task in tasks if d.pop(task, None)]
    d['accelerator_count'] = int(d.get('accelerator_count', 1))
    d['memory_size'] = int(d.get('memory_size', 1))
    d['total_parameters'] = int(d.get('total_parameters', 1))
    return d

@app.post('/submit')
def submit(session, d: dict):
    session.setdefault('stac_format_d', {})
    session.setdefault('form_format_d', {})
    session['form_format_d'].update(copy.deepcopy(d))
    d = form_format_to_stac_format_input(d)
    # fix??? preserves state when going back to mlm form but not assets
    session['stac_format_d'].update(d)
    # this does not
    ml_model_metadata = construct_ml_model_properties(d)
    assets = construct_assets(session['stac_format_d'].get('assets'))
    item = create_pystac_item(ml_model_metadata, assets)
    return Div("Please fill in all required fields before submitting.", style='color: red;'), prettyJsonTemplate(item)
    
    # This preserves state
    # session['stac_format_d'].update(d)
    # return Div("Please fill in all required fields before submitting.", style='color: red;'), prettyJsonTemplate(session['stac_format_d'])

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
                    trueFalseRadioTemplate(label="Is it pretrained for one or more tasks and one or more data domains?", name="pretrained"),
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
                    inputTemplate(label="Accelerator Count", name="accelerator_count", val=1, input_type='number'),
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
    # TODO decide whether to show just asset section or full json on asset page on load and edit
    #result = session['form_format_d'].get('assets', {})
    trigger = "input delay:200ms, load" if submitOnLoad and session.get('stac_format_d') else "input delay:200ms"
    session_asset_form = Form(hx_post='/submit_asset', hx_target='#result', hx_trigger=trigger, id="session_asset_form", hx_swap_oob="#session_asset_form")(
                    inputTemplate(label="Title", name="title", val='', input_type='text', canValidateInline=False),
                    inputTemplate(label="URI", name="href", val='', input_type='text', canValidateInline=False),
                    inputTemplate(label="Media Type", name="media_type", val='', input_type='text', canValidateInline=False),
                    selectCheckboxTemplate(label="Roles", options=roles, name="roles", canValidateInline=False),
                    selectEnumTemplate(
                        label="Artifact Type",
                        options=model_asset_artifact_types,
                        name="mlm:artifact_type",
                        canValidateInline=False
                    ),
                )
    fill_form(session_asset_form, session['form_format_d'].get('assets', {}))
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
    session['form_format_d']['assets'].update(copy.deepcopy(d))
    d['roles'] = model_asset_implicit_roles + [role for role in roles if d.pop(role, None)]
    d['type'] = d.pop('media_type')
    session['stac_format_d']['assets'].update(d)
    # pystac doesn't directly support validating an asset, so put the asset inside a
    # dummy item and run the validation on that
    dummy_item = pystac.Item(
        id="item",
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
    dummy_item.assets["model"] = pystac.Asset.from_dict(d)

    assets = construct_assets(session['stac_format_d'].get('assets'))

    try:
        validation_result = pystac.validation.validate(dummy_item)
    except pystac.errors.STACValidationError as e:
        error_message = str(e)
        if "'href'" in error_message and "non-empty" in error_message:
            error_message = "The 'URI' field must be non-empty."
        else:
            error_message = f"STACValidationError: {error_message}".replace('\\n', '<br>')
        return error_template(error_message), prettyJsonTemplate(assets["model"].to_dict())
    return prettyJsonTemplate(assets["model"].to_dict())
serve()