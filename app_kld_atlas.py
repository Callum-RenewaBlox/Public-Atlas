"""KLD Atlas — Kinlochdamph 999 kW run-of-river hydro, Loch Damh (Wester Ross).

A standalone Leaflet atlas of the built-but-stranded Kinlochdamph scheme: site
assets georeferenced from the construction drawings, the 11/33/132 kV network
around it, the two SSEN connection options (1 km at 50 kW vs 7.8 km at 999 kW)
and the embedded-hydro fleet already on the same radial.

One app, two views — the same shape as ``app_srv_atlas.py``, so the two site
atlases behave identically:

* default — the map (``kld_atlas.html``), carrying a pulsing BLOX badge on the
  powerhouse with a standing "3D Revenue Sim" call to action.
* ``?view=3d`` — the 3D Revenue Sim: the Kinlochdamph living site model
  (``kld_interactive.html``),
  full-bleed, with an "Atlas" control to come back.

The model is a separate route rather than an in-page overlay, so the map page
stays at ~0.3 MB and the model gets the whole browser window. Note that
``kld_interactive.html`` is shared with the investor-demo apps and must stay
untouched: the atlas chrome for it (design-system overrides plus the back
control) lives in ``kld_hydro_chrome.html`` and is appended at serve time.
Both generated files come from
``Contracts/Kinlochdamph/Atlas/build_kld_atlas.py``.

Self-contained: everything is inlined, no database and no secrets.

Public tool. Run locally:  streamlit run app_kld_atlas.py
"""
from pathlib import Path

import streamlit as st

VIEW_3D = st.query_params.get("view") == "3d"

st.set_page_config(
    page_title="KLD Atlas — 3D Revenue Sim" if VIEW_3D else "KLD Atlas — Kinlochdamph",
    page_icon=":material/hub:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Both views are the whole page: strip Streamlit's chrome and padding so the
# iframe owns the full viewport (each page positions its own bar, panels and
# controls absolutely inside it).
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
if VIEW_3D:
    html = (HERE / "kld_interactive.html").read_text(encoding="utf-8")
    chrome = HERE / "kld_hydro_chrome.html"
    if chrome.exists():
        html = html.replace("</body>", chrome.read_text(encoding="utf-8") + "\n</body>", 1)
else:
    html = (HERE / "kld_atlas.html").read_text(encoding="utf-8")

st.iframe(html, height=900)
