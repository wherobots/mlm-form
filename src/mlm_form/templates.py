from fasthtml.common import *

######################
### HTML Templates ###
######################

def inputTemplate(label, name, val, error_msg=None, input_type='text'):
    return Div(hx_target='this', hx_swap='outerHTML', cls=f"{error_msg if error_msg else 'Valid'}", style="display: flex; flex-direction: column; align-items: center;")(
               Label(label),
               Input(name=name,type=input_type,value=f'{val}',hx_post=f'/{name.lower()}', style="width: 400px; text-align: center;"),
               Div(f'{error_msg}', style='color: red;') if error_msg else None)

def inputListTemplate(label, name, values=[None, None, None, None], error_msg=None, input_type='number'):
    return Div(hx_target='this', hx_swap='outerHTML', cls=f"{error_msg if error_msg else 'Valid'}", style="display: flex; flex-direction: column; align-items: center;")(
        Label(label),
        Div(style="display: flex; gap: 20px; justify-content: center; width: 100%; max-width: 600px;")(
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
    return Div(style="display: flex; flex-direction: column; align-items: flex-start;")(
        *[Div(CheckboxX(id=option, label=option), style="width: 100%;") for option in options]
    )

def selectEnumTemplate(label, options, name, error_msg=None):
    return Div(hx_target='this', hx_swap='outerHTML', cls=f"{error_msg if error_msg else 'Valid'}", style="display: flex; flex-direction: column; align-items: center;")(
        Label(label),
        Select(
            *mk_opts(name, options),
            name=name,
            hx_post=f'/{name.lower()}'),
        Div(f'{error_msg}', style='color: red;') if error_msg else None)

def selectCheckboxTemplate(label, options, name, error_msg=None):
    return Div(hx_target='this', hx_swap='outerHTML', cls=f"{error_msg if error_msg else 'Valid'}", style="display: flex; flex-direction: column; align-items: center;")(
        Label(label),
        Group(
            mk_checkbox(options),
            name=name,
            hx_post=f'/{name.lower()}'),
        Div(f'{error_msg}', style='color: red;') if error_msg else None)

def trueFalseRadioTemplate(label, name, error_msg=None):
    return Div(
        Label(label),
        Div(
            Input(type="radio", name=name, value="true"),
            Label("True", for_=name),
            Input(type="radio", name=name, value="false"),
            Label("False", for_=name),
            style="display: flex; flex-direction: row; align-items: center;"
        ),
        Div(f'{error_msg}', style='color: red;') if error_msg else None,
        style="display: flex; flex-direction: column; align-items: center;"
    )

def modelInputTemplate(label, name, error_msg=None):
    return Div(
        Label(label),
        Div(
            Label("Name"),
            Input(type="text", name=f"{name}[name]"),
            style="display: flex; flex-direction: column; align-items: flex-start;"
        ),
        Div(
            Label("Bands"),
            Input(type="text", name=f"{name}[bands]"),
            style="display: flex; flex-direction: column; align-items: flex-start;"
        ),
        Div(
            Label("Norm by Channel"),
            CheckboxX(name=f"{name}[norm_by_channel]"),
            style="display: flex; flex-direction: column; align-items: flex-start;"
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
                name=f"{name}[norm_type]"
            ),
            style="display: flex; flex-direction: column; align-items: flex-start;"
        ),
        Div(
            Label("Norm Clip"),
            Input(type="text", name=f"{name}[norm_clip]"),
            style="display: flex; flex-direction: column; align-items: flex-start;"
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
                name=f"{name}[resize_type]"
            ),
            style="display: flex; flex-direction: column; align-items: flex-start;"
        ),
        Div(
            Label("Statistics"),
            Input(type="text", name=f"{name}[statistics]"),
            style="display: flex; flex-direction: column; align-items: flex-start;"
        ),
        Div(
            Label("Pre Processing Function"),
            Input(type="text", name=f"{name}[pre_processing_function]"),
            style="display: flex; flex-direction: column; align-items: flex-start;"
        ),
        Div(f'{error_msg}', style='color: red;') if error_msg else None,
        style="display: flex; flex-direction: column; align-items: center;"
    )
