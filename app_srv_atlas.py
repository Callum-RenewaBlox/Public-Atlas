"""SRV Atlas — Scrivelsby (Home Farm AD) electrical site survey.

A standalone Leaflet site-survey map of the Home Farm AD site at Scrivelsby
(LN9 6JB, operator Qila Energy): site assets (CHP, transformer, LV switchroom,
proposed compute load bank), geolocated site photos, and grid/site context.

One app, two views. The atlas carries a pulsing BLOX badge over the yard;
clicking it opens the SRV 3D Sim in a full-screen overlay whose iframe loads
this same app at ``?view=3d`` — so the atlas page stays light and the sim's
5.8 MB boots only when summoned. The badge layer lives in
``srv_atlas_3d_badge.html`` (built by
``Contracts/Scrivelsby Farm Ltd/Atlas/build_srv_atlas_badge.py``) and is
appended at serve time, so the hand-maintained map file stays pristine.

Self-contained: both views read local HTML (Leaflet / three.js, all data and
photos embedded) and render via ``st.iframe``. No database, no secrets.

Public tool. Run locally:  streamlit run app_srv_atlas.py
"""
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="SRV Atlas",
    page_icon=":material/map:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Both views are the whole page: strip Streamlit's chrome and padding so the
# iframe owns the full viewport (the HTML positions its own brand bar, panels
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

HERE = Path(__file__).resolve().parent

# Read fresh from the main script each run (Streamlit re-runs this script but
# can keep imported modules cached, so reading here keeps the embedded pages
# current after every redeploy).
if st.query_params.get("view") == "3d":
    # The sim view — reached from the badge overlay's iframe (?view=3d&embed=true)
    # or directly for a full-screen tab.
    html = (HERE / "srv_3d_sim.html").read_text(encoding="utf-8")
else:
    html = (HERE / "srv_atlas.html").read_text(encoding="utf-8")
    badge = HERE / "srv_atlas_3d_badge.html"
    if badge.exists():
        html = html.replace("</body>", badge.read_text(encoding="utf-8") + "\n</body>", 1)

st.iframe(html, height=900)
