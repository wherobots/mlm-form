from fasthtml.common import *
import json

from .styles import *
from .validation import *
from stac_model.input import NormalizeType, ResizeType
from typing import get_args
from stac_model.base import TaskEnum

 # idk what Typing.Literal is or why I need to do this :(
normalize_type_values = [value for value in get_args(get_args(NormalizeType)[0])]
resize_type_values = [value for value in get_args(get_args(ResizeType)[0])]
tasks = [task.value for task in TaskEnum]
######################
### HTML Templates ###
######################

def inputTemplate(label, name, val, placeholder=None, error_msg=None, input_type='text', canValidateInline=False):
    return Div(hx_target='this', hx_swap='outerHTML', cls=f"{error_msg if error_msg else 'Valid'}", style=control_container_style)(
               labelDecoratorTemplate(Label(label), name in model_required_keys),
               Input(id=name, name=name,type=input_type, placeholder=placeholder, value=f'{val}',hx_post=f'/{name.lower()}' if canValidateInline else None, style=text_input_style),
               Div(f'{error_msg}', style='color: red;') if error_msg else None)

def inputListTemplate(label, name, placeholder=None, values=[None, None, None, None], error_msg=None, input_type='number', canValidateInline=False):
    return Div(hx_target='this', hx_swap='outerHTML', cls=f"{error_msg if error_msg else 'Valid'}", style=control_container_style)(
        labelDecoratorTemplate(Label(label), name in model_required_keys),
        Div(style="display: flex; gap: 20px; justify-content: flex-start; width: 100%; max-width: 600px;")(
            *[
                Input(name=f'{name.lower()}_{i+1}', id=f'{name.lower()}_{i+1}',
                      placeholder=placeholder, type=input_type, value=val,
                      style="width: 160px;", hx_post=f'/{name.lower()}' if canValidateInline else None)
                for i, val in enumerate(values)
            ]
        ),
        Div(f'{error_msg}', style='color: red;') if error_msg else None
    )

def mk_opts(nm, cs):
    return (
        Option(f'-- select {nm} --', disabled='', selected='', value=''),
        *map(lambda c: Option(c, value=c), cs))

def selectEnumTemplate(label, options, name, get=None, hx_target=None, error_msg=None, canValidateInline=False):
    return Div(hx_target='this', hx_swap='outerHTML', cls=f"{error_msg if error_msg else 'Valid'}", style=control_container_style)(
        labelDecoratorTemplate(Label(label), name in model_required_keys),
        Select(
            *mk_opts(name, options),
            name=name,
            hx_post=f'/{name.lower()}' if canValidateInline else None,
            get=get,
            hx_target=hx_target,
            style=select_input_style),
        Div(f'{error_msg}', style='color: red;') if error_msg else None)

def mk_checkbox(options):
    return Div(style=control_container_style)(
        *[Div(CheckboxX(id=option, label=option), style="width: 100%;") for option in options]
    )

def selectCheckboxTemplate(label, options, name, error_msg=None, canValidateInline=False):
    return Div(hx_target='this', hx_swap='outerHTML', cls=f"{error_msg if error_msg else 'Valid'}", style=control_container_style)(
        labelDecoratorTemplate(Label(label), name in model_required_keys),
        Group(
            mk_checkbox(options),
            name=name,
            hx_post=f'/{name.lower()}' if canValidateInline else None),
        Div(f'{error_msg}', style='color: red;') if error_msg else None)

def trueFalseRadioTemplate(label, name, error_msg=None):
    return Div(
        labelDecoratorTemplate(Label(label), name in model_required_keys),
        Div(
            Input(type="radio", name=f"{name}", value="true"),
            Label("True", for_=name),
            Input(type="radio", name=f"{name}", value="false"),
            Label("False", for_=name),
            style="display: flex; flex-direction: row; align-items: center;"
        ),
        Div(f'{error_msg}', style='color: red;') if error_msg else None,
        style=f'{control_container_style} margin-bottom: 15px;'
    )

def modelInputTemplate(label, name, form_data, error_msg=None):
    stats= update_statistics_by_norm(form_data.get('mlm_input_norm_type'))
    return Div(
        labelDecoratorTemplate(H4(label, style="margin-left: -30px;"), name in model_required_keys),
        Div(
            Label("Name"),
            Input(type="text", name=f"{name}_name", placeholder="A descriptive name for the model input", style=text_input_style)
        ),
        Div(
            Label("Bands (enter a single comma separated list of values)"),
            Input(type="text", name=f"{name}_bands", placeholder='''e.g. B01,B02,B03,B04,B05,B06,B07,B08,B8A,B09,B10,B11,B12''',
                style=text_input_style),
        ),
        inputListTemplate(label="Input Dimension Sizes", placeholder="Enter Value", name=f"{name}_shape", error_msg=None, input_type='number'),
        inputListTemplate(label="Input Dimension Labels", placeholder="Enter Text Label", name=f"{name}_dim_order", error_msg=None, input_type='text'),
        selectEnumTemplate("Input Data Type", datatypes,
            f"{name}_data_type", error_msg=None, canValidateInline=False),
        trueFalseRadioTemplate("Normalize Each Channel By Statistics", f"{name}_norm_by_channel", error_msg=None),
        selectEnumTemplate("Normalization Type", normalize_type_values,
            f"{name}_norm_type", error_msg=None, canValidateInline=False),
        ## TODO this isn't working route not found
        stats,
        selectEnumTemplate("Resize Type", resize_type_values,
            f"{name}_resize_type", error_msg=None, canValidateInline=False),
        Div(f'{error_msg}', style='color: red;') if error_msg else None,
        style=f'{control_container_style} margin-left: 30px;'
    )

def mk_input(**kw): return Input(id="new-title", name="title", placeholder="New Todo", **kw)

def modelOutputTemplate(label, name, error_msg=None):
    return Div(
        labelDecoratorTemplate(H4(label, style="margin-left: -30px;"), name in model_required_keys),
        Div(
            Label("Name"),
            Input(type="text", name=f"{name}_name", placeholder="A descriptive name of the model output content", style=text_input_style)
        ),
        # TODO disabling this because we only work with models tha accept single outputs for now but
        # this should be flipped on and made working in the future
        #selectCheckboxTemplate(label="Tasks", options=tasks, name=f"{name}_tasks", canValidateInline=False),
        inputListTemplate(label="Output Dimension Sizes", name=f"{name}_shape", placeholder="Enter Value", error_msg=None, input_type='number'),
        # TODO possibly overly restrictive schema, this can;t contain numeric characters
        inputListTemplate(label="Output Dimension Labels", name=f"{name}_dim_order", placeholder="Enter Text Label", error_msg=None, input_type='text'),
        selectEnumTemplate("Output Data Type", datatypes,
            f"{name}_data_type", error_msg=None, canValidateInline=False),
        # TODO this should be made dynamic so that users can enter an N length list of classes similar to
        # https://gallery.fastht.ml/start_simple/sqlite_todo/code
        Div(
        Label("Classes (enter a single comma separated list of classes)"),
        Input(type="text", name=f"{name}_classes", placeholder=''' e.g. "Annual Crop, Forest, Herbaceous Vegetation, Highway, Industrial Buildings, Pasture, Permanent Crop, Residential Buildings, River, SeaLake"''',
               style=text_input_style),
        ),
        Div(f'{error_msg}', style='color: red;') if error_msg else None,
        style=f'{control_container_style} margin-left: 30px;'
    )

def labelDecoratorTemplate(label, isRequired):
    required_indicator = Span('*', style="color: red; margin-right: 5px;")
    return Div(
        required_indicator if isRequired else None,
        label,
        style="display: flex;"
    )

def outputTemplate():
    return Div(
        Div(id="result", style="position: fixed; right: 50px; width: 500px; height: calc(100vh - 250px); overflow: auto;"),
        style="position: relative;"
    )

def prettyJsonTemplate(obj):
    return Div(Div(Pre(json.dumps(obj, indent = 4), style="margin-top: 25px; width: 100%;"),
               style="position: fixed; right: 50px; width: 500px; height: calc(100vh - 250px); overflow: auto;", id='#result'), style="position: relative;")

def error_template(msg):
    return  Div(msg, style='color: red; white-space: pre-wrap; margin-left: 10px; margin-bottom: 15px; text-indent: -10px;')

def update_statistics_by_norm(mlm_input_norm_type: str):
    if mlm_input_norm_type == 'none':
        return Div(name='statistics')
    elif mlm_input_norm_type == 'z-score':
        return  Div(Div(
                Label("Mean Statistic (enter a single comma separated list of values)"),
                Input(type="text", name=f"mlm_input_mean", 
                    placeholder='''e.g. 1354.40546513, 1118.24399958, 1042.92983953, 947.62620298,
                                            1199.47283961, 1999.79090914, 2369.22292565,
                                            2296.82608323, 732.08340178, 12.11327804,
                                            1819.01027855, 1118.92391149, 2594.14080798''',
                                            style=text_input_style),
            ),
            Div(
                Label("Std Statistic (enter a single comma separated list of values)"),
                Input(type="text", name=f"mlm_input_std", 
                    placeholder='''e.g. 245.71762908, 333.00778264, 395.09249139,
                                        593.75055589,
                                        566.4170017,
                                        861.18399006,
                                        1086.63139075,
                                        1117.98170791,
                                        404.91978886,
                                        4.77584468,
                                        1002.58768311,
                                        761.30323499,
                                        1231.58581042''',
                                        style=text_input_style),

            ), name='statistics')
    elif mlm_input_norm_type == 'min-max':
        return  Div(
                Div(
                Label("Min Statistic (enter a single comma separated list of values)"),
                Input(type="text", name=f"mlm_input_min", 
                    placeholder='''e.g. ....''', style=text_input_style)),
                Div(
                Label("Max Statistic (enter a single comma separated list of values)"),
                Input(type="text", name=f"mlm_input_max", 
                    placeholder='''e.g. ....''', style=text_input_style)),
                name='statistics')
    else:
        return Div(name='statistics')