"""Peaker Demo — Peaker Plant 3D on its own link.

The Peaker Plant 3D model lifted out of the Investor Demo pack and served
standalone: one link, straight into the model, no landing page and no pack
navigation. Prices stay in £/MWh, exactly as the packs show them, so this is
the investor-facing peaker on a URL of its own — the pack keeps its Peaker
card too, this is an additional door, not a move.

Tailored for an energy-literate audience: the strike price opens at £80/MWh
on a £50–£100 range (the packs run £40–£160 from £100), the export price is
named for what it is — day-ahead plus gDUoS — on the seesaw and in the
dispatch-desk legend, and the footer's "peaker model" explainer is dropped,
leaving its price-sourcing line.

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

# Everything that makes this surface different is declared here and applied by
# the model at load, so peaker_plant_3d.html stays a byte-for-byte upstream copy
# shared by all four peaker surfaces: the guided-tour view strip is dropped (as
# the packs do), and PEAKER_CFG narrows the strike control and names the export
# price. The model leaves both alone when a surface declares neither.
DEMO_CFG = """
<script>window.PEAKER_CFG={
  strike:{value:80, min:50, max:100},
  exportLabel:"Export \\u00B7 DA + gDUoS",
  legendLabel:"Export value \\u00B7 DA + gDUoS"
};</script>
"""

DEMO_CSS = """
<style>
  /* the guided-tour view strip — the packs drop it too */
  #viewstrip {display:none !important;}
  /* the "peaker model:" explainer: this audience reads the dispatch desk
     itself, so the footer keeps only its price-sourcing and copyright line */
  footer > div:first-child {display:none !important;}
</style>
"""

# Read the scene fresh from the main script each run (Streamlit re-runs this
# script but can keep imported modules cached, so reading here keeps the
# embedded build current after every redeploy).
PEAKER_HTML = (Path(__file__).resolve().parent / "peaker_plant_3d.html").read_text(
    encoding="utf-8").replace("</head>", DEMO_CFG + DEMO_CSS + "</head>", 1)

st.iframe(PEAKER_HTML, height=900)
