# RenewaBlox — Public Atlas

Public-facing, self-contained map tools built by RenewaBlox. Each app is a thin
Streamlit wrapper around a standalone Leaflet map (Leaflet from a CDN, all data
embedded) — no database, no secrets. Because this repo is public, the apps
deploy as **public apps** on Streamlit Community Cloud (unlimited, free).

## Apps

| App | Map | What it shows |
| --- | --- | --- |
| `app_srv_atlas.py` | `srv_atlas.html` | SRV Atlas — Scrivelsby (Home Farm AD) electrical site survey: geolocated assets, site photos and grid context (LN9 6JB) |

Each app reads its HTML inline and renders it with `st.iframe`, so a redeploy
always serves the current map.

## Run locally

    pip install -r requirements.txt
    streamlit run app_srv_atlas.py

## Deploy

Deploy on Streamlit Community Cloud pointing at the app's `app_*.py` entry file.
This repo is public, so apps deploy as public apps — unlimited and free.
