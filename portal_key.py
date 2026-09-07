"""Print the key the investor portal's link should carry.

Usage::

    python portal_key.py <the PORTAL_PASSCODE you set in Streamlit secrets>

Prints the keyed hash the app accepts as ``?k=<key>`` on its URL. Put that
link behind the portal's button (the portal is logged-in, so the link stays
with the people who should have it); investors clicking it never see a code
prompt. Change the code in the secrets and every old link and cookie expires.
"""
import hashlib
import hmac
import sys

if len(sys.argv) != 2:
    sys.exit(__doc__)
code = sys.argv[1].strip()
key = hmac.new(code.encode(), b"rbx-portal", hashlib.sha256).hexdigest()
print(f"?k={key}")
