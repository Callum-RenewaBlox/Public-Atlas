# RenewaBlox — Public Atlas

Public-facing, self-contained site tools built by RenewaBlox. Each app is a thin
Streamlit wrapper around a standalone page — a Leaflet map, or a three.js scene —
with all data embedded and no database and no secrets. Because this repo is
public, the apps deploy as **public apps** on Streamlit Community Cloud
(unlimited, free).

## Apps

| App | Page(s) | What it shows |
| --- | --- | --- |
| `app_srv_atlas.py` | `srv_atlas.html` | SRV Atlas — Scrivelsby (Home Farm AD) electrical site survey: geolocated assets, site photos and grid context (LN9 6JB) |
| `app_kld_atlas.py` | `kld_atlas.html` | KLD Atlas — Kinlochdamph 999 kW run-of-river hydro (Loch Damh, Wester Ross): site assets, the 11/33/132 kV network, the two SSEN connection options, and an interactive 3D model of the powerhouse |
| `app_moray_atlas.py` | `moray_atlas.html` | Moray Cluster Atlas — the Keith & Huntly primaries (the only two green-headroom primaries in the Savills Moray screen): candidate plots, ownership areas, GSP saturation, the 33/132/275/400 kV network and the offshore wind landing on it |
| `app_srv_3d_sim.py` | `srv_3d_sim.html` | SRV 3D Sim — the Scrivelsby Peaker: a three.js model of the Home Farm AD site with a half-hourly dispatch simulation of the 350 kW switchable block over a real metered year, and the site survey photography on every asset pin |
| `app_investor_demo.py` | `investor_demo_home.html` + `peaker_plant_3d.html` + `kld_interactive.html` + `nem_negative_price_atlas.html` | Investor Demo — a landing page for prospective investors that packs the interactive 3D models: Peaker Plant 3D (the peaker business model as a living site, `?view=peaker`), Hydro 3D (the KLD powerhouse and its in-room data centre, `?view=hydro`) and NEM 3D (mining economics across the Australian NEM, `?view=nem`) |

Each app reads its HTML inline and renders it with `st.iframe`, so a redeploy
always serves the current map. The one exception is the Investor Demo's landing
page: an HTML fragment rendered in the parent page with `st.markdown`, because
Streamlit sandboxes component iframes without `allow-top-navigation`, so links
inside one can never drive the app's `?view=` navigation.

## Generated files

`kld_atlas.html`, `moray_atlas.html` and `srv_3d_sim.html` are built, not
hand-edited. Each builder re-skins its hand-authored source in the shared
RenewaBlox design system (petrol brand tokens, Inter, glass panels, brand bar)
and re-uses the source's data and vendored payloads byte-for-byte:

| Output | Builder |
| --- | --- |
| `kld_atlas.html` | `Contracts/Kinlochdamph/Atlas/build_kld_atlas.py` |
| `moray_atlas.html` | `Contracts/Savills Earth/Atlas/build_moray_atlas.py` |
| `srv_3d_sim.html` | `Contracts/Scrivelsby Farm Ltd/Atlas/build_srv_3d_sim.py` |

The Investor Demo's model pages are copies of their upstream sources — refresh
them after an upstream rebuild:

| Copy in this repo | Source of truth |
| --- | --- |
| `peaker_plant_3d.html` | internal Atlas 3D build (`peaker_plant_3d_2.html`) |
| `kld_interactive.html` | `Contracts/Kinlochdamph/Atlas/kld_interactive.html` |
| `nem_negative_price_atlas.html` | internal Atlas 3D build (`nem_negative_price_atlas_2.html`) |

The app serves the model pages with small presentation-only CSS patches
(`PATCH_CSS` in `app_investor_demo.py`) — e.g. the peaker's guided-tour view
strip is hidden for investors — so the files themselves stay byte-for-byte
copies of upstream.

`investor_demo_home.html` is hand-authored (wordmark and scene thumbnails
inlined as data URIs) — edit it directly. It is a fragment (`<style>` + one
`<div>`, no `<html>`/`<body>`, no scripts, every class prefixed `rbx-`); the
app strips blank lines before handing it to `st.markdown`, and any new link in
it needs an explicit `target="_self"` or Streamlit will retarget it to a new
tab.

The SRV builder also lifts the 12 survey photographs out of `srv_atlas.html`,
re-encodes them to WebP and wires them onto the 3D scene's asset pins, so the
two SRV apps can never disagree about the site record — rebuild it after any
change to the 2D atlas's photos or captions. It needs Pillow.

## Run locally

    pip install -r requirements.txt
    streamlit run app_srv_atlas.py
    streamlit run app_kld_atlas.py
    streamlit run app_moray_atlas.py
    streamlit run app_srv_3d_sim.py
    streamlit run app_investor_demo.py

## Deploy

Deploy on Streamlit Community Cloud pointing at the app's `app_*.py` entry file.
This repo is public, so apps deploy as public apps — unlimited and free.
