"""The pages that came off Streamlit, as atlas/build.py puts them on atlas.renewablox.com.

Each was a Streamlit app around HTML files at the root of this repository (or, for Reabold and
Citygate, of their own repositories, copied into vendor/): the app routed ?view=, spliced files
together, patched them as it served them and framed the result. Here the same files are put in
place at build time with the same splices, plus the few patches a page needs to work on its own
rather than inside Streamlit's frame. Every patch names an exact string that must occur once, so
a regenerated source that loses it fails the build instead of shipping a page that half works.

    /clients/srv/             SRV Atlas (?view=3d the 3D Dispatch Sim, ?view=siting the 3D Compute Kiosk)
    /clients/srv-contractor/  SRV Contractor Atlas, the electrical survey for the LV connection RFQ
    /clients/bry/             Bryn Atlas, code BRY (?view=3d the 3D Site Model, ?view=compute the Compute Render)
    /clients/kld/             KLD Atlas (?view=3d the 3D Revenue Sim)
    /clients/ihn/             IHN Atlas (?view=3d Heat Network 3D)
    /clients/reabold/west-newton/, /clients/reabold/reservoirs/   Reabold's two maps
    /clients/citygate/        Citygate Church's electricity portrait
    /team/keith-huntly/, /team/moray/   the team's decision pages for the Moray primaries
    /investors/demo/, /investors/australia/, /investors/portal/   the investor packs (landing + models)
    /models/peaker-plant/, /models/peaker-demo/   Peaker Plant 3D on links of its own

/clients/ and /team/ are behind the sign-in (netlify/edge-functions/atlas-gate.js), which opens
/clients/<code>/ to the addresses listed for <code> in Supabase's public.atlas_access and to the
team, /team/ to the team only, and routes ?view=. The client pages name their sites, so they live only
behind the sign-in; only a client's public cover on the front page is held to the anonymity checks (build.py).
/investors/portal/ is not gated: the Wix investor portal's members area links to it, and only its address keeps it
from the public.
"""
import base64
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
VENDOR = HERE / "vendor"
SITE_URL = "https://atlas.renewablox.com"

sys.path.insert(0, str(REPO))
import packs  # noqa: E402  (the pack definitions, shared with the energy site)
from build_energy_site import FRAME_CSS, FAVICON  # noqa: E402  (the pack bar's page, as the energy site draws it)


class PageError(Exception):
    """A source no longer matches what its patches expect; build.py fails on it."""


def source(name):
    """A page's source: a file at the root of the repository, or a copy in vendor/."""
    path = VENDOR / name if (VENDOR / name).is_file() else REPO / name
    return path.read_text(encoding="utf-8")


def once(text, old, new, what):
    n = text.count(old)
    if n != 1:
        raise PageError(f"{what}: expected {old[:70]!r} once, found it {n} times")
    return text.replace(old, new, 1)


def splice(page, insert, what):
    """The Streamlit apps' splice: a chrome or badge file put in just before the page's </body>."""
    return once(page, "</body>", insert + "\n</body>", what)


# The badges and back controls navigate with rbxGo(url), written for Streamlit's sandboxed frame: it clicks a link in
# the parent document and, should that not commit within 1.2 s, pushes the address into the parent's history and
# reloads. Served on its own, the click already navigates, and the fallback would fire whenever a page is slow to
# answer (a sign-in check, a phone): it fetches the page twice and leaves a history entry over the wrong document.
# Outside a frame the guard navigates at once; inside one it does nothing, as before.
RBXGO = re.compile(r"function rbxGo\(url\)\s*\{")
RBXGO_GUARD = "\n    if (window.parent === window) { location.assign(url); return; }"


def top_level_nav(text, what):
    text, n = RBXGO.subn(lambda m: m.group(0) + RBXGO_GUARD, text)
    if n != 1:
        raise PageError(f"{what}: expected one rbxGo(url) to guard, found {n}")
    return text


def noindex(text, what):
    """Every client page asks not to be indexed (the gates send X-Robots-Tag too)."""
    if re.search(r'<meta\s+name="robots"', text[:20000], re.I):
        return text
    text, n = re.subn(r'<meta\s+charset="?utf-8"?\s*/?>', lambda m: m.group(0) + '\n<meta name="robots" content="noindex, nofollow">',
                      text, count=1, flags=re.I)
    if n != 1:
        raise PageError(f"{what}: no <meta charset> to put the robots line after")
    return text


# The opening page of every client atlas with a map, so they all look the same: the RenewaBlox bar (what is proposed
# and the site's code, over its name and place), the site on satellite imagery, and a BLOX badge for each of its 3D
# views, with nothing else drawn (atlas/client_map/map.html). A badge's pill stands to the left of its chip, or to
# the right with "side": "right" where it would cover another; "anchor" moves the chip off its point, in pixels
# (Leaflet's iconAnchor; [23, 23] centres it). The map opens at "zoom" on "at" (on a small screen, no closer than
# fits every badge in), and the imagery's own detail runs to "nativeZoom" (19 unless given).
CLIENT_MAP = HERE / "client_map"
CLIENT_MAPS = {
    "srv": {"title": "SRV Atlas — Scrivelsby", "kick": "Proposed compute load bank · SRV Atlas",
            "place": "Home Farm AD site, Scrivelsby, Horncastle LN9 6JB", "at": [53.17680, -0.11020], "zoom": 18.5,
            "badges": [{"at": [53.176703, -0.110826], "label": "3D Dispatch Sim", "short": "3D Sim", "view": "3d"},
                       {"at": [53.176878, -0.110333], "label": "3D Compute Kiosk", "short": "Kiosk", "view": "siting",
                        "side": "right", "anchor": [-37, 4]}]},
    "kld": {"title": "KLD Atlas — Kinlochdamph", "kick": "999 kW run-of-river hydro · KLD Atlas",
            "place": "Kinlochdamph hydro scheme, Loch Damh, Wester Ross", "at": [57.46160, -5.55778], "zoom": 17,
            "badges": [{"at": [57.46160, -5.55778], "label": "3D Revenue Sim", "short": "3D Sim", "view": "3d"}]},
}


def client_bar(kick, place):
    """The RenewaBlox bar every client atlas opens under (atlas/client_map/bar.html), as (its stylesheet, for the
    page's head; the bar, for the top of its body): the wordmark, then the kick ("what is proposed · CODE Atlas") over
    the site's name and place."""
    what = "atlas/client_map/bar.html"
    style, bar = (CLIENT_MAP / "bar.html").read_text(encoding="utf-8").split("<!-- bar -->\n")
    kick = re.sub(r"\b([kMG]Wh?|kV)\b", r'<span class="u">\1</span>', html.escape(kick))  # 999 kW, not KW
    for key, value in (("WORDMARK", png_data(CLIENT_MAP / "wordmark.png")), ("KICK", kick), ("PLACE", html.escape(place))):
        bar = once(bar, f"%%{key}%%", value, what)
    return style.rstrip("\n"), bar.rstrip("\n")


def png_data(path):
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def client_map(code):
    """The opening page of /clients/<code>/: atlas/client_map/map.html filled in from the site's entry in CLIENT_MAPS."""
    site, what = CLIENT_MAPS[code], "atlas/client_map/map.html"
    badged, views = sorted(b["view"] for b in site["badges"]), sorted(CLIENT_PAGES[f"/clients/{code}/"].get("views", {}))
    if badged != views:
        raise PageError(f"{what}: {code} needs a badge for each of its views, and no other (badges {badged}, views {views})")
    style, bar = client_bar(site["kick"], site["place"])
    config = {"at": site["at"], "zoom": site["zoom"], "nativeZoom": site.get("nativeZoom", 19), "badges": site["badges"]}
    page = (CLIENT_MAP / "map.html").read_text(encoding="utf-8")
    for key, value in (("TITLE", html.escape(site["title"])), ("BAR_STYLE", style), ("BAR", bar),
                       ("SITE", json.dumps(config, ensure_ascii=False)), ("CHIP", png_data(CLIENT_MAP / "blox-chip.png"))):
        page = once(page, f"%%{key}%%", value, what)
    return page


# IHN keeps its opening page by the owner's word: the three.js scene of the district with the network, its callouts and
# the plant room cut away, its view strip and its caveat, as ihn_atlas.html has them. Its bar and its badge are the
# family's: the RenewaBlox bar in place of the page's own header (whose two buttons go: the badge opens the model, and
# "How it works" moves into the view strip, where the page's script still finds it by its id), and the badge in the
# shared style, one line, its chip the 44 px roundel in its white border. The page's script still places and docks the badge, measuring it
# as drawn.
IHN_BAR = ("Proposed data-centre plant room · IHN Atlas", "Seward Street plant room, Bunhill heat network, Islington EC1")
IHN_STYLE = """<style>
/* ---- the IHN Atlas in the family's bar and badge (atlas/pages.py, ihn_atlas) ---- */
/* the bar takes its place above the scene, as the page's own header did, rather than floating over it */
#rbx-bar{position:relative;flex:none;z-index:6}
/* the badge as on the other atlases: a 44 px chip with its pulse, a one-line pill, the arrow towards the chip */
#ihn-badge,#ihn-badge.docked{height:46px;gap:7px}
#ihn-badge .chipbox,#ihn-badge.docked .chipbox{width:46px;height:46px}
/* the page sizes every box border-box; the roundel is 44 px inside its 2.5 px border and centred on its box, as on
   the shared map, hover included */
#ihn-badge .chip,#ihn-badge.docked .chip{box-sizing:content-box;inset:auto;left:50%;top:50%;width:44px;height:44px;
  transform:translate(-50%,-50%)}
#ihn-badge:hover .chip{transform:translate(-50%,-50%) scale(1.12)}
#ihn-badge .ring,#ihn-badge.docked .ring{width:52px;height:52px;margin:-26px 0 0 -26px}
#ihn-badge .core,#ihn-badge.docked .core{width:44px;height:44px;margin:-22px 0 0 -22px}
#ihn-badge .cta,#ihn-badge.docked .cta{gap:7px;padding:9px 20px 9px 14px;font:700 12px/1 var(--font)}
#ihn-badge .cta b{font:inherit;letter-spacing:.015em}
#ihn-badge.flip .cta{padding:9px 14px 9px 20px}
#ihn-badge.flip .cta i{order:-1;transform:scaleX(-1)}
#ihn-badge.flip:hover .cta i{transform:scaleX(-1) translateX(3px)}
</style>"""


def ihn_atlas(page):
    """IHN's opening page with the family's bar and badge (IHN_STYLE says what changes and why)."""
    what = "ihn_atlas.html"
    page = once(page, "<title>RenewaBlox — IHN Atlas</title>", f"<title>{CLIENT_PAGES['/clients/ihn/']['title']}</title>", what)
    style, bar = client_bar(*IHN_BAR)
    page = once(page, "</head>", f"{style}\n{IHN_STYLE}\n</head>", what)
    head = re.findall(r"<header>\n  <div class=\"logo\">.*?</header>\n", page, flags=re.S)
    if len(head) != 1 or 'id="btn-about"' not in head[0]:
        raise PageError(f"{what}: expected one <header> holding the How it works button, found {len(head)}")
    page = once(page, head[0], bar + "\n", what)
    page = once(page, '<button class="chip" type="button" id="btn-layers">Layers</button>',
                '<button class="chip" type="button" id="btn-layers">Layers</button>'
                '<button class="chip" type="button" id="btn-about">How it works</button>', what)
    return once(page, "<span>half-hourly dispatch model of this plant room</span>", "", what)


def client_pages():
    """{site path: text} for the client atlases and the team pages."""
    out = {}

    # SRV: Scrivelsby (Home Farm AD). The map's badges open the two 3D views; the contractor survey has a grant of its
    # own (client 'srv-contractor'), so a contractor never sees the client's views.
    out["clients/srv/index.html"] = client_map("srv")
    page = once(source("srv_3d_sim.html"), "<title>SRV 3D Sim - Scrivelsby Peaker</title>",
                "<title>SRV Atlas — 3D Dispatch Sim</title>", "srv_3d_sim.html")
    out["clients/srv/3d.html"] = top_level_nav(page, "srv_3d_sim.html")
    page = once(source("srv_siting_3d.html"), "<title>SRV Compute Kiosk - Scrivelsby Home Farm</title>",
                "<title>SRV Atlas — 3D Compute Kiosk</title>", "srv_siting_3d.html")
    out["clients/srv/siting.html"] = top_level_nav(page, "srv_siting_3d.html")
    page = once(source("srv_contractor.html"),
                "<title>RenewaBlox — Scrivelsby Atlas · Home Farm AD site (LN9 6JB) · Electrical Site Survey</title>",
                "<title>SRV Contractor Atlas</title>", "srv_contractor.html")
    # the regrade note's call to action ended in a stray control character and "92" (an arrow's escape gone wrong)
    page = once(page, '.cabtip .cta:after{content:" \x1192"}', '.cabtip .cta:after{content:" \\2192"}', "srv_contractor.html")
    out["clients/srv-contractor/index.html"] = noindex(page, "srv_contractor.html")

    # Bryn: the badge opened the models by their file names outside Streamlit, and the models' "Atlas" control fell
    # back to bryn_atlas.html; both now use the page's own addresses. The 3D model read ?view= as a camera preset.
    badge = once(source("bryn_atlas_3d_badge.html"),
                 'var STANDALONE_3D = "bryn_3d_sim.html", STANDALONE_COMPUTE = "bryn_compute_3d.html";',
                 'var STANDALONE_3D = "?view=3d", STANDALONE_COMPUTE = "?view=compute";', "bryn_atlas_3d_badge.html")
    page = splice(source("bryn_atlas.html"), badge, "bryn_atlas.html")
    page = once(page, "<title>RenewaBlox — Bryn Atlas · Bryn Power AD plant, Gelligaer (CF82 8FY) · Proposed data centre</title>",
                "<title>Bryn Atlas — Bryn Power AD plant</title>", "bryn_atlas.html")
    out["clients/bry/index.html"] = noindex(page, "bryn_atlas.html")
    page = once(source("bryn_3d_sim.html"), "<title>Bryn 3D - surplus power to compute</title>",
                "<title>Bryn Atlas — 3D Site Model</title>", "bryn_3d_sim.html")
    page = once(page, 'window.__ATLAS_PAGE = "bryn_atlas.html";', 'window.__ATLAS_PAGE = "/clients/bry/";', "bryn_3d_sim.html")
    page = once(page, 'Oi.get("view")||"overview"',
                '(/^(top|overview|blox|chp|tanks|solar|plant)$/.test(Oi.get("view"))?Oi.get("view"):"overview")', "bryn_3d_sim.html")
    # "Atlas" goes back in history only when the visitor came from the Bryn map itself
    page = once(page, 'if(document.referrer&&new URL(document.referrer).origin===window.location.origin&&window.history.length>1)'
                      '{window.history.back();return}',
                'if(document.referrer&&(r=>r.origin===window.location.origin&&r.pathname===window.location.pathname&&'
                '!r.searchParams.has("view"))(new URL(document.referrer))&&window.history.length>1){window.history.back();return}',
                "bryn_3d_sim.html")
    out["clients/bry/bryn_3d_sim.html"] = page
    page = once(source("bryn_compute_3d.html"), "<title>Bryn Compute Render</title>",
                "<title>Bryn Atlas — Compute Render</title>", "bryn_compute_3d.html")
    page = once(page, 'window.__ATLAS_PAGE = "bryn_atlas.html";', 'window.__ATLAS_PAGE = "/clients/bry/";', "bryn_compute_3d.html")
    page = once(page, "if (document.referrer && new URL(document.referrer).origin === window.location.origin && "
                      "window.history.length > 1) { window.history.back(); return; }",
                "if (document.referrer && (function(r){ return r.origin === window.location.origin && r.pathname === "
                "window.location.pathname && !r.searchParams.has(\"view\"); })(new URL(document.referrer)) && "
                "window.history.length > 1) { window.history.back(); return; }", "bryn_compute_3d.html")
    out["clients/bry/bryn_compute_3d.html"] = page

    # KLD: Kinlochdamph. The map's badge opens the 3D view, the shared model with the KLD chrome (its "Atlas" control)
    # spliced in, and the root clip Streamlit's frame gave it, without which a phone pans sideways.
    out["clients/kld/index.html"] = client_map("kld")
    page = splice(source("kld_interactive.html"), source("kld_hydro_chrome.html"), "kld_interactive.html")
    page = once(page, "<title>RenewaBlox — Kinlochdamph Living Site Model</title>", "<title>KLD Atlas — 3D Revenue Sim</title>",
                "kld_interactive.html")
    page = once(page, "  #stage{background:#0d1b23}", "  #stage{background:#0d1b23}\n  html{overflow:hidden}", "kld_hydro_chrome.html")
    out["clients/kld/3d.html"] = noindex(top_level_nav(page, "kld_hydro_chrome.html"), "kld_interactive.html")

    # IHN: the heat network. Its opening page keeps its own scene (ihn_atlas below); the 3D view is the shared Heat
    # Network 3D with the IHN chrome spliced in.
    out["clients/ihn/index.html"] = noindex(top_level_nav(ihn_atlas(source("ihn_atlas.html")), "ihn_atlas.html"), "ihn_atlas.html")
    chrome = top_level_nav(source("ihn_heat_chrome.html"), "ihn_heat_chrome.html")
    page = splice(source("heat_network_3d.html"), chrome, "heat_network_3d.html")
    page = once(page, "<title>RenewaBlox — Heat Network 3D</title>", "<title>IHN Atlas — Heat Network 3D</title>", "heat_network_3d.html")
    out["clients/ihn/3d.html"] = noindex(page, "heat_network_3d.html")

    # Reabold: the wrappers' captions move into the maps' own panels, and the reservoir map takes the wrapper's title.
    page = once(source("wn_infrastructure_map.html"), "Confirm against NPg / NESO records before design.</div>';",
                "Confirm against NPg / NESO records before design.</div>'+\n '<div class=\"note\">Prepared by RenewaBlox &middot; "
                "West Newton infrastructure map &middot; contact <a href=\"mailto:callum@renewablox.com\">callum@renewablox.com</a>"
                "</div>';", "wn_infrastructure_map.html")
    out["clients/reabold/west-newton/index.html"] = noindex(page, "wn_infrastructure_map.html")
    page = once(source("reservoir_map.html"), "<title>RenewaBlox Atlas — UKCS Reservoir Layer (prototype)</title>",
                "<title>Reservoir Atlas — UKCS</title>", "reservoir_map.html")
    page = once(page, "Basemap © OpenStreetMap contributors © CARTO.</p></details>",
                "Basemap © OpenStreetMap contributors © CARTO.</p></details>\n  <p class=\"src\">Prepared by RenewaBlox · UKCS "
                "reservoir layer (prototype) · contact <a href=\"mailto:callum@renewablox.com\">callum@renewablox.com</a></p>",
                "reservoir_map.html")
    out["clients/reabold/reservoirs/index.html"] = noindex(page, "reservoir_map.html")

    # Citygate Church: as it is.
    out["clients/citygate/index.html"] = noindex(source("citygate_electricity.html"), "citygate_electricity.html")

    # The team's pages. Keith & Huntly reads its deep links (?beat=, ?step=, ?still) from its own address now, so the
    # wrapper's injected query goes; its hint no longer needs a click to focus a frame. Moray asks OpenStreetMap for
    # tiles at the one address its tile policy names.
    page = once(source("kh_atlas.html"), "click once, then <kbd>&rarr;</kbd> to step", "<kbd>&rarr;</kbd> to step", "kh_atlas.html")
    out["team/keith-huntly/index.html"] = noindex(page, "kh_atlas.html")
    page = once(source("moray_atlas.html"),
                "const osmT=L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; OpenStreetMap'});",
                "const osmT=L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; OpenStreetMap'});",
                "moray_atlas.html")
    out["team/moray/index.html"] = noindex(page, "moray_atlas.html")
    return out


# What the sign-in needs to know of each page: who it is for, its name on /clients/, and its views.
CLIENT_PAGES = {
    "/clients/srv/": {"client": "srv", "title": "SRV Atlas — Scrivelsby", "list": True,
                      "views": {"3d": "3d.html", "siting": "siting.html"}},
    "/clients/srv-contractor/": {"client": "srv-contractor", "title": "SRV Contractor Atlas — electrical site survey", "list": True},
    "/clients/bry/": {"client": "bry", "title": "Bryn Atlas — Bryn Power AD plant", "list": True,
                      "views": {"3d": "bryn_3d_sim.html", "compute": "bryn_compute_3d.html"}},
    "/clients/kld/": {"client": "kld", "title": "KLD Atlas — Kinlochdamph", "list": True, "views": {"3d": "3d.html"}},
    "/clients/ihn/": {"client": "ihn", "title": "IHN Atlas — Islington heat network", "list": True, "views": {"3d": "3d.html"}},
    "/clients/reabold/west-newton/": {"client": "reabold", "title": "West Newton infrastructure map", "list": True},
    "/clients/reabold/reservoirs/": {"client": "reabold", "title": "UKCS reservoir atlas (prototype)", "list": True},
    "/clients/citygate/": {"client": "citygate", "title": "Citygate Church · Electricity Portrait", "list": True},
    "/team/keith-huntly/": {"client": "*", "title": "Keith & Huntly Atlas", "list": True},
    "/team/moray/": {"client": "*", "title": "Moray Cluster Atlas — Keith & Huntly", "list": True},
}
# /clients/bryn/ was Bryn's address for a day: the public front page names a client by its code only (BRY)
CLIENT_REDIRECTS = {"/clients/reabold/": "/clients/", "/clients/bryn/": "/clients/bry/"}

# Each page's security policy, as measured page by page: what it loads (Leaflet from cdnjs, imagery from Esri,
# OpenStreetMap or CARTO tiles, Google Fonts), whether its mesh decoder compiles WebAssembly ('wasm-unsafe-eval'),
# and whether three.js fetches its textures as blob: URLs. A view file has its own policy where it needs one.
_END = "object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
_OSM = "https://a.tile.openstreetmap.org https://b.tile.openstreetmap.org https://c.tile.openstreetmap.org"
# the opening page every client map shares (client_map): Leaflet from cdnjs, the imagery from Esri
CLIENT_MAP_CSP = ("default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
                  "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
                  "img-src 'self' data: https://server.arcgisonline.com https://cdnjs.cloudflare.com; font-src 'self'; "
                  "connect-src 'self'; media-src 'none'; worker-src 'none'; frame-src 'none'; " + _END)
CLIENT_CSP = {
    "/clients/srv/": CLIENT_MAP_CSP,
    "/clients/srv/3d.html": ("default-src 'self'; script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval'; style-src 'self' 'unsafe-inline'; "
                             "img-src 'self' data: blob:; font-src 'self'; connect-src 'self' blob:; media-src 'none'; "
                             "worker-src 'none'; frame-src 'none'; " + _END),
    "/clients/srv/siting.html": ("default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
                                 "img-src 'self' data: blob:; font-src 'self'; connect-src 'self' blob:; media-src 'none'; "
                                 "worker-src 'none'; frame-src 'none'; " + _END),
    "/clients/srv-contractor/": ("default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
                                 "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
                                 f"img-src 'self' data: https://server.arcgisonline.com {_OSM} https://cdnjs.cloudflare.com; "
                                 "font-src 'self' https://fonts.gstatic.com; connect-src 'self'; media-src 'none'; worker-src 'none'; "
                                 "frame-src 'self'; " + _END),
    "/clients/bry/": ("default-src 'self'; script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval' https://cdnjs.cloudflare.com; "
                       "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
                       "img-src 'self' data: blob: https://server.arcgisonline.com; font-src 'self' data:; connect-src 'self' blob:; "
                       "media-src 'none'; worker-src 'none'; frame-src 'none'; " + _END),
    "/clients/kld/": CLIENT_MAP_CSP,
    "/clients/kld/3d.html": ("default-src 'self'; script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval'; style-src 'self' 'unsafe-inline'; "
                             f"img-src 'self' data: https://server.arcgisonline.com {_OSM}; font-src 'self'; connect-src 'self'; "
                             "media-src 'self'; worker-src 'self'; " + _END),
    "/clients/ihn/": "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; " + _END,
    "/clients/reabold/west-newton/": ("default-src 'none'; script-src 'unsafe-inline' https://cdnjs.cloudflare.com; "
                                      "style-src 'unsafe-inline' https://cdnjs.cloudflare.com; "
                                      f"img-src data: https://cdnjs.cloudflare.com https://server.arcgisonline.com {_OSM}; " + _END),
    "/clients/reabold/reservoirs/": ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
                                     "img-src data: https://a.basemaps.cartocdn.com https://b.basemaps.cartocdn.com "
                                     "https://c.basemaps.cartocdn.com; " + _END),
    "/clients/citygate/": "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; font-src data:; " + _END,
    "/team/keith-huntly/": ("default-src 'none'; script-src 'unsafe-inline' 'wasm-unsafe-eval'; style-src 'unsafe-inline'; "
                            "img-src data: blob:; font-src data:; connect-src blob:; " + _END),
    "/team/moray/": ("default-src 'none'; script-src 'unsafe-inline' https://cdnjs.cloudflare.com; "
                     "style-src 'unsafe-inline' https://cdnjs.cloudflare.com; "
                     "img-src data: https://server.arcgisonline.com https://tile.openstreetmap.org; " + _END),
}


# ---- the investor packs and the standalone models ----

# The models are self-contained three.js pages, each framed by its pack page: the mesh decoder compiles WebAssembly,
# and GLTF textures are blob: URLs, fetched or drawn. The public packs take it from root/_headers; the portal from the
# rules build.py writes for it (site_headers), which let the Wix site frame it.
MODEL_CSP = ("default-src 'self'; script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval'; style-src 'self' 'unsafe-inline'; "
             "img-src 'self' data: blob:; font-src 'self'; connect-src 'self' blob:; frame-src 'self'; object-src 'none'; "
             "base-uri 'self'; form-action 'self'; frame-ancestors 'self'")

PACKS = {
    "investors/demo": {
        "home": "investor_demo_home.html", "views": packs.INVESTOR_VIEWS, "gated": packs.GATED,
        "title": "RenewaBlox — Investor Demo", "crumb": "Investor Demo",
        "description": "RenewaBlox's projects as working 3D simulations: Peaker Plant, Hydro, Heat Network and Demand for Constraints.",
    },
    "investors/australia": {
        "home": "investor_demo_aus_home.html", "views": packs.AUS_VIEWS, "gated": {},
        "title": "RenewaBlox — Investor Demo (Australia)", "crumb": "Investor Demo &middot; Australia",
        "description": "RenewaBlox's projects as working 3D simulations: Peaker Plant, Hydro and NEM.",
    },
    "investors/portal": {
        "home": "investor_portal_home.html", "views": packs.INVESTOR_VIEWS, "gated": {},
        "title": "RenewaBlox — Investor Portal", "crumb": "Investor Portal",
        "description": "The RenewaBlox project pack for registered investors.",
    },
}

# the investor demo's portal pill, beside the pack bar's links on a view whose figures are blurred
PORTAL_PILL_CSS = """
  .rbx-bar a.portal { margin-left:8px; border:1px solid rgba(255,255,255,.38); color:#fff; font-weight:600; }
  .rbx-bar a.portal:hover { background:#fff; color:#0d1b23; }
"""


def head(title, description, extra=""):
    t, d = html.escape(title), html.escape(description)
    return f"""<!DOCTYPE html>
<html lang="en-GB"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{t}</title>
<meta name="description" content="{d}">
<meta name="theme-color" content="#12475e">
{FAVICON}
{extra}</head>"""


def forward_script(pack_key, views):
    """An old ?view=<key> link (the Streamlit app's address, its domain swapped) opens the model's page."""
    routes = {k: f"/{pack_key}/{v['slug']}/" for k, v in views.items()}
    return ("<script>(function(){var r=" + json.dumps(routes, separators=(",", ":"))
            + ',v=new URLSearchParams(location.search).get("view");'
            + 'if(v&&Object.prototype.hasOwnProperty.call(r,v))location.replace(r[v]+location.hash);})();</script>')


def landing(pack_key, pack):
    """The pack's landing fragment in a document of its own, its ?view= links made real addresses."""
    frag = source(pack["home"])
    slugs = {k: v["slug"] for k, v in pack["views"].items()}

    def to_path(m):
        if m.group(1) not in slugs:
            raise PageError(f"{pack['home']}: link to unknown view ?view={m.group(1)}")
        return f'href="/{pack_key}/{slugs[m.group(1)]}/"'
    frag = re.sub(r'href="\?view=([a-z]+)"', to_path, frag)
    frag = frag.replace('href="?view=home"', f'href="/{pack_key}/"')
    if "?view=" in frag:
        raise PageError(f"{pack['home']}: a ?view= link the build does not understand")
    # the fragments paint Streamlit's own .stApp; here that is the page wrapper
    base = "<style>html{scroll-behavior:smooth} html,body{margin:0} body{background:#f4f8fa}.stApp{min-height:100vh}</style>"
    return (head(pack["title"], pack["description"], base + "\n" + forward_script(pack_key, pack["views"]))
            + f'\n<body><div class="stApp">\n{frag}\n</div></body></html>\n')


def frame_page(pack_key, pack, key):
    """A model's page: the pack bar on top, the model framed below it (model.html beside it)."""
    view = pack["views"][key]
    links = []
    for k, v in pack["views"].items():
        active = ' class="active" aria-current="page"' if k == key else ""
        links.append(f'<a href="/{pack_key}/{v["slug"]}/"{active}><span class="lbl-f">{v["label"]}</span>'
                     f'<span class="lbl-s">{v["short"]}</span></a>')
    portal = (f'<a href="{packs.PORTAL_URL}" target="_blank" rel="noopener" class="portal">Investor data &rarr; portal</a>'
              if key in pack["gated"] else "")
    return (head(f'RenewaBlox — {view["label"]}', pack["description"], f"<style>{FRAME_CSS}{PORTAL_PILL_CSS}</style>\n")
            + f"""
<body>
<div class="rbx-bar">
  <a href="/{pack_key}/" class="back">&larr; All models</a>
  <div class="crumb">{pack["crumb"]} &middot; {view["label"]}</div>
  <nav>{"".join(links)}{portal}</nav>
</div>
<iframe class="rbx-model" src="model.html" title="{html.escape(view["label"])}" allow="fullscreen"></iframe>
</body></html>
""")


def model(pack, key):
    """The model as the pack serves it: its head patch, and in the public demo the blur and the portal card."""
    view = pack["views"][key]
    page = source(view["file"])
    if view.get("head"):
        page = once(page, "</head>", view["head"] + "</head>", view["file"])
    g = pack["gated"].get(key)
    if g:
        css = packs.GATE_CSS.format(blur=g["blur"], hide=g["hide"] or "#rbx-gate-none", top=g["top"], right=g.get("right", "18px"))
        page = once(page, "</head>", f"<style>{css}</style></head>", view["file"])
        page = once(page, "</body>", packs.GATE_HTML.format(url=packs.PORTAL_URL) + "</body>", view["file"])
    return page


def investor_pages():
    """{site path: text} for the three investor packs and the two standalone peakers."""
    out = {}
    for pack_key, pack in PACKS.items():
        out[f"{pack_key}/index.html"] = landing(pack_key, pack)
        for key, view in pack["views"].items():
            out[f"{pack_key}/{view['slug']}/index.html"] = frame_page(pack_key, pack, key)
            out[f"{pack_key}/{view['slug']}/model.html"] = model(pack, key)
    # on links of their own the models are the top window, which a phone would pan sideways where the model's panels
    # are wider than the screen; the packs' frame (and Streamlit's before it) clips them at the screen's edge
    peaker = source("peaker_plant_3d.html")
    clip = "<style>html{overflow:hidden}</style>"
    out["models/peaker-plant/index.html"] = once(peaker, "</head>", packs.PEAKER_PLANT_HEAD + clip + "</head>", "peaker_plant_3d.html")
    demo = once(peaker, "</head>", packs.PEAKER_DEMO_HEAD + clip + "</head>", "peaker_plant_3d.html")
    out["models/peaker-demo/index.html"] = once(demo, "<title>RenewaBlox — Peaker Plant 3D</title>",
                                                "<title>RenewaBlox — Peaker Demo</title>", "peaker_plant_3d.html")
    return out
