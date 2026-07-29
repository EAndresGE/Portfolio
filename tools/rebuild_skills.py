"""Rebuild academic.html: evidence-linked skills instead of percentage bars.

The old page carried self-assessed percentages (ArcGIS Pro 90%, Python 75%).
Three problems:
  - unverifiable, and hiring managers discount them
  - they invite "so what is the missing 10%?"
  - they contradicted the evidence: Python sat at 75% while the two flagship
    projects on the site are Python CLI tools

Worse, the page omitted most of what the CV says the day job involves: Dagster
on Kubernetes, AWS S3 pipelines, Mapbox vector tiling with tippecanoe, Luzmo
dashboards, PostgreSQL, boto3, geopandas. The site described a GIS analyst
while the CV described a data engineer.

Every row now carries a tier and, wherever possible, a link to the project on
this site that demonstrates it. Rows whose only evidence is the current role
link to the Sharper Shape page.
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

TIERS = {
    "prod": ("Production", "Used daily in production systems"),
    "strong": ("Proficient", "Used on delivered professional or thesis work"),
    "working": ("Working", "Used on specific projects; would need ramp-up for production"),
}

# (name, tier, evidence label, evidence href or None)
GROUPS = [
    ("fas fa-cogs", "Data engineering &amp; orchestration", [
        ("FME", "prod", "FME at Sharper Shape", "work3.html"),
        ("Dagster on Kubernetes", "prod", "Sharper Shape", "work3.html"),
        ("Python &mdash; geopandas, pandas, shapely, pyproj", "prod", "GeoQC Flow", "geoqc.html"),
        ("AWS S3 delivery pipelines, boto3", "prod", "Sharper Shape", "work3.html"),
        ("PostgreSQL", "strong", "Sharper Shape", "work3.html"),
        ("Geodatabase QA/QC at scale", "prod", "GeoQC Flow", "geoqc.html"),
        ("REST API integration &mdash; Monday, ENTSO-E", "strong", "Power or Nah", "powerornah.html"),
    ]),
    ("fas fa-globe", "GIS platforms", [
        ("ArcGIS Pro", "prod", "Avalanche risk model", "risk.html"),
        ("ArcGIS Online", "strong", "Sharper Shape", "work3.html"),
        ("QGIS", "strong", "Rantalaidun geodatabase", "work4.html"),
        ("ArcGIS Desktop", "working", "Flying squirrel PPGIS", "work1.html"),
        ("Model Builder", "strong", "Multi-criteria site selection", "MCDA.html"),
    ]),
    ("fas fa-map-marked-alt", "Web mapping &amp; visualisation", [
        ("Mapbox GL, tippecanoe vector tiling", "prod", "Sharper Shape", "work3.html"),
        ("MapLibre GL", "strong", "Interactive viewshed map", "visibility.html"),
        ("Luzmo BI dashboards", "prod", "Sharper Shape", "work3.html"),
        ("Cartographic design", "strong", "Paper-cut cartography", "pp1.html"),
    ]),
    ("fas fa-chart-bar", "Spatial analysis &amp; modelling", [
        ("Regression modelling", "strong", "MSc thesis, moose-vehicle collisions", "work2.html"),
        ("Spatial statistics &mdash; Getis-Ord, kernel density", "strong", "PPGIS conflict analysis", "work1.html"),
        ("Geostatistics &mdash; Kriging, IDW", "strong", "Interpolation study", "geo.html"),
        ("Weighted overlay &amp; MCDA", "strong", "Avalanche risk index", "risk.html"),
        ("Terrain &amp; viewshed analysis", "strong", "Wind turbine visibility", "visibility.html"),
        ("R", "strong", "PPGIS statistical verification", "work1.html"),
        ("Network analysis", "working", "Light rail accessibility", "network.html"),
        ("MAXENT species distribution", "working", "LUKE, 2020&ndash;2021", "work.html"),
        ("SPSS, MATLAB", "working", "Fire impact analysis", "remote.html"),
    ]),
    ("fas fa-satellite", "Remote sensing &amp; point clouds", [
        ("Point clouds &mdash; LAS/LAZ, laspy", "strong", "TreeForge", "treeforge.html"),
        ("Canopy height modelling, crown segmentation", "strong", "TreeForge", "treeforge.html"),
        ("Raster &amp; satellite analysis", "strong", "Bushfire impact, Australia", "remote.html"),
        ("OpenDroneMap / WebODM", "working", "TreeForge", "treeforge.html"),
        ("LiDAR360", "working", "Sharper Shape", "work3.html"),
    ]),
    ("fas fa-file-export", "Reporting &amp; delivery", [
        ("Automated XLSX and PDF reporting in Python", "prod", "GeoQC Flow", "geoqc.html"),
        ("Batch processing pipelines &mdash; Python, R", "strong", "Open forest data", "batch.html"),
        ("Technical documentation", "prod", "TreeForge", "treeforge.html"),
    ]),
]

LANGUAGES = [("Spanish", "Mother tongue"),
             ("English", "Professional proficiency"),
             ("Finnish", "Elementary proficiency")]

CSS = """/* Skills layout */
			.skills-grid {
			  display: grid;
			  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
			  gap: 1.5em;
			  margin-top: 1.5em;
			}
			.skill-group {
			  background-color: #242d42;
			  border: 1.5px solid #2d3855;
			  border-radius: 8px;
			  padding: 1.5em;
			}
			.skill-group-title {
			  display: flex;
			  align-items: center;
			  gap: 0.6em;
			  font-size: 0.8em;
			  font-weight: 700;
			  letter-spacing: 0.08em;
			  text-transform: uppercase;
			  color: #b8c4dc;
			  margin-bottom: 1.2em;
			  padding-bottom: 0.6em;
			  border-bottom: 1px solid #2d3855;
			}
			.skill-group-title i { font-size: 1.1em; color: #7db8f0; }

			.skill-row {
			  padding: 0.7em 0;
			  border-bottom: 1px solid #1f2739;
			}
			.skill-row:last-child { border-bottom: 0; padding-bottom: 0; }
			.skill-head {
			  display: flex;
			  align-items: baseline;
			  justify-content: space-between;
			  gap: 0.8em;
			}
			.skill-name { color: #d8e0f0; font-size: 0.9em; font-weight: 600; line-height: 1.35; }
			.skill-ev { font-size: 0.76em; margin-top: 0.25em; color: #b8c4dc; }
			.skill-ev a { color: #7db8f0; }
			.skill-ev i { font-size: 0.85em; margin-right: 0.35em; opacity: 0.8; }

			/* Tier chips. Three honest bands beat a fabricated percentage. */
			.tier {
			  flex-shrink: 0;
			  font-size: 0.62em;
			  font-weight: 700;
			  letter-spacing: 0.1em;
			  text-transform: uppercase;
			  padding: 0.25em 0.7em;
			  border-radius: 999px;
			  white-space: nowrap;
			}
			.tier-prod    { background: rgba(45,125,210,0.16);  color: #7db8f0; border: 1px solid #2d7dd2; }
			.tier-strong  { background: rgba(26,158,166,0.16);  color: #5ed6dc; border: 1px solid #1a9ea6; }
			.tier-working { background: rgba(136,150,184,0.14); color: #b8c4dc; border: 1px solid #4a5980; }

			.tier-legend {
			  display: flex;
			  flex-wrap: wrap;
			  gap: 0.7em 1.4em;
			  margin: 1.4em 0 0.4em;
			  padding: 1em 1.2em;
			  background: #242d42;
			  border: 1.5px solid #2d3855;
			  border-radius: 8px;
			  font-size: 0.8em;
			}
			.tier-legend div { display: flex; align-items: center; gap: 0.6em; }
			.tier-legend span.lab { color: #b8c4dc; }

			.lang-list { display: flex; flex-wrap: wrap; gap: 0.8em; margin-top: 0.4em; }
			.lang-item {
			  background: #242d42;
			  border: 1.5px solid #2d3855;
			  border-radius: 8px;
			  padding: 0.8em 1.2em;
			}
			.lang-item strong { color: #d8e0f0; display: block; font-size: 0.95em; }
			.lang-item span { color: #b8c4dc; font-size: 0.8em; }
"""


def row(name, tier, label, href):
    cls = f"tier-{tier}"
    tier_name = TIERS[tier][0]
    if href:
        ev = (f'<div class="skill-ev"><i class="fas fa-link" aria-hidden="true"></i>'
              f'<a href="{href}">{label}</a></div>')
    else:
        ev = f'<div class="skill-ev">{label}</div>'
    return (f'\t\t\t\t\t\t\t<div class="skill-row">\n'
            f'\t\t\t\t\t\t\t\t<div class="skill-head">'
            f'<span class="skill-name">{name}</span>'
            f'<span class="tier {cls}">{tier_name}</span></div>\n'
            f'\t\t\t\t\t\t\t\t{ev}\n'
            f'\t\t\t\t\t\t\t</div>\n')


def build_body():
    out = ['<h1>Technical Skills</h1>']
    out.append('\t\t\t\t\t\t<p>Grouped by domain, with the project on this site that '
               'demonstrates each one. Percentages have been removed deliberately: they '
               'are unverifiable and invite the question of what the missing fraction is. '
               'Three bands and a link to real work say more.</p>')
    out.append('\t\t\t\t\t\t<div class="tier-legend">')
    for key in ("prod", "strong", "working"):
        nm, desc = TIERS[key]
        out.append(f'\t\t\t\t\t\t\t<div><span class="tier tier-{key}">{nm}</span>'
                   f'<span class="lab">{desc}</span></div>')
    out.append('\t\t\t\t\t\t</div>')
    out.append('\t\t\t\t\t\t<hr />')
    out.append('\n\t\t\t\t\t\t<div class="skills-grid">')

    for icon, title, rows in GROUPS:
        out.append('\n\t\t\t\t\t\t\t<div class="skill-group">')
        out.append(f'\t\t\t\t\t\t\t\t<div class="skill-group-title">'
                   f'<i class="{icon}" aria-hidden="true"></i> {title}</div>')
        for r in rows:
            out.append(row(*r).rstrip("\n"))
        out.append('\t\t\t\t\t\t\t</div>')

    out.append('\n\t\t\t\t\t\t</div><!-- end skills-grid -->')

    out.append('\n\t\t\t\t\t\t<h2 style="font-size:1.1em; margin-top:2em;">Languages</h2>')
    out.append('\t\t\t\t\t\t<div class="lang-list">')
    for name, level in LANGUAGES:
        out.append(f'\t\t\t\t\t\t\t<div class="lang-item"><strong>{name}</strong>'
                   f'<span>{level}</span></div>')
    out.append('\t\t\t\t\t\t</div>')
    return "\n".join(out)


def main():
    p = ROOT / "academic.html"
    t = p.read_text(encoding="utf-8")

    css_m = re.search(r"/\* Skills layout \*/.*?(?=\n\t\t\t/\* Visible back navigation)", t, re.S)
    body_m = re.search(r"<h1>Technical Skills</h1>.*?</div><!-- end skills-grid -->", t, re.S)
    if not css_m or not body_m:
        raise SystemExit("anchors not found; aborting without writing")

    n_bars = len(re.findall(r'class="skill-fill"', t))
    t = t.replace(css_m.group(0), CSS.rstrip("\n"), 1)
    t = t.replace(body_m.group(0), build_body(), 1)

    # The bar animation script is now dead code.
    t = re.sub(r"\n\t\t<!-- Animate progress bars on load -->\s*<script>.*?</script>\n",
               "\n", t, flags=re.S)

    p.write_text(t, encoding="utf-8", newline="")

    rows = sum(len(g[2]) for g in GROUPS)
    print(f"removed {n_bars} percentage bars and the animation script")
    print(f"wrote {len(GROUPS)} groups, {rows} skill rows, {len(LANGUAGES)} languages")
    linked = sum(1 for g in GROUPS for r in g[2] if r[3])
    print(f"{linked}/{rows} rows carry an evidence link")
    for key in ("prod", "strong", "working"):
        n = sum(1 for g in GROUPS for r in g[2] if r[1] == key)
        print(f"  {TIERS[key][0]:11} {n}")


if __name__ == "__main__":
    main()
