"""Rewrite the homepage tile titles and blurbs.

11 of 15 tiles were generic where the page behind them was specific:
"Risk modelling / Evaluating potential risk" fronting a page titled
"Avalanche Risk Modelling - Valais, Switzerland". The tile is what decides
whether anyone clicks, so it should carry the specific claim.

Blurbs lead with the concrete thing done, not the tool used. The two pages
that now have interactive maps say so, because that is the strongest signal
on the homepage.

Matched on each tile's href, so tile order can change freely. Idempotent.
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

# href: (h2, blurb)
TILES = {
    "geoqc.html": (
        "GeoQC Flow",
        "Python CLI that automates QA across multi-step FileGDB pipelines"),
    "treeforge.html": (
        "TreeForge",
        "Drone point cloud to a full forest inventory in one command"),
    "powerornah.html": (
        "Power or Nah",
        "M5StickC device showing the live electricity price at a glance"),
    "pp1.html": (
        "Paper-Cut Cartography of Quito",
        "Andean topography at 2,850 m as a layered paper-cut map"),

    "work3.html": (
        "FME Data Integration",
        "Automating QA of vector deliveries and LiDAR tiles at Sharper Shape"),
    "work2.html": (
        "Moose-Vehicle Collision Analysis",
        "18 forest structure variables regressed against collision density"),
    "work1.html": (
        "Public Participation GIS",
        "Social use areas against flying squirrel habitat, three municipalities"),
    "work4.html": (
        "GIS Database Administration",
        "Pasture digitisation and water sampling site selection for LUKE"),

    "visibility.html": (
        "Wind Turbine Visibility Analysis",
        "Interactive viewshed map of three proposed sites near Joensuu"),
    "risk.html": (
        "Avalanche Risk Modelling",
        "Interactive map ranking Valais settlements by avalanche risk"),
    "MCDA.html": (
        "Multi-Criteria Site Selection",
        "Siting a biathlon high school against four competing criteria"),
    "geo.html": (
        "Geostatistical Interpolation",
        "Interactive map comparing Kriging and IDW against the source grid"),
    "batch.html": (
        "Batch Processing Forest Data",
        "Python and R over a 16 x 16 m open forest inventory grid"),
    "network.html": (
        "Light Rail Accessibility",
        "Walking and driving service areas for every proposed stop, Canberra"),
    "remote.html": (
        "Remote Sensing and Fire Impact",
        "Before and after bushfire analysis in MATLAB, south-west Australia"),
}

ARTICLE = re.compile(r'<article\b.*?</article>', re.S)


def main():
    f = ROOT / "index.html"
    src = f.read_text(encoding="utf-8")
    changed = []
    missing = set(TILES)

    def fix(m):
        art = m.group(0)
        href = re.search(r'<a\s+href="([^"]+)"', art)
        if not href or href.group(1) not in TILES:
            return art
        slug = href.group(1)
        missing.discard(slug)
        h2, blurb = TILES[slug]

        old_h2 = re.search(r"<h2>(.*?)</h2>", art, re.S)
        old_p = re.search(r'(<div class="content">\s*<p>)(.*?)(</p>)', art, re.S)
        if not old_h2 or not old_p:
            return art

        before = (old_h2.group(1).strip(), re.sub(r"\s+", " ", old_p.group(2)).strip())
        art = art.replace(old_h2.group(0), f"<h2>{h2}</h2>")
        art = art.replace(old_p.group(0), old_p.group(1) + blurb + old_p.group(3))

        if before != (h2, blurb):
            changed.append((slug, before, (h2, blurb)))
        return art

    out = ARTICLE.sub(fix, src)
    if out != src:
        f.write_text(out, encoding="utf-8", newline="")

    for slug, before, after in changed:
        print(f"  {slug}")
        print(f"      was: {before[0]}  /  {before[1][:62]}")
        print(f"      now: {after[0]}  /  {after[1][:62]}")
    print(f"\n{len(changed)} tiles rewritten")
    if missing:
        print(f"WARNING: hrefs in the table but not found in index.html: {sorted(missing)}")

    # The typo that was in the MCDA blurb.
    body = f.read_text(encoding="utf-8")
    if "ArcGis" in body:
        print(f'WARNING: "ArcGis" still present {body.count("ArcGis")}x')
    else:
        print('"ArcGis" typo: gone')


if __name__ == "__main__":
    main()
