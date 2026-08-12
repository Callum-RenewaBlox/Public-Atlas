"""SRV 3D Sim — the Scrivelsby Peaker, Home Farm AD (Horncastle LN9 6JB).

A three.js model of the site wrapped around a half-hourly dispatch simulation:
the 499 kWe biogas CHP's 350 kW switchable block follows price — above the
strike it exports to the constrained 11 kV grid, below it the energy is
absorbed on site by the compute load bank. Drive it from the dispatch desk
over a real metered year, or step the annual table half-hour by half-hour.

Every asset pin carries the electrical site survey photography from the 2D SRV
Atlas — thumbnails in the asset card, full frames in a lightbox with the
original caption, capture date and camera bearing.

Self-contained: reads ``srv_3d_sim.html`` (three.js, the site GLB, a metered
year of prices and all 12 photographs inlined — no CDN, no database, no
secrets) and renders it full-bleed via ``st.iframe``. Rebuild that file from
the working scene with
``Contracts/Scrivelsby Farm Ltd/Atlas/build_srv_3d_sim.py``.

Public tool. Run locally:  streamlit run app_srv_3d_sim.py
"""
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="SRV 3D Sim — Scrivelsby Peaker",
    page_icon=":material/bolt:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# The simulator is the whole page: strip Streamlit's chrome and padding so it
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
      html, body, .stApp {overflow:hidden !important; background:#0d1b23 !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Read the scene fresh from the main script each run (Streamlit re-runs this
# script but can keep imported modules cached, so reading here keeps the
# embedded build current after every redeploy).
SRV_HTML = (Path(__file__).resolve().parent / "srv_3d_sim.html").read_text(
    encoding="utf-8")

st.iframe(SRV_HTML, height=900)
