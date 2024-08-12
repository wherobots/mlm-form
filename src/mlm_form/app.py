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
    # Create a TypeAdapter using the field's annotation/type
    adapter = TypeAdapter(field_info.annotation)
    return adapter.validate_python(value)

app, rt = fast_app()

@app.get('/')
def homepage():
    return Form(hx_post='/submit', hx_target='#submit-btn-container', hx_swap='outerHTML')(
                # Calls /email route to validate email
                Div(hx_target='this', hx_swap='outerHTML')(
                    Label(_for='shape')('Shape'),
                    Input(type='number', name='shape', id='shape', hx_post='/shape', hx_indicator='#shapeind'),
                    Input(type='number', name='shape', id='shape', hx_post='/shape', hx_indicator='#shapeind'),
                    Input(type='number', name='shape', id='shape', hx_post='/shape', hx_indicator='#shapeind'),
                    Input(type='number', name='shape', id='shape', hx_post='/shape', hx_indicator='#shapeind')),
                # Calls /cool route to validate cool
                Div(hx_target='this', hx_swap='outerHTML')(
                    Label(_for='cool')('Is this cool?'),
                    Input(type='text', name='cool', id='cool', hx_post='/cool', hx_indicator='#coolind')),
                # Calls /coolscale route to validate coolscale
                Div(hx_target='this', hx_swap='outerHTML')(
                    Label(_for='CoolScale')('How cool (scale of 1 - 10)?'),
                    Input(type='number', name='CoolScale', id='CoolScale', hx_post='/coolscale', hx_indicator='#coolscaleind')),
                # Submits the form which calls /submit route to validate whole form
                Div(id='submit-btn-container')(
                    Button(type='submit', id='submit-btn',)('Submit')))

### Field Validation Routing ###
# Validates the field and generates FastHTML with appropriate validation and template function

@app.post('/shape')
def check_shape(shape: list): return shapeInputTemplate(shape, validate_shape(shape))

@app.post('/cool')
def contact_cool(cool: str): return coolInputTemplate(cool, validate_cool(cool))

@app.post('/coolscale')
def contact_coolscale(CoolScale: int): return coolScaleInputTemplate(CoolScale, validate_coolscale(CoolScale))

@app.post('/submit')
def submit(shape: list, cool: str, CoolScale: int):
    # Validates all fields in the form
    errors = {'shape': validate_shape(shape),
             'cool': validate_cool(cool),
             'coolscale': validate_coolscale(CoolScale) }
    # Removes the None values from the errors dictionary (No errors)
    errors = {k: v for k, v in errors.items() if v is not None}
    # Return Button with error message if they exist
    return Div(id='submit-btn-container')(
        Button(type='submit', id='submit-btn', hx_post='/submit', hx_target='#submit-btn-container', hx_swap='outerHTML')('Submit'),
        *[Div(error, style='color: red;') for error in errors.values()])

########################
### Validation Logic ###
########################

def validate_shape(shape: list):
    # Check if email address is a valid one
    if not validate_single_field(InputStructure, "shape", shape):
        return "Please enter a valid shape"

def validate_cool(cool: str):
    if cool.lower() not in ["yes", "definitely"]: return "Yes or definitely are the only correct answers"

def validate_coolscale(CoolScale: int):
    if CoolScale < 1 or CoolScale > 10: return "Please enter a number between 1 and 10"

######################
### HTML Templates ###
######################

def inputTemplate(label, name, val, errorMsg=None, input_type='text'):
    # Generic template for replacing the input field and showing the validation message
    return Div(hx_target='this', hx_swap='outerHTML', cls=f"{errorMsg if errorMsg else 'Valid'}")(
               Label(label), # Creates label for the input field
               Input(name=name,type=input_type,value=f'{val}',hx_post=f'/{name.lower()}',hx_indicator=f'#{name.lower()}ind'), # Creates input field
               Div(f'{errorMsg}', style='color: red;') if errorMsg else None) # Creates red error message below if there is an error

def shapeInputTemplate(val, errorMsg=None): return inputTemplate('Shape', 'shape', val, errorMsg)

def coolInputTemplate(val, errorMsg=None): return inputTemplate('Is this cool?', 'cool', val, errorMsg)

def coolScaleInputTemplate(val, errorMsg=None): return inputTemplate('How cool (scale of 1 - 10)?', 'CoolScale', val, errorMsg, input_type='number')
