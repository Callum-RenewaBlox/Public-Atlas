"""Print the key the investor portal's link should carry.

Usage::

    python portal_key.py <the PORTAL_PASSCODE set on the renewablox-atlas Netlify project>

Prints the keyed hash the portal's gate (atlas/netlify/edge-functions/portal-gate.js)
accepts as ``?k=<key>`` on its address. Put that link behind the Wix portal's
button, https://atlas.renewablox.com/investors/portal/?k=<key> (the portal is
logged-in, so the link stays with the people who should have it); investors
clicking it never see a code prompt. Change PORTAL_PASSCODE and every old link
and cookie expires.
"""
import hashlib
import hmac
import sys

if len(sys.argv) != 2:
    sys.exit(__doc__)
code = sys.argv[1].strip()
key = hmac.new(code.encode(), b"rbx-portal", hashlib.sha256).hexdigest()
print(f"?k={key}")
