from fasthtml.common import *

import pystac
import shapely
from dateutil.parser import parse as parse_dt
from pystac.extensions.file import FileExtension

from stac_model.base import ProcessingExpression
from stac_model.input import InputStructure, MLMStatistic, ModelInput
from stac_model.output import MLMClassification, ModelOutput, ModelResult
from stac_model.schema import ItemMLModelExtension, MLModelExtension, MLModelProperties

app, rt = fast_app(live=True, debug=True)

def InputStructureComponents():
    shape_inputs = [Input(type="number", id="shape", step="any",
                          min="0", max="100", placeholder="Enter a float value")
                          for s in list(range(4))]
    return [*shape_inputs,
            Input(type="text", id="dim_order", placeholder="Dim Order"),
            Input(type="text", id="data_type", placeholder="Data Type")]

@rt('/')
def get():
    return Titled('ML Model Metadata Form',
        Form(hx_post="/submit", hx_target="#result", hx_trigger="input delay:200ms")(
            *InputStructureComponents(),
            ),
        Div(id="result")
    )

@rt('/submit')
def post(d:dict):
    print(d)
    d['shape'] = [int(s) for s in d['shape']]
    d['dim_order'] = d['dim_order'].split(',')
    d['data_type'] = d['data_type']
    assert InputStructure(shape=d['shape'], dim_order=d['dim_order'], data_type=d['data_type'])
    return d