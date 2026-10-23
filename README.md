# RenewaBlox — Public Atlas

The source of RenewaBlox's public-facing sites, every one of them static and hosted
on Netlify, with Supabase for the Atlas's sign-in:

* **atlas.renewablox.com**, the RenewaBlox Atlas (`atlas/`): the Market Atlas, the
  investor packs and their standalone models, and, behind a Google sign-in, the
  client atlases and the team's pages;
* **energy.renewablox.co.uk**, the client packs for generators and businesses
  (`build_energy_site.py`);
* **ai.renewablox.com**, RenewaBlox's AI tools (`ai/`).

Each page is a self-contained standalone file — a Leaflet map, or a three.js scene —
with all of its data embedded, built into its site by a standard-library Python
script that Netlify runs when a push changes that site's files (see "Builds and
credits" under Deploy). This repository is public, so the sign-in
protects the addresses, not the files.
None of it is hosted on Streamlit any more: every page that was a Streamlit app is
now an address on one of these sites, and the Atlas's build fails if any page
points at a `streamlit.app` address.

## Pages

| Address | Built from | What it shows |
| --- | --- | --- |
| **atlas.renewablox.com** | | |
| `/market/` | `atlas/root/market/index.html`, framing `/market/map/`: `atlas/vendor/client_atlas_v2.html`, a copy of Eunice-Platform's | Market Atlas — where RenewaBlox can put flexible and stranded renewable capacity to work across Great Britain: AD peakers, subsidised generators and stranded hydro, with Balancing Mechanism tiers and a PPA benchmark; `?view=`, `?site=` and `?theme=` on the market page's address open the map where a shared link points |
| `/investors/demo/` | `investor_demo_home.html` + `peaker_plant_3d.html` + `kld_interactive.html` + `heat_network_3d.html` + `demand_for_constraints_3d.html` | Investor Demo — a landing page for prospective investors that packs the interactive 3D models: Peaker Plant 3D (the peaker business model as a living site, `peaker-plant/`), Hydro 3D (the KLD powerhouse and its in-room data centre, `hydro/`), Heat Network 3D (the IHN heat network and the data centre that heats it, a year half-hour by half-hour, `heat-network/`) and Demand for Constraints 3D (the Moray cluster north of the B4 constraint and the two BLOX halls NESO dispatches to absorb curtailed wind, `demand-for-constraints/`). **Investor data is gated:** on Hydro 3D, Heat Network 3D and Demand for Constraints 3D the panels that carry the figures are blurred and inert and a card points to the investor portal (`GATED` in `packs.py`, applied by the build — the model files are untouched, and the portal serves them unblurred) |
| `/investors/portal/` | `investor_portal_home.html` + the same four model files | Investor Portal — the Investor Demo's pack in full, unblurred, at the address the Wix investor portal's members area links to, with the Investor Atlas inside it at `/investors/portal/atlas/`. It isn't gated on the Atlas: the way in is the Wix portal's registration and investor declaration, and only the address keeps it from the public (its pages ask not to be indexed). The files themselves stay public in this repository |
| `/investors/portal/atlas/` | `atlas/vendor/investor_atlas_v3.html`, a copy of Eunice-Platform's | Investor Atlas — contract value, pipeline and market context for AD peakers, subsidised generators and stranded hydro across Great Britain (the SAM, TAM, hydro and PPA views, with a Present mode), in the investor portal; `?view=`, `?site=`, `?theme=` and `?present=1` open it where a shared link points |
| `/investors/australia/` | `investor_demo_aus_home.html` + `peaker_plant_3d.html` + `kld_interactive.html` + `nem_negative_price_atlas.html` | Investor Demo (Australia) — Peaker Plant 3D and Hydro 3D plus NEM 3D (mining economics across the Australian NEM, `nem/`), on its own address for the investor group that model was built for |
| `/models/peaker-plant/` | `peaker_plant_3d.html` | Peaker Plant 3D standalone — the same peaker model on its own link, for client brochures (AD operators): no landing page, no pack navigation, straight into the model, prices in **p/kWh** |
| `/models/peaker-demo/` | `peaker_plant_3d.html` | Peaker Demo — the pack's Peaker Plant 3D on a link of its own, for sending the peaker without the rest of the pack: no landing page, no pack navigation, prices in **£/MWh**, and tailored for an energy-literate audience (strike opens at £80 on a £50–£100 range; the export price is named **DA + gDUoS**) |
| **atlas.renewablox.com, behind the sign-in** | | |
| `/clients/srv/` | `srv_atlas.html` + `srv_atlas_3d_badge.html` + `srv_3d_sim.html` + `srv_siting_3d.html` | SRV Atlas — the client view of the Scrivelsby (Home Farm AD) scheme: where the compute load bank sits, how it connects, and the site around it, kept deliberately minimal (LN9 6JB). Two pulsing BLOX badges on the yard open the 3D Dispatch Sim (`?view=3d`) and the 3D Compute Kiosk (`?view=siting`, two siting schemes on one page: option A, one 4 m kiosk for the LV board, three DCX hydro racks and their cooling loop with the dry cooler on the roof; option B, the existing kiosk extended for the board and the Winchain 10 ft hydro cooling container behind it with the dry cooler on the container roof) full-screen — views of the same address, so the map page carries none of the models' weight |
| `/clients/srv/?view=3d` | `srv_3d_sim.html` | SRV 3D Sim — the Scrivelsby Peaker: a three.js model of the Home Farm AD site with a half-hourly dispatch simulation of the 350 kW switchable block over a real metered year, and the site survey photography on every asset pin |
| `/clients/srv-contractor/` | `srv_contractor.html` | SRV Contractor Atlas — the same site surveyed for the LV connection RFQ: switchgear detail, the full 12-photo survey including switchroom interiors, the feeder route with its tie-in and containment notes, and OSM/DNO context |
| `/clients/bryn/` | `bryn_atlas.html` + `bryn_atlas_3d_badge.html` + `bryn_3d_sim.html` + `bryn_compute_3d.html` | Bryn Atlas — the client view of the Bryn Power AD plant scheme (Gelliargwellt Farm, Gelligaer CF82 8FY): where a BLOX data centre would stand, on the yard a few metres from the LV room at the CHP engines, to take about 200 kW of the site's surplus power by a short connection with no cable route across the site, kept deliberately minimal. A pulsing BLOX badge on the proposed plot opens the 3D Site Model full-screen (`?view=3d`): a three.js model of the plant, built in Blender from aerial imagery, with the data centre in place, in four tabs in the header. It opens on **Site**, the model alone. **Dispatch** plays the site's power half hour by half hour on a representative day per season (weekday or weekend, average or sunny; site load 125 kW on weekdays and 25 kW less at weekends and on bank holidays), Today against With BLOX: a live readout, the dispatch desk (two chart lanes: potential generation, and export against the 1.8 MW limit), Bryn's extra export as a single assumption (350,400 kWh a year at 16p/kWh, £56,064 a year, the figure Finance uses), and the seasons side by side in a fold that opens on demand; the data centre is 24 miners, 172.8 kW of compute installed, drawing at most 200 kW overclocked with its pumps, dry cooler and controls (their own load, about 5–8 kW, comes out of the 200 kW); with BLOX load following, export is held at 1,715 kW (85 kW headroom) against 1,675 kW today and the data centre takes the rest up to its 200 kW, and that target and the engines' warm-weather easing are set so a typical year matches the Finance tab (350,400 kWh of extra export, and 1,548,857 kWh into the data centre in a typical year: less 5% for outages, the 84% site capacity factor the revenue-share model uses); the scene follows the clock (the sun, the data centre rising out of its slab, its fans and the solar roofs' glow). **Finance** is the walk-through of the three ways of funding it (RenewaBlox funds it, 50:50 CAPEX share, Bryn funds it), from the revenue-share model for the final deployment (*Bryn Recycling 172.8kW final*, 19 October 2026: 172.8 kW, 24 miners, RenewaBlox's option recovering its CAPEX over 24 months; the options are scaled to the model's site-level outputs, £593,693 over the contract and a 17.6-month project payback) with Bryn's extra export added to Bryn's side: the panel is led by the 50:50 CAPEX share, opening on it in every size and keeping a soft amber mark on it when another option is chosen, and starts as a pill quoting it (Bryn receives £577,166), with the engine strip along the bottom; the strip maximises into a big-figure view led by the installation's 5-year total contract value; the pill opens a card of the three options, the chosen one showing what Bryn receives, its payback and a sparkline (and from then the split callout rides on the unit), and "Cash flow, year by year" widens it for the discussion: the options as chips with each one's outlay, total and payback, the answer in one line ("Bryn receives £755,274 over 5 years · paid back in 14.4 months"), one sentence on how the option works, what Bryn puts in against what it receives as two bars, and each side's cash in hand year by year on one fixed scale, with the installation and every model figure behind one disclosure; the engine strip stays under the wide panel when both fit. **Export only – assumes no Bitcoin** is the hypothetical with no Bitcoin income: Bryn's £280,320 over 5 years from its extra export alone against what it puts in under each option (paid back in 19.6 months on the 50:50 CAPEX share, 39.2 months when it pays it all), anchored on the 50:50 CAPEX share, which the tab opens on and keeps softly marked, with the sum behind it along the bottom and Bryn's £91,684 half paid back in 19.6 months on a 5-year line; the two tabs share the chosen option. Opened as a plain file, `bryn_3d_sim.html?tab=dispatch`, `?tab=finance` or `?tab=export` starts on that tab and `?deal=card`, `?deal=open` and `?engine=max` start Finance at those stages (on the Atlas the address passes them on, so `/clients/bryn/?view=3d&tab=finance` opens on Finance). A second, teal badge on the compute container's spot by the LV cabinet opens the Compute Render full-screen (`?view=compute`): the yard south of the feed tank rebuilt in metres from imagery and the 13 October 2026 site photos, with the Green Hash 10 ft container in place and the two ways of placing its dry cooler (on the roof, or on the pad beside it), the LV cabinet at the west end of its compound by the Heras line with the transformer a walkway east of it, the cable route into the open trench, and every part carrying its source and what was assumed (click it); each a view of the same address, so the map page carries none of the models' weight |
| `/clients/kld/` | `kld_atlas.html` + `kld_hydro_chrome.html` + `kld_interactive.html` | KLD Atlas — Kinlochdamph 999 kW run-of-river hydro (Loch Damh, Wester Ross): site assets, the 11/33/132 kV network and the two SSEN connection options. A pulsing BLOX badge on the powerhouse opens the 3D Revenue Sim full-screen — a view of the same address, `?view=3d`, so the atlas page carries none of the model's weight |
| `/clients/ihn/` | `ihn_atlas.html` + `ihn_heat_chrome.html` + `heat_network_3d.html` | IHN Atlas — the IHN heat network: a still, daytime three.js satellite atlas of the district with the network main, the existing and proposed connections, the 11 kV route and the HNES blocks drawn on the imagery, and the 76 × 25 m plant room cut away under the block; four camera views (Overview, the Plant room as an amber call to action, EC1, EC2) with a caption that follows the view, a key, layers and a Council site-map overlay. A pulsing BLOX badge over the plant room opens the dispatch model, Heat Network 3D, full-screen — a view of the same address, `?view=3d`, with the same model file the investor pack serves, all data included, so the atlas page carries none of the model's weight |
| `/clients/reabold/west-newton/`, `/clients/reabold/reservoirs/` | `atlas/vendor/wn_infrastructure_map.html`, `atlas/vendor/reservoir_map.html`, copies of Reabold-Atlas's | Reabold's two maps: the West Newton infrastructure map and the UKCS reservoir atlas (a prototype; its gas flows show the bundled snapshot, as data.nationalgas.com's live feed can't be read from another site) |
| `/clients/citygate/` | `atlas/vendor/citygate_electricity.html`, a copy of Electricity-Analysis's | Citygate Church · Electricity Portrait |
| `/clients/bln/`, `/clients/bln/3d/` | `atlas/bln/` | BLN Atlas — the BLN powerhouse on the satellite imagery with the BLOX badge, and BLN 3D, the 3D render it opens (the model, a cutaway and the flythrough). Its public cover on the Atlas front page names it by its code only; behind the sign-in the pages may carry the site's details in full |
| `/team/keith-huntly/` | `kh_atlas.html` | Keith & Huntly Atlas — the decision page for the two Moray primaries SSEN has priced: a three.js satellite scene of each substation with SSEN's proposed works (joints, cable, metered RMU, the 33 kV diversion at Huntly) and Savills' siting options drawn on it, and a nine-step, keyboard-driven telling of the two budget estimates built for presenting to the team. It opens and closes on a **cost ladder** (find out / secure a place / connect / our own works) under a Both £2,170 · Huntly £1,240 · Keith £930 · Neither £0 switch (the minimum SSEN fees for feasibility studies), walks Keith's £150,000 for 1,999 kVA (1,300 kVA applied for) and Huntly's £110,000–£121,000 for 2.78 MVA over the scene with what each figure covers and what Savills inferred is left in the breakers, says plainly that the two figures are **not like for like** (Keith's has SSEN digging; Huntly's leaves the digging, civils, transformer and LV side to RenewaBlox and carries a 150 m diversion), names the gates before anything can be lodged (a landowner's Letter of Authority, and Savills' fees from its October 2025 proposal: £1,200 per DNO pre-application meeting, £7,500 to submit a connection application, land procurement TBC), and ends on three decision lines. Arrow keys step, `1`–`9` jump, `D` opens the site's detail drawer (scope, exclusions, the full capacity chart, the ranked plots, every open question), `S` the sources, `L` the camera and layer popover, `?` the key map; `?beat=n` or `?step=decide` deep-links a step, `?still` skips the flights. Unknowns stay unknown on the page: RenewaBlox's own works are "to be costed", never a number |
| `/team/moray/` | `moray_atlas.html` | Moray Cluster Atlas — the Keith & Huntly primaries (the only two green-headroom primaries in the Savills Moray screen): candidate plots, ownership areas, GSP saturation, the 33/132/275/400 kV network and the offshore wind landing on it |
| `/team/outreach/` | `atlas/team/outreach/index.html` | Outreach Strategy — RenewaBlox × tem's business outreach strategy (working draft of 2 October 2026) as one self-contained page: seven pages under a sticky tab rail, each on its own address (`#/`, `#/offer`, `#/linkedin`, `#/strategies`, `#/plan`, `#/compliance`, `#/toolkit`). Overview (the Bill X-ray hook, the five-channel map, the four plays, the first week's moves); Offer & targets (the edge, the claims and whose they are, the three limits, the segments and a **segment playbook** that gathers each segment's buyer, hook, LinkedIn angle, Demand Atlas source and opener on one card); LinkedIn (foundations to paid, with the funnel as a **live model**: its planning rates are sliders, and the paid stop rule follows them); Three strategies (Demand Atlas, Local Power with a generator **sizing calculator**, Borrowed trust); The plan (the 14 weeks on a chart with a **today line and live status** from the viewer's date, `?date=YYYY-MM-DD` to preview another day, and the tasks **filtered by owner**); Compliance (the two decisions, the checklist, the sources and how each was checked); Toolkit (every template and crew prompt, with the common fields **filled once** for all of them, length checks against the strategy's limits, search and a copy button on each) |
| **energy.renewablox.co.uk** | | |
| `energy.renewablox.co.uk/generators/` | `generator_demo_home.html` + `peaker_plant_3d.html` + `kld_interactive.html` | Generator Demo — the client pack for generators RenewaBlox is reaching out to, with tem, on its own address: a landing page that puts the two partners together (through tem and P442, a better PPA for renewables of all types; through RenewaBlox, any excess monetised by compute at the point of generation, drawn as an illustrative week of output split at the export limit), with a PPA check beside the headline (export MPAN and PPA end date, or a PPA statement), then sorts the models by the client's sector, each sector led by the same two steps (a better PPA through tem, then RenewaBlox), with the peaker under **Fuelled Renewables** as the **Peaker Plant model** (`peaker-plant/`, prices in **p/kWh**) and the hydro under **Stranded Renewables** as the **Run-of-River Hydro model** (`run-of-river-hydro/`). Each model's header carries its client-pack name, the pack bar names the sector and offers a "Talk to us" email link, and nothing is gated — the investor-portal blur is for investors |
| `energy.renewablox.co.uk/business/` | `business_demo_home.html` + `business_site_analysis.html` + `business_haas.html` + `heat_network_3d.html` | Business Electricity — RenewaBlox with tem, the client pack for businesses that buy electricity: a landing page that explains what's in a business bill and who works on which side of the meter (the animated BLOX wordmark marks RenewaBlox's side), sets out tem's supply (RED, priced against tem's UK renewable portfolio through its Rosso platform) and the RED Plus benefit (P442 exempt supply) as the foundation of every tier, then offers three tiers, each including RED and RED Plus and building on the one before: **Tier 1, Holistic Site Analysis** (`site-analysis/`, an interactive example report on an illustrative site built from tem's example quote — capacity, night-rate timing, power factor, levies and bands, with a running total), **Tier 2, Heat-as-a-Service** (`heat-as-a-service/`, an animated isometric site heated by Bitcoin miners through a large dry cooler or as space heaters) and **Tier 3, Heat Network** (`heat-network/`, Heat Network 3D, served with all of its data) |

The two investor demos are separate packs on purpose: NEM 3D was built for one
group of Australian investors, so it appears only in the pack they are sent to.
The Australia pack carries Peaker, Hydro and NEM 3D; Heat Network 3D and
Demand for Constraints 3D joined the main pack first and are not in the Australia
pack yet. They share the model copies and the landing-page design; each has its
own address and its own landing fragment. Old links in the form `?view=<key>`
still work: each pack's landing page forwards them to the model's own address,
and a key the pack doesn't have, such as
`?view=nem` against the main pack, stays on the landing page.

Five surfaces serve the same `peaker_plant_3d.html`, and they differ only in
framing — audience decides which link goes out:

| Surface | Chrome | Prices | Strike | Export price reads |
| --- | --- | --- | --- | --- |
| the investor packs, `…/peaker-plant/` | landing page + pack bar | £/MWh | £100, £40–£160 | "Price of electricity" |
| `/models/peaker-demo/` | none | £/MWh | £80, £50–£100 | "Export · DA + gDUoS" |
| `/models/peaker-plant/` | none | p/kWh (AD operators) | £100, £40–£160 | "Price of electricity" |
| `energy.renewablox.co.uk/generators/peaker-plant/` | landing page + pack bar | p/kWh (generators) | £100, £40–£160 | "Price of electricity" |

Standing the peaker up on its own did not take it out of the packs: they still
carry their Peaker card.

Those per-surface differences are declared by the page that frames the model and
applied by the model at load — `window.PEAKER_UNITS` for p/kWh, `window.PEAKER_CFG`
for the strike range and the export-price labels — so the HTML never forks. Both
default to the packs' behaviour when a surface declares neither. Tailor a
surface in `packs.py` (`PEAKER_PLANT_HEAD`, `PEAKER_DEMO_HEAD`, a view's `head`),
never by editing `peaker_plant_3d.html`.

The outreach strategy was the one native Streamlit app; it is now one
self-contained page, `atlas/team/outreach/index.html`, ported from it word for
word. Its live parts (the funnel, the sizing calculator, the plan's status and
chart, the Toolkit's fields) are drawn by the script at the end of the file from
the data at its top, each formula naming the Python lines it was ported from
(`outreach/sections.py`, `toolkit.py` and `ui.py`, in this repository's history).
It follows the viewer's light or dark setting until one is chosen with its toggle,
and its only outside requests are the fonts from Google Fonts.

Every other page is published as its file, or as files spliced together, with a
few exact-string patches made by the build: `atlas/pages.py` for the Atlas,
`build_energy_site.py` for the energy site, both reading the packs from
`packs.py`. Each patch names a string that must occur exactly once, so a
regenerated source that loses it fails the build instead of shipping a page that
half works. Change a page by changing its file here (or upstream, for the
copies), never the built output.

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
badge, the popup call-to-action rows and the overlay. The Atlas's build
appends it to `srv_atlas.html`, so the hand-maintained map file
stays pristine and the sim loads through `?view=3d` only when opened.
`bryn_atlas_3d_badge.html` does the same job for the Bryn Atlas, with two
badges: the BLOX logo on the proposed plot, which opens the 3D Site Model, and
a teal fan chip on the compute container's spot by the LV cabinet, 20 m west of
the plot, which opens the Compute Render (`?view=compute`); the data-centre and CHP
popups carry a CTA row for each.

The investor demos' model pages are copies of their upstream sources — refresh
them after an upstream rebuild:

| Copy in this repo | Used by | Source of truth |
| --- | --- | --- |
| `peaker_plant_3d.html` | the investor packs + generator pack + `/models/peaker-plant/` + `/models/peaker-demo/` | internal Atlas 3D build (`peaker_plant_3d_2.html`) |
| `kld_interactive.html` | the investor packs + generator pack + KLD Atlas | `Contracts/Kinlochdamph/Atlas/kld_live_3.html` |
| `nem_negative_price_atlas.html` | Australia pack | internal Atlas 3D build (`nem_negative_price_atlas_2.html`) |

The packs and the standalone peakers publish their model pages with small
presentation-only patches (a view's `head` in `packs.py`) — the peaker's
guided-tour view strip is hidden on every surface — so the files themselves stay
byte-for-byte copies of upstream. The generator pack goes one step further and
renames each model in its own header (`title` in `GENERATOR_VIEWS` in
`packs.py`, an exact-string swap of the `<h1>`): if an upstream rebuild changes
that heading the swap simply misses and the model keeps its own title, so check
the pack after refreshing a copy. The KLD Atlas does the same for
`kld_interactive.html`: the build appends `kld_hydro_chrome.html`
(design-system overrides plus the "Atlas" control back to the map). **Never edit
`kld_interactive.html` to add atlas-specific chrome** — it is served on four
surfaces, and a "back to the KLD Atlas" button baked into it would appear,
pointing at the wrong place, in the investor packs and the generator pack.

## The site-atlas pattern

The SRV, KLD, IHN and Bryn atlases are deliberately the same shape, so a new site
can be stood up by copying any of them (its entry in `CLIENT_PAGES` and its
function in `atlas/pages.py`, and a row for its client in Supabase):

* one address, two views — the atlas by default (a Leaflet map for SRV, KLD and
  Bryn, a still three.js satellite scene for IHN), its 3D model at `?view=3d`,
  each a full-window page (Bryn adds a third view, `?view=compute`); the sign-in
  serves the view's file at the page's own address, so a link to a view is the
  address with its `?view=`;
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
plain file, Bryn's model page finds the map page by relative link
(`bryn_atlas.html`), and on the Atlas by its address (`/clients/bryn/`, set by
the build); the map page's route to the model lives in the badge layer, which
only the build appends.

The gateways and the models' "Atlas" pills navigate through `rbxGo(url)`,
written for the sandboxed frame without allow-top-navigation that the pages
were first served in: it creates an anchor in the parent document and clicks it,
which the browser attributes to the parent and so navigates the page in place;
if even that is refused it rewrites the parent's history entry and reloads it,
and as a last resort opens the destination in a new tab. On the Atlas each page
is the top window, so the build puts a guard at the top of `rbxGo` that
navigates in place by `location.assign` when the page is not framed
(`top_level_nav` in `atlas/pages.py`); the files here keep the frame-safe code,
so they still work framed.

`heat_network_3d.html` is served on four surfaces (the investor demo and portal,
the IHN Atlas and the business pack): **never bake atlas chrome into it** — the IHN "Atlas" pill lives in
`ihn_heat_chrome.html` and is appended by the build, exactly as
`kld_hydro_chrome.html` is for `kld_interactive.html`.

`investor_demo_home.html`, `investor_demo_aus_home.html`,
`generator_demo_home.html` and `business_demo_home.html` are hand-authored
(wordmark and scene thumbnails inlined as data URIs) — edit them directly. Each
is a fragment (`<style>` + one `<div>`, no `<html>`/`<body>`, no scripts, every
class prefixed `rbx-`, and a `.stApp` rule for the page background, which the
builds give a wrapper of that class); each build wraps it in a document of its
own and turns its `?view=<key>` links into the pack's addresses, failing on a
key it doesn't know. The main landing page groups its
models into delivery windows (2026/27: Peaker and Hydro; 2027 & beyond: Heat
Network plus a slot for the next model, whose delivery may run to 2029/30) with
CSS-only tabs — radio inputs and
`:checked` selectors, as the fragments carry no scripts. The first window is the
CSS default rather than a `checked` attribute (the fragments were first rendered
by a React tree that snapped a `checked` radio back after a click).
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
server logic and no secrets, published as a static site at
**energy.renewablox.co.uk**: a client email reads better, and sits better with
spam filters, when its links are on the sending domain.

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
it on a push to live that changes one of its inputs (`energy_inputs.txt`;
`netlify.toml`, project `renewablox-energy`). It reads
the packs through **`packs.py`**, as the Atlas's investor packs do: each view's
file, labels and patches (the model renames and the peaker's p/kWh) are defined
there once, so add or rename a view there. The build wraps each landing fragment
in a document of its own, turns every `?view=<key>` link into a real address
(and fails if a fragment links to a view it doesn't know), and puts each model
under a slim pack bar, in an iframe of the patched model at `<slug>/model.html`
(the Atlas's packs share the bar). An old-style link with only its domain
swapped (`energy.renewablox.co.uk/?view=site`) is forwarded from the welcome
page to its page: the two packs' view keys never collide, and the build checks
that they don't.
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
the fragment's `<!--save-form-->` stand-in. **Netlify Forms** receives
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

## atlas.renewablox.com — the RenewaBlox Atlas

The Atlas is built from `atlas/` by **`atlas/build.py`** into `atlas/site/`
(git-ignored). The `renewablox-atlas` Netlify project runs the build on a push
to live that changes one of its inputs (`atlas/inputs.txt`; `atlas/netlify.toml`,
base directory `atlas/`), then the gates'
tests (`atlas/tests/gates.test.mjs`), and deploys only if both pass. Nothing of
it is hosted anywhere else, and the build fails if any page points at a
`streamlit.app` address.

| Address | Page | Source | Who can open it |
| --- | --- | --- | --- |
| `/` | the Atlas front page, with its Client Atlas section | `atlas/root/index.html`; the section is `atlas/front/clients.html`, put between its marker comments by the build | anyone |
| `/investors/` | the Investor Atlas preview, pointing to the Wix investor portal | `atlas/root/investors/index.html` | anyone |
| `/market/`, `/market/map/` | the Market Atlas page, and the map it frames | `atlas/root/market/index.html`, `atlas/vendor/client_atlas_v2.html` | anyone |
| `/clients/bln/`, `/clients/bln/3d/` | BLN Atlas and BLN 3D | `atlas/bln/` | the sign-in: the team, and the addresses listed for `bln` |
| `/investors/demo/`, `/investors/australia/`, `/models/` | the public investor packs and the standalone peakers | `atlas/pages.py`, from the files at the root of this repository | anyone with the link |
| `/investors/portal/`, `/investors/portal/atlas/` | the Investor Portal pack and the Investor Atlas | `atlas/pages.py`, `atlas/vendor/investor_atlas_v3.html` | anyone with the address: the Wix investor portal's members area links to it |
| `/clients/<code>/…` | the client atlases | `atlas/pages.py` | the sign-in: the team, and the addresses listed for `<code>` |
| `/team/…` | the team's pages | `atlas/pages.py`, `atlas/team/` | the sign-in: the team only |

Pages "anyone with the link" can open ask not to be indexed; every page behind
a gate is served with `noindex` too.

`atlas/root/` holds the Atlas site's own files, served at the root as they are,
with their header rules in `atlas/root/_headers`; the build adds the investor
portal's rules after them (`site_headers` in `atlas/build.py`) in the site's
`_headers`, and the pages behind the sign-in take theirs from `EDGE_CSP`. Netlify applies every rule that matches a path and joins a header
two rules set, so each page takes its Content-Security-Policy from one rule
only, and the build checks that it does. Netlify's header rules don't reach a
response that passes through an edge function, so the gated pages' headers are
set by their gates, from the policies in `atlas/pages.py` and `EDGE_CSP` in the
build (which writes them to `atlas/netlify/edge-lib/pages.js`, git-ignored, for
the gates to import). The two brand fonts, Telegraf and Garet, are licensed for
the website, so they are not in this public repository: the build fetches them
from renewablox.com's own font files and checks their hashes (`FONTS`).

**Pages copied from other repositories.** `atlas/vendor/` holds the five pages
built elsewhere: the Market Atlas and the Investor Atlas (Eunice-Platform's
`client_atlas_v2.html` and `investor_atlas_v3.html`), Reabold's two maps
(Reabold-Atlas) and Citygate's portrait (Electricity-Analysis). To take newer
copies:

    python atlas/build.py --sync     # copies each from its repository's main branch into atlas/vendor/
    python atlas/build.py            # then look at what changed, and commit the copies

**The two maps** (`MAPS` in the build). The Market Atlas used to be framed from
`renewablox-client-atlas-v3.streamlit.app` and the Investor Atlas from
`renewablox-investor-atlas-v3.streamlit.app`, whose wrappers read `?view=`,
`?site=` and `?theme=` (and, for the Investor Atlas, `?present=1`) from the
address, checked each against a pattern and handed them to the page as
`window.__ATLAS_INIT__`. Here the page does that itself (`map_init` in the
build, with the same patterns), and the market page passes its own address on
to the map, so a shared link such as `/market/?view=hydro&theme=night` opens
there. The build also points each map's "Copy link" at its address here, and
gives every link out of a map `target="_blank"`, as a link followed inside a
frame would be refused.

**The sign-in** (`atlas/netlify/edge-functions/atlas-gate.js`). Every request
under `/clients/` and `/team/` passes through it. A visitor without a session
is sent to `/access/`, signs in with Google through RenewaBlox's Supabase
project (`renewablox-crm`, the same sign-in the CRM uses) and comes back to the
page they asked for. What they may open is Supabase's to say:
`public.atlas_my_access()`, asked with the visitor's own token, answers `*` for
an active CRM team member (`team_members`) and otherwise the client codes listed
for their address in `public.atlas_access`. `/clients/<code>/…` opens to `*` or
`<code>`; `/team/…` to `*` only; `/clients/` and `/team/` list what the visitor
may open. The answer is asked again at the first page opened after ten
minutes, so a row removed in Supabase shuts a client out within minutes, with
no redeploy. A page's views are routed here too: `/clients/srv/?view=3d` serves
the view's file at the page's own address. Anything missing or wrong fails
closed. To share a page with a client (an admin's job, by the table's row
security), add a row for their Google address in Supabase's SQL editor:

    insert into public.atlas_access (email, client, note)
    values ('name@example.com', 'srv', 'SRV Atlas for the farm manager');

The codes are `srv`, `srv-contractor`, `bryn`, `kld`, `ihn`, `reabold` (both
Reabold maps) and `citygate`; the address is stored in lower case. Google is
the only sign-in the Supabase project offers, so a client needs a Google
account for the address listed (a Google Workspace address, or a Gmail one);
anyone else's sign-in reaches a page saying nothing is shared with them.

**The investor portal** (`/investors/portal/`) isn't gated on the Atlas. The way
in is the Wix investor portal at renewablox.com/invest (registration and the
investor declaration), whose members-area buttons link to
`https://atlas.renewablox.com/investors/portal/` and
`https://atlas.renewablox.com/investors/portal/atlas/`. Its pages ask not to be
indexed, and their header rules (`site_headers` in `atlas/build.py`) let the Wix
site frame them. Anyone given the address can open them, and the files are
public in this repository.

**BLN** (`/clients/bln/`, client code `bln`) is behind the sign-in, so its pages
may carry the site's details in full; old `/bln/` links redirect there
(`_redirects`, written by the build). What stays public is its card on the
front page (`atlas/front/`), which keeps the anonymity checks it was built with
(see the docstring of `atlas/build.py`): no word that names or places the site,
no postcode or grid reference, no image metadata. The words live outside this
public repository, in `atlas/.names` (git-ignored) or the `ATLAS_NAMES`
environment variable; a build on Netlify refuses to run without them. They are
names that rightly appear elsewhere on the site, so Netlify's own scan for
secret values leaves `ATLAS_NAMES` out (`SECRETS_SCAN_OMIT_KEYS` in
`atlas/netlify.toml`), or it would fail every build.

Build and look at it locally:

    python atlas/build.py
    python -m http.server 8901 -d atlas/site      # then open http://localhost:8901/
    node atlas/tests/gates.test.mjs               # the sign-in, against a stand-in Supabase

A plain server doesn't run the edge functions, so locally the gated pages open
without a sign-in and their views are files of their own
(`/clients/srv/3d.html`, `/clients/bryn/bryn_3d_sim.html`).

## ai.renewablox.com — RenewaBlox's AI tools

The in-house tools live on one domain of their own, built from `ai/` by its own Netlify
project, separate from the energy site. For now that is OSCAR; whether Atlas joins it isn't
decided.

| Address | Page |
| --- | --- |
| `/` | the home page: OSCAR, in the Atlas's house style (`ai/index.html`): the Atlas's topbar, navy hero and footer, with OSCAR's miner catalogue charted where the Atlas has its map, OSCAR's card (its halving schedule as the art) beside a card that leaves room for more tools, and its three cards of inputs |
| `/oscar/` | OSCAR, the site model, served exactly as the team's own file (`ai/oscar.html`) |

The home page's figures are OSCAR's own (the eleven miners, the market models, the halving
schedule), written into the page: when a newer `ai/oscar.html` changes them, change the home page
with it.

`/atlas/` still answers by proxy from Atlas's own Netlify project (`renewablox-atlas`,
atlas.renewablox.com), with the root-relative links Atlas's pages may use (`/investors/`,
`/market/`, `/portal/`) sent back under `/atlas/`, but nothing on the site links to it.

The home page and the 404 page wear the Atlas's brand from the Atlas's own files: `ai/build.py`
copies its stylesheet (`atlas.css`), wordmarks and icons from `atlas/root/` and fetches the two
brand fonts from renewablox.com's own files, against the same hashes as the Atlas's build, so
the two sites can't drift apart (so `ai/inputs.txt` lists those files beside `ai/`, and a change
to them rebuilds the site). The build writes `ai/site/` (git-ignored) and checks three things that would
otherwise break quietly: every input id a saved OSCAR scenario can hold is still on the page
(`SCENARIO_IDS`, which only ever grows), the home and 404 pages load nothing from elsewhere,
and OSCAR's Content-Security-Policy in `ai/netlify.toml` allows every origin the page reaches
and no other. `ai/netlify.toml` holds the rest: the Atlas proxy, the policies (the home page
loads only from the site itself) and `noindex` (with a `robots.txt` that disallows everything):
these are tools for the team and the clients they are sent to, not for search engines.

**OSCAR** (Optimising Site Capacity & ASIC Revenue) is the team's own self-contained page,
"a simple planning tool for Bitcoin mining site economics (GBP)", served byte for byte as it is
and keeping its own look: replace `ai/oscar.html` with a newer file to update it, and the build
says if the newer file reaches a source its policy doesn't allow. What a site earns when its
power goes into Bitcoin mining, energy markets (export, demand turn-up, the capacity market) and
heat off-take, what it costs, how the revenue is shared between RenewaBlox and the client, and
when the CAPEX comes back:

* **Inputs** in three cards (Miner & Market Data, Site Inputs, Modelling assumptions), then the
  revenue share structure: who funds the CAPEX (RenewaBlox, the client, 50/50 or a custom
  split) and the revenue mode (a fixed CAPEX recovery period, a share from the start, or an
  initial and a remainder split), over the contract length. The miner list holds eleven
  MicroBT and Bitmain models, with overclock profiles for the Whatsminers and the Antminer S21 XP
  Hydro; Phase 2 adds a second block of power partway through the contract.
* **Two views**, Expert and Client, and light and dark themes, chosen in the header and
  remembered in the browser (`uiMode` and `theme` in local storage).
* **Live inputs**: the Bitcoin price in GBP from CoinGecko and the 30-day average network hash
  rate from mempool.space (Blockchain.com if that fails), refreshed on opening and by "Refresh
  live inputs". CoinGecko is called directly; each hash-rate source is called directly first
  and, if a browser or network refuses that, through three public CORS proxies in turn
  (allorigins.win, cors.isomorphic-git.org, codetabs.com), which the policy allows for that reason.
* **Outputs**: headline figures, the cost summary, the revenue share, the annual and p/kWh
  comparisons against the site's existing power revenue, the cash-flow timeline, the annual
  revenue breakdown, BTC value against a treasury hold, and BTC rewards, drawn on canvas.
* **Scenarios** are saved in the browser (`scenarios` in local storage), loaded back into the
  inputs, opened in a new window as a link that carries the whole scenario (`?scenario=`),
  compared in a table and exported as CSV; "Export PDF (Print)" prints the page. As the file
  stands, saving with no scenario chosen in the list replaces the first one saved (the list's
  empty choice reads as 0), so the list holds one scenario at a time.

Deploy: the Netlify project is `renewablox-ai` (renewablox-ai.netlify.app). Link it to this
repository with production branch `live` and its **base directory set to `ai`** (it then reads
`ai/netlify.toml`, not the root one), add `ai.renewablox.com` as its domain, and point a CNAME
record `ai` at `renewablox-ai.netlify.app` at the renewablox.com DNS host, as for `atlas.` and
`crm.`. The `/atlas/` proxy targets `https://atlas.renewablox.com`, so that domain must resolve.
Netlify then builds on a push to live that changes one of its inputs (`ai/inputs.txt`). The project was created private (a team login on every
deploy, production included); the energy and Atlas projects ask for one on previews only.

Build and look at it locally (`ai/oscar.html` also works opened straight from the folder; the
home page needs the build's brand files):

    python ai/build.py
    python -m http.server 8900 -d ai/site      # then open http://localhost:8900/

## Run locally

Every site builds with Python's standard library alone (3.12); the Atlas's gate
tests need Node 22:

    python build_energy_site.py && python -m http.server 8800 -d energy_site   # energy.renewablox.co.uk
    python atlas/build.py && python -m http.server 8901 -d atlas/site           # atlas.renewablox.com
    node atlas/tests/gates.test.mjs                                             # the Atlas's sign-in
    python ai/build.py && python -m http.server 8900 -d ai/site                 # ai.renewablox.com

The dev container (`.devcontainer/`) builds the Atlas and serves it on port 8901.

## Deploy

Three Netlify projects build from this repository, all from `live` (`main` publishes
nothing), each only when that site's own files change (see "Builds and credits" below):

| Project | Domain | Base directory | Branch | Configured by |
| --- | --- | --- | --- | --- |
| `renewablox-atlas` | atlas.renewablox.com | `atlas` | live | `atlas/netlify.toml` |
| `renewablox-energy` | energy.renewablox.co.uk | the root | live | `netlify.toml` |
| `renewablox-ai` | ai.renewablox.com | `ai` | live | `ai/netlify.toml` |

`renewablox-atlas` needs these environment variables (Project configuration →
Environment variables; `ATLAS_NAMES` is read by the build, the rest by the edge
functions, so their scope must include Functions; a change needs a redeploy):

| Variable | Value |
| --- | --- |
| `ATLAS_NAMES` | the names the clients' public covers on the front page must never carry, comma-separated; marked secret |
| `SUPABASE_URL` | `https://enghoowpiwopsfabfurx.supabase.co` (renewablox-crm) |
| `SUPABASE_PUBLISHABLE_KEY` | renewablox-crm's publishable key (Supabase → Project settings → API keys) |
| `ATLAS_SESSION_SECRET` | 32 or more random characters, marked secret; changing it signs everyone out |

And in Supabase (renewablox-crm → Authentication → URL Configuration → Redirect
URLs): `https://atlas.renewablox.com/access/callback`, without which Supabase
sends the browser to the CRM and the sign-in can't finish.

After the first deploy with the sign-in, check that no other spelling of a gated
address reaches a page. Netlify picks edge functions by the address as sent but
serves a file after folding a run of slashes, which is why the sign-in routes by
pattern (`config` in `atlas-gate.js`) and sends every spelling to its one form.
Each of these should answer 301, never 200:

    for p in //clients/srv/ //team/outreach/ //clients/bln/; do
      curl -s --path-as-is -o /dev/null -w "%{http_code} $p\n" "https://atlas.renewablox.com$p"; done

The Wix investor portal's members-area buttons point at
`https://atlas.renewablox.com/investors/portal/` (the pack) and
`https://atlas.renewablox.com/investors/portal/atlas/` (the Investor Atlas). A
button that opens a new tab is the best home for a full-screen 3D scene; the
pack also works inside a Wix "Embed a site" element.

The pages' old Streamlit addresses, and where each now is (the query carries
over as it is):

| Was | Now |
| --- | --- |
| `renewablox-client-atlas-v3.streamlit.app` | `atlas.renewablox.com/market/` |
| `renewablox-investor-atlas-v3.streamlit.app` | `atlas.renewablox.com/investors/portal/atlas/` |
| `investor-demo.streamlit.app/?view=<key>` | `atlas.renewablox.com/investors/demo/?view=<key>`, forwarded to the model's page |
| `investor-demo-aus.streamlit.app` | `atlas.renewablox.com/investors/australia/` |
| `investor-insight.streamlit.app/?view=<view>` | `atlas.renewablox.com/investors/portal/?view=<view>`, forwarded to the model's page |
| `peakerplant-3d.streamlit.app` | `atlas.renewablox.com/models/peaker-plant/` |
| `ihn-atlas.streamlit.app/?view=3d` | `atlas.renewablox.com/clients/ihn/?view=3d` |
| `bryn-atlas.streamlit.app/?view=<view>` | `atlas.renewablox.com/clients/bryn/?view=<view>` |

The rest were never given a public address of their own; the Pages table above
lists where each now lives.

### Builds and credits

Netlify charges 15 credits for each successful production deploy. Deploy
previews, branch deploys, failed builds and skipped builds cost nothing, Netlify
Forms are free, and the gates' edge functions are billed as ordinary web requests
(2 credits per 10,000). So what costs is a build of a production branch, and
each project builds only when its own files change:

* **Work on `main`, publish from `live`.** No project builds from `main`; merge
  into `live` when a change should go out, and a push of several commits builds
  once.
* **On `live`, a push that changes nothing a site is built from skips that
  site.** Each project's ignore command (`tools/netlify-ignore.sh`) compares the
  push with the project's last build over the site's list (`energy_inputs.txt`,
  `atlas/inputs.txt`, `ai/inputs.txt`) and cancels the build if nothing on it
  changed, so a README, tools or workflow change builds nothing, and a change
  to one site doesn't rebuild the others. A build fails if it reads a file of
  the repository its list doesn't cover (`site_inputs.py`), so a list can't fall
  behind: add the file to the list the error names.
* **It builds whenever it can't tell**: a project's first build, "Clear cache and
  deploy", or "Trigger deploy" of a commit already built. A build hook always
  builds.
* `[skip netlify]` in the last commit's message skips a push that does change a
  site, for publishing it with a later push instead.
* Set a project's environment variables before its first build: changing them
  takes a redeploy, which is another production deploy.
