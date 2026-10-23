"""Build ai.renewablox.com — RenewaBlox's AI tools — into ai/site/.

    /           the home page (index.html)
    /oscar/     OSCAR, the site model (oscar.html), served exactly as the team's own file
    404.html    for any other address

The home page and the 404 page wear the Atlas's brand, from the Atlas's own files: the build copies its
stylesheet, wordmarks and icons from atlas/root/ (BRAND) and fetches the two brand fonts as atlas/build.py
does (FONTS), so the two sites can't drift apart. OSCAR is copied as it is and keeps its own look.

The build checks the things that would otherwise break quietly:

  * OSCAR stores saved scenarios by input id, so every id a saved scenario can hold must still be on the
    page (SCENARIO_IDS);
  * the home page and the 404 page load nothing from elsewhere;
  * every origin OSCAR reaches (its Google font, its live sources and the proxies it falls back on) is
    allowed by its Content-Security-Policy in netlify.toml, and the policy allows no other.

Run:  python ai/build.py            (writes ai/site/, git-ignored)
      python -m http.server 8900 -d ai/site
Netlify runs it on every push to the renewablox-ai project's production branch (ai/netlify.toml).
Without the network (here, not on Netlify) the fonts are skipped with a warning and the pages fall back to
the system font. Standard library only.
"""
import hashlib
import os
import re
import shutil
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "site"
ATLAS_ROOT = HERE.parent / "atlas" / "root"
ON_NETLIFY = os.environ.get("NETLIFY") == "true"

PAGES = {
    "index.html": "index.html",
    "oscar/index.html": "oscar.html",
    "404.html": "404.html",
}

# The Atlas's brand files, served here at the same paths.
BRAND = [
    "assets/atlas.css",
    "assets/logos/renewablox-wordmark-dark.png",
    "assets/logos/renewablox-wordmark-light.png",
    "assets/favicon-32.png",
    "assets/apple-touch-icon.png",
    "favicon.ico",
]

# The brand fonts: the same files as atlas/build.py's FONTS (renewablox.com's own, licensed for the website,
# so not kept in this public repository), checked against the same hashes.
FONTS = {
    "assets/fonts/telegraf-regular.woff2": (
        "https://static.wixstatic.com/ufonts/cf5726_79e38b37da5449e5b14f405020faa098/woff2/file.woff2",
        "feca33b49819dbb4943b83db8d68e1f8840c92032b90f3a355902017e56d28bd"),
    "assets/fonts/garet-book.woff2": (
        "https://static.wixstatic.com/ufonts/e0c63f_dd8ef7e318764b8aa50aae38de0fb7c0/woff2/file.woff2",
        "30329680a639d076033f725b84ef0cab77df14b1797f2b487bd24f30e6496608"),
}

# Every input a saved OSCAR scenario holds (the September 2026 edition's 61). Add to this list; never take from it.
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
scenarioNameInput
""".split()

EXTERNAL_LOAD = re.compile(
    r"<(?:script|img|iframe|source|video|audio)\b[^>]*\bsrc\s*=\s*[\"']?(?:https?:)?//"
    r"|<link\b[^>]*\bhref\s*=\s*[\"']?(?:https?:)?//"
    r"|@import|url\(\s*[\"']?(?:https?:)?//",
    re.I)
# Links a reader follows, which no policy governs; every other address in OSCAR is one it loads or calls.
ANCHOR = re.compile(r"<a\b[^>]*>", re.I)
ORIGIN = re.compile(r"https://[a-z0-9.-]+\.[a-z]{2,}", re.I)


def check_self_contained(name, page):
    m = EXTERNAL_LOAD.search(page)
    if m:
        raise SystemExit(f"{name}: loads something from elsewhere: {page[m.start():m.start() + 120]!r}")


def oscar_policy():
    toml = (HERE / "netlify.toml").read_text(encoding="utf-8")
    m = re.search(r'for = "/oscar/\*"\s*\[headers\.values\]\s*Content-Security-Policy = "([^"]+)"', toml)
    if not m:
        raise SystemExit("netlify.toml: no Content-Security-Policy for /oscar/*")
    return m.group(1)


def check_oscar(page):
    ids = set(re.findall(r"<(?:input|select|textarea)\b[^>]*\bid=\"([^\"]+)\"", page))
    missing = [i for i in SCENARIO_IDS if i not in ids]
    if missing:
        raise SystemExit("oscar.html: saved scenarios need these inputs, now missing: " + ", ".join(missing))
    used = set(ORIGIN.findall(ANCHOR.sub("", page)))
    allowed = set(ORIGIN.findall(oscar_policy()))
    if used - allowed:
        raise SystemExit("netlify.toml: OSCAR's Content-Security-Policy doesn't allow " + ", ".join(sorted(used - allowed)))
    if allowed - used:
        raise SystemExit("netlify.toml: OSCAR's Content-Security-Policy allows what the page never uses: "
                         + ", ".join(sorted(allowed - used)))


def put_brand():
    for rel in BRAND:
        target = OUT / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ATLAS_ROOT / rel, target)


def put_fonts():
    """The brand fonts, fetched and checked against their hashes. A build without them (offline) warns, and the
    pages fall back to the system font; on Netlify it fails instead."""
    warnings = []
    for rel, (url, digest) in FONTS.items():
        try:
            data = urllib.request.urlopen(url, timeout=60).read()
        except OSError as e:
            if ON_NETLIFY:
                raise SystemExit(f"could not fetch {rel} from {url}: {e}")
            warnings.append(f"could not fetch {rel} ({e}), so the pages will fall back to the system font")
            continue
        got = hashlib.sha256(data).hexdigest()
        if got != digest:
            raise SystemExit(f"{url} is not the font {rel} was built with (sha256 {got}); check the new file and update FONTS")
        target = OUT / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return warnings


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    for dest, src in PAGES.items():
        data = (HERE / src).read_bytes()
        page = data.decode("utf-8")
        if src == "oscar.html":
            check_oscar(page)
        else:
            check_self_contained(src, page)
        path = OUT / dest
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    put_brand()
    warnings = put_fonts()
    # Tools for the team and the clients we send them to, not for search engines.
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    for p in sorted(OUT.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(OUT)}  {p.stat().st_size / 1024:.0f} kB")
    for w in warnings:
        print("warning: " + w)


if __name__ == "__main__":
    main()
