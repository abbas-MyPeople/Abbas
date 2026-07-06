"""
growth_engine.notify — SEND the daily brief email (ported from seo_engine.notify, retargeted to AZ).

Sends the composed brief from/to the business inbox (send-to-self) so the whole approve→reply loop lives
in one Gmail thread. SMTP + a Gmail app password (stdlib smtplib). Credential-guarded: with no secret it
DRY-RUNS (prints, writes the batch), safe to run anywhere. Stamps an X-AZ-Batch id + Message-ID so the
reply reader (inbox.py) can match the reply. Never prints secret values.

OWNER SETUP (one time): Gmail App Password for the sending account; two env / GitHub secrets:
  WK_ENGINE_EMAIL         = <sending gmail>
  WK_ENGINE_APP_PASSWORD  = <16-char app password>
  WK_ENGINE_TO            = azoeb27@gmail.com   (optional; defaults to WK_ENGINE_EMAIL)
Kill switch: ENGINE_DISABLED=1 → no-op.
"""
from __future__ import annotations
import os, json, smtplib, datetime
from email.message import EmailMessage
from email.utils import make_msgid, formatdate
from . import model, compose

SMTP_HOST, SMTP_PORT = "smtp.gmail.com", 587
BATCH_FILE = model.STATE / "batches.jsonl"


def _disabled() -> bool:
    return os.environ.get("ENGINE_DISABLED") == "1"


def _creds():
    return os.environ.get("WK_ENGINE_EMAIL"), os.environ.get("WK_ENGINE_APP_PASSWORD")


def _batch_id(today=None):
    today = today or datetime.date.today()
    return f"az-{today.isoformat()}"


def _record_batch(rec):
    BATCH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with BATCH_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")


def send_daily(verbose: bool = True) -> dict:
    """Compose from the current finding queue and send (or dry-run). Returns the batch record."""
    if _disabled():
        if verbose:
            print("notify: ENGINE_DISABLED=1 — no-op.")
        return {"disabled": True}

    email_addr, app_pw = _creds()
    e = compose.from_state()
    batch_id = _batch_id()
    msg_id = make_msgid(domain="azrestaurantpartners.com")

    rec = {"batch_id": batch_id, "ts": model.now(), "message_id": msg_id,
           "subject": e["subject"], "counts": e["counts"], "surfaced": e.get("surfaced", []),
           "sent": False, "dry_run": True}

    if not (email_addr and app_pw):
        _record_batch(rec)
        if verbose:
            print(f"notify: DRY-RUN (no WK_ENGINE_EMAIL/APP_PASSWORD). Would send «{e['subject']}».")
        return rec

    recipient = os.environ.get("WK_ENGINE_TO") or email_addr    # deliver to the owner's monitored inbox
    m = EmailMessage()
    m["From"] = email_addr
    m["To"] = recipient
    m["Reply-To"] = email_addr
    m["Subject"] = f"{e['subject']}  [{batch_id}]"
    m["Message-ID"] = msg_id
    m["Date"] = formatdate(localtime=True)
    m["X-AZ-Batch"] = batch_id
    m.set_content(e["body"] + f"\n\n[batch {batch_id} — reply to this email to approve/reject]")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
            s.starttls()
            s.login(email_addr, app_pw)
            s.send_message(m)
        rec.update(sent=True, dry_run=False, recipient=recipient)
        if verbose:
            print(f"notify: sent «{e['subject']}» (batch {batch_id}).")
    except Exception as ex:      # a send failure must not crash the cron; it just wasn't sent
        rec.update(error=f"{type(ex).__name__}")     # note: no secret / no address in the error line
        if verbose:
            print(f"notify: SEND FAILED ({type(ex).__name__}). Nothing sent.")

    _record_batch(rec)
    return rec


def queue_clarification(batch_id: str, question: str, verbose: bool = True) -> dict:
    """Send a short clarifying question back to the owner when a freeform reply is ambiguous/out-of-scope.
    Dry-runs without creds. Used by execute.py via the LLM actioner."""
    if _disabled():
        return {"disabled": True}
    email_addr, app_pw = _creds()
    subject = f"AZ site engine — need a quick clarification [{batch_id}]"
    body = (f"I couldn't safely map your reply to a specific page/section, so I did NOT change anything.\n\n"
            f"{question}\n\n"
            f"Reply with the page + section (e.g. \"index.html hero: make it say …\") and I'll do it.\n"
            f"— {compose.FROM_NAME}")
    if not (email_addr and app_pw):
        if verbose:
            print(f"notify: DRY-RUN clarification — would ask: {question}")
        return {"dry_run": True, "question": question}
    recipient = os.environ.get("WK_ENGINE_TO") or email_addr
    m = EmailMessage()
    m["From"] = email_addr; m["To"] = recipient; m["Reply-To"] = email_addr
    m["Subject"] = subject; m["Message-ID"] = make_msgid(domain="azrestaurantpartners.com")
    m["Date"] = formatdate(localtime=True); m["X-AZ-Batch"] = batch_id
    m.set_content(body)
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
            s.starttls(); s.login(email_addr, app_pw); s.send_message(m)
        if verbose:
            print("notify: clarification sent.")
        return {"sent": True, "question": question}
    except Exception as ex:
        if verbose:
            print(f"notify: clarification SEND FAILED ({type(ex).__name__}).")
        return {"error": type(ex).__name__}


if __name__ == "__main__":
    send_daily()
