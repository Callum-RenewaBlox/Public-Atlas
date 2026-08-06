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
| `app_moray_atlas.py` | `moray_atlas.html` | Moray Cluster Atlas — the Keith & Huntly primaries (the only two green-headroom primaries in the Savills Moray screen): candidate plots, ownership areas, GSP saturation, the 33/132/275/400 kV network and the offshore wind landing on it |

Each app reads its HTML inline and renders it with `st.iframe`, so a redeploy
always serves the current map.

`kld_atlas.html` and `moray_atlas.html` are generated, not hand-edited — rebuild
them from their working atlases with
`Contracts/Kinlochdamph/Atlas/build_kld_atlas.py` and
`Contracts/Savills Earth/Atlas/build_moray_atlas.py`. Both re-skin the source map
in the shared RenewaBlox design system (petrol brand tokens, Inter, glass panel,
brand bar) and re-use the source's data and vendored payloads byte-for-byte.

## Run locally

    pip install -r requirements.txt
    streamlit run app_srv_atlas.py
    streamlit run app_kld_atlas.py
    streamlit run app_moray_atlas.py

## Deploy

Deploy on Streamlit Community Cloud pointing at the app's `app_*.py` entry file.
This repo is public, so apps deploy as public apps — unlimited and free.
