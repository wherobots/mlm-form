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