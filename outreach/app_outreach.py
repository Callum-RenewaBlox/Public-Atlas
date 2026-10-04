"""RenewaBlox × tem — the business outreach strategy, as an app.

The strategy (working draft of 2 October 2026) in seven pages under one sticky
tab rail, each with its own address:

* ``/``            Overview — the hook, the channel map, the four plays, the first week
* ``/offer``       Offer & targets — the edge, the claims, the limits, the segments
                   and a segment playbook that pulls each segment's thread together
* ``/linkedin``    LinkedIn — foundations to paid, with the funnel as a live model
* ``/strategies``  Three strategies — Demand Atlas, Local Power, Borrowed trust
* ``/plan``        The plan — the 14 weeks on a live chart, tasks by owner
* ``/compliance``  Compliance — the two decisions, the checklist, the sources
* ``/toolkit``     Toolkit — every template and crew prompt, fields filled once

Unlike the repo's other apps this is native Streamlit rather than a wrapped
page, so its models (funnel, sizing, plan status) can respond to the reader.
It lives in its own folder so its theme (``.streamlit/config.toml`` here)
applies to it alone. No data, no secrets.

Public tool. Run locally:  streamlit run outreach/app_outreach.py
"""
import streamlit as st

import sections
import toolkit
from ui import html, inject_css

st.set_page_config(
    page_title="RenewaBlox × tem — Outreach strategy",
    page_icon=":material/electric_bolt:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PAGES = [
    st.Page(sections.overview, title="Overview", icon=":material/space_dashboard:", default=True),
    st.Page(sections.offer, title="Offer & targets", icon=":material/my_location:", url_path="offer"),
    st.Page(sections.linkedin, title="LinkedIn", icon=":material/person_add:", url_path="linkedin"),
    st.Page(sections.strategies, title="Three strategies", icon=":material/hub:", url_path="strategies"),
    st.Page(sections.plan, title="The plan", icon=":material/calendar_month:", url_path="plan"),
    st.Page(sections.compliance, title="Compliance", icon=":material/verified_user:", url_path="compliance"),
    st.Page(toolkit.page, title="Toolkit", icon=":material/edit_note:", url_path="toolkit"),
]

current = st.navigation(PAGES, position="hidden")
st.set_page_config(page_title=f"{current.title} · RenewaBlox outreach strategy")
inject_css()

html("""
<div class="brandbar">
  <div class="wordmark">
    <span class="wm">RENEWA<b>BLOX</b><span class="dot">.</span></span>
    <span class="wm-x">×</span>
    <span class="temmark">tem</span>
    <span class="wm-sep" aria-hidden="true"></span>
    <span class="wm-label">Business<br>outreach strategy</span>
  </div>
  <div class="metas">
    <span class="pill"><span class="k">As of</span> 2 October 2026</span>
    <span class="pill opt"><span class="k">Author</span> Callum Wheeler</span>
    <span class="pill opt"><span class="k">For</span> Tom, Jason and the crew</span>
  </div>
</div>
""")

with st.container(key="rail", horizontal=True):
    for page in PAGES:
        st.page_link(page)

current.run()

# Previous and next, so the strategy also reads straight through.
i = next(n for n, p in enumerate(PAGES) if p.url_path == current.url_path)
with st.container(key="pager", horizontal=True, horizontal_alignment="distribute"):
    if i > 0:
        st.page_link(PAGES[i - 1], label=f"Previous · {PAGES[i - 1].title}", icon=":material/arrow_back:")
    else:
        st.empty()
    if i < len(PAGES) - 1:
        st.page_link(PAGES[i + 1], label=f"Next · {PAGES[i + 1].title}", icon=":material/arrow_forward:")
html("""
<div class="colophon">
  <span>RenewaBlox Ltd · Business outreach strategy · working draft of 2 October 2026</span>
  <span>Figures about tem are tem’s. Funnel rates and the 1p/kWh example are planning assumptions.</span>
</div>
""")
