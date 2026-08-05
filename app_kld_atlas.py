"""KLD Atlas — Kinlochdamph 999 kW run-of-river hydro, Loch Damh (Wester Ross).

A standalone Leaflet atlas of the built-but-stranded Kinlochdamph scheme: site
assets georeferenced from the construction drawings, the 11/33/132 kV network
around it, the two SSEN connection options (1 km at 50 kW vs 7.8 km at 999 kW),
the embedded-hydro fleet already on the same radial, and an interactive 3D
model of the powerhouse with the proposed co-located data centre.

Self-contained: reads ``kld_atlas.html`` (Leaflet, Google model-viewer and the
powerhouse GLB all inlined — no CDN, no database, no secrets) and renders it
full-bleed via ``st.iframe``. Rebuild that file from the working atlas with
``Contracts/Kinlochdamph/Atlas/build_kld_atlas.py``.

Public tool. Run locally:  streamlit run app_kld_atlas.py
"""
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="KLD Atlas — Kinlochdamph",
    page_icon=":material/hub:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# The map is the whole page: strip Streamlit's chrome and padding so the atlas
# fills the viewport edge to edge, and let the iframe own the full height (the
# HTML positions its own panel, controls and legend absolutely inside it).
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

# Read the map fresh from the main script each run (Streamlit re-runs this
# script but can keep imported modules cached, so reading here keeps the
# embedded map current after every redeploy). The HTML carries its own brand
# bar, briefing panel, layer controls, legend and 3D viewer, so nothing else
# is rendered around it.
KLD_HTML = (Path(__file__).resolve().parent / "kld_atlas.html").read_text(
    encoding="utf-8")

st.iframe(KLD_HTML, height=900)
