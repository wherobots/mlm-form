from fasthtml.common import *

from src.mlm_form.session import load_session
from src.mlm_form.styles import *
from src.mlm_form.templates import *
from src.mlm_form.validation import *
from src.mlm_form.make_item import (
    construct_ml_model_properties,
    construct_assets,
    create_pystac_item,
)
from stac_model.runtime import AcceleratorEnum
from datetime import datetime
import pystac
import copy

app, rt = fast_app(hdrs=(picolink))

app_title = "Machine Learning Model Metadata Form"


@app.get("/")
def homepage(session):
    session = load_session(session)
    return (
        Title(app_title),
        Main(
            Header(
                title_bar(app_title, session),
                tab_bar(selected="/"),
                Img(
                    src="https://static.scarf.sh/a.png?x-pxid=0a803684-62c5-4f72-8971-01626aa82623",
                    referrerpolicy="no-referrer-when-downgrade",
                ),
            ),
            Div(
                session_form(session, submitOnLoad=True),
                outputTemplate(),
                id="page",
                style="display: flex; flex-direction: row; overflow: auto;",
            ),
            style=main_element_style,
        ),
    )


@app.post("/clear_form")
def clear_form(session):
    session = load_session(session)
    session.clear()
    return session_form(session), button_bar(session)


def form_format_to_stac_format_input(d):
    # TODO for some reason the enum and checkbox template don't set default empty values
    d["mlm_input_norm_type"] = d.get("mlm_input_norm_type")
    d["mlm_input_resize_type"] = d.get("mlm_input_resize_type")
    d["mlm_input_data_type"] = d.get("mlm_input_data_type")
    d["mlm_output_data_type"] = d.get("mlm_output_data_type")
    d["accelerator"] = d.get("accelerator")
    d["accelerator_constrained"] = d.get("accelerator_constrained")
    # this handles empty strings on submit and the fact that we have to manually collate list values
    d["mlm_input_shape"] = [
        int(d.pop(f"mlm_input_shape_{i + 1}"))
        if d.get(f"mlm_input_shape_{i + 1}")
        else d.pop(f"mlm_input_shape_{i + 1}")
        for i in range(4)
    ]
    d["mlm_output_shape"] = [
        int(d.pop(f"mlm_output_shape_{i + 1}"))
        if d.get(f"mlm_output_shape_{i + 1}")
        else d.pop(f"mlm_output_shape_{i + 1}")
        for i in range(4)
    ]
    # TODO need to raise error to user if dim values aren't unique.
    # need to raise and prettify any error from pystac validation
    d["mlm_input_dim_order"] = [
        d.pop(f"mlm_input_dim_order_{i + 1}")
        if d.get(f"mlm_input_dim_order_{i + 1}")
        else d.pop(f"mlm_input_dim_order_{i + 1}")
        for i in range(4)
    ]
    d["mlm_output_dim_order"] = [
        d.pop(f"mlm_output_dim_order_{i + 1}")
        if d.get(f"mlm_output_dim_order_{i + 1}")
        else d.pop(f"mlm_output_dim_order_{i + 1}")
        for i in range(4)
    ]
    d["mlm_output_classes"] = [
        item.strip() for item in d.get("mlm_output_classes", "").split(",")
    ]
    d["mlm_input_bands"] = [
        item.strip() for item in d.get("mlm_input_bands", "").split(",")
    ]
    d["mlm_input_mean"] = [
        float(item.strip()) if item != "" else [""]
        for item in d.get("mlm_input_mean", "").split(",")
    ]
    d["mlm_input_std"] = [
        float(item.strip()) if item != "" else [""]
        for item in d.get("mlm_input_std", "").split(",")
    ]
    d["mlm_input_min"] = [
        float(item.strip()) if item != "" else [""]
        for item in d.get("mlm_input_min", "").split(",")
    ]
    d["mlm_input_max"] = [
        float(item.strip()) if item != "" else [""]
        for item in d.get("mlm_input_max", "").split(",")
    ]
    # from the fasthtml discord https://discordapp.com/channels/689892369998676007/1247700012952191049/1273789690691981412
    # this might change past version 0.4.4 it seems pretty hacky
    d["tasks"] = [task for task in tasks if d.pop(task, None)]
    # d['mlm:output_tasks'] = [task for task in tasks if d.pop(task, None)]
    d["accelerator_count"] = int(d.get("accelerator_count", 1))
    d["memory_size"] = int(d.get("memory_size", 1))
    d["total_parameters"] = int(d.get("total_parameters", 1))
    d["batch_size_suggestion"] = int(d.get("batch_size_suggestion", 1))
    # remove empty strs
    d["mlm_output_shape"] = [item for item in d["mlm_output_shape"] if item]
    d["mlm_output_dim_order"] = [item for item in d["mlm_output_dim_order"] if item]
    d["mlm_input_shape"] = [item for item in d["mlm_input_shape"] if item]
    d["mlm_input_dim_order"] = [item for item in d["mlm_input_dim_order"] if item]
    return d


@app.post("/submit")
def submit(session, d: dict):
    session = load_session(session)
    session.setdefault("stac_format_d", {})
    session.setdefault("form_format_d", {})
    session["form_format_d"].update(copy.deepcopy(d))
    d = form_format_to_stac_format_input(d)
    session["stac_format_d"].update(d)
    ml_model_metadata = construct_ml_model_properties(d)
    assets = construct_assets(session["stac_format_d"].get("assets"))
    item = create_pystac_item(ml_model_metadata, assets)
    return prettyJsonTemplate(item), button_bar(session)


roles = [role for role in model_asset_roles if role not in model_asset_implicit_roles]


# helper function to render out the session form
# because of the `hx_swap_oob`, this snippet can be returned by any handler and will update the form
# see https://htmx.org/examples/update-other-content/#oob
#
# `submitOnLoad` should be set to true for the initial page load so that the form will
# auto-submit to populate the results if there is saved state in the session
def session_form(session, submitOnLoad=False):
    session.setdefault("stac_format_d", {})
    session.setdefault("form_format_d", {})
    result = session.get("form_format_d", {})
    trigger = (
        "input delay:200ms, load" if submitOnLoad and result else "input delay:200ms"
    )
    session_form = Form(
        hx_post="/submit",
        hx_target="#result",
        hx_trigger=trigger,
        id="session_form",
        hx_swap_oob="#session_form",
        style=form_style,
    )(
        P(
            "The ",
            A(
                "STAC Machine Learning Model ",
                href="https://github.com/stac-extensions/mlm/blob/main/README.md",
                target="_blank",
                rel="noopener noreferrer",
                cls="border-b-2 border-b-black/30 hover:border-b-black/80",
            ),
            "(MLM) metadata specification makes it easy to describe the metadata needed to reproduce model inference and enable search and discovery. The MLM makes it easier to share, reuse, and run models "
            "on inference providers that support it, such as ",
            A(
                "Wherobots",
                href="https://wherobots.com/wherobotsai-for-raster-inference/",
                target="_blank",
                rel="noopener noreferrer",
                cls="border-b-2 border-b-black/30 hover:border-b-black/80",
            ),
            ", and open source ml frameworks.\n\n"
            "Please complete all required fields below and in the Asset Form prior to copying or downloading the JSON result. Downloaded JSONs will be stored in your download directory and named based on Model Name field. ",
            "For more information on the specification, refer to the ",
            A(
                "MLM documentation",
                href="https://github.com/stac-extensions/mlm/blob/main/README.md",
                target="_blank",
                rel="noopener noreferrer",
                cls="border-b-2 border-b-black/30 hover:border-b-black/80",
            ),
            ".",
        ),
        inputTemplate(
            label="Model Name",
            name="model_name",
            placeholder="A unique identifier for your model",
            val="",
            input_type="text",
        ),
        inputTemplate(
            label="Architecture",
            name="architecture",
            placeholder="A recognizable name for the model architecture",
            val="",
            input_type="text",
        ),
        selectCheckboxTemplate(
            label="Tasks", options=tasks, name="tasks", canValidateInline=False
        ),
        inputTemplate(
            label="Framework",
            name="framework",
            placeholder='The name of the model framework e.g. "Pytorch"',
            val="",
            input_type="text",
        ),
        inputTemplate(
            label="Framework Version",
            name="framework_version",
            placeholder="A version identifier e.g. 2.3.0",
            val="",
            input_type="text",
        ),
        inputTemplate(
            label="Memory Size", name="memory_size", val=1, input_type="number"
        ),
        inputTemplate(
            label="Total Parameters",
            name="total_parameters",
            val=1,
            input_type="number",
        ),
        trueFalseRadioTemplate(
            label="Is it pretrained for one or more tasks and one or more data domains?",
            name="pretrained",
        ),
        inputTemplate(
            label="If pretrained, what dataset was used for pretraining?",
            name="pretrained_source",
            placeholder="A recognizable name for the dataset",
            val="",
            input_type="text",
        ),
        inputTemplate(
            label="Suggested batch size for inference",
            name="batch_size_suggestion",
            val=1,
            input_type="number",
        ),
        selectEnumTemplate(
            label="Accelerator",
            options=[task.value for task in AcceleratorEnum],
            name="accelerator",
            error_msg=None,
            canValidateInline=False,
        ),
        trueFalseRadioTemplate(
            label="Accelerator constrained", name="accelerator_constrained"
        ),
        inputTemplate(
            label="Accelerator Summary",
            name="accelerator_summary",
            placeholder='A description for the accelerator, e.g. "Nvidia A100"',
            val="",
            input_type="text",
        ),
        inputTemplate(
            label="Accelerator Count",
            name="accelerator_count",
            val=1,
            input_type="number",
        ),
        modelInputTemplate(label="MLM Input", name="mlm_input"),
        modelOutputTemplate(label="MLM Output", name="mlm_output"),
    )
    fill_form(session_form, result)
    return session_form


def session_asset_form(session, submitOnLoad=False):
    session.setdefault("stac_format_d", {})
    session.setdefault("form_format_d", {})
    session["stac_format_d"].setdefault("assets", {})
    session["form_format_d"].setdefault("assets", {})
    # TODO decide whether to show just asset section or full json on asset page on load and edit
    # result = session['form_format_d'].get('assets', {})
    trigger = (
        "input delay:200ms, load"
        if submitOnLoad and session.get("stac_format_d")
        else "input delay:200ms"
    )
    session_asset_form = Form(
        hx_post="/submit_asset",
        hx_target="#result",
        hx_trigger=trigger,
        id="session_asset_form",
        hx_swap_oob="#session_asset_form",
        style=form_style,
    )(
        P(
            "Please complete all fields below to describe the machine learning model asset. ",
            "The artifact type field follows the convention described in the ",
            A(
                "MLM best practices document",
                href="https://github.com/stac-extensions/mlm/blob/main/best-practices.md#framework-specific-artifact-types",
            ),
            ". A model artifact is referenced by the framework specific method that created it.",
        ),
        inputTemplate(
            label="Title",
            name="title",
            val="",
            input_type="text",
            canValidateInline=False,
        ),
        inputTemplate(
            label="URI", name="href", val="", input_type="text", canValidateInline=False
        ),
        inputTemplate(
            label="Media Type",
            name="media_type",
            val="",
            input_type="text",
            canValidateInline=False,
        ),
        selectCheckboxTemplate(
            label="Roles", options=roles, name="roles", canValidateInline=False
        ),
        selectEnumTemplate(
            label="Artifact Type",
            options=model_asset_artifact_types,
            name="mlm:artifact_type",
            canValidateInline=False,
        ),
    )
    fill_form(session_asset_form, session["form_format_d"].get("assets", {}))
    return session_asset_form


@app.get("/asset")
def asset_homepage(session):
    session = load_session(session)
    return (
        Title(app_title),
        Main(
            Header(title_bar(app_title, session), tab_bar(selected="/asset")),
            Div(
                session_asset_form(session, submitOnLoad=True),
                outputTemplate(),
                style="display: flex; flex-direction: row; overflow: auto;",
            ),
            style=main_element_style,
        ),
    )


@app.post("/submit_asset")
def submit_asset(session, d: dict):
    session = load_session(session)
    session["form_format_d"]["assets"].update(copy.deepcopy(d))
    d["roles"] = model_asset_implicit_roles + [
        role for role in roles if d.pop(role, None)
    ]
    d["type"] = d.pop("media_type")
    session["stac_format_d"]["assets"].update(copy.deepcopy(d))
    # pystac doesn't directly support validating an asset, so put the asset inside a
    # dummy item and run the validation on that
    dummy_item = pystac.Item(
        id="item",
        geometry={
            "type": "Polygon",
            "coordinates": [
                [
                    [-101.0, 40.0],
                    [-101.0, 41.0],
                    [-100.0, 41.0],
                    [-100.0, 40.0],
                    [-101.0, 40.0],
                ]
            ],
        },
        bbox=[-101.0, 40.0, -100.0, 41.0],
        datetime=datetime.utcnow(),
        properties={},
    )
    dummy_item.assets["model"] = pystac.Asset.from_dict(d)

    try:
        validation_result = pystac.validation.validate(dummy_item)
    except pystac.errors.STACValidationError as e:
        error_message = str(e)
        if "'href'" in error_message and "non-empty" in error_message:
            error_message = "The 'URI' field must be non-empty."
        else:
            error_message = f"STACValidationError: {error_message}".replace(
                "\\n", "<br>"
            )
        return error_template(error_message), prettyJsonTemplate(
            dummy_item.assets["model"].to_dict()
        )
    return prettyJsonTemplate(dummy_item.assets["model"].to_dict())


serve()
