"""
AZ Social Tables — restaurant social dining demand engine (pilot MVP).

Standalone Flask app. Runs entirely from this folder: JSON-file storage,
mocked Clover adapter, HTTP Basic auth on /admin (same convention as the
sibling Render apps: AUTH_USER / AUTH_PASS env vars; dev default admin/admin).

    pip install -r requirements.txt
    python app.py            # http://localhost:5100
"""

import os
from functools import wraps

from flask import (
    Flask, abort, flash, redirect, render_template, request, url_for, Response,
)

import store
from integrations.clover import get_adapter

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-not-a-secret")

AUTH_USER = os.environ.get("AUTH_USER", "admin")
AUTH_PASS = os.environ.get("AUTH_PASS", "admin")

clover = get_adapter()

AGE_RANGES = ["21-29", "25-39", "30-45", "40+", "21+"]
AREAS = [
    "Spring / Klein", "The Woodlands", "Tomball / Cypress",
    "North Houston", "Houston (other)", "Other",
]


@app.context_processor
def inject_globals():
    return {
        "EVENT_TYPES": store.EVENT_TYPES,
        "INTENTS": store.INTENTS,
    }


# ------------------------------------------------------------- public site

@app.get("/")
def landing():
    events = store.list_events(status=["open", "full"])
    return render_template("index.html", events=events[:3])


@app.get("/events")
def events_list():
    etype = request.args.get("type") or None
    if etype not in store.EVENT_TYPES:
        etype = None
    events = store.list_events(status=["open", "full"], etype=etype)
    stats = {e["id"]: store.event_stats(e) for e in events}
    return render_template("events.html", events=events, stats=stats, active_type=etype)


@app.get("/events/<event_id>")
def event_detail(event_id):
    event = store.get_event(event_id)
    if not event or event["status"] in ("draft", "cancelled"):
        abort(404)
    stats = store.event_stats(event)
    return render_template(
        "event_detail.html", event=event, stats=stats,
        age_ranges=AGE_RANGES, areas=AREAS,
    )


@app.post("/events/<event_id>/apply")
def event_apply(event_id):
    event = store.get_event(event_id)
    if not event or event["status"] not in ("open", "full"):
        abort(404)
    form = request.form
    required = ["name", "contact", "age_range", "intent", "area", "vibe"]
    missing = [f for f in required if not form.get(f, "").strip()]
    if missing or not form.get("consent"):
        flash("Please fill in every required field and accept the guest agreement.")
        return redirect(url_for("event_detail", event_id=event_id) + "#apply")
    store.create_application({
        "event_id": event_id,
        "name": form["name"].strip(),
        "contact": form["contact"].strip(),
        "age_range": form["age_range"],
        "gender": form.get("gender", "").strip(),
        "intent": form["intent"],
        "dietary": form.get("dietary", "").strip(),
        "area": form["area"],
        "vibe": form["vibe"].strip()[:500],
        "consent": True,
    })
    return render_template("apply_success.html", event=event)


@app.get("/restaurants")
def restaurants():
    return render_template("restaurants.html")


@app.post("/restaurants/inquiry")
def restaurant_inquiry():
    form = request.form
    if not form.get("restaurant", "").strip() or not form.get("contact", "").strip():
        flash("Restaurant name and a way to reach you are required.")
        return redirect(url_for("restaurants") + "#inquiry")
    store.create_inquiry({
        "restaurant": form["restaurant"].strip(),
        "name": form.get("name", "").strip(),
        "contact": form["contact"].strip(),
        "area": form.get("area", "").strip(),
        "slow_nights": form.get("slow_nights", "").strip(),
        "notes": form.get("notes", "").strip()[:1000],
    })
    flash("Thanks — we'll reach out within one business day to talk through your slow nights.")
    return redirect(url_for("restaurants") + "#inquiry")


@app.get("/health")
def health():
    return {"ok": True}


# ------------------------------------------------------------------ admin

def requires_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != AUTH_USER or auth.password != AUTH_PASS:
            return Response(
                "Operator login required.", 401,
                {"WWW-Authenticate": 'Basic realm="AZ Social Tables admin"'},
            )
        return fn(*args, **kwargs)
    return wrapper


def _event_form_fields(form):
    errors = []
    fields = {
        "title": form.get("title", "").strip(),
        "type": form.get("type", ""),
        "venue": form.get("venue", "").strip(),
        "venue_area": form.get("venue_area", "").strip(),
        "date": form.get("date", "").strip(),
        "time": form.get("time", "").strip(),
        "age_range": form.get("age_range", "").strip(),
        "offer": form.get("offer", "").strip(),
        "dietary_notes": form.get("dietary_notes", "").strip(),
        "description": form.get("description", "").strip(),
        "vibe": form.get("vibe", "").strip(),
        "status": form.get("status", "draft"),
    }
    if not fields["title"]:
        errors.append("Title is required.")
    if fields["type"] not in store.EVENT_TYPES:
        errors.append("Pick a valid event type.")
    if not fields["venue"]:
        errors.append("Venue is required.")
    if not fields["date"] or not fields["time"]:
        errors.append("Date and time are required.")
    if fields["status"] not in store.EVENT_STATUSES:
        errors.append("Invalid status.")
    for key, label in [("capacity", "Capacity"), ("deposit", "Deposit"),
                       ("per_guest_fee", "Per-seated-guest fee")]:
        raw = form.get(key, "").strip()
        try:
            fields[key] = max(0, int(float(raw))) if raw else 0
        except ValueError:
            errors.append(f"{label} must be a number.")
            fields[key] = 0
    if fields.get("capacity", 0) <= 0:
        errors.append("Capacity must be at least 1.")
    return fields, errors


@app.get("/admin")
@requires_auth
def admin_dashboard():
    events = store.list_events()
    stats = {e["id"]: store.event_stats(e) for e in events}
    inquiries = store.list_inquiries()
    totals = {
        "applications": sum(s["applications"] for s in stats.values()),
        "pending": sum(s["pending"] for s in stats.values()),
        "confirmed": sum(s["confirmed"] for s in stats.values()),
        "seated": sum(s["seated"] for s in stats.values()),
    }
    return render_template(
        "admin/dashboard.html", events=events, stats=stats,
        inquiries=inquiries, totals=totals,
    )


@app.route("/admin/events/new", methods=["GET", "POST"])
@requires_auth
def admin_event_new():
    if request.method == "POST":
        fields, errors = _event_form_fields(request.form)
        if errors:
            for e in errors:
                flash(e)
            return render_template("admin/event_form.html", event=fields, is_new=True)
        ev = store.create_event(fields)
        flash("Event created.")
        return redirect(url_for("admin_event", event_id=ev["id"]))
    return render_template("admin/event_form.html", event=None, is_new=True)


@app.route("/admin/events/<event_id>/edit", methods=["GET", "POST"])
@requires_auth
def admin_event_edit(event_id):
    event = store.get_event(event_id)
    if not event:
        abort(404)
    if request.method == "POST":
        fields, errors = _event_form_fields(request.form)
        if errors:
            for e in errors:
                flash(e)
            fields["id"] = event_id
            return render_template("admin/event_form.html", event=fields, is_new=False)
        store.update_event(event_id, fields)
        flash("Event updated.")
        return redirect(url_for("admin_event", event_id=event_id))
    return render_template("admin/event_form.html", event=event, is_new=False)


@app.get("/admin/events/<event_id>")
@requires_auth
def admin_event(event_id):
    event = store.get_event(event_id)
    if not event:
        abort(404)
    apps = store.list_applications(event_id)
    stats = store.event_stats(event)
    roi = event.get("roi") or {}
    sales = roi.get("sales_estimate")
    baseline = roi.get("baseline_estimate")
    # Manual operator numbers win; the mocked Clover report fills the gap so the
    # panel demonstrates what the automated version will show.
    clover_report = None
    if sales is None or baseline is None:
        end_hour = (int(event["time"][:2]) + 3) % 24 if event.get("time") else 21
        clover_report = clover.event_night_report(
            event["date"], event.get("time", "18:30"), f"{end_hour:02d}:00")
    eff_sales = sales if sales is not None else (clover_report or {}).get("revenue")
    eff_base = baseline if baseline is not None else (clover_report or {}).get("baseline")
    fee = int(event.get("per_guest_fee") or 0) * stats["seated"]
    roi_summary = None
    if eff_sales is not None and eff_base is not None:
        incremental = round(eff_sales - eff_base, 2)
        roi_summary = {
            "revenue": eff_sales,
            "baseline": eff_base,
            "incremental": incremental,
            "fee": fee,
            "restaurant_net": round(incremental - fee, 2),
            "multiple": round(incremental / fee, 1) if fee else None,
            "spend_per_seated": round(eff_sales / stats["seated"], 2) if stats["seated"] else None,
            "estimated": sales is None or baseline is None,
        }
    return render_template(
        "admin/event_detail.html", event=event, apps=apps, stats=stats,
        roi=roi, roi_summary=roi_summary,
    )


@app.post("/admin/applications/<app_id>/decision")
@requires_auth
def admin_app_decision(app_id):
    application = store.get_application(app_id)
    decision = request.form.get("decision")
    if not application or decision not in store.APP_STATUSES:
        abort(400)
    fields = {"status": decision}
    if decision != "approved":
        fields["confirmed"] = False
    store.update_application(app_id, fields)
    return redirect(url_for("admin_event", event_id=application["event_id"]))


@app.post("/admin/applications/<app_id>/confirm")
@requires_auth
def admin_app_confirm(app_id):
    application = store.get_application(app_id)
    if not application:
        abort(400)
    store.update_application(app_id, {"confirmed": request.form.get("confirmed") == "1"})
    return redirect(url_for("admin_event", event_id=application["event_id"]))


@app.post("/admin/applications/<app_id>/attendance")
@requires_auth
def admin_app_attendance(app_id):
    application = store.get_application(app_id)
    mark = request.form.get("attendance", "")
    if not application or mark not in store.ATTENDANCE:
        abort(400)
    store.update_application(app_id, {"attendance": mark})
    return redirect(url_for("admin_event", event_id=application["event_id"]))


@app.post("/admin/events/<event_id>/roi")
@requires_auth
def admin_event_roi(event_id):
    event = store.get_event(event_id)
    if not event:
        abort(404)

    def num(name):
        raw = request.form.get(name, "").strip()
        try:
            return round(float(raw), 2) if raw else None
        except ValueError:
            return None

    store.update_event_roi(
        event_id, num("sales_estimate"), num("baseline_estimate"),
        request.form.get("notes", "").strip()[:1000],
    )
    flash("ROI numbers saved.")
    return redirect(url_for("admin_event", event_id=event_id))


@app.post("/admin/inquiries/<inq_id>/status")
@requires_auth
def admin_inquiry_status(inq_id):
    status = request.form.get("status")
    if status not in ("new", "contacted", "closed"):
        abort(400)
    store.update_inquiry(inq_id, {"status": status})
    return redirect(url_for("admin_dashboard") + "#inquiries")


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5100)))
