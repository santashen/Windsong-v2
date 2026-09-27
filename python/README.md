# Windsong Python Services

Python capability services used internally by the Windsong Go backend.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn windsong_python.main:app --reload --port 8000
```

The service is intended to be called by the Go backend. It is not a public browser API.
