"""Build energy.renewablox.co.uk — the client packs as a static site.

The Generator Demo and Business Electricity packs are plain pages: no server
logic, no secrets. On Streamlit they are routes of one app (``?view=<key>``);
here each is a real address on RenewaBlox's own domain:

    /                                   welcome page (energy_welcome.html)
    /business/                          Business Electricity landing
    /business/site-analysis/            Tier 1 · Holistic Site Analysis
    /business/heat-as-a-service/        Tier 2 · Heat-as-a-Service
    /business/heat-network/             Tier 3 · Heat Network 3D
    /business/thanks/                   after the savings check, if it was sent without its script
    /generators/                        Generator Demo landing
    /generators/peaker-plant/           Peaker Plant model
    /generators/run-of-river-hydro/     Run-of-River Hydro model

Everything is read from the same files the Streamlit apps serve, through
packs.py, so both surfaces always show the same pages: the landing fragments
are wrapped in a document of their own, and each model page sits under the
same slim navigation bar the apps draw, in an iframe of the model with its
serve-time patches applied (``<slug>/model.html``) — exactly how Streamlit
frames it, so every model lays out as it does there.

One thing the Streamlit surface can't have is a working form, so the Business
landing's savings check is a link there; here the build puts the real form
(energy_save_form.html, received by Netlify Forms) in its marked place.

Run:  python build_energy_site.py        (writes energy_site/, git-ignored)
Netlify runs it on every push to main (netlify.toml).
Standard library only.
"""
import html
import json
import re
import shutil
from pathlib import Path

from packs import (BUSINESS_HOME, BUSINESS_SUBJECT, BUSINESS_VIEWS, CONTACT,
                   GENERATOR_HOME, GENERATOR_VIEWS, home_fragment, model_page)

HERE = Path(__file__).resolve().parent
OUT = HERE / "energy_site"
ASSETS = HERE / "energy_site_assets"
SITE_URL = "https://energy.renewablox.co.uk"

FAVICON = ('<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 '
           'viewBox=%220 0 16 16%22><circle cx=%228%22 cy=%228%22 r=%227%22 fill=%22%231F5F7F%22/></svg>">')

PACKS = {
    "business": {
        "home": BUSINESS_HOME,
        "views": BUSINESS_VIEWS,
        "title": "RenewaBlox × tem — Business Electricity",
        "description": ("tem works on the supply; RenewaBlox works on the demand. Explore how we can save "
                        "you money off your electricity bill, in three tiers."),
        "crumb": "Business Electricity",
        "back": "&larr; Overview",
        "cta": ("Send us a bill", f"mailto:{CONTACT}?subject={BUSINESS_SUBJECT}"),
        "og": "og-business.jpg",
        "form": "energy_save_form.html",
    },
    "generators": {
        "home": GENERATOR_HOME,
        "views": GENERATOR_VIEWS,
        "title": "RenewaBlox × tem — For Generators",
        "description": ("Through tem and P442, a better PPA for renewables of all types. Through RenewaBlox, "
                        "any excess monetised, with compute at the point of generation."),
        "crumb": None,
        "back": "&larr; All models",
        "cta": ("Talk to us", f"mailto:{CONTACT}?subject=Our%20generation%20site"),
        "og": "og-generators.jpg",
    },
}

BAR_H = 46

# The apps' pack bar, as a page of its own: the bar on top, the model framed below it.
FRAME_CSS = f"""
  html, body {{ margin:0; height:100%; background:#f4f8fa; overflow:hidden; }}
  .rbx-bar {{ position:fixed; inset:0 0 auto 0; height:{BAR_H}px; background:#0d1b23; display:flex; align-items:center;
      gap:14px; padding:0 14px; overflow-x:auto; scrollbar-width:none; -webkit-overflow-scrolling:touch; box-sizing:border-box;
      font-family:"Inter","Inter var",system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif; }}
  .rbx-bar::-webkit-scrollbar {{ display:none; }}
  .rbx-bar .crumb {{ font-size:12.5px; color:#93a2aa; white-space:nowrap; }}
  .rbx-bar nav {{ margin-left:auto; display:flex; gap:6px; align-items:center; }}
  .rbx-bar a {{ text-decoration:none; font-size:12.5px; padding:5px 13px; border-radius:999px; color:#b9c6cd;
      white-space:nowrap; transition:background .15s, color .15s; }}
  .rbx-bar a:hover {{ color:#fff; background:rgba(255,255,255,.09); }}
  .rbx-bar a:focus-visible {{ outline:2px solid #fff; outline-offset:2px; }}
  .rbx-bar a.active {{ color:#0d1b23; background:#fff; font-weight:600; }}
  .rbx-bar a .t {{ opacity:.6; margin-right:5px; font-weight:600; }}
  .rbx-bar a.back {{ color:#fff; font-weight:600; padding-left:2px; }}
  .rbx-bar a.talk {{ margin-left:8px; border:1px solid rgba(255,63,16,.7); color:#fff; font-weight:600; }}
  .rbx-bar a.talk:hover {{ background:#ff3f10; border-color:#ff3f10; color:#fff; }}
  .rbx-bar .lbl-s {{ display:none; }}
  iframe.rbx-model {{ position:fixed; top:{BAR_H}px; left:0; width:100%; height:calc(100% - {BAR_H}px); border:0; display:block; }}
  @media (max-width:900px) {{ .rbx-bar .crumb {{ display:none; }} }}
  @media (max-width:640px) {{ .rbx-bar .lbl-f {{ display:none; }} .rbx-bar .lbl-s {{ display:inline; }} }}
"""


def head(title, description, path, og_image, extra=""):
    url = SITE_URL + path
    t, d = html.escape(title), html.escape(description)
    return f"""<!DOCTYPE html>
<html lang="en-GB"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="RenewaBlox">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}/{og_image}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#12475e">
{FAVICON}
{extra}</head>"""


def landing(pack_key, pack):
    """A pack's landing fragment in a document of its own, its ?view= links made real addresses."""
    frag = home_fragment(pack["home"])
    slugs = {k: v["slug"] for k, v in pack["views"].items()}

    def to_path(m):
        key = m.group(1)
        if key not in slugs:
            raise SystemExit(f"{pack['home']}: link to unknown view ?view={key}")
        return f'href="/{pack_key}/{slugs[key]}/"'

    if pack.get("form"):
        # the fragment's stand-in for the form, between <!--save-form--> markers, makes way for the form
        form = (HERE / pack["form"]).read_text(encoding="utf-8")
        frag, n = re.subn(r"<!--save-form-->.*?<!--/save-form-->", lambda m: form, frag, flags=re.S)
        if n != 1:
            raise SystemExit(f"{pack['home']}: expected one <!--save-form--> block, found {n}")
    frag = re.sub(r'href="\?view=([a-z]+)"', to_path, frag)
    frag = frag.replace('href="?view=home"', f'href="/{pack_key}/"')
    if "?view=" in frag:
        raise SystemExit(f"{pack['home']}: a ?view= link the build does not understand")
    # the fragments paint Streamlit's own .stApp; here that is the page wrapper
    base = ("<style>html{scroll-behavior:smooth} html,body{margin:0} body{background:#f4f8fa}"
            ".stApp{min-height:100vh}</style>")
    return (head(pack["title"], pack["description"], f"/{pack_key}/", pack["og"], base)
            + f'\n<body><div class="stApp">\n{frag}\n</div></body></html>\n')


def frame_page(pack_key, pack, key):
    """A model page: the pack bar on top, the patched model framed below it."""
    view = pack["views"][key]
    links = []
    for k, v in pack["views"].items():
        active = ' class="active" aria-current="page"' if k == key else ""
        tier = f'<span class="t">{v["tier"][-1]}</span>' if "tier" in v else ""
        links.append(f'<a href="/{pack_key}/{v["slug"]}/"{active}><span class="lbl-f">{tier}{v["label"]}</span>'
                     f'<span class="lbl-s">{v["short"]}</span></a>')
    crumb_lead = pack["crumb"] or view.get("sector", "")
    crumb = " &middot; ".join(x for x in (crumb_lead, view.get("tier", ""), view["label"]) if x)
    cta_label, cta_href = pack["cta"]
    title = f'RenewaBlox — {view["tier"] + " · " if "tier" in view else ""}{view["label"]}'
    return (head(title, pack["description"], f'/{pack_key}/{view["slug"]}/', pack["og"],
                 f"<style>{FRAME_CSS}</style>\n")
            + f"""
<body>
<div class="rbx-bar">
  <a href="/{pack_key}/" class="back">{pack["back"]}</a>
  <div class="crumb">{crumb}</div>
  <nav>{"".join(links)}<a href="{cta_href}" class="talk">{cta_label}</a></nav>
</div>
<iframe class="rbx-model" src="model.html" title="{html.escape(view["label"])}" allow="fullscreen"></iframe>
</body></html>
""")


def welcome():
    """The welcome page, forwarding old Streamlit-style links (…/?view=<key>) to their pages.

    The two packs' view keys never collide, so a link that only had its domain
    swapped for this one still lands on the right model.
    """
    routes = {k: f"/{pk}/{v['slug']}/" for pk, pack in PACKS.items() for k, v in pack["views"].items()}
    if len(routes) != sum(len(p["views"]) for p in PACKS.values()):
        raise SystemExit("two packs share a view key; ?view= links would be ambiguous")
    forward = ("<script>(function(){var r=" + json.dumps(routes, separators=(",", ":"))
               + ',v=new URLSearchParams(location.search).get("view");if(v&&r[v])location.replace(r[v]);})();</script>')
    page = (HERE / "energy_welcome.html").read_text(encoding="utf-8")
    return page.replace("</head>", forward + "</head>", 1)


def thanks():
    """Where the savings check lands if it was posted without its script (it otherwise thanks in place)."""
    page = (ASSETS / "404.html").read_text(encoding="utf-8")
    body = re.search(r'<div class="card">.*</div>', page, re.S).group(0)
    card = ("""<div class="card">
  <div class="k">Free bill check</div>
  <h1>Thank you &mdash; it&rsquo;s with us.</h1>
  <p>We&rsquo;ll take a look and come back to you by email with what you could save.</p>
  <nav><a class="pri" href="/business/">Back to Business Electricity</a></nav>
</div>""")
    return (page.replace(body, card)
            .replace("<title>Page not found — RenewaBlox Energy</title>", "<title>Thank you — RenewaBlox Energy</title>"))


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    write(OUT / "index.html", welcome())
    write(OUT / "business" / "thanks" / "index.html", thanks())
    for pack_key, pack in PACKS.items():
        write(OUT / pack_key / "index.html", landing(pack_key, pack))
        for key, view in pack["views"].items():
            write(OUT / pack_key / view["slug"] / "index.html", frame_page(pack_key, pack, key))
            write(OUT / pack_key / view["slug"] / "model.html", model_page(view))
    for f in ASSETS.iterdir():
        shutil.copy(f, OUT / f.name)
    pages = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file())
    size = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"energy_site/: {len(pages)} files, {size / 1e6:.1f} MB")
    for p in pages:
        print("  ", p)


if __name__ == "__main__":
    main()
