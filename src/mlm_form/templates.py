from fasthtml.common import *
import json

from .styles import *
from .validation import *

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

def mk_checkbox(options):
    return Div(style=control_container_style)(
        *[Div(CheckboxX(id=option, label=option), style="width: 100%;") for option in options]
    )

def selectEnumTemplate(label, options, name, error_msg=None, canValidateInline=True):
    return Div(hx_target='this', hx_swap='outerHTML', cls=f"{error_msg if error_msg else 'Valid'}", style=control_container_style)(
        labelDecoratorTemplate(Label(label), name in model_required_keys),
        Select(
            *mk_opts(name, options),
            name=name,
            hx_post=f'/{name.lower()}' if canValidateInline else None,
            style=select_input_style),
        Div(f'{error_msg}', style='color: red;') if error_msg else None)

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
            Input(type="text", name=f"{name}[name]", style=text_input_style)
        ),
        Div(
            Label("Bands"),
            Input(type="text", name=f"{name}[bands]", style=text_input_style),
        ),
        Div(
            Label("Norm by Channel"),
            CheckboxX(name=f"{name}[norm_by_channel]"),
            style="margin-bottom: 15px;"
        ),
        Div(
            Label("Norm Type"),
            Select(
                Option("Select Norm Type", disabled=True, selected=True),
                Option("min-max", value="min-max"),
                Option("z-score", value="z-score"),
                Option("l1", value="l1"),
                Option("l2", value="l2"),
                Option("l2sqr", value="l2sqr"),
                Option("hamming", value="hamming"),
                Option("hamming2", value="hamming2"),
                Option("type-mask", value="type-mask"),
                Option("relative", value="relative"),
                Option("inf", value="inf"),
                name=f"{name}[norm_type]",
                style=select_input_style
            ),
        ),
        Div(
            Label("Norm Clip"),
            Input(type="text", name=f"{name}[norm_clip]", style=text_input_style),
        ),
        Div(
            Label("Resize Type"),
            Select(
                Option("Select Resize Type", disabled=True, selected=True),
                Option("crop", value="crop"),
                Option("pad", value="pad"),
                Option("interpolation-nearest", value="interpolation-nearest"),
                Option("interpolation-linear", value="interpolation-linear"),
                Option("interpolation-cubic", value="interpolation-cubic"),
                Option("interpolation-area", value="interpolation-area"),
                Option("interpolation-lanczos4", value="interpolation-lanczos4"),
                Option("interpolation-max", value="interpolation-max"),
                Option("wrap-fill-outliers", value="wrap-fill-outliers"),
                Option("wrap-inverse-map", value="wrap-inverse-map"),
                name=f"{name}[resize_type]",
                style=select_input_style
            ),
        ),
        Div(
            Label("Statistics"),
            Input(type="text", name=f"{name}[statistics]", style=text_input_style),
        ),
        Div(
            Label("Pre Processing Function"),
            Input(type="text", name=f"{name}[pre_processing_function]", style=text_input_style),
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

def outputTemplate(id):
    return Div(
        Div(id=id, style="position: fixed; right: 50px; width: 500px;"),
        style="position: relative;"
    )

def prettyJsonTemplate(obj):
    return Pre(json.dumps(obj, indent = 4), style="margin-top: 25px; width: 100%;")