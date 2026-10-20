"""Build the client pages for atlas.renewablox.com into atlas/site/.

    /bln/       BLN Atlas: the powerhouse on the satellite imagery, with the BLOX badge (bln/index.html)
    /bln/3d/    BLN 3D: the 3D render the badge opens (bln/3d/index.html)
    /           the Client Atlas section of the Atlas front page (front/clients.html), with its cover
                images under /assets/img/clients/, put in place by --merge between marker comments

Atlas itself (its front page, /investors/, /market/, /portal/) is the renewablox-atlas Netlify
project, deployed by upload from its own folder; this repository holds the client pages that go
into it. The build copies them into place and checks what would otherwise go wrong quietly:

  * anonymity: a client page is named by its code (BLN) only. No page or asset may carry a word that
    names or places the site (the list is kept out of this public repository, in atlas/.names), nor a
    postcode, grid reference, company number or Windows path (TEXT_PATTERNS), nor image metadata; the
    cabinet's nameplate in each GLB must be the short "BLOX.  50 kW" line, and the flythrough must be
    the reviewed file (FLYTHROUGH_SHA256);
  * nothing loads from elsewhere except the satellite imagery (ALLOWED_HOSTS);
  * every file a page refers to is there, and every page asks not to be indexed;
  * the powerhouse's position on the imagery has been confirmed (a warning until it is).

Run:  python atlas/build.py                      (writes atlas/site/, git-ignored)
      python -m http.server 8901 -d atlas/site   (then open http://localhost:8901/bln/)
      python atlas/build.py --merge DIR          (also puts bln/ and its header rules into DIR, a copy
                                                  of the Atlas site's own folder, ready to upload)
Standard library only.
"""
import hashlib
import json
import os
import re
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "site"
CLIENTS = ["bln"]

# The words that would name or place a client's site (the site, the places around it, the firms on
# its drawings) are never written in this public repository, not even as hashes, which a gazetteer
# reverses in seconds. They live in atlas/.names (git-ignored, one word per line, # for comments) or
# in the ATLAS_NAMES environment variable (comma-separated). A build without them warns; --merge,
# which prepares an upload, refuses to run.
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
# The flythrough as reviewed (title card reads "BLN", nothing else names the site). A new render
# must be checked frame by frame for the site's name before its hash goes here.
FLYTHROUGH_SHA256 = {"bln/assets/bln_flythrough_720p.mp4":
                     "7bc736ad98d6ef337d8f5ab28cbc06aa35620512674ca95e89d74bea51b4db8e"}
# The nameplate's second line reads "BLOX.  50 kW" (0.110 m); with the site's name it is 0.184 m.
NAMEPLATE_MAX_WIDTH_M = 0.15

# The front page's Client Atlas section: front/clients.html, and the images beside it, which go to
# /assets/img/clients/. --merge replaces whatever lies between these two comments on the front page.
FRONT = HERE / "front"
FRONT_BEGIN = "<!-- client atlas (Public-Atlas atlas/front/clients.html, placed by atlas/build.py --merge) -->"
FRONT_END = "<!-- end of client atlas -->"
FRONT_ASSETS = "assets/img/clients"

HEADERS_BEGIN = "# --- client pages (Public-Atlas atlas/build.py) ---"
HEADERS_END = "# --- end of client pages ---"


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


def check_nameplate(path, rel):
    b = path.read_bytes()
    clen = struct.unpack_from("<I", b, 12)[0]
    j = json.loads(b[20:20 + clen])
    node = next((n for n in j["nodes"] if n.get("name") == "rack_brand_text2"), None)
    if node is None:
        fail(f"{rel}: no rack_brand_text2 node, so the cabinet's nameplate cannot be checked")
    acc = j["accessors"][j["meshes"][node["mesh"]]["primitives"][0]["attributes"]["POSITION"]]
    width = acc["max"][0] - acc["min"][0]
    if width > NAMEPLATE_MAX_WIDTH_M:
        fail(f"{rel}: the cabinet's nameplate line is {width:.3f} m wide, so it still carries the site's name; "
             "cut it as the README describes")


SCRIPT = re.compile(r"(<script\b[^>]*>)(.*?)(</script>)", re.S | re.I)
TAG = re.compile(r"""<([a-zA-Z][\w-]*)\b((?:[^>"']|"[^"]*"|'[^']*')*)>""")   # a '>' inside quotes does not end it
ATTR = re.compile(r"""([\w:-]+)\s*=\s*("[^"]*"|'[^']*'|[^\s"'>]+)""")
CSS_URL = re.compile(r"""url\(\s*["']?([^"')]+?)["']?\s*\)|@import""", re.I)
REMOTE = re.compile(r"^\s*(?:https?:|wss?:)?//([^/\s]+)", re.I)
SCRIPT_URL = re.compile(r"""["'`(]\s*(?:https?:|wss?:)?//([^/"'`\s)]+)""", re.I)
SCRIPT_ASSET = re.compile(r"""["'](\.\./assets/[^"']+|assets/[^"']+)["']""")
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
    for ref in SCRIPT_ASSET.findall(scripts):
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
                        "site's name; --merge will refuse to run until there is one")
    for client in CLIENTS:
        src = HERE / client
        for path in sorted(src.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(HERE).as_posix()
            check_names(path, rel, names)
            check_metadata(path, rel)
            if path.suffix == ".glb":
                check_nameplate(path, rel)
            if path.suffix == ".css":
                check_css(path.read_text(encoding="utf-8"), rel, None, None)
            if rel in FLYTHROUGH_SHA256:
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                if digest != FLYTHROUGH_SHA256[rel]:
                    fail(f"{rel} is not the reviewed flythrough (sha256 {digest}). Check every frame, the title "
                         "card above all, for the site's name, then put the new hash in FLYTHROUGH_SHA256")
            dest = OUT / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
        for page in sorted(src.rglob("index.html")):
            text = check_page(page, page.relative_to(HERE).as_posix(), src.resolve())
            if page.parent == src and not site_confirmed(text):
                warnings.append(f"{client}/index.html: the powerhouse's place on the imagery is not confirmed yet "
                                f"(open /{client}/?place, set it, and paste the line into SITE)")
    check_front(names)
    headers = (HERE / "_headers").read_text(encoding="utf-8")
    (OUT / "_headers").write_text(headers, encoding="utf-8")
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
                else:
                    ok = (OUT / path / "index.html").is_file() if path.endswith("/") else (OUT / path).is_file()
                if not ok:
                    fail(f"front/clients.html refers to {value}, which neither the build nor front/ provides")


def merge_front(dest):
    """Put the Client Atlas section on the front page, between its markers, and its images beside it."""
    page = dest / "index.html"
    text = page.read_text(encoding="utf-8")
    if text.count(FRONT_BEGIN) != 1 or text.count(FRONT_END) != 1 or text.index(FRONT_END) < text.index(FRONT_BEGIN):
        print("WARNING: the front page has no client atlas markers, so its Client Atlas section was left as it is; "
              "put the two marker comments (FRONT_BEGIN, FRONT_END) where the section belongs and merge again")
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


def merge(dest, headers):
    """Put the client pages and their header rules into a copy of the Atlas site's own folder."""
    dest = Path(dest).resolve()
    repo = HERE.parent
    if dest == repo or repo in dest.parents or dest in repo.parents:
        fail(f"{dest} is part of this repository; give the folder the Atlas site is uploaded from")
    if not (dest / "index.html").is_file():
        fail(f"{dest} has no index.html: give the folder the Atlas site is uploaded from")
    for client in CLIENTS:
        target = dest / client
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(OUT / client, target)
    hp = dest / "_headers"
    old = hp.read_text(encoding="utf-8") if hp.exists() else ""
    block = HEADERS_BEGIN + "\n" + headers.strip() + "\n" + HEADERS_END + "\n"
    if HEADERS_BEGIN in old:
        old = re.sub(re.escape(HEADERS_BEGIN) + r".*?" + re.escape(HEADERS_END) + r"\n?", "", old, flags=re.S)
    hp.write_text(old.rstrip("\n") + ("\n\n" if old.strip() else "") + block, encoding="utf-8")
    merge_front(dest)
    print(f"merged {', '.join(CLIENTS)}, the header rules and the front page's Client Atlas section into {dest}")


def main():
    args = sys.argv[1:]
    if args[:1] == ["--merge"] and len(args) != 2:
        fail("usage: python atlas/build.py --merge DIR")
    names = load_names()
    if args[:1] == ["--merge"] and names is None:
        fail("refusing to prepare an upload without the list of names: put the words that would name or place "
             "the site in atlas/.names (git-ignored, one per line) or in ATLAS_NAMES")
    headers = build(names)
    if args[:1] == ["--merge"]:
        merge(args[1], headers)


if __name__ == "__main__":
    main()
