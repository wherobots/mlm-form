from typing import cast, Dict, Any

import pystac
import shapely
from dateutil.parser import parse as parse_dt
from pystac.extensions.file import FileExtension

from stac_model.base import ProcessingExpression
from stac_model.input import InputStructure, MLMStatistic, ModelInput
from stac_model.output import MLMClassification, ModelOutput, ModelResult
from stac_model.schema import ItemMLModelExtension, MLModelExtension, MLModelProperties

# Assuming the necessary Pydantic models are imported or defined above

def construct_ml_model_properties(d: Dict[str, Any]) -> MLModelProperties:
    """Creates the pydantic model for model properties.

    This takes the payload from all the form inputs which is flat and
    inserts the data into the pydantic models so that we generate JSON with
    the correct structure. It duplicates work done in the inline validation
    but not sure how to avoid that.

    Args:
        d (Dict[str, Any]): The payload from the form with all item property info.

    Returns:
        MLModelProperties: The pydantic model for MLM specific properties.
    """
    # Construct InputStructure
    input_struct = InputStructure(
        shape=d['input_shape'],
        dim_order=d['input_dim_order'],
        data_type=d['input_data_type'],
    )

    # Construct MLMStatistic
    stats = [
        MLMStatistic(
            mean=mean,
            stddev=stddev,
        )
        for mean, stddev in zip(d['stats_mean'], d['stats_stddev'])
    ]

    # Construct ModelInput
    model_input = ModelInput(
        name=d['input_name'],
        bands=d['band_names'],
        input=input_struct,
        norm_by_channel=d['norm_by_channel'],
        norm_type=d['norm_type'],
        resize_type=d['resize_type'],
        statistics=stats,
        pre_processing_function=ProcessingExpression(
            format=d['pre_processing_format'],
            expression=d['pre_processing_expression'],
        ),
    )

    # Construct ModelResult
    result_struct = ModelResult(
        shape=d['result_shape'],
        dim_order=d['result_dim_order'],
        data_type=d['result_data_type'],
    )

    # Construct MLMClassification
    class_objects = [
        MLMClassification(
            value=class_value,
            name=class_name,
        )
        for class_name, class_value in d['class_map'].items()
    ]

    # Construct ModelOutput
    model_output = ModelOutput(
        name=d['output_name'],
        tasks=d['tasks'],
        classes=class_objects,
        result=result_struct,
        post_processing_function=None,
    )

    # Construct MLModelProperties
    ml_model_meta = MLModelProperties(
        name=d['model_name'],
        architecture=d['architecture'],
        tasks=d['tasks'],
        framework=d['framework'],
        framework_version=d['framework_version'],
        accelerator=d['accelerator'],
        accelerator_constrained=d['accelerator_constrained'],
        accelerator_summary=d['accelerator_summary'],
        file_size=d['file_size'],
        memory_size=d['memory_size'],
        pretrained=d['pretrained'],
        pretrained_source=d['pretrained_source'],
        total_parameters=d['total_parameters'],
        input=[model_input],
        output=[model_output],
    )

    return ml_model_meta

def create_pystac_item(ml_model_meta: MLModelProperties, assets: Dict[str, pystac.Asset]) -> pystac.Item:
    """Creates stac item metadata and extends it with MLM specific properties.

    This includes asset level metadata. TODO is including asset metadata in the pystac item. Not sure
    how to keep state from multiple form pages and post form input to
    multiple routes.

    Args:
        ml_model_meta (MLModelProperties): _description_
        assets (Dict[str, pystac.Asset]): _description_

    Returns:
        pystac.Item: _description_
    """
    start_datetime_str = "1900-01-01"
    end_datetime_str = "9999-01-01"
    start_datetime = parse_dt(start_datetime_str).isoformat() + "Z"
    end_datetime = parse_dt(end_datetime_str).isoformat() + "Z"
    bbox = [
        -7.882190080512502,
        37.13739173208318,
        27.911651652899923,
        58.21798141355221,
    ]
    geometry = shapely.geometry.Polygon.from_bounds(*bbox).__geo_interface__
    item_name = "item_basic"
    col_name = "ml-model-examples"
    item = pystac.Item(
        id=item_name,
        collection=col_name,
        geometry=geometry,
        bbox=bbox,
        datetime=None,
        properties={
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "description": "Sourced from torchgeo python library, identifier is ResNet18_Weights.SENTINEL2_ALL_MOCO",
        },
        assets=assets,
    )

    item.add_link(
        pystac.Link(
            target="https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a",
            rel=pystac.RelType.DERIVED_FROM,
            media_type=pystac.MediaType.JSON,
        )
    )

    col = pystac.Collection(
        id=col_name,
        title="Machine Learning Model examples",
        description="Collection of items contained in the Machine Learning Model examples.",
        extent=pystac.Extent(
            temporal=pystac.TemporalExtent([[parse_dt(start_datetime), parse_dt(end_datetime)]]),
            spatial=pystac.SpatialExtent([bbox]),
        ),
    )
    col.set_self_href("./examples/collection.json")
    col.add_item(item)
    item.set_self_href(f"./examples/{item_name}.json")

    model_asset = cast(
        FileExtension[pystac.Asset],
        pystac.extensions.file.FileExtension.ext(assets["model"], add_if_missing=True),
    )
    model_asset.apply(size=ml_model_meta.file_size)

    item_mlm = MLModelExtension.ext(item, add_if_missing=True)
    item_mlm.apply(ml_model_meta.model_dump(by_alias=True, exclude_unset=True, exclude_defaults=True))
    return item_mlm
