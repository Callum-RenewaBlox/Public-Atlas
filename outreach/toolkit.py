"""The Toolkit page: every template and crew prompt from the strategy, with
the common fields filled in once and a copy button on each block.

The templates live here as plain text so the Offer page's segment playbook
can show the same opener the Toolkit does. Anything still in {braces} after
filling is a field to complete by hand.
"""
import re

import streamlit as st

from ui import e, html, intro, keep, kept, save

# (key, label, placeholder); each fills the {braces} named in FILLS.
FIELDS = [
    ("first_name", "Their first name", "Sarah"),
    ("company", "Their company", "Harbour Hotel"),
    ("sector", "Their sector", "hotel"),
    ("town", "Town or area", "Swansea"),
    ("pence", "Our commission, p per kWh", "1.0"),
    ("link", "Link to send", "renewablox.co.uk/x-ray"),
    ("your_name", "Your name", "Callum Wheeler"),
    ("your_role", "Your role", "Co-CEO"),
]
FILLS = {
    "first_name": ["first name"],
    "company": ["company", "Company", "organisation", "club"],
    "sector": ["sector"],
    "town": ["town", "area"],
    "pence": ["x"],
    "link": ["link"],
    "your_name": ["your name"],
    "your_role": ["your role"],
}

MESSAGE_RULE = ("words", 60)   # "Under 60 words, one idea, one easy question"
NOTE_RULE = ("chars", 200)     # connection notes: write to the free tier's 200

# Each group: id, filter tab, title, hint, items. An item is
# (title, when, body, rule) — rule is None or ("chars"|"words", limit).
GROUPS = [
    {
        "id": "profile", "tab": "LinkedIn", "title": "Profile copy", "hint": "headline · banner · about",
        "items": [
            ("Headline, option 1", "", "I X-ray business electricity bills. Co-CEO at RenewaBlox, tem partner.", None),
            ("Headline, option 2", "", "Line-by-line audits of business electricity bills, priced through tem. RenewaBlox.", None),
            ("Headline, option 3", "", "Connecting UK generators with the businesses that buy their power. RenewaBlox, tem partner.", None),
            ("Banner line", "", "Send one bill. Get a line-by-line audit and a tem quote. Our commission shown in pence.", None),
            ("About section, first draft", "", (
                "A large part of every business electricity bill has nothing to do with the power itself, "
                "and much of it goes unchecked.\n\n"
                "I’m {your name}, {your role} at RenewaBlox. We audit business electricity bills line by line: "
                "capacity charges, VAT, levies and contract terms as well as the unit rate. Then we price the supply "
                "through tem, which buys direct from UK renewable generators instead of the wholesale market. We work "
                "with the generators too, so we see both ends of the deal.\n\n"
                "How we’re paid: tem pays us a commission per kWh, printed on the first page of every quote. "
                "We never cold call.\n\n"
                "Send me one bill and I’ll show you what we find: {link}"), None),
        ],
    },
    {
        "id": "notes", "tab": "LinkedIn", "title": "Connection notes", "hint": "under 200 characters, no pitch",
        "items": [
            ("Local prospect", "", "Hi {first name}. I’m based in {town} and audit electricity bills for {sector} businesses nearby. No pitch in your inbox. Good to connect.", NOTE_RULE),
            ("New in role", "", "Congratulations on the move to {company}, {first name}. I share bill teardowns for {sector} sites, which may help a first-quarter cost review.", NOTE_RULE),
            ("Engaged with a post", "", "Thanks for your comment on the {topic} post, {first name}. Happy to connect.", NOTE_RULE),
            ("Partner", "", "Hi {first name}. I audit business electricity bills around {area} and work with a few local practices. Good to connect.", NOTE_RULE),
        ],
    },
    {
        "id": "messages", "tab": "LinkedIn", "title": "The four messages", "hint": "one question, one offer, then stop",
        "items": [
            ("Message 1, the question", "within a day of acceptance", "Thanks for connecting, {first name}. One question: do you know when {company}’s electricity contract ends? I audit business bills line by line and price them through tem, which buys direct from UK generators. One bill is enough for a side-by-side. Shall I run yours?", MESSAGE_RULE),
            ("Message 2, the sample", "day 3 or 4", "{first name}, this is what the audit looks like for a {sector} site: {link}. Half of it is the price. The other half is capacity, VAT and levies, which is where errors hide. For transparency: tem pays us {x}p per kWh, and it is printed on the quote.", MESSAGE_RULE),
            ("Message 3, the mid-contract offer", "day 8 to 10", "If you’re tied in for now, that’s fine. Tell me the end date and I’ll come back six months before with a live price, and leave you alone until then. The audit is still worth doing today, because capacity and tax errors can be fixed mid-contract.", MESSAGE_RULE),
            ("Message 4, the close", "day 21", "I’ll leave it there, {first name}. If a bill ever looks wrong, send it over and I’ll take a look. No charge.", MESSAGE_RULE),
        ],
    },
    {
        "id": "openers", "tab": "LinkedIn", "title": "Openers by segment", "hint": "swap into message 1",
        "note": "The generator line needs the generator’s written permission. The published-data line needs the figure checked against the source.",
        "items": [
            ("Hospitality", "", "Do you know whether {company} pays for more grid capacity than it draws? It is the first thing I check on a hotel bill.", None),
            ("Manufacturing and food", "", "Is there a reactive power charge on your bill? On sites with motors it can often be removed for good.", None),
            ("Care homes", "", "A 24-hour site can fix day and night rates well ahead. Do you know when your contract ends?", None),
            ("Churches and charities", "", "Has anyone checked that {organisation} is charged the right VAT and Climate Change Levy? Charities are often overcharged, and several years can usually be reclaimed.", None),
            ("Schools", "", "Have governors seen a forward price for next September? I can set one beside your current deal.", None),
            ("Sports clubs", "", "tem’s published case study says Gorseinon RFC cut its bill by 40%, about £12,000 a year. Would a free check of {club}’s bill be useful?", None),
            ("New FD or operations lead", "", "I keep a one-page checklist for reviewing an energy contract in a first quarter. Would it help?", None),
            ("Near a generator", "", "{Generator} now sells its power through tem, and nearby businesses can buy on the same platform. Would you like your bill checked against it?", None),
            ("FD with published energy data", "", "Your {year} accounts report {figure} kWh of electricity. I have posted you a one-page estimate of what that costs and what could change. Worth ten minutes?", None),
        ],
    },
    {
        "id": "replies", "tab": "LinkedIn", "title": "Replies", "hint": "when they answer",
        "items": [
            ("“We’re in contract”", "", "Understood. What’s the end date? I’ll diary a live price six months before. Meanwhile the audit can still catch errors your current supplier has to correct.", MESSAGE_RULE),
            ("“We use a broker”", "", "Sensible. One thing worth knowing: since October 2024 suppliers must show the broker’s fee on new contracts. Ours is {x}p per kWh. Happy to price alongside yours.", MESSAGE_RULE),
            ("“Never heard of tem”", "", "Fair question. tem says more than 5,500 UK businesses run on its RED product, supplied through a licensed partner, with renewals above 91%. I can send their case studies or arrange a call with them.", MESSAGE_RULE),
            ("“How are you paid?”", "", "tem pays us {x}p per kWh. It is on the first page of every quote, and here is our one-pager: {link}.", MESSAGE_RULE),
        ],
    },
    {
        "id": "inmail", "tab": "LinkedIn", "title": "InMail", "hint": "triggered accounts only · body under 80 words",
        "items": [
            ("Subject: {Company}’s electricity, from your accounts", "", "Hi {first name}. {Company}’s {year} accounts report {figure} MWh of electricity. At typical business rates that is £{low} to £{high} a year. I run line-by-line bill audits and price them through tem, which buys direct from UK generators. Would a one-page estimate for {company} be useful? Callum, RenewaBlox", ("words", 80)),
        ],
    },
    {
        "id": "partners", "tab": "Partners & generators", "title": "Partner sequence", "hint": "accountants and advisers",
        "items": [
            ("Partner message 1", "", "Thanks for connecting, {first name}. I audit business electricity bills and price them through tem. Practices like yours already hold clients’ invoices, so I can check five of your clients’ bills free and send you what comes back. Worth a try on five?", MESSAGE_RULE),
            ("Partner message 2", "", "Here is a sample of the report you would receive, with your name on it: {link}. Any fee we earn appears on the client’s quote in pence per kWh.", MESSAGE_RULE),
            ("Partner message 3", "", "The pilot takes you about ten minutes: one client email, which I have drafted, and an export from Dext or Hubdoc.", MESSAGE_RULE),
        ],
    },
    {
        "id": "consent", "tab": "Partners & generators", "title": "Client consent email", "hint": "for accountants to send",
        "items": [
            ("Subject: A free check of your electricity bill", "", "We have arranged for RenewaBlox, an energy broker, to check our clients’ electricity bills for errors and to price them with a supplier called tem. It costs you nothing. If you would like yours checked, reply YES and we will share your last 12 months of electricity invoices with RenewaBlox for that purpose only. If RenewaBlox earns a commission on any switch, the amount will be shown on your quote.", None),
        ],
    },
    {
        "id": "generator", "tab": "Partners & generators", "title": "Generator-owner note", "hint": "for strategy B",
        "items": [
            ("From the owner to a neighbour", "", "Hi {first name}. We have started selling the plant’s power through tem, and it works better for us when local businesses buy there too. The people who arranged it, RenewaBlox, will check your electricity bill for nothing and show you a price. Shall I ask Callum to get in touch?", None),
        ],
    },
    {
        "id": "posts", "tab": "Content & pages", "title": "Post bank", "hint": "20 ideas, 40% teardowns",
        "items": [
            ("Twenty posts", "", "\n".join(f"{i}. {t}" for i, t in enumerate([
                "The four lines on a business electricity bill that are most often wrong.",
                "What a kVA charge is, and how to tell if yours is too high.",
                "We earn {x}p per kWh. Here is why we print it on page one.",
                "What P442 is, what it saves, and what it does not.",
                "Why your standing charge went up.",
                "What changes on your bill on 1 April.",
                "“We’re in contract until 2027” is the best time to check your bill.",
                "A church, a VAT rate and four years of overpayment (anonymised).",
                "How an agent crew audits a bill in minutes, and where a human checks it.",
                "Where the money goes: from your bill to a UK generator.",
                "Half-hourly settlement is reaching small businesses. What it means for yours.",
                "Why UK business electricity costs more than almost anywhere else.",
                "One question for your broker: what is your commission in pence per kWh?",
                "Reactive power: the charge most factories can remove.",
                "What a rugby club did with £12,000 (tem’s case study, shared with permission).",
                "Deemed rates: what happens to your bill when you move premises.",
                "Your waste, your power: buying from the AD plant your factory feeds.",
                "What we found in our first 30 bills.",
                "Why we never cold call.",
                "A week in the life of our agent crew.",
            ], 1)), None),
        ],
    },
    {
        "id": "paid", "tab": "Content & pages", "title": "“How we’re paid”: draft one-pager", "hint": "six lines",
        "items": [
            ("One-pager", "", "\n".join("• " + line for line in [
                "RenewaBlox is an energy broker. We belong to the Energy Ombudsman’s dispute scheme for brokers. {Add once membership is confirmed.}",
                "We tender your supply to tem. We do not compare the whole market, and we will say so if we think you should look elsewhere.",
                "If you sign a tem contract through us, tem pays us {x}p for each kWh you use. That amount is inside your unit rate and is shown on your quote and your contract.",
                "The audit is free whether or not you switch.",
                "Your letter of authority lets us request your meter data and prices. It does not let us sign anything for you.",
                "Complaints go to {contact}, and to the Energy Ombudsman if we cannot resolve them.",
            ]), None),
        ],
    },
    {
        "id": "prompts", "tab": "Crew & tem", "title": "Crew prompts", "hint": "research · drafting · triage · extraction · review",
        "prompts": True,
        "items": [
            ("Research card", "", """You are preparing a research card on one UK business for a founder of RenewaBlox, an energy broker that audits electricity bills and tenders supply through tem. Use only public web sources. Never open or scrape linkedin.com.

Input: company name, address, website, segment.

Return five lines:
1. Site: what it is and what is likely to drive its electricity load.
2. Size evidence: floor area, beds, covers, pupils or published kWh, each with its source URL.
3. Trigger: a dated reason to act now, or "none found".
4. Hook: the audit check most likely to find something at this kind of site, and why.
5. Legal form from Companies House (limited company, LLP, partnership, sole trader, charity), because it decides which channels we may use.

Say what you could not find. Do not estimate savings.""", None),
            ("Message drafter", "", """Draft LinkedIn messages for {founder} to send by hand. Match the voice of the writing samples below: plain British English, no sales language, no exclamation marks.

Use the research card. Produce:
- a connection note under 200 characters with no pitch;
- message 1, under 60 words, asking when the electricity contract ends and offering a side-by-side from one bill;
- messages 2 to 4 following the sequence in the strategy doc.

Rules: one idea per message. Any figure about tem is attributed to tem. No saving is promised. No claim about the prospect that the card does not support. Say how RenewaBlox is paid by message 2.""", None),
            ("Reply triage", "", """Classify the prospect's reply as one of: in contract, has broker, wants information, asks how we are paid, doubts tem, sent a bill, not interested, other.

Draft the founder's answer from the reply table. Extract any contract end date, supplier name and site detail, and write them to Watt's Next.

If the reply is "not interested", mark do-not-contact on every channel and draft nothing further. Flag anything that reads as a complaint to Callum at once.""", None),
            ("Accounts extraction, for the Demand Atlas", "", """From the attached annual report, find the energy and carbon disclosure. Return:
- the reporting entity, and whether the figures cover a group;
- the financial year end;
- UK electricity use in kWh, if stated separately;
- total energy use in kWh;
- location-based Scope 2 emissions;
- the page number and the exact table row or sentence for each figure.

If electricity is not stated separately, say so. Derive it only when Scope 2 and that year's grid factor are both available; label the result "derived" and show the arithmetic. Never fill a gap with an estimate.""", None),
            ("Cobb’s review", "", """Before anything goes to a founder, check:
- every number traces to a source in the record;
- tem's claims are attributed to tem;
- no saving is promised;
- the recipient's legal form permits this channel;
- the recipient is not on the suppression list;
- the message is inside its length limit;
- no customer or generator is named without recorded permission.

Return "pass", or "fail" with the line that failed.""", None),
        ],
    },
    {
        "id": "tem", "tab": "Crew & tem", "title": "Email to tem: five questions", "hint": "before outreach starts",
        "items": [
            ("Subject: Five questions before we start outreach", "", """Hi {partner manager},

We are about to start outreach for RED and want to describe it accurately. Could you help with five points?

1. Meters: is RED open only to legacy half-hourly meters, or also to smart and advanced meters now settled half-hourly? Is there a minimum annual consumption?
2. Quotes: what is the usual turnaround from a letter of authority to a firm quote, how long does a quote stand, and what most often causes a decline?
3. Matching: under RED Plus, can a generator we introduce be paired with named local customers? What may a customer say in public about where its power comes from?
4. Marketing: which case studies, figures and logos may we use, and would you join a webinar or a joint post?
5. Generators: does our agreement cover generator introductions, and on what terms?

Thanks, Callum""", None),
        ],
    },
]

TABS = ["All", "LinkedIn", "Partners & generators", "Content & pages", "Crew & tem"]

# The Bill X-ray report outline is a structure, not text to send.
REPORT_PAGE_1 = [
    "Site, meter and contract: MPAN, supplier, contract end date, notice period.",
    "The side-by-side: current annual cost against the tem quote, line by line, on the same consumption.",
    "Our commission, in p/kWh and in pounds a year.",
]
REPORT_CHECKS = [
    ("Agreed capacity", "kVA paid for against peak demand in the half-hourly data"),
    ("VAT", "Whether the reduced rate applies and has been applied"),
    ("Climate Change Levy", "Reliefs and exemptions the site qualifies for"),
    ("Reactive power", "Charges that power factor correction would remove"),
    ("Excess capacity", "Penalties from an agreed capacity set too low"),
    ("TNUoS band", "Whether a lower capacity would drop the site a band"),
    ("Standing and metering charges", "Costs moved out of the unit rate; meter operator and data collector fees"),
    ("Contract status", "Out-of-contract or deemed rates; notice deadlines"),
    ("Day and night split", "Whether the rate structure suits the load profile"),
]


def opener(title):
    """An opener's text by its title (used by the Offer page's playbook)."""
    for group in GROUPS:
        if group["id"] == "openers":
            for t, _when, body, _rule in group["items"]:
                if t == title:
                    return body
    return ""


def fill(text):
    """Swap in every field the reader has filled; blanks stay in braces."""
    for key, names in FILLS.items():
        value = (kept(key) or "").strip()
        if value:
            for name in names:
                text = text.replace("{" + name + "}", value)
    return text


def length_badge(text, rule):
    if not rule:
        return ""
    unit, limit = rule
    n = len(text) if unit == "chars" else len(re.findall(r"\S+", text))
    word = "characters" if unit == "chars" else "words"
    cls = "ok" if n <= limit else "over"
    mark = "✓" if n <= limit else "over"
    return f'<span class="len {cls}" title="Rule: under {limit} {word}">{n} / {limit} {word} {mark}</span>'


def fields_panel():
    with st.container(key="fields"):
        html('<p class="eyebrow">Fill once, every template updates</p>')
        cols = st.columns(4)
        for i, (key, label, placeholder) in enumerate(FIELDS):
            with cols[i % 4]:
                st.text_input(label, key=keep(key, ""), placeholder=f"e.g. {placeholder}",
                              on_change=save, args=(key,))


def template(group, i, item, prose):
    title, when, body, rule = item
    text = fill(body)
    when_html = f'<span class="when">{e(when)}</span>' if when else ""
    html(f'<div class="tplhead"><h4>{e(fill(title))}</h4>{when_html}{length_badge(text, rule)}</div>')
    with st.container(key=f'tpl{"msg" if prose else "pr"}_{group["id"]}_{i}'):
        st.code(text, language=None, wrap_lines=True)


def template_row(group, pair, prose):
    if len(pair) == 1 and len(pair[0][1][2]) >= 420:
        template(group, *pair[0], prose)
        return
    for col, (i, item) in zip(st.columns(2, gap="medium"), pair):
        with col:
            template(group, i, item, prose)


def page():
    intro("Templates and prompts", "Working drafts for the founders and the crew",
          "Edit each one into your own voice before use. Anything still in <code>{braces}</code> is a field. "
          "Every figure about tem must stay attributed to tem. Hover any block for its copy button; "
          "it copies as plain text.")
    fields_panel()

    left, right = st.columns([3, 2], vertical_alignment="bottom")
    with left:
        tab = st.segmented_control("Show", TABS, key=keep("tpl_tab", "LinkedIn"), on_change=save,
                                   args=("tpl_tab",), label_visibility="collapsed")
    with right:
        query = st.text_input("Search", key=keep("tpl_q", ""), on_change=save, args=("tpl_q",),
                              placeholder="Search every template", label_visibility="collapsed",
                              icon=":material/search:")
    q = (query or "").strip().lower()
    tab = "All" if q else (tab or "All")   # a search looks everywhere

    shown = 0
    for group in GROUPS:
        if tab != "All" and group["tab"] != tab:
            continue
        items = [it for it in group["items"]
                 if not q or q in it[0].lower() or q in it[2].lower() or q in group["title"].lower()]
        if not items:
            continue
        shown += len(items)
        html(f'<div class="grouphead"><h3>{e(group["title"])}</h3><span class="hint">{e(group["hint"])}</span></div>')
        prose = not group.get("prompts")
        # short templates sit two to a row; long ones take the full width
        pair = []
        for i, item in enumerate(items):
            if len(item[2]) < 420:
                pair.append((i, item))
                if len(pair) == 2:
                    template_row(group, pair, prose)
                    pair = []
            else:
                if pair:
                    template_row(group, pair, prose)
                    pair = []
                template_row(group, [(i, item)], prose)
        if pair:
            template_row(group, pair, prose)
        if group.get("note") and not q:
            html(f'<p class="small muted">{e(group["note"])}</p>')

    if tab in ("All", "Content & pages") and (not q or "report" in q or "x-ray" in q or "outline" in q):
        shown += 1
        rows = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in REPORT_CHECKS)
        page1 = "".join(f"<li>{x}</li>" for x in REPORT_PAGE_1)
        html(f"""
        <div class="grouphead"><h3>Bill X-ray: report outline</h3><span class="hint">two pages</span></div>
        <div class="cols mt">
          <div class="mini"><h4>Page 1</h4><ul>{page1}</ul>
            <p style="margin-top:10px">Close with the assumptions made, the data used, the next step and how long the quote stands.</p></div>
          <div class="tablewrap"><table class="compact"><thead><tr><th>Page 2 · Check</th><th>What it looks for</th></tr></thead>
            <tbody>{rows}</tbody></table></div>
        </div>""")

    if not shown:
        html('<div class="callout mt">No template matches that search. Try a word from its text, such as '
             '“contract”, “broker” or “VAT”.</div>')
