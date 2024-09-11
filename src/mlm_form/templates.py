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

def inputTemplate(label, name, val, error_msg=None, input_type='text', canValidateInline=True):
    return Div(hx_target='this', hx_swap='outerHTML', cls=f"{error_msg if error_msg else 'Valid'}", style=control_container_style)(
               labelDecoratorTemplate(Label(label), name in model_required_keys),
               Input(name=name,type=input_type,value=f'{val}',hx_post=f'/{name.lower()}' if canValidateInline else None, style=text_input_style),
               Div(f'{error_msg}', style='color: red;') if error_msg else None)

def inputListTemplate(label, name, values=[None, None, None, None], error_msg=None, input_type='number'):
    return Div(hx_target='this', hx_swap='outerHTML', cls=f"{error_msg if error_msg else 'Valid'}", style=control_container_style)(
        labelDecoratorTemplate(Label(label), name in model_required_keys),
        Div(style="display: flex; gap: 20px; justify-content: flex-start; width: 100%; max-width: 600px;")(
            *[
                Input(name=f'{name.lower()}_{i+1}', id=f'{name.lower()}_{i+1}',
                      placeholder=f"Enter {label} {i+1}", type=input_type, value=val,
                      style="width: 120px;", hx_post=f'/{name.lower()}')
                for i, val in enumerate(values)
            ]
        ),
        Div(f'{error_msg}', style='color: red;') if error_msg else None
    )

def mk_opts(nm, cs):
    return (
        Option(f'-- select {nm} --', disabled='', selected='', value=''),
        *map(Option, cs))

def selectEnumTemplate(label, options, name, error_msg=None, canValidateInline=True):
    return Div(hx_target='this', hx_swap='outerHTML', cls=f"{error_msg if error_msg else 'Valid'}", style=control_container_style)(
        labelDecoratorTemplate(Label(label), name in model_required_keys),
        Select(
            *mk_opts(name, options),
            name=name,
            hx_post=f'/{name.lower()}' if canValidateInline else None,
            style=select_input_style),
        Div(f'{error_msg}', style='color: red;') if error_msg else None)

def mk_checkbox(options):
    return Div(style=control_container_style)(
        *[Div(CheckboxX(id=option, label=option), style="width: 100%;") for option in options]
    )

def selectCheckboxTemplate(label, options, name, error_msg=None, canValidateInline=True):
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
            Input(type="radio", name=name, value="true"),
            Label("True", for_=name),
            Input(type="radio", name=name, value="false"),
            Label("False", for_=name),
            style="display: flex; flex-direction: row; align-items: center;"
        ),
        Div(f'{error_msg}', style='color: red;') if error_msg else None,
        style=f'{control_container_style} margin-bottom: 15px;'
    )

def modelInputTemplate(label, name, error_msg=None):
    return Div(
        labelDecoratorTemplate(H4(label, style="margin-left: -30px;"), name in model_required_keys),
        Div(
            Label("Name"),
            Input(type="text", name=f"{name}_name", style=text_input_style)
        ),
        Div(
            Label("Bands"),
            Input(type="text", name=f"{name}_bands", style=text_input_style),
        ),
        inputListTemplate(label="Shape", name=f"{name}_shape", error_msg=None, input_type='number'),
        inputListTemplate(label="Dimension Order", name=f"{name}_dim_order", error_msg=None, input_type='text'),
        Div(
            Label("Data Type"),
        Input(type="text", name=f"{name}_data_type", style=text_input_style),
        ),
        Div(
            Label("Norm by Channel"),
            CheckboxX(name=f"{name}_norm_by_channel"),
            style="margin-bottom: 15px;"
        ),
        selectEnumTemplate("Normalization Type", normalize_type_values,
            f"{name}_norm_type", error_msg=None, canValidateInline=False),
        Div(
            Label("Norm Clip"),
            Input(type="text", name=f"{name}_norm_clip", style=text_input_style),
        ),
        selectEnumTemplate("Resize Type", resize_type_values,
            f"{name}_resize_type", error_msg=None, canValidateInline=True),
        # TODO this should be made dynamic so that users can create a new field for a statistic and
        # then enter an N length list of values for that statistic similar to 
        # https://gallery.fastht.ml/start_simple/sqlite_todo/code
        Div(
        Label("Mean Statistic (currently you must enter a single comma separated list of values)"),
        Input(type="text", name=f"{name}_mean", style=text_input_style),
        ),
        Div(
        Label("Std Statistic (currently you must enter a single comma separated list of values)"),
        Input(type="text", name=f"{name}_std", style=text_input_style),
        ),
        # Div(
        #     Label("Pre Processing Function"),
        #     Input(type="text", name=f"{name}_pre_processing_function", style=text_input_style),
        # ),
        Div(f'{error_msg}', style='color: red;') if error_msg else None,
        style=f'{control_container_style} margin-left: 30px;'
    )

def mk_input(**kw): return Input(id="new-title", name="title", placeholder="New Todo", **kw)

def modelOutputTemplate(label, name, error_msg=None):
    return Div(
        labelDecoratorTemplate(H4(label, style="margin-left: -30px;"), name in model_required_keys),
        Div(
            Label("Name"),
            Input(type="text", name=f"{name}_name", style=text_input_style)
        ),
        # TODO disabling this because we only work with models tha accept single outputs for now but
        # this should be flipped on and made working in the future
        #selectCheckboxTemplate(label="Tasks", options=tasks, name=f"{name}_tasks", canValidateInline=False),
        inputListTemplate(label="Shape", name=f"{name}_shape", error_msg=None, input_type='number'),
        inputListTemplate(label="Dimension Order", name=f"{name}_dim_order", error_msg=None, input_type='text'),
        Div(
        Label("Data Type"),
        Input(type="text", name=f"{name}_data_type", style=text_input_style),
        ),
        # TODO this should be made dynamic so that users can enter an N length list of classes similar to 
        # https://gallery.fastht.ml/start_simple/sqlite_todo/code
        Div(
        Label("Categories (currently you must enter a single comma separated list of categories)"),
        Input(type="text", name=f"{name}_classes", style=text_input_style),
        ),
        # Div(
        #     Label("Post Processing Function"),
        #     Input(type="text", name=f"{name}_pre_processing_function", style=text_input_style),
        # ),
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
    return Pre(json.dumps(obj, indent = 4), style="margin-top: 25px; width: 100%;")

def error_template(msg):
    return  Div(msg, style='color: red; white-space: pre-wrap; margin-left: 10px; margin-bottom: 15px; text-indent: -10px;')