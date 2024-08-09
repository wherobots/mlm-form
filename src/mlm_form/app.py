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

    # input_struct = InputStructure(
    #     shape=[-1, 13, 64, 64],
    #     dim_order=["batch", "channel", "height", "width"],
    #     data_type="float32",
    # )
    # band_names = [
    #     "B01",
    #     "B02",
    #     "B03",
    #     "B04",
    #     "B05",
    #     "B06",
    #     "B07",
    #     "B08",
    #     "B8A",
    #     "B09",
    #     "B10",
    #     "B11",
    #     "B12",
    # ]
    # stats_mean = [
    #     1354.40546513,
    #     1118.24399958,
    #     1042.92983953,
    #     947.62620298,
    #     1199.47283961,
    #     1999.79090914,
    #     2369.22292565,
    #     2296.82608323,
    #     732.08340178,
    #     12.11327804,
    #     1819.01027855,
    #     1118.92391149,
    #     2594.14080798,
    # ]
    # stats_stddev = [
    #     245.71762908,
    #     333.00778264,
    #     395.09249139,
    #     593.75055589,
    #     566.4170017,
    #     861.18399006,
    #     1086.63139075,
    #     1117.98170791,
    #     404.91978886,
    #     4.77584468,
    #     1002.58768311,
    #     761.30323499,
    #     1231.58581042,
    # ]
    # stats = [
    #     MLMStatistic(
    #         mean=mean,
    #         stddev=stddev,
    #     )
    #     for mean, stddev in zip(stats_mean, stats_stddev)
    # ]
    # model_input = ModelInput(
    #     name="13 Band Sentinel-2 Batch",
    #     bands=band_names,
    #     input=input_struct,
    #     norm_by_channel=True,
    #     norm_type="z-score",
    #     resize_type=None,
    #     statistics=stats,
    #     pre_processing_function=ProcessingExpression(
    #         format="python",
    #         expression="torchgeo.datamodules.eurosat.EuroSATDataModule.collate_fn",
    #     ),  # noqa: E501
    # )
    # result_struct = ModelResult(
    #     shape=[-1, 10],
    #     dim_order=["batch", "class"],
    #     data_type="float32",
    # )
    # class_map = {
    #     "Annual Crop": 0,
    #     "Forest": 1,
    #     "Herbaceous Vegetation": 2,
    #     "Highway": 3,
    #     "Industrial Buildings": 4,
    #     "Pasture": 5,
    #     "Permanent Crop": 6,
    #     "Residential Buildings": 7,
    #     "River": 8,
    #     "SeaLake": 9,
    # }
    # class_objects = [
    #     MLMClassification(
    #         value=class_value,
    #         name=class_name,
    #     )
    #     for class_name, class_value in class_map.items()
    # ]
    # model_output = ModelOutput(
    #     name="classification",
    #     tasks={"classification"},
    #     classes=class_objects,
    #     result=result_struct,
    #     post_processing_function=None,
    # )
    # assets = {
    #     "model": pystac.Asset(
    #         title="Pytorch weights checkpoint",
    #         description=(
    #             "A Resnet-18 classification model trained on normalized Sentinel-2 "
    #             "imagery with Eurosat landcover labels with torchgeo."
    #         ),
    #         href="https://huggingface.co/torchgeo/resnet18_sentinel2_all_moco/resolve/main/resnet18_sentinel2_all_moco-59bfdff9.pth",
    #         media_type="application/octet-stream; application=pytorch",
    #         roles=[
    #             "mlm:model",
    #             "mlm:weights",
    #             "data",
    #         ],
    #     ),
    #     "source_code": pystac.Asset(
    #         title="Model implementation.",
    #         description="Source code to run the model.",
    #         href="https://github.com/microsoft/torchgeo/blob/61efd2e2c4df7ebe3bd03002ebbaeaa3cfe9885a/torchgeo/models/resnet.py#L207",
    #         media_type="text/x-python",
    #         roles=[
    #             "mlm:model",
    #             "code",
    #         ],
    #     ),
    # }

    # ml_model_size = 43000000
    # ml_model_meta = MLModelProperties(
    #     name="Resnet-18 Sentinel-2 ALL MOCO",
    #     architecture="ResNet-18",
    #     tasks={"classification"},
    #     framework="pytorch",
    #     framework_version="2.1.2+cu121",
    #     accelerator="cuda",
    #     accelerator_constrained=False,
    #     accelerator_summary="Unknown",
    #     file_size=ml_model_size,
    #     memory_size=1,
    #     pretrained=True,
    #     pretrained_source="EuroSat Sentinel-2",
    #     total_parameters=11_700_000,
    #     input=[model_input],
    #     output=[model_output],
    # )
    # input_struct = InputStructure(
    #     shape=[-1, 13, 64, 64],
    #     dim_order=["batch", "channel", "height", "width"],
    #     data_type="float32",
    # )

def InputStructureC(shp_list="[-1, 3, 256, 256]",
                    dim_order_list=["batch", "channel", "height", "width"],
                    data_type="float32"):
    if InputStructure(
        shape=eval(shp_list),
        dim_order=dim_order_list,
        data_type= data_type,
    ):
        return [Input(type="text", id="shape", placeholder="Shape"),
               Input(type="text", id="dim_order", placeholder="Dim Order"),
               Input(type="text", id="data_type", placeholder="Data Type")]

@rt('/')
def get():
    return Titled('ML Model Metadata Form',
        Form(hx_post="/submit", hx_target="#result", hx_trigger="input delay:200ms")(
            Select(Option("One"), Option("Two"), id="select"),
            Input(type="text", id="name", placeholder="Name"),
            Input(type="text", id="email", placeholder="Email")),
            *InputStructureC(),
        Div(id="result")
    )

@rt('/submit')
def post(d:dict): return d