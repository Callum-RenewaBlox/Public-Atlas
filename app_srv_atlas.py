"""SRV Atlas — Scrivelsby (Home Farm AD) electrical site survey.

A standalone Leaflet site-survey map of the Home Farm AD site at Scrivelsby
(LN9 6JB, operator Qila Energy): site assets (CHP, transformer, LV switchroom,
proposed compute load bank), geolocated site photos, and grid/site context.

One app, three views — the same shape as ``app_kld_atlas.py``, so the site
atlases behave identically and a new site is a copy of either:

* default — the map (``srv_atlas.html``), carrying two pulsing BLOX badges on
  the yard, each with a standing call to action.
* ``?view=3d`` — the 3D Dispatch Sim (``srv_3d_sim.html``): the peaker model
  over a real metered year.
* ``?view=siting`` — the 3D Siting Options (``srv_siting_3d.html``): the
  410 kW load bank container and its dry cooler placed four ways, A–D.

A badge navigates the whole page to its route rather than opening an overlay,
so the map page stays light and each model gets the entire browser window;
every model page carries its own "Atlas" control to come back. The badge
layer lives in ``srv_atlas_3d_badge.html`` (built by
``Contracts/Scrivelsby Farm Ltd/Atlas/build_srv_atlas_badge.py``) and is
appended at serve time, so the generated map file stays pristine. The model
pages come from ``build_srv_3d_sim.py`` and ``build_srv_siting_3d.py`` in the
same folder.

Self-contained: every view reads local HTML (Leaflet / three.js, all data and
photos embedded) and renders via ``st.iframe``. No database, no secrets.

Public tool. Run locally:  streamlit run app_srv_atlas.py
"""
from pathlib import Path

import streamlit as st

HERE = Path(__file__).resolve().parent

VIEWS = {
    "3d":     ("srv_3d_sim.html",    "SRV Atlas — 3D Dispatch Sim"),
    "siting": ("srv_siting_3d.html", "SRV Atlas — 3D Siting Options"),
}
# read before set_page_config so the tab title can follow the route
view = st.query_params.get("view", "")
if view not in VIEWS:
    view = ""

st.set_page_config(
    page_title=VIEWS[view][1] if view else "SRV Atlas — Scrivelsby",
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
    html = (HERE / "srv_atlas.html").read_text(encoding="utf-8")
    badge = HERE / "srv_atlas_3d_badge.html"
    if badge.exists():
        html = html.replace("</body>", badge.read_text(encoding="utf-8") + "\n</body>", 1)

st.iframe(html, height=900)
