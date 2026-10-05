# RenewaBlox — Public Atlas

Public-facing, self-contained site tools built by RenewaBlox. Each app is a thin
Streamlit wrapper around a standalone page — a Leaflet map, or a three.js scene —
with all data embedded and no database and no secrets. Because this repo is
public, the apps deploy as **public apps** on Streamlit Community Cloud
(unlimited, free).

## Apps

| App | Page(s) | What it shows |
| --- | --- | --- |
| `app_srv_atlas.py` | `srv_atlas.html` + `srv_atlas_3d_badge.html` + `srv_3d_sim.html` + `srv_siting_3d.html` | SRV Atlas — the client view of the Scrivelsby (Home Farm AD) scheme: where the compute load bank sits, how it connects, and the site around it, kept deliberately minimal (LN9 6JB). Two pulsing BLOX badges on the yard open the 3D Dispatch Sim (`?view=3d`) and the 3D Compute Kiosk (`?view=siting`, two siting schemes on one page: option A, one 4 m kiosk for the LV board, three DCX hydro racks and their cooling loop with the dry cooler on the roof; option B, the existing kiosk extended for the board and the Winchain 10 ft hydro cooling container behind it with the dry cooler on the container roof) full-screen — the same app serving each route, so the map page carries none of the models' weight |
| `app_srv_contractor.py` | `srv_contractor.html` | SRV Contractor Atlas — the same site surveyed for the LV connection RFQ: switchgear detail, the full 12-photo survey including switchroom interiors, the feeder route with its tie-in and containment notes, and OSM/DNO context |
| `app_kld_atlas.py` | `kld_atlas.html` + `kld_hydro_chrome.html` + `kld_interactive.html` | KLD Atlas — Kinlochdamph 999 kW run-of-river hydro (Loch Damh, Wester Ross): site assets, the 11/33/132 kV network and the two SSEN connection options. A pulsing BLOX badge on the powerhouse opens the 3D Revenue Sim full-screen — the same app serving `?view=3d`, so the atlas page carries none of the model's weight |
| `app_ihn_atlas.py` | `ihn_atlas.html` + `ihn_heat_chrome.html` + `heat_network_3d.html` | IHN Atlas — the IHN heat network: a still, daytime three.js satellite atlas of the district with the network main, the existing and proposed connections, the 11 kV route and the HNES blocks drawn on the imagery, and the 76 × 25 m plant room cut away under the block; four camera views (Overview, the Plant room as an amber call to action, EC1, EC2) with a caption that follows the view, a key, layers and a Council site-map overlay. A pulsing BLOX badge over the plant room opens the dispatch model, Heat Network 3D, full-screen — the same app serving `?view=3d` with the same model file the investor pack serves, all data included, so the atlas page carries none of the model's weight |
| `app_moray_atlas.py` | `moray_atlas.html` | Moray Cluster Atlas — the Keith & Huntly primaries (the only two green-headroom primaries in the Savills Moray screen): candidate plots, ownership areas, GSP saturation, the 33/132/275/400 kV network and the offshore wind landing on it |
| `app_srv_3d_sim.py` | `srv_3d_sim.html` | SRV 3D Sim — the Scrivelsby Peaker: a three.js model of the Home Farm AD site with a half-hourly dispatch simulation of the 350 kW switchable block over a real metered year, and the site survey photography on every asset pin |
| `app_investor_demo.py` | `investor_demo_home.html` + `peaker_plant_3d.html` + `kld_interactive.html` + `heat_network_3d.html` + `demand_for_constraints_3d.html` | Investor Demo — a landing page for prospective investors that packs the interactive 3D models: Peaker Plant 3D (the peaker business model as a living site, `?view=peaker`), Hydro 3D (the KLD powerhouse and its in-room data centre, `?view=hydro`), Heat Network 3D (the IHN heat network and the data centre that heats it, a year half-hour by half-hour, `?view=heat`) and Demand for Constraints 3D (the Moray cluster north of the B4 constraint and the two BLOX halls NESO dispatches to absorb curtailed wind, `?view=dfc`). **Investor data is gated:** on Hydro 3D, Heat Network 3D and Demand for Constraints 3D the panels that carry the figures are blurred and inert at serve time and a card points to the investor portal (`GATED` in the entry file — the model files are untouched, and the portal edition serves them unblurred) |
| `app_investor_portal.py` | `investor_portal_home.html` + the same four model files | Investor Portal — the Investor Demo duplicated at the URL the investor portal links to, so the portal keeps the full pack while the public demo is cut back; when `PORTAL_PASSCODE` is set in the app's Streamlit secrets (never in the repo) every view is locked: the portal's button carries the key in its link (`?k=<key>`, printed by `portal_key.py`) so investors clicking through from the logged-in portal never see a prompt, and a code prompt is the fallback for anyone sent the code by other means; whichever way in, the pack's own links carry the key on, so the model links never re-ask, and a cookie lets a later return to the bare URL skip the prompt too. The files themselves stay public in this repository whatever the gate says |
| `app_investor_demo_aus.py` | `investor_demo_aus_home.html` + `peaker_plant_3d.html` + `kld_interactive.html` + `nem_negative_price_atlas.html` | Investor Demo (Australia) — Peaker Plant 3D and Hydro 3D plus NEM 3D (mining economics across the Australian NEM, `?view=nem`), on its own URL for the investor group that model was built for |
| `app_peaker_3d.py` | `peaker_plant_3d.html` | Peaker Plant 3D standalone — the same peaker model on its own link, for client brochures (AD operators): no landing page, no pack navigation, straight into the model, prices in **p/kWh** |
| `app_peaker_demo.py` | `peaker_plant_3d.html` | Peaker Demo — the pack's Peaker Plant 3D on a link of its own, for sending the peaker without the rest of the pack: no landing page, no pack navigation, prices in **£/MWh**, and tailored for an energy-literate audience (strike opens at £80 on a £50–£100 range; the export price is named **DA + gDUoS**) |
| `app_generator_demo.py` | `generator_demo_home.html` + `peaker_plant_3d.html` + `kld_interactive.html` | Generator Demo — the client pack for generators RenewaBlox is reaching out to, with tem, on its own URL: a landing page that puts the two partners together (through tem and P442, a better PPA for renewables of all types; through RenewaBlox, any excess monetised by compute at the point of generation, drawn as an illustrative week of output split at the export limit), with a PPA check beside the headline (export MPAN and PPA end date, or a PPA statement), then sorts the models by the client's sector, each sector led by the same two steps (a better PPA through tem, then RenewaBlox), with the peaker under **Fuelled Renewables** as the **Peaker Plant model** (`?view=peaker`, prices in **p/kWh**) and the hydro under **Stranded Renewables** as the **Run-of-River Hydro model** (`?view=hydro`). Each model's header carries its client-pack name, the pack bar names the sector and offers a "Talk to us" email link, and nothing is gated — the investor-portal blur is for investors |
| `app_business_demo.py` | `business_demo_home.html` + `business_site_analysis.html` + `business_haas.html` + `heat_network_3d.html` | Business Electricity — RenewaBlox with tem, the client pack for businesses that buy electricity: a landing page that explains what's in a business bill and who works on which side of the meter (the animated BLOX wordmark marks RenewaBlox's side), sets out tem's supply (RED, priced against tem's UK renewable portfolio through its Rosso platform) and the RED Plus benefit (P442 exempt supply) as the foundation of every tier, then offers three tiers, each including RED and RED Plus and building on the one before: **Tier 1, Holistic Site Analysis** (`?view=site`, an interactive example report on an illustrative site built from tem's example quote — capacity, night-rate timing, power factor, levies and bands, with a running total), **Tier 2, Heat-as-a-Service** (`?view=haas`, an animated isometric site heated by Bitcoin miners through a large dry cooler or as space heaters) and **Tier 3, Heat Network** (`?view=heat`, Heat Network 3D, served with all of its data) |
| `outreach/app_outreach.py` | none — native Streamlit (`outreach/sections.py`, `outreach/toolkit.py`, `outreach/ui.py`) | Outreach Strategy — RenewaBlox × tem's business outreach strategy (working draft of 2 October 2026) as an app: seven pages under a sticky tab rail, each on its own address (`/`, `/offer`, `/linkedin`, `/strategies`, `/plan`, `/compliance`, `/toolkit`). Overview (the Bill X-ray hook, the five-channel map, the four plays, the first week's moves); Offer & targets (the edge, the claims and whose they are, the three limits, the segments and a **segment playbook** that gathers each segment's buyer, hook, LinkedIn angle, Demand Atlas source and opener on one card); LinkedIn (foundations to paid, with the funnel as a **live model**: its planning rates are sliders, and the paid stop rule follows them); Three strategies (Demand Atlas, Local Power with a generator **sizing calculator**, Borrowed trust); The plan (the 14 weeks on a chart with a **today line and live status** from the viewer's date, `?date=YYYY-MM-DD` to preview another day, and the tasks **filtered by owner**); Compliance (the two decisions, the checklist, the sources and how each was checked); Toolkit (every template and crew prompt, with the common fields **filled once** for all of them, length checks against the strategy's limits, search and a copy button on each) |

The two investor demos are separate apps on purpose: NEM 3D was built for one
group of Australian investors, so it appears only in the pack they are sent to.
The Australia pack carries Peaker, Hydro and NEM 3D; Heat Network 3D and
Demand for Constraints 3D joined the main pack first and are not in the Australia pack yet. They share this repo, the model copies and the landing-page
design; each has its own entry file and its own landing fragment. A stale
`?view=nem` link against the main pack falls back to its landing page rather
than erroring.

Five surfaces serve the same `peaker_plant_3d.html`, and they differ only in
framing — audience decides which link goes out:

| Surface | Chrome | Prices | Strike | Export price reads |
| --- | --- | --- | --- | --- |
| the two packs, `?view=peaker` | landing page + pack bar | £/MWh | £100, £40–£160 | "Price of electricity" |
| `app_peaker_demo.py` | none | £/MWh | £80, £50–£100 | "Export · DA + gDUoS" |
| `app_peaker_3d.py` | none | p/kWh (AD operators) | £100, £40–£160 | "Price of electricity" |
| `app_generator_demo.py`, `?view=peaker` | landing page + pack bar | p/kWh (generators) | £100, £40–£160 | "Price of electricity" |

Standing the peaker up on its own did not take it out of the packs: both still
carry their Peaker card, so `?view=peaker` links already sent out keep working.

Those per-surface differences are declared by the serving app and applied by the
model at load — `window.PEAKER_UNITS` for p/kWh, `window.PEAKER_CFG` for the
strike range and the export-price labels — so the HTML never forks. Both
default to the packs' behaviour when a surface declares neither. Tailor a
surface by editing its entry file, never by editing `peaker_plant_3d.html`.

The outreach strategy is the exception to the wrapped-page pattern: it is
native Streamlit (custom HTML blocks through `st.html`, with Streamlit widgets
for the parts the reader drives), so its funnel, sizing and plan status can
respond. It lives in `outreach/` because its theme does: Streamlit reads a
`.streamlit/config.toml` beside the entry script after the project one, so
`outreach/.streamlit/config.toml` (petrol and tem palette, Inter and IBM Plex
Mono, light and dark variants that follow the viewer's system) styles that
app alone and leaves every app at the root on Streamlit's default theme. Its
`outreach/requirements.txt` asks for Streamlit 1.65 or later. Two things to
know before editing it: `st.html` strips inline `<svg>` (the diagrams are HTML
and CSS), and its sanitiser drops a whole `<style>` block that contains a
`<` anywhere, so any SVG data URI in the stylesheet must be URL-encoded.

Each app reads its HTML inline and renders it with `st.iframe`, so a redeploy
always serves the current map. The one exception is the investor demos' landing
pages: HTML fragments rendered in the parent page with `st.markdown`, because
Streamlit sandboxes component iframes without `allow-top-navigation`, so links
inside one can never drive the app's `?view=` navigation.

## Generated files

`kld_atlas.html`, `moray_atlas.html`, `srv_3d_sim.html`, `srv_siting_3d.html`,
`srv_atlas_3d_badge.html`, `heat_network_3d.html`, `demand_for_constraints_3d.html` and `ihn_atlas.html` are built, not hand-edited. Each builder re-skins its
hand-authored source in the shared RenewaBlox design system (petrol brand
tokens, Inter, brand bar — and glass panels where the build re-skins the panels) and re-uses the source's data and
vendored payloads byte-for-byte:

| Output | Builder |
| --- | --- |
| `kld_atlas.html` + `kld_hydro_chrome.html` | `Contracts/Kinlochdamph/Atlas/build_kld_atlas.py` |
| `moray_atlas.html` | `Contracts/Savills Earth/Atlas/build_moray_atlas.py` |
| `srv_3d_sim.html` | `Contracts/Scrivelsby Farm Ltd/Atlas/build_srv_3d_sim.py` |
| `srv_siting_3d.html` | `Contracts/Scrivelsby Farm Ltd/Atlas/siting/build_siting.py` (three.js viewer bundled with esbuild; the schemes live in `siting/src/scheme.js` (option A) and `siting/src/scheme_b.js` (option B)) |
| `srv_atlas_3d_badge.html` | `Contracts/Scrivelsby Farm Ltd/Atlas/build_srv_atlas_badge.py` |
| `heat_network_3d.html` | `Contracts/<IHN client>/Atlas/build_heat_network_3d.py` — from the client edition of the IHN heat-network model, with the site anonymised to IHN: the brand bar, house type and chips go on, the Google Fonts links come off, and the scene, panels, data and payloads pass through byte-for-byte |
| `ihn_atlas.html` | `Contracts/<IHN client>/Atlas/build_ihn_atlas.py` — from the in-house IHN Atlas 3D scene (`IHN_Atlas_3D_1.html`): the house bar, light glass panels and white callouts go on, the live-dispatch inset, the dispatch desk, the settlement clock and the sky switcher come off (the dispatch series with them, so the page is lighter than its source), the sky is fixed at day, and the scene, its data, the imagery and the vendored three.js pass through byte-for-byte. The scene script is minified, so every cut is an exact-string splice that must match once or the build fails; the build also fails if the source's link to the investor portal, or its access key, survives |
| `demand_for_constraints_3d.html` | `Data Room/Inhouse IP/Atlas 3D/DfC/build_dfc_3d.py` — from edition 4 of the in-house DfC model (`make_edition_4.py` derives it from edition 3: Heat Network pacing, a full-year opening run with three highlight days, state-keyed weather, and the wholesale projection's continental coupling with a consistent price stack and RO roll-off, all editable in the assumptions drawer): the brand bar, house type and chips go on, the footer row comes off, the layout is tidied for a laptop screen, and the scene, model, data and payloads pass through byte-for-byte |

`srv_atlas_3d_badge.html` is the 3D-sim gateway for the client atlas: the BLOX
badge, the popup call-to-action rows and the overlay. `app_srv_atlas.py`
appends it to `srv_atlas.html` at serve time, so the hand-maintained map file
stays pristine and the sim loads through `?view=3d` only when opened.

The investor demos' model pages are copies of their upstream sources — refresh
them after an upstream rebuild:

| Copy in this repo | Used by | Source of truth |
| --- | --- | --- |
| `peaker_plant_3d.html` | both packs + generator pack + `app_peaker_3d.py` + `app_peaker_demo.py` | internal Atlas 3D build (`peaker_plant_3d_2.html`) |
| `kld_interactive.html` | both packs + generator pack + KLD Atlas | `Contracts/Kinlochdamph/Atlas/kld_live_3.html` |
| `nem_negative_price_atlas.html` | Australia pack | internal Atlas 3D build (`nem_negative_price_atlas_2.html`) |

Both packs and the standalone peaker serve their model pages with small
presentation-only CSS patches (`PATCH_CSS` in the packs, inline in
`app_peaker_3d.py`) — the peaker's guided-tour view strip is hidden in all
three — so the files themselves stay byte-for-byte copies of upstream. The
generator pack goes one step further and renames each model in its own header
(`title` in `MODELS` in `app_generator_demo.py`, an exact-string swap of the
`<h1>`): if an upstream rebuild changes that heading the swap simply misses and
the model keeps its own title, so check the pack after refreshing a copy.
`app_kld_atlas.py` does the same for `kld_interactive.html`, appending
`kld_hydro_chrome.html` (design-system overrides plus the "Atlas" control back
to the map). **Never edit `kld_interactive.html` to add atlas-specific chrome** —
it is served by four apps, and a "back to the KLD Atlas" button baked into it
would appear, pointing at the wrong place, in both investor packs and the
generator pack.

## The site-atlas pattern

`app_srv_atlas.py`, `app_kld_atlas.py` and `app_ihn_atlas.py` are deliberately
the same shape, so a new site can be stood up by copying any of them:

* one app, two views — the atlas by default (a Leaflet map for SRV and KLD, a
  still three.js satellite scene for IHN), its 3D model at `?view=3d`, both
  rendered full-bleed through the same Streamlit chrome-stripping CSS;
* the model is a route, never an in-page overlay, so the map page stays small
  (KLD is 0.31 MB) and the model gets the whole window;
* the same gateway on the map: a pulsing BLOX chip with a gradient
  call-to-action pill and a matching CTA row inside the relevant popups —
  and a map can carry more than one (SRV has two: the dispatch sim and the
  compute kiosk, each its own `?view=` route);
* the same way back: an "Atlas" pill as the first item in the model's header;
* one shared token set (`--brand:#12475e`, `--accent:#1f5f7f`, Inter, the
  `--sh-1`/`--sh-2` elevations, `--r-s`/`--r-m`/`--r-l`/`--r-pill` radii) across
  every page, defined in each build's stylesheet.

Where they genuinely differ: SRV's client build shows a top brand bar and no
side panel, KLD shows a briefing panel whose header carries the wordmark and no
top bar — giving KLD both would print the wordmark twice. SRV also stands its
CTA pill at full length because it opens over a single yard, whereas KLD opens
on 20 km of 33 kV spur and shows the short form until zoom 13.5. IHN's badge is
tracked to the plant room in the 3D scene (and docks above the caveat when the
camera is down in the plant room), and its header carries the same house bar
as the Heat Network 3D page it opens, so the two read as one product.

One consequence of Streamlit's component sandbox for all three: the gateway and
the model's "Atlas" pill try to navigate the page they sit in and, when the
sandbox refuses, open the destination in a new tab instead — so on Streamlit
Cloud the model opens in a new tab and the Atlas pill opens the atlas in
another. Served outside Streamlit (a plain static host) they navigate in place.

`heat_network_3d.html` is now served by four apps (the investor demo and portal,
the IHN Atlas and the business pack): **never bake atlas chrome into it** — the IHN "Atlas" pill lives in
`ihn_heat_chrome.html` and is appended at serve time, exactly as
`kld_hydro_chrome.html` is for `kld_interactive.html`.

`investor_demo_home.html`, `investor_demo_aus_home.html`,
`generator_demo_home.html` and `business_demo_home.html` are hand-authored
(wordmark and scene thumbnails inlined as data URIs) — edit them directly. Each
is a fragment (`<style>` + one `<div>`, no `<html>`/`<body>`, no scripts, every
class prefixed `rbx-`); the app strips blank lines before handing it to
`st.markdown`, and any new link in it needs an explicit `target="_self"` or
Streamlit will retarget it to a new tab. The main landing page groups its
models into delivery windows (2026/27: Peaker and Hydro; 2027 & beyond: Heat
Network plus a slot for the next model, whose delivery may run to 2029/30) with
CSS-only tabs — radio inputs and
`:checked` selectors, since scripts never run inside `st.markdown`. The first
window is the CSS default rather than a `checked` attribute: Streamlit's React
tree treats a `checked` radio as controlled and snaps it back after a click.
The Australia fragment still has the earlier single-grid design with NEM 3D as
its third card; the tabbed design has not been ported to it yet, pending a
decision on which window NEM 3D belongs to. The generator fragment is its own
design for a client audience: a dark hero with a "Which describes your site?"
picker, one feature section per sector (Fuelled Renewables, Stranded
Renewables), a three-step "How we work with generators" strip and an email
call to action. Its two scene frames are declared once each, as backgrounds on
the `.rbx-img-peaker` / `.rbx-img-hydro` classes, and shared by the picker and
the sector cards, so neither image is inlined twice.

Card thumbnails are frames taken from the models themselves, so they go stale
when a model is rebuilt. The three.js scenes render with `preserveDrawingBuffer`
and expose `window.__atlas`, so a frame is: hide the pins (`#labels`), point the
camera (`__atlas.view('hall')`), size the canvas 2:1
(`__atlas.renderer.setSize(2400, 1200, false)` with `cam.aspect = 2`), render,
then `__atlas.shoot()` for a PNG data URL. Downscale to 1200×600 and inline it
as WebP (~40 kB at quality 78 matches the other cards). Heat Network 3D has no
`__atlas` hook: its card is a plain 2:1 crop of a `#stage` screenshot taken in
Phase 2, when the thermal stores are lit. The generator page's frames are 3:2
(1320×880, WebP quality 76): the peaker from `pos [24,15,44]`, `tgt [-1,2,-8]`,
the hydro from `__atlas.view('hall')`, both with the pins off
(`__atlas.state.labels` false) and shot once the intro fly-in has settled.

The business pack's two tier pages, `business_site_analysis.html` (Tier 1) and
`business_haas.html` (Tier 2), are hand-authored full pages served in the
pack's iframe, where their scripts run: the site analysis draws its charts and
running total in SVG, and the Heat-as-a-Service scene is an isometric SVG
drawn by a small projector in the page (`P(x, y, z)` to screen, a `box()` of
three faces, painted back to front), with the two layouts as groups that fade
in and out. The site analysis takes its usage, unit rates, RED Plus benefit and
£2.39/kVA/month capacity rate from tem's example quote (RED Plus customer
guide, May 2026); the site's capacity, peaks and power factor are invented and
say so. The HaaS figures are physics only — no prices — and its 95% heat
recovery for layout A is the heat-network demonstrator's ratio (250 kWe in,
237 kWth out). The landing cards' frames are shots of these pages (Tier 1 a
composite of its capacity chart and running total) and the investor pack's
Heat Network 3D frame, so re-shoot them after a page changes. The BLOX
wordmark on the landing page is the 10-second brand animation, keyed off its
background, held at a steady size (the source eases out of a 5% zoom), cleaned
of video grain and looped as a 12 fps animated WebP on white (about 140 kB);
visitors with reduced motion turned on get a still of the resting logo.

The SRV builder also lifts the 12 survey photographs out of
`srv_contractor.html`, re-encodes them to WebP and wires them onto the 3D
scene's asset pins, so the 3D sim and the survey can never disagree about the
site record — rebuild it after any change to the contractor atlas's photos or
captions. It needs Pillow.

It reads the **contractor** atlas deliberately: `srv_atlas.html` is the
minimalist client build and carries only a few exterior shots, so pointing the
builder at it would quietly strip the 3D sim's photography.

## energy.renewablox.co.uk — the client packs on RenewaBlox's own domain

The Generator Demo and Business Electricity packs are plain pages, with no
server logic and no secrets, so they are also published as a static site at
**energy.renewablox.co.uk**. Streamlit Community Cloud only serves
`*.streamlit.app`, and a client email reads better, and sits better with spam
filters, when its links are on the sending domain. The Streamlit apps stay up,
so links already sent keep working.

| Address | Page |
| --- | --- |
| `/` | welcome page: which side of the meter are you on? One island, two routes, two doors (`energy_welcome.html`) |
| `/business/` | Business Electricity landing |
| `/business/site-analysis/`, `/business/heat-as-a-service/`, `/business/heat-network/` | the three tiers |
| `/business/thanks/` | after the savings check, if it was sent without its script |
| `/generators/` | Generator Demo landing |
| `/generators/peaker-plant/`, `/generators/run-of-river-hydro/` | the two models |
| `/generators/thanks/` | after the PPA check, if it was sent without its script |

`build_energy_site.py` writes it to `energy_site/` (git-ignored); Netlify runs
it on every push to main (`netlify.toml`, project `renewablox-energy`), so the
site and the apps change together. Both read the packs through **`packs.py`**:
each view's file, labels and serve-time patches (the model renames and the
peaker's p/kWh) are defined there once. Add or rename a view in `packs.py`, not
in an app. The build wraps each landing fragment in a document of its own,
turns every `?view=<key>` link into a real address (and fails if a fragment
links to a view it doesn't know), and puts each model under the same pack bar
the apps draw, in an iframe of the patched model at `<slug>/model.html`, exactly
as Streamlit frames it. An old Streamlit-style link with only its domain swapped
(`energy.renewablox.co.uk/?view=site`) is forwarded from the welcome page to its
page: the two packs' view keys never collide, and the build checks that they don't.
`energy_site_assets/` holds the 404 page and the 1200×630 share-preview images
(`og-*.jpg`, frames of each landing page's headline): re-shoot them if a
headline changes.

**The welcome page** (`energy_welcome.html`) is one island with the meter line
down the middle: generators (AD, wind, solar) on the supply side, businesses on
the demand side, tem's marketplace on the line between them, and the usual
route (the wholesale market, a row of market middlemen and a levy gate) along
the back. It is a Blender build exported to GLB and drawn with three.js, with
the GLB, three.js, the wordmark and a poster frame all inlined, so the file is
about 1.6 MB and makes no requests; where WebGL is unavailable the poster frame
stands in. A first visit sees **the usual route first**: the power drawn stop
by stop from the generators through the wholesale market, the market middlemen
and the levy gate, each label lit as it is reached, then out to the businesses;
then the page switches to **RenewaBlox × tem** and stays there, and the scene
plays its own introduction (the BLOX links, the site scan, each generator's
pairings). That opening is the readable script at the end of the file, driving
the scene through `window.rbxScene`; the bundled scene script is minified (its
source isn't in this repo) and carries five one-line hooks for it, each marked
`rbx-opening`. A click on either route button or on pause ends the opening,
and reduced motion or no WebGL skips it. The two doors flank the island on
wide screens (304 px, 356 px from 1720 px) and sit under it below 1360 px; each
carries its pack's CTA and a link to its check.

**The savings check and the PPA check.** Beside each landing's headline, a
card asks for an MPAN and an end date, or a document, plus the client's email:
on Business, the MPAN and contract end date or a recent bill (the savings
check); on Generators, the export MPAN and PPA end date or a recent PPA
statement or self-billing invoice (the PPA check, "Find out your PPA uplift
now"). The document can be dropped on the card, chosen as a file, or
photographed on a phone (PDF or image, up to 8 MB). On the energy site each is
a working form built from one template, `energy_save_form.html`, in its pack's
wording (`FORMS` in `build_energy_site.py`), which the build puts in place of
the fragment's `<!--save-form-->` stand-in (Streamlit can't run a form, so the
apps' cards link to these and offer email instead). **Netlify Forms** receives
them as two forms, `bill-check` and `ppa-check`: each is found in the built page
at every deploy (Forms must be enabled on the project), each submission is kept
with its document under the project's **Forms** tab, and email notifications
send them to **energy@renewablox.co.uk** (Project configuration → Notifications
→ Emails and webhooks → Form submission notifications; one per form, or one for
any form). The script checks the MPAN's check digit before sending, posts in the
background and thanks the client in the card; without the script it posts as a
plain form and lands on `/business/thanks/` or `/generators/thanks/`. A honeypot
field turns away most bots.

Domain: `renewablox.co.uk`'s DNS is at Wix. The subdomain is a CNAME record
`energy` → `renewablox-energy.netlify.app` there, with `energy.renewablox.co.uk`
added as the project's domain in Netlify, which issues the HTTPS certificate.
The apex and `www` records keep redirecting `.co.uk` to `.com`. Netlify's
visitor access controls ask for a team login on preview deploys only; the
production site is public.

Build and look at it locally:

    python build_energy_site.py
    python -m http.server 8800 -d energy_site     # then open http://localhost:8800/

## Run locally

    pip install -r requirements.txt
    streamlit run app_srv_atlas.py
    streamlit run app_srv_contractor.py
    streamlit run app_kld_atlas.py
    streamlit run app_ihn_atlas.py
    streamlit run app_moray_atlas.py
    streamlit run app_srv_3d_sim.py
    streamlit run app_investor_demo.py
    streamlit run app_peaker_3d.py
    streamlit run app_peaker_demo.py
    streamlit run app_investor_demo_aus.py
    streamlit run app_investor_portal.py
    streamlit run app_generator_demo.py
    streamlit run app_business_demo.py
    streamlit run outreach/app_outreach.py

## Deploy

Deploy on Streamlit Community Cloud pointing at the app's `app_*.py` entry file.
This repo is public, so apps deploy as public apps — unlimited and free. One app
per entry file, each with its own custom subdomain:

| Entry file | URL |
| --- | --- |
| `app_investor_demo.py` | `investor-demo.streamlit.app` |
| `app_investor_demo_aus.py` | `investor-demo-aus.streamlit.app` |
| `app_peaker_3d.py` | `peakerplant-3d.streamlit.app` |
| `app_investor_portal.py` | `investor-insight.streamlit.app` — linked from the members-only area of the Wix investor portal |
| `app_ihn_atlas.py` | `ihn-atlas.streamlit.app` — the client-facing IHN Atlas, with Heat Network 3D at `?view=3d` |

`app_peaker_demo.py` is ready to deploy and has no subdomain yet — add its row
above once one is claimed. So is `app_generator_demo.py`, the generator pack;
`generator-demo.streamlit.app` matches the investor pack's naming. Once it is
live, add its row above and its URL to `APPS` in
`.github/scripts/keep_awake.py` (and to the alert's app list in the workflow).
The same goes for `app_business_demo.py`, the business pack
(`business-demo.streamlit.app` would match).
And for `outreach/app_outreach.py`, the outreach strategy: set the main file path
to `outreach/app_outreach.py` (`renewablox-outreach.streamlit.app` would suit).
The IHN Atlas serves Heat Network 3D with all of its data at `?view=3d`, so its
link is for the client, not the public demo's footing. All five deployed apps are visited hourly by the keep-awake workflow
(`.github/workflows/keep-awake.yml`). For the portal app, set
`PORTAL_PASSCODE` in the app's secrets on Streamlit Cloud to lock it (the code
never lives in this repo; `.streamlit/secrets.toml` is git-ignored), then run
`python portal_key.py <code>` and put the printed `?k=…` on the end of the app's
URL behind the portal's button (a button that opens the app in a new tab is the
best home for a full-screen 3D scene; the pack also works inside a Wix "Embed a
site" element with `?embed=true&k=…`, because its own links carry the key on and
do not depend on the cookie). Rotate the code to expire every old link.
