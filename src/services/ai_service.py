import json
from typing import Iterable

from src.models.schemas import TagSuggestionRequest
from src.models.task import Task, TaskPriority
from src.utils.llm_client import LLMClient


def _priority_from_string(value: str) -> TaskPriority:
    value_lower = value.lower().strip()
    if value_lower in {"high", "urgent"}:
        return TaskPriority.high
    if value_lower in {"low"}:
        return TaskPriority.low
    if value_lower in {"medium", "normal", ""}:
        return TaskPriority.medium
    # Unknown priority string
    raise ValueError(f"Invalid priority value: {value}")


def parse_natural_language_task(text: str, client: LLMClient) -> dict:
    """
    Use the LLM (or stub) to turn free-form text into structured task fields.

    Expected JSON output from the LLM:
      {
        "title": "...",
        "description": "...",
        "priority": "low|medium|high",
        "tags": ["tag1", "tag2"]
      }

    If parsing or validation fails, this function raises ValueError so the API
    layer can return a clear 400 error to the user.
    """
    # For the stub provider, keep behaviour deterministic and local.
    if client.provider == "stub":
        first_sentence = text.split(".")[0].strip()
        title = first_sentence[:80] or text[:80]
        priority = _priority_from_string("medium")
        return {
            "title": title,
            "description": text,
            "priority": priority,
            "tags": [],
        }

    prompt = f"""
Given the following command:
"{text}"
Extract fields title, description, priority and tags, and return ONLY valid JSON. priority should be one of low, medium, high:
{{
  "title": "TITLE",
  "description": "DESCRIPTION",
  "priority": "low|medium|high",
  "tags": ["tag1", "tag2"]
}}
"""
    raw = client.generate(prompt)
    print(raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM response was not valid JSON: {exc}") from exc

    # Basic shape validation
    required_keys = {"title", "description", "priority", "tags"}
    missing = required_keys - data.keys()
    if missing:
        raise ValueError(f"LLM response was missing fields: {', '.join(sorted(missing))}")

    title = str(data["title"]).strip()
    description = str(data["description"]).strip() or text
    priority_str = str(data["priority"])
    tags_raw = data["tags"]

    if not title:
        raise ValueError("Title extracted from text was empty.")

    if not isinstance(tags_raw, list):
        raise ValueError("Field 'tags' must be a list.")

    try:
        priority = _priority_from_string(priority_str)
    except ValueError as exc:
        # Surface invalid priority back to caller
        raise

    tags = [str(tag).strip() for tag in tags_raw if str(tag).strip()]

    return {
        "title": title,
        "description": description,
        "priority": priority,
        "tags": tags,
    }


def suggest_tags_and_priority(task: Task | None, prompt: TagSuggestionRequest, client: LLMClient) -> dict:
    """
    Suggest priority and tags for a task, using the LLM when available.

    For non-LLM providers, falls back to a simple heuristic based on text.
    """
    base_title = prompt.title
    base_description = prompt.description or ""

    # Heuristic fallback (also used on errors)
    def _heuristic() -> tuple[TaskPriority, list[str]]:
        text = f"{base_title} {base_description}".lower()
        if "urgent" in text or "high" in text:
            prio = TaskPriority.high
        elif "low" in text:
            prio = TaskPriority.low
        else:
            prio = TaskPriority.medium

        tags: list[str] = []
        for candidate in ["work", "personal", "shopping", "school", "research", "ai", "coding"]:
            if candidate in text:
                tags.append(candidate)
        return prio, tags

    priority = None
    tags: list[str] = []

    if client.provider != "stub" and client.api_key:
        llm_prompt = f"""
You help assign priority and tags to tasks.

Task title: "{base_title}"
Task description: "{base_description}"

Return ONLY valid JSON in this format:
{{
  "priority": "low|medium|high",
  "tags": ["tag1", "tag2"]
}}
"""
        raw = client.generate(llm_prompt)
        try:
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("LLM response must be a JSON object.")

            if "priority" not in data or "tags" not in data:
                raise ValueError("LLM response missing required fields 'priority' or 'tags'.")

            priority = _priority_from_string(str(data["priority"]))
            tags_raw = data["tags"]
            if not isinstance(tags_raw, list):
                raise ValueError("Field 'tags' must be a list.")
            tags = [str(tag).strip() for tag in tags_raw if str(tag).strip()]
        except Exception:
            # Fall back to heuristic if anything goes wrong
            priority, tags = _heuristic()
    else:
        priority, tags = _heuristic()

    suggestion_text = f"priority={priority.value}, tags={tags}"

    return {
        "task_id": task.id if task else None,
        "priority": priority,
        "tags": tags,
        "suggestion": suggestion_text,
        "provider": client.info(),
    }


def summarize_tasks(tasks: Iterable[Task], client: LLMClient) -> dict:
    """
    Produce a short natural-language summary over a list of tasks.

    Uses the LLM when configured; otherwise falls back to a simple
    deterministic summary.
    """
    tasks_list = list(tasks)
    titles = [t.title for t in tasks_list]

    # Fallback summary if we can't or don't want to call an LLM
    def _fallback() -> str:
        if not titles:
            return "No tasks to summarize."
        if len(titles) == 1:
            return f"1 task: {titles[0]}"
        return f"{len(titles)} tasks, including: " + "; ".join(titles[:3])

    summary_text: str

    if client.provider != "stub" and client.api_key and tasks_list:
        lines = []
        for t in tasks_list:
            lines.append(f"- [id={t.id}] {t.title}: {t.description or ''}")
        task_block = "\n".join(lines)

        prompt = f"""
You are summarizing a user's task list.

Tasks:
{task_block}

Return ONLY valid JSON in this format:
{{
  "summary": "One or two sentences summarizing the tasks."
}}
"""
        raw = client.generate(prompt)
        try:
            data = json.loads(raw)
            if not isinstance(data, dict) or "summary" not in data:
                raise ValueError("LLM response missing 'summary'.")
            summary_text = str(data["summary"]).strip() or _fallback()
        except Exception:
            summary_text = _fallback()
    else:
        summary_text = _fallback()

    return {"summary": summary_text, "count": len(tasks_list), "provider": client.info()}


def semantic_search(query: str, tasks: list[Task], client: LLMClient, limit: int = 10) -> dict:
    """
    Semantic search over tasks using embeddings + cosine similarity.

    - Uses client.embed(...) for both the query and each task.
    - Falls back to a simple tag-overlap score if embeddings are unavailable
      or an error occurs.
    """
    if not tasks:
        return {"results": [], "provider": client.info()}

    def _cosine(a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))

    def _fallback() -> list[dict]:
        # Original lexical/tag overlap scoring
        query_terms = set(query.lower().split())
        scored_local: list[dict] = []
        for t in tasks:
            tag_terms = set(tag.lower() for tag in (t.tags or []))
            score = float(len(query_terms & tag_terms))
            scored_local.append({"task_id": t.id, "title": t.title, "score": score})
        scored_local.sort(key=lambda x: x["score"], reverse=True)
        return scored_local[:limit]

    try:
        query_vec = client.embed(query)
        if not isinstance(query_vec, list) or not query_vec:
            raise ValueError("Invalid query embedding.")

        scored: list[dict] = []
        for t in tasks:
            # Combine title, description, and tags into a single text for embedding
            combined = f"{t.title} {t.description or ''} {' '.join(t.tags or [])}"
            task_vec = client.embed(combined)
            if not isinstance(task_vec, list) or not task_vec:
                score = 0.0
            else:
                score = _cosine(query_vec, task_vec)
            scored.append({"task_id": t.id, "title": t.title, "score": score})

        scored.sort(key=lambda x: x["score"], reverse=True)
        final = scored[:limit]
        # If all scores are zero, embeddings likely failed silently; fall back.
        if not final or all(item["score"] == 0.0 for item in final):
            final = _fallback()
    except Exception:
        final = _fallback()

    return {"results": final, "provider": client.info()}


if __name__ == "__main__":
    # Simple manual tests for the AI helpers with multiple NL tasks:
    #   python -m src.services.ai_service
    from src.config import settings

    sample_texts = [
        "Remind me to buy groceries tomorrow at 3pm with high priority, tags: personal, shopping.",
        "Finish the AI-LLM coding challenge by Friday evening.",
    ]
    llm_client = LLMClient(provider=settings.llm_provider, api_key=settings.llm_api_key)

    print(f"Provider: {llm_client.provider}, has_api_key={bool(llm_client.api_key)}")

    tasks: list[Task] = []

    # 1) Test natural language parsing on multiple inputs
    for idx, text in enumerate(sample_texts, start=1):
        try:
            parsed = parse_natural_language_task(text, llm_client)
            print(f"\n[Task {idx}] NL Input :", text)
            print(f"[Task {idx}] NL Parsed:", parsed)

            task = Task(
                title=parsed["title"],
                description=parsed["description"],
                priority=parsed["priority"],
                tags=parsed["tags"],
            )
            # Fake ids for local testing only
            task.id = idx  # type: ignore[attr-defined]
            tasks.append(task)
        except ValueError as exc:
            print(f"[Task {idx}] Failed to parse natural language task:", exc)

    if tasks:
        # 2) Test tag suggestion helper for each task
        for t in tasks:
            tag_req = TagSuggestionRequest(title=t.title, description=t.description)
            tag_suggestion = suggest_tags_and_priority(t, tag_req, llm_client)
            print(f"\nTag suggestion for task id={t.id}:", tag_suggestion)

        # 3) Test summarization over all tasks
        summary = summarize_tasks(tasks, llm_client)
        print("\nSummary over all tasks:", summary)

        # 4) Test semantic search over all tasks
        search_result = semantic_search("do coding job", tasks, llm_client, limit=5)
        print("\nSemantic search results:", search_result)