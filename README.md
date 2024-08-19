# Starting mlm-form

1. `pip install -r requirements.txt`
2. `python main.py`


To deploy to Vercel, `requirements.txt` must be present, so must `main.py`, and the FastHTML framework option needs to be selected in the Vercel UI. Trying to adopt a different package structure and edit vercel.json startCommand and buildCommand came with much peril.