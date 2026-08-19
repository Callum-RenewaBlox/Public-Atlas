# RenewaBlox — Public Atlas

Public-facing, self-contained site tools built by RenewaBlox. Each app is a thin
Streamlit wrapper around a standalone page — a Leaflet map, or a three.js scene —
with all data embedded and no database and no secrets. Because this repo is
public, the apps deploy as **public apps** on Streamlit Community Cloud
(unlimited, free).

## Apps

| App | Page(s) | What it shows |
| --- | --- | --- |
| `app_srv_atlas.py` | `srv_atlas.html` + `srv_atlas_3d_badge.html` + `srv_3d_sim.html` | SRV Atlas — the client view of the Scrivelsby (Home Farm AD) scheme: where the compute load bank sits, how it connects, and the site around it, kept deliberately minimal (LN9 6JB). A pulsing BLOX badge on the yard opens the SRV 3D Sim in a full-screen overlay — the same app serving `?view=3d`, so the atlas page carries none of the sim's weight |
| `app_srv_contractor.py` | `srv_contractor.html` | SRV Contractor Atlas — the same site surveyed for the LV connection RFQ: switchgear detail, the full 12-photo survey including switchroom interiors, the feeder route with its tie-in and containment notes, and OSM/DNO context |
| `app_kld_atlas.py` | `kld_atlas.html` + `kld_hydro_chrome.html` + `kld_interactive.html` | KLD Atlas — Kinlochdamph 999 kW run-of-river hydro (Loch Damh, Wester Ross): site assets, the 11/33/132 kV network and the two SSEN connection options. A pulsing BLOX badge on the powerhouse opens the 3D Revenue Sim full-screen — the same app serving `?view=3d`, so the atlas page carries none of the model's weight |
| `app_moray_atlas.py` | `moray_atlas.html` | Moray Cluster Atlas — the Keith & Huntly primaries (the only two green-headroom primaries in the Savills Moray screen): candidate plots, ownership areas, GSP saturation, the 33/132/275/400 kV network and the offshore wind landing on it |
| `app_srv_3d_sim.py` | `srv_3d_sim.html` | SRV 3D Sim — the Scrivelsby Peaker: a three.js model of the Home Farm AD site with a half-hourly dispatch simulation of the 350 kW switchable block over a real metered year, and the site survey photography on every asset pin |
| `app_investor_demo.py` | `investor_demo_home.html` + `peaker_plant_3d.html` + `kld_interactive.html` | Investor Demo — a landing page for prospective investors that packs the interactive 3D models: Peaker Plant 3D (the peaker business model as a living site, `?view=peaker`) and Hydro 3D (the KLD powerhouse and its in-room data centre, `?view=hydro`) |
| `app_investor_demo_aus.py` | `investor_demo_aus_home.html` + `peaker_plant_3d.html` + `kld_interactive.html` + `nem_negative_price_atlas.html` | Investor Demo (Australia) — the same pack plus NEM 3D (mining economics across the Australian NEM, `?view=nem`), on its own URL for the investor group that model was built for |
| `app_peaker_3d.py` | `peaker_plant_3d.html` | Peaker Plant 3D standalone — the same peaker model on its own link, for client brochures (AD operators): no landing page, no pack navigation, straight into the model |

The two investor demos are separate apps on purpose: NEM 3D was built for one
group of Australian investors, so it appears only in the pack they are sent to.
The Australia pack is a superset — the same two models plus NEM 3D — not a
different demo. They share this repo, the model copies and the landing-page
design; each has its own entry file and its own landing fragment. A stale
`?view=nem` link against the main pack falls back to its landing page rather
than erroring.

Each app reads its HTML inline and renders it with `st.iframe`, so a redeploy
always serves the current map. The one exception is the investor demos' landing
pages: HTML fragments rendered in the parent page with `st.markdown`, because
Streamlit sandboxes component iframes without `allow-top-navigation`, so links
inside one can never drive the app's `?view=` navigation.

## Generated files

`kld_atlas.html`, `moray_atlas.html`, `srv_3d_sim.html` and
`srv_atlas_3d_badge.html` are built, not hand-edited. Each builder re-skins its
hand-authored source in the shared RenewaBlox design system (petrol brand
tokens, Inter, glass panels, brand bar) and re-uses the source's data and
vendored payloads byte-for-byte:

| Output | Builder |
| --- | --- |
| `kld_atlas.html` + `kld_hydro_chrome.html` | `Contracts/Kinlochdamph/Atlas/build_kld_atlas.py` |
| `moray_atlas.html` | `Contracts/Savills Earth/Atlas/build_moray_atlas.py` |
| `srv_3d_sim.html` | `Contracts/Scrivelsby Farm Ltd/Atlas/build_srv_3d_sim.py` |
| `srv_atlas_3d_badge.html` | `Contracts/Scrivelsby Farm Ltd/Atlas/build_srv_atlas_badge.py` |

`srv_atlas_3d_badge.html` is the 3D-sim gateway for the client atlas: the BLOX
badge, the popup call-to-action rows and the overlay. `app_srv_atlas.py`
appends it to `srv_atlas.html` at serve time, so the hand-maintained map file
stays pristine and the sim loads through `?view=3d` only when opened.

The investor demos' model pages are copies of their upstream sources — refresh
them after an upstream rebuild:

| Copy in this repo | Used by | Source of truth |
| --- | --- | --- |
| `peaker_plant_3d.html` | both packs + `app_peaker_3d.py` | internal Atlas 3D build (`peaker_plant_3d_2.html`) |
| `kld_interactive.html` | both packs + KLD Atlas | `Contracts/Kinlochdamph/Atlas/kld_live_3.html` |
| `nem_negative_price_atlas.html` | Australia pack | internal Atlas 3D build (`nem_negative_price_atlas_2.html`) |

Both packs and the standalone peaker serve their model pages with small
presentation-only CSS patches (`PATCH_CSS` in the packs, inline in
`app_peaker_3d.py`) — the peaker's guided-tour view strip is hidden in all
three — so the files themselves stay byte-for-byte copies of upstream.
`app_kld_atlas.py` does the same for `kld_interactive.html`, appending
`kld_hydro_chrome.html` (design-system overrides plus the "Atlas" control back
to the map). **Never edit `kld_interactive.html` to add atlas-specific chrome** —
it is served by three apps, and a "back to the KLD Atlas" button baked into it
would appear, pointing at the wrong place, in both investor packs.

## The site-atlas pattern

`app_srv_atlas.py` and `app_kld_atlas.py` are deliberately the same shape, so a
new site can be stood up by copying either:

* one app, two views — the Leaflet map by default, its 3D model at `?view=3d`,
  both rendered full-bleed through the same Streamlit chrome-stripping CSS;
* the model is a route, never an in-page overlay, so the map page stays small
  (KLD is 0.31 MB) and the model gets the whole window;
* the same gateway on the map: a pulsing BLOX chip with a gradient
  call-to-action pill and a matching CTA row inside the relevant popups;
* the same way back: an "Atlas" pill as the first item in the model's header;
* one shared token set (`--brand:#12475e`, `--accent:#1f5f7f`, Inter, the
  `--sh-1`/`--sh-2` elevations, `--r-s`/`--r-m`/`--r-l`/`--r-pill` radii) across
  every page, defined in each build's stylesheet.

Where the two genuinely differ: SRV's client build shows a top brand bar and no
side panel, KLD shows a briefing panel whose header carries the wordmark and no
top bar — giving KLD both would print the wordmark twice. SRV also stands its
CTA pill at full length because it opens over a single yard, whereas KLD opens
on 20 km of 33 kV spur and shows the short form until zoom 13.5.

`investor_demo_home.html` and `investor_demo_aus_home.html` are hand-authored
(wordmark and scene thumbnails inlined as data URIs) — edit them directly. Each
is a fragment (`<style>` + one `<div>`, no `<html>`/`<body>`, no scripts, every
class prefixed `rbx-`); the app strips blank lines before handing it to
`st.markdown`, and any new link in it needs an explicit `target="_self"` or
Streamlit will retarget it to a new tab. The two fragments are the same page —
the Australia one carries a third card and says so in its kicker — so a design
change to one wants porting to the other.

Card thumbnails are frames taken from the models themselves, so they go stale
when a model is rebuilt. The three.js scenes render with `preserveDrawingBuffer`
and expose `window.__atlas`, so a frame is: hide the pins (`#labels`), point the
camera (`__atlas.view('hall')`), size the canvas 2:1
(`__atlas.renderer.setSize(2400, 1200, false)` with `cam.aspect = 2`), render,
then `__atlas.shoot()` for a PNG data URL. Downscale to 1200×600 and inline it
as WebP (~40 kB at quality 78 matches the other cards).

The SRV builder also lifts the 12 survey photographs out of
`srv_contractor.html`, re-encodes them to WebP and wires them onto the 3D
scene's asset pins, so the 3D sim and the survey can never disagree about the
site record — rebuild it after any change to the contractor atlas's photos or
captions. It needs Pillow.

It reads the **contractor** atlas deliberately: `srv_atlas.html` is the
minimalist client build and carries only a few exterior shots, so pointing the
builder at it would quietly strip the 3D sim's photography.

## Run locally

    pip install -r requirements.txt
    streamlit run app_srv_atlas.py
    streamlit run app_srv_contractor.py
    streamlit run app_kld_atlas.py
    streamlit run app_moray_atlas.py
    streamlit run app_srv_3d_sim.py
    streamlit run app_investor_demo.py
    streamlit run app_peaker_3d.py
    streamlit run app_investor_demo_aus.py

## Deploy

Deploy on Streamlit Community Cloud pointing at the app's `app_*.py` entry file.
This repo is public, so apps deploy as public apps — unlimited and free. One app
per entry file, each with its own custom subdomain:

| Entry file | URL |
| --- | --- |
| `app_investor_demo.py` | `investor-demo.streamlit.app` |
| `app_investor_demo_aus.py` | `investor-demo-aus.streamlit.app` |
