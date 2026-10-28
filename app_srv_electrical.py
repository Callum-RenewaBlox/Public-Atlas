"""SRV Electrical — the LV connection at Scrivelsby (Home Farm AD), drawn two ways.

Paktronic's quoted changeover board (LF42344) set against the shared-busbar
design RenewaBlox needs, for the Home Farm AD site at Scrivelsby (LN9 6JB,
operator Qila Energy). Two main tabs in the brand bar, opening on the first:

* **Single-line diagram** — the animated SLD (``srv_electrical/sld.html``):
  the DNO transformer, the existing 2014 board, the new board with the CHP's
  generator breaker, and the data-centre section with its racks, cooler and
  CDU, power drawn flowing in engine orange or grid blue.
* **Site view** — the same scheme on the September 2026 Scrivelsby site model
  (``srv_electrical/site3d.html`` with ``static/srv_electrical/site.glb``):
  the GRP kiosk with both boards back to back, the data-centre container under
  the cooler gantry, and the cable routes carrying the power, with a status
  pill on each asset.

Each view has the same two sub-tabs, **What Lee designed** (the quote as
drawn: two 1250 A ACBs, mechanically interlocked, so the engine feeds the site
or the data centre, never both) and **What we need** (the interlock removed,
the miners turned down in software, and a hardwired trip that drops the racks
if the engine stops), and each sub-tab steps through three operating states.
The design and state picked in one view carry over when the other is opened.
On What we need, each view also carries the change list for LF42344, "What we
need, step by step" (``srv_electrical/what_we_need.js``, one copy inlined into
both pages): eleven numbered steps with their owners, what stays as quoted,
and what we confirm before ordering. It starts collapsed behind a call to
action, a "Step-by-step (11)" button: on the SLD it opens a card under the
diagram, on the site view a card pinned top right from 1280 px, with the
scene re-centred between the two cards (a bottom sheet below that). Each step
opens up (``srv_electrical/steps_explained.js``): what's needed as numbered
points, why, and done when, shown on the diagram with its parts lit and
numbered markers where each point applies, and on the site with the camera
flown there, the equipment outlined and the points pinned. The step open in
one view is open in the other. A glossary of the key terms and acronyms
(``srv_electrical/glossary.js``) sits under both views.

The bar and the two frames are ``srv_electrical/shell.html``; this script
fills it at serve time with the two pages, so the sources in
``srv_electrical/`` are edited in place with no build step. The site view is
only built into its frame the first time it is opened, and only then fetches
its 3 MB model, which Streamlit serves from ``static/`` (``enableStaticServing``
in ``.streamlit/config.toml``), so the page it opens on stays light. Deep
links: ``?view=site`` opens on the site view, ``?design=what-we-need`` on the
second sub-tab, ``?state=2`` on that operating state (1 to 3), ``?step=4`` on
that step of What we need, opened up (1 to 11).

three.js and the fonts load from CDNs. No database, no secrets.

Run locally:  streamlit run app_srv_electrical.py
"""
import json
import re
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
      /* the shell's own background, light or dark, so nothing flashes while it loads */
      html, body, .stApp {overflow:hidden !important; background:#eef2f5 !important;}
      @media (prefers-color-scheme: dark) {
          html, body, .stApp {background:#11161c !important;}}
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
if params.get("step") in [str(n) for n in range(1, 12)]:
    query["step"] = int(params.get("step")) - 1

# Read fresh from the main script each run (Streamlit re-runs this script but
# can keep imported modules cached, so reading here keeps the pages current
# after every redeploy).
# The data both pages share (the step list, each step opened up, and the
# glossary): one copy of each, inlined as the data script each page keeps for
# them. None of it may end that script early.
DATA_FILES = ("what_we_need.js", "steps_explained.js", "glossary.js")
data = []
for name in DATA_FILES:
    text = (SRC / name).read_text(encoding="utf-8")
    if re.search(r"</script|<!--", text, re.IGNORECASE):
        raise RuntimeError(f"{name} must not contain </script or <!--")
    data.append(text)
data = "\n".join(data)
sld = fill((SRC / "sld.html").read_text(encoding="utf-8"), "/*__WHAT_WE_NEED__*/", data)
site = fill((SRC / "site3d.html").read_text(encoding="utf-8"), "/*__WHAT_WE_NEED__*/", data)
html = (SRC / "shell.html").read_text(encoding="utf-8")
html = fill(html, "__LV_QUERY__", json.dumps(query))
html = fill(html, "__SLD_JSON__", script_json(sld))
html = fill(html, "__SITE_JSON__", script_json(site))

st.iframe(html, height=900)
