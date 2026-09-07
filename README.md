# AI Helpdesk Automation System

A portfolio project that demonstrates a Python backend for triaging support tickets with local AI assistance. The application accepts tickets through a FastAPI API, stores their lifecycle in SQLite, runs analysis in a background task, and exposes results in a Streamlit dashboard.

> **Project status:** technical demonstration. The repository contains deployment notes from an AWS EC2 deployment; it is not presented as a currently operated customer-support service.

## What it demonstrates

- **FastAPI + SQLAlchemy:** ticket creation, retrieval, validation, and SQLite persistence.
- **Asynchronous work:** ticket analysis runs as a FastAPI background task, keeping ticket creation responsive.
- **Local AI pipeline:** an instant, deterministic fallback for local demos, plus optional retrieval, sentiment detection, and GGUF inference through `llama-cpp-python`.
- **Operational thinking:** retry/backoff logic, SQLite WAL configuration, rotating logs, and automated smoke tests for the local API flow.
- **External integration:** a Zendesk adapter for fetching tickets and adding comments when credentials are configured.
- **Deployment:** previously deployed on an Ubuntu AWS EC2 instance with PM2 managing the API and Streamlit dashboard.

## Architecture

```text
Support ticket
    |
    v
FastAPI API  -->  SQLite / SQLAlchemy
    |
    +--> Background analysis task
            |
            +--> retrieve relevant examples
            +--> analyze sentiment
            +--> local LLM classification
            +--> validate structured response or use fallback
    |
    v
Streamlit dashboard / optional Zendesk integration
```

## Technology

Python, FastAPI, SQLAlchemy, SQLite, Streamlit, Plotly, NumPy, sentence-transformers, `llama-cpp-python`, PM2, AWS EC2, and the Zendesk REST API.

## Local setup

```bash
git clone https://github.com/fafnirkyu/helpdesk.git
cd helpdesk
python -m venv venv
```

Activate the environment, install dependencies, and create your local configuration:

```bash
.\venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

The default `AI_MODE=fallback` runs a fast keyword-based categorizer without downloading models. Set `AI_MODE=local_models` and configure `MODEL_PATH` only after downloading the optional embedding, sentiment, and GGUF model files.

Start the API:

```bash
.\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Then open `http://127.0.0.1:8000/docs` for the interactive API documentation. Start the dashboard separately:

```bash
.\venv\Scripts\python.exe -m streamlit run dashboard.py
```

## Try the local demo

1. Open `http://127.0.0.1:8000/docs` and submit a ticket through `POST /tickets`.
2. The API saves it immediately as `PENDING` and processes it in a background task.
3. Fetch it through `GET /ticket/{ticket_id}`. In fallback mode, an order-related ticket is categorized as `ORDER` with a category-specific support response.
4. Open `http://localhost:8501` to view the stored ticket in the dashboard.

## Tests

The smoke tests use a temporary SQLite database and keep Zendesk disabled:

```bash
.\venv\Scripts\python.exe -m pytest -q tests\test_local_demo.py
```

## Zendesk configuration

Zendesk integration is disabled by default. Add the following values to `.env` only when using a dedicated test account:

```env
ZENDESK_ENABLED=false
ZENDESK_SUBDOMAIN=
ZENDESK_EMAIL=
ZENDESK_TOKEN=
```

## Known limitations

- The application currently uses FastAPI background tasks rather than a durable queue; a production multi-worker deployment should use a task queue with persistent job state.
- The project includes local smoke tests but does not yet have a CI workflow.
- Zendesk processing should use durable idempotency records before being enabled for customer-facing replies.

## Recruiter notes

This repository is intentionally retained as a portfolio project because it demonstrates an end-to-end Python service: API design, persistence, background processing, local AI inference, error handling, observability, a dashboard, external API integration, and cloud deployment.
