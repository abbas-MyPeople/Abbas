"""
Local JSON storage for az-social-tables.

Deliberately boring: one gitignored JSON file (data/db.json), loaded and written
whole under a lock. Right-sized for a manual pilot (a handful of events, dozens
of applicants). The moment this needs concurrency or scale, swap for SQLite —
the store API below is the only thing app.py talks to.
"""

import json
import os
import threading
import uuid
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("AZST_DB_PATH", os.path.join(HERE, "data", "db.json"))

_LOCK = threading.Lock()

EVENT_TYPES = {
    "singles": "Singles Dinner Night",
    "friends": "New Friends Dinner",
    "discovery": "Food Discovery Table",
    "community": "Community Dinner Night",
}
EVENT_STATUSES = ["draft", "open", "full", "completed", "cancelled"]
APP_STATUSES = ["pending", "approved", "waitlist", "rejected"]
ATTENDANCE = ["", "seated", "no_show"]
INTENTS = {
    "dating": "Dating",
    "friends": "New friends",
    "food": "Food discovery",
    "community": "Community",
}

# Seed events for the Wok & Karahi pilot. Dates are intentionally on the
# restaurant's slow mid-week dinner windows (Tue–Thu; Monday closed).
SEED_EVENTS = [
    {
        "title": "Houston Singles Dinner at Wok & Karahi",
        "type": "singles",
        "venue": "Wok & Karahi",
        "venue_area": "Spring, TX (FM 2920)",
        "date": "2026-07-23",
        "time": "18:30",
        "age_range": "25-39",
        "capacity": 16,
        "deposit": 10,
        "per_guest_fee": 6,
        "offer": "Complimentary appetizer platters for the table",
        "dietary_notes": "Fully halal kitchen. Vegetarian options available. No alcohol served.",
        "description": (
            "One long table, sixteen Houston-area singles, and the halal Chinese + "
            "Indo-Pak kitchen locals rate highest in Spring. We balance the table, "
            "a host kicks things off with two easy icebreakers, and then it's just "
            "dinner — order what you like, talk to real people. No apps, no name "
            "tags, no pitch. Your $10 deposit comes off your food bill."
        ),
        "vibe": "Warm, low-pressure, host-led. Come hungry, leave with numbers you actually want.",
        "status": "open",
    },
    {
        "title": "New Friends Dinner at Wok & Karahi",
        "type": "friends",
        "venue": "Wok & Karahi",
        "venue_area": "Spring, TX (FM 2920)",
        "date": "2026-07-29",
        "time": "18:30",
        "age_range": "21+",
        "capacity": 20,
        "deposit": 10,
        "per_guest_fee": 6,
        "offer": "Free mocktail with any entrée",
        "dietary_notes": "Fully halal kitchen. Vegetarian options available.",
        "description": (
            "New to Spring or North Houston? Work from home and tired of it? This "
            "table is for making actual friends — no dating angle, mixed ages, "
            "seated in small groups that rotate between courses. Deposit counts "
            "toward your meal."
        ),
        "vibe": "Casual and platonic on purpose. Board-game energy, biryani portions.",
        "status": "open",
    },
    {
        "title": "Food Discovery Table: Crispy Beef & the Indo-Chinese Story",
        "type": "discovery",
        "venue": "Wok & Karahi",
        "venue_area": "Spring, TX (FM 2920)",
        "date": "2026-08-06",
        "time": "18:30",
        "age_range": "21+",
        "capacity": 12,
        "deposit": 15,
        "per_guest_fee": 6,
        "offer": "Family-style chef's tasting priced per head, deposit included",
        "dietary_notes": "Fully halal. Tasting can be made vegetarian — note it when you apply.",
        "description": (
            "A family-style guided tasting through the rare all-in-one halal "
            "Chinese + Indian + Pakistani menu — including the Crispy Beef the "
            "restaurant is known for — with the story of how Indo-Chinese food "
            "came to Texas. Twelve seats, shared plates, strangers welcome."
        ),
        "vibe": "For the people whose camera roll is 60% food. Curious eaters, zero snobbery.",
        "status": "open",
    },
]


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def _empty_db():
    return {"events": [], "applications": [], "inquiries": []}


def _seeded_db():
    db = _empty_db()
    for seed in SEED_EVENTS:
        ev = dict(seed)
        ev["id"] = _new_id("evt")
        ev["created_at"] = _now()
        ev["roi"] = {"sales_estimate": None, "baseline_estimate": None, "notes": ""}
        db["events"].append(ev)
    return db


def _load():
    if not os.path.exists(DB_PATH):
        db = _seeded_db()
        _save(db)
        return db
    with open(DB_PATH) as f:
        return json.load(f)


def _save(db):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    tmp = DB_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(db, f, indent=2)
    os.replace(tmp, DB_PATH)


# ---------------------------------------------------------------- events

def list_events(status=None, etype=None):
    with _LOCK:
        events = _load()["events"]
    if status:
        statuses = status if isinstance(status, (list, tuple, set)) else [status]
        events = [e for e in events if e["status"] in statuses]
    if etype:
        events = [e for e in events if e["type"] == etype]
    return sorted(events, key=lambda e: (e["date"], e["time"]))


def get_event(event_id):
    with _LOCK:
        for e in _load()["events"]:
            if e["id"] == event_id:
                return e
    return None


def create_event(fields):
    ev = {
        "id": _new_id("evt"),
        "created_at": _now(),
        "roi": {"sales_estimate": None, "baseline_estimate": None, "notes": ""},
    }
    ev.update(fields)
    with _LOCK:
        db = _load()
        db["events"].append(ev)
        _save(db)
    return ev


def update_event(event_id, fields):
    with _LOCK:
        db = _load()
        for e in db["events"]:
            if e["id"] == event_id:
                e.update(fields)
                _save(db)
                return e
    return None


def update_event_roi(event_id, sales_estimate, baseline_estimate, notes):
    with _LOCK:
        db = _load()
        for e in db["events"]:
            if e["id"] == event_id:
                e["roi"] = {
                    "sales_estimate": sales_estimate,
                    "baseline_estimate": baseline_estimate,
                    "notes": notes,
                }
                _save(db)
                return e
    return None


# ---------------------------------------------------------- applications

def list_applications(event_id=None):
    with _LOCK:
        apps = _load()["applications"]
    if event_id:
        apps = [a for a in apps if a["event_id"] == event_id]
    return sorted(apps, key=lambda a: a["created_at"])


def get_application(app_id):
    with _LOCK:
        for a in _load()["applications"]:
            if a["id"] == app_id:
                return a
    return None


def create_application(fields):
    app = {
        "id": _new_id("app"),
        "created_at": _now(),
        "status": "pending",
        "confirmed": False,
        "attendance": "",
    }
    app.update(fields)
    with _LOCK:
        db = _load()
        db["applications"].append(app)
        _save(db)
    return app


def update_application(app_id, fields):
    with _LOCK:
        db = _load()
        for a in db["applications"]:
            if a["id"] == app_id:
                a.update(fields)
                _save(db)
                return a
    return None


# ------------------------------------------------------------- inquiries

def list_inquiries():
    with _LOCK:
        inqs = _load()["inquiries"]
    return sorted(inqs, key=lambda i: i["created_at"], reverse=True)


def create_inquiry(fields):
    inq = {"id": _new_id("inq"), "created_at": _now(), "status": "new"}
    inq.update(fields)
    with _LOCK:
        db = _load()
        db["inquiries"].append(inq)
        _save(db)
    return inq


def update_inquiry(inq_id, fields):
    with _LOCK:
        db = _load()
        for i in db["inquiries"]:
            if i["id"] == inq_id:
                i.update(fields)
                _save(db)
                return i
    return None


# ----------------------------------------------------------- aggregates

def event_stats(event):
    """Pipeline + attendance tallies for one event (pure function of its apps)."""
    apps = list_applications(event["id"])
    approved = [a for a in apps if a["status"] == "approved"]
    stats = {
        "applications": len(apps),
        "pending": sum(1 for a in apps if a["status"] == "pending"),
        "approved": len(approved),
        "waitlist": sum(1 for a in apps if a["status"] == "waitlist"),
        "rejected": sum(1 for a in apps if a["status"] == "rejected"),
        "confirmed": sum(1 for a in approved if a.get("confirmed")),
        "seated": sum(1 for a in apps if a.get("attendance") == "seated"),
        "no_show": sum(1 for a in apps if a.get("attendance") == "no_show"),
        "gender": {},
        "intent": {},
    }
    for a in approved:
        g = (a.get("gender") or "unspecified").lower()
        stats["gender"][g] = stats["gender"].get(g, 0) + 1
        i = a.get("intent") or "unspecified"
        stats["intent"][i] = stats["intent"].get(i, 0) + 1
    stats["seats_left"] = max(0, int(event.get("capacity") or 0) - stats["approved"])
    confirmed_or_seated = max(stats["confirmed"], stats["seated"] + stats["no_show"])
    stats["show_rate"] = (
        round(100 * stats["seated"] / confirmed_or_seated)
        if confirmed_or_seated else None
    )
    return stats
