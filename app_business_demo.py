"""Business Electricity — RenewaBlox with tem, the client pack for business customers.

For businesses that buy electricity, not experts in it. The pack tells one story:
around half of a business electricity bill isn't the electricity, and tem and
RenewaBlox work on it from either side of the meter. tem supplies the power
(RED, priced against its UK renewable portfolio through the Rosso platform) and
the RED Plus benefit (P442 exempt supply); RenewaBlox works on the site in
three tiers, each including RED and RED Plus and building on the one before:

* ``?view=site`` — Tier 1, **Holistic Site Analysis**: an example report for an
  illustrative site built on tem's example quote — capacity, night-rate
  timing, power factor, levies and bands, with a running total
  (``business_site_analysis.html``).
* ``?view=haas`` — Tier 2, **Heat-as-a-Service**: Bitcoin miners heating the
  site, through a large dry cooler or as space heaters, in an animated
  isometric scene with heat figures (``business_haas.html``).
* ``?view=heat`` — Tier 3, **Heat Network**: Heat Network 3D, the investor
  pack's model of a data centre heating a district network
  (``heat_network_3d.html``), served with all of its data — the investor-portal
  blur in ``app_investor_demo.py`` is for investors, not this audience.

Self-contained: the landing page (``business_demo_home.html``, hand-authored,
page frames and wordmark inlined) and every page carry all data embedded — no
CDN, no database, no secrets. Navigation is plain query-param links, so each
tier has a shareable URL. The landing fragment and the two tier pages are
hand-authored (wordmark and page frames inlined as data URIs): edit them directly.

The landing page is a script-free HTML fragment rendered in the parent page
with ``st.markdown`` rather than inside ``st.iframe`` — Streamlit sandboxes
component iframes without ``allow-top-navigation``, so links inside one can
never change the app's URL. The tier pages run their own scripts inside the
iframe and scroll within it.

Public tool. Run locally:  streamlit run app_business_demo.py
"""
from pathlib import Path

import streamlit as st

HERE = Path(__file__).resolve().parent

CONTACT = "callum@renewablox.com"
BILL_SUBJECT = "Business%20electricity%20%E2%80%94%20our%20bill"

VIEWS = {
    "site": {"file": "business_site_analysis.html", "tier": "Tier 1",
             "label": "Holistic Site Analysis", "short": "Site"},
    "haas": {"file": "business_haas.html", "tier": "Tier 2",
             "label": "Heat-as-a-Service", "short": "HaaS"},
    "heat": {"file": "heat_network_3d.html", "tier": "Tier 3",
             "label": "Heat Network", "short": "Network"},
}

view = st.query_params.get("view", "home")
if view not in VIEWS:
    view = "home"

st.set_page_config(
    page_title=("RenewaBlox × tem — Business Electricity" if view == "home"
                else f"RenewaBlox — {VIEWS[view]['tier']} · {VIEWS[view]['label']}"),
    page_icon=":material/electric_bolt:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Strip Streamlit's chrome and padding on every view. On tier views the page
# fills the viewport below a 46 px pack bar and scrolls inside its iframe; the
# landing page keeps the app's natural page scroll.
BAR_H = 46

VIEWPORT_CSS = {
    "model": f"""
      [data-testid="stAppViewContainer"] {{overflow:hidden !important;}}
      /* stMain scrolls by default and reserves a scrollbar gutter, which would
         leave a dead strip down the right-hand edge of a full-bleed page */
      [data-testid="stMain"] {{overflow:hidden !important; height:100dvh !important;}}
      [data-testid="stIFrame"] {{
          height:calc(100dvh - {BAR_H}px) !important; width:100% !important;
          display:block; border:0;}}
      html, body, .stApp {{overflow:hidden !important;}}
    """,
    "home": """
      [data-testid="stMain"] {scrollbar-width:thin; scroll-behavior:smooth;}
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
      {VIEWPORT_CSS["model" if view in VIEWS else "home"]}

      /* The bar is purely navigational — each page's own header below it
         carries the wordmark, so the bar doesn't repeat the brand. */
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
      .rbx-bar a .t {{opacity:.6; margin-right:5px; font-weight:600;}}
      .rbx-bar a.back {{color:#fff; font-weight:600; padding-left:2px;}}
      .rbx-bar a.talk {{margin-left:8px; border:1px solid rgba(255,63,16,.7); color:#fff; font-weight:600;}}
      .rbx-bar a.talk:hover {{background:#ff3f10; border-color:#ff3f10; color:#fff;}}
      .rbx-bar .lbl-s {{display:none;}}
      @media (max-width:900px) {{ .rbx-bar .crumb {{display:none;}} }}
      @media (max-width:640px) {{
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
    home = (HERE / "business_demo_home.html").read_text(encoding="utf-8")
    # st.markdown parses this as Markdown: a blank line ends a CommonMark HTML
    # block and the indented remainder would render as a code block, so drop
    # blank lines before handing the fragment over.
    home = "\n".join(line for line in home.splitlines() if line.strip())
    st.markdown(home, unsafe_allow_html=True)
else:
    page = VIEWS[view]
    # target="_self" matters: Streamlit's markdown renderer retargets plain
    # anchors to open in a new tab, which would orphan the pack navigation.
    links = []
    for key, v in VIEWS.items():
        active = ' class="active"' if key == view else ""
        links.append(
            f'<a href="?view={key}" target="_self"{active}>'
            f'<span class="lbl-f"><span class="t">{v["tier"][-1]}</span>{v["label"]}</span>'
            f'<span class="lbl-s">{v["short"]}</span></a>')
    st.markdown(
        f"""
        <div class="rbx-bar">
          <a href="?view=home" target="_self" class="back">&larr; Overview</a>
          <div class="crumb">Business Electricity &middot; {page["tier"]} &middot; {page["label"]}</div>
          <nav>{"".join(links)}<a href="mailto:{CONTACT}?subject={BILL_SUBJECT}"
            target="_self" class="talk">Send us a bill</a></nav>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.iframe((HERE / page["file"]).read_text(encoding="utf-8"), height=900)
