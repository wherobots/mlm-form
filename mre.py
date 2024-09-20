from fasthtml.common import *

app, rt = fast_app()

chapters = ['ch1', 'ch2', 'ch3']
lessons = {
    'ch1': ['lesson1', 'lesson2', 'lesson3'],
    'ch2': ['lesson4', 'lesson5', 'lesson6'],
}

def mk_opts(nm, cs):
    return (
        Option(f'-- select {nm} --', disabled='', selected='', value=''),
        *map(Option, cs))

@app.get('/get_lesson')
def get_lesson(chapter: str):
    return Select(*mk_opts('lesson', lessons[chapter]), name='lesson')

@app.get('/')
def homepage():
    chapter_dropdown = Select(
        *mk_opts('chapter', chapters),
        name='chapter',
        get='get_lesson', hx_target='#lesson')

    return Div(
        Div(
            Label("Chapter:", for_="chapter"),
            chapter_dropdown),
        Div(
            Label("Lesson:", for_="lesson"),
            Div(Div(id='lesson')),
    ))

serve()