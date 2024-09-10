from typing import cast, Dict, Any

import pystac
import shapely
from dateutil.parser import parse as parse_dt
from pystac.extensions.file import FileExtension

from stac_model.input import InputStructure, MLMStatistic, ModelInput
from stac_model.output import MLMClassification, ModelOutput, ModelResult
from stac_model.schema import ItemMLModelExtension, MLModelExtension, MLModelProperties, T

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
    input_struct = InputStructure.model_construct(
        shape=d['mlm_input_shape'],
        dim_order=d['mlm_input_dim_order'],
        data_type=d['mlm_input_data_type'],
    )

    # Construct MLMStatistic
    stats = [
        MLMStatistic.model_construct(
            mean=mean,
            stddev=stddev,
        )
        for mean, stddev in zip(d['mlm_input_mean'], d['mlm_input_std'])
    ]
    print(d.keys())
    # Construct ModelInput
    model_input = ModelInput.model_construct(
        name=d['mlm_input_name'],
        bands=d['mlm_input_bands'],
        input=input_struct,
        norm_by_channel=d['mlm_input_norm_by_channel'],
        norm_type=d['mlm_input_norm_type'],
        resize_type=d['mlm_input_resize_type'],
        statistics=stats,
        # TODO though not sure this makes sense in a form filler.
        # pre_processing_function=ProcessingExpression(
        #     format=d['mlm_input_pre_processing_format'],
        #     expression=d['mlm_input_pre_processing_expression'],)
    )

    # Construct ModelResult
    result_struct = ModelResult.model_construct(
        shape=d['mlm_output_shape'],
        dim_order=d['mlm_output_dim_order'],
        data_type=d['mlm_output_data_type'],
    )

    # Construct MLMClassification
    if d['mlm_output_classes'] == ['']:
        class_objects = [
        MLMClassification(
            value=class_value+1,
            name=class_name,
        )
        # TODO the user needs to determine the class name / value mapping
        for class_value, class_name in enumerate(["example_class1", "example_class2", "example_class3"])
    ]
    else:
        class_objects = [
            MLMClassification(
                value=class_value+1,
                name=class_name,
                description=""
            )
            # TODO the user needs to determine the class name / value mapping
            for class_value, class_name in enumerate(d['mlm_output_classes'])
        ]

    # Construct ModelOutput
    model_output = ModelOutput.model_construct(
        name=d['mlm_output_name'],
        tasks=d['tasks'],
        classes=class_objects,
        result=result_struct,
        post_processing_function=None,
    )

    # Construct MLModelProperties
    ml_model_meta = MLModelProperties.model_construct(
        name=d['model_name'],
        architecture=d['architecture'],
        tasks=d['tasks'],
        framework=d['framework'],
        framework_version=d['framework_version'],
        accelerator=d['accelerator'],
        accelerator_constrained=bool(d['accelerator_constrained']),
        accelerator_summary=d['accelerator_summary'],
        memory_size=d['memory_size'],
        pretrained=d['pretrained'],
        pretrained_source=d['pretrained_source'],
        total_parameters=d['total_parameters'],
        input=[model_input],
        output=[model_output],
    )

    return ml_model_meta

def construct_assets(d: Dict[str, Any]) -> Dict[str, pystac.Asset]:
    """Creates the assets for the STAC item.

    This function takes the payload from the form input and constructs the
    assets for the STAC item. The assets are the model file and any other
    files that are needed to run the model.

    Args:
        d (Dict[str, Any]): The payload from the form with all item property info.

    Returns:
        Dict[str, pystac.Asset]: The assets for the STAC item.
    """
    assets = {}
    required_keys = ['title', 'model_file', 'type', 'roles', 'mlm:artifact_type']
    if d and all(key in d and d[key] is not None for key in required_keys):
        # TODO correct mlm_ > mlm:
        model_file = pystac.Asset(
            title=d.get('title'),
            href=d.get('model_file'),
            media_type=d.get('type'),
            roles=d.get('roles'),
            extra_fields={"mlm_artifact_type": d.get('mlm:artifact_type'),}
        )
        assets["model"] = model_file
    return assets

def create_pystac_item(ml_model_meta: MLModelProperties, assets: Dict[str, pystac.Asset], self_href="./item.json") -> pystac.Item:
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
    # TODO make the time and geometry components configurable
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
    item_name = "item"
    # TODO if the scope of the form evolves to capture collections
    # col_name = "ml-model-examples"
    item = pystac.Item(
        id=item_name,
        # collection=col_name,
        geometry=geometry,
        bbox=bbox,
        datetime=None,
        properties={
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "description": "An Item with Machine Learning Model Extension metadata.",
        },
        assets=assets,
    )
    # TODO we need an interface for users to select from a list of data collections. Maybe based on STAC Index?
    # For now, hard default to sentinel-2.
    item.add_link(
        pystac.Link(
            target="https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a",
            rel=pystac.RelType.DERIVED_FROM,
            media_type=pystac.MediaType.JSON,
        )
    )
    # TODO have this be user supplied? based on where they store the JSON
    item.set_self_href(self_href)

    # TODO assets is unset until asset form is filled so we need to handle it
    if assets:
        model_asset = cast(
            FileExtension[pystac.Asset],
            pystac.extensions.file.FileExtension.ext(assets["model"], add_if_missing=True),
        )

    item_mlm = MLModelExtension.ext(item, add_if_missing=True)
    # TODO validation issues because of none fields and can't bypass validation on whole model level
    item_d = item.to_dict()
    properties = ml_model_meta.model_dump(by_alias=True, exclude_unset=True, exclude_defaults=True)
    #item_mlm.apply(ml_model_meta.model_dump(by_alias=True, exclude_unset=True, exclude_defaults=True))
    item_d['properties'].update(properties)
    return item_d

import json
from typing import Union
class NoValMLModelExtension(MLModelExtension[T]):
    def apply(
        self,
        properties: Union[MLModelProperties, dict[str, Any]],
    ) -> None:
        """
        Applies Machine Learning Model Extension properties to the extended :mod:`~pystac` object.
        """
        if isinstance(properties, dict):
            properties = MLModelProperties.model_construct(**properties)
        data_json = json.loads(properties.model_dump_json(by_alias=True))
        for prop, val in data_json.items():
            self._set_property(prop, val)