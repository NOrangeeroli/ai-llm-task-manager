# AI-LLM Task Manager

NOTICE: I replied heavily on cursor coding assistant.

## Role Track

AI-LLM

## Tech Stack

- Language: Python 3.10+
- Framework: FastAPI
- Database: SQLite (upgrade path to Postgres)
- Other tools: SQLAlchemy, Pydantic, pydantic-settings, httpx (LLM calls)

## Features Implemented

- [X] REST Task CRUD (FastAPI)
- [X] Natural language task creation (LLM-assisted)
- [X] Tag/priority recommendations
- [X] Task summarization / semantic search

## Setup Instructions

1. Prerequisites
   - Python 3.10+
   - `pip` (or `uv`)
2. Installation
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Configuration
   - Copy `.env.example` to `.env` and fill in secrets (e.g., `OPENAI_API_KEY`).
   - Override `DATABASE_URL` if not using the default SQLite file under `./data/tasks.db`.
4. Running the application
   ```bash
   uvicorn src.main:app --reload
   ```

## API Documentation

- Interactive docs available at `/docs` and `/redoc` when the server is running.
- Planned endpoints (see `src/routes/task_routes.py`):

  - `POST /tasks` create task
  - `GET /tasks` list/filter tasks
  - `GET /tasks/{task_id}` retrieve a task
  - `PATCH /tasks/{task_id}` update task
  - `DELETE /tasks/{task_id}` delete task
  - `POST /tasks/natural-language` LLM-assisted creation
  - `POST /tasks/{task_id}/tags/suggestions` tag/priority hints
  - `POST /tasks/summary` summarize tasks
  - `POST /tasks/search` semantic search placeholder
  - 

  ## Time Spent
- About 4 hrs
