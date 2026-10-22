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
| `app_bryn_atlas.py` | `bryn_atlas.html` + `bryn_atlas_3d_badge.html` + `bryn_3d_sim.html` + `bryn_compute_3d.html` | Bryn Atlas — the client view of the Bryn Power AD plant scheme (Gelliargwellt Farm, Gelligaer CF82 8FY): where a BLOX data centre would stand, on the yard a few metres from the LV room at the CHP engines, to take about 200 kW of the site's surplus power by a short connection with no cable route across the site, kept deliberately minimal. A pulsing BLOX badge on the proposed plot opens the 3D Site Model full-screen (`?view=3d`): a three.js model of the plant, built in Blender from aerial imagery, with the data centre in place, in four tabs in the header. It opens on **Site**, the model alone. **Dispatch** plays the site's power half hour by half hour on a representative day per season (weekday or weekend, average or sunny; site load 125 kW on weekdays and 25 kW less at weekends and on bank holidays), Today against With BLOX: a live readout, the dispatch desk (two chart lanes: potential generation, and export against the 1.8 MW limit), Bryn's extra export as a single assumption (350,400 kWh a year at 16p/kWh, £56,064 a year, the figure Finance uses), and the seasons side by side in a fold that opens on demand; the data centre is 24 miners, 172.8 kW of compute installed, drawing at most 200 kW overclocked with its pumps, dry cooler and controls (their own load, about 5–8 kW, comes out of the 200 kW); with BLOX load following, export is held at 1,715 kW (85 kW headroom) against 1,675 kW today and the data centre takes the rest up to its 200 kW, and that target and the engines' warm-weather easing are set so a typical year matches the Finance tab (350,400 kWh of extra export, and 1,548,857 kWh into the data centre in a typical year: less 5% for outages, the 84% site capacity factor the revenue-share model uses); the scene follows the clock (the sun, the data centre rising out of its slab, its fans and the solar roofs' glow). **Finance** is the walk-through of the three ways of funding it (RenewaBlox funds it, 50:50 CAPEX share, Bryn funds it), from the revenue-share model for the final deployment (*Bryn Recycling 172.8kW final*, 19 October 2026: 172.8 kW, 24 miners, RenewaBlox's option recovering its CAPEX over 24 months; the options are scaled to the model's site-level outputs, £593,693 over the contract and a 17.6-month project payback) with Bryn's extra export added to Bryn's side: the panel is led by the 50:50 CAPEX share, opening on it in every size and keeping a soft amber mark on it when another option is chosen, and starts as a pill quoting it (Bryn receives £577,166), with the engine strip along the bottom; the strip maximises into a big-figure view led by the installation's 5-year total contract value; the pill opens a card of the three options, the chosen one showing what Bryn receives, its payback and a sparkline (and from then the split callout rides on the unit), and "Cash flow, year by year" widens it for the discussion: the options as chips with each one's outlay, total and payback, the answer in one line ("Bryn receives £755,274 over 5 years · paid back in 14.4 months"), one sentence on how the option works, what Bryn puts in against what it receives as two bars, and each side's cash in hand year by year on one fixed scale, with the installation and every model figure behind one disclosure; the engine strip stays under the wide panel when both fit. **Export only – assumes no Bitcoin** is the hypothetical with no Bitcoin income: Bryn's £280,320 over 5 years from its extra export alone against what it puts in under each option (paid back in 19.6 months on the 50:50 CAPEX share, 39.2 months when it pays it all), anchored on the 50:50 CAPEX share, which the tab opens on and keeps softly marked, with the sum behind it along the bottom and Bryn's £91,684 half paid back in 19.6 months on a 5-year line; the two tabs share the chosen option. Opened as a plain file, `bryn_3d_sim.html?tab=dispatch`, `?tab=finance` or `?tab=export` starts on that tab and `?deal=card`, `?deal=open` and `?engine=max` start Finance at those stages (the Streamlit frame passes no query string through, so the app always opens on Site). A second, teal badge on the compute container's spot by the LV cabinet opens the Compute Render full-screen (`?view=compute`): the yard south of the feed tank rebuilt in metres from imagery and the 13 October 2026 site photos, with the Green Hash 10 ft container in place and the two ways of placing its dry cooler (on the roof, or on the pad beside it), the LV cabinet at the west end of its compound by the Heras line with the transformer a walkway east of it, the cable route into the open trench, and every part carrying its source and what was assumed (click it); the same app serves each route, so the map page carries none of the models' weight |
| `app_kld_atlas.py` | `kld_atlas.html` + `kld_hydro_chrome.html` + `kld_interactive.html` | KLD Atlas — Kinlochdamph 999 kW run-of-river hydro (Loch Damh, Wester Ross): site assets, the 11/33/132 kV network and the two SSEN connection options. A pulsing BLOX badge on the powerhouse opens the 3D Revenue Sim full-screen — the same app serving `?view=3d`, so the atlas page carries none of the model's weight |
| `app_ihn_atlas.py` | `ihn_atlas.html` + `ihn_heat_chrome.html` + `heat_network_3d.html` | IHN Atlas — the IHN heat network: a still, daytime three.js satellite atlas of the district with the network main, the existing and proposed connections, the 11 kV route and the HNES blocks drawn on the imagery, and the 76 × 25 m plant room cut away under the block; four camera views (Overview, the Plant room as an amber call to action, EC1, EC2) with a caption that follows the view, a key, layers and a Council site-map overlay. A pulsing BLOX badge over the plant room opens the dispatch model, Heat Network 3D, full-screen — the same app serving `?view=3d` with the same model file the investor pack serves, all data included, so the atlas page carries none of the model's weight |
| `app_kh_atlas.py` | `kh_atlas.html` | Keith & Huntly Atlas — the decision page for the two Moray primaries SSEN has priced: a three.js satellite scene of each substation with SSEN's proposed works (joints, cable, metered RMU, the 33 kV diversion at Huntly) and Savills' siting options drawn on it, and a nine-step, keyboard-driven telling of the two budget estimates built for presenting to the team. It opens and closes on a **cost ladder** (find out / secure a place / connect / our own works) under a Both £2,170 · Huntly £1,240 · Keith £930 · Neither £0 switch (the minimum SSEN fees for feasibility studies), walks Keith's £150,000 for 1,999 kVA (1,300 kVA applied for) and Huntly's £110,000–£121,000 for 2.78 MVA over the scene with what each figure covers and what Savills inferred is left in the breakers, says plainly that the two figures are **not like for like** (Keith's has SSEN digging; Huntly's leaves the digging, civils, transformer and LV side to RenewaBlox and carries a 150 m diversion), names the gates before anything can be lodged (a landowner's Letter of Authority, and Savills' fees from its October 2025 proposal: £1,200 per DNO pre-application meeting, £7,500 to submit a connection application, land procurement TBC), and ends on three decision lines. Arrow keys step, `1`–`9` jump, `D` opens the site's detail drawer (scope, exclusions, the full capacity chart, the ranked plots, every open question), `S` the sources, `L` the camera and layer popover, `?` the key map; `?beat=n` or `?step=decide` deep-links a step, `?still` skips the flights. Unknowns stay unknown on the page: RenewaBlox's own works are "to be costed", never a number |
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
`srv_atlas_3d_badge.html`, `bryn_atlas.html`, `bryn_atlas_3d_badge.html`, `bryn_3d_sim.html`, `bryn_compute_3d.html`, `heat_network_3d.html`, `demand_for_constraints_3d.html` and `ihn_atlas.html` are built, not hand-edited. Each builder re-skins its
hand-authored source in the shared RenewaBlox design system (petrol brand
tokens, Inter, brand bar — and glass panels where the build re-skins the panels) and re-uses the source's data and
vendored payloads byte-for-byte:

| Output | Builder |
| --- | --- |
| `kld_atlas.html` + `kld_hydro_chrome.html` | `Contracts/Kinlochdamph/Atlas/build_kld_atlas.py` |
| `moray_atlas.html` | `Contracts/Savills Earth/Atlas/build_moray_atlas.py` |
| `kh_atlas.html` | `Contracts/Savills Earth/Atlas/build_kh_atlas.py` — from the working page `Keith_Huntly_Atlas.html` beside it: the three.js bundle, the scene engine, the GLB kit, the geometry, the imagery, the roundel, the wordmark and the embedded Inter face pass through byte-for-byte (cut out by exact marker; the build fails if a marker is missing or ambiguous), and the stylesheet, markup and panel code are re-authored in `parts/kh_style.css`, `parts/kh_body.html` and `parts/kh_ui.js` as the guided, decision-first page. The hand-written part is wrapped in a closure of its own inside the bundle's, because the bundle's minified names (`hl`, `li`, `mk`, …) share the outer scope and would overwrite same-named declarations. The two sites' scene geometry (`scene:` and `options:` in `SITES`) is copied verbatim from the working page so the map and the model agree; every other figure on the page is traceable to the SSEN letters, the Savills grid-surgery report and the Savills engagement letters |
| `srv_3d_sim.html` | `Contracts/Scrivelsby Farm Ltd/Atlas/build_srv_3d_sim.py` |
| `srv_siting_3d.html` | `Contracts/Scrivelsby Farm Ltd/Atlas/siting/build_siting.py` (three.js viewer bundled with esbuild; the schemes live in `siting/src/scheme.js` (option A) and `siting/src/scheme_b.js` (option B)) |
| `srv_atlas_3d_badge.html` | `Contracts/Scrivelsby Farm Ltd/Atlas/build_srv_atlas_badge.py` |
| `bryn_atlas.html` + `bryn_atlas_3d_badge.html` | `Contracts/Bryn/Atlas/atlas/build_bryn_atlas.py` — from the site layout in `bryn_site.py`, the one source the 3D model is also built from, so the plot and the features agree between the map and the model |
| `bryn_3d_sim.html` | `Contracts/Bryn/Atlas/viewer/build.mjs` (three.js viewer bundled with esbuild; both are loaded from `tools/node_modules`, so the folder can live anywhere). The scene is generated in Blender by `blender/build_scene.py` from `bryn_site.py` and compressed by `tools/optimize_glb.mjs`; the commercial figures live in `viewer/src/data.js`, transcribed from the revenue-share model for the final 172.8 kW deployment (24 miners); `viewer/src/finance.js` adds Bryn's extra export and works out the paybacks with it and the Export only figures, and `viewer/src/ui.js` lists the few values it derives for display; the Dispatch tab's model is `viewer/src/model.js` (from the 14 October 2026 seasons handover, set to match the Finance tab's energy and extra export), its desk chart `viewer/src/chart.js` and its panel `viewer/src/dispatch.js` |
| `bryn_compute_3d.html` | `Contracts/Bryn/Atlas/atlas/build_bryn_compute.py` — from the compute siting render `blender/bryn_site.html` (a self-contained three.js page generated outside the folder, in Blender via bpy): the builder keeps its scene and bundle, moves the parts the October 2026 layout changed by patching the embedded GLB and metadata (the LV cabinet, the transformer, the trench, the ground cooler), re-skins the page in the design system from `bryn_compute.template.html` and appends its own edition of the render's app code, `bryn_compute_app.js`, which draws the pipes and the cable route from the metadata |
| `heat_network_3d.html` | `Contracts/<IHN client>/Atlas/build_heat_network_3d.py` — from the client edition of the IHN heat-network model, with the site anonymised to IHN: the brand bar, house type and chips go on, the Google Fonts links come off, and the scene, panels, data and payloads pass through byte-for-byte |
| `ihn_atlas.html` | `Contracts/<IHN client>/Atlas/build_ihn_atlas.py` — from the in-house IHN Atlas 3D scene (`IHN_Atlas_3D_1.html`): the house bar, light glass panels and white callouts go on, the live-dispatch inset, the dispatch desk, the settlement clock and the sky switcher come off (the dispatch series with them, so the page is lighter than its source), the sky is fixed at day, and the scene, its data, the imagery and the vendored three.js pass through byte-for-byte. The scene script is minified, so every cut is an exact-string splice that must match once or the build fails; the build also fails if the source's link to the investor portal, or its access key, survives |
| `demand_for_constraints_3d.html` | `Data Room/Inhouse IP/Atlas 3D/DfC/build_dfc_3d.py` — from edition 4 of the in-house DfC model (`make_edition_4.py` derives it from edition 3: Heat Network pacing, a full-year opening run with three highlight days, state-keyed weather, and the wholesale projection's continental coupling with a consistent price stack and RO roll-off, all editable in the assumptions drawer): the brand bar, house type and chips go on, the footer row comes off, the layout is tidied for a laptop screen, and the scene, model, data and payloads pass through byte-for-byte |

`srv_atlas_3d_badge.html` is the 3D-sim gateway for the client atlas: the BLOX
badge, the popup call-to-action rows and the overlay. `app_srv_atlas.py`
appends it to `srv_atlas.html` at serve time, so the hand-maintained map file
stays pristine and the sim loads through `?view=3d` only when opened.
`bryn_atlas_3d_badge.html` does the same job for `app_bryn_atlas.py`, with two
badges: the BLOX logo on the proposed plot, which opens the 3D Site Model, and
a teal fan chip on the compute container's spot by the LV cabinet, 20 m west of
the plot, which opens the Compute Render (`?view=compute`); the data-centre and CHP
popups carry a CTA row for each.

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

`app_srv_atlas.py`, `app_kld_atlas.py`, `app_ihn_atlas.py` and `app_bryn_atlas.py`
are deliberately the same shape, so a new site can be stood up by copying any of them:

* one app, two views — the atlas by default (a Leaflet map for SRV, KLD and Bryn, a
  still three.js satellite scene for IHN), its 3D model at `?view=3d`, both
  rendered full-bleed through the same Streamlit chrome-stripping CSS (Bryn adds
  a third route, `?view=compute`, served the same way);
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
Bryn's badge sits on the proposed plot itself — the BLOX logo marks where the
data centre would go — and its model is in four tabs: Site (the model alone,
the first view), Dispatch (the seasons against the export limit, with the
dispatch desk), Finance (the three funding options, as a pill, then a card
of the three options, widening on demand) and Export only (the hypothetical
with no Bitcoin income), so the first view is the site and the wide views are
for the discussion. Opened as a
plain file, outside Streamlit, Bryn's model page finds the map page by
relative link (`bryn_atlas.html`); the map page's route to the model lives in
the badge layer, which only the app appends at serve time.

One consequence of Streamlit's component sandbox for all four: the frame has no
allow-top-navigation, so the gateway and the models' "Atlas" pills cannot set
the parent's location (the browser refuses it silently). Instead they create an
anchor in the parent document and click it, which the browser attributes to the
parent and so navigates the page in place; if even that is refused they rewrite
the parent's history entry and reload it, and as a last resort open the
destination in a new tab. Served outside Streamlit (a plain static host) they
navigate in place by ordinary links.

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
| `/privacy/` | the privacy notice (`energy_privacy.html`), linked from the welcome page's footer with the registered company details |

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

Netlify's own notification emails have not been reliable (and on a credit-based
plan they are one more thing that can stop), so the route the inbox actually
relies on is **`tools/forward_form_submissions.py`**, run every 15 minutes by
GitHub Actions (`.github/workflows/forward-form-submissions.yml`): it reads the
site's verified submissions from Netlify's API and emails each new one, from
energy@renewablox.co.uk to itself through AgentMail, with the same details a
Netlify notification would carry and a link to any attached document. The inbox
is its only state: each email's subject carries the submission's tag
(`[bill-check #3]`), and a submission whose tag is already in the inbox is not
sent again. It needs two repository secrets, `NETLIFY_AUTH_TOKEN` (a Netlify
personal access token) and `AGENTMAIL_API_KEY`, and does nothing until both
exist; "Run workflow" on the Actions tab runs it on demand.

Domain: `renewablox.co.uk`'s DNS is at Wix. The subdomain is a CNAME record
`energy` → `renewablox-energy.netlify.app` there, with `energy.renewablox.co.uk`
added as the project's domain in Netlify, which issues the HTTPS certificate.
The apex and `www` records keep redirecting `.co.uk` to `.com`. Netlify's
visitor access controls ask for a team login on preview deploys only; the
production site is public.

Build and look at it locally:

    python build_energy_site.py
    python -m http.server 8800 -d energy_site     # then open http://localhost:8800/

## ai.renewablox.com — RenewaBlox's AI tools

The in-house tools live on one domain of their own, built from `ai/` by its own Netlify
project, separate from the energy site:

| Address | Page |
| --- | --- |
| `/` | the front door: the tools, two doors (`ai/index.html`) |
| `/oscar/` | OSCAR, the site model (`ai/oscar.html`) |
| `/atlas/` | Atlas, served by proxy from its own Netlify project (`renewablox-atlas`, atlas.renewablox.com), which keeps deploying as it does now |

`ai/build.py` copies the pages into `ai/site/` (git-ignored) and checks three things that
would otherwise break quietly: every input id a saved OSCAR scenario can hold is still on the
page (`SCENARIO_IDS`, which only ever grows), no page loads anything from elsewhere, and the
live sources OSCAR calls are the ones `ai/netlify.toml` proxies and allows. `ai/netlify.toml`
holds the rest: the Atlas proxy (with the root-relative links Atlas's own pages may use,
`/investors/`, `/market/`, `/portal/`, sent back under `/atlas/`), the live-data rewrites, a
Content-Security-Policy that allows inline code, data images and, for OSCAR, its three live
sources, and `noindex` (with a `robots.txt` that disallows everything): these are tools for the
team and the clients they are sent to, not for search engines.

**OSCAR** (Optimising Site Capacity & ASIC Revenue) is one self-contained page: what a site
earns when its power goes into Bitcoin mining, energy markets (export, demand turn-up, the
capacity market) and heat off-take, how the revenue is shared between RenewaBlox and the client,
and when each side's CAPEX comes back. The inputs sit in a rail on the left, in the order the
conversation runs (site, mining, energy markets, heat, the deal, then the expert-only hardware,
market and Phase 2); the results answer on the right and recalculate as anything changes.

* **Two views.** Expert shows every input and every table. Client hides the hardware and market
  assumptions, prices CAPEX at `CLIENT_CAPEX` (£640,000 per MW of site power plus 5%
  contingency, miners' VAT included; the note on the page reads from the same constant), opens on
  a hero of what the site receives against today's power revenue, and sets the recovery period
  to the month RenewaBlox's share of the CAPEX is paid back, recomputed with every input. The
  site (its power, uptime, streams, today's revenue, contract length, market inputs) travels
  between the views; the deal settings are remembered per view.
* **The model** is `compute(inputs)`, pure and separate from the page, so scenarios and tests run
  it directly (`window.OSCAR.compute`). A month is 1/12 of a 365-day year throughout; energy
  follows the whole miners installed; transaction fees are a share of today's block subsidy, held
  constant in BTC per block so they don't halve with it; the revenue-share totals are what each
  side is paid, after the cost of power, matching the cash-flow chart.
* **Live inputs** (the Bitcoin price in GBP, the 30-day network hash rate, the last week's fees)
  come from CoinGecko, mempool.space and Blockchain.com: each is asked directly first, then
  through the site's own rewrites under `/oscar/api/`, never through a third-party proxy. The
  chip in the header says whether the figures in use are live or as entered, and refreshes them.
  A scenario opened from a link keeps its saved market inputs until the chip is clicked.
* **Scenarios** are saved in the browser (`oscar.scenarios` in local storage), compared in a
  table, exported and imported as JSON (the way to move them between browsers, or from the
  September 2026 file edition, whose scenarios are brought over automatically the first time the
  new page opens in the same browser), and shared as links that carry the whole scenario in the
  address's `#s=` fragment, so it never reaches a server. The September edition's
  `?scenario=` links still open. Its "Phase 2 start (years)" counted the contract year Phase 2
  starts in (1 = from day one); the field now counts the years before it starts, and older
  scenarios are converted as they are opened.
* **Charts** are SVG drawn at the width of their box, in one categorical palette checked for
  colour-blind separation in both themes (RenewaBlox blue, client magenta, mining orange, export
  aqua, capacity yellow, turn-up green, heat red, today's revenue grey), one axis each, with a
  crosshair and tooltip that follow the mouse, a finger or the arrow keys.
* **PDF.** Printing (or "Save as PDF") gives a report of the current scenario: a header with its
  name and date, the results, and an assumptions block, with the charts redrawn to the page width.
* Light and dark follow the system until chosen in the header; the page works from 360 px up.

Deploy: the Netlify project is `renewablox-ai` (renewablox-ai.netlify.app). Link it to this
repository with production branch `main` and its **base directory set to `ai`** (it then reads
`ai/netlify.toml`, not the root one), add `ai.renewablox.com` as its domain, and point a CNAME
record `ai` at `renewablox-ai.netlify.app` at the renewablox.com DNS host, as for `atlas.` and
`crm.`. The `/atlas/` proxy targets `https://atlas.renewablox.com`, so that domain must resolve.
Netlify then builds on every push to main. The project was created private (a team login on every
deploy, production included); the energy and Atlas projects ask for one on previews only.

Build and look at it locally (or open `ai/index.html` and `ai/oscar.html` straight from the
folder, where the live sources are called directly):

    python ai/build.py
    python -m http.server 8900 -d ai/site      # then open http://localhost:8900/

## atlas.renewablox.com — client pages

Atlas (the `renewablox-atlas` Netlify project) is deployed by upload from a folder of its own: its
front page, `/investors/`, `/market/` and `/portal/` are not in this repository. The client pages it
carries are, in `atlas/`, one folder per client, each named by the client's code and nothing else.
BLN is the first:

| Address | Page |
| --- | --- |
| `/bln/` | BLN Atlas (`atlas/bln/index.html`): the hydro powerhouse on the satellite imagery, with the BLOX badge |
| `/bln/3d/` | BLN 3D (`atlas/bln/3d/index.html`): the 3D render the badge opens |

**BLN Atlas** is the site-atlas pattern on a static host: a full-window Leaflet map on Esri World
Imagery under the house brand bar, the powerhouse, its inlet chamber and its grid compound drawn from
the 3D model's own plan (so the map and the render agree; each opens its note from the keyboard as
well as the mouse), and a pulsing BLOX badge on the powerhouse with its "Open the 3D render" pill
standing above it (not along the building, where it would cover the inlet chamber), a matching row in
the powerhouse's popup and a "3D render" button in the bar, which stays live when the bar fades at
close zoom. Each opens `3d/` in the same window; the render's "Atlas" pill and the browser's Back come
back. The labels appear from zoom 18, the inlet's from 19. The powerhouse's place on the imagery is one line, `SITE`
(the slab's centre and the compass bearing of its long axis, west gable to east gable). It was set on
Esri's imagery (WorldView-2, 13 May 2025): the building at the end of its own track loop beside the burn,
where the glen floor reaches the powerhouse's +184 m, its roof about 10 × 6 m with the fenced grid
compound off one gable and the inlet chamber off the other, which puts the model's axis at about 43°
(south-west to north-east) rather than the east–west the model assumes. To move it, open `/bln/?place`
(the drawing and the badge then let clicks through to the imagery), click the middle of the roof, turn
the footprint with `[` and `]` (Shift for 10°), copy the line it prints into `SITE` and rebuild. Esri
has imagery here to zoom 19, which the map's tiles stop at (`maxNativeZoom`); beyond that it enlarges.

**BLN 3D** is the handover's model-viewer page re-made in the house style of the Bryn 3D page: the
header with the "Atlas" pill, wordmark and tabs (**Model**, **Flythrough & stills** and **Economic
dispatch**, which is still to be built; `#media`, `#economic` or `?tab=` open on one, and the old
`#flythrough` and `#stills` still lead to the second), an **Assumptions** button in the bottom corner
that opens what is measured and what is assumed as a sheet over any tab (`#assumptions`, or the old
`#facts`), and on Model the whole window
for the model, a camera rail (Exterior, Cutaway, Inside, BLOX cabinet, Ventilation, then the Open
cabinet, See-through cabinet, Walls and roof, Heat enclosure, Airflow, Markers and Turn slowly
switches, and Technical dispatch; a bottom strip on a phone) and a caption that follows the view. Turn
slowly sets the model turning on model-viewer's turntable at once, a full turn in 36 seconds; any
camera preset stops it. It keeps the handover's mechanics: two models swapped by `src` with the camera preset
re-applied on load, `max-field-of-view="70deg"` so the wide presets get through, the cabinet door driven
by seeking the cutaway's `open_cabinet` clip, and the airflow arrows (materials `air_cold`, `air_hot`)
shown by alpha. Three things differ from the handover page. The clip loops, so seeking to its full
length wraps to frame 0 and the door snapped shut on its last frame; the page stops a millisecond
short. The burn's water is exported as near-black glass (85% transmission) and showed as a black band;
the page turns the transmission off and gives it a river's colour on load. And a marker behind
something solid (the inlet chamber seen through the roof, the cabinet from outside) is dimmed by a ray
cast at it once the camera settles, as model-viewer already dims one facing away; a dimmed marker comes
up to full strength when pointed at or opened, and one off the edge of the frame leaves the Tab order.
A marker's note is its button's description, opens on whichever side has room and is kept on screen,
clear of the rail and the caption; while one is open the other markers fade, since model-viewer
re-stacks their layers every frame and a later dot would otherwise paint over the note. A camera
preset turns the model back square and stops Turn slowly, which turns the model rather than the
camera and would otherwise carry every preset round with it. The cutaway model is fetched into the cache shortly after the first
model is on screen; Open cabinet pressed while it is on its way opens the door when it arrives; if it
fails to arrive the page goes back to the model it has and says so, and asks again under a new address
next time (model-viewer remembers a failed load under the old one), and a lost WebGL context (a phone
switching apps) is left to model-viewer to restore.

**The 21 October changes** (the client's notes, with a photograph of the cabinet and sketches on the
model) are in the model and the page. The cabinet holds 20 miners, three to a shelf on the lower six
shelves and two on the top one with its south slot spare, as in the photograph; the network switch
and edge controller stand on edge in the gap beside the shelves, with the patch leads running down
it, and a PDU stands in each side gap low down. The single 630 mm wall fan is now two 450 mm fans
on the cabinet's centre line, one above the timber batten that crosses the gable at 2.0–2.1 m and
one below it (2.55 m and 1.50 m to their centres, read from the sketch; the yellow crane beam above
leaves no room for a fan over it). The client's back-up option, an 18 mm OSB box from the cabinet's
rear panel to the gable round both fans, is in both models and hidden until Heat enclosure is on.
Model-viewer reaches materials and animations but not single parts, so the page reaches into its
three.js scene (behind the `scene` symbol) for the rest: Walls and roof hides the cladding, roof,
gutters, door, louvres, battens, the fans' outside cowls, the fittings on the walls and the whole
steel frame, all but the yellow crane beam with its stops and hoist; See-through cabinet gives the cabinet's sides, top and back (and the
enclosure, when shown) a faint copy of their own material that the marker rays pass through; each
miner's status light can go dark on its own; and each fan's hub and blades hang from an empty,
`fan1_rotor` and `fan2_rotor`, which the page turns while the airflow is drawn or the simulation
runs the fan. A hidden part is hidden mesh by mesh, since model-viewer's ray cast skips only a
mesh that is itself hidden. Technical dispatch opens a panel (at the right on a wide screen or a phone on its
side, along the bottom otherwise) and moves the camera to the open cabinet: `3d/dispatch.js`, fetched on first use, simulates a day minute by minute (the
river's power is invented; the rule is the client's: start a miner while export sits at the 250 kW
limit, another each minute it stays there, stop one each minute it is at or under 245 kW; 3.4 kW a
miner, so 15 run at the full surplus; an illustrative thermostat brings the lead fan in at 24 °C and
keeps it running while any miner does, and the second in at 32 °C and out at 21 °C, each with a
minimum run time) and charts it,
and its state lights the miners and turns the fans. The
flythrough was left as it was, so it shows the first layout; its page says so.

**Anonymity.** The handover package named the site in three places that a browser would show: the
page text, a line of 3D text on the cabinet's nameplate in both GLBs ("BLOX.  <site> 50 kW") and the
flythrough's opening title card. In `atlas/bln/assets/` the nameplate line has had the name cut out of
its mesh (it reads "BLOX.  50 kW"; the cut vertices are overwritten, not hidden) and the flythrough's
first three seconds are rebuilt from its first clean frame under a new card reading "BLN · BLOX data
centre", fading in and out as the original did; the rest of the film is the original, re-encoded at
720p (CRF 22). The stills carry no legible name (in two of them the old nameplate line is a smudge
two pixels tall) and no metadata. The exterior GLB's grid compound parts are named `grid_*`, as the pages
call it, rather than after the network operator. The regeneration kit (the Blender scene script and
its job files) and the handover notes name the site, so they stay out of this public repository. A
re-render from that kit brings the name back unless `rack_brand_text2` reads "BLOX.  50 kW" and the
title card's second line "BLN · BLOX data centre" in the scene script; the kit as changed for the
21 October layout writes the nameplate that way, and its export is followed by a small step that
renames the grid compound's parts, which the kit names after the network operator, to `grid_*`.

`atlas/build.py` copies the pages into `atlas/site/` (git-ignored) and fails on anything that would
undo that: a word that names or places the site, checked in every file, binaries included, as UTF-8
and UTF-16; a UK postcode, OS grid reference, Scottish company number or Windows home folder in the
text files; any EXIF, XMP, comment or text chunk in a JPEG or PNG, read from the bytes whatever the
file is called and including images packed in a model (any other kind of image is refused); a nameplate
line wider than "BLOX.  50 kW"
(or a GLB without that node); a flythrough other than the reviewed one (`FLYTHROUGH_SHA256`: check a new
one frame by frame, the title card above all, before changing it); anything loaded from elsewhere but
the imagery tiles (in any attribute, style or script, the pages' own script modules included; a plain
link the visitor follows is fine); a file
referred to but missing; or a page without `noindex`. The words themselves are never written in this
public repository, not even as hashes, which a gazetteer reverses in seconds: they live in
`atlas/.names` (git-ignored, one word per line) or in the `ATLAS_NAMES` environment variable
(comma-separated; a byte-order mark from a Windows editor is allowed for). Without them the build warns and `--merge` refuses to run, so an upload is never
prepared unchecked; whoever deploys keeps the file. `atlas/_headers` holds the pages' header
rules (a Content-Security-Policy that allows the pages' own files and the imagery host, `nosniff`,
`noindex`).

Deploy: download the Atlas site's current deploy from Netlify (renewablox-atlas → Deploys → the
published deploy → Download), unzip it, then

    python atlas/build.py --merge path/to/the/unzipped/folder

which puts `bln/` into it and adds the header rules to its `_headers` between marker lines (re-running
replaces them; it refuses a folder inside this repository), and drag the folder onto the project's Deploys page. If the Atlas site's own `_headers`
sets a stricter Content-Security-Policy on `/*`, both policies apply and the stricter one wins, so
check `/bln/` and `/bln/3d/` load their imagery and models after the deploy. The pages link by
relative address only, so they also work under ai.renewablox.com's `/atlas/` proxy, which sends a
root-relative `/bln/` back under `/atlas/` like Atlas's other sections.

Atlas's front page lists the client pages in its **Client Atlas** section (it replaced "Choose your
atlas"; the Market and Investor Atlases stay in the page's own navigation and hero). The section is
`atlas/front/clients.html`: a card per client, named by its code (BLN, with the turbine-hall render as
its cover, opening `/bln/` and `/bln/3d/`), then "This could be your site" with the access e-mail.
`--merge` writes it into the front page between the lines
`<!-- client atlas (Public-Atlas atlas/front/clients.html, placed by atlas/build.py --merge) -->` and
`<!-- end of client atlas -->` (which the live page now carries, so a fresh download keeps working),
and copies the other files in `atlas/front/` (the cover images) to `assets/img/clients/`. The build
checks them as it checks the pages, and also that every root-relative address in the section is a
cover or a client page. To add a client, add its folder and a card, and put its cover beside
`clients.html`. If the markers are missing (a front page re-made by hand), `--merge` says so and
leaves the page alone; put them back around the section first.

Build and look at it locally (the map's imagery needs the internet; the models must be served over
http, not opened from the folder):

    python atlas/build.py
    python -m http.server 8901 -d atlas/site     # then open http://localhost:8901/bln/

## Run locally

    pip install -r requirements.txt
    streamlit run app_srv_atlas.py
    streamlit run app_srv_contractor.py
    streamlit run app_bryn_atlas.py
    streamlit run app_kld_atlas.py
    streamlit run app_ihn_atlas.py
    streamlit run app_moray_atlas.py
    streamlit run app_kh_atlas.py
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
| `app_bryn_atlas.py` | `bryn-atlas.streamlit.app` — the client-facing Bryn Atlas, with the 3D Site Model at `?view=3d` and the Compute Render at `?view=compute` |

`app_peaker_demo.py` is ready to deploy and has no subdomain yet — add its row
above once one is claimed. So is `app_generator_demo.py`, the generator pack;
`generator-demo.streamlit.app` matches the investor pack's naming. Once it is
live, add its row above and its URL to `APPS` in
`.github/scripts/keep_awake.py` (and to the alert's app list in the workflow).
The same goes for `app_business_demo.py`, the business pack
(`business-demo.streamlit.app` would match).
And for `outreach/app_outreach.py`, the outreach strategy: set the main file path
to `outreach/app_outreach.py` (`renewablox-outreach.streamlit.app` would suit).
`app_kh_atlas.py`, the Keith & Huntly Atlas, is ready to deploy too
(`kh-atlas.streamlit.app` would match the other atlases); it is an internal
decision page that draws on a Savills report marked Sensitive, so share its
link with the team rather than publicly, and add it to the keep-awake list
only if it is to stay up between meetings.
The IHN and Bryn atlases serve their models with all of their data at
`?view=3d` (and Bryn's compute render at `?view=compute`), so their links are for the client, not the public demo's footing.
All six deployed apps are visited hourly by the keep-awake workflow
(`.github/workflows/keep-awake.yml`). For the portal app, set
`PORTAL_PASSCODE` in the app's secrets on Streamlit Cloud to lock it (the code
never lives in this repo; `.streamlit/secrets.toml` is git-ignored), then run
`python portal_key.py <code>` and put the printed `?k=…` on the end of the app's
URL behind the portal's button (a button that opens the app in a new tab is the
best home for a full-screen 3D scene; the pack also works inside a Wix "Embed a
site" element with `?embed=true&k=…`, because its own links carry the key on and
do not depend on the cookie). Rotate the code to expire every old link.
