main_element_style = "padding-left: 25px; padding-right: 25px; display: flex; flex-direction: column; height: 100vh;"

control_container_style = (
    "display: flex; flex-direction: column; align-items: flex-start;"
)

text_input_style = "width: 400px; text-align: center;"

select_input_style = "width: 400px;"

form_style = "overflow: auto; flex: 1 0 50%;"

tab_border_color = "#999"

tab_wrapper_style = f"padding-right: 10px; border-bottom: 1px solid {tab_border_color}; position: relative;"

tab_style_base = "border-bottom-left-radius: 0; border-bottom-right-radius: 0; position: relative; top: 1px;"

tab_style = {
    "selected": f"{tab_style_base} background-color: #13171f; border-color: {tab_border_color}; border-bottom-color: #13171f; cursor: default;",
    "unselected": f"{tab_style_base} border-bottom-color: {tab_border_color};",
}

tab_spacer_style = f"border-bottom: 1px solid {tab_border_color}; flex: 1 0 auto;"
