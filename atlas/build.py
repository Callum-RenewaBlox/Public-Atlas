"""Build atlas.renewablox.com, the RenewaBlox Atlas, into atlas/site/.

    /             the Atlas front page (root/index.html), with its Client Atlas section (front/clients.html)
                  put in place between marker comments and the section's cover images under /assets/img/clients/
    /investors/   the Investor Atlas preview (root/investors/index.html)
    /market/      the Market Atlas page (root/market/index.html), which frames the map below
    /market/map/  the Market Atlas map: Eunice-Platform's client_atlas_v2.html (a copy in vendor/), with the
                  deep links its Streamlit wrapper used to read now read by the page itself (MAPS)
    /clients/, /team/   the client atlases and the team's pages, behind the sign-in (pages.py, team/), BLN's
                  among them: /clients/bln/, the powerhouse on the satellite imagery with the BLOX badge
                  (bln/index.html), and /clients/bln/3d/, the 3D render the badge opens (bln/3d/index.html);
                  its old public address, /bln/, now redirects there (_redirects)
    /investors/demo/, /investors/australia/, /investors/portal/, /models/   the investor packs and the
                  standalone peakers (pages.py), with the Investor Atlas at /investors/portal/atlas/
                  (Eunice-Platform's investor_atlas_v3.html, a copy in vendor/). The portal is not gated here:
                  the Wix investor portal's members area links to it, and the Wix site may frame it

Every page here was once a Streamlit app; pages.py says how each is put in place without one.

The renewablox-atlas Netlify project builds the site from this folder on every push (netlify.toml);
nothing of it is hosted anywhere else. root/ holds the Atlas site's own files, served at the root of the
domain as they are, with root/_headers for their header rules. The build puts every page in place and
checks what would otherwise go wrong quietly:

  * nothing on the site points at Streamlit (a streamlit.app or share.streamlit.io address anywhere fails it);
  * each map (MAPS) loads only from its hosts, every one of which its Content-Security-Policy allows, and
    each page takes its Content-Security-Policy from exactly one header rule (Netlify joins a header set by
    two matching rules into one value, which would turn two policies into one broken one), or from its gate;
  * the two brand fonts (FONTS) are fetched from renewablox.com's own font files and must match their
    hashes: they are licensed for the website, so they are not kept in this public repository.

The client pages built here (CLIENTS) are behind the sign-in, so they may name their site in full; what stays
public is their cover on the front page (front/), which is checked further:

  * anonymity: the cover names the client by its code (BLN) only. No file in front/ may carry a word that names
    or places the site (the list is kept out of this public repository, in atlas/.names or ATLAS_NAMES), nor a
    postcode, grid reference, company number or Windows path (TEXT_PATTERNS), nor image metadata.

And the client pages themselves: nothing loads from elsewhere except the satellite imagery (ALLOWED_HOSTS),
every file a page refers to is there, every page asks not to be indexed, and the powerhouse's position on the
imagery has been confirmed (a warning until it is).

Run:  python atlas/build.py                      (writes atlas/site/, git-ignored)
      python -m http.server 8901 -d atlas/site   (then open http://localhost:8901/)
      python atlas/build.py --sync               (copies the latest of each page vendor/ holds from its own
                                                  repository's main branch, to be committed like any change)
On Netlify (NETLIFY=true) the build refuses to run without the list of names, as the site it builds is
published; the netlify.toml beside this file says where that list is kept there.
Standard library only.
"""
import hashlib
import json
import os
import re
import shutil
import struct
import sys
import urllib.request
from pathlib import Path

import pages  # the pages that came off Streamlit (beside this file)
import site_inputs  # the list of what the site is built from (inputs.txt), checked against what the build reads

HERE = Path(__file__).resolve().parent
OUT = HERE / "site"
ROOT = HERE / "root"
CLIENTS = ["bln"]
ON_NETLIFY = os.environ.get("NETLIFY") == "true"

# The words that would name or place a client's site (the site, the places around it, the firms on
# its drawings), which its public cover on the front page must never carry, are never written in this
# public repository, not even as hashes, which a gazetteer reverses in seconds. They live in atlas/.names (git-ignored, one word per line, # for comments) or
# in the ATLAS_NAMES environment variable (comma-separated). A build without them warns here, and on
# Netlify, where the site it builds is published, refuses to run.
NAMES_FILE = HERE / ".names"
# Generic shapes, checked case-sensitively in the text files: UK postcodes, OS grid references,
# Scottish company numbers, and the home folders of a Windows machine.
TEXT_PATTERNS = [r"\b[A-Z]{1,2}\d[A-Z\d]? \d[A-Z]{2}\b", r"\b[HNOST][A-HJ-Z] ?\d{3,5} ?\d{3,5}\b",
                 r"\bSC\d{6}\b", r"(?i)[A-Z]:\\Users\\"]
TEXT_SUFFIXES = {".html", ".css", ".js", ".json", ".txt", ".md", ".svg"}

# The only place a page may load from: the satellite imagery under the map. www.w3.org appears as
# the SVG namespace in data images and is never fetched.
ALLOWED_HOSTS = {"server.arcgisonline.com"}
NAMESPACE_HOSTS = {"www.w3.org"}

# The front page's Client Atlas section: front/clients.html, and the images beside it, which go to
# /assets/img/clients/. The build replaces whatever lies between these two comments on the front page (the
# first still names --merge, the step that used to do it, as the live page carries it).
FRONT = HERE / "front"
FRONT_BEGIN = "<!-- client atlas (Public-Atlas atlas/front/clients.html, placed by atlas/build.py --merge) -->"
FRONT_END = "<!-- end of client atlas -->"
FRONT_ASSETS = "assets/img/clients"

HEADERS_BEGIN = "# --- the investor portal (written by atlas/build.py from its pack) ---"
HEADERS_END = "# --- end of the investor portal ---"
# The Wix site that links to the investor portal and may frame it: its pages, its editor and its embed host.
PORTAL_FRAMERS = ("'self' https://www.renewablox.com https://renewablox.com https://*.wixsite.com https://*.wix.com "
                  "https://*.filesusr.com")

# The two atlas maps built in Eunice-Platform (its atlas/build.py) and copied into vendor/: the Market Atlas at
# /market/map/, framed by the market page, and the Investor Atlas at /investors/portal/atlas/, in the investor portal
# (it carries site-level commercial detail: contract values, BTC, operators). Each page leaves a placeholder for its
# host to fill with window.__ATLAS_INIT__: on Streamlit its wrapper filled it from the query string after checking
# each value; here the page does the same with the same patterns, then takes those parameters out of its address, so
# the view it writes to its #hash is what a reload, a bookmark or a copied address opens (the market's ?present=1,
# which that page reads itself, stays). "Copy link" builds on the config's publicUrl, pointed here at the page's own
# address.
SITE_HOST = "atlas.renewablox.com"
MAP_PLACEHOLDER = "/*__ATLAS_INIT__*/"


def map_init(allowed):
    return ("(function(){var A={" + ",".join(f"{k}:{rx}" for k, rx in allowed.items()) + "},"
            "q=new URLSearchParams(location.search),o={},n=0,k,v;for(k in A){v=q.get(k);"
            "if(v!==null&&A[k].test(v))o[k]=v;if(q.has(k)){q.delete(k);n++;}}window.__ATLAS_INIT__=o;"
            "if(n){v=q.toString();try{history.replaceState(null,'',location.pathname+(v?'?'+v:'')+location.hash);}"
            "catch(e){}}})();")


_VIEW_SITE_THEME = {"view": "/^(sam|tam|hydro|ppa)$/", "site": "/^[A-Za-z0-9-]{1,48}$/", "theme": "/^(paper|night)$/"}
MAPS = {
    "market": {
        "file": "client_atlas_v2.html", "target": "market/map/index.html", "url": f"https://{SITE_HOST}/market/",
        "init": map_init(_VIEW_SITE_THEME),
        # MapLibre and its stylesheet, Open Sans, the base map, the terrain and postcodes (its near-me search)
        "hosts": {"cdn.jsdelivr.net", "fonts.googleapis.com", "fonts.gstatic.com", "tiles.openfreemap.org",
                  "s3.amazonaws.com", "api.postcodes.io"},
    },
    "investor": {
        "file": "investor_atlas_v3.html", "target": "investors/portal/atlas/index.html",
        "url": f"https://{SITE_HOST}/investors/portal/atlas/",
        # app_investor_atlas_v3.py also passed ?present=1 on, which this page does not read itself
        "init": map_init({**_VIEW_SITE_THEME, "present": "/^1$/"}),
        # the market's hosts but postcodes.io, which this map only credits
        "hosts": {"cdn.jsdelivr.net", "fonts.googleapis.com", "fonts.gstatic.com", "tiles.openfreemap.org",
                  "s3.amazonaws.com"},
    },
}
# The pages vendor/ holds, copied from their own repositories (--sync refreshes them).
VENDOR = HERE / "vendor"
_RAW = "https://raw.githubusercontent.com/Callum-RenewaBlox"
VENDORED = {
    "client_atlas_v2.html": f"{_RAW}/Eunice-Platform/main/client_atlas_v2.html",
    "investor_atlas_v3.html": f"{_RAW}/Eunice-Platform/main/investor_atlas_v3.html",
    "wn_infrastructure_map.html": f"{_RAW}/Reabold-Atlas/main/wn_infrastructure_map.html",
    "reservoir_map.html": f"{_RAW}/Reabold-Atlas/main/reservoir_map.html",
    "citygate_electricity.html": f"{_RAW}/Electricity-Analysis/main/citygate_electricity.html",
}
# A link out of a map must open a new tab: followed inside the market page's frame, it would be refused
# (frame-src 'self') and leave an error page where the map was; the Investor Atlas may sit in the Wix portal's frame. The build adds target="_blank" to any that lacks it.
MAP_LINK = re.compile(r"""<a href=(\\?["'])(https?://[^"'\\]+)\1>""")
MAP_LINK_ANY = re.compile(r"""<a\s[^>]*?href=\\?["']https?://[^>]*>""")

# The brand fonts, as renewablox.com serves them (the Wix site's uploaded fonts), fetched at build time.
FONTS = {
    "assets/fonts/telegraf-regular.woff2": (
        "https://static.wixstatic.com/ufonts/cf5726_79e38b37da5449e5b14f405020faa098/woff2/file.woff2",
        "feca33b49819dbb4943b83db8d68e1f8840c92032b90f3a355902017e56d28bd"),
    "assets/fonts/garet-book.woff2": (
        "https://static.wixstatic.com/ufonts/e0c63f_dd8ef7e318764b8aa50aae38de0fb7c0/woff2/file.woff2",
        "30329680a639d076033f725b84ef0cab77df14b1797f2b487bd24f30e6496608"),
}

STREAMLIT = re.compile(r"streamlit\.app|share\.streamlit\.io", re.I)

# Pages behind a gate. Everything under these folders passes through an edge function (netlify/edge-functions/):
# /clients/ and /team/ through the sign-in (atlas-gate.js: Google or Microsoft through Supabase, access per client in
# public.atlas_access, '*' for the team).
# Netlify's _headers rules don't reach those responses, so the gates set each page's headers themselves, from the
# policies here; the build writes GATED_PAGES, EDGE_CSP and EDGE_REDIRECTS to netlify/edge-lib/pages.js for them.
GATED_PREFIXES = ("/clients/", "/team/")
EDGE_LIB = HERE / "netlify" / "edge-lib" / "pages.js"
# Team pages written by hand for the site (team/<page>/), copied as they are to /team/<page>/.
TEAM = HERE / "team"
# path -> {client: code or '*' (team only), title, list: shown on /clients/, views: {view: file in the folder}}
GATED_PAGES = {
    "/team/outreach/": {"client": "*", "title": "Outreach strategy (RenewaBlox × tem)", "list": True},
    "/clients/bln/": {"client": "bln", "title": "BLN Atlas", "list": True},
    "/clients/bln/3d/": {"client": "bln", "title": "BLN 3D model", "list": True},
}
# folder -> Content-Security-Policy for every file in it (the longest folder holding a path wins)
EDGE_CSP = {
    # one self-contained page: inline script and styles, Inter and IBM Plex Mono from Google Fonts
    "/team/outreach/": ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline' https://fonts.googleapis.com; "
                        "font-src https://fonts.gstatic.com; img-src data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"),
    # BLN: the pages load their own files and, for the map, the satellite imagery; the 3D viewer fetches its models
    # from the same folder (and compiles its mesh decoder, so WebAssembly is allowed, not eval)
    "/clients/bln/": ("default-src 'self'; script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval'; style-src 'self' 'unsafe-inline'; "
                      "img-src 'self' data: blob: https://server.arcgisonline.com; font-src 'self'; connect-src 'self' blob: data:; "
                      "media-src 'self'; worker-src 'self' blob:; object-src 'none'; base-uri 'none'; form-action 'none'; "
                      "frame-ancestors 'self'"),
}
# old address -> new one, answered by the sign-in once the visitor is in
EDGE_REDIRECTS = {}
# the pages that came off Streamlit (pages.py)
GATED_PAGES.update(pages.CLIENT_PAGES)
EDGE_CSP.update(pages.CLIENT_CSP)
EDGE_REDIRECTS.update(pages.CLIENT_REDIRECTS)
# The Investor Atlas's policy: MapLibre from jsDelivr, Open Sans, OpenFreeMap and the AWS terrain, workers from blob:
# URLs (site_headers adds the frame-ancestors: the Wix portal may frame it)
INVESTOR_ATLAS_CSP = (
    "default-src 'none'; script-src 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; font-src data: https://fonts.gstatic.com; "
    "img-src data: blob: https://tiles.openfreemap.org https://s3.amazonaws.com; "
    "connect-src https://tiles.openfreemap.org https://s3.amazonaws.com; worker-src blob:; child-src blob:; "
    "object-src 'none'; base-uri 'none'; form-action 'none'")
# BLN's old public address, now behind the sign-in: Netlify answers these before the site's files (_redirects)
SITE_REDIRECTS = [("/bln", "/clients/bln/"), ("/bln/*", "/clients/bln/:splat")]


def fail(msg):
    raise SystemExit("atlas/build.py: " + msg)


def load_names():
    """The deny-list, or None when this machine has none (never printed, never echoed)."""
    words = set()
    if NAMES_FILE.is_file():
        # utf-8-sig: a list saved by a Windows editor starts with a byte-order mark, which would
        # otherwise stick to the first word (most likely the site's own name) and stop it matching
        for line in NAMES_FILE.read_text(encoding="utf-8-sig").splitlines():
            line = line.split("#", 1)[0].strip().lower()
            if line:
                words.add(line)
    words.update(w.strip().lower() for w in os.environ.get("ATLAS_NAMES", "").split(",") if w.strip())
    return words or None


def check_names(path, rel, names):
    data = path.read_bytes()
    low = data.lower()
    for w in names or ():
        if any(w.encode(enc) in low for enc in ("utf-8", "utf-16-le", "utf-16-be")):
            fail(f"{rel} carries a word from the list of names (atlas/.names); a client page is named by its code only")
    if path.suffix in TEXT_SUFFIXES:
        text = data.decode("utf-8", "replace")
        for pat in TEXT_PATTERNS:
            m = re.search(pat, text)
            if m:
                fail(f"{rel} carries {m.group(0)!r}, which could place the site")


def check_image(b, rel):
    """Images go out as pixels only: no EXIF, XMP, comments or text chunks, which renders and cameras fill in.
    The kind is read from the bytes, not the name; JPEG and PNG are walked, and any other image is refused."""
    if b[:3] == b"\xff\xd8\xff":
        i = 2
        while i + 4 <= len(b) and b[i] == 0xFF and b[i + 1] != 0xDA:
            marker, length = b[i + 1], int.from_bytes(b[i + 2:i + 4], "big")
            if 0xE1 <= marker <= 0xEF or marker == 0xFE:
                fail(f"{rel} carries metadata (JPEG segment 0x{marker:02X}); strip it")
            i += 2 + length
    elif b[:8] == b"\x89PNG\r\n\x1a\n":
        i = 8
        while i + 8 <= len(b):
            length, kind = struct.unpack(">I4s", b[i:i + 8])
            if kind in (b"tEXt", b"zTXt", b"iTXt", b"eXIf"):
                fail(f"{rel} carries metadata (PNG {kind.decode()} chunk); strip it")
            i += 12 + length
    elif (b[:4] == b"RIFF" and b[8:12] == b"WEBP") or b[:4] == b"GIF8" or b[4:12] in (b"ftypavif", b"ftypavis"):
        fail(f"{rel} is a WebP, GIF or AVIF image, whose metadata this build does not read; use a JPEG or PNG")


def check_metadata(path, rel):
    b = path.read_bytes()
    check_image(b, rel)
    if b[:4] == b"glTF":   # and the images packed inside a model
        clen = struct.unpack_from("<I", b, 12)[0]
        j = json.loads(b[20:20 + clen])
        binstart = 20 + clen + 8
        for i, img in enumerate(j.get("images", [])):
            if "bufferView" in img:
                bv = j["bufferViews"][img["bufferView"]]
                start = binstart + bv.get("byteOffset", 0)
                check_image(b[start:start + bv["byteLength"]], f"{rel} (image {i})")


SCRIPT = re.compile(r"(<script\b[^>]*>)(.*?)(</script>)", re.S | re.I)
TAG = re.compile(r"""<([a-zA-Z][\w-]*)\b((?:[^>"']|"[^"]*"|'[^']*')*)>""")   # a '>' inside quotes does not end it
ATTR = re.compile(r"""([\w:-]+)\s*=\s*("[^"]*"|'[^']*'|[^\s"'>]+)""")
CSS_URL = re.compile(r"""url\(\s*["']?([^"')]+?)["']?\s*\)|@import""", re.I)
REMOTE = re.compile(r"^\s*(?:https?:|wss?:)?//([^/\s]+)", re.I)
SCRIPT_URL = re.compile(r"""["'`(]\s*(?:https?:|wss?:)?//([^/"'`\s)]+)""", re.I)
SCRIPT_ASSET = re.compile(r"""["'](\.\./assets/[^"']+|assets/[^"']+)["']""")
SCRIPT_MODULE = re.compile(r"""\bimport\(\s*["'`](\.{1,2}/[^"'`?#]+)""")   # a module the page fetches on use
REF_ATTRS = {"src", "href", "data-full", "poster", "srcset"}


def check_local(page, rel, root, ref):
    if not ref:   # a link to this page's own address with only a ?query or #fragment
        return
    if ref.endswith("/"):
        folder = (page.parent / ref).resolve()
        # a folder above the client's own (the Atlas front page) is on the live site, not in this build
        if (folder == root or root in folder.parents) and not (folder / "index.html").is_file():
            fail(f"{rel} links to {ref}, which has no index.html")
        return
    target = (page.parent / ref).resolve()
    if root not in target.parents or not target.is_file():
        fail(f"{rel} refers to {ref}, which is not in the build")


def check_css(text, rel, page, root):
    for m in CSS_URL.finditer(text):
        if m.group(0).lower() == "@import":
            fail(f"{rel} imports a stylesheet; inline it or link it from the page")
        ref = m.group(1).strip()
        if ref.startswith(("data:", "#")):
            continue
        r = REMOTE.match(ref)
        if r:
            if r.group(1) not in ALLOWED_HOSTS | NAMESPACE_HOSTS:
                fail(f"{rel} loads {ref} from elsewhere")
        elif page is not None:
            check_local(page, rel, root, ref.split("?")[0])


def check_page(page, rel, root):
    text = page.read_text(encoding="utf-8")
    if not re.search(r'<meta name="robots" content="noindex', text):
        fail(f"{rel} must ask not to be indexed")
    scripts = "\n".join(m.group(2) for m in SCRIPT.finditer(text))
    markup = SCRIPT.sub(lambda m: m.group(1) + m.group(3), text)
    # the markup: every address in an attribute, and every url() in its styles
    for tag in TAG.finditer(markup):
        name = tag.group(1).lower()
        for a in ATTR.finditer(tag.group(2)):
            attr, value = a.group(1).lower(), a.group(2).strip("\"'")
            r = REMOTE.match(value)
            if r:
                # a link the visitor follows is not a load; anything else must come from an allowed host
                if not (name == "a" and attr == "href") and r.group(1) not in ALLOWED_HOSTS | NAMESPACE_HOSTS:
                    fail(f"{rel} loads something from elsewhere: <{name} {attr}={value[:80]!r}>")
                continue
            if attr not in REF_ATTRS or value.startswith(("#", "data:", "mailto:")) or ":" in value.split("/")[0]:
                continue
            for ref in ([s.strip().split()[0] for s in value.split(",") if s.strip()] if attr == "srcset" else [value]):
                check_local(page, rel, root, ref.split("#")[0].split("?")[0])
    check_css(markup, rel, page, root)
    # the scripts: any address they could fetch, and every asset path they name
    for host in SCRIPT_URL.findall(scripts):
        if host not in ALLOWED_HOSTS | NAMESPACE_HOSTS:
            fail(f"{rel} reaches {host}, which is not an allowed host")
    for ref in SCRIPT_ASSET.findall(scripts) + SCRIPT_MODULE.findall(scripts):
        check_local(page, rel, root, ref)
    return text


def site_confirmed(text):
    m = re.search(r"const SITE=\{[^}]*confirmed:(true|false)", text)
    if not m:
        fail("bln/index.html: SITE not found")
    return m.group(1) == "true"


def build(names):
    if OUT.exists():
        shutil.rmtree(OUT)
    warnings = []
    if names is None:
        warnings.append("no list of names (atlas/.names or ATLAS_NAMES), so the pages were not checked for the "
                        "site's name; a build on Netlify refuses to run until there is one")
    # the client pages built here, behind the sign-in at /clients/<code>/: they may name their site, so only their
    # public cover (front/) is held to the names (check_front)
    for client in CLIENTS:
        src = HERE / client
        for path in sorted(src.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(HERE).as_posix()
            if path.suffix == ".css":
                check_css(path.read_text(encoding="utf-8"), rel, None, None)
            # a page's own script module (bln/3d/dispatch.js) is held to its page's rule; the vendored libraries
            # in assets/ carry their authors' URLs, which the pages' security policy keeps from loading
            if path.suffix == ".js" and "assets" not in path.relative_to(HERE).parts:
                for host in SCRIPT_URL.findall(path.read_text(encoding="utf-8")):
                    if host not in ALLOWED_HOSTS | NAMESPACE_HOSTS:
                        fail(f"{rel} reaches {host}, which is not an allowed host")
            dest = OUT / "clients" / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
        for page in sorted(src.rglob("index.html")):
            text = check_page(page, page.relative_to(HERE).as_posix(), src.resolve())
            if page.parent == src and not site_confirmed(text):
                warnings.append(f"{client}/index.html: the powerhouse's place on the imagery is not confirmed yet "
                                f"(open /clients/{client}/?place, set it, and paste the line into SITE)")
    put_root(names)
    merge_front(OUT)
    warnings += put_fonts()
    put_map("market")
    put_map("investor")
    put_team()
    put_pages()
    check_front(names)   # once every page is in place, so the section may link to any of them
    headers = site_headers()
    (OUT / "_headers").write_text(headers, encoding="utf-8")
    (OUT / "_redirects").write_text("".join(f"{old}  {new}  301\n" for old, new in SITE_REDIRECTS), encoding="utf-8")
    write_edge_lib()
    check_site(headers)
    total = 0
    for p in sorted(OUT.rglob("*")):
        if p.is_file():
            total += p.stat().st_size
            print(f"  {p.relative_to(OUT)}  {p.stat().st_size / 1024:,.0f} kB")
    print(f"  {total / 1048576:.1f} MB in all")
    for w in warnings:
        print("WARNING: " + w)
    return headers


def check_front(names):
    """The front page's section: no names, no metadata, nothing from elsewhere, and every address it uses
    is either a client page built here or an image beside it."""
    for path in sorted(FRONT.iterdir()):
        check_names(path, f"front/{path.name}", names)
        check_metadata(path, f"front/{path.name}")
    text = (FRONT / "clients.html").read_text(encoding="utf-8")
    for tag in TAG.finditer(text):
        for a in ATTR.finditer(tag.group(2)):
            value = a.group(2).strip("\"'")
            r = REMOTE.match(value)
            if r and r.group(1) not in NAMESPACE_HOSTS:
                fail(f"front/clients.html loads something from elsewhere: {value[:80]!r}")
            if a.group(1).lower() in REF_ATTRS and value.startswith("/"):
                path = value.split("#")[0].split("?")[0].lstrip("/")
                if path.startswith(FRONT_ASSETS + "/"):
                    ok = (FRONT / path[len(FRONT_ASSETS) + 1:]).is_file()
                elif path == "" or path.endswith("/"):
                    ok = (OUT / path / "index.html").is_file()
                else:
                    ok = (OUT / path).is_file()
                if not ok:
                    fail(f"front/clients.html refers to {value}, which neither the build nor front/ provides")


def merge_front(dest):
    """Put the Client Atlas section on the front page, between its markers, and its images beside it."""
    page = dest / "index.html"
    text = page.read_text(encoding="utf-8")
    if text.count(FRONT_BEGIN) != 1 or text.count(FRONT_END) != 1 or text.index(FRONT_END) < text.index(FRONT_BEGIN):
        print("WARNING: the front page has no client atlas markers, so its Client Atlas section was left as it is; "
              "put the two marker comments (FRONT_BEGIN, FRONT_END) where the section belongs and build again")
        return
    section = (FRONT / "clients.html").read_text(encoding="utf-8").rstrip("\n")
    a = text.index(FRONT_BEGIN) + len(FRONT_BEGIN)
    b = text.index(FRONT_END)
    page.write_text(text[:a] + "\n" + section + "\n  " + text[b:], encoding="utf-8")
    images = dest / FRONT_ASSETS
    images.mkdir(parents=True, exist_ok=True)
    for path in sorted(FRONT.iterdir()):
        if path.suffix != ".html":
            shutil.copy2(path, images / path.name)


def put_root(names):
    """The Atlas site's own files, at the root of the site as they are (their header rules go into _headers)."""
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.relative_to(ROOT).as_posix() == "_headers":
            continue
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix in TEXT_SUFFIXES:   # the front page carries the client section, so it is held to its rule
            check_names(path, f"root/{rel}", names)
        target = OUT / rel
        if target.exists():
            fail(f"root/{rel} would replace {rel}, which the build has already put in place")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def put_team():
    """The team pages written for the site (team/), at /team/ as they are; the sign-in lets only the team in."""
    for path in sorted(TEAM.rglob("*")):
        if path.is_file():
            target = OUT / "team" / path.relative_to(TEAM)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def put_fonts():
    """The brand fonts, fetched from renewablox.com's own files and checked against their hashes. A build here
    without them (offline) warns, and the pages fall back to the system font; on Netlify it fails instead."""
    warnings = []
    for rel, (url, digest) in FONTS.items():
        try:
            data = urllib.request.urlopen(url, timeout=60).read()
        except OSError as e:
            if ON_NETLIFY:
                fail(f"could not fetch {rel} from {url}: {e}")
            warnings.append(f"could not fetch {rel} ({e}), so the pages will fall back to the system font")
            continue
        got = hashlib.sha256(data).hexdigest()
        if got != digest:
            fail(f"{url} is not the font {rel} was built with (sha256 {got}); check the new file and update FONTS")
        target = OUT / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return warnings


URL_HOST = re.compile(r"(?:https?:)?//([a-z0-9.-]+\.[a-z]{2,})", re.I)
A_HREF = re.compile(r"""<a\s[^>]*href=\\?["']$""")   # an <a href> in the markup, or in a string of the page's script


def market_hosts(page):
    """Every host a map page names, except in a link (<a href>), as the SVG namespace or as the Atlas itself
    (its "Copy link" base): what it loads from."""
    hosts = set()
    for m in URL_HOST.finditer(page):
        host = m.group(1).lower()
        if (host in NAMESPACE_HOSTS or host == SITE_HOST
                or A_HREF.search(page[page.rfind("<", 0, m.start()):m.start()])):
            continue
        hosts.add(host)
    return hosts


def put_map(name):
    """An atlas map (MAPS) in place: the copy from Eunice-Platform with its deep links read by the page itself, its
    "Copy link" base pointed at its own address, and its links out opened in a new tab."""
    m = MAPS[name]
    page = (VENDOR / m["file"]).read_text(encoding="utf-8")
    if page.count(MAP_PLACEHOLDER) != 1:
        fail(f"vendor/{m['file']} should hold {MAP_PLACEHOLDER} once, for the page's deep links")
    page = page.replace(MAP_PLACEHOLDER, m["init"], 1)
    page, n = re.subn(r'"publicUrl":"[^"]*"', '"publicUrl":"' + m["url"] + '"', page)
    if n != 1:
        fail(f"vendor/{m['file']} should set publicUrl once in its config, but sets it {n} times")
    page = MAP_LINK.sub(lambda g: f'<a href={g.group(1)}{g.group(2)}{g.group(1)} target={g.group(1)}_blank{g.group(1)} '
                                  f'rel={g.group(1)}noopener{g.group(1)}>', page)
    stay = [g.group(0) for g in MAP_LINK_ANY.finditer(page) if "target=" not in g.group(0)]
    if stay:
        fail(f"vendor/{m['file']} links out without opening a new tab, which its frame would refuse: {stay[0][:100]}")
    extra = market_hosts(page) - m["hosts"]
    if extra:
        fail(f"vendor/{m['file']} loads from {', '.join(sorted(extra))}, which MAPS[{name!r}] and the page's "
             "Content-Security-Policy do not allow")
    target = OUT / m["target"]
    if target.exists():
        fail(f"{m['target']} is built from vendor/{m['file']}, so nothing else may put one there")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page, encoding="utf-8")


def put_pages():
    """The client atlases, the team's pages, the investor packs and the standalone models (pages.py)."""
    try:
        built = {**pages.client_pages(), **pages.investor_pages()}
    except pages.PageError as e:
        fail(str(e))
    for rel, text in built.items():
        target = OUT / rel
        if target.exists():
            fail(f"{rel} would replace a file the build has already put in place")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def site_headers():
    """The site's _headers: the Atlas site's own rules (root/_headers), then the investor portal's between marker
    lines, one rule per part of the pack so that no address takes two policies: the landing page and each model
    with the models' policy, the Investor Atlas with its own; the Wix site may frame any of them."""
    own = (ROOT / "_headers").read_text(encoding="utf-8").rstrip("\n")
    base = "/investors/portal/"
    model = pages.MODEL_CSP.replace("frame-ancestors 'self'", f"frame-ancestors {PORTAL_FRAMERS}")
    if model == pages.MODEL_CSP:
        fail("pages.MODEL_CSP no longer ends in frame-ancestors 'self'; update site_headers")
    rules = [(base, model), (base + "index.html", model)]
    rules += [(f"{base}{v['slug']}/*", model) for v in pages.PACKS["investors/portal"]["views"].values()]
    rules += [(base + "atlas/*", f"{INVESTOR_ATLAS_CSP}; frame-ancestors {PORTAL_FRAMERS}")]
    portal = "\n\n".join(f"{path}\n  Content-Security-Policy: {csp}\n  X-Robots-Tag: noindex, nofollow" for path, csp in rules)
    return own + "\n\n" + HEADERS_BEGIN + "\n" + portal + "\n" + HEADERS_END + "\n"


def header_rules(text):
    """[(path pattern, {header name: value})] for each rule of a _headers file."""
    rules = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line[0].isspace():
            rules.append((line.strip(), {}))
        elif rules:
            name, _, value = line.strip().partition(":")
            rules[-1][1][name.strip().lower()] = value.strip()
    return rules


def rule_matches(pattern, path):
    """As Netlify matches a header rule: * is anything, and a trailing slash is optional. A rule for a folder
    ("/market/") does not cover the address of its index ("/market/index.html"), which is served too."""
    return re.fullmatch(re.escape(pattern.rstrip("/")).replace(r"\*", ".*") + "/?", path) is not None


def check_site(headers):
    """Each page's security policy comes from one rule, the market map's allows what the map loads, and
    nothing on the site points at Streamlit."""
    rules = header_rules(headers)
    for page in sorted(OUT.rglob("*.html")):
        rel = page.relative_to(OUT).as_posix()
        paths = ["/" + rel]
        if rel.endswith("index.html"):   # a page is served at its folder's address and at its own
            paths.append("/" + rel[:-len("index.html")])
        if paths[0].startswith(GATED_PREFIXES):
            # served through a gate, which sets the headers: the policy must be in EDGE_CSP, and no _headers rule
            # may pretend to set one
            if not edge_policy(paths[0]):
                fail(f"{paths[0]} is behind a gate but has no Content-Security-Policy in EDGE_CSP")
            for path in paths:
                stray = [p for p, h in rules if "content-security-policy" in h and rule_matches(p, path)]
                if stray:
                    fail(f"{path} is behind a gate, where _headers rules don't apply, but {', '.join(stray)} sets its policy")
            continue
        for path in paths:
            for name in ("content-security-policy", "x-frame-options"):
                setters = [p for p, h in rules if name in h and rule_matches(p, path)]
                if len(setters) > 1:
                    fail(f"{path} takes {name} from {len(setters)} rules ({', '.join(setters)}), which Netlify would "
                         "join into one broken value")
            if rel.endswith("index.html") and not any("content-security-policy" in h and rule_matches(p, path)
                                                      for p, h in rules):
                fail(f"{path} has no Content-Security-Policy: give it a rule in root/_headers")
    for name, m in MAPS.items():
        path = "/" + m["target"][:-len("index.html")]
        if path.startswith(GATED_PREFIXES):
            csp = edge_policy(path) or ""
        else:
            csp = " ".join(h.get("content-security-policy", "") for p, h in rules if rule_matches(p, path))
        allowed = {token.rstrip(";") for token in csp.split()}
        missing = sorted(host for host in m["hosts"] if "https://" + host not in allowed)
        if missing:
            fail(f"the policy for {path} does not allow {', '.join(missing)}, which MAPS[{name!r}] loads from")
    # every file the site serves or is configured by (a redirect or proxy to Streamlit would count too)
    for f in sorted(OUT.rglob("*")) + [HERE / "netlify.toml"] + sorted((HERE / "netlify").rglob("*")):
        if f.is_file():
            text = f.read_bytes().decode("latin-1")
            m = STREAMLIT.search(text)
            if m:
                fail(f"{f.relative_to(HERE).as_posix()} points at Streamlit ({m.group(0)}); the Atlas is hosted here")


def edge_policy(path):
    """The gated path's policy: the longest EDGE_CSP folder that holds it, as the gates choose it."""
    best = max((p for p in EDGE_CSP if path.startswith(p)), key=len, default=None)
    return EDGE_CSP[best] if best else None


def write_edge_lib():
    """The gated pages, their policies and moved addresses, as a module for the edge functions (git-ignored, written
    by every build so the gates always match the site they guard)."""
    for path, pg in GATED_PAGES.items():
        if not path.startswith(GATED_PREFIXES) or not path.endswith("/"):
            fail(f"GATED_PAGES: {path} must be a folder under {', '.join(GATED_PREFIXES)}")
        if not (OUT / path.lstrip("/") / "index.html").is_file():
            fail(f"GATED_PAGES: {path} has no index.html in the build")
        for view, file in (pg.get("views") or {}).items():
            if not re.fullmatch(r"[a-z0-9-]{1,32}", view) or not (OUT / path.lstrip("/") / file).is_file():
                fail(f"GATED_PAGES: {path}?view={view} -> {file}, which is not in the build")
        if path.startswith(("/clients/", "/team/")):
            want = "*" if path.startswith("/team/") else path.split("/")[2]
            if pg.get("client") != want:
                fail(f"GATED_PAGES: {path} must be for client {want!r}, as the sign-in reads it from the address")
    for old, new in EDGE_REDIRECTS.items():
        if not old.startswith(("/clients/", "/team/")) or not new.startswith(("/clients/", "/team/")):
            fail(f"EDGE_REDIRECTS: {old} -> {new} must stay under /clients/ or /team/")
    js = lambda v: json.dumps(v, indent=1, sort_keys=True, ensure_ascii=True)
    EDGE_LIB.parent.mkdir(parents=True, exist_ok=True)
    EDGE_LIB.write_text("// Written by atlas/build.py: the gated pages, their policies and moved addresses. Do not edit.\n"
                        f"export const PAGES = {js(GATED_PAGES)};\nexport const CSP = {js(EDGE_CSP)};\n"
                        f"export const REDIRECTS = {js(EDGE_REDIRECTS)};\n", encoding="utf-8")


def sync():
    """Copy the latest of each page vendor/ holds from its own repository's main branch."""
    for name, url in VENDORED.items():
        data = urllib.request.urlopen(url, timeout=60).read()
        maps = [m for m in MAPS.values() if m["file"] == name]
        if maps:
            page = data.decode("utf-8")
            if page.count(MAP_PLACEHOLDER) != 1 or len(re.findall(r'"publicUrl":"[^"]*"', page)) != 1:
                fail(f"{url} no longer has the placeholder and the publicUrl this build fills in; see what changed there")
        path = VENDOR / name
        old = path.read_bytes() if path.is_file() else b""
        path.write_bytes(data)
        print(f"vendor/{name}: {'unchanged' if old == data else 'updated'} (sha256 {hashlib.sha256(data).hexdigest()[:12]})")
    print("build, look at what changed, and commit it")


def main():
    args = sys.argv[1:]
    if args == ["--sync"]:
        sync()
        return
    if args:
        fail("usage: python atlas/build.py [--sync]")
    names = load_names()
    if names is None and ON_NETLIFY:
        fail("refusing to build the site on Netlify without the list of names: set ATLAS_NAMES (the words that "
             "would name or place a client's site, comma-separated) in the renewablox-atlas project's environment "
             "variables, as a secret")
    site_inputs.watch()
    build(names)
    site_inputs.check("atlas/inputs.txt")


if __name__ == "__main__":
    main()
