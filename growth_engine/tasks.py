"""
growth_engine.tasks — the reply-task QUEUE (command/reply-tasks.json).

A freeform owner directive that the fenced auto-executor can't safely do itself (write a new page,
research + build something, redesign a section) becomes a TASK here instead of being dropped. The
reply-agent (run.py --mode agent) builds each queued task on a throwaway branch and opens a PR; the
owner ships it by replying "merge" (run.py --mode merge). Data-only + committed to main, so the queue
is durable and visible on the /command board.

Statuses: queued → building → pr_open → merged   (or → failed).
"""
from __future__ import annotations
import json, hashlib
from . import model
from .executors import REPO

TASKS_FILE = REPO / "command" / "reply-tasks.json"


def load() -> list:
    try:
        return json.loads(TASKS_FILE.read_text(encoding="utf-8")).get("tasks", [])
    except Exception:
        return []


def save(tasks) -> None:
    TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    TASKS_FILE.write_text(json.dumps({"tasks": tasks}, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _tid(directive: str, batch_id: str) -> str:
    h = hashlib.sha256(f"{batch_id}|{directive.strip()}".encode()).hexdigest()[:8]
    return f"task-{h}"


def enqueue(directive: str, batch_id: str):
    """Add a task, idempotent on (batch, directive). Returns (task, created?)."""
    directive = (directive or "").strip()
    tasks = load()
    tid = _tid(directive, batch_id)
    for t in tasks:
        if t.get("id") == tid:
            return t, False
    t = {"id": tid, "created": model.now(), "batch_id": batch_id, "directive": directive,
         "status": "queued", "branch": None, "pr_url": None, "pr_number": None, "summary": None}
    tasks.append(t)
    save(tasks)
    return t, True


def next_queued():
    for t in load():
        if t.get("status") == "queued":
            return t
    return None


def open_prs() -> list:
    return [t for t in load() if t.get("status") == "pr_open" and t.get("pr_number")]


def update(tid: str, **fields):
    tasks = load()
    for t in tasks:
        if t.get("id") == tid:
            t.update(fields)
    save(tasks)
    return tasks
