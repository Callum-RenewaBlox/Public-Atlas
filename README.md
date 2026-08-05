# RenewaBlox — Public Atlas

Public-facing, self-contained map tools built by RenewaBlox. Each app is a thin
Streamlit wrapper around a standalone Leaflet map (Leaflet from a CDN, all data
embedded) — no database, no secrets. Because this repo is public, the apps
deploy as **public apps** on Streamlit Community Cloud (unlimited, free).

## Apps

| App | Map | What it shows |
| --- | --- | --- |
| `app_srv_atlas.py` | `srv_atlas.html` | SRV Atlas — Scrivelsby (Home Farm AD) electrical site survey: geolocated assets, site photos and grid context (LN9 6JB) |
| `app_kld_atlas.py` | `kld_atlas.html` | KLD Atlas — Kinlochdamph 999 kW run-of-river hydro (Loch Damh, Wester Ross): site assets, the 11/33/132 kV network, the two SSEN connection options, and an interactive 3D model of the powerhouse |

Each app reads its HTML inline and renders it with `st.iframe`, so a redeploy
always serves the current map.

`kld_atlas.html` is generated, not hand-edited — rebuild it from the working
atlas with `Contracts/Kinlochdamph/Atlas/build_kld_atlas.py`, which re-skins the
source map and re-uses its vendored Leaflet, model-viewer and GLB payloads
byte-for-byte.

## Run locally

    pip install -r requirements.txt
    streamlit run app_srv_atlas.py
    streamlit run app_kld_atlas.py

## Deploy

Deploy on Streamlit Community Cloud pointing at the app's `app_*.py` entry file.
This repo is public, so apps deploy as public apps — unlimited and free.
