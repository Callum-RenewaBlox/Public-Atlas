"""The strategy's pages, one function each. The words are the strategy's
(working draft of 2 October 2026); the layout is the app's.

Three things are live rather than printed: the plan's status and the
"today" line on the 14-week chart (from the viewer's own date, or
``?date=YYYY-MM-DD`` to preview another day), the LinkedIn
funnel (its planning assumptions are sliders, so the founders can put their
own rates in after four weeks), and the generator sizing in strategy B.
"""
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st

import toolkit
from ui import (callout, card, cards, e, html, intro, keep, kept, link, mini, ol, save, sec,
                stat, subhead, table, ul)

# ---------------------------------------------------------------- sources
TEM_FAQS = "https://www.tem.energy/faqs"
TEM_TARIFFS = "https://www.tem.energy/business-energy-tariffs"
TEM_GORSEINON = "https://www.tem.energy/case-studies/gorseinon-rfc"
ELEXON_MHHS = "https://www.elexon.co.uk/bsc/operational/market-wide-half-hourly-settlement/"
ELEXON_P442 = "https://www.elexon.co.uk/bsc/mod-proposal/p442/"
ELEXON_ESNA = "https://www.elexon.co.uk/2026/09/23/rule-change-to-help-exempt-supply-notification-agents-receive-the-data-they-need-under-mhhs/"
OVO_EVIDENCE = "https://committees.parliament.uk/writtenevidence/134157/html/"
OFGEM_PROTECT = "https://www.ofgem.gov.uk/publications/ofgem-confirms-greater-protection-businesses"
OFGEM_TPI = "https://www.ofgem.gov.uk/call-for-input/third-party-intermediaries-tpis-market-review"
ICO_B2B = "https://ico.org.uk/for-organisations/direct-marketing/business-to-business-marketing"
ICO_EMAIL = ("https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/"
             "guidance-on-direct-marketing-using-electronic-mail/key-concepts-for-direct-marketing-using-electronic-mail/")
LINKEDIN_HELP = "https://www.linkedin.com/help/linkedin/answer/a1340522"
SALESFORGE = "https://www.salesforge.ai/blog/linkedin-connection-request-limit"
CROWE_SECR = "https://www.crowe.com/uk/insights/streamlined-energy-and-carbon-reporting"
EPC_DATA = "https://epc.opendatacommunities.org"
DFE_EXAMPLE = "https://financial-benchmarking-and-insights-tool.education.gov.uk/trust/07387540/summary"
ADBA = "https://adbioresources.org/industry-directory/tem-energy/"
BED_TEM = "https://www.businessenergydeals.co.uk/blog/tem-energy/"

# ---------------------------------------------------------------- the plan's calendar
PLAN_START = date(2026, 10, 5)
PLAN_END = date(2027, 1, 8)
CHART_DAYS = 14 * 7
PHASES = [
    {"n": 1, "name": "Foundations", "start": date(2026, 10, 5), "end": date(2026, 10, 16),
     "dates": "5 to 16 October",
     "gate": ("Gate 1 · 16 Oct", "<b>X-ray page live, three audits complete,</b> tem’s answers in hand.",
              "X-ray page live, 3 audits done, tem’s answers in hand"),
     "tasks": [
         ("Callum", "Put five questions to tem: meter eligibility after the half-hourly migration, quote turnaround and what gets a quote declined, local pairing and what customers may claim, joint marketing, and referral terms on the generator side"),
         ("All three", "Agree one flat commission rate and write the “How we’re paid” page"),
         ("Each founder", "Rewrite profile and banner from crew drafts; fix locations"),
         ("Tom", "Build the Bill X-ray page, the secure upload and the sample audit"),
         ("Tom", "Add the LinkedIn queue, the active-channel field and the renewal radar to Watt’s Next"),
         ("Each founder", "Export connections; send the first 50 warm messages"),
         ("Each founder", "Open a Sales Navigator seat and save the first three lists"),
         ("Callum + crew", "Run three audits end to end on bills you already hold"),
         ("Callum", "Ask the biogas client for the story, the trading-partner list and a November date"),
     ]},
    {"n": 2, "name": "Engine on", "start": date(2026, 10, 19), "end": date(2026, 11, 27),
     "dates": "19 October to 27 November",
     "gate": ("Gate 2 · 27 Nov", "<b>15 bills received, 8 quotes issued,</b> acceptance rate at 30% or better, one partner pilot complete.",
              "15 bills in, 8 quotes out, 30% accepted, 1 pilot done"),
     "tasks": [
         ("Each founder", "80 requests and two posts a week"),
         ("Callum", "First issue of the newsletter; first live bill clinic"),
         ("Callum", "Local Power campaign one, with the site breakfast in November"),
         ("Jason", "Sign two accounting practices and one installer; complete the first book X-ray"),
         ("Jason", "Run the Bitcoin Business Network group tender"),
         ("Tom + crew", "Build 200 Demand Atlas records in one vertical; send the first 50 memos"),
     ]},
    {"n": 3, "name": "Prove and scale", "start": date(2026, 11, 30), "end": date(2027, 1, 8),
     "dates": "30 November to 8 January",
     "gate": ("Gate 3 · 8 Jan", "<b>First contracts signed,</b> and cost per bill and close rate known for each channel.",
              "First contracts signed, cost per bill known"),
     "tasks": [
         ("All three", "Double the time on the best channel; pause the worst"),
         ("Callum", "Publish “what we found in our first 30 bills”"),
         ("Tom", "Start the paid test, only if ten bills have arrived organically"),
         ("Jason", "Second generator campaign and two more partners"),
         ("All three", "Build the January campaign around contracts ending 31 March and the 1 April rate changes"),
     ]},
]


def today():
    """The viewer's date, from their browser's time zone where it is known.

    ``?date=YYYY-MM-DD`` on the address previews the plan as it will read on
    another day.
    """
    asked = st.query_params.get("date")
    if asked:
        try:
            return date.fromisoformat(asked)
        except ValueError:
            pass
    try:
        tz = st.context.timezone
        if tz:
            return datetime.now(ZoneInfo(tz)).date()
    except Exception:
        pass
    return date.today()


def short(d):
    return f"{d.day} {d.strftime('%b')}"


def long(d):
    return f"{d.strftime('%A')} {d.day} {d.strftime('%B')}"


def days(n):
    return "today" if n == 0 else "tomorrow" if n == 1 else f"in {n} days"


def plan_status(d):
    """(label, sentence, phase number in play or next) for date ``d``."""
    if d < PLAN_START:
        n = (PLAN_START - d).days
        return "Up next", f"Phase 1 starts {days(n)}, {long(PLAN_START)}", 1
    if d > PLAN_END:
        return "Plan window closed", f"Gate 3 was {long(PLAN_END)}: time to read the numbers", 3
    week = (d - PLAN_START).days // 7 + 1
    for ph in PHASES:
        if ph["start"] <= d <= ph["end"]:
            n = (ph["end"] - d).days
            gate = ph["gate"][0].split(" · ")[0]
            return (f"Week {week} of 14",
                    f"Phase {ph['n']}, {ph['name']} · {gate} {days(n)}", ph["n"])
    nxt = next(ph for ph in PHASES if ph["start"] > d)
    return (f"Week {week} of 14",
            f"Phase {nxt['n']}, {nxt['name']}, starts {days((nxt['start'] - d).days)}", nxt["n"])


# ---------------------------------------------------------------- the funnel
FUNNEL_DEFAULTS = {"per_week": 80, "founders": 3, "acc": 30, "conv": 15, "bill": 35,
                   "quote": 60, "close": 30, "mwh": 200, "pence": 1.0}


def funnel():
    """Monthly funnel numbers on the current (kept) assumptions."""
    a = {k: kept("f_" + k, v) for k, v in FUNNEL_DEFAULTS.items()}
    requests = a["per_week"] * a["founders"] * 52 / 12
    accepted = requests * a["acc"] / 100
    convs = accepted * a["conv"] / 100
    bills = convs * a["bill"] / 100
    quotes = bills * a["quote"] / 100
    contracts = quotes * a["close"] / 100
    commission = contracts * a["mwh"] * 1000 * a["pence"] / 100   # £ of annual commission added each month
    per_bill = commission / bills if bills else 0
    return a, [requests, accepted, convs, bills, quotes, contracts], commission, per_bill


def approx(x):
    if x >= 100:
        return f"{round(x, -1):,.0f}"
    if x >= 1:
        return f"{round(x):,.0f}"
    return f"{x:.1f}"


def money(x):
    """Planning-grade pounds: the nearest £1,000 above £10k, £500 above £1k, £10 above £100."""
    if x >= 10_000:
        return f"£{round(x, -3):,.0f}"
    if x >= 1000:
        return f"£{round(x / 500) * 500:,.0f}"
    return f"£{round(x, -1):,.0f}" if x >= 100 else f"£{x:,.0f}"


def reset_funnel():
    for k, v in FUNNEL_DEFAULTS.items():
        st.session_state["f_" + k] = v
        st.session_state["_f_" + k] = v


# ================================================================ 01 OVERVIEW
def overview():
    label, sentence, _ = plan_status(today())
    a, stages, commission, per_bill = funnel()
    html(f"""
    <section class="hero"><div class="hero-grid"><div>
      <p class="eyebrow">LinkedIn plus three unconventional channels</p>
      <h1>One offer, sold through <span class="grad">every channel.</span></h1>
      <p class="lead">A free <b>Bill X-ray</b> turns one electricity bill into a line-by-line audit and a tem quote,
      with RenewaBlox’s commission in plain sight. LinkedIn is the steady base, sent by hand by the three founders
      while the crew researches and drafts. Three further plays are where one relationship brings many meters.</p>
      <div class="status"><span class="dotlive"></span><span class="k">{e(label)}</span>{e(sentence)}</div>
    </div>
    <div class="facts" aria-label="Key figures">
      <div class="fact"><div class="k">The hook</div><div class="v">One bill in, an audit and a tem quote out</div></div>
      <div class="fact"><div class="k">Base rate</div><div class="v">About 3 contracts a month from cold LinkedIn alone</div></div>
      <div class="fact"><div class="k">Plan window</div><div class="v">14 weeks, 5 October to 8 January</div></div>
      <div class="fact"><div class="k">Founder time</div><div class="v">About four hours a week each</div></div>
    </div></div></section>""")

    html(sec("Summary", "Sell one thing through every channel",
             "Every route ends in the same action: the prospect sends one bill and a letter of authority, and gets back "
             "a line-by-line audit with a tem quote beside their current deal. Mid-contract prospects are not lost: "
             "their end dates go on the renewal radar and come back as quotes six months before expiry.", first=True),
         """
    <div class="chmap mt">
      <div class="ttl"><h4>Five channels, one hook</h4><span class="badge quiet">How the channels fit</span></div>
      <div class="channels">
        <div class="channel"><b>LinkedIn</b><span>sent by founders</span></div>
        <div class="channel"><b>Email crew</b><span>companies and LLPs</span></div>
        <div class="channel"><b>Demand Atlas</b><span>pre-priced memos</span></div>
        <div class="channel"><b>Local Power</b><span>generator-led</span></div>
        <div class="channel"><b>Partners</b><span>already hold the bills</span></div>
      </div>
      <div class="bus"></div>
      <div class="xray"><b>The Bill X-ray</b><span>one bill in, an audit and a tem quote out</span></div>
      <div class="split"></div>
      <div class="fork">
        <div class="leg"><span class="lab">mid-contract</span>
          <div class="outcome"><b>Renewal radar</b><span>Contract end date logged; a live price six months before</span></div></div>
        <div class="leg"><span class="lab">ending inside 12 months</span>
          <div class="outcome go"><b>Quote, then switch</b><span>Side by side with the current deal; commission shown in pence</span></div></div>
      </div>
      <div class="basebar">Every bill lands in <b>Watt’s Next</b> and adds to your own benchmarks</div>
    </div>
    <p class="figcap">Whichever way a prospect arrives, the Bill X-ray is the offer, and every bill feeds the CRM and the renewal radar.</p>
    """)

    html(sec("The four plays", "One steady base and three ways to bring many meters at once"),
         '<div class="mt">', cards([
             card("80 connection requests a week per founder, sent by hand, plus two posts a week each.",
                  tag="Base · LinkedIn", title="Founder-led outreach and bill teardowns", cls="base",
                  lead='<div class="letter">in</div>',
                  kv=[("Hard to copy because", "The crew’s research on every prospect"),
                      ("First move", "Rewrite the profiles and build the trust pack")]),
             card("Pre-priced memos built from public energy data, sent by post, LinkedIn and email.",
                  tag="Strategy A · Demand Atlas", title="Price it before you meet them",
                  lead='<div class="letter">A</div>',
                  kv=[("Hard to copy because", "Needs agents that can read thousands of filings"),
                      ("First move", "200 records and 50 memos in one vertical")]),
             card("A campaign around every plant you bring to tem: its story, its trading partners, a site breakfast.",
                  tag="Strategy B · Local Power", title="Each generator recruits its neighbours",
                  lead='<div class="letter">B</div>',
                  kv=[("Hard to copy because", "Only you sign generators as well as customers"),
                      ("First move", "Story, partner list and a breakfast date from the biogas client")]),
             card("Accountants and other advisers whose bookkeeping apps hold a year of every client’s invoices.",
                  tag="Strategy C · Borrowed trust", title="Partners who already hold the bills",
                  lead='<div class="letter">C</div>',
                  kv=[("Hard to copy because", "A whole client book audited overnight"),
                      ("First move", "A free five-client pilot with two practices")]),
         ]), "</div>")

    html('<div class="sec"></div><div class="cols wide-left">', "<div>",
         '<p class="eyebrow">Three corrections to the brief</p><h3 style="margin:9px 0 16px">What changed between the brief and the plan</h3>',
         '<div class="stack">',
         callout("tem says many brokers already sell RED. Your edge is the audit, the generator side, open commission and speed.",
                 "RED and P442 are not exclusive to you.", "correction"),
         callout("RED needs a half-hourly meter, so the target is sites using roughly 100,000 kWh a year or more.",
                 "“Businesses” is too wide.", "correction"),
         callout("LinkedIn bans third-party automation, and a restricted founder account would cost more than any tool saves.",
                 "The AI edge on LinkedIn is research and drafting, not sending.", "correction"),
         "</div></div><div>",
         '<p class="eyebrow">What to expect</p><h3 style="margin:9px 0 6px">A base, not a business</h3>',
         '<p class="small muted" style="margin-bottom:14px">Planning assumptions, not benchmarks. Replace them with your own numbers after four weeks, on the LinkedIn page’s funnel.</p>',
         '<div class="stats">',
         stat("3", "Contracts from cold LinkedIn alone, across three founders", "a month"),
         stat("£6,000", "Annual commission added each month by those three contracts, at a 200,000 kWh median site and 1p/kWh", "a year"),
         stat("100+", "Dated contracts on the renewal radar after a year of LinkedIn alone"),
         "</div>",
         '<p class="small" style="margin-top:12px;color:var(--ink-2)">The upside sits in strategies A, B and C and in the renewal radar, which compounds.</p>',
         "</div></div>")

    html('<div class="sec"></div><div class="cols wide-left"><div>',
         '<p class="eyebrow">Do these five things first</p><h3 style="margin:9px 0 16px">The first week’s moves</h3>',
         ol([
             "<b>Put five questions to tem:</b> meter eligibility after the half-hourly migration, quote turnaround and what gets a quote declined, local pairing, joint marketing, and generator referral terms. The email is drafted in the Toolkit.",
             "<b>Agree one flat commission rate</b> and write the “How we’re paid” page.",
             "<b>Build the Bill X-ray page</b> and one sample audit.",
             "<b>Fix the three LinkedIn profiles,</b> export your connections and send 50 warm messages.",
             "<b>Ask the biogas client</b> for its story, its trading-partner list and a November date.",
         ]),
         "</div><div>",
         '<p class="eyebrow">Two figures to confirm</p><h3 style="margin:9px 0 16px">Marked for the partner hub</h3>',
         callout("tem’s partner pages would not open when this plan was checked, so two figures are marked to confirm "
                 "in the partner hub: the share of a bill that P442 saves, and the generator uplift on exempt output. "
                 "Neither changes the plan; both change what you may say in public.",
                 "Two tem figures are unconfirmed", "decision"),
         "</div></div>")


# ================================================================ 02 OFFER & TARGETS
SEGMENTS = [
    # tier, segment, why it fits, who signs, best hook, LinkedIn angle, opener title, where the Demand Atlas finds them
    (1, "Hotels, spa hotels, holiday parks, large pubs and restaurants", "Long hours, big kitchens and laundry; owner is reachable",
     "Owner, general manager", "Bill X-ray plus capacity check", "Agreed capacity against real peak demand", "Hospitality",
     "Display Energy Certificates and non-domestic EPCs: ratings and floor area for large premises"),
    (1, "Light manufacturing, fabrication, food and drink production, cold stores", "Motors and refrigeration; reactive power and kVA often wrong",
     "MD, operations director", "Capacity and reactive power findings", "Reactive power and capacity charges", "Manufacturing and food",
     "FSA approved food establishments (cold stores, meat, dairy and fish plants) and Environment Agency permits"),
    (1, "Care homes and small care groups", "24-hour load, thin margins, finance-led",
     "Owner, finance manager", "Side-by-side quote", "Fixed forward price for a 24-hour load", "Care homes",
     "CQC care directory: care homes, providers and bed numbers"),
    (1, "Sports and leisure: clubs, gyms, golf, leisure trusts", "Floodlights, kitchens, pools; tem already has a rugby club case",
     "Treasurer, general manager", "Gorseinon RFC story", "Gorseinon RFC’s result with tem", "Sports clubs",
     "Display Energy Certificates and non-domestic EPCs (leisure)"),
    (1, "Farms with heavy load: dairy, poultry, glasshouses, aquaculture", "Already in your pipeline; often next to your generators",
     "Farmer, farm manager", "Local generator story", "The local plant now selling through tem", "Near a generator",
     "Environment Agency permits: intensive poultry and pig units"),
    (2, "Churches and charities with large buildings", "VAT and CCL errors are common and refundable",
     "Trustee, operations manager", "VAT and CCL check", "VAT and CCL check, with refunds for past overcharges", "Churches and charities",
     "Charity accounts: premises and utility costs for larger charities"),
    (2, "Independent schools and academy trusts", "Large, predictable load; check any framework tie first",
     "Bursar, school business manager", "Forward quote for the next academic year",
     "Forward quote for the next academic year, shown to governors as a side-by-side", "Schools",
     "DfE school financial benchmarking: utilities spend for every academy and trust"),
    (2, "Multi-site retail, garden centres, car dealerships", "Several meters, one decision",
     "FD, property manager", "One audit across all sites", "", "",
     "Published Scope 2 emissions (multi-site groups) and the VOA rating list for sizing"),
    (2, "Mid-market companies that file energy data in their accounts", "Usage is public, so you can pre-price",
     "FD, CFO", "Pre-priced memo (strategy A)", "The pre-priced memo (strategy A)", "FD with published energy data",
     "Annual accounts at Companies House (SECR) and published Scope 2"),
    (2, "Landlords and managing agents of multi-let estates", "One relationship, many meters",
     "Asset manager", "Group tender day", "", "", "VOA rating list: floor area and use of every rated property"),
    (3, "Micro-businesses on non-half-hourly meters", "Not eligible for RED today", "—", "Park until tem confirms", "", "", ""),
    (3, "Public bodies on buying frameworks", "Locked to the framework", "—", "Skip", "", "", ""),
    (3, "Energy Intensive Industries", "RED only, no RED Plus; usually have a large consultant", "—", "Skip for now", "", "", ""),
]
TIER_NOTE = {1: "Tier 1 · attack first", 2: "Tier 2 · as the engine runs", 3: "Tier 3 · parked or skipped"}


def offer():
    intro("The offer", "One hook, three limits, and the people it is for",
          "The prospect sends one bill and a letter of authority, and gets back a line-by-line audit with a tem quote "
          "beside their current deal. Working name: the <b>Bill X-ray</b>. It is the offer you already gave Boardy, "
          "made into a product. Aim it at owner-led and finance-led businesses with a half-hourly meter, in three home "
          "patches, at the moment something changes.")

    html(sec("Correction first", "RED is not your edge. What you wrap around the quote is.",
             "tem says many brokers already sell RED. Any broker on tem’s panel can quote the same price and the same "
             "RED Plus line. Four things set the Bill X-ray apart.", first=True),
         '<div class="mt">', cards([
             card("VAT and CCL treatment, agreed kVA against real peaks, TNUoS band, reactive power, out-of-contract "
                  "rates. tem’s own tariff page lists most of these as reducible and leaves the work to the customer. "
                  "You do the work.", tag="01 · Forensics beyond price"),
             card("You bring generators to tem as well as demand. No ordinary broker can show a business the plant its "
                  "money reaches.", tag="02 · Both sides of the market"),
             card("Commission is a bonus for you, not the model. Set one flat rate in p/kWh and print it on page one of "
                  "every quote.", tag="03 · Commission in plain sight"),
             card("An agent crew can turn a bill into an audit in minutes. A traditional broker takes days and a phone "
                  "call.", tag="04 · Speed"),
         ]), "</div>")

    html(sec("What you can say, and on whose authority", "Every tem figure is tem’s until you have your own"),
         '<div class="mt">', table(["Claim", "Source", "How to use it"], [
             ["RED is priced outside the wholesale market; customers typically save around 30%", link("tem FAQs", TEM_FAQS),
              "Always attribute to tem. Swap in your own quote data after the first 15 quotes"],
             ["RED Plus is a fixed p/kWh reduction from P442, shown as its own invoice line on every eligible quote",
              link("tem tariffs", TEM_TARIFFS),
              "A line on the quote, not the headline. tem’s partner explainer puts P442 at a single-digit share of the total bill: confirm in the partner hub"],
             ["Unit rates, standing and capacity charges fixed; third-party costs passed through at 0% markup",
              link("tem tariffs", TEM_TARIFFS), "The transparency story: every charge named"],
             ["5,500+ businesses on RED, renewal above 91%, £60M+ saved", link("tem tariffs", TEM_TARIFFS),
              "Borrowed credibility until RenewaBlox has switched customers of its own"],
             ["Gorseinon RFC cut its bill 40%, saving £12,000 a year", link("tem case study", TEM_GORSEINON),
              "A proof point in Callum’s own county"],
             ["RED Plus excludes Energy Intensive Industries", link("tem tariffs", TEM_TARIFFS), "Qualification rule for the crew"],
         ]), "</div>")

    html(sec("Three limits to design around", "The meter, the scheme and the calendar"),
         '<div class="mt">', cards([
             card(f"RED needs a half-hourly meter ({link('tem FAQs', TEM_FAQS)}). Elexon expects about 80% of all meters "
                  f"on half-hourly settlement by October 2026 and the rest by May 2027 ({link('Elexon', ELEXON_MHHS)}). "
                  "Ask tem whether newly migrated smart meters qualify: if yes, the reachable market widens well beyond "
                  "today’s half-hourly sites.", tag="Half-hourly meters only", title="Roughly 100,000 kWh a year and up"),
             card(f"P442 went live on 27 February 2025 ({link('Elexon', ELEXON_P442)}). Elexon counts "
                  f"{link('four active ESNAs', ELEXON_ESNA)}, and other suppliers sell exempt supply. OVO has told "
                  f"Parliament the exemption shifts levy costs onto other customers ({link('written evidence', OVO_EVIDENCE)}). "
                  "Never build a campaign on the scheme alone.", tag="P442 is shared and exposed",
                  title="Sell the all-in price and the audit"),
             card("Quote forward start dates, as with the June 2027 church tender. Log every contract end date you learn "
                  "in Watt’s Next. That list becomes next year’s pipeline: the <b>renewal radar</b>.",
                  tag="Most prospects are mid-contract", title="Quote forward, log every end date"),
         ], "c3"), "</div>")

    # segments: the table, then a playbook that pulls each segment's thread through the whole strategy
    rows, tier = [], None
    for t, seg, why, who, hook, *_ in SEGMENTS:
        if t != tier:
            tier = t
            rows.append(f'<tr class="tierrow"><td colspan="4">{TIER_NOTE[t]}</td></tr>')
        cls = "" if t == 1 else f" t{t}"
        rows.append(f'<tr><td><span class="tier{cls}">{t}</span>&nbsp; {seg}</td><td>{why}</td><td>{who}</td><td>{hook}</td></tr>')
    html(sec("Targets", "Segments, in order of attack",
             "“Businesses” is too wide a target for three people; the meter rule alone removes most micro-businesses. "
             "Tier 1 first, tier 2 as the engine runs, tier 3 parked or skipped."),
         '<div class="tablewrap mt"><table><thead><tr><th>Segment</th><th>Why it fits</th><th>Who signs</th><th>Best hook</th>'
         '</tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>")

    html('<div class="sec" style="padding-top:26px"><p class="eyebrow">Segment playbook</p>'
         '<h3>One segment, the whole play on one card</h3>'
         '<p class="sub">Pick a segment to see who signs, the hook, the LinkedIn opening angle, where the Demand Atlas '
         'finds them and the opener to send, gathered from across the strategy.</p></div>')
    live = [s for s in SEGMENTS if s[0] < 3]
    with st.container(key="playbook"):
        names = [s[1] for s in live]
        choice = st.selectbox("Segment", names, key=keep("segment", names[0]), on_change=save, args=("segment",),
                              label_visibility="collapsed")
        t, seg, why, who, hook, angle, opener_title, atlas = next(s for s in live if s[1] == choice)
        angle_html = angle or "Use message 1 as written"
        html(f'<p style="margin-top:2px"><span class="badge accent">Tier {t}</span>&nbsp; '
             f'<span class="muted small">{why}</span></p>'
             f'<div class="play"><div><b>Who signs</b>{who}</div><div><b>Best hook</b>{hook}</div>'
             f'<div><b>LinkedIn opening angle</b>{angle_html}</div><div><b>Where the Atlas finds them</b>{atlas}</div></div>')
        if opener_title:
            html(f'<p class="eyebrow" style="margin-top:6px">Opener to swap into message 1 · {e(opener_title)}</p>')
            with st.container(key="tplmsg_playbook"):
                st.code(toolkit.fill(toolkit.opener(opener_title)), language=None, wrap_lines=True)

    html(sec("Triggers and patches", "When a cold prospect becomes a warm one, and where"),
         '<div class="cols wide-left mt"><div>',
         ul([
             "<b>Contract end inside 12 months.</b> The only trigger that matters at quote stage. Everything else is a way of finding it.",
             "<b>New finance or operations lead in the last 90 days.</b> New hires review supplier contracts. Sales Navigator filters for this.",
             "<b>New premises or a new site.</b> A change of tenancy usually means expensive deemed rates.",
             "<b>Out-of-contract rates on the bill.</b> The most urgent case you will meet.",
             "<b>Public talk about energy cost, solar, EV chargers or net zero.</b> They are already thinking about it.",
             f"<b>Budget season and 1 April.</b> TNUoS and CCL rates change each April; CCL rises from 0.801p to 0.827p per kWh in April 2027 ({link('tem tariffs', TEM_TARIFFS)}).",
             "<b>New treasurer, bursar or trustee.</b> The charity and school version of a new FD.",
         ]),
         '</div><div class="stack">',
         subhead("Three home patches of about 50 miles"),
         mini("Swansea and South Wales", "<p><span class='owner'>Callum</span>Gorseinon RFC is a proof point in the same county.</p>"),
         mini("Brighton and Sussex", "<p><span class='owner'>Tom</span></p>"),
         mini("Winnersh and the Thames Valley", "<p><span class='owner'>Jason</span></p>"),
         callout("These match the local-lead buckets already in Watt’s Next. Add a patch around each generator you sign "
                 "to tem, starting with the biogas client that goes live on 3 October."),
         "</div></div>")


# ================================================================ 03 LINKEDIN
def linkedin():
    intro("LinkedIn", "People accept people. Run it through the founders.",
          "Run LinkedIn through the three founders’ personal profiles, not the company page. The company page only has "
          "to pass the credibility check a prospect makes after your request lands. The crew does the research and the "
          "drafting; a founder sends every message by hand.")
    tabs = st.tabs(["Foundations", "Targeting", "Content", "Sequences", "AI workflow", "Numbers", "Paid layer"])

    with tabs[0]:
        html(sec("Part 1 · Foundations", "Each founder’s profile, the company page and the trust pack", first=True),
             '<div class="cols wide-left mt"><div>', subhead("Each founder’s profile"),
             ul([
                 "<b>Headline says what the reader gets.</b> For example: “I X-ray business electricity bills. Co-CEO at RenewaBlox, tem partner.” Job titles alone earn no clicks.",
                 "<b>Location matches the patch.</b> Callum’s profile showed Slough on 2 October. Set it to Swansea: local targeting and “I’m 20 minutes from you” both depend on it.",
                 "<b>Banner carries the offer in one line.</b> “Send one bill. Get a line-by-line audit and a tem quote. Our commission shown in pence.”",
                 "<b>About section in three short paragraphs.</b> The problem, what you do, how to start.",
                 "<b>Featured section holds four things.</b> The Bill X-ray page, a sample audit, your best teardown post, the tem partnership post.",
                 "<b>Get verified and collect two recommendations.</b> An ID badge and a generator’s or client’s recommendation do more than any claim you write yourself.",
                 "<b>Turn on Open Profile</b> once you have Premium or Sales Navigator, so anyone can message you free.",
             ]),
             "</div><div>", subhead("Company page"),
             ul([
                 "Tagline and About repeat the offer, and state the facts a cautious FD looks for: tem partner, Energy Ombudsman ADR member (once confirmed), how you are paid.",
                 "All three of you list RenewaBlox as current employer, with the same wording.",
                 "Two posts a week, mostly reshares of the founders’ best posts and case studies.",
                 "Use the page’s monthly invite-to-follow credits on new connections.",
             ]),
             "</div></div>")
        html(sec("The trust pack", "Build this before sending a single request",
                 "A start-up broker with an unfamiliar supplier has to answer “who are you and what’s the catch?” "
                 "before the conversation starts. Six assets do it."),
             '<div class="grid3 mt">',
             mini("Bill X-ray page with a secure upload", "<p>Host it on a subdomain of the .co.uk domain so renewablox.com stays untouched. Netlify and Supabase, as with Watt’s Next.</p>"),
             mini("A sample audit", "<p>Two pages, anonymised, showing real findings and the side-by-side quote.</p>"),
             mini("“How we’re paid” one-pager", "<p>Commission in p/kWh, the ADR scheme, the complaints route, and the plain statement that you tender to tem rather than the whole market.</p>"),
             mini("A narrow letter of authority", "<p>Data access and quoting only, 12 months, no power to sign contracts. Narrow LOAs get signed faster.</p>"),
             mini("tem’s own material", "<p>Case studies and explainers from the partner hub, used as tem’s guidance says.</p>"),
             mini("A booking link", "<p>A Google Calendar appointment page for a 15-minute results call.</p>"),
             "</div>",
             '<div class="mt">', callout("Do not use the church as a public case study until it has switched and agreed. "
                                        "Describe it without the name or town if you need the VAT and CCL example sooner.",
                                        kind="rule tem"), "</div>")

    with tabs[1]:
        html(sec("Part 2 · Targeting and list building", "Build the list outside LinkedIn, then find the person inside it",
                 "That keeps the crew doing the heavy research on open data and keeps every action on LinkedIn human.", first=True),
             '<div class="cols wide-left mt"><div>', subhead("Start with the network you already have"),
             ul([
                 "<b>Export your own connections.</b> LinkedIn’s data download gives each of you a file of your first-degree connections. The crew can segment it in minutes: who owns or runs a site with a half-hourly meter, who is an adviser, who is a generator.",
                 "<b>Message those people first.</b> A warm note to 50 existing connections will outperform 500 cold requests. Ask each one a single question: “Who do you know with an electricity bill over £30,000 a year?”",
                 "<b>Mine second-degree paths.</b> For every tier 1 account, check who you both know before you send anything. An introduction beats a request.",
             ]),
             '<div style="height:24px"></div>', subhead("Three lists that convert better than any filter"),
             ul([
                 "<b>People who reacted to or commented on your posts.</b> Message within a day.",
                 "<b>People who viewed your profile</b> after a request or a post.",
                 "<b>Attendees of local business events you attend.</b> LinkedIn shows the attendee list for events you have joined.",
             ]),
             "</div><div>", subhead("What the crew adds to each account"),
             '<p class="small muted" style="margin:-4px 0 12px">A five-line research card, built from public sources and stored in Watt’s Next.</p>',
             ol([
                 "What the site is and what probably drives its load.",
                 "Evidence of size: floor area, beds, covers, pupils, or reported kWh where published.",
                 "The trigger, if there is one.",
                 "The hook: which audit finding is most likely for this kind of site.",
                 "A drafted connection note and first message in the founder’s voice.",
             ]),
             "</div></div>")
        html(sec("Sales Navigator set-up", "One seat each, lists named so the CRM can match them",
                 "Build lead lists by patch, segment and buyer, for example <code>SWA-Hospitality-Owner</code>. Save each "
                 "search and switch on alerts: new matches arrive as a feed, and the crew turns them into the next day’s queue."),
             '<div class="mt">', table(["Filter", "Setting", "Why"], [
                 ["Geography", "The founder’s 50-mile patch, by region or postcode", "Local credibility and site visits"],
                 ["Company headcount", "11 to 500", "Big enough for a half-hourly meter, small enough to reach the decision-maker"],
                 ["Industry", "One segment per list", "Lets every message carry a sector-specific finding"],
                 ["Seniority", "Owner, CXO, Director", "People who can sign"],
                 ["Title keywords", "Finance Director, Operations Director, General Manager, Facilities, Estates, Bursar, Treasurer", "The buyers in the segments table"],
                 ["Changed jobs in last 90 days", "On, as a separate list", "The strongest timing trigger LinkedIn can see"],
                 ["Posted in last 30 days", "On, as a priority flag", "Active members accept and reply far more often"],
                 ["Following your company, viewed your profile", "On, checked weekly", "Warmest leads on the platform"],
             ], "compact"), "</div>")

    with tabs[2]:
        pillars = [
            ("Bill teardowns", 40, "One anonymised bill, one finding: “This hotel paid for 250 kVA and never drew more than 140.”", "Shows the product. Every reader checks their own bill"),
            ("Market explainers", 20, "Why standing charges jumped, what changes on 1 April, what P442 is and is not", "Callum already does this on panels and in the Net Zero series"),
            ("Proof and pay", 20, "Quotes won, savings with permission, “here is exactly what we earned on this deal”", "Very few brokers publish their commission before they are asked"),
            ("Building with AI", 10, "What the crew caught this week, how long an audit takes, where a human signs off", "Distinctive, and it draws partners and press as well as customers"),
            ("Generators and place", 10, "The plant, the people, where the money goes", "Sets up strategy B"),
        ]
        rows = [[p, f'<span class="share"><span class="trk"><i style="width:{s / 40 * 100:.0f}%"></i></span>{s}%</span>', w, y]
                for p, s, w, y in pillars]
        html(sec("Part 3 · Content engine", "Content does the trust work so that messages can stay short",
                 "A prospect who receives your request looks at your last three posts before deciding. Those posts should "
                 "show a real bill, a real finding and a plain statement of how you are paid.", first=True),
             '<div class="mt">', table(["Pillar", "Share of posts", "What it looks like", "Why it works"], rows), "</div>")
        html('<div class="cols wide-left mt-l"><div>', subhead("Formats, in order of return"),
             ol([
                 "<b>Document carousels.</b> Six to eight slides: the bill, the finding, the fix, the saving, the offer.",
                 "<b>Short video.</b> Sixty to ninety seconds, a founder talking over the bill on screen.",
                 "<b>Text with one annotated image.</b> The fastest to produce.",
                 "<b>A fortnightly newsletter.</b> Call it The Bill X-ray. LinkedIn notifies subscribers of each issue.",
                 "<b>A monthly live bill clinic.</b> Thirty minutes, three anonymised bills audited live, promoted as a LinkedIn Event.",
             ]),
             '</div><div class="stack">',
             mini("Cadence", "<ul><li>Each founder: two posts a week, Tuesday to Thursday mornings.</li>"
                  "<li>Each founder: 15 minutes a day commenting on posts by target accounts and local connectors. Comments are the cheapest reach on the platform.</li>"
                  "<li>Company page: two reshares a week.</li>"
                  "<li>All three of you engage with each other’s posts in the first hour.</li></ul>"),
             mini("Production line", "<ul><li>The crew drafts only from real artefacts: bills, quotes, tem’s partner material, Callum’s blog. No invented numbers.</li>"
                  "<li>Each founder gets drafts in their own voice, trained on their past writing, and edits for ten minutes before posting.</li>"
                  "<li>Batch six drafts every Sunday. Cobb reviews; a founder approves.</li>"
                  "<li>Every post ends with the same line: “Send one bill and I’ll do yours.”</li>"
                  "<li>Tag tem on partnership posts, and ask your partner manager for a joint post or a joint live session. Their audience is far larger than yours today.</li></ul>"),
             callout("Savings figures are either tem’s, attributed, or your own, evidenced. Never a blend. No customer or "
                     "generator is named without written permission. No engagement pods and no bought followers: they "
                     "distort the only signal you need, which is whether target buyers respond.", "Rules.", "rule"),
             "</div></div>")

    with tabs[3]:
        touches = [
            ("Day 0", "Warm the name", "View the profile, follow the company, and comment on a recent post if there is one.", ""),
            ("Day 1", "Connection request", "Test a blank request against a short note. Free accounts get only a handful of notes a month, so the test matters.", ""),
            ("+1 day", "Message 1, the question", "Within a day of acceptance: ask the contract end date and offer the side-by-side from one bill.", "msg"),
            ("Day 3–4", "Message 2, the sample", "Send the anonymised audit for their sector.", "msg"),
            ("Day 8–10", "Message 3, the mid-contract offer", "End date now, live price six months before, nothing in between. The audit is still worth doing today.", "msg"),
            ("Day 21", "Message 4, the close", "Leave the door open and stop.", "stop"),
        ]
        track = "".join(f'<div class="touch {c}"><div class="dot">{i}</div><div class="day">{d}</div><b>{t}</b><p>{b}</p></div>'
                        for i, (d, t, b, c) in enumerate(touches, 1))
        html(sec("Part 4 · Outreach sequences", "One question, one offer, four touches, then stop",
                 "Every sequence asks “when does your electricity contract end?” and makes one offer, the Bill X-ray. "
                 "Every message is drafted in the Toolkit.", first=True),
             f'<div class="loop mt"><div class="track">{track}</div></div>',
             '<div class="mt">', callout("For tier 1 accounts in the home patch, replace message 2 with a 30-second voice "
                                        "note from the founder. It must be the founder’s real voice.", "Voice note for tier 1"),
             "</div>",
             '<div class="grid3 mt">',
             mini("Rules for every message", "<ul><li>No pitch in the connection request.</li><li>Under 60 words, one idea, one easy question.</li>"
                  "<li>Lead with a finding relevant to their kind of site, not with RenewaBlox.</li>"
                  "<li>Say how you are paid by the second exchange, before they ask.</li>"
                  "<li>Sent by a founder, by hand. The crew drafts; it never sends.</li></ul>"),
             mini("InMail", "<p>Only for people with a clear trigger whom you cannot reach by request: an FD at a company that has published its energy use, or a new arrival in role. Subject under five words, body under 80.</p>"),
             mini("Daily rhythm, per founder", "<p>Twenty-five minutes a day: send 15 to 20 requests from the queue, answer acceptances and replies, leave five comments, tick the queue in Watt’s Next. Reply to any prospect message within two working hours.</p>"),
             "</div>")
        html(sec("When they reply", "Most replies will be “we’re in contract”",
                 "The audit-now, price-later answer turns each one into a future quote instead of a dead end."),
             '<div class="mt">', table(["They say", "You do"], [
                 ["“We’re in contract until 2027”", "Log the date in Watt’s Next. Offer the audit now: capacity, VAT and CCL errors can be fixed mid-contract. Diary a live price six months out"],
                 ["“We already use a broker”", f"Ask if they know that broker’s commission in p/kWh. Suppliers have had to show it on new contracts since 1 October 2024 ({link('Ofgem', OFGEM_PROTECT)}). Offer to price alongside"],
                 ["“Send me something”", "The sample audit and the page link. Follow up in three days"],
                 ["“How do you make money?”", "The one-pager, with the commission figure in the first line"],
                 ["“Never heard of tem”", "tem’s own numbers, attributed; the licensed supply partner; one case study. For a large site, offer a three-way call with tem"],
                 ["Sends a bill", "Audit inside 48 hours, letter of authority for half-hourly data, tem tender, results call"],
                 ["“Not interested”", "Thank them, stop, mark do-not-contact"],
                 ["Silence after message 4", "No more messages. They stay in your content audience"],
             ], "compact"), "</div>")
        html(sec("Variants by segment", "Swap one of these into message 1 in place of the general question",
                 "The Offer page’s segment playbook pairs each with its opener."),
             '<div class="mt">', table(["Segment", "Opening angle"], [
                 ["Hospitality", "Agreed capacity against real peak demand"],
                 ["Manufacturing and food", "Reactive power and capacity charges"],
                 ["Care homes", "Fixed forward price for a 24-hour load"],
                 ["Churches and charities", "VAT and CCL check, with refunds for past overcharges"],
                 ["Schools", "Forward quote for the next academic year, shown to governors as a side-by-side"],
                 ["Sports clubs", "Gorseinon RFC’s result with tem"],
                 ["New FD or operations lead", "A supplier-contract checklist for their first 90 days"],
                 ["Farms near a generator", "The local plant now selling through tem"],
                 ["FDs at companies that publish energy data", "The pre-priced memo (strategy A)"],
             ], "compact"), "</div>")

    with tabs[4]:
        steps = [
            ("Account list", "Builds it from open data, the web and the CRM", "Approves the segment"),
            ("Finding the person", "Suggests names and titles from company sites and Companies House", "Finds and saves the lead in Sales Navigator"),
            ("Research card", "Writes the five lines", "Skims them"),
            ("Messages", "Drafts the note and four messages in the founder’s voice", "Edits and sends by hand"),
            ("Replies", "Drafts the answer, updates Watt’s Next, books the diary", "Sends; takes the call"),
            ("Audit and quote", "Bill to audit, tem tender by email, side-by-side", "Signs off every quote"),
            ("Content", "Drafts from real artefacts", "Edits and posts"),
            ("Quality", "Cobb reviews everything; morning digest to Callum", "Daily review"),
        ]
        body = "".join(f'<tr><td>{s}</td><td class="crew">{c}</td><td>{f}</td></tr>' for s, c, f in steps)
        html(sec("Part 5 · AI workflow", "Research and drafting at a depth no broker can match by hand. Not automated sending.",
                 f"LinkedIn bans third-party tools that automate activity and restricts accounts that use them "
                 f"({link('LinkedIn Help', LINKEDIN_HELP)}). A restricted founder account would cost more than any tool could save.",
                 first=True),
             '<div class="tablewrap mt"><table class="compact lanes"><thead><tr><th>Step</th><th class="crew">The crew</th>'
             f'<th class="founder">The founder</th></tr></thead><tbody>{body}</tbody></table></div>',
             '<div class="cols mt">',
             callout("Today’s 20 names per founder, the card, the drafts, and a status dropdown (sent, accepted, replied, "
                     "bill in). Updating it takes seconds and gives you clean funnel data.",
                     "The one piece of software to build is a LinkedIn queue view in Watt’s Next."),
             callout("Nothing automated touches linkedin.com: no auto-connect tools, no scraping extensions, no shared "
                     "logins, no agent browsing a founder’s account. Vendors sell “safe” automation; LinkedIn’s own page "
                     "makes no such exception. Allowed and useful: Sales Navigator, native post scheduling, your own data "
                     "export, LinkedIn Ads and Lead Gen Forms.", "The hard line.", "rule tem"),
             "</div>")

    with tabs[5]:
        numbers_tab()

    with tabs[6]:
        _, _, _, per_bill = funnel()
        html(sec("Paid layer", "Only after organic works",
                 "Start paid after ten bills have arrived organically, so you know which message converts.", first=True),
             '<div class="mt">', cards([
                 card("Sponsor a founder’s best teardown post to a company list uploaded from Watt’s Next.", tag="Thought Leader Ads"),
                 card("“Free Bill X-ray”, asking only name, company and contract end month.", tag="Lead Gen Form"),
                 card("People who visited the page or watched half a video.", tag="Retargeting"),
                 card(f"£1,500 over six weeks. On the funnel’s current assumptions a bill is worth about "
                      f"<b>{money(per_bill)}</b> of first-year commission, so stop if a bill costs more than £150.",
                      tag="Budget and stop rule"),
             ]), "</div>")


def numbers_tab():
    html(sec("Limits and numbers", "What LinkedIn outbound will produce",
             "Planning assumptions, not benchmarks. Each bar is the share of the previous stage that carries through; "
             "the figure at the right is the monthly result. Move the sliders to your own rates after four weeks.", first=True))
    left, right = st.columns([1.45, 1], gap="large")
    with right:
        with st.container(key="calc"):
            html('<p class="eyebrow">Assumptions</p>')
            st.slider("Requests a week, per founder", 10, 100, step=5, key=keep("f_per_week", 80),
                      on_change=save, args=("f_per_week",), help="LinkedIn reportedly allows about 100 a rolling week.")
            st.slider("Founders sending", 1, 3, key=keep("f_founders", 3), on_change=save, args=("f_founders",))
            c1, c2 = st.columns(2)
            with c1:
                st.slider("Accepted %", 5, 60, key=keep("f_acc", 30), on_change=save, args=("f_acc",))
                st.slider("Bills received %", 5, 80, key=keep("f_bill", 35), on_change=save, args=("f_bill",))
                st.slider("Contracts signed %", 5, 80, key=keep("f_close", 30), on_change=save, args=("f_close",))
            with c2:
                st.slider("Conversations %", 5, 50, key=keep("f_conv", 15), on_change=save, args=("f_conv",))
                st.slider("Quotable %", 10, 100, key=keep("f_quote", 60), on_change=save, args=("f_quote",))
                st.slider("Commission, p/kWh", 0.25, 3.0, step=0.05, key=keep("f_pence", 1.0),
                          on_change=save, args=("f_pence",), format="%.2f")
            st.slider("Median site, MWh a year", 50, 1000, step=10, key=keep("f_mwh", 200),
                      on_change=save, args=("f_mwh",))
            st.button("Reset to the plan’s assumptions", on_click=reset_funnel, icon=":material/restart_alt:",
                      type="tertiary")
    a, s, commission, per_bill = funnel()
    with left:
        stages = [
            ("Requests sent", f"{a['per_week']} a week each", None, s[0]),
            ("Accepted", f"{a['acc']}% of requests", a["acc"], s[1]),
            ("Real conversations", f"{a['conv']}% of acceptances", a["conv"], s[2]),
            ("Bills received", f"{a['bill']}% of conversations", a["bill"], s[3]),
            ("Quotable now or forward", f"{a['quote']}% of bills", a["quote"], s[4]),
            ("Contracts signed", f"{a['close']}% of quotes", a["close"], s[5]),
        ]
        rows = []
        for i, (lab, sub, rate, val) in enumerate(stages):
            last = " last" if i == len(stages) - 1 else ""
            if rate is None:
                founders = "founder" if a["founders"] == 1 else "founders"
                bar = f'<i style="width:100%"></i><em style="left:10px;color:var(--on-accent)">{a["founders"]} {founders}</em>'
            else:
                bar = f'<i style="width:{rate}%"></i><em style="left:calc({rate}% + 8px)">{rate}%</em>'
            unit = "<small>a month</small>" if i == 0 else ""
            rows.append(f'<div class="frow{last}" title="{e(lab)}: about {approx(val)} a month">'
                        f'<div class="lab">{lab}<small>{sub}</small></div><div class="bar">{bar}</div>'
                        f'<div class="val">~{approx(val)}{unit}</div></div>')
        site = f"{a['mwh'] * 1000:,}"
        html('<div class="stats">',
             stat(approx(s[5]), "Contracts a month", cls="hot"),
             stat(money(commission), "Annual commission added each month", "a year"),
             stat(money(per_bill), "First-year commission one bill is worth"),
             "</div>",
             f'<div class="funnel mt" role="img" aria-label="Monthly funnel on the current assumptions">{"".join(rows)}</div>',
             f'<p class="figcap">From about {approx(s[0])} requests a month to about {approx(s[5])} contracts. At a {site} kWh '
             f'median site and {a["pence"]:g}p/kWh, they add about {money(commission)} of annual commission each month: '
             'a steady drip, not a business. Warm lists, content and the three strategies are where one relationship brings ten meters.</p>')
        if a["acc"] < 25:
            html(callout("If acceptance drops under 25%, fix the profile and the targeting before sending more.",
                         "Acceptance is under 25%.", "correction"))

    html('<div class="cols wide-left mt-l"><div>',
         table(["Limit", "Reported level", "Plan at"], [
             ["Connection requests", "About 100 per rolling week, on every account tier", "80 a week per founder"],
             ["Personalised notes, free accounts", "About 5 a month", "Use paid seats, or send blank"],
             ["Note length", "200 characters free, 300 paid", "Write to 200"],
             ["InMail credits, Sales Navigator", "50 a month, returned if the recipient replies", "Triggered accounts only"],
             ["Pending requests", "No stated cap", "Withdraw after three weeks"],
         ], "compact"),
         f'<p class="small muted" style="margin-top:8px">LinkedIn publishes few numbers. These are widely reported by tool '
         f'vendors ({link("example", SALESFORGE)}); treat them as approximate.</p>',
         "</div><div>",
         callout("Requests sent, acceptance rate, reply rate, bills received, letters of authority signed, quotes issued, "
                 "contracts signed, kWh under contract. If acceptance drops under 25%, fix the profile and the targeting "
                 "before sending more.", "Weekly numbers, per founder."),
         "</div></div>")


# ================================================================ 04 THREE STRATEGIES
def strategies():
    intro("Three strategies", "Where one relationship brings many meters",
          "Cold LinkedIn is a drip. These three plays each use something RenewaBlox has that an ordinary broker does "
          "not: agents that can read thousands of filings, generators of its own, and partners who already hold their "
          "clients’ bills.")
    tabs = st.tabs(["A · Demand Atlas", "B · Local Power", "C · Borrowed trust"])

    with tabs[0]:
        html(sec("Strategy A · Demand Atlas", "Price it before you meet them",
                 "For thousands of UK organisations, annual energy use is already public. The crew can read it, estimate "
                 "the electricity bill, and put a one-page memo with the prospect’s own number on the finance director’s "
                 "desk before anyone has spoken. You did this by hand for two law firms from their Scope 2 figures. This "
                 "industrialises it. You already have an Atlas of generation sites; this is the same idea for demand, and "
                 "it belongs in the same BigQuery project.", first=True),
             '<div class="mt">', table(["Source", "What it gives", "Best for"], [
                 ["Annual accounts at Companies House", f"Large companies and LLPs must report UK energy use in kWh ({link('SECR', CROWE_SECR)}): two of £36m turnover, £18m balance sheet, 250 staff", "Mid-market finance directors"],
                 ["Published Scope 2 emissions", "Electricity use, back-calculated with the grid factor", "Professional services, multi-site groups"],
                 ["Display Energy Certificates and non-domestic EPCs", f"Energy ratings and floor area for public-facing and commercial buildings ({link('open data', EPC_DATA)})", "Leisure, education, large premises"],
                 ["DfE school financial benchmarking", f"Utilities spend for every academy and trust ({link('example', DFE_EXAMPLE)})", "Trust finance leads and bursars"],
                 ["CQC care directory", "Care homes, providers and bed numbers", "Care groups"],
                 ["FSA approved food establishments", "Meat, dairy and fish plants, cold stores", "Refrigeration-heavy sites"],
                 ["Environment Agency permits", "Intensive poultry and pig units, food and drink plants", "Farms and factories with large loads"],
                 ["Charity accounts", "Premises and utility costs for larger charities", "Churches and charities"],
                 ["VOA rating list", "Floor area and use of every rated property", "Sizing everything else"],
             ], "compact"),
             '<p class="small muted" style="margin-top:8px">The crew should confirm each dataset’s licence and field '
             'definitions in week one. The EPC data carries restrictions on its address fields: use it for sizing, and '
             'take postal addresses from the organisation’s own website.</p></div>')
        html('<div class="cols wide-left mt-l"><div>', subhead("The memo: one page, addressed to a named person"),
             ul([
                 "Their number, with the source and page it came from.",
                 "An estimated annual electricity cost, as a range, with the working shown.",
                 "What RED and RED Plus change, in tem’s words and attributed to tem. No promised saving.",
                 "The three checks a Bill X-ray would run on a site like theirs.",
                 "One action: a QR code to the secure upload, or “reply with one bill”.",
                 "Who you are, how you are paid, and how to opt out.",
             ]),
             '<div style="height:24px"></div>', subhead("Delivery: three touches in one week"),
             ol([
                 "<b>Post.</b> A printed letter to the named finance lead at the trading address. A letter with the reader’s own filed number in it gets opened. Postal marketing sits outside the email rules, though data protection law still applies to the named person.",
                 "<b>LinkedIn.</b> The founder connects and mentions the letter.",
                 "<b>Email from the crew.</b> Limited companies and LLPs only, as the Compliance page explains.",
             ]),
             '</div><div class="stack">',
             mini("Quality gate", "<ul><li>Use only an explicit electricity figure. SECR totals often mix fuels and cover a whole group; where that is so, say so on the memo.</li>"
                  "<li>Cobb checks every extraction against its source. A founder samples one memo in five before anything is posted.</li>"
                  "<li>Present estimates as estimates. Misleading business-to-business claims are unlawful as well as bad for trust.</li></ul>"),
             mini("Where it will and will not work", "<p>The largest reporters already have a consultant and a flexible purchasing contract. Aim at the lower end: organisations using roughly 0.5 to 5 GWh a year, where the FD still signs the energy contract personally.</p>"),
             callout("Pick one vertical in the three home patches. Build 200 records. Send 50 memos. Count replies and "
                     "bills received per 100 memos, then decide whether to scale.", "First 30 days.", "decision"),
             "</div></div>")

    with tabs[1]:
        steps = [
            ("A generator joins tem", "signed through RenewaBlox"),
            ("Its story goes local", "owner-led notes, site breakfast"),
            ("Neighbours send bills", "audited and priced together"),
            ("Local businesses switch", "more demand on the platform"),
            ("The generator benefits", "and refers the next plant"),
        ]
        loop = "".join(f'<div class="lstep"><span class="n">0{i}</span><b>{t}</b><span>{s}</span></div>'
                       for i, (t, s) in enumerate(steps, 1))
        html(sec("Strategy B · Local Power", "Let each generator recruit its neighbours",
                 "You sign generators as well as customers, and ordinary brokers do not. Each generator you bring to tem "
                 "is a local landmark, run by someone who knows every business owner for 20 miles and has a commercial "
                 "reason to help. Build one campaign around each plant.", first=True),
             f'<div class="loop mt"><div class="loop-steps">{loop}</div>'
             '<div class="loop-back"><span>↺ the satisfied owner refers the next plant, and the loop restarts</span></div>'
             '<p class="loop-core"><b>RenewaBlox runs every turn:</b> the story pack, the Bill X-rays, the tem quotes, the matched demand.</p></div>')
        why, side = st.columns([1.25, 1], gap="large")
        with why:
            html('<div class="stack mt">',
                 mini("Why the generator will help",
                      f"<ul><li><b>It pays them.</b> tem says qualifying generators earn extra on exempt output matched to business demand ({link('ADBA listing', ADBA)}). tem’s 2025 generator blog put this at £20 to £30 per MWh; that page has moved, so confirm the current figure.</li>"
                      "<li><b>They have the relationships.</b> Feedstock suppliers, hauliers, tenants, the NFU branch, the rugby club.</li>"
                      "<li><b>They want the story told.</b> Most small generators have never had a marketing budget.</li></ul>"),
                 callout("tem matches across its whole portfolio, many generators to many businesses. Before any campaign says "
                         "“buy your power from the plant down the road”, ask tem whether a named generator can be paired with "
                         "named local customers under RED Plus, and what a customer may say in public about where its power "
                         "comes from. Until you have answers, the honest line is: “Buy on the same platform as this plant, and "
                         "see what share of your power is tied to real UK generators.”",
                         "One question to settle with tem first.", "decision"),
                 "</div>")
        with side:
            with st.container(key="sizing"):
                html('<p class="eyebrow">Sizing</p><h4 style="margin:8px 0 2px">How many neighbours one plant covers</h4>'
                     '<p class="small muted">The plan’s example: a 500 kW engine at 90% load.</p>')
                c1, c2 = st.columns(2)
                with c1:
                    kw = st.number_input("Engine size, kW", 50, 5_000, step=50, key=keep("g_kw", 500),
                                         on_change=save, args=("g_kw",))
                with c2:
                    lf = st.slider("Load factor %", 30, 100, key=keep("g_lf", 90), on_change=save, args=("g_lf",))
                gwh = kw * lf / 100 * 8760 / 1e6
                sites = gwh * 1e6 / 200_000
                html('<div class="stats">', stat(f"{gwh:.1f}", "A year of output", "GWh"),
                     stat(f"~{sites:.0f}", "Sites of 200,000 kWh it could cover: the campaign’s natural target", cls="hot"),
                     "</div>")
            html(callout("The biogas client goes live on tem on 3 October. This week, ask the owner for three things: "
                         "permission to tell the story, a list of trading partners, and a date in November for a site breakfast.",
                         "First move.", "decision"))
        html(sec("The campaign kit", "Six things per generator"),
             '<div class="grid3 mt">',
             mini("Permission and a story pack", "<p>Photos, a 60-second film, a one-page fact sheet.</p>"),
             mini("A demand map", "<p>Every likely half-hourly site within 20 miles, plus the generator’s own trading partners. The crew builds it from the Demand Atlas data and publishes it as a Felt map.</p>"),
             mini("Owner-led introductions", "<p>Fifteen personal notes from the owner, drafted by the crew: “We now sell our power through tem. The people who arranged it will check your bill for nothing.”</p>"),
             mini("A site breakfast", "<p>A tour of the plant, then three bills audited live.</p>"),
             mini("Local press and LinkedIn", "<p>The local paper, parish and trade newsletters, and founder posts tagged to the area.</p>"),
             mini("A group tender day", "<p>One date by which local businesses send bills, priced together. A deadline and good company both speed decisions.</p>"),
             "</div>",
             '<div class="cols wide-left mt">',
             callout("An AD plant’s feedstock comes from food manufacturers, farms and hospitality: large electricity users "
                     "with sustainability teams. Offer them power from the platform their own waste supplies. “Your waste, "
                     "your power” is a story their marketing team will tell for you. The 129 AD sites in your SAM pipeline "
                     "are therefore 129 doors into food and farming supply chains. Add one question to every AD "
                     "conversation: “Who supplies your feedstock?”", "The circular version for anaerobic digestion."),
             callout("Introductions made, bills received, MWh signed within 20 miles, and new generators referred by the "
                     "owner.", "Numbers to watch, per generator.", "rule"),
             "</div>")

    with tabs[2]:
        html(sec("Strategy C · Borrowed trust", "Partners who already hold the bills",
                 "Recruit 30 advisers who each have 100 business clients, instead of finding 3,000 businesses yourself. "
                 "The sharpest version starts with accountants and bookkeepers: they already hold a year of every client’s "
                 "electricity invoices in their bookkeeping apps. With client consent, the crew can X-ray a whole client "
                 "book overnight.", first=True),
             '<div class="cols wide-left mt"><div>', subhead("X-ray the book, in five steps"),
             ol([
                 "The practice signs a short partner agreement covering data sharing and how any fee is disclosed.",
                 "It emails clients a one-click consent, from a template you supply (in the Toolkit).",
                 "For clients who agree, it exports 12 months of electricity invoices from Dext, Hubdoc or AutoEntry to your secure upload.",
                 "The crew audits them overnight and returns a ranked list: who has a half-hourly meter, whose contract ends when, and where VAT, CCL or capacity looks wrong.",
                 "The accountant and a founder call the top five clients together.",
             ]),
             '<p class="small" style="margin-top:14px;color:var(--ink-2)">The accountant gets an advisory win with no work, '
             'and a quarterly list of client contracts coming up for renewal. You get warm introductions, with the bills already in hand.</p>',
             '</div><div class="stack">',
             mini("Terms that make partners say yes", "<ul><li>A pilot with no commitment: five bills, results in a week.</li>"
                  "<li>A co-branded report they can send under their own name.</li><li>No exclusivity and no targets.</li>"
                  "<li>Any referral fee printed on the customer’s quote in p/kWh. Accountants answer to their institute on commissions, and many will prefer a client benefit or a charity donation to a fee.</li>"
                  "<li>A tracked Bill X-ray link per partner, so Watt’s Next attributes every bill.</li></ul>"),
             callout("A sports club or church gets its own bill checked first. If it saves, it has a story, as Gorseinon "
                     "RFC does with tem. It then introduces the sponsors and members who own businesses. For each meter "
                     "that switches, the club receives a fixed donation, shown on the customer’s quote. A sponsor board "
                     "is a list of local businesses with a reason to say yes.", "The affinity model."),
             "</div></div>")
        html(sec("Partner types", "Who holds the door",
                 "Search each home patch in Sales Navigator for accountants, bookkeepers, property agents and installers, "
                 "and run the same four-touch sequence with a different offer: “Can I X-ray five of your clients’ bills, "
                 "free, so you can see what comes back?”"),
             '<div class="mt">', table(["Partner", "Why they hold the door", "First move"], [
                 ["Accountants and bookkeepers", "Hold the invoices; trusted on cost", "Offer to X-ray five clients free, results in a week"],
                 ["Fractional FDs and turnaround advisers", "Paid to cut costs quickly", "Same pilot, one client"],
                 ["Commercial property agents and solicitors", "See every lease start, when tenants land on deemed rates", "A “new tenant energy pack” they hand over with the keys"],
                 ["Managing agents of estates and business parks", "One relationship, many meters", "A group tender day for the estate"],
                 ["Solar, EV-charger and M&amp;E installers", "On site when load changes; often hold half-hourly data", "A joint quote: cheaper import now, and export sold through tem later"],
                 ["Land agents and farm advisers", "Farms have both generation and demand", "Join their client newsletter with one worked example"],
                 ["Chambers, BIDs and trade bodies", "Members’ trust and a ready-made room", "A live bill clinic at their next meeting"],
                 ["Clubs, churches and charities", "Members and sponsors own businesses", "“Switch and the club earns”"],
                 ["The Bitcoin Business Network", "Already yours", "The first group tender"],
                 ["Boardy", "Already in motion", "Supply the references it asked for"],
             ], "compact"), "</div>",
             '<div class="cols mt">',
             callout("Two accounting practices, one installer, one property agent, one club or church, and a first group "
                     "tender for the Bitcoin Business Network.", "Sixty-day target.", "decision"),
             callout("Partners are busy: do all the work for them, including the client email. Client data: nothing moves "
                     "without the client’s consent and a data-sharing agreement. One bad audit burns a partner: every "
                     "partner audit gets founder sign-off.", "What can go wrong.", "rule tem"),
             "</div>")


# ================================================================ 05 THE PLAN
def gantt(d):
    def pos(day):
        return (day - PLAN_START).days / CHART_DAYS * 100

    weeks = "".join(f"<div><b>W{i + 1}</b>{short(PLAN_START + timedelta(weeks=i))}</div>" for i in range(14))
    lanes = []
    _, _, live = plan_status(d)
    for ph in PHASES:
        left, right = pos(ph["start"]), pos(ph["end"] + timedelta(days=1))
        state = "now" if ph["n"] == live and PLAN_START <= d <= PLAN_END else "done" if d > ph["end"] else ""
        top = (ph["n"] - 1) * 52
        lanes.append(
            f'<div class="pbar {state}" style="left:{left:.2f}%;width:{right - left:.2f}%;top:{top}px;padding:0;height:12px;border-radius:6px;'
            f'background:{"var(--muted-2)" if state == "done" else "var(--accent)"};border:0"></div>'
            f'<div class="glab" style="left:{left:.2f}%;top:{top + 16}px">'
            f'<span style="font-weight:700;font-size:13.5px">{ph["n"]} · {ph["name"]}</span> '
            f'<span class="mono" style="font-size:10.5px;color:var(--muted)">{ph["dates"]}</span></div>')
        g = pos(ph["end"] + timedelta(days=1))
        name, _, short_text = ph["gate"]
        align = "left:-6px;text-align:left" if g < 20 else "right:-6px;text-align:right" if g > 80 else "left:50%;transform:translateX(-50%);text-align:center"
        lanes.append(
            f'<div class="gate-m" style="left:{g:.2f}%;top:{3 * 52 + 4}px"></div>'
            f'<div style="position:absolute;left:{g:.2f}%;top:{3 * 52 + 24}px;width:0">'
            f'<div class="glab gate-l2" style="{align}">'
            f'<b style="display:block;color:var(--heat-d);font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;text-transform:uppercase">{name}</b>'
            f'{short_text}</div></div>')
    today_html = ""
    if PLAN_START <= d <= PLAN_END + timedelta(days=2):
        x = pos(d) + 0.5 / CHART_DAYS * 100
        flag = ' style="left:auto;right:-2px"' if x > 85 else ""   # keep the flag inside the chart
        today_html = (f'<div class="today" style="left:{x:.2f}%">'
                      f'<span{flag}>Today · {short(d)}</span></div>')
    return (f'<div class="gantt"><div class="gantt-in"><div class="weeks">{weeks}</div>'
            f'<div class="lanes-g" style="height:{3 * 52 + 84}px;margin-top:22px">{"".join(lanes)}{today_html}</div></div></div>'
            '<p class="gantt-note">Three phases, each closed by a gate with a measurable test.</p>')


def plan():
    intro("How the channels work together", "One spine, then fourteen weeks",
          "Every channel feeds the Bill X-ray, every bill lands in Watt’s Next, and every contract end date goes on the "
          "renewal radar. Build the trust pack in two weeks, run LinkedIn and one campaign per strategy for six, then "
          "spend December doubling what worked. The plan lands on the January to March quoting season, when businesses "
          "with April contract starts are choosing suppliers.")
    d = today()
    label, sentence, live = plan_status(d)
    html(sec("The first 14 weeks · 5 October to 8 January", "Two weeks to build, six to run, six to prove and scale",
             "Each phase ends at a gate. If a gate is missed, fix that before taking on the next phase’s work.", first=True),
         f'<p class="mt"><span class="badge tem">{e(label)}</span>&nbsp; <span style="color:var(--ink-2)">{e(sentence)}</span></p>',
         '<div class="mt">', gantt(d), "</div>")

    left, right = st.columns([3, 2], vertical_alignment="center")
    with left:
        html('<p class="eyebrow">Who does what</p><p class="small muted" style="margin-top:6px">Owners are a first guess: '
             'Tom, as CTO, takes the builds; Jason takes partners and networks; swap freely.</p>')
    with right:
        who = st.segmented_control("Show tasks for", ["Everyone", "Callum", "Tom", "Jason"],
                                   key=keep("owner", "Everyone"), on_change=save, args=("owner",),
                                   label_visibility="collapsed", width="stretch")
    who = who or "Everyone"

    cols = st.columns(3, gap="small")
    for col, ph in zip(cols, PHASES):
        tasks = [(o, t) for o, t in ph["tasks"]
                 if who == "Everyone" or who in o or o in ("All three", "Each founder")]
        items = "".join(f'<li><span class="owner">{o}</span>{t}</li>' for o, t in tasks)
        hidden = len(ph["tasks"]) - len(tasks)
        more = f'<p class="small muted" style="margin-top:10px">+{hidden} for the others</p>' if hidden else ""
        now = ph["n"] == live
        badge = ""
        if now:
            badge = '<span class="badge tem">Now</span>' if PLAN_START <= d <= PLAN_END else '<span class="badge accent">Up next</span>'
        gate_name, gate_text, _ = ph["gate"]
        with col:
            html(f'<div class="phase{" now" if now else ""}"><h4>Phase {ph["n"]} · {ph["name"]} {badge}</h4>'
                 f'<div class="dates">{ph["dates"]}</div><ul class="check">{items}</ul>{more}'
                 f'<div class="gate"><div class="d">{gate_name}</div><div class="t">{gate_text}</div></div></div>')
    html(callout("About four hours a week each: 25 minutes a day on LinkedIn, half an hour editing posts, and the rest on "
                 "results calls. Site events and partner meetings come on top. If that is more than you have, drop "
                 "strategy A to phase 3 rather than thinning everything.", "Founder time.", "rule"))

    html(sec("Email and LinkedIn", "Rules of engagement"),
         '<div class="cols mt"><div>',
         ul([
             "<b>One owner per prospect at a time.</b> An “active channel” field in Watt’s Next. The crew’s emails pause the moment a founder opens a LinkedIn conversation, and the reverse.",
             "<b>Email leads outside the home patches, to limited companies and LLPs.</b> LinkedIn and post lead inside the patches, and for sole traders and partnerships, whom the email rules treat as individuals.",
             "<b>An email reply or click moves the prospect to a founder’s LinkedIn queue the same day.</b> A human follow-up within hours is where the two channels multiply.",
             "<b>One suppression list.</b> Anyone who says no on any channel comes off all of them.",
             "<b>One offer, one page, one set of words.</b> The Bill X-ray, everywhere.",
         ]),
         "</div><div>", subhead("Who leads"),
         '<div class="matrix">'
         '<div></div><div class="h">Limited company or LLP</div><div class="h">Sole trader or partnership</div>'
         '<div class="r">Inside a home patch</div>'
         '<div class="c li"><b>A founder on LinkedIn</b>Post for Atlas memos; the crew drafts</div>'
         '<div class="c li"><b>A founder on LinkedIn, or post</b>Introductions where you can get them</div>'
         '<div class="r">Outside the patches</div>'
         '<div class="c em"><b>Email from the crew</b>Signed as written on a founder’s behalf; opt-out in every email</div>'
         '<div class="c po"><b>Introduction, post or content</b>No email without consent</div>'
         "</div></div></div>")

    html('<div class="sec"></div><div class="cols"><div>',
         '<p class="eyebrow">The renewal radar</p><h3 style="margin:9px 0 16px">Every mid-contract prospect becomes a dated opportunity</h3>',
         ol([
             "Every conversation ends with a contract end date, or a note of why there is none.",
             "The crew sets reminders at 12, 6 and 3 months before that date, and records the notice period.",
             "At six months it requests a live tem price and sends the side-by-side, to prospects who agreed to receive it.",
             "Partners receive a quarterly list of their own clients’ upcoming dates.",
         ]),
         '<p class="small" style="margin-top:14px;color:var(--ink-2)">After a year of LinkedIn outreach alone, on the '
         'planning assumptions, the radar should hold well over 100 dated contracts. That calendar is worth more than the '
         'first three months of sales.</p>',
         "</div><div>",
         '<p class="eyebrow">The data flywheel</p><h3 style="margin:9px 0 16px">The one asset a competing broker cannot copy</h3>',
         '<p style="color:var(--ink-2)">Every audit adds to a private benchmark set: unit rates, capacity headroom, and how '
         'often VAT, CCL or reactive power is wrong, by sector. After 50 audits you can publish “what we found in 50 bills”. '
         'That feeds content, press and partner pitches, and it is the one asset a competing broker cannot copy from tem’s panel.</p>',
         "</div></div>")

    html(sec("Seven more plays on the bench", "Later, in this order"),
         '<div class="mt">', table(["Play", "What it is", "When"], [
             ["Search and AI-answer intercept", "Publish the clearest independent explainers of RED, RED Plus and P442 eligibility. A business pitched tem by another broker searches for exactly this, and comparison sites answer today", '<span class="badge accent">Month 2</span>'],
             ["Live bill clinic", "Monthly, 30 minutes, three anonymised bills", '<span class="badge accent">Month 2</span>'],
             ["Joint activity with tem", "A shared webinar, case study or podcast slot", '<span class="badge tem">Ask now</span>'],
             ["Press", "The AI crew story for trade press; generator stories for local press", '<span class="badge quiet">With the first switch</span>'],
             ["Reviews", "Ask every audited business for a Google or Trustpilot review, switch or no switch", '<span class="badge quiet">From the first audit</span>'],
             ["Free tools", "A capacity checker for half-hourly data; a VAT and CCL eligibility check for charities", '<span class="badge accent">Month 3</span>'],
             ["Tender watch", "The crew monitors public notices from small bodies buying electricity outside frameworks", '<span class="badge quiet">Later</span>'],
         ], "compact"), "</div>")


# ================================================================ 06 COMPLIANCE & SOURCES
def compliance():
    intro("Compliance and risk", "The rules mostly reward what this plan already does",
          "Disclose commission, keep humans on LinkedIn, and filter email by legal form. Two points need a decision from "
          "you, marked below. This is a working checklist, not legal advice.")
    html(sec("Two decisions for you", "Settle these before scaling", first=True),
         '<div class="cols mt">',
         callout("You tender to tem, not to the whole market. State it on the “How we’re paid” page and in every audit. "
                 "<b>Decide</b> whether to add one or two comparison suppliers for credibility.",
                 "Single supplier", "decision"),
         callout(f"The ICO counts private messages on social media as electronic mail ({link('ICO', ICO_EMAIL)}). How that "
                 "applies to one-to-one business messages is a grey area most of the market ignores. <b>Decide</b> to take "
                 "a short legal view before scaling.", "LinkedIn messages", "decision"),
         "</div>")
    dec = '<br><span class="badge decision" style="margin-top:6px">Decision</span> '
    html(sec("The checklist", "Thirteen rules and risks, and what to do about each"),
         '<div class="mt">', table(["Area", "The rule or risk", "What to do"], [
             ["Broker status", f"Suppliers must show broker fees on all non-domestic contracts signed since 1 October 2024, and may only take small-business contracts from brokers in a redress scheme ({link('Ofgem', OFGEM_PROTECT)})",
              "Complete Energy Ombudsman membership before the first quote. Show your commission before the supplier has to"],
             ["Coming regulation", f"Government intends to make Ofgem the regulator of brokers, with powers to set rules and authorise them. Ofgem’s call for input ran from 4 June to 17 July 2026 ({link('Ofgem', OFGEM_TPI)})",
              "Build to the likely standard now: written disclosure, a complaints process, recorded consent, an audit trail. Say so in public"],
             ["Single supplier", "You tender to tem, not to the whole market",
              f"State it on the “How we’re paid” page and in every audit.{dec}whether to add one or two comparison suppliers for credibility"],
             ["Savings claims", "Misleading business-to-business marketing is unlawful, and the 30% figure is tem’s, not yours",
              "Attribute, use ranges, keep an evidence file. Never present RED Plus as guaranteed beyond the contract term"],
             ["Email from the crew", f"The email consent rule does not cover companies and LLPs. Sole traders and ordinary partnerships count as individuals and need consent ({link('ICO', ICO_B2B)})",
              "Filter every list by legal form at Companies House. Reach farms, pubs and other partnerships by introduction, post or content. Identify the sender and offer an opt-out in every email"],
             ["LinkedIn messages", f"The ICO counts private messages on social media as electronic mail ({link('ICO', ICO_EMAIL)}). How that applies to one-to-one business messages is a grey area most of the market ignores",
              f"Keep messages individual and relevant, ask before sending material, stop at the first objection.{dec}take a short legal view before scaling"],
             ["LinkedIn terms", f"No third-party automation or scraping ({link('LinkedIn Help', LINKEDIN_HELP)})", "Founders send by hand. The crew never touches the site"],
             ["Phone", "Cold calls to businesses must be screened against the preference registers, and automated calls need consent",
              "Do neither. Make “we never cold call” a public promise"],
             ["Personal data", "Named contacts, bills and half-hourly data are personal or confidential",
              "A legitimate-interests assessment for outreach, a privacy notice on the X-ray page, data-sharing terms with partners, a narrow letter of authority, a retention limit"],
             ["AI disclosure", "An agent writing as if it were a founder is a trust risk", "Keep signing crew emails as written on a founder’s behalf, as you do now"],
             ["AI error", "A wrong audit or memo sent in your name", "Founder sign-off on every quote and memo. Cobb’s checks logged"],
             ["P442 policy", "The exemption moves levy costs onto other customers and has critics in Parliament", "Sell the all-in price. Treat RED Plus as a bonus line"],
             ["Dependence on tem", "One supplier, with terms you cannot negotiate", "Keep the audit valuable on its own, so the relationship with the customer is yours"],
         ]), "</div>")

    opened = '<span class="badge accent">Opened in full</span>'
    extract = '<span class="badge quiet">Search extract</span>'
    html(sec("Sources and how each was checked", "All checked on 2 October 2026",
             "Where a row says “search extract”, the relevant passage of the page was seen in search results but the "
             "whole page was not opened."),
         '<div class="mt">', table(["Source", "Used for", "How checked"], [
             [link("tem FAQs", TEM_FAQS), "Brokers selling RED, the half-hourly meter rule, the 30% claim, the licensed supply partner", opened],
             [link("tem business tariffs", TEM_TARIFFS), "RED Day/Night Fixed, RED Plus, customer and renewal numbers, CCL rates, Gorseinon RFC", opened],
             [link("Business Energy Deals on tem", BED_TEM), "An outside description of the model", f"{opened}<br><span class='small muted'>a comparison site, so secondary</span>"],
             [link("Ofgem TPI market review", OFGEM_TPI), "Coming regulation of brokers", opened],
             [link("Ofgem, greater protection for businesses", OFGEM_PROTECT), "Fee disclosure from 1 October 2024; the redress scheme rule", extract],
             [f"{link('Elexon on P442', ELEXON_P442)} and {link('on ESNAs', ELEXON_ESNA)}", "The P442 date; four active ESNAs", extract],
             [link("Elexon on half-hourly settlement", ELEXON_MHHS), "The migration timetable", extract],
             [link("OVO written evidence", OVO_EVIDENCE), "Political exposure of the exemption", extract],
             [f"{link('ICO on business-to-business marketing', ICO_B2B)} and {link('on electronic mail', ICO_EMAIL)}", "Email and private-message rules", extract],
             [link("LinkedIn Help", LINKEDIN_HELP), "The ban on automation", extract],
             [link("Crowe on SECR", CROWE_SECR), "Reporting thresholds", extract],
             [link("ADBA directory entry for tem", ADBA), "Generators earning extra on exempt output", extract],
             [f"Tool-vendor blogs, {link('for example', SALESFORGE)}", "LinkedIn limits", f"{extract}<br><span class='small muted'>LinkedIn does not publish these numbers</span>"],
             ["Two tem pages: the partner explainer on P442 and a 2025 generator blog", "P442’s share of a bill; the generator uplift", '<span class="badge tem">Would not open</span><br><span class="small muted">both figures are marked to confirm</span>'],
             ["Your own briefings", "Pipeline, crew set-up, the church, the generators, the commission terms", '<span class="badge quiet">As described</span><br><span class="small muted">not re-verified</span>'],
             ["Planning assumptions", "The LinkedIn funnel rates, the 200,000 kWh median site, the 1p/kWh example", '<span class="badge decision">Planning only</span><br><span class="small muted">replace with actuals</span>'],
         ], "compact"), "</div>")
