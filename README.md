# AI-LLM Task Manager

## Role Track
AI-LLM

## Tech Stack
- Language: Python 3.10+
- Framework: FastAPI
- Database: SQLite (upgrade path to Postgres)
- Other tools: SQLAlchemy, Pydantic, pydantic-settings, httpx (LLM calls)

## Features Implemented
- [ ] REST Task CRUD (FastAPI)
- [ ] Task filtering & sorting
- [ ] Natural language task creation (LLM-assisted)
- [ ] Tag/priority recommendations
- [ ] Task summarization / semantic search
- [ ] Vector store integration

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

## Design Decisions
- FastAPI chosen for speed of prototyping and great docs.
- SQLite by default for zero-setup; swap `DATABASE_URL` for Postgres/MySQL in `.env`.
- Layered structure (`models`, `controllers`, `services`, `routes`, `utils`) to keep concerns separated and make it easy to extend with LLM + vector DB components.
- `services/ai_service.py` and `utils/llm_client.py` encapsulate model provider specifics.

## Challenges & Solutions
- TBD (fill in after implementation).

## Future Improvements
- Finish CRUD + filtering + pagination.
- Add embeddings + vector DB (Chroma/FAISS) for semantic search.
- Add background jobs for summarization/tagging.
- Add tests and CI workflow.
- Dockerfile + Compose for local dev.

## Time Spent
Approximately X hours (fill in after implementation).
