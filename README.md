# AI Helpdesk Automation System

A portfolio project that demonstrates a Python backend for triaging support tickets with local AI assistance. The application accepts tickets through a FastAPI API, stores their lifecycle in SQLite, runs analysis in a background task, and exposes results in a Streamlit dashboard.

> **Project status:** technical demonstration. The repository contains deployment notes from an AWS EC2 deployment; it is not presented as a currently operated customer-support service.

## What it demonstrates

- **FastAPI + SQLAlchemy:** ticket creation, retrieval, validation, and SQLite persistence.
- **Asynchronous work:** ticket analysis runs as a FastAPI background task, keeping ticket creation responsive.
- **Local AI pipeline:** retrieval of relevant support examples, sentiment detection, local GGUF inference through `llama-cpp-python`, structured-output validation, and a keyword fallback when inference fails.
- **Operational thinking:** retry/backoff logic, SQLite WAL configuration, rotating logs, and a stress-test script for the HTTP API.
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
python -m venv .venv
```

Activate the environment, install dependencies, and create your local configuration:

```bash
pip install -r requirements.txt
copy .env.example .env  # Windows PowerShell
```

Set `MODEL_PATH` in `.env` to the location of your local GGUF model if you want inference enabled. Without a model, the application falls back to keyword-based categorization.

Start the API:

```bash
uvicorn main:app --reload
```

Then open `http://127.0.0.1:8000/docs` for the interactive API documentation. Start the dashboard separately:

```bash
streamlit run dashboard.py
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
- The project does not yet have a maintained automated unit/integration test suite or CI workflow.
- Zendesk processing should use durable idempotency records before being enabled for customer-facing replies.

## Recruiter notes

This repository is intentionally retained as a portfolio project because it demonstrates an end-to-end Python service: API design, persistence, background processing, local AI inference, error handling, observability, a dashboard, external API integration, and cloud deployment.
