# RenewaBlox — Public Atlas

Public-facing, self-contained site tools built by RenewaBlox. Each app is a thin
Streamlit wrapper around a standalone page — a Leaflet map, or a three.js scene —
with all data embedded and no database and no secrets. Because this repo is
public, the apps deploy as **public apps** on Streamlit Community Cloud
(unlimited, free).

## Apps

| App | Map | What it shows |
| --- | --- | --- |
| `app_srv_atlas.py` | `srv_atlas.html` | SRV Atlas — Scrivelsby (Home Farm AD) electrical site survey: geolocated assets, site photos and grid context (LN9 6JB) |
| `app_kld_atlas.py` | `kld_atlas.html` | KLD Atlas — Kinlochdamph 999 kW run-of-river hydro (Loch Damh, Wester Ross): site assets, the 11/33/132 kV network, the two SSEN connection options, and an interactive 3D model of the powerhouse |
| `app_moray_atlas.py` | `moray_atlas.html` | Moray Cluster Atlas — the Keith & Huntly primaries (the only two green-headroom primaries in the Savills Moray screen): candidate plots, ownership areas, GSP saturation, the 33/132/275/400 kV network and the offshore wind landing on it |
| `app_srv_3d_sim.py` | `srv_3d_sim.html` | SRV 3D Sim — the Scrivelsby Peaker: a three.js model of the Home Farm AD site with a half-hourly dispatch simulation of the 350 kW switchable block over a real metered year, and the site survey photography on every asset pin |

Each app reads its HTML inline and renders it with `st.iframe`, so a redeploy
always serves the current map.

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

## Deploy

Deploy on Streamlit Community Cloud pointing at the app's `app_*.py` entry file.
This repo is public, so apps deploy as public apps — unlimited and free.
