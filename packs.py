"""The client packs' pages — one definition for every site that serves them.

``build_energy_site.py`` builds the Generator Demo and Business Electricity
packs into the static site for energy.renewablox.co.uk (``/<pack>/<slug>/``);
``atlas/build.py`` (through ``atlas/pages.py``) builds the investor packs and
the standalone peakers into atlas.renewablox.com. Both read this module, so a
label, a file or a patch is changed once and every page that uses it follows.

A view's ``file`` is published with its patches applied at build time —
``title`` swaps the model's own ``<h1>`` for this pack's name for it (an
exact-string splice: if an upstream rebuild changes the heading, the model
keeps its own title rather than failing), ``head`` is injected before
``</head>`` and ``body`` before ``</body>`` — so the model files stay
byte-for-byte upstream copies.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent

CONTACT = "callum@renewablox.com"

# Generator Demo — the client pack for generators, sorted by sector.
GENERATOR_HOME = "generator_demo_home.html"
GENERATOR_VIEWS = {
    "peaker": {
        "slug": "peaker-plant",
        "file": "peaker_plant_3d.html",
        "sector": "Fuelled Renewables",
        "label": "Peaker Plant model",
        "short": "Peaker",
        "title": ("<h1>Peaker Plant 3D</h1>", "<h1>Peaker Plant model</h1>"),
        # p/kWh, the unit AD operators work in; the guided-tour strip is dropped
        "head": ('<script>window.PEAKER_UNITS="p/kWh";</script>'
                 "<style>#viewstrip{display:none !important;}</style>"),
    },
    "hydro": {
        "slug": "run-of-river-hydro",
        "file": "kld_interactive.html",
        "sector": "Stranded Renewables",
        "label": "Run-of-River Hydro model",
        "short": "Hydro",
        "title": ("<h1>Kinlochdamph — Living Site Model</h1>", "<h1>Run-of-River Hydro model</h1>"),
        "head": "",
    },
}

# Business Electricity — RenewaBlox with tem, in three tiers.
BUSINESS_HOME = "business_demo_home.html"
BUSINESS_SUBJECT = "Business%20electricity%20%E2%80%94%20our%20bill"
BUSINESS_VIEWS = {
    "site": {"slug": "site-analysis", "file": "business_site_analysis.html", "tier": "Tier 1",
             "label": "Holistic Site Analysis", "short": "Site"},
    "haas": {"slug": "heat-as-a-service", "file": "business_haas.html", "tier": "Tier 2",
             "label": "Heat-as-a-Service", "short": "HaaS"},
    "heat": {"slug": "heat-network", "file": "heat_network_3d.html", "tier": "Tier 3",
             "label": "Heat Network", "short": "Network"},
}


# The investor packs, built by atlas/build.py for atlas.renewablox.com: the public Investor Demo
# (/investors/demo/), the Australia pack (/investors/australia/) and the Investor Portal
# (/investors/portal/, behind the portal's key), each a landing page and its models behind the
# pack bar. The guided-tour view strip is dropped from the peaker for investors: the overview
# scene is the demo.
PEAKER_HEAD = "<style>#viewstrip{display:none !important;}</style>"
INVESTOR_VIEWS = {
    "peaker": {"slug": "peaker-plant", "file": "peaker_plant_3d.html", "label": "Peaker Plant 3D", "short": "Peaker",
               "head": PEAKER_HEAD},
    "hydro": {"slug": "hydro", "file": "kld_interactive.html", "label": "Hydro 3D", "short": "Hydro"},
    "heat": {"slug": "heat-network", "file": "heat_network_3d.html", "label": "Heat Network 3D", "short": "Heat"},
    # "Demand" alone would not say what this is on a phone
    "dfc": {"slug": "demand-for-constraints", "file": "demand_for_constraints_3d.html",
            "label": "Demand for Constraints 3D", "short": "DfC"},
}
# NEM 3D was built for one group of Australian investors, who get it at an address of their own.
AUS_VIEWS = {
    "peaker": INVESTOR_VIEWS["peaker"],
    "hydro": INVESTOR_VIEWS["hydro"],
    "nem": {"slug": "nem", "file": "nem_negative_price_atlas.html", "label": "NEM 3D", "short": "NEM"},
}

# Views whose figures are for investors. In the public demo the panels that carry them are
# blurred and inert (a visitor sees that the data is there) and a card points to the investor
# portal. Cosmetic by design: the numbers are still in the page the browser receives, and the
# model files are public in this repository; the portal serves the same files unblurred behind
# its key. ``blur`` lists the panels that carry figures, ``hide`` the controls that only make
# sense with them (the DfC assumptions drawer is the whole commercial model), ``top`` puts the
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
    # the card column, the status line under the headline, the year strip, the figures on the
    # scene labels (their names stay), the How-it-works tables
    "heat": {
        "blur": "#right, #status, #stripwrap, #labels .lbl span, #about table",
        "hide": "",
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

# Peaker Plant 3D on links of its own (atlas.renewablox.com/models/): for AD operators' brochures,
# prices in p/kWh; and the Peaker Demo, for an energy-literate audience, in GBP/MWh with the strike
# opening at 80 on a 50-100 range and the export price named DA + gDUoS.
PEAKER_PLANT_HEAD = '<script>window.PEAKER_UNITS="p/kWh";</script>' + PEAKER_HEAD
PEAKER_DEMO_HEAD = """
<script>window.PEAKER_CFG={
  strike:{value:80, min:50, max:100},
  exportLabel:"Export \\u00B7 DA + gDUoS",
  legendLabel:"Export value \\u00B7 DA + gDUoS"
};</script>

<style>
  /* the guided-tour view strip — the packs drop it too */
  #viewstrip {display:none !important;}
  /* the "peaker model:" explainer: this audience reads the dispatch desk
     itself, so the footer keeps only its price-sourcing and copyright line */
  footer > div:first-child {display:none !important;}
  /* the dispatch desk moves to the bottom-right, unchanged in every other
     respect; it clears #rightcol, which is anchored top-right */
  #deskwrap {left:auto !important; right:14px !important;}
</style>
"""


def model_page(view):
    """A view's page as served: its file, read fresh, with the view's patches applied."""
    html = (HERE / view["file"]).read_text(encoding="utf-8")
    if view.get("title"):
        html = html.replace(*view["title"], 1)
    if view.get("head"):
        html = html.replace("</head>", view["head"] + "</head>", 1)
    if view.get("body"):
        html = html.replace("</body>", view["body"] + "</body>", 1)
    return html


def home_fragment(name):
    """A pack's landing fragment, read fresh (see the landing-page notes in the README)."""
    return (HERE / name).read_text(encoding="utf-8")
