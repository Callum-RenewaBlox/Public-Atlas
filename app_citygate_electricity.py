"""Citygate Church — Electricity Portrait.

Fourteen months of half-hourly meter readings for Citygate Church (138a
Holdenhurst Road, Bournemouth), told in plain English for the church's
leaders: the whole year in one picture, a typical week, where the electricity
goes, the seasons, the size of the grid connection and what the data could be
worth, with a short version up top and a sensible order to act in.

Self-contained: reads ``citygate_electricity.html`` (hand-authored; Inter, the
wordmark and the meter data inlined, no CDN, no requests) and renders it via
``st.iframe``, where its charts and tooltips run. No database, no secrets.

Client-facing. Run locally:  streamlit run app_citygate_electricity.py
"""
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="RenewaBlox — Citygate Church · Electricity Portrait",
    page_icon=":material/electric_bolt:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# The page is the whole app: strip Streamlit's chrome and padding so it fills
# the viewport and scrolls inside its own frame, keeping its house header
# pinned at the top.
st.markdown(
    """
    <style>
      [data-testid="stHeader"], [data-testid="stToolbar"],
      [data-testid="stDecoration"], [data-testid="stStatusWidget"],
      [data-testid="stBottomBlockContainer"], footer {display:none !important;}
      [data-testid="stAppViewContainer"] {overflow:hidden !important;}
      /* stMain scrolls by default and reserves a scrollbar gutter, which would
         leave a dead strip down the right-hand edge of a full-bleed page */
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

# Read the page fresh from the main script each run (Streamlit re-runs this
# script but can keep imported modules cached, so reading here keeps the
# embedded page current after every redeploy).
PAGE = (Path(__file__).resolve().parent / "citygate_electricity.html").read_text(
    encoding="utf-8")

# Nothing after the iframe: it owns the full 100dvh and stMain is
# overflow:hidden, so anything rendered below it could never be scrolled to.
st.iframe(PAGE, height=900)
