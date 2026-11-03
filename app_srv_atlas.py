"""SRV Atlas — Scrivelsby (Home Farm AD) electrical site survey.

A standalone Leaflet map of the Home Farm AD site at Scrivelsby (LN9 6JB,
operator Qila Energy). The generated map file still draws the earlier scheme
(the asset pins and labels, the proposed cable route and the compute load bank
plot); that is out of date, so ``srv_atlas_clear.html`` takes it all off at
serve time and the map shows the satellite imagery and the three badges.

One app, four views — the same shape as ``app_kld_atlas.py``, so the site
atlases behave identically and a new site is a copy of either:

* default — the map (``srv_atlas.html``), carrying three pulsing BLOX badges on
  the yard, each with a standing call to action: 3D Dispatch Sim, 3D Compute
  Kiosk and ASIC Deployment.
* ``?view=3d`` — the 3D Dispatch Sim (``srv_3d_sim.html``): the peaker model
  over a real metered year.
* ``?view=siting`` — the 3D Compute Kiosk (``srv_siting_3d.html``): the two
  siting schemes on one page. Option A, one 4 m kiosk for the LV board, three
  DCX racks and their cooling loop with the dry cooler on the roof; option B,
  the existing kiosk extended for the board and the Winchain 10 ft hydro
  cooling container behind it with the dry cooler on the container roof.
* ``?view=fleet`` — the Miner Fleet (``srv_fleet_3d.html``): 40, 44 or 50
  miners on the same CHP surplus, as charts (2D) and as the Winchain container
  with every miner coloured by its overclock as the metered year replays (3D).
  ``#f44-3d`` and the like pick the fleet and the view.

A badge navigates the whole page to its route rather than opening an overlay,
so the map page stays light and each model gets the entire browser window;
every model page carries its own "Atlas" control to come back. The badge
layer lives in ``srv_atlas_3d_badge.html`` (built by
``Contracts/Scrivelsby Farm Ltd/Atlas/build_srv_atlas_badge.py``) and is
appended at serve time, so the generated map file stays pristine. The model
pages come from ``build_srv_3d_sim.py`` and ``siting/build_siting.py`` in the
same folder. The Miner Fleet has no builder yet: ``srv_fleet_3d.html`` is
edited in place. Its ways in are hand-maintained layers appended at serve time
too (``LAYERS``), so a rebuild of the generated pages cannot drop them: the
ASIC Deployment badge in ``srv_atlas_fleet_badge.html``, and the link under the
option text on the kiosk page in ``srv_siting_fleet_link.html``.

Self-contained: every view reads local HTML (Leaflet / three.js, all data and
photos embedded) and renders via ``st.iframe``. No database, no secrets.

Public tool. Run locally:  streamlit run app_srv_atlas.py
"""
from pathlib import Path

import streamlit as st

HERE = Path(__file__).resolve().parent

VIEWS = {
    "3d":     ("srv_3d_sim.html",    "SRV Atlas — 3D Dispatch Sim"),
    "siting": ("srv_siting_3d.html", "SRV Atlas — 3D Compute Kiosk"),
    "fleet":  ("srv_fleet_3d.html",  "SRV Atlas — Miner Fleet"),
}
# Layers appended to a page at serve time, in order, so the generated files
# stay pristine. On the map the clear-out goes first (it takes the generated
# page's out-of-date drawing off, so it must run before any badge is added),
# and the ASIC Deployment badge reuses the generated badge layer's styles, so
# it comes after that.
LAYERS = {
    "":       ("srv_atlas_clear.html", "srv_atlas_3d_badge.html", "srv_atlas_fleet_badge.html"),
    "siting": ("srv_siting_fleet_link.html",),
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
html = (HERE / (VIEWS[view][0] if view else "srv_atlas.html")).read_text(encoding="utf-8")
for name in LAYERS.get(view, ()):
    layer = HERE / name
    if layer.exists():
        html = html.replace("</body>", layer.read_text(encoding="utf-8") + "\n</body>", 1)

st.iframe(html, height=900)
