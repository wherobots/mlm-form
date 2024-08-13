from fasthtml.common import *

import pystac
import shapely
from dateutil.parser import parse as parse_dt
from pystac.extensions.file import FileExtension

from stac_model.base import ProcessingExpression
from stac_model.input import InputStructure, MLMStatistic, ModelInput
from stac_model.output import MLMClassification, ModelOutput, ModelResult
from stac_model.schema import ItemMLModelExtension, MLModelExtension, MLModelProperties

from pydantic import ValidationError, TypeAdapter

def validate_single_field(model_class, field_name, value):
    field_info = model_class.model_fields[field_name]
    adapter = TypeAdapter(field_info.annotation)
    try:
        return adapter.validate_python(value)
    except Exception as e:
        return f"Error for field '{field_name}': {e}"


app, rt = fast_app()

@app.get('/')
def homepage():
    return Grid(Form(hx_post='/submit', hx_target='#result', hx_trigger="input delay:200ms")(
                inputListTemplate(label="Shape", name="shape", error_msg=None, input_type='number'),
                ),
                Div(id="result"),
                Div(id="logs")
            )

### Field Validation Routing ###

@app.post('/shape')
def check_shape(shape_1: int | None, shape_2: int | None, shape_3: int | None, shape_4: int | None):
    shape = [shape_1, shape_2, shape_3, shape_4]
    return shapeInputTemplate(shape, validate_shape(shape))

# TODO make this a download button
# @app.post('/submit')
# def submit(shape_1:int, shape_2:int, shape_3:int, shape_4: int, cool: str, CoolScale: int):
#     # Validates all fields in the form
#     errors = {'shape': validate_shape([shape_1,shape_2,shape_3,shape_4]),
#              'cool': validate_cool(cool),
#              'coolscale': validate_coolscale(CoolScale) }
#     # Removes the None values from the errors dictionary (No errors)
#     errors = {k: v for k, v in errors.items() if v is not None}
#     # Return Button with error message if they exist
#     return Div(id='submit-btn-container')(
#         Button(type='submit', id='submit-btn', hx_post='/submit', hx_target='#submit-btn-container', hx_swap='outerHTML')('Submit'),
#         *[Div(error, style='color: red;') for error in errors.values()])

@app.post('/submit')
def submit(d:dict):
    # hack since I don't know how to pass 4 input values with array notation
    d['shape'] = [d.pop(f'shape_{i+1}') for i in range(4)]
    return d

########################
### Validation Logic ###
########################

def validate_shape(shape: list):
    if not validate_single_field(InputStructure, "shape", shape):
        return "Please enter a valid shape"

def validate_dim_type(dim_order: list):
    if not validate_single_field(InputStructure, "dim_order", dim_order):
        return "Please enter a valid dimension ordering"

######################
### HTML Templates ###
######################

def inputTemplate(label, name, val, error_msg=None, input_type='text'):
    return Div(hx_target='this', hx_swap='outerHTML', cls=f"{error_msg if error_msg else 'Valid'}")(
               Label(label),
               Input(name=name,type=input_type,value=f'{val}',hx_post=f'/{name.lower()}',hx_indicator=f'#{name.lower()}ind'),
               Div(f'{error_msg}', style='color: red;') if error_msg else None)

def inputListTemplate(label, name, values=[None, None, None, None], error_msg=None, input_type='number'):
    return Div(hx_target='this', hx_swap='outerHTML', cls=f"{error_msg if error_msg else 'Valid'}")(
        *[
            item
            for i, val in enumerate(values)
            for item in (
                Label(f"{label} {i+1}"),
                Input(name=f'{name.lower()}_{i+1}', id=f'{name.lower()}_{i+1}', type=input_type, value=val, hx_post=f'/{name.lower()}', max = 10),
            ) if not isinstance(item, str)
        ],
        Div(f'{error_msg}', style='color: red;') if error_msg else None
    )

def shapeInputTemplate(values, error_msg=None):
    return inputListTemplate('Shape', 'shape', values, error_msg)