from fasthtml.common import *
import json
import os

from .styles import *
from .validation import *
from .make_item import (
    construct_ml_model_properties,
    construct_assets,
    create_pystac_item,
)
from stac_model.input import ResizeType
from typing import get_args
from stac_model.base import TaskEnum


resize_type_values = [value for value in get_args(get_args(ResizeType)[0])]
tasks = [task.value for task in TaskEnum]


######################
### HTML Templates ###
######################
def inputTemplate(
    label,
    name,
    val,
    placeholder=None,
    error_msg=None,
    input_type="text",
    canValidateInline=False,
):
    return Div(
        hx_target="this",
        hx_swap="outerHTML",
        cls=f"{error_msg if error_msg else 'Valid'}",
        style=control_container_style,
    )(
        labelDecoratorTemplate(Label(label), name in model_required_keys),
        Input(
            id=name,
            name=name,
            type=input_type,
            placeholder=placeholder,
            value=f"{val}",
            hx_post=f"/{name.lower()}" if canValidateInline else None,
            style=text_input_style,
        ),
        Div(f"{error_msg}", style="color: red;") if error_msg else None,
    )


def inputListTemplate(
    label,
    name,
    placeholder=None,
    values=[None, None, None, None],
    error_msg=None,
    input_type="number",
    canValidateInline=False,
):
    return Div(
        hx_target="this",
        hx_swap="outerHTML",
        cls=f"{error_msg if error_msg else 'Valid'}",
        style=control_container_style,
    )(
        labelDecoratorTemplate(Label(label), name in model_required_keys),
        Div(
            style="display: flex; gap: 20px; justify-content: flex-start; width: 100%; max-width: 600px;"
        )(
            *[
                Input(
                    name=f"{name.lower()}_{i + 1}",
                    id=f"{name.lower()}_{i + 1}",
                    placeholder=placeholder,
                    type=input_type,
                    value=val,
                    style="width: 160px;",
                    hx_post=f"/{name.lower()}" if canValidateInline else None,
                )
                for i, val in enumerate(values)
            ]
        ),
        Div(f"{error_msg}", style="color: red;") if error_msg else None,
    )


def mk_opts(nm, cs):
    return (
        Option(f"-- select {nm} --", disabled=True, selected=True, value=""),
        *map(lambda c: Option(c, value=c), cs),
    )


def selectEnumTemplate(
    label, options, name, hx_target=None, error_msg=None, canValidateInline=False
):
    return Div(
        hx_target="this",
        hx_swap="outerHTML",
        cls=f"{error_msg if error_msg else 'Valid'}",
        style=control_container_style,
    )(
        labelDecoratorTemplate(Label(label), name in model_required_keys),
        Select(
            *mk_opts(name, options),
            name=name,
            id=name,
            hx_post=f"/{name.lower()}" if canValidateInline else None,
            hx_target=hx_target,
            style=select_input_style,
        ),
        Div(f"{error_msg}", style="color: red;") if error_msg else None,
    )


def mk_checkbox(options):
    return Div(style=control_container_style)(
        *[
            Div(CheckboxX(id=option, label=option), style="width: 100%;")
            for option in options
        ]
    )


def selectCheckboxTemplate(
    label, options, name, error_msg=None, canValidateInline=False
):
    return Div(
        hx_target="this",
        hx_swap="outerHTML",
        cls=f"{error_msg if error_msg else 'Valid'}",
        style=control_container_style,
    )(
        labelDecoratorTemplate(Label(label), name in model_required_keys),
        Group(
            mk_checkbox(options),
            name=name,
            id=name,
            hx_post=f"/{name.lower()}" if canValidateInline else None,
        ),
        Div(f"{error_msg}", style="color: red;") if error_msg else None,
    )


def trueFalseRadioTemplate(label, name, error_msg=None):
    return Div(
        labelDecoratorTemplate(Label(label), name in model_required_keys),
        Div(
            Input(type="radio", name=f"{name}", id=f"{name}_true", value="true"),
            Label("True", for_=f"{name}_true"),
            Input(type="radio", name=f"{name}", id=f"{name}_false", value="false"),
            Label("False", for_=f"{name}_false"),
            style="display: flex; flex-direction: row; align-items: center;",
        ),
        Div(f"{error_msg}", style="color: red;") if error_msg else None,
        style=f"{control_container_style} margin-bottom: 15px;",
    )


def modelInputTemplate(label, name, error_msg=None):
    return Div(
        labelDecoratorTemplate(
            H4(label, style="margin-left: -30px;"), name in model_required_keys
        ),
        inputTemplate(
            label="Name",
            name=f"{name}_name",
            val="",
            placeholder="A descriptive name for the model input",
            input_type="text",
        ),
        inputTemplate(
            label="Bands (enter a single comma separated list of values)",
            name=f"{name}_bands",
            val="",
            placeholder="""e.g. B01,B02,B03,B04,B05,B06,B07,B08,B8A,B09,B10,B11,B12""",
            input_type="text",
        ),
        inputListTemplate(
            label="Input Dimension Sizes",
            placeholder="Enter Value",
            name=f"{name}_shape",
            error_msg=None,
            input_type="number",
        ),
        inputListTemplate(
            label="Input Dimension Labels",
            placeholder="Enter Text Label",
            name=f"{name}_dim_order",
            error_msg=None,
            input_type="text",
        ),
        selectEnumTemplate(
            "Input Data Type",
            datatypes,
            f"{name}_data_type",
            error_msg=None,
            canValidateInline=False,
        ),
        Div(f"{error_msg}", style="color: red;") if error_msg else None,
        style=f"{control_container_style} margin-left: 30px;",
    )


def mk_input(**kw):
    return Input(id="new-title", name="title", placeholder="New Todo", **kw)


def modelOutputTemplate(label, name, error_msg=None):
    return Div(
        labelDecoratorTemplate(
            H4(label, style="margin-left: -30px;"), name in model_required_keys
        ),
        inputTemplate(
            label="Name",
            name=f"{name}_name",
            val="",
            placeholder="A descriptive name of the model output content",
            input_type="text",
        ),
        # TODO disabling this because we only work with models that accept single outputs for now but
        # this should be flipped on and made working in the future
        # selectCheckboxTemplate(label="Tasks", options=tasks, name=f"{name}_tasks", canValidateInline=False),
        inputListTemplate(
            label="Output Dimension Sizes",
            name=f"{name}_shape",
            placeholder="Enter Value",
            error_msg=None,
            input_type="number",
        ),
        # TODO possibly overly restrictive schema, this can't contain numeric characters
        inputListTemplate(
            label="Output Dimension Labels",
            name=f"{name}_dim_order",
            placeholder="Enter Text Label",
            error_msg=None,
            input_type="text",
        ),
        selectEnumTemplate(
            "Output Data Type",
            datatypes,
            f"{name}_data_type",
            error_msg=None,
            canValidateInline=False,
        ),
        # TODO this should be made dynamic so that users can enter an N length list of classes similar to
        # https://gallery.fastht.ml/start_simple/sqlite_todo/code
        inputTemplate(
            label="Classes (enter a single comma separated list of classes)",
            name=f"{name}_classes",
            val="",
            placeholder=''' e.g. "Annual Crop, Forest, Herbaceous Vegetation, Highway, Industrial Buildings, Pasture, Permanent Crop, Residential Buildings, River, SeaLake"''',
            input_type="text",
        ),
        Div(f"{error_msg}", style="color: red;") if error_msg else None,
        style=f"{control_container_style} margin-left: 30px;",
    )


def labelDecoratorTemplate(label, isRequired):
    required_indicator = Span("*", style="color: red; margin-right: 5px;")
    return Div(
        required_indicator if isRequired else None, label, style="display: flex;"
    )


def outputTemplate():
    return Div(
        Div(id="result", style=""),
        style="flex: 1 0 50%; overflow: auto; padding-left: 20px;",
    )


def prettyJsonTemplate(obj):
    return Div(
        Div(
            Pre(json.dumps(obj, indent=4), style="padding: 10px;"),
        ),
    )


def error_template(msg):
    return Div(
        msg,
        style="color: red; white-space: pre-wrap; margin-left: 10px; margin-bottom: 15px; text-indent: -10px;",
    )


copy_js_file_path = os.path.join(
    os.path.dirname(__file__), "js", "copy_to_clipboard.js"
)
copy_js = None
with open(copy_js_file_path, "r") as file:
    copy_js = file.read()


def copy_to_clipboard_button(item):
    return Button(
        "Copy JSON",
        style="margin-left: 10px; min-width: 120px;",
        onclick=copy_js,
        data_clipboard_text=(json.dumps(item, indent=2) if item else ""),
        disabled=(item is None),
    )


download_js_file_path = os.path.join(
    os.path.dirname(__file__), "js", "download_to_file.js"
)
download_js = None
with open(download_js_file_path, "r") as file:
    download_js = file.read()


def download_button(item):
    model_name = item.get("properties", {}).get("mlm:name") if item else None
    return Button(
        "Download JSON",
        style="margin-left: 10px;",
        onclick=download_js,
        data_file_name=f"{model_name if model_name else 'model'}.json",
        data_file_content=(json.dumps(item, indent=2) if item else ""),
        disabled=(item is None),
    )


def button_bar(session):
    item = None
    d = session["stac_format_d"]
    if d:
        try:
            ml_model_metadata = construct_ml_model_properties(d)
            assets = construct_assets(d.get("assets"))
            item = create_pystac_item(ml_model_metadata, assets)
        except:
            pass

    return Div(
        Button(
            "Reset", hx_post="/clear_form", hx_target="#result", hx_swap="innerHTML"
        ),
        copy_to_clipboard_button(item),
        download_button(item),
        id="button-bar",
        hx_swap_oob="#button_bar",
    )


def title_bar(title, session):
    return Div(
        H1(title),
        button_bar(session),
        style="display: flex; justify-content: space-between; align-items: center;",
    )


def tab_bar(selected):
    return Nav(
        Div(
            A(
                "MLM Form",
                href="/",
                _class="secondary" if selected == "/" else "contrast",
                style=tab_style["selected"]
                if selected == "/"
                else tab_style["unselected"],
                role="button",
            ),
            style=tab_wrapper_style,
        ),
        Div(
            A(
                "Asset Form",
                href="/asset",
                _class="secondary" if selected == "/asset" else "contrast",
                style=tab_style["selected"]
                if selected == "/asset"
                else tab_style["unselected"],
                role="button",
            ),
            style=tab_wrapper_style,
        ),
        Div(style=tab_spacer_style),
        style="justify-content: flex-start; margin: 15px 0;",
    )
