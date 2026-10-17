"""Build ai.renewablox.com — RenewaBlox's AI tools — into ai/site/.

    /           the front door (index.html)
    /oscar/     OSCAR, the site model (oscar.html)
    /atlas/     Atlas, served by proxy from its own Netlify project (netlify.toml)
    404.html    for any other address

The pages are hand-authored and self-contained, so the build copies them into place and checks
the three things that would otherwise break quietly:

  * OSCAR stores saved scenarios by input id, so every id a saved scenario can hold must still be
    on the page (SCENARIO_IDS);
  * no page loads a script, stylesheet, font, image or frame from elsewhere;
  * the live sources OSCAR calls are exactly the ones netlify.toml proxies under /oscar/api/.

Run:  python ai/build.py            (writes ai/site/, git-ignored)
      python -m http.server 8900 -d ai/site
Netlify runs it on every push to main that changes ai/ (ai/netlify.toml). Standard library only.
"""
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "site"

PAGES = {
    "index.html": "index.html",
    "oscar/index.html": "oscar.html",
    "404.html": "404.html",
}

# Every input a saved OSCAR scenario holds: the September 2026 edition's 62, then txFeePct and
# fixedRecoveryAuto from October 2026. Add to this list; never take from it.
SCENARIO_IDS = """
miner minerHashrate minerPowerDraw unitPrice overclockEnabled overclockProfile powerKw siteCapacityFactorPct
existingRevenuePkwh bitcoinMiningEnabled miningDeploymentPct uptime powerCost energyMarketsEnabled exportRevenueEnabled
exportUptimePct exportPricePerMwh demandTurnUpEnabled turnUpEligiblePct turnUpPricePerMwh capacityMarketPerMwYear
heatOfftakeEnabled heatOfftakePct heatPricePerMwh phase2Enabled phase2StartYears phase2PowerKw phase2UptimePct
phase2ExportUptimePct btcPrice globalHashrate marketModel btcCagr hashCagr poolFee install contingencyPct capexFunding
customCapexSlider revenueMode fixedRecoveryMonths weightedInitialMonths weightedInitialSplitSlider weightedRbxShareSlider
shareSplitSlider contractYears toggleCashflowTotal toggleCashflowMining toggleCashflowEnergy toggleCashflowClient
toggleCashflowRbx toggleAnnualPowerCostLine expertExistingRevenuePkwh treasuryHoldPct toggleTotalRevenue
toggleRbxRevenue toggleClientRevenue toggleCumulativeBtcTotal toggleCumulativeBtcRbx toggleCumulativeBtcClient
scenarioNameInput txFeePct fixedRecoveryAuto
""".split()

# OSCAR's live sources: the name it uses under /oscar/api/ and the origin it calls directly.
LIVE_SOURCES = {
    "coingecko": "https://api.coingecko.com/",
    "mempool": "https://mempool.space/",
    "blockchain": "https://api.blockchain.info/",
}

EXTERNAL_LOAD = re.compile(
    r"<(?:script|img|iframe|source|video|audio)\b[^>]*\bsrc\s*=\s*[\"']?(?:https?:)?//"
    r"|<link\b[^>]*\bhref\s*=\s*[\"']?(?:https?:)?//"
    r"|@import|url\(\s*[\"']?(?:https?:)?//",
    re.I)


def check_self_contained(name, page):
    m = EXTERNAL_LOAD.search(page)
    if m:
        raise SystemExit(f"{name}: loads something from elsewhere: {page[m.start():m.start() + 120]!r}")


def check_oscar(page):
    ids = set(re.findall(r"<(?:input|select|textarea)\b[^>]*\bid=\"([^\"]+)\"", page))
    missing = [i for i in SCENARIO_IDS if i not in ids]
    if missing:
        raise SystemExit("oscar.html: saved scenarios need these inputs, now missing: " + ", ".join(missing))
    toml = (HERE / "netlify.toml").read_text(encoding="utf-8")
    hosts = re.search(r"const LIVE_HOSTS = (\{[^}]*\})", page)
    if not hosts:
        raise SystemExit("oscar.html: LIVE_HOSTS not found")
    used = dict(re.findall(r"(\w+):\s*'([^']+)'", hosts.group(1)))
    if used != LIVE_SOURCES:
        raise SystemExit(f"oscar.html: live sources {used} differ from build.py's {LIVE_SOURCES}")
    for name, origin in LIVE_SOURCES.items():
        rule = f'from = "/oscar/api/{name}/*"\n  to = "{origin}:splat"'
        if rule not in toml:
            raise SystemExit(f"netlify.toml: no proxy rule /oscar/api/{name}/* -> {origin}:splat")
        if origin.rstrip("/") not in toml.split("Content-Security-Policy", 1)[1].split("\n", 1)[0]:
            raise SystemExit(f"netlify.toml: OSCAR's Content-Security-Policy doesn't allow {origin}")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    for dest, src in PAGES.items():
        page = (HERE / src).read_text(encoding="utf-8")
        check_self_contained(src, page)
        if src == "oscar.html":
            check_oscar(page)
        path = OUT / dest
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(page, encoding="utf-8")
    # Tools for the team and the clients we send them to, not for search engines.
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    for p in sorted(OUT.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(OUT)}  {p.stat().st_size / 1024:.0f} kB")


if __name__ == "__main__":
    main()
