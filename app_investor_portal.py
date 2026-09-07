"""Investor Portal — the RenewaBlox project pack, at the URL the investor
portal links to.

A duplicate of the Investor Demo (``app_investor_demo.py``) at its own URL, so
the portal can carry the full pack while the public demo is cut back. Same
four models, same landing, same navigation. The one addition is an access
gate: if the app's Streamlit secrets carry ``PORTAL_PASSCODE``, every view is
locked until the visitor arrives with the key. Two ways in, both remembered in
a browser cookie so the model links never re-ask:

* frictionless — the portal's link carries the key, ``?k=<key>``, where the
  key is the code's keyed hash (``portal_key.py`` prints it); an investor who
  clicks through from the logged-in portal never sees a prompt, and the key is
  removed from the address bar on arrival;
* fallback — a code prompt, for anyone you send the code to by other means.

With no secret set the app is open, exactly like the demo. Note that the model
files and this code are in a public repository whatever the gate says — the
gate protects the URL, not the files.

A minimal landing page introduces the pack and links to the interactive 3D
models, each rendered full-bleed behind a slim petrol navigation bar:

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

Run locally:  streamlit run app_investor_portal.py
"""
import hashlib
import hmac
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

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

view = st.query_params.get("view", "home")
if view not in MODELS:
    view = "home"

st.set_page_config(
    page_title=("RenewaBlox — Investor Portal" if view == "home"
                else f"RenewaBlox — {MODELS[view]['label']}"),
    page_icon=":material/deployed_code:",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def passcode_ok() -> bool:
    """True when no access code is configured, or the visitor has entered it.

    The code lives in Streamlit secrets as ``PORTAL_PASSCODE`` (never in the
    repo). The pack's navigation is plain links, and every link is a full page
    load — a new Streamlit session — so the pass is remembered in a browser
    cookie: a keyed hash of the code, set once on success and checked at the
    start of each session. The same hash is the key a portal link can carry
    (``?k=``), which opens the pack without a prompt. Clearing cookies, or
    changing the code, asks again.
    """
    try:
        code = str(st.secrets.get("PORTAL_PASSCODE", ""))
    except Exception:  # no secrets file at all (local runs)
        code = ""
    if not code:
        return True
    token = hmac.new(code.encode(), b"rbx-portal", hashlib.sha256).hexdigest()
    if st.session_state.get("portal_ok"):
        if st.session_state.pop("portal_set_cookie", False):
            # a 0-height component runs script; Streamlit's component frames share
            # the page's origin, so this lands the cookie on the app itself
            components.html(
                f"<script>parent.document.cookie = 'rbx_portal={token}; path=/; max-age=2592000; SameSite=Lax'"
                " + (parent.location.protocol === 'https:' ? '; Secure' : '');</script>", height=0)
        return True
    # the key in the portal's link: in, cookie set, key dropped from the address bar
    key = str(st.query_params.get("k", ""))
    if key and (hmac.compare_digest(key, token) or hmac.compare_digest(key, code)):
        del st.query_params["k"]
        st.session_state["portal_ok"] = True
        st.session_state["portal_set_cookie"] = True
        st.rerun()
    try:
        seen = st.context.cookies.get("rbx_portal", "")
    except Exception:  # older Streamlit without st.context
        seen = ""
    if seen and hmac.compare_digest(seen, token):
        st.session_state["portal_ok"] = True
        return True
    st.markdown(
        """
        <style>
          .rbx-gate {max-width:380px; margin:14vh auto 0; font-family:"Inter","Inter var",system-ui,
              -apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif; color:#12475e;}
          .rbx-gate .k {font-size:12px; font-weight:700; letter-spacing:.16em; text-transform:uppercase;
              color:#1f5f7f; margin-bottom:6px;}
          .rbx-gate h1 {font-size:26px; font-weight:800; letter-spacing:-.02em; margin:0 0 6px;}
          .rbx-gate p {font-size:14px; color:#4f6572; margin:0 0 14px; line-height:1.5;}
          [data-testid="stForm"] {max-width:380px; margin:0 auto; border:1px solid #dde5ea; border-radius:14px;
              padding:18px 18px 8px; background:#fff;}
        </style>
        <div class="rbx-gate"><div class="k">Investor portal</div><h1>RenewaBlox project pack</h1>
        <p>Enter the access code from your portal invitation to open the models.</p></div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("rbx-gate", clear_on_submit=False):
        entered = st.text_input("Access code", type="password", label_visibility="collapsed",
                                placeholder="Access code")
        submitted = st.form_submit_button("Open the pack")
    if submitted:
        if hmac.compare_digest(entered.strip(), code):
            st.session_state["portal_ok"] = True
            st.session_state["portal_set_cookie"] = True
            st.rerun()
        st.error("That code was not recognised.")
    return False


if not passcode_ok():
    st.stop()

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
    home = (HERE / "investor_portal_home.html").read_text(encoding="utf-8")
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
        short = model.get("short", model["label"].split()[0])
        links.append(
            f'<a href="?view={key}" target="_self"{active}>'
            f'<span class="lbl-f">{model["label"]}</span>'
            f'<span class="lbl-s">{short}</span></a>')
    st.markdown(
        f"""
        <div class="rbx-bar">
          <a href="?view=home" target="_self" class="back">&larr; All models</a>
          <div class="crumb">Investor Portal &middot; {MODELS[view]["label"]}</div>
          <nav>{"".join(links)}</nav>
        </div>
        """,
        unsafe_allow_html=True,
    )
    model_html = (HERE / MODELS[view]["file"]).read_text(encoding="utf-8")
    if view in PATCH_CSS:
        model_html = model_html.replace(
            "</head>", f"<style>{PATCH_CSS[view]}</style></head>", 1)
    st.iframe(model_html, height=900)
