"""The outreach app's design system: one stylesheet and a few HTML helpers.

Every block of custom HTML goes through ``html()``, which wraps it in
``<div class="ob">`` so the stylesheet can scope its rules under ``.ob`` and
win over Streamlit's own element styles. ``st.html`` is used rather than
``st.markdown``: it renders the HTML as written (no Markdown pass, no heading
anchors) and keeps ``target="_blank"`` on links, which matters because a
deployed app runs inside an iframe that most source sites refuse to load in.
It does strip inline ``<svg>``, so diagrams here are drawn in HTML and CSS,
which also lets them reflow on a phone instead of scrolling sideways.

Tokens follow energy.renewablox.co.uk (petrol brand, tem orange, Inter and
IBM Plex Mono) and switch with the viewer's colour scheme, as the app's
Streamlit theme does (``.streamlit/config.toml`` beside the entry script).
"""
from html import escape

import streamlit as st

CSS = r"""
<style>
:root{
  --bg:#f4f8fa; --surface:#ffffff; --surface-2:#eaf1f5; --surface-3:#e2ebf0;
  --line:#dfe8ed; --line-2:#edf3f6; --line-strong:#b9cad3;
  --ink:#0d1b23; --ink-2:#33454f; --muted:#61717a; --muted-2:#93a2aa;
  --brand:#12475e; --accent:#1f5f7f; --accent-l:#3a89ae; --accent-bg:#e4eff5; --on-accent:#ffffff;
  --track:#d5e4ec;
  --tem:#ff3f10; --tem-d:#cf300a; --tem-bg:#fff1ec; --tem-line:rgba(255,63,16,.28);
  --heat:#e0801f; --heat-d:#a9580c; --heat-bg:#fdf1e3; --heat-line:rgba(224,128,31,.38);
  --sh-1:0 1px 2px rgba(9,26,35,.06),0 6px 18px rgba(9,26,35,.07);
  --sh-2:0 2px 6px rgba(9,26,35,.10),0 18px 48px rgba(9,26,35,.16);
  --hero-a:#0d1b23; --hero-b:#12475e; --hero-ink:#f2f7fa; --hero-ink-2:#b9cdd8; --hero-line:rgba(255,255,255,.14);
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --r:14px; --r-s:9px;
}
@media (prefers-color-scheme: dark){
  :root{
    --bg:#0b161c; --surface:#10222b; --surface-2:#162c37; --surface-3:#1c3542;
    --line:#22363f; --line-2:#1a2d36; --line-strong:#3a5461;
    --ink:#e8f0f4; --ink-2:#c3d2da; --muted:#8fa3ad; --muted-2:#66808b;
    --brand:#a9d6ea; --accent:#6fb3d3; --accent-l:#8fc8e3; --accent-bg:#14303c; --on-accent:#07161e;
    --track:#1d3a48;
    --tem:#ff6a44; --tem-d:#ff8a6a; --tem-bg:rgba(255,106,68,.12); --tem-line:rgba(255,106,68,.35);
    --heat:#f0a050; --heat-d:#f7b76f; --heat-bg:rgba(240,160,80,.13); --heat-line:rgba(240,160,80,.4);
    --sh-1:0 1px 2px rgba(0,0,0,.35),0 6px 18px rgba(0,0,0,.30);
    --sh-2:0 2px 6px rgba(0,0,0,.4),0 18px 48px rgba(0,0,0,.5);
    --hero-a:#0d1f28; --hero-b:#123a4b; --hero-line:rgba(255,255,255,.12);
  }
}

/* ---------- Streamlit frame ---------- */
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"],[data-testid="stSidebarCollapsedControl"],footer{display:none !important}
[data-testid="stMainBlockContainer"],.block-container{max-width:1160px !important;padding:14px clamp(16px,4vw,40px) 56px !important}
[data-testid="stMain"]{scrollbar-width:thin}
[data-testid="stElementContainer"]:has(> .stHtml:empty){display:none}

/* ---------- base ---------- */
.ob{color:var(--ink);font-size:15.5px;line-height:1.6;font-feature-settings:"cv05","cv11","ss01";-webkit-font-smoothing:antialiased}
.ob *,.ob *::before,.ob *::after{box-sizing:border-box}
:where(.ob) p{margin:0}
:where(.ob) :is(h1,h2,h3,h4){margin:0;padding:0}
.ob :is(h1,h2,h3,h4){color:var(--ink);text-wrap:balance;letter-spacing:-.015em;font-family:inherit;}
.ob h1{font-size:clamp(34px,5.4vw,58px);line-height:1.02;font-weight:800;letter-spacing:-.035em}
.ob h2{font-size:clamp(26px,3.2vw,36px);line-height:1.12;font-weight:800;letter-spacing:-.03em}
.ob h3{font-size:clamp(19px,2vw,23px);line-height:1.25;font-weight:750;letter-spacing:-.02em}
.ob h4{font-size:16px;line-height:1.35;font-weight:700}
.ob strong,.ob b{font-weight:650;color:var(--ink)}
.ob a{color:var(--accent);text-decoration:underline;text-decoration-color:color-mix(in srgb,var(--accent) 38%,transparent);text-underline-offset:2px}
.ob a:hover{text-decoration-color:var(--accent)}
.ob code{font-family:var(--mono);font-size:.88em;background:var(--surface-2);border-radius:5px;padding:1px 5px;color:var(--ink-2)}
.ob .mono{font-family:var(--mono)}
.ob .muted{color:var(--muted)}
.ob .small{font-size:13.5px}
:where(.ob) :is(ul,ol){margin:0;padding:0}

/* ---------- brand bar ---------- */
.brandbar{display:flex;align-items:center;justify-content:space-between;gap:12px 18px;flex-wrap:wrap;padding:6px 0 4px}
.wordmark{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.wm{font-weight:300;font-size:21px;letter-spacing:.06em;line-height:1;color:var(--ink);white-space:nowrap}
.wm b{font-weight:800}
.wm .dot{color:var(--accent)}
.wm-x{color:var(--muted-2);font-size:14px}
.temmark{display:inline-flex;align-items:center;gap:5px;color:var(--tem);font-weight:650;font-size:19px;letter-spacing:-.01em;line-height:1}
.temmark::before{content:"";width:14px;height:14px;background:var(--tem);
  -webkit-mask:url("data:image/svg+xml;utf8,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20viewBox=%270%200%2016%2016%27%3E%3Cpath%20d=%27M8%200c.6%204.2%203.8%207.4%208%208-4.2.6-7.4%203.8-8%208-.6-4.2-3.8-7.4-8-8%204.2-.6%207.4-3.8%208-8z%27/%3E%3C/svg%3E") center/contain no-repeat;
          mask:url("data:image/svg+xml;utf8,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20viewBox=%270%200%2016%2016%27%3E%3Cpath%20d=%27M8%200c.6%204.2%203.8%207.4%208%208-4.2.6-7.4%203.8-8%208-.6-4.2-3.8-7.4-8-8%204.2-.6%207.4-3.8%208-8z%27/%3E%3C/svg%3E") center/contain no-repeat}
.wm-sep{width:1px;height:24px;background:var(--line-strong)}
.wm-label{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-2);line-height:1.3}
.metas{display:flex;gap:8px;flex-wrap:wrap}
.pill{display:inline-flex;align-items:center;gap:6px;background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:5px 12px;font-size:12.5px;color:var(--ink-2);white-space:nowrap}
.pill .k{color:var(--muted)}
@media (max-width:600px){.wm-sep,.metas .pill.opt{display:none}}

/* ---------- tab rail (st.page_link in a keyed horizontal container) ---------- */
[data-testid="stLayoutWrapper"]:has(> .st-key-rail){position:sticky;top:0;z-index:40;
  margin:0 calc(-1 * clamp(16px,4vw,40px));padding:0 clamp(16px,4vw,40px);
  background:color-mix(in srgb,var(--bg) 86%,transparent);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
  border-bottom:1px solid var(--line)}
.st-key-rail{flex-wrap:nowrap !important;overflow-x:auto;scrollbar-width:none;gap:2px !important;padding:6px 0}
.st-key-rail::-webkit-scrollbar{display:none}
@media (max-width:900px){.st-key-rail{-webkit-mask-image:linear-gradient(90deg,#000 85%,transparent);mask-image:linear-gradient(90deg,#000 85%,transparent)}}
.st-key-rail [data-testid="stPageLink"]{flex:none}
.st-key-rail [data-testid="stPageLink"] a{padding:7px 12px;border-radius:999px;white-space:nowrap;margin:0}
.st-key-rail [data-testid="stPageLink"] a span,.st-key-rail [data-testid="stPageLink"] a p{font-size:14px;font-weight:600;color:var(--muted)}
.st-key-rail [data-testid="stPageLink"] a:hover{background:var(--surface-2)}
.st-key-rail [data-testid="stPageLink"] a:hover p{color:var(--ink)}
.st-key-rail [data-testid="stPageLink-NavLink"][aria-current="page"],
.st-key-rail [data-testid="stPageLink"] a[aria-current="page"]{background:var(--accent-bg)}
.st-key-rail [data-testid="stPageLink"] a[aria-current="page"] p,
.st-key-rail [data-testid="stPageLink"] a[aria-current="page"] span{color:var(--brand)}

/* ---------- next / previous ---------- */
.st-key-pager{border-top:1px solid var(--line);padding-top:18px;margin-top:18px}
.st-key-pager [data-testid="stPageLink"] a{border:1px solid var(--line);background:var(--surface);border-radius:999px;padding:8px 16px;box-shadow:var(--sh-1)}
.st-key-pager [data-testid="stPageLink"] a:hover{border-color:var(--accent-l)}

/* ---------- hero (overview) ---------- */
.hero{position:relative;overflow:hidden;border-radius:22px;padding:clamp(26px,4.5vw,52px);margin-top:14px;
  background:radial-gradient(900px 480px at 0% 0%,rgba(58,137,174,.35),transparent 60%),
             radial-gradient(640px 420px at 105% 0%,rgba(255,63,16,.26),transparent 62%),
             linear-gradient(140deg,var(--hero-a),var(--hero-b));
  color:var(--hero-ink);box-shadow:var(--sh-2);border:1px solid var(--hero-line)}
.hero::after{content:"";position:absolute;inset:0;pointer-events:none;opacity:.5;
  background-image:linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);
  background-size:44px 44px;mask-image:linear-gradient(to bottom,#000,transparent 75%);-webkit-mask-image:linear-gradient(to bottom,#000,transparent 75%)}
.hero > *{position:relative;z-index:1}
.hero .eyebrow{color:#8fc8e3}
.hero .eyebrow::before{background:#8fc8e3}
.hero h1{color:#fff;margin-top:16px;max-width:15ch}
.hero .grad{background:linear-gradient(92deg,#8fc8e3 0%,#c9e6f3 35%,#ff7a52 78%,#ff3f10 100%);-webkit-background-clip:text;background-clip:text;color:transparent;font-style:italic;padding-right:.08em}
.hero .lead{margin-top:20px;font-size:clamp(16px,1.6vw,18.5px);line-height:1.6;color:var(--hero-ink-2);max-width:60ch}
.hero .lead b{color:#fff}
.hero-grid{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:clamp(24px,4vw,48px);align-items:end}
.facts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.fact{background:rgba(255,255,255,.06);border:1px solid var(--hero-line);border-radius:12px;padding:13px 15px;backdrop-filter:blur(6px)}
.fact .k{font-family:var(--mono);font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;color:#8fc8e3}
.fact .v{margin-top:5px;font-weight:650;font-size:15px;line-height:1.35;color:#fff}
.status{display:inline-flex;align-items:center;gap:10px;margin-top:26px;padding:7px 14px 7px 10px;border-radius:999px;
  background:rgba(255,255,255,.08);border:1px solid var(--hero-line);font-size:13.5px;color:#fff}
.status .dotlive{width:9px;height:9px;border-radius:50%;background:#ff7a52;box-shadow:0 0 0 0 rgba(255,122,82,.6);animation:pulse 2.2s infinite}
.status .k{white-space:nowrap;font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:#8fc8e3}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(255,122,82,.55)}70%{box-shadow:0 0 0 10px rgba(255,122,82,0)}100%{box-shadow:0 0 0 0 rgba(255,122,82,0)}}
@media (prefers-reduced-motion:reduce){.status .dotlive{animation:none}}
@media (max-width:860px){.hero-grid{grid-template-columns:1fr}}
@media (max-width:420px){.facts{grid-template-columns:1fr}}

/* ---------- page intro & section heads ---------- */
.eyebrow{display:flex;align-items:center;gap:12px;font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--accent);font-weight:500;margin:0}
.eyebrow::before{content:"";width:24px;height:1.5px;background:currentColor;flex:none}
.intro{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);gap:16px 48px;align-items:end;padding:26px 0 8px}
.intro h2{margin-top:12px}
.intro .lead{font-size:17px;line-height:1.62;color:var(--ink-2)}
@media (max-width:860px){.intro{grid-template-columns:1fr;padding-top:20px}}
.sec{padding-top:34px;margin-top:12px;border-top:1px solid var(--line)}
.sec.first{border-top:0;padding-top:10px;margin-top:0}
.sec h3{margin-top:9px}
.sec .sub{margin-top:8px;color:var(--muted);font-size:15px;max-width:74ch;line-height:1.55}
.subhead{font-size:16px;font-weight:700;margin:0 0 12px;color:var(--ink)}

/* ---------- layout ---------- */
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:22px 36px;align-items:start}
.cols > *{min-width:0}
.cols.wide-left{grid-template-columns:minmax(0,1.25fr) minmax(0,1fr)}
@media (max-width:860px){.cols.wide-left{grid-template-columns:1fr}}
.stack{display:grid;gap:12px}
.mt{margin-top:18px}.mt-l{margin-top:28px}

/* ---------- cards ---------- */
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,232px),1fr));gap:14px}
.cards.c3{grid-template-columns:repeat(auto-fit,minmax(min(100%,290px),1fr))}
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:18px 18px 16px;box-shadow:var(--sh-1);display:flex;flex-direction:column;gap:8px;min-width:0}
.card .tag{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:600}
.card h4{font-size:17px;letter-spacing:-.012em}
.card p{font-size:14.5px;color:var(--ink-2);line-height:1.55}
.card .kv{display:grid;gap:8px;margin-top:auto;padding-top:12px;border-top:1px solid var(--line-2)}
.card .kv div{font-size:13.5px;color:var(--ink-2);line-height:1.45}
.card .kv b{display:block;font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-weight:500;margin-bottom:2px}
.card.base{background:linear-gradient(180deg,var(--accent-bg),var(--surface) 72%);border-color:color-mix(in srgb,var(--accent) 38%,var(--line))}
.card .letter{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;font-weight:800;font-size:16px;background:var(--accent-bg);color:var(--brand)}
.card.base .letter{background:var(--accent);color:var(--on-accent)}
.card .num{font-family:var(--mono);font-size:11px;color:var(--muted-2);letter-spacing:.06em}
.mini{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-s);padding:14px 16px;min-width:0}
.mini h4{font-size:15px;margin-bottom:6px}
.mini p,.mini li{font-size:14px;color:var(--ink-2);line-height:1.55}
.ob .mini ul{padding-left:18px;margin:4px 0 0}
.mini li{margin:5px 0}
.mini li::marker{color:var(--muted-2)}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:12px}
.grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:12px}

/* ---------- callouts ---------- */
.callout{border-radius:var(--r-s);padding:14px 16px;background:var(--surface-2);border:1px solid var(--line);font-size:14.5px;color:var(--ink-2);line-height:1.58}
.callout .ttl{display:block;font-weight:700;color:var(--ink);margin-bottom:3px}
.callout.correction{background:var(--tem-bg);border-color:var(--tem-line)}
.callout.correction .ttl{color:var(--tem-d)}
.callout.decision{background:var(--heat-bg);border-color:var(--heat-line)}
.callout.decision .ttl{color:var(--heat-d)}
.callout.rule{background:var(--surface);border-left:3px solid var(--accent);border-radius:0 var(--r-s) var(--r-s) 0}
.callout.rule.tem{border-left-color:var(--tem)}
.badge{display:inline-flex;align-items:center;gap:6px;font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;border-radius:999px;padding:3px 9px;font-weight:600;white-space:nowrap}
.badge.decision{background:var(--heat-bg);color:var(--heat-d);border:1px solid var(--heat-line)}
.badge.accent{background:var(--accent-bg);color:var(--brand)}
.badge.tem{background:var(--tem-bg);color:var(--tem-d);border:1px solid var(--tem-line)}
.badge.quiet{background:var(--surface-2);color:var(--muted)}

/* ---------- lists ---------- */
ul.clean{list-style:none;display:grid;gap:11px}
ul.clean li{position:relative;padding-left:20px;color:var(--ink-2)}
ul.clean li::before{content:"";position:absolute;left:0;top:.62em;width:7px;height:7px;border-radius:2px;background:var(--accent-l)}
ol.steps{list-style:none;counter-reset:s;display:grid;gap:12px}
ol.steps li{position:relative;padding-left:40px;counter-increment:s;color:var(--ink-2)}
ol.steps li::before{content:counter(s);position:absolute;left:0;top:0;width:27px;height:27px;border-radius:50%;background:var(--accent-bg);color:var(--brand);font-family:var(--mono);font-size:12px;font-weight:600;display:grid;place-items:center}
ul.check{list-style:none;display:grid;gap:9px;margin-top:14px}
ul.check li{position:relative;padding-left:28px;font-size:14.5px;color:var(--ink-2);line-height:1.5}
ul.check li{padding-left:18px}
ul.check li::before{content:"";position:absolute;left:0;top:.6em;width:7px;height:7px;border-radius:2px;background:var(--accent-l)}
ul.check li.dim{opacity:.38}
.ob ul.clean,.ob ol.steps,.ob ul.check{padding:0;margin-left:0;margin-right:0;margin-bottom:0}
.ob ul.clean,.ob ol.steps{margin-top:0}
.ob ul.clean li,.ob ol.steps li,.ob ul.check li{margin:0}

/* ---------- stats ---------- */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,140px),1fr));gap:12px}
.stat{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-s);padding:16px 18px;box-shadow:var(--sh-1)}
.stat .v{font-size:30px;font-weight:800;letter-spacing:-.03em;line-height:1;color:var(--brand)}
.stat .v small{font-size:13.5px;font-weight:600;letter-spacing:0;color:var(--muted);margin-left:5px}
.stat .l{margin-top:8px;font-size:13.5px;color:var(--ink-2);line-height:1.42}
.stat.hot .v{color:var(--tem)}

/* ---------- tables ---------- */
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:var(--r-s);background:var(--surface);box-shadow:var(--sh-1)}
.ob table{border-collapse:collapse;width:100%;font-size:14px;line-height:1.5;margin:0;border:0}
.ob thead th{text-align:left;font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-weight:500;padding:11px 14px;border:0;border-bottom:1px solid var(--line);background:var(--surface-2);white-space:nowrap}
.ob tbody td{padding:11px 14px;border:0;border-bottom:1px solid var(--line-2);vertical-align:top;color:var(--ink-2)}
.ob tbody tr:last-child td{border-bottom:0}
.ob tbody td:first-child{color:var(--ink);font-weight:600}
.ob tbody tr:hover td{background:color-mix(in srgb,var(--surface-2) 45%,transparent)}
.ob table.compact td,.ob table.compact th{padding:9px 12px}
.ob td.nowrap{white-space:nowrap}
.tier{display:inline-grid;place-items:center;width:24px;height:24px;border-radius:7px;font-family:var(--mono);font-size:12px;font-weight:600;background:var(--accent);color:var(--on-accent)}
.tier.t2{background:var(--accent-bg);color:var(--brand)}
.tier.t3{background:transparent;border:1px solid var(--line-strong);color:var(--muted)}
.tierrow td{background:var(--surface-2) !important;font-family:var(--mono);font-size:10.5px !important;letter-spacing:.12em;text-transform:uppercase;color:var(--muted) !important;font-weight:500 !important;padding:7px 14px !important}
.share{display:flex;align-items:center;gap:10px;font-variant-numeric:tabular-nums;font-weight:650;color:var(--ink)}
.share .trk{width:96px;height:10px;background:var(--track);border-radius:3px;overflow:hidden;flex:none}
.share .trk i{display:block;height:100%;background:var(--accent);border-radius:0 3px 3px 0}

/* ---------- channel map (overview) ---------- */
.chmap{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:22px clamp(16px,3vw,28px) 18px;box-shadow:var(--sh-1)}
.chmap .ttl{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:baseline;margin-bottom:16px}
.chmap .ttl h4{font-size:16px}
.channels{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;position:relative}
.channel{position:relative;background:var(--surface);border:1px solid var(--line-strong);border-radius:10px;padding:11px 10px;text-align:center}
.channel b{display:block;font-size:14px}
.channel span{display:block;font-size:12.5px;color:var(--muted);line-height:1.35;margin-top:2px}
.channel::after{content:"";position:absolute;left:50%;bottom:-17px;width:1.5px;height:16px;background:var(--line-strong)}
.bus{position:relative;height:34px}
.bus::before{content:"";position:absolute;left:calc((100% - 40px) / 10);right:calc((100% - 40px) / 10);top:16px;height:1.5px;background:var(--line-strong)}
.bus::after{content:"";position:absolute;left:50%;top:16px;width:1.5px;height:18px;background:var(--line-strong)}
.xray{position:relative;margin:0 auto;max-width:520px;text-align:center;border-radius:12px;padding:14px 18px;
  background:linear-gradient(135deg,var(--accent),var(--brand));color:var(--on-accent);box-shadow:var(--sh-2)}
.xray b{display:block;font-size:17px;color:inherit;letter-spacing:-.01em}
.xray span{font-size:13.5px;opacity:.9}
@media (prefers-color-scheme: dark){.xray{background:linear-gradient(135deg,#2a6f90,#164a60);color:#fff}}
.split{position:relative;height:18px}
.split::before{content:"";position:absolute;left:50%;top:0;width:1.5px;height:18px;background:var(--line-strong)}
.split::after{content:"";position:absolute;left:calc((100% - 16px) / 4);right:calc((100% - 16px) / 4);top:17px;height:1.5px;background:var(--line-strong)}
.fork{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:0}
.fork .leg{position:relative;padding-top:36px;text-align:center}
.fork .leg::before{content:"";position:absolute;left:50%;top:0;width:1.5px;height:28px;background:var(--line-strong)}
.fork .leg::after{content:"";position:absolute;left:calc(50% - 4.5px);top:26px;border:4.5px solid transparent;border-top:7px solid var(--line-strong);border-bottom:0}
.fork .lab{position:absolute;top:6px;left:calc(50% + 10px);font-size:12px;color:var(--muted);white-space:nowrap;font-family:var(--mono);letter-spacing:.02em}
.outcome{border:1px solid var(--line-strong);border-radius:10px;padding:12px 14px;background:var(--surface)}
.outcome b{display:block;font-size:14.5px}
.outcome span{display:block;font-size:13px;color:var(--muted);line-height:1.45;margin-top:2px}
.outcome.go{border-color:color-mix(in srgb,var(--tem) 45%,var(--line));background:var(--tem-bg)}
.basebar{margin-top:14px;background:var(--surface-2);border:1px dashed var(--line-strong);border-radius:10px;padding:10px 14px;text-align:center;font-size:13.5px;color:var(--ink-2)}
.figcap{margin-top:12px;font-size:13.5px;color:var(--muted);line-height:1.5}
@media (max-width:720px){
  .channels{grid-template-columns:repeat(2,minmax(0,1fr))}
  .channel:last-child{grid-column:1/-1}
  .channel::after,.bus::before{display:none}
  .bus{height:28px}.bus::after{top:4px;height:22px}
  .split::after{display:none}
  .fork{grid-template-columns:1fr}
  .fork .lab{position:static;display:block;margin-bottom:6px}
  .fork .leg{padding-top:0}
  .fork .leg::before,.fork .leg::after{display:none}
  .fork .leg:first-child{margin-top:12px}
}

/* ---------- funnel (meter rows: fill = stage rate, value = monthly count) ---------- */
.funnel{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:18px clamp(14px,2.5vw,22px);box-shadow:var(--sh-1);display:grid;gap:13px}
.frow{display:grid;grid-template-columns:minmax(120px,176px) minmax(0,1fr) 84px;gap:14px;align-items:center}
.frow .lab{font-size:14px;font-weight:600;color:var(--ink);line-height:1.3}
.frow .lab small{display:block;color:var(--muted);font-weight:400;font-size:12.5px}
.frow .bar{height:18px;background:var(--track);border-radius:4px;position:relative}
.frow .bar i{position:absolute;inset:0 auto 0 0;background:var(--accent);border-radius:0 4px 4px 0;min-width:2px}
.frow .bar em{position:absolute;top:50%;transform:translateY(-50%);font-style:normal;font-family:var(--mono);font-size:11.5px;color:var(--ink-2);white-space:nowrap}
.frow .val{text-align:right;font-variant-numeric:tabular-nums;font-weight:750;font-size:17px;color:var(--ink)}
.frow .val small{display:block;font-weight:400;color:var(--muted);font-size:11.5px}
.frow.last .bar i{background:var(--tem)}
.frow.last .val{color:var(--tem)}
@media (max-width:560px){.frow{grid-template-columns:minmax(0,1fr) 76px;grid-template-areas:"lab val" "bar bar";gap:6px 12px}.frow .lab{grid-area:lab}.frow .val{grid-area:val}.frow .bar{grid-area:bar}}

/* ---------- sequence track (LinkedIn) ---------- */
.track{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:0;position:relative;padding-top:4px}
.track::before{content:"";position:absolute;left:8%;right:8%;top:19px;height:2px;background:var(--track)}
.touch{position:relative;text-align:center;padding:0 8px}
.touch .dot{width:30px;height:30px;margin:0 auto;border-radius:50%;background:var(--surface);border:2px solid var(--accent);display:grid;place-items:center;font-family:var(--mono);font-size:11.5px;font-weight:600;color:var(--brand);position:relative;z-index:1;box-shadow:0 0 0 4px var(--bg)}
.touch.msg .dot{background:var(--accent);color:var(--on-accent)}
.touch.stop .dot{border-color:var(--tem);background:var(--tem);color:#fff}
.touch .day{margin-top:10px;font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--accent)}
.touch b{display:block;font-size:14px;margin-top:3px;line-height:1.3}
.touch p{font-size:13px;color:var(--muted);line-height:1.45;margin-top:4px}
@media (max-width:860px){
  .track{grid-template-columns:1fr;gap:14px}
  .track::before{left:14px;right:auto;top:8px;bottom:8px;width:2px;height:auto}
  .touch{display:grid;grid-template-columns:30px minmax(0,1fr);column-gap:14px;text-align:left;padding:0}
  .touch .dot{grid-row:1/4;margin:0}
  .touch .day{margin-top:0}
}

/* ---------- swimlane (AI workflow) ---------- */
.lanes thead th.crew{color:var(--brand)}
.lanes thead th.founder{color:var(--tem-d)}
.lanes td.crew{background:color-mix(in srgb,var(--accent-bg) 50%,transparent)}

/* ---------- flywheel (strategy B) ---------- */
.loop{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:20px clamp(14px,2.5vw,24px);box-shadow:var(--sh-1)}
.loop-steps{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:26px;position:relative}
.lstep{position:relative;border:1px solid var(--line-strong);border-radius:12px;padding:13px 12px;background:var(--surface)}
.lstep:first-child{background:var(--accent-bg);border-color:var(--accent)}
.lstep .n{font-family:var(--mono);font-size:11px;color:var(--accent);font-weight:600}
.lstep b{display:block;font-size:14.5px;margin-top:2px;line-height:1.3}
.lstep span{display:block;font-size:12.5px;color:var(--muted);margin-top:3px;line-height:1.4}
.lstep:not(:last-child)::after{content:"";position:absolute;right:-21px;top:50%;width:16px;height:2px;background:var(--line-strong)}
.lstep:not(:last-child)::before{content:"";position:absolute;right:-23px;top:calc(50% - 4px);border:4.5px solid transparent;border-left:6px solid var(--line-strong);border-right:0}
.lstep .via{position:absolute;right:-26px;top:calc(50% - 26px);width:26px;text-align:center;font-size:10px;color:var(--muted-2);line-height:1.1;display:none}
.loop-back{position:relative;margin:16px 10% 0;height:26px;border:2px solid var(--line-strong);border-top:0;border-radius:0 0 14px 14px}
.loop-back span{position:absolute;left:50%;bottom:-11px;transform:translateX(-50%);background:var(--surface);padding:0 10px;font-size:12.5px;color:var(--muted);white-space:nowrap}
.loop-back::after{content:"";position:absolute;left:-7px;top:-8px;border:6px solid transparent;border-bottom:8px solid var(--line-strong);border-top:0}
.loop-core{margin-top:26px;text-align:center;font-size:14px;color:var(--ink-2)}
.loop-core b{color:var(--brand)}
@media (max-width:860px){
  .loop-steps{grid-template-columns:1fr;gap:22px}
  .lstep:not(:last-child)::after{right:auto;left:24px;top:auto;bottom:-17px;width:2px;height:12px}
  .lstep:not(:last-child)::before{right:auto;left:20px;top:auto;bottom:-22px;border:4.5px solid transparent;border-top:6px solid var(--line-strong);border-bottom:0}
  .loop-back{margin:14px 0 0;border:0;height:auto}.loop-back::after{display:none}
  .loop-back span{position:static;transform:none;display:block;text-align:center;padding:8px 10px;border:1px dashed var(--line-strong);border-radius:10px;white-space:normal}
}

/* ---------- 14-week gantt ---------- */
.gantt{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:18px clamp(14px,2.5vw,22px) 16px;box-shadow:var(--sh-1);overflow-x:auto}
.gantt-in{min-width:680px;position:relative}
.weeks{display:grid;grid-template-columns:repeat(14,minmax(0,1fr));border-bottom:1px solid var(--line);padding-bottom:6px}
.weeks div{font-family:var(--mono);font-size:10px;letter-spacing:.04em;color:var(--muted-2);white-space:nowrap;padding-left:3px}
.weeks div b{display:block;color:var(--muted);font-weight:600}
.lanes-g{position:relative;height:214px;margin-top:10px;
  background-image:linear-gradient(90deg,var(--line-2) 1px,transparent 1px);background-size:calc(100% / 14) 100%}
.pbar{position:absolute;height:auto;border-radius:10px;padding:10px 12px;border:1px solid var(--line-strong);background:var(--surface);overflow:hidden}
.pbar.p1{top:0}.pbar.p2{top:70px}.pbar.p3{top:140px}
.pbar .t{font-weight:700;font-size:13.5px;white-space:nowrap}
.pbar .d{font-family:var(--mono);font-size:10.5px;color:var(--muted);letter-spacing:.04em;white-space:nowrap}
.pbar.now{border-color:var(--accent);background:var(--accent-bg);box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 18%,transparent)}
.pbar.done{opacity:.55}
.gate-m{position:absolute;width:13px;height:13px;background:var(--heat);transform:translate(-50%,0) rotate(45deg);border-radius:2px;box-shadow:0 0 0 3px var(--surface)}
.gate-l{position:absolute;transform:translateX(-100%);padding-right:12px;text-align:right;font-size:11.5px;line-height:1.35;color:var(--muted);white-space:nowrap}
.gate-l b{display:block;color:var(--heat-d);font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;text-transform:uppercase}
.gantt-in{padding-top:26px}
.today{position:absolute;top:-86px;bottom:0;width:0;border-left:2px solid var(--tem);z-index:1}
.today span{position:absolute;top:0;left:-2px;font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#fff;background:var(--tem);border-radius:4px;padding:2px 6px;white-space:nowrap}
.glab{position:absolute;z-index:2;white-space:nowrap;background:var(--surface);padding:0 6px 1px 0;border-radius:3px}
.gate-l2{width:max-content;max-width:220px;white-space:normal;font-size:11.5px;line-height:1.35;color:var(--muted);padding:0 4px}
.gantt-note{margin-top:10px;font-size:13px;color:var(--muted)}
@media (max-width:720px){.gantt-note::before{content:"Scroll sideways for all 14 weeks. ";color:var(--accent)}}

/* ---------- phases ---------- */
.phase{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:18px 20px;box-shadow:var(--sh-1);height:100%}
.phase.now{border-color:var(--accent);box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 14%,transparent),var(--sh-1)}
.phase h4{font-size:17px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.phase .dates{font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-top:4px}
.owner{display:inline-block;font-family:var(--mono);font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--brand);background:var(--accent-bg);border-radius:4px;padding:2px 6px;margin-right:7px;vertical-align:1px;white-space:nowrap}
.gate{display:flex;gap:12px;align-items:flex-start;background:var(--heat-bg);border:1px solid var(--heat-line);border-radius:var(--r-s);padding:11px 14px;margin-top:16px}
.gate .d{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--heat-d);white-space:nowrap;padding-top:3px;font-weight:600}
.gate .t{font-size:14px;color:var(--ink-2);line-height:1.5}

/* ---------- matrix (who leads) ---------- */
.matrix{display:grid;grid-template-columns:auto 1fr 1fr;gap:8px;font-size:14px}
.matrix .h{font-family:var(--mono);font-size:10.5px;letter-spacing:.11em;text-transform:uppercase;color:var(--muted);padding:4px 6px;align-self:end}
.matrix .r{font-weight:650;color:var(--ink);padding:12px 8px 12px 0;font-size:13.5px}
.matrix .c{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 14px;color:var(--ink-2);font-size:13.5px;line-height:1.45}
.matrix .c b{display:block;color:var(--ink);font-size:14px;margin-bottom:2px}
.matrix .c.li{border-left:3px solid var(--accent)}
.matrix .c.em{border-left:3px solid var(--tem)}
.matrix .c.po{border-left:3px solid var(--line-strong)}

/* ---------- playbook & toolkit ---------- */
.play{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,210px),1fr));gap:10px;margin-top:12px}
.play div{background:var(--surface-2);border-radius:var(--r-s);padding:11px 13px;font-size:14px;color:var(--ink-2);line-height:1.45}
.play div b{display:block;font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-weight:500;margin-bottom:3px}
.tplhead{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin:6px 0 -6px}
.tplhead h4{font-size:15px;margin-right:auto}
.tplhead .when{font-family:var(--mono);font-size:11px;color:var(--muted);letter-spacing:.03em}
.len{font-family:var(--mono);font-size:10.5px;border-radius:999px;padding:2px 8px;white-space:nowrap}
.len.ok{background:var(--accent-bg);color:var(--brand)}
.len.over{background:var(--tem-bg);color:var(--tem-d)}
.grouphead{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;padding-top:24px;margin-top:6px;border-top:1px solid var(--line)}
.grouphead h3{font-size:20px}
.grouphead .hint{font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
/* message templates read as prose; crew prompts stay monospaced */
[class*="st-key-tplmsg"] [data-testid="stCode"] code,[class*="st-key-tplmsg"] [data-testid="stCode"] pre{font-family:"Inter",system-ui,sans-serif !important;font-size:14.5px !important;line-height:1.6 !important;color:var(--ink-2) !important}
[data-testid="stCode"] pre{border:1px solid var(--line);border-radius:var(--r-s)}
.st-key-fields{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:16px 18px 6px;box-shadow:var(--sh-1)}
.st-key-calc{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:14px 18px 8px;box-shadow:var(--sh-1)}
.st-key-sizing{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:16px 18px 12px;box-shadow:var(--sh-1);margin-top:18px}
.st-key-playbook{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:16px 18px 10px;box-shadow:var(--sh-1)}

/* ---------- footer ---------- */
.colophon{display:flex;justify-content:space-between;gap:10px 16px;flex-wrap:wrap;font-size:12.5px;color:var(--muted);padding-top:6px}

/* ---------- streamlit widgets, light touch ---------- */
[data-testid="stTabs"] [data-testid="stTab"] p{font-weight:600;font-size:14.5px}
[data-testid="stExpander"] details{background:var(--surface);border-color:var(--line)}
[data-testid="stWidgetLabel"] p{font-weight:600}
</style>
"""


def inject_css():
    st.html(CSS)


def html(*parts):
    """Render a block of the app's own HTML, scoped under ``.ob``."""
    st.html('<div class="ob">' + "".join(parts) + "</div>")


def e(text):
    return escape(str(text), quote=True)


def intro(eyebrow, title, lead):
    html(f'<div class="intro"><div><p class="eyebrow">{eyebrow}</p><h2>{title}</h2></div>'
         f'<p class="lead">{lead}</p></div>')


def sec(eyebrow, title, sub="", first=False, extra=""):
    """A section head; ``extra`` is HTML placed under it in the same block."""
    sub_html = f'<p class="sub">{sub}</p>' if sub else ""
    return (f'<div class="sec{" first" if first else ""}"><p class="eyebrow">{eyebrow}</p>'
            f'<h3>{title}</h3>{sub_html}</div>{extra}')


def card(body, tag="", title="", kv=(), cls="", lead=""):
    tag_html = f'<div class="tag">{tag}</div>' if tag else ""
    title_html = f"<h4>{title}</h4>" if title else ""
    body_html = f"<p>{body}</p>" if body else ""
    kv_html = ""
    if kv:
        kv_html = '<div class="kv">' + "".join(f"<div><b>{k}</b>{v}</div>" for k, v in kv) + "</div>"
    return f'<div class="card {cls}">{lead}{tag_html}{title_html}{body_html}{kv_html}</div>'


def cards(items, cls=""):
    return f'<div class="cards {cls}">' + "".join(items) + "</div>"


def callout(body, title="", kind=""):
    title_html = f'<span class="ttl">{title}</span>' if title else ""
    return f'<div class="callout {kind}">{title_html}{body}</div>'


def mini(title, body):
    return f'<div class="mini"><h4>{title}</h4>{body}</div>'


def ul(items, cls="clean"):
    return f'<ul class="{cls}">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def ol(items):
    return '<ol class="steps">' + "".join(f"<li>{i}</li>" for i in items) + "</ol>"


def table(headers, rows, cls=""):
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f'<div class="tablewrap"><table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def stat(value, label, unit="", cls=""):
    unit_html = f"<small>{unit}</small>" if unit else ""
    return f'<div class="stat {cls}"><div class="v">{value}{unit_html}</div><div class="l">{label}</div></div>'


def link(text, url):
    return f'<a href="{url}" target="_blank" rel="noopener">{text}</a>'


def subhead(text):
    return f'<h4 class="subhead">{text}</h4>'


# Streamlit drops a widget's state when a page that doesn't draw it runs, so
# the fields and the funnel assumptions would reset on every page change.
# Each widget is seeded from a plain session key that outlives it instead.
def keep(key, default):
    store = "_" + key
    if store not in st.session_state:
        st.session_state[store] = default
    if key not in st.session_state:
        st.session_state[key] = st.session_state[store]
    return key


def save(key):
    st.session_state["_" + key] = st.session_state[key]


def kept(key, default=None):
    """A kept value, readable from any page."""
    return st.session_state.get("_" + key, default)
