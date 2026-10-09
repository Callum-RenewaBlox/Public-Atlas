"""Forward new Netlify form submissions to energy@renewablox.co.uk, through AgentMail.

Netlify stores every verified submission of the energy site's two forms (bill-check on
/business/, ppa-check on /generators/) but its own notification emails have not been
reaching the inbox, and on a credit-based plan they are one more thing that can stop. This
script is the route that does not depend on them: it asks Netlify's API for the site's
verified submissions, and sends each one the inbox has not yet seen as an email from
energy@renewablox.co.uk to itself — the same subject and details Netlify's notification
would have carried, plus a link to the submission and to any attached bill or statement.

"Already seen" is decided by the inbox itself: every email this script sends carries the
submission's number in its subject ("[bill-check #3]"), and before sending it lists the
inbox's messages with that subject. So the inbox is the only state there is; running this
twice sends nothing twice, and a run that cannot read the inbox sends nothing at all.

Runs on a schedule in GitHub Actions (.github/workflows/forward-form-submissions.yml) with
two repository secrets, and does nothing until both exist:
    NETLIFY_AUTH_TOKEN   a Netlify personal access token (user settings > Applications)
    AGENTMAIL_API_KEY    an AgentMail API key (console.agentmail.to)
Run by hand:  NETLIFY_AUTH_TOKEN=... AGENTMAIL_API_KEY=... python tools/forward_form_submissions.py
Standard library only.
"""
import html
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

SITE_ID = "ddab5026-9c37-430b-b6c2-e2618ed9f7d0"          # renewablox-energy
INBOX = "energy@renewablox.co.uk"
NETLIFY = "https://api.netlify.com/api/v1"
AGENTMAIL = "https://api.agentmail.to/v0"
MAX_AGE_DAYS = 30                                           # older submissions are left alone

# the forms, and what each is about (the subject's wording and the attachment's name)
FORMS = {
    "bill-check": {"what": "Bill check", "doc": "bill"},
    "ppa-check": {"what": "PPA check", "doc": "PPA statement"},
}


def call(url, token, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Authorization": f"Bearer {token}", "Accept": "application/json",
                                          **({"Content-Type": "application/json"} if data else {})})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            text = r.read().decode()
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{method} {url} -> HTTP {e.code}: {e.read().decode()[:500]}")


def submissions(token):
    """The site's verified submissions, newest first (Netlify leaves spam out by default)."""
    out, page = [], 1
    while True:
        batch = call(f"{NETLIFY}/sites/{SITE_ID}/submissions?per_page=100&page={page}", token)
        out += batch
        if len(batch) < 100:
            return out
        page += 1


def seen(key, number, form):
    """Has the inbox already got the email for this submission? (its subject carries the tag)"""
    q = urllib.parse.urlencode({"subject": tag(form, number), "limit": 5})
    found = call(f"{AGENTMAIL}/inboxes/{INBOX}/messages?{q}", key)
    return bool(found.get("messages"))


def tag(form, number):
    return f"[{form} #{number}]"


def when(iso):
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    except Exception:
        return iso


def email_for(s):
    form = s.get("form_name", "")
    f = FORMS.get(form, {"what": form or "Form", "doc": "document"})
    d = s.get("data") or {}
    number = s.get("number")
    sender = (d.get("email") or s.get("email") or "").strip()
    rows = [(x.get("title") or x.get("name"), x.get("value")) for x in (s.get("ordered_human_fields") or [])
            if x.get("name") not in ("subject", "bot-field", "bill", "ppa_statement") and x.get("value")]
    attached = d.get("bill") or d.get("ppa_statement") or ""
    # Netlify stores an uploaded file at a URL of its own
    link = attached if isinstance(attached, str) and attached.startswith("http") else ""
    subject = f"{tag(form, number)} {d.get('subject') or s.get('summary') or f['what']}"
    lines = [f"{f['what']} from energy.renewablox.co.uk — submission #{number}, {when(s.get('created_at', ''))}", ""]
    lines += [f"{k}: {v}" for k, v in rows]
    if link:
        lines += ["", f"Attached {f['doc']}: {link}"]
    lines += ["", f"Reply to: {sender}" if sender else "",
              f"On Netlify: https://app.netlify.com/projects/renewablox-energy/forms/{s.get('form_id', '')}",
              f"Site: {s.get('site_url', '')}  ·  from {d.get('referrer', '')}"]
    text = "\n".join(x for x in lines if x is not None)
    table = "".join(f"<tr><td style='padding:4px 12px 4px 0;color:#61717a'>{html.escape(str(k))}</td>"
                    f"<td style='padding:4px 0'><b>{html.escape(str(v))}</b></td></tr>" for k, v in rows)
    body_html = (f"<div style='font-family:Inter,Segoe UI,Arial,sans-serif;font-size:15px;color:#0d1b23'>"
                 f"<p style='margin:0 0 12px'><b>{html.escape(f['what'])}</b> from energy.renewablox.co.uk — submission #{number}, {html.escape(when(s.get('created_at', '')))}</p>"
                 f"<table style='border-collapse:collapse'>{table}</table>"
                 + (f"<p><a href='{html.escape(link)}'>Attached {html.escape(f['doc'])}</a></p>" if link else "")
                 + (f"<p>Reply to: <a href='mailto:{html.escape(sender)}'>{html.escape(sender)}</a></p>" if sender else "")
                 + f"<p style='color:#61717a;font-size:13px'><a href='https://app.netlify.com/projects/renewablox-energy/forms/{html.escape(str(s.get('form_id', '')))}'>On Netlify</a></p></div>")
    return {"to": [INBOX], "subject": subject, "text": text, "html": body_html}


def main():
    netlify, agentmail = os.environ.get("NETLIFY_AUTH_TOKEN"), os.environ.get("AGENTMAIL_API_KEY")
    if not netlify or not agentmail:
        print("NETLIFY_AUTH_TOKEN and AGENTMAIL_API_KEY are not both set; nothing to do.")
        return
    subs = submissions(netlify)
    now = datetime.now(timezone.utc)
    recent = []
    for s in subs:
        try:
            age = (now - datetime.fromisoformat(s["created_at"].replace("Z", "+00:00"))).days
        except Exception:
            age = 0
        if age <= MAX_AGE_DAYS and s.get("form_name") in FORMS:
            recent.append(s)
    print(f"{len(subs)} verified submissions on the site; {len(recent)} from the last {MAX_AGE_DAYS} days on the two forms")
    sent = 0
    for s in sorted(recent, key=lambda x: x.get("created_at", "")):
        form, number = s.get("form_name"), s.get("number")
        if seen(agentmail, number, form):
            continue
        msg = email_for(s)
        call(f"{AGENTMAIL}/inboxes/{INBOX}/messages/send", agentmail, "POST", msg)
        print(f"sent {tag(form, number)}: {msg['subject'][:90]}")
        sent += 1
    print(f"{sent} forwarded, {len(recent) - sent} already in the inbox")


if __name__ == "__main__":
    sys.exit(main())
