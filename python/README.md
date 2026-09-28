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

## Configuration

The service reads `LLM_API_URL`, `LLM_API_KEY`, `LLM_MODEL`, and optional
`LLM_TIMEOUT_SECONDS` from the environment. Production Compose keeps port 8000
inside the application network and gives the Go backend the internal URL
`http://python:8000`.
