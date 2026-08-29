#!/usr/bin/env python3
"""Monthly spend ceiling and per-IP throttle.

Google bills real money past the free tier, so this fails CLOSED: if the counter
file cannot be read or written, the answer is no. A tool that goes quiet is
recoverable; a surprise invoice is not.

Caps default well under the free allowances (Nearby and Text Search are Pro SKUs
at 5,000 free calls each per month) so there is headroom for a bad day.

    python3 opportunity/budget.py --selftest
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import threading
import time
from datetime import datetime, timezone

STATE = pathlib.Path(os.environ.get("OPP_STATE_DIR", "/data")) / "budget.json"

CAPS = {
    "places_text": int(os.environ.get("CAP_PLACES_TEXT", "4000")),
    "places_nearby": int(os.environ.get("CAP_PLACES_NEARBY", "4000")),
}

_lock = threading.Lock()


def _month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


class Budget:
    """Per-SKU monthly counter. One instance per process; guarded by a lock."""

    def __init__(self, path: pathlib.Path = STATE, caps: dict | None = None):
        self.path = path
        self.caps = caps if caps is not None else CAPS
        self.exhausted_sku: str | None = None

    def _read(self) -> dict:
        try:
            data = json.loads(self.path.read_text())
        except FileNotFoundError:
            return {"month": _month(), "counts": {}}
        except (OSError, ValueError):
            # Unreadable state means we do not know what we have spent. Fail closed.
            return None
        if data.get("month") != _month():
            return {"month": _month(), "counts": {}}
        return data

    def _write(self, data: dict) -> bool:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data))
            tmp.replace(self.path)
            return True
        except OSError:
            return False

    def spend(self, sku: str, n: int = 1) -> bool:
        """Reserve n calls against `sku`. False means do not make the call."""
        cap = self.caps.get(sku)
        if cap is None:
            return True
        with _lock:
            data = self._read()
            if data is None:
                self.exhausted_sku = sku
                return False
            used = data["counts"].get(sku, 0)
            if used + n > cap:
                self.exhausted_sku = sku
                return False
            data["counts"][sku] = used + n
            if not self._write(data):
                self.exhausted_sku = sku
                return False
            return True

    def status(self) -> dict:
        data = self._read() or {"month": _month(), "counts": {}}
        return {"month": data["month"],
                "used": data["counts"],
                "caps": self.caps,
                "remaining": {k: max(v - data["counts"].get(k, 0), 0)
                              for k, v in self.caps.items()}}


class RateLimit:
    """Per-IP sliding window, plus a global ceiling. In memory - a restart forgives."""

    def __init__(self, per_ip: int = 5, window_s: int = 3600, global_per_min: int = 30):
        self.per_ip, self.window_s = per_ip, window_s
        self.global_per_min = global_per_min
        self._hits: dict[str, list] = {}
        self._global: list = []

    def allow(self, ip: str) -> tuple[bool, str]:
        now = time.time()
        with _lock:
            self._global = [t for t in self._global if now - t < 60]
            if len(self._global) >= self.global_per_min:
                return False, "busy"

            hits = [t for t in self._hits.get(ip, []) if now - t < self.window_s]
            if len(hits) >= self.per_ip:
                return False, "per_ip"

            hits.append(now)
            self._hits[ip] = hits
            self._global.append(now)

            if len(self._hits) > 5000:          # bound the map
                cutoff = now - self.window_s
                self._hits = {k: v for k, v in self._hits.items() if v and v[-1] > cutoff}
            return True, "ok"


def _selftest() -> int:
    import tempfile
    failures = []

    with tempfile.TemporaryDirectory() as d:
        b = Budget(pathlib.Path(d) / "b.json", caps={"places_nearby": 3})
        if not all(b.spend("places_nearby") for _ in range(3)):
            failures.append("first 3 spends should succeed")
        if b.spend("places_nearby"):
            failures.append("4th spend should be refused")
        if b.status()["remaining"]["places_nearby"] != 0:
            failures.append("remaining should be 0")

        # Unreadable state must fail closed, not fall through to allowed.
        bad = pathlib.Path(d) / "bad.json"
        bad.write_text("{not json")
        if Budget(bad, caps={"places_text": 10}).spend("places_text"):
            failures.append("corrupt state must fail closed")

    r = RateLimit(per_ip=2, window_s=60, global_per_min=100)
    if not (r.allow("1.1.1.1")[0] and r.allow("1.1.1.1")[0]):
        failures.append("first 2 per-IP hits should pass")
    if r.allow("1.1.1.1")[0]:
        failures.append("3rd per-IP hit should be blocked")
    if not r.allow("2.2.2.2")[0]:
        failures.append("a different IP should be unaffected")

    g = RateLimit(per_ip=99, window_s=60, global_per_min=2)
    g.allow("a"); g.allow("b")
    if g.allow("c")[0]:
        failures.append("global ceiling should block")

    for f in failures:
        print("FAIL:", f)
    if not failures:
        print("ok - budget fails closed, rate limits hold")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(_selftest() if "--selftest" in sys.argv else print(__doc__))
