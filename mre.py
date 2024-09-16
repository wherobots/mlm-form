from fasthtml.common import *
import json
app, rt = fast_app(hdrs=(picolink))

main_element_style = "padding-left: 25px;"

control_container_style = "display: flex; flex-direction: column; align-items: flex-start;"

text_input_style = "width: 400px; text-align: center;"

select_input_style = "width: 400px;"
@app.get('/')
def homepage(session):

    return Body(
        Main(
            Header(
                H1("Input Text with Session State and Fill Form"),
            ),
            Section(
                Button("Clear Form State", hx_post='/clear_form',
                       style="margin-top: 20px;", hx_target="#result", hx_swap="innerHTML")
            ),
            Grid(
                session_form(session, submitOnLoad=True),
                outputTemplate()
            ),
            style=main_element_style
        )
    )

@app.post('/clear_form')
def clear_form(session):
    session.clear()
    return session_form(session)


def prettyJsonTemplate(obj):
    return Pre(json.dumps(obj, indent = 4), style="margin-top: 25px; width: 100%;")

def outputTemplate():
    return Div(
        Div(id="result", style="position: fixed; right: 50px; width: 500px; height: calc(100vh - 250px); overflow: auto;"),
        style="position: relative;"
    )

def inputTemplate(label, name, val, error_msg=None, input_type='text', canValidateInline=False):
    return Div(hx_target='this', hx_swap='outerHTML', cls=f"{error_msg if error_msg else 'Valid'}", style=control_container_style)(
               Input(name=name,type=input_type,value=f'{val}',hx_post=f'/{name.lower()}' if canValidateInline else None, style=text_input_style),
               Div(f'{error_msg}', style='color: red;') if error_msg else None)

@app.post('/submit')
def submit(session, d: dict):
    session.setdefault('form_data', {})
    session['form_data'].update(d)
    return prettyJsonTemplate(d)

# helper function to render out the session form
# because of the `hx_swap_oob`, this snippet can be returned by any handler and will update the form
# see https://htmx.org/examples/update-other-content/#oob
#
# `submitOnLoad` should be set to true for the initial page load so that the form will
# auto-submit to populate the results if there is saved state in the session
def session_form(session, submitOnLoad=False):
    session.setdefault('form_data', {})
    result = session.get('form_data', {})
    trigger = "input delay:200ms, load" if submitOnLoad and result else "input delay:200ms"
    session_form = Form(hx_post='/submit', hx_target='#result', hx_trigger=trigger, id="session_form", hx_swap_oob="#session_form")(
                    inputTemplate(label="Text Input. Paste text and then refresh the page. fill form does not keep the pasted value if it is over 122 characters.", val='', name="text_input"),
                )
    fill_form(session_form, result)
    return session_form

serve()