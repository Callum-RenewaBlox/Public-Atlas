"""Investor Demo — the RenewaBlox project pack.

One app, three doors. A minimal landing page introduces the pack and links to
the interactive 3D models, each rendered full-bleed behind a slim petrol
navigation bar:

* ``?view=peaker`` — Peaker Plant 3D: the peaker business model as a living
  site, with its half-hourly dispatch desk (``peaker_plant_3d.html``).
* ``?view=hydro`` — Hydro 3D: the Kinlochdamph powerhouse and its in-room data
  centre, water to wire to rack (``kld_interactive.html``).
* ``?view=heat`` — Heat Network 3D: the ISL heat network and the
  data centre that heats it, a year half-hour by half-hour
  (``heat_network_3d.html``, built by ``build_heat_network_3d.py`` in the
  ISL client's contract folder).
* ``?view=dfc`` — Demand for Constraints 3D: the Moray cluster north of the
  B4 constraint and the two BLOX halls NESO dispatches to absorb curtailed
  wind, a year half-hour by half-hour (``demand_for_constraints_3d.html``,
  built by ``build_dfc_3d.py`` in the in-house Atlas 3D folder).

NEM 3D is not in this pack: it was built for one group of Australian investors,
who get Peaker Plant 3D and Hydro 3D plus that one at a URL of their own
(Heat Network 3D is not in the Australia pack yet) — see
``app_investor_demo_aus.py``.

Self-contained: the landing page (``investor_demo_home.html``, hand-authored,
scene thumbnails and wordmark inlined) and every model carry all data embedded
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
    "heat": {"file": "heat_network_3d.html", "label": "Heat Network 3D"},
    # the pack bar shortens labels to their first word on a phone; "Demand" alone
    # would not say what this is
    "dfc": {"file": "demand_for_constraints_3d.html", "label": "Demand for Constraints 3D", "short": "DfC"},
}

# Presentation-only patches applied to a model page as it is served, so the
# HTML files stay byte-for-byte copies of their upstream builds. Peaker: the
# guided-tour view strip is dropped for investors — the overview scene is the
# demo.
PATCH_CSS = {
    "peaker": "#viewstrip{display:none !important;}",
}

# Views whose figures are for investors. In this public pack the panels that
# carry them are blurred and inert — a visitor sees that the data is there —
# and a card points to the investor portal. Cosmetic by design: the numbers
# are still in the page the browser receives, and the model files are public
# in this repository; the portal edition (``app_investor_portal.py``) serves
# the same files unblurred behind its access gate. ``blur`` lists the panels
# that carry figures, ``hide`` the controls that only make sense with them
# (the DfC assumptions drawer is the whole commercial model), ``top`` puts the
# card over the blurred column.
PORTAL_URL = "https://www.renewablox.com/invest"
GATED = {
    "hydro": {
        "blur": ("#nowpanel, #powerwrap, #revpanel, #island .imbody, #deskwrap #chart, "
                 "#deskwrap #tip, #scstats, header .fchip b"),
        "hide": "",
        "top": "56%",
    },
    "dfc": {
        "blur": ("#rightcol, #stack, #modecard p, #modecard .row, #why, #sitecard .grid, "
                 "#sitecard .kit, #desk .lane:nth-child(2)"),
        "hide": "#gear",
        "top": "36%",
    },
}

GATE_CSS = """
  {blur}{{filter:blur(7px) saturate(.85); pointer-events:none !important; user-select:none;}}
  {hide}{{display:none !important;}}
  #rbx-gate{{position:fixed; right:{right}; top:{top}; transform:translateY(-50%); width:318px; z-index:40;
      font-family:"Inter","Inter var",system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
      background:rgba(255,255,255,.97); color:#12475e; border:1px solid #dde5ea; border-radius:14px;
      box-shadow:0 18px 48px rgba(9,26,35,.38); padding:18px 20px 16px;}}
  #rbx-gate .k{{font-size:11px; font-weight:700; letter-spacing:.16em; text-transform:uppercase; color:#1f5f7f;
      margin:0 0 6px; display:flex; align-items:center; gap:8px;}}
  #rbx-gate .k::before{{content:""; width:20px; height:2px; background:#1f5f7f; border-radius:2px;}}
  #rbx-gate h3{{margin:0 0 14px; font-size:15px; font-weight:600; letter-spacing:-.005em; line-height:1.45;}}
  #rbx-gate p{{margin:0 0 12px; font-size:13px; line-height:1.5; color:#4f6572;}}
  #rbx-gate a{{display:inline-flex; align-items:center; gap:8px; background:#1f5f7f; color:#fff; text-decoration:none;
      font-weight:600; font-size:13px; padding:9px 15px; border-radius:999px; transition:background .15s;}}
  #rbx-gate a:hover{{background:#16485f;}}
"""
GATE_HTML = """<div id="rbx-gate"><div class="k">Investor data</div>
<h3>Access to the full, unredacted version is controlled via the RenewaBlox Investor Portal which requires registration</h3>
<a href="{url}" target="_blank" rel="noopener">Open the investor portal &rarr;</a></div>
"""

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
      .rbx-bar a.portal {{margin-left:8px; border:1px solid rgba(255,255,255,.38); color:#fff; font-weight:600;}}
      .rbx-bar a.portal:hover {{background:#fff; color:#0d1b23;}}
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
    portal_link = (f'<a href="{PORTAL_URL}" target="_blank" rel="noopener" class="portal">'
                   f'Investor data &rarr; portal</a>' if view in GATED else "")
    for key, model in MODELS.items():
        active = ' class="active"' if key == view else ""
        short = model.get("short", model["label"].split()[0])
        links.append(
            f'<a href="?view={key}" target="_self"{active}>'
            f'<span class="lbl-f">{model["label"]}</span>'
            f'<span class="lbl-s">{short}</span></a>')
    st.markdown(
        f"""
        <div class="rbx-bar">
          <a href="?view=home" target="_self" class="back">&larr; All models</a>
          <div class="crumb">Investor Demo &middot; {MODELS[view]["label"]}</div>
          <nav>{"".join(links)}{portal_link}</nav>
        </div>
        """,
        unsafe_allow_html=True,
    )
    model_html = (HERE / MODELS[view]["file"]).read_text(encoding="utf-8")
    if view in PATCH_CSS:
        model_html = model_html.replace(
            "</head>", f"<style>{PATCH_CSS[view]}</style></head>", 1)
    if view in GATED:
        g = GATED[view]
        css = GATE_CSS.format(blur=g["blur"], hide=g["hide"] or "#rbx-gate-none",
                              top=g["top"], right=g.get("right", "18px"))
        model_html = model_html.replace("</head>", f"<style>{css}</style></head>", 1)
        model_html = model_html.replace("</body>", GATE_HTML.format(url=PORTAL_URL) + "</body>", 1)
    st.iframe(model_html, height=900)
