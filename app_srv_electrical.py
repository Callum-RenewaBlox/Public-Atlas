"""SRV Electrical — the LV connection at Scrivelsby (Home Farm AD), drawn two ways.

Paktronic's quoted changeover board (LF42344) set against the shared-busbar
design RenewaBlox needs, for the Home Farm AD site at Scrivelsby (LN9 6JB,
operator Qila Energy). Two main tabs in the brand bar, opening on the first:

* **Single-line diagram** — the animated SLD (``srv_electrical/sld.html``):
  the DNO transformer, the existing 2014 board, the new board with the CHP's
  generator breaker, and the data-centre section with its racks, cooler and
  CDU, power drawn flowing in engine orange or grid blue.
* **Site view** — the same scheme on the September 2026 Scrivelsby site model
  (``srv_electrical/site3d.template.html`` with ``srv_electrical/site.glb``):
  the GRP kiosk with both boards back to back, the data-centre container under
  the cooler gantry, and the cable routes carrying the power, with a status
  pill on each asset.

Each view has the same two sub-tabs, **What Lee designed** (the quote as
drawn: two 1250 A ACBs, mechanically interlocked, so the engine feeds the site
or the data centre, never both) and **What we need** (the interlock removed,
the miners turned down in software, and a hardwired trip that drops the racks
if the engine stops), and each sub-tab steps through three operating states.
The design and state picked in one view carry over when the other is opened.

The bar and the two frames are ``srv_electrical/shell.html``; this script
fills it at serve time with the two pages, the site model embedded in the
site view as base64, so the sources in ``srv_electrical/`` are edited in place
with no build step. The site view is only built into its frame the first time
it is opened. Deep links: ``?view=site`` opens on the site view,
``?design=what-we-need`` on the second sub-tab, ``?state=2`` on that
operating state (1 to 3).

Self-contained apart from three.js and the fonts, which load from CDNs. No
database, no secrets.

Run locally:  streamlit run app_srv_electrical.py
"""
import base64
import json
from pathlib import Path

import streamlit as st

SRC = Path(__file__).resolve().parent / "srv_electrical"

st.set_page_config(
    page_title="SRV Electrical — Scrivelsby LV connection",
    page_icon=":material/electrical_services:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# The page is the whole viewport: strip Streamlit's chrome and padding so the
# iframe owns the full height (the shell positions its own brand bar, and each
# view lays itself out against the frame below it).
st.markdown(
    """
    <style>
      [data-testid="stHeader"], [data-testid="stToolbar"],
      [data-testid="stDecoration"], [data-testid="stStatusWidget"],
      [data-testid="stBottomBlockContainer"], footer {display:none !important;}
      [data-testid="stAppViewContainer"] {overflow:hidden !important;}
      /* stMain scrolls by default and reserves a scrollbar gutter, which would
         leave a dead strip down the right-hand edge of a full-bleed page */
      [data-testid="stMain"] {overflow:hidden !important; height:100dvh !important;}
      [data-testid="stMain"] .block-container,
      [data-testid="stMainBlockContainer"], .block-container {
          padding:0 !important; margin:0 !important; max-width:100% !important;}
      [data-testid="stVerticalBlock"], [data-testid="stVerticalBlockBorderWrapper"] {
          gap:0 !important;}
      [data-testid="stElementContainer"], [data-testid="element-container"] {
          width:100% !important;}
      [data-testid="stIFrame"] {
          height:100dvh !important; width:100% !important; display:block; border:0;}
      html, body, .stApp {overflow:hidden !important; background:#0d1b23 !important;}
    </style>
    """,
    unsafe_allow_html=True,
)


def script_json(text):
    """``text`` as a JSON string literal that is inert inside a <script> element.

    Escaping ``<``, ``>`` and ``&`` keeps ``</script>`` and ``<!--`` in the
    embedded pages from ending or re-parsing the element they ride in.
    """
    return (json.dumps(text)
            .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026"))


def fill(page, marker, value):
    """Replace the one ``marker`` in ``page``; fail loudly if it is not there once."""
    if page.count(marker) != 1:
        raise RuntimeError(f"{marker} should appear exactly once")
    return page.replace(marker, value)


# Deep links, read from the app's own query string (the shell sits in an
# about:srcdoc frame and cannot see it) and passed in as known values only.
params = st.query_params
query = {}
if params.get("view") == "site":
    query["view"] = "site"
if params.get("design") in ("what-we-need", "ours"):
    query["design"] = "ours"
if params.get("state") in ("1", "2", "3"):
    query["state"] = int(params.get("state")) - 1

# Read fresh from the main script each run (Streamlit re-runs this script but
# can keep imported modules cached, so reading here keeps the pages current
# after every redeploy).
sld = (SRC / "sld.html").read_text(encoding="utf-8")
site = fill((SRC / "site3d.template.html").read_text(encoding="utf-8"), "__GLB_B64__",
            base64.b64encode((SRC / "site.glb").read_bytes()).decode("ascii"))
html = (SRC / "shell.html").read_text(encoding="utf-8")
html = fill(html, "__LV_QUERY__", json.dumps(query))
html = fill(html, "__SLD_JSON__", script_json(sld))
html = fill(html, "__SITE_JSON__", script_json(site))

st.iframe(html, height=900)
