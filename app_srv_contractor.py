"""SRV Contractor Atlas — Scrivelsby (Home Farm AD) electrical site survey.

The contractor-facing survey map for the Home Farm AD site at Scrivelsby
(LN9 6JB, operator Qila Energy). Built to accompany the LV connection RFQ:
site assets with switchgear detail, the full geolocated photo survey including
switchroom interiors, the proposed LV feeder route with its tie-in and
containment notes, and OSM/DNO context layers.

Self-contained: reads ``srv_contractor.html`` (Leaflet from a CDN, all data and
photos embedded) and renders it via ``st.iframe``. No database, no secrets.

Contractor-facing. The client-facing minimalist version is ``app_srv_atlas.py``.
Run locally:  streamlit run app_srv_contractor.py
"""
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="SRV Contractor Atlas",
    page_icon=":material/construction:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Read the map fresh from the main script each run (Streamlit re-runs this
# script but can keep imported modules cached, so reading here keeps the
# embedded map current after every redeploy). The HTML carries its own brand
# bar, map, layer controls and legend, so the Streamlit chrome stays minimal.
# The map is the whole page: strip Streamlit's chrome and padding so the atlas
# fills the viewport and the brand bar stays pinned in view instead of
# scrolling away with the page (the HTML positions its own bar, controls and
# labels absolutely inside it).
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

SRV_HTML = (Path(__file__).resolve().parent / "srv_contractor.html").read_text(
    encoding="utf-8")

st.iframe(SRV_HTML, height=900)
st.caption(
    "RenewaBlox · Scrivelsby Contractor Atlas — Home Farm AD electrical site "
    "survey · contact callum@renewablox.com")
