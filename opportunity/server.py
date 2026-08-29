#!/usr/bin/env python3
"""The opportunity-finder service.

Public, unauthenticated and calling a metered API, so the order of checks
matters: origin, then bot check, then rate limit, then budget, and only then
does anything cost money.

Run one worker with threads. The rate-limit window lives in memory, so multiple
workers would each keep their own and the effective limit would multiply.

    gunicorn --workers 1 --threads 8 --bind 0.0.0.0:8080 opportunity.server:app
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request

from flask import Flask, jsonify, request

from . import budget as budget_mod
from . import pipeline

app = Flask(__name__)

ALLOWED_ORIGINS = {
    "https://azrestaurantpartners.com",
    "https://www.azrestaurantpartners.com",
}
if os.environ.get("OPP_ALLOW_LOCALHOST") == "1":
    ALLOWED_ORIGINS |= {"http://localhost:8765", "http://127.0.0.1:8765"}

BUDGET = budget_mod.Budget()
LIMITER = budget_mod.RateLimit(
    per_ip=int(os.environ.get("OPP_PER_IP_HOUR", "5")),
    window_s=3600,
    global_per_min=int(os.environ.get("OPP_GLOBAL_PER_MIN", "30")),
)

TURNSTILE_SECRET = os.environ.get("CF_TURNSTILE_SECRET")


def _cors(resp, origin: str | None):
    if origin in ALLOWED_ORIGINS:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Vary"] = "Origin"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        resp.headers["Access-Control-Max-Age"] = "86400"
    return resp


def _client_ip() -> str:
    fwd = request.headers.get("Fly-Client-IP") or request.headers.get("X-Forwarded-For", "")
    return (fwd.split(",")[0] or request.remote_addr or "unknown").strip()


def _turnstile_ok(token: str | None) -> bool:
    """Only enforced when a secret is configured, so it can be added later."""
    if not TURNSTILE_SECRET:
        return True
    if not token:
        return False
    body = urllib.parse.urlencode({"secret": TURNSTILE_SECRET, "response": token}).encode()
    req = urllib.request.Request(
        "https://challenges.cloudflare.com/turnstile/v0/siteverify", data=body)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return bool(json.loads(r.read().decode()).get("success"))
    except Exception:
        return False


@app.route("/health")
def health():
    return jsonify({
        "ok": True,
        "places_key": bool(os.environ.get("PLACES_API_KEY")),
        "ticketmaster_key": bool(os.environ.get("TICKETMASTER_API_KEY")),
        "groq_key": bool(os.environ.get("GROQ_API_KEY")),
        "budget": BUDGET.status(),
    })


@app.route("/find", methods=["POST", "OPTIONS"])
def find():
    origin = request.headers.get("Origin")

    if request.method == "OPTIONS":
        return _cors(app.make_default_options_response(), origin)

    if origin is not None and origin not in ALLOWED_ORIGINS:
        return _cors(jsonify({"ok": False, "reason": "origin"}), origin), 403

    payload = request.get_json(silent=True) or {}
    query = (payload.get("query") or "").strip()
    if not query or len(query) > 200:
        return _cors(jsonify({"ok": False, "reason": "bad_query"}), origin), 400

    if not _turnstile_ok(payload.get("turnstile_token")):
        return _cors(jsonify({"ok": False, "reason": "bot_check"}), origin), 403

    allowed, why = LIMITER.allow(_client_ip())
    if not allowed:
        return _cors(jsonify({"ok": False, "reason": why}), origin), 429

    try:
        result = pipeline.search(query, budget=BUDGET)
    except Exception:
        app.logger.exception("search failed")
        return _cors(jsonify({"ok": False, "reason": "error"}), origin), 500

    # The budget refusing mid-run is not an error the owner caused. Say so.
    if not result.get("ok") and result.get("reason") == "budget":
        return _cors(jsonify({
            "ok": False, "reason": "budget",
            "message": "This tool is resting until the first of the month.",
        }), origin), 503

    return _cors(jsonify(result), origin)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
