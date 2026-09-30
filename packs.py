"""The client packs' pages — one definition, two ways to serve them.

``app_generator_demo.py`` and ``app_business_demo.py`` serve these packs on
Streamlit (``?view=<key>``); ``build_energy_site.py`` builds the same pages
into a static site for energy.renewablox.co.uk (``/<pack>/<slug>/``). Both read
this module, so a label, a file or a serve-time patch is changed once and
every surface follows.

A view's ``file`` is served with its patches applied at serve time — ``title``
swaps the model's own ``<h1>`` for this pack's name for it (an exact-string
splice: if an upstream rebuild changes the heading, the model keeps its own
title rather than failing), ``head`` is injected before ``</head>`` — so the
model files stay byte-for-byte upstream copies.
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


def model_page(view):
    """A view's page as served: its file, read fresh, with the view's patches applied."""
    html = (HERE / view["file"]).read_text(encoding="utf-8")
    if view.get("title"):
        html = html.replace(*view["title"], 1)
    if view.get("head"):
        html = html.replace("</head>", view["head"] + "</head>", 1)
    return html


def home_fragment(name):
    """A pack's landing fragment, read fresh (see the landing-page notes in the README)."""
    return (HERE / name).read_text(encoding="utf-8")
