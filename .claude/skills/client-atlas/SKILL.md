---
name: client-atlas
description: Playbook for putting a client's site atlas on atlas.renewablox.com, whether moving a Streamlit client atlas ("next up is xyz-atlas.streamlit.app") or adding a new site. Covers the uniform opening map, the front-page card under the site's code, the checks, the owner's steps and the one paid build. Follow it for every client atlas without waiting to be briefed.
---

# Client atlas playbook

The owner's standard is **uniformity**: every client atlas looks and works the same, so a client who has seen one
knows them all. Keep to it unasked. When a source page differs from the standard (its own panel, labels, lines,
legend, a different badge), bring it to the standard rather than carrying the difference over, and say what you
left out.

## The standard

**Address.** `/clients/<code>/`, the site's three-letter code in lower case (`bln`, `bry`, `srv`, `kld`). Each 3D
model is a view of that address: `?view=3d` for the main model, others by name (SRV's `?view=siting`). An address a
client may already hold redirects (`CLIENT_REDIRECTS` in `atlas/pages.py`, e.g. `/clients/bryn/` → `/clients/bry/`).

**Opening page.** Always the shared map, never the source's own map: `atlas/client_map/map.html`, filled in from the
site's entry in `CLIENT_MAPS` in `atlas/pages.py` and served by `client_map("<code>")` in `client_pages()`.
- The RenewaBlox bar: `kick` is "<what is proposed, or the scheme> · <CODE> Atlas" ("Proposed compute load bank ·
  SRV Atlas", "999 kW run-of-river hydro · KLD Atlas"); `place` is "<site>, <place>[, <postcode>]".
- The site on Esri satellite imagery, opening on the site itself (SRV: zoom 18.5 on the yard; KLD: 17 on the
  powerhouse). Prefer a whole zoom: in-between zooms leave hairline seams between imagery tiles.
- One BLOX badge per view, its pill at full length ("3D Dispatch Sim", "3D Revenue Sim"; `short` for phones). Put
  the chip on, or just beside, the thing the view is about. Use `side: "right"` or `anchor` only to keep two
  badges apart. The build fails unless the badges and the page's views match one for one.
- Nothing else: no labels, numbered pins, shapes, cable or grid lines, popups, layer switches, legends, briefing
  panels, caveat boxes or extra buttons. Don't cut or patch the source's map to get there; leave it in the repo for
  its Streamlit app and take it out of `atlas/inputs.txt` once nothing reads it.

**Owner's exceptions.** Only the owner can let a site keep its own opening page (IHN, for its heat network scene). Such
a page still takes the family's bar and badge: the RenewaBlox bar from `client_bar()` (`atlas/client_map/bar.html`,
the file the shared map takes it from) in place of the page's own header, a header's buttons going (the badge opens
the model; anything else moves into the page's own controls, keeping any id its script looks up), and the BLOX
badge restyled to the shared look (the 44 px roundel inside a 2.5 px white border, 49 px across and centred on its
46 px box and its pulse; a one-line pill; the arrow towards the chip). Check the page's `box-sizing`: IHN's is
border-box, so its chip needs `box-sizing:content-box` to come out the same size. See `ihn_atlas()` in
`atlas/pages.py`. The card is the same as any other site's.

**Views.** The model page as it comes from upstream, with only the patches `pages.py` needs: a title of
"<CODE> Atlas — <view name>", `top_level_nav`, and an "Atlas" control back to the map. Never bake atlas chrome into
a model that's shared with other pages (`kld_interactive.html` and `heat_network_3d.html` serve four surfaces): put
it in a chrome file the build appends.

**Security policy.** `CLIENT_CSP` in `pages.py`: the site's folder (`/clients/<code>/`) uses `CLIENT_MAP_CSP`, and
each model file has an entry of its own (`/clients/<code>/3d.html`) with what that model needs.

**Front-page card.** Goes in `atlas/front/clients.html`, mirrored byte for byte into `atlas/root/index.html` between
the client atlas markers. It comes after the existing site cards and before the "This could be your site" card.
- Named by code only: eyebrow = the technology ("Anaerobic digestion", "Run-of-river hydro"), h3 = the CODE.
- No name, place, postcode, grid reference, estate, operator, person or supplier anywhere in it, alt text
  included.
- Cover `atlas/front/<code>-cover.jpg`:
  - a frame of the site's own 3D model in daylight, with every label, HUD, panel and lettered 3D sign hidden;
  - 1280×720, progressive JPEG, quality 82, no EXIF or ICC (Pillow);
  - look at it before using it, and make it differ from the other covers.
  - How the earlier covers were shot: serve the repository root, open the model in Playwright's Chromium with
    `--enable-unsafe-swiftshader --use-angle=swiftshader`, use the page's own view hooks (`window.__atlas`,
    `window.__SITING__`, `window.__hn` on Heat Network 3D), hide the DOM except the canvas, hide meshes textured with
    a `CanvasTexture`, and read the canvas back with `toDataURL` (SwiftShader is too slow for `page.screenshot` at
    1920×1080). A renderer made without `preserveDrawingBuffer` (Heat Network 3D) reads back blank: ask for it by
    wrapping `getContext` in an init script, or read inside a `requestAnimationFrame` callback, straight after the
    page's own render.
- Paragraph in the house voice, one or two sentences: the scheme's size, its limit or constraint, and what BLOX does
  there. Trace every figure to the site's own pages. Leave out any figure that is commercially confidential, or that
  gives one away (a heat network's demand, or the share of it BLOX meets: IHN's card gives no figures at all); when
  unsure, leave the figure out and say so to the owner.
- If the owner supplies the cover, use it as given: trim only empty margin, frame it whole at 16:9 (carry its own
  ground out to the sides rather than crop the subject), save it as above and look for text or metadata all the same.
- Four bullets on what the visitor finds: the map with its badge(s) first, then each view.
- Buttons: "Open <CODE>" → `/clients/<code>/`, and "3D model" → `/clients/<code>/?view=3d`.
- The grid is three across. The invitation card stretches to fill its row when it would sit short of one (the
  rules are in the `<style>` at the top of `clients.html`); check that the last row looks right.

## Steps

1. Read the site's Streamlit app on `main` (`git show origin/main:app_<x>.py`) for its views and files, and its
   current entries in `atlas/pages.py` (`client_pages`, `CLIENT_PAGES`, `CLIENT_CSP`) and `README.md`.
2. Run two background agents together while you work:
   - one gathers the card's facts, each with a verbatim quote from the site's pages;
   - one shoots 4–6 cover candidates.
3. Add the `CLIENT_MAPS` entry and serve the map from `client_map("<code>")`. Set the views and CSP. Add the card,
   the cover and the root mirror.
4. README:
   - the site's row in the Pages table;
   - a row in the Streamlit table (`<x>-atlas.streamlit.app/?view=<view>` →
     `atlas.renewablox.com/clients/<code>/?view=<view>`);
   - the client code in the `atlas_access` paragraph;
   - a paragraph on the code beside the BRY/SRV ones (the names it needs in `ATLAS_NAMES`, how the cover was taken).
5. Verify all of it, every time:
   - `ATLAS_NAMES='<every existing word>,<this site's words>' python3 atlas/build.py` passes. The site's words are
     its name, farm or estate, village, town, postcode district, operator and nearby places. Then put one word into
     the card, confirm the build fails, and put it back.
   - `node atlas/tests/gates.test.mjs` passes.
   - In Playwright, against `python3 -m http.server -d atlas/site` (locally the gated pages open with no sign-in):
     - The map at 1440×900 and 390×844 shows the bar, the imagery and the badges only, with no console errors.
       Every chip and pill starts on screen at phone, landscape-phone (640×360), tablet and desktop sizes.
     - A badge reached with Tab opens its view on Enter and on Space, once.
     - Each badge opens `?view=<v>`; locally that reloads the map, so open `/clients/<code>/<file>.html` to see a
       view.
     - Compare it side by side with SRV's map: the chrome must match.
     - The front-page section at 1600, 1100, 1000 and 390 wide: no horizontal scroll, and the cover loads at
       1280 px.
   - An independent review (a workflow of reviewers plus skeptics) before the paid push. Fix what it confirms.
6. Credits: each Atlas deploy costs 15 credits. Netlify builds a push unless its head commit says
   `[skip netlify]`, or nothing on the site's list (`atlas/inputs.txt`) changed since the site's last *successful
   build*, not since the previous push. So:
   - push work in progress with `[skip netlify]` on every commit, README and `.claude/` ones included: once one of
     them has touched an Atlas input, any later push without it builds and deploys everything since the last build;
   - make the one push without it when the work is reviewed and ready to go live. Netlify finds the tag anywhere in
     the head commit's message, so that commit must not quote it, even to explain it (say "the skip tag");
   - confirm on the live site (`curl` the front page for the cover) and in Netlify that only the Atlas built.
7. Tell the owner, short and in this order:
   - that it's live, with the link;
   - what changed;
   - their steps:
     - (a) add the site's words to `ATLAS_NAMES` in Netlify;
     - (b) add `atlas_access` rows (`'<email, lower case>', '<code>', '<note>'`);
     - (c) send the client the link and retire the Streamlit app;
   - anything left over, as one-line offers.

## Where the sites stand

| Code | Opening map | Front-page card |
| --- | --- | --- |
| BLN | its own (`atlas/bln/index.html`): labels, caveat, an extra "3D render" button | yes |
| BRY | its own (`bryn_atlas.html` + badge layer): numbered labels, a teal fan chip, caveat | yes |
| SRV | shared | yes |
| KLD | shared | yes |
| IHN | its own three.js scene, by the owner's word, under the shared bar and badge | yes |

BRY and BLN are off the standard and wait on the owner's word. A site whose source opens on something other than
a map gets the shared map unless the owner says otherwise (as for IHN); ask. Update this table when a site changes.
