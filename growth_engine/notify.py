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
    if e.get("html"):                       # branded HTML is the primary view; plain text is the fallback
        m.add_alternative(e["html"], subtype="html")

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


def send_ack(batch_id, understood, next_steps, verbose: bool = True) -> dict:
    """Reply to the owner right after their reply: what we understood + what we'll do. Dry-runs w/o creds."""
    if _disabled():
        return {"disabled": True}
    email_addr, app_pw = _creds()
    C = compose
    subject = f"AZ site engine — got your reply, here's the plan [{batch_id}]"
    u = "\n".join(f"  • {x}" for x in understood) or "  • (no clear items)"
    n = "\n".join(f"  • {x}" for x in next_steps) or "  • Nothing to ship."
    body = (f"Got your reply — here's what I understood, and what I'll do next.\n\n"
            f"WHAT I UNDERSTOOD\n{u}\n\nWHAT I'LL DO\n{n}\n\n"
            f"Nothing goes live until it passes validation. You'll see how it turned out in tomorrow's brief.\n"
            f"— {C.FROM_NAME}")

    def _li(items, dot):
        return "".join(f'<div style="color:{C._BODY};font-size:14px;padding:3px 0 3px 16px;position:relative;">'
                       f'<span style="position:absolute;left:0;color:{dot};">•</span>{C._esc(x)}</div>' for x in items)
    html = (f'<!doctype html><html><body style="margin:0;background:{C._PAPER};">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{C._PAPER};padding:20px 0;"><tr><td align="center">'
            f'<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:{C._CARD};border:1px solid {C._LINE};border-radius:14px;overflow:hidden;">'
            f'<tr><td style="height:4px;background:{C._EMBER};"></td></tr>'
            f'<tr><td style="padding:18px 24px 6px;"><div style="font-family:{C._SERIF};color:{C._INK};font-size:18px;font-weight:700;">Got it — here\'s the plan</div>'
            f'<div style="color:{C._MUTED};font-size:13px;margin-top:2px;">Reply received · batch {C._esc(batch_id or "")}</div></td></tr>'
            f'<tr><td style="padding:10px 24px 2px;"><div style="font-family:{C._SERIF};color:{C._INK};font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;">What I understood</div>{_li(understood, C._MUTED)}</td></tr>'
            f'<tr><td style="padding:12px 24px 2px;"><div style="font-family:{C._SERIF};color:{C._INK};font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;">What I\'ll do next</div>{_li(next_steps, C._EMBER)}</td></tr>'
            f'<tr><td style="padding:14px 24px 20px;color:{C._MUTED};font-size:12px;">Nothing goes live until it passes validation. You\'ll see how it turned out in tomorrow\'s brief.<br>— {C.FROM_NAME}</td></tr>'
            f'</table></td></tr></table></body></html>')

    if not (email_addr and app_pw):
        if verbose:
            print(f"notify: DRY-RUN ack — {len(understood)} understood, {len(next_steps)} next step(s).")
        return {"dry_run": True}
    recipient = os.environ.get("WK_ENGINE_TO") or email_addr
    m = EmailMessage()
    m["From"] = email_addr; m["To"] = recipient; m["Reply-To"] = email_addr
    m["Subject"] = subject; m["Message-ID"] = make_msgid(domain="azrestaurantpartners.com")
    m["Date"] = formatdate(localtime=True); m["X-AZ-Batch"] = batch_id or ""
    m.set_content(body); m.add_alternative(html, subtype="html")
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
            s.starttls(); s.login(email_addr, app_pw); s.send_message(m)
        if verbose:
            print("notify: ack sent.")
        return {"sent": True}
    except Exception as ex:
        if verbose:
            print(f"notify: ack SEND FAILED ({type(ex).__name__}).")
        return {"error": type(ex).__name__}


def _send_simple(subject, body, html, batch_id, verbose=True) -> dict:
    """Shared SMTP send for the reply-agent notifications. Dry-runs without creds; never raises out."""
    if _disabled():
        return {"disabled": True}
    email_addr, app_pw = _creds()
    if not (email_addr and app_pw):
        if verbose:
            print(f"notify: DRY-RUN — would send «{subject}».")
        return {"dry_run": True}
    recipient = os.environ.get("WK_ENGINE_TO") or email_addr
    m = EmailMessage()
    m["From"] = email_addr; m["To"] = recipient; m["Reply-To"] = email_addr
    m["Subject"] = subject; m["Message-ID"] = make_msgid(domain="azrestaurantpartners.com")
    m["Date"] = formatdate(localtime=True); m["X-AZ-Batch"] = batch_id or ""
    m.set_content(body)
    if html:
        m.add_alternative(html, subtype="html")
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
            s.starttls(); s.login(email_addr, app_pw); s.send_message(m)
        if verbose:
            print(f"notify: sent «{subject}».")
        return {"sent": True}
    except Exception as ex:
        if verbose:
            print(f"notify: SEND FAILED ({type(ex).__name__}).")
        return {"error": type(ex).__name__}


def send_task_done(task, pr_url, summary, verbose: bool = True) -> dict:
    """Email the owner that a reply-task is built and open as a PR to review, with the link.
    Tags the subject with the task's batch id so a 'merge' reply threads back to the loop."""
    C = compose
    bid = (task or {}).get("batch_id", "")
    directive = (task or {}).get("directive", "")
    subject = f"AZ site engine — built what you asked, ready to review [{bid}]"
    link = pr_url or "(PR link unavailable — check the repo's Pull Requests)"
    body = (f"You asked:\n  “{directive}”\n\n"
            f"I built it and opened a pull request so you can review it before anything goes live:\n"
            f"  {link}\n\n"
            f"What I did: {summary}\n\n"
            f"On that page you can see the full diff and a preview of the change. If it looks good, just "
            f"reply “merge” and I'll ship it to the live site. If not, tell me what to change.\n"
            f"— {C.FROM_NAME}")
    btn = (f'<a href="{C._esc(pr_url)}" style="display:inline-block;background:{C._EMBER};color:#fff;'
           f'text-decoration:none;font-family:{C._SANS};font-weight:600;font-size:14px;padding:11px 20px;'
           f'border-radius:999px;">Review the change &rarr;</a>') if pr_url else ""
    html = (f'<!doctype html><html><body style="margin:0;background:{C._PAPER};">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{C._PAPER};padding:20px 0;"><tr><td align="center">'
            f'<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:{C._CARD};border:1px solid {C._LINE};border-radius:14px;overflow:hidden;">'
            f'<tr><td style="height:4px;background:{C._EMBER};"></td></tr>'
            f'<tr><td style="padding:18px 24px 4px;"><div style="font-family:{C._SERIF};color:{C._INK};font-size:19px;font-weight:700;">Built what you asked — ready to review</div></td></tr>'
            f'<tr><td style="padding:6px 24px 2px;"><div style="color:{C._MUTED};font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;">You asked</div>'
            f'<div style="color:{C._INK};font-size:15px;font-style:italic;padding:4px 0 10px;">&ldquo;{C._esc(directive)}&rdquo;</div></td></tr>'
            f'<tr><td style="padding:2px 24px 6px;"><div style="color:{C._MUTED};font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;">What I did</div>'
            f'<div style="color:{C._BODY};font-size:14px;padding:4px 0 12px;line-height:1.5;">{C._esc(summary)}</div>{btn}</td></tr>'
            f'<tr><td style="padding:16px 24px 20px;color:{C._BODY};font-size:13px;line-height:1.55;">'
            f'Open the link to see the full diff + preview. If it&rsquo;s good, reply <b style="color:{C._EMBER};">&ldquo;merge&rdquo;</b> and I&rsquo;ll ship it live. '
            f'If not, tell me what to change.<div style="color:{C._MUTED};font-size:12px;margin-top:10px;">Nothing is live yet — it&rsquo;s waiting on your say-so.<br>&mdash; {C.FROM_NAME}</div></td></tr>'
            f'</table></td></tr></table></body></html>')
    return _send_simple(subject, body, html, bid, verbose=verbose)


def send_merged(task, verbose: bool = True) -> dict:
    """Confirm to the owner that their approved reply-task PR was merged + is deploying."""
    C = compose
    bid = (task or {}).get("batch_id", "")
    directive = (task or {}).get("directive", "")
    subject = f"AZ site engine — merged + shipping [{bid}]"
    body = (f"Done — I merged it and it's deploying to the live site now (usually live within a minute or two).\n\n"
            f"  “{directive}”\n\n"
            f"You'll see it in the next growth update too.\n— {C.FROM_NAME}")
    html = (f'<!doctype html><html><body style="margin:0;background:{C._PAPER};">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{C._PAPER};padding:20px 0;"><tr><td align="center">'
            f'<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:{C._CARD};border:1px solid {C._LINE};border-radius:14px;overflow:hidden;">'
            f'<tr><td style="height:4px;background:{C._GREEN};"></td></tr>'
            f'<tr><td style="padding:18px 24px 6px;"><div style="font-family:{C._SERIF};color:{C._INK};font-size:19px;font-weight:700;">Merged &mdash; it\'s shipping</div>'
            f'<div style="color:{C._INK};font-size:15px;font-style:italic;padding:8px 0 2px;">&ldquo;{C._esc(directive)}&rdquo;</div>'
            f'<div style="color:{C._MUTED};font-size:13px;padding:8px 0 4px;">Deploying to the live site now &mdash; usually live within a minute or two.<br>&mdash; {C.FROM_NAME}</div></td></tr>'
            f'</table></td></tr></table></body></html>')
    return _send_simple(subject, body, html, bid, verbose=verbose)


if __name__ == "__main__":
    send_daily()
