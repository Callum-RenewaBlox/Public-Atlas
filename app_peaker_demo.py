"""Peaker Demo — Peaker Plant 3D on its own link.

The Peaker Plant 3D model lifted out of the Investor Demo pack and served
standalone: one link, straight into the model, no landing page and no pack
navigation. Prices stay in £/MWh, exactly as the packs show them, so this is
the investor-facing peaker on a URL of its own — the pack keeps its Peaker
card too, this is an additional door, not a move.

Three apps serve ``peaker_plant_3d.html``; they differ only in framing:

* ``app_investor_demo.py`` (and ``_aus``) — inside the pack, £/MWh, pack bar.
* this app — standalone, £/MWh, no chrome.
* ``app_peaker_3d.py`` — standalone, **p/kWh** for the AD-operator brochure.

Self-contained: reads ``peaker_plant_3d.html`` (three.js, all data inlined —
no CDN, no database, no secrets), a byte-for-byte copy of the internal Atlas
3D build, and renders it full-bleed via ``st.iframe``.

Public tool. Run locally:  streamlit run app_peaker_demo.py
"""
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="RenewaBlox — Peaker Demo",
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
# embedded build current after every redeploy). The guided-tour view strip is
# dropped with a serve-time patch — the same one the packs apply — so the HTML
# stays a byte-for-byte upstream copy shared by all four peaker surfaces.
PEAKER_HTML = (Path(__file__).resolve().parent / "peaker_plant_3d.html").read_text(
    encoding="utf-8").replace(
    "</head>", "<style>#viewstrip{display:none !important;}</style></head>", 1)

st.iframe(PEAKER_HTML, height=900)
