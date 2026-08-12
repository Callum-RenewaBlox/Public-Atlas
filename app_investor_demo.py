"""Investor Demo — the RenewaBlox project pack.

One app, three doors. A minimal landing page introduces the pack and links to
the interactive 3D models, each rendered full-bleed behind a slim petrol
navigation bar:

* ``?view=peaker`` — Peaker Plant 3D: the peaker business model as a living
  site, with its half-hourly dispatch desk (``peaker_plant_3d.html``).
* ``?view=hydro`` — Hydro 3D: the Kinlochdamph powerhouse and its in-room data
  centre, water to wire to rack (``kld_interactive.html``).
* a third model joins the pack shortly (ghost card on the landing page).

Self-contained: the landing page (``investor_demo_home.html``, hand-authored,
scene thumbnails and wordmark inlined) and both models carry all data embedded
— no CDN, no database, no secrets. Navigation is plain query-param links, so
each model has a shareable URL.

The landing page is a script-free HTML fragment rendered in the parent page
with ``st.markdown`` rather than inside ``st.iframe`` — Streamlit sandboxes
component iframes without ``allow-top-navigation``, so links inside one can
never change the app's URL.

Public tool. Run locally:  streamlit run app_investor_demo.py
"""
from pathlib import Path

import streamlit as st

HERE = Path(__file__).resolve().parent

MODELS = {
    "peaker": {"file": "peaker_plant_3d.html", "label": "Peaker Plant 3D"},
    "hydro": {"file": "kld_interactive.html", "label": "Hydro 3D"},
}

view = st.query_params.get("view", "home")
if view not in MODELS:
    view = "home"

st.set_page_config(
    page_title=("RenewaBlox — Investor Demo" if view == "home"
                else f"RenewaBlox — {MODELS[view]['label']}"),
    page_icon=":material/deployed_code:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Strip Streamlit's chrome and padding on every view. On model views the
# scene fills the viewport edge to edge below a 46 px pack bar and nothing
# scrolls; the landing page keeps the app's natural page scroll.
BAR_H = 46

VIEWPORT_CSS = {
    # model views: lock the page — the scene owns the viewport
    "model": f"""
      [data-testid="stAppViewContainer"] {{overflow:hidden !important;}}
      /* stMain scrolls by default and reserves a scrollbar gutter, which would
         leave a dead strip down the right-hand edge of a full-bleed scene */
      [data-testid="stMain"] {{overflow:hidden !important; height:100dvh !important;}}
      [data-testid="stIFrame"] {{
          height:calc(100dvh - {BAR_H}px) !important; width:100% !important;
          display:block; border:0;}}
      html, body, .stApp {{overflow:hidden !important;}}
    """,
    # landing page: scroll as a normal page, with a slim scrollbar
    "home": """
      [data-testid="stMain"] {scrollbar-width:thin;}
    """,
}

st.markdown(
    f"""
    <style>
      [data-testid="stHeader"], [data-testid="stToolbar"],
      [data-testid="stDecoration"], [data-testid="stStatusWidget"],
      [data-testid="stBottomBlockContainer"], .stApp > footer {{display:none !important;}}
      [data-testid="stMain"] .block-container,
      [data-testid="stMainBlockContainer"], .block-container {{
          padding:0 !important; margin:0 !important; max-width:100% !important;}}
      [data-testid="stVerticalBlock"], [data-testid="stVerticalBlockBorderWrapper"] {{
          gap:0 !important;}}
      [data-testid="stElementContainer"], [data-testid="element-container"] {{
          width:100% !important;}}
      .stApp {{background:#f4f8fa;}}
      {VIEWPORT_CSS["model" if view in MODELS else "home"]}

      /* The bar is purely navigational — the model's own header below it
         carries the real wordmark, so the bar doesn't repeat the brand. */
      .rbx-bar {{height:{BAR_H}px; background:#0d1b23; display:flex; align-items:center;
          gap:14px; padding:0 14px; overflow-x:auto; scrollbar-width:none;
          -webkit-overflow-scrolling:touch;
          font-family:"Inter","Inter var",system-ui,-apple-system,"Segoe UI",
                      Roboto,"Helvetica Neue",Arial,sans-serif;}}
      .rbx-bar::-webkit-scrollbar {{display:none;}}
      .rbx-bar .crumb {{font-size:12.5px; color:#93a2aa; white-space:nowrap;}}
      .rbx-bar nav {{margin-left:auto; display:flex; gap:6px; align-items:center;}}
      .rbx-bar a {{text-decoration:none; font-size:12.5px; padding:5px 13px;
          border-radius:999px; color:#b9c6cd; white-space:nowrap;
          transition:background .15s, color .15s;}}
      .rbx-bar a:hover {{color:#fff; background:rgba(255,255,255,.09);}}
      .rbx-bar a:focus-visible {{outline:2px solid #fff; outline-offset:2px;}}
      .rbx-bar a.active {{color:#0d1b23; background:#fff; font-weight:600;}}
      .rbx-bar a.back {{color:#fff; font-weight:600; padding-left:2px;}}
      .rbx-bar .lbl-s {{display:none;}}
      @media (max-width:640px) {{ .rbx-bar .crumb {{display:none;}} }}
      @media (max-width:480px) {{
        .rbx-bar .lbl-f {{display:none;}}
        .rbx-bar .lbl-s {{display:inline;}}
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Read the pages fresh from the main script each run (Streamlit re-runs this
# script but can keep imported modules cached, so reading here keeps the
# embedded build current after every redeploy).
if view == "home":
    home = (HERE / "investor_demo_home.html").read_text(encoding="utf-8")
    # st.markdown parses this as Markdown: a blank line ends a CommonMark HTML
    # block and the indented remainder would render as a code block, so drop
    # blank lines before handing the fragment over.
    home = "\n".join(line for line in home.splitlines() if line.strip())
    st.markdown(home, unsafe_allow_html=True)
else:
    # target="_self" matters: Streamlit's markdown renderer retargets plain
    # anchors to open in a new tab, which would orphan the pack navigation.
    links = []
    for key, model in MODELS.items():
        active = ' class="active"' if key == view else ""
        short = model["label"].split()[0]
        links.append(
            f'<a href="?view={key}" target="_self"{active}>'
            f'<span class="lbl-f">{model["label"]}</span>'
            f'<span class="lbl-s">{short}</span></a>')
    st.markdown(
        f"""
        <div class="rbx-bar">
          <a href="?view=home" target="_self" class="back">&larr; All models</a>
          <div class="crumb">Investor Demo &middot; {MODELS[view]["label"]}</div>
          <nav>{"".join(links)}</nav>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.iframe((HERE / MODELS[view]["file"]).read_text(encoding="utf-8"),
              height=900)
