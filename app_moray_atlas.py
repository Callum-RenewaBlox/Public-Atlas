"""Moray Cluster Atlas — Keith & Huntly primaries (Savills Earth screen).

A standalone Leaflet atlas of the RenewaBlox Moray cluster: the only two
green-headroom primaries in the Savills Moray screen (Keith 6.42 MVA, Huntly
8.08 MVA), the BLOX candidate plots digitised from the Savills pack, ownership
areas and evidence pins, GSP saturation, the real 33/132/275/400 kV and HVDC
geometry around them, and the offshore/onshore wind that lands on it.

Self-contained: reads ``moray_atlas.html`` (all data embedded, Leaflet from
CDN — no database, no secrets) and renders it full-bleed via ``st.iframe``.
Rebuild that file from the working map with
``Contracts/Savills Earth/Atlas/build_moray_atlas.py``.

Run locally:  streamlit run app_moray_atlas.py
"""
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Moray Cluster Atlas — Keith & Huntly",
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
# bar, briefing panel, layer control and legend, so nothing else is rendered
# around it.
MORAY_HTML = (Path(__file__).resolve().parent / "moray_atlas.html").read_text(
    encoding="utf-8")

st.iframe(MORAY_HTML, height=900)
