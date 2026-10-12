"""Keith & Huntly Atlas — SSEN's budget estimates for a BLOX connection at each primary.

A standalone three.js page: the Keith and Huntly primary substations (the
two green-headroom primaries in the Savills Moray screen) on satellite
imagery, with SSEN's proposed connection works and Savills' siting options
drawn on each, and a guided, decision-first panel telling the same story
SSEN's two budget estimates tell -- what each figure buys, what it leaves
out, and what it costs to take either site to the next step.

Self-contained: reads ``kh_atlas.html`` (all data and the three.js bundle
embedded -- no database, no secrets, no requests) and renders it full-bleed
via ``st.iframe``. Rebuild that file from the working page with
``Contracts/Savills Earth/Atlas/build_kh_atlas.py``.

Deep links the page understands: ``?beat=5`` (or ``?step=huntly``) opens on
that step of the story (``decision`` is the opening ladder, ``decide`` the
closing one), ``?site=huntly`` opens on Huntly's figure, ``?still`` skips the
flights.

Run locally:  streamlit run app_kh_atlas.py
"""
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Keith & Huntly Atlas",
    page_icon=":material/bolt:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# The page is the whole viewport: strip Streamlit's chrome and padding so the
# atlas fills it edge to edge, and let the iframe own the full height (the
# HTML positions its own header, panels and controls inside it).
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
      html, body, .stApp {overflow:hidden !important; background:#0d1b23 !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Read fresh from the main script each run (Streamlit re-runs this script but
# can keep imported modules cached, so reading here keeps the embedded page
# current after every redeploy).
HTML = (Path(__file__).resolve().parent / "kh_atlas.html").read_text(encoding="utf-8")

# The page reads its deep links from its own location, which inside the
# component iframe is about:srcdoc. Hand the app's query string in instead.
params = {k: v for k, v in st.query_params.to_dict().items()
          if k in ("beat", "step", "site", "view", "still", "q", "dpr")}
if params:
    import json
    HTML = HTML.replace("<body>", "<body><script>window.__KH_QUERY=" + json.dumps(params) + "</script>", 1)

st.iframe(HTML, height=900)
