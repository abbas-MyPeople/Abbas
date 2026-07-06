"""
Route-level smoke test for az-social-tables. No test framework needed:

    python smoke_test.py

Uses a throwaway DB file so the real data/db.json is untouched.
"""

import base64
import os
import sys
import tempfile

_tmp = tempfile.mkdtemp(prefix="azst-test-")
os.environ["AZST_DB_PATH"] = os.path.join(_tmp, "db.json")

import store  # noqa: E402  (env must be set before import)
import app as app_module  # noqa: E402

AUTH = {"Authorization": "Basic " + base64.b64encode(b"admin:admin").decode()}
failures = []


def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail and not ok else ""))
    if not ok:
        failures.append(name)


client = app_module.app.test_client()
print("public routes:")
for path in ["/", "/events", "/events?type=singles", "/restaurants", "/health"]:
    r = client.get(path)
    check(f"GET {path} -> 200", r.status_code == 200, str(r.status_code))

events = store.list_events(status="open")
check("seed events exist (3)", len(events) == 3, str(len(events)))
ev = events[0]

r = client.get(f"/events/{ev['id']}")
check("GET event detail -> 200", r.status_code == 200, str(r.status_code))
check("event detail shows trust language", b"Trust &amp; safety" in r.data)
check("GET missing event -> 404", client.get("/events/evt_nope").status_code == 404)

print("consumer application:")
r = client.post(f"/events/{ev['id']}/apply", data={
    "name": "Test Guest", "contact": "555-0100", "age_range": "25-39",
    "gender": "woman", "intent": "dating", "dietary": "no nuts",
    "area": "Spring / Klein", "vibe": "Engineer who cooks.", "consent": "1",
})
check("valid application -> success page", r.status_code == 200 and b"queue" in r.data)
apps = store.list_applications(ev["id"])
check("application persisted", len(apps) == 1)
r = client.post(f"/events/{ev['id']}/apply", data={"name": "No Consent"}, follow_redirects=True)
check("invalid application rejected with flash",
      len(store.list_applications(ev["id"])) == 1 and b"required" in r.data)

print("restaurant inquiry:")
client.post("/restaurants/inquiry", data={
    "restaurant": "Test Bistro", "contact": "owner@test.com", "slow_nights": "Tue",
})
check("inquiry persisted", len(store.list_inquiries()) == 1)

print("admin auth:")
check("admin without auth -> 401", client.get("/admin").status_code == 401)
check("admin with auth -> 200", client.get("/admin", headers=AUTH).status_code == 200)

print("admin flows:")
app_id = apps[0]["id"]
client.post(f"/admin/applications/{app_id}/decision", data={"decision": "approved"}, headers=AUTH)
check("approve applicant", store.get_application(app_id)["status"] == "approved")
client.post(f"/admin/applications/{app_id}/confirm", data={"confirmed": "1"}, headers=AUTH)
check("mark deposit confirmed", store.get_application(app_id)["confirmed"] is True)
client.post(f"/admin/applications/{app_id}/attendance", data={"attendance": "seated"}, headers=AUTH)
check("mark seated", store.get_application(app_id)["attendance"] == "seated")

r = client.post("/admin/events/new", data={
    "title": "QA Community Dinner", "type": "community", "venue": "Wok & Karahi",
    "venue_area": "Spring, TX", "date": "2026-08-20", "time": "18:30",
    "age_range": "21+", "capacity": "18", "deposit": "10", "per_guest_fee": "6",
    "status": "draft", "offer": "", "dietary_notes": "", "vibe": "QA", "description": "QA",
}, headers=AUTH)
check("create event via admin", r.status_code == 302)
new_ev = [e for e in store.list_events() if e["title"] == "QA Community Dinner"]
check("created event persisted as draft", bool(new_ev) and new_ev[0]["status"] == "draft")
if new_ev:
    check("draft event hidden from public", client.get(f"/events/{new_ev[0]['id']}").status_code == 404)
    r = client.post(f"/admin/events/{new_ev[0]['id']}/edit", data={
        "title": "QA Community Dinner", "type": "community", "venue": "Wok & Karahi",
        "venue_area": "Spring, TX", "date": "2026-08-20", "time": "18:30",
        "age_range": "21+", "capacity": "18", "deposit": "10", "per_guest_fee": "6",
        "status": "open", "offer": "", "dietary_notes": "", "vibe": "QA", "description": "QA",
    }, headers=AUTH)
    check("edit event -> open", store.get_event(new_ev[0]["id"])["status"] == "open")
    check("open event visible publicly", client.get(f"/events/{new_ev[0]['id']}").status_code == 200)

client.post(f"/admin/events/{ev['id']}/roi",
            data={"sales_estimate": "512.50", "baseline_estimate": "180", "notes": "test"},
            headers=AUTH)
roi = store.get_event(ev["id"])["roi"]
check("ROI saved", roi["sales_estimate"] == 512.5 and roi["baseline_estimate"] == 180.0)
r = client.get(f"/admin/events/{ev['id']}", headers=AUTH)
check("admin event page renders ROI", r.status_code == 200 and b"Restaurant net" in r.data)

print("clover adapter (mock):")
from integrations.clover import get_adapter  # noqa: E402
rep = get_adapter().event_night_report("2026-07-23", "18:30", "21:30")
check("mock report has incremental", isinstance(rep["incremental"], float) and rep["source"] == "mock")

print()
if failures:
    print(f"{len(failures)} FAILURE(S): {failures}")
    sys.exit(1)
print("ALL CHECKS PASSED")
