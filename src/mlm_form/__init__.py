from .app import app
import uvicorn

def main() -> int:
    uvicorn.run("mlm_form:app", host='0.0.0.0', port=5001, reload=True)
    return 0
