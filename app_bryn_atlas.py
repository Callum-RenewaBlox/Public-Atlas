"""Bryn Atlas — Bryn Power AD plant (Gelliargwellt Farm, Gelligaer).

A standalone Leaflet map of the Bryn Power anaerobic-digestion site at
Gelliargwellt Farm, Gelligaer (CF82 8FY), showing where a BLOX data centre
would stand: on the yard a few metres from the LV room at the CHP engines,
where it would take about 200 kW of the site's surplus power by a short
connection, with no cable route across the site.

One app, two views — the same shape as ``app_srv_atlas.py`` and
``app_kld_atlas.py``, so the site atlases behave identically and a new site is
a copy of any of them:

* default — the map (``bryn_atlas.html``), carrying a pulsing BLOX badge on the
  proposed plot with a standing call to action.
* ``?view=3d`` — the 3D Site Model (``bryn_3d_sim.html``): a model of the plant
  with the data centre in place by the LV room, and the three ways of funding
  it (RBX CapEx, 50/50, Bryn CapEx) drawn from the revenue-share model. This
  site is surplus power to compute, not peaker arbitrage, so there is no
  dispatch desk.

The badge navigates the whole page to its route rather than opening an
overlay, so the map page stays light and the model gets the entire browser
window; the model page carries its own "Atlas" control to come back. The badge
layer lives in ``bryn_atlas_3d_badge.html`` and is appended at serve time, so
the generated map file stays pristine.

Self-contained: both views read local HTML (Leaflet / three.js, all data
embedded) and render via ``st.iframe``. No database, no secrets.

Public tool. Run locally:  streamlit run app_bryn_atlas.py
"""
from pathlib import Path

import streamlit as st

HERE = Path(__file__).resolve().parent

VIEWS = {
    "3d": ("bryn_3d_sim.html", "Bryn Atlas — 3D Site Model"),
}
# read before set_page_config so the tab title can follow the route
view = st.query_params.get("view", "")
if view not in VIEWS:
    view = ""

st.set_page_config(
    page_title=VIEWS[view][1] if view else "Bryn Atlas — Bryn Power AD plant",
    page_icon=":material/map:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Every view is the whole page: strip Streamlit's chrome and padding so the
# iframe owns the full viewport (each page positions its own brand bar, panels
# and controls absolutely inside it).
st.markdown(
    """
    <style>
      [data-testid="stHeader"], [data-testid="stToolbar"],
      [data-testid="stDecoration"], [data-testid="stStatusWidget"],
      [data-testid="stBottomBlockContainer"], footer {display:none !important;}
      [data-testid="stAppViewContainer"] {overflow:hidden !important;}
      /* stMain scrolls by default and reserves a scrollbar gutter, which would
         leave a dead strip down the right-hand edge of a full-bleed map */
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

# Read fresh from the main script each run (Streamlit re-runs this script but
# can keep imported modules cached, so reading here keeps the embedded pages
# current after every redeploy).
if view:
    html = (HERE / VIEWS[view][0]).read_text(encoding="utf-8")
else:
    html = (HERE / "bryn_atlas.html").read_text(encoding="utf-8")
    badge = HERE / "bryn_atlas_3d_badge.html"
    if badge.exists():
        html = html.replace("</body>", badge.read_text(encoding="utf-8") + "\n</body>", 1)

st.iframe(html, height=900)
