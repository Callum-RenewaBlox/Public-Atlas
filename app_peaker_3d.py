"""Peaker Plant 3D — standalone client link.

The RenewaBlox peaker business model as a living site, served on its own for
client brochures (built for AD operators): one link, straight into the model,
no landing page and no pack navigation. The scene carries its own header,
dispatch desk and price seesaw; the guided-tour view strip is hidden here,
matching the Investor Demo's presentation (``app_investor_demo.py``).

Self-contained: reads ``peaker_plant_3d.html`` (three.js, all data inlined —
no CDN, no database, no secrets), a byte-for-byte copy of the internal Atlas
3D build, and renders it full-bleed via ``st.iframe``.

Public tool. Run locally:  streamlit run app_peaker_3d.py
"""
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="RenewaBlox — Peaker Plant 3D",
    page_icon=":material/bolt:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# The model is the whole page: strip Streamlit's chrome and padding so it
# fills the viewport edge to edge. The HTML carries its own header, footer and
# floating panels, and lays itself out against the full iframe height.
st.markdown(
    """
    <style>
      [data-testid="stHeader"], [data-testid="stToolbar"],
      [data-testid="stDecoration"], [data-testid="stStatusWidget"],
      [data-testid="stBottomBlockContainer"], footer {display:none !important;}
      [data-testid="stAppViewContainer"] {overflow:hidden !important;}
      /* stMain scrolls by default and reserves a scrollbar gutter, which would
         leave a dead strip down the right-hand edge of a full-bleed scene */
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
      html, body, .stApp {overflow:hidden !important; background:#f4f8fa !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Read the scene fresh from the main script each run (Streamlit re-runs this
# script but can keep imported modules cached, so reading here keeps the
# embedded build current after every redeploy). Serve-time patches keep the
# HTML a byte-for-byte upstream copy shared with the investor packs: the
# guided-tour view strip is dropped, and PEAKER_UNITS switches every price on
# the page to p/kWh — the unit AD operators know — where the packs keep £/MWh.
PEAKER_HTML = (Path(__file__).resolve().parent / "peaker_plant_3d.html").read_text(
    encoding="utf-8").replace(
    "</head>",
    '<script>window.PEAKER_UNITS="p/kWh";</script>'
    "<style>#viewstrip{display:none !important;}</style></head>", 1)

st.iframe(PEAKER_HTML, height=900)
