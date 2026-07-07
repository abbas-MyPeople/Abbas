"""
growth_engine.inbox — READ the owner's reply (ported from seo_engine.inbox, retargeted to AZ).

IMAP + the business Gmail app password (stdlib imaplib). Finds the reply to the latest batch (matches our
Message-ID in In-Reply-To/References, or the [batch id] subject tag) and FAILS CLOSED on sender: the From
must be the single AZ owner allowlist, else it's ignored and an alert is raised. No reply → nothing happens.
Credential-guarded: no secret → no-op. Kill switch: ENGINE_DISABLED=1 → no-op.
"""
from __future__ import annotations
import os, json, email, imaplib
from . import model

IMAP_HOST = "imap.gmail.com"
# Single allowed approver — fail closed. (AZ Restaurant Partners owner.)
OWNER_ALLOWLIST = {"azoeb27@gmail.com"}
BATCH_FILE = model.STATE / "batches.jsonl"
DECISIONS = model.STATE / "decisions.jsonl"


def _disabled() -> bool:
    return os.environ.get("ENGINE_DISABLED") == "1"


def _creds():
    return os.environ.get("WK_ENGINE_EMAIL"), os.environ.get("WK_ENGINE_APP_PASSWORD")


def _latest_batch():
    rows = model.load(BATCH_FILE)
    return rows[-1] if rows else None


def _addr(raw):
    return (email.utils.parseaddr(raw or "")[1] or "").lower()


def _body_text(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition")):
                return part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "replace")
        return ""
    return msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", "replace")


def fetch_reply(verbose: bool = True) -> dict | None:
    """Return {batch_id, from, text, verified} for the owner's reply to the latest batch, or None."""
    if _disabled():
        if verbose:
            print("inbox: ENGINE_DISABLED=1 — no-op.")
        return None
    email_addr, app_pw = _creds()
    if not (email_addr and app_pw):
        if verbose:
            print("inbox: no WK_ENGINE_EMAIL/APP_PASSWORD — skipping reply read.")
        return None
    batch = _latest_batch()
    if not batch:
        if verbose:
            print("inbox: no batch sent yet — nothing to match a reply to.")
        return None

    try:
        M = imaplib.IMAP4_SSL(IMAP_HOST)
        M.login(email_addr, app_pw)
        M.select("INBOX")
        typ, data = M.search(None, "TEXT", f'"{batch["batch_id"]}"')
        ids = data[0].split() if data and data[0] else []
        for mid in reversed(ids):                        # newest first
            typ, md = M.fetch(mid, "(RFC822)")
            msg = email.message_from_bytes(md[0][1])
            frm = _addr(msg.get("From"))
            refs = (msg.get("In-Reply-To", "") + " " + msg.get("References", ""))
            subj = msg.get("Subject") or ""
            own_id = msg.get("Message-ID", "") or ""
            bmid = batch.get("message_id", "")
            # Send-to-self: our OWN outbound is in this inbox too — never treat it as a reply.
            if bmid and bmid in own_id:
                continue
            is_reply = (bmid and bmid in refs) or (subj.strip().lower().startswith("re:")
                                                   and batch["batch_id"] in subj)
            if not is_reply:
                continue
            verified = frm in OWNER_ALLOWLIST
            text = _body_text(msg)
            M.logout()
            if not verified:
                model.finding("G_sec_reply", f"batch:{batch['batch_id']}", "alert", "bad",
                              "Reply to the daily brief from an unrecognized sender — ignored",
                              detail="Not on the owner allowlist. Nothing was actioned (fail-closed).")
                if verbose:
                    print("inbox: reply from UNVERIFIED sender — ignored (fail-closed).")
                return None
            if verbose:
                print(f"inbox: verified reply to batch {batch['batch_id']}.")
            return {"batch_id": batch["batch_id"], "from": frm, "text": text, "verified": True}
        M.logout()
    except Exception as e:
        if verbose:
            print(f"inbox: read failed ({type(e).__name__}) — nothing actioned.")
        return None

    if verbose:
        print(f"inbox: no reply yet to batch {batch['batch_id']}.")
    return None


def record_decisions(batch_id, parsed):
    DECISIONS.parent.mkdir(parents=True, exist_ok=True)
    rec = {"ts": model.now(), "batch_id": batch_id, "global": parsed.get("global_"),
           "items": parsed.get("items"), "ambiguous": parsed.get("ambiguous")}
    # Frequent reads see the same reply repeatedly — don't append a duplicate decision.
    existing = model.load(DECISIONS)
    if existing:
        last = existing[-1]
        if (last.get("batch_id") == rec["batch_id"] and last.get("items") == rec["items"]
                and last.get("global") == rec["global"]):
            return last
    with DECISIONS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec
