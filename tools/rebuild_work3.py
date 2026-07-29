"""Rewrite work3.html to describe the whole Sharper Shape role.

The page covered FME and LiDAR360 only, while the CV describes Dagster on
Kubernetes, AWS S3 delivery, Mapbox vector tiling with tippecanoe, Luzmo
dashboards, PostgreSQL and a stack of Python tooling. The rebuilt skills page
cites this page as evidence for several of those, so the claim and the page
had to be reconciled. Content is drawn from the CV's own description of the
role, with no client names.

Also renames the page from "FME Data Integration" to reflect the real scope.
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

TITLE = "Geospatial Data Engineering at Sharper Shape"

BODY = """<h1>Geospatial Data Engineering at Sharper Shape</h1>
					<p class="project-meta"><span><i class="fas fa-calendar-alt" aria-hidden="true"></i>October 2022 &ndash; present</span><span><i class="fas fa-building" aria-hidden="true"></i>Sharper Shape Group</span><span><i class="fas fa-user-tie" aria-hidden="true"></i>Geospatial Data Engineer</span></p>
					<span class="section-label"><i class="fas fa-question-circle" style="margin-right:0.4em;"></i>The challenge</span>
					<p>Sharper Shape turns raw aerial inspection data into deliverables for electric utilities across North America. That work started out as manual desktop effort: FME workspaces launched by hand, exports assembled per project, nothing scheduled and nothing monitored. It did not scale with volume, a failed run was discovered rather than reported, and the process was difficult to audit after the fact.</p>
					<img src="images/fme.jpg" alt="FME workspace automating geospatial data integration" class="project-image"/>
					<span class="section-label"><i class="fas fa-drafting-compass" style="margin-right:0.4em;"></i>What I build</span>
					<p><strong style="color:#d8e0f0;">Orchestration.</strong> Legacy FME workspaces ported into production Dagster jobs running on Kubernetes, scheduled daily and fanning out per work item. Manual desktop runs became orchestrated workflows with monitoring, so failures surface instead of being noticed later.</p>
					<p><strong style="color:#d8e0f0;">Python delivery tooling.</strong> Automated asset import, validation, styling and delivery to AWS S3 using geopandas, pandas, requests, openpyxl and boto3. Large workbooks are streamed rather than held in memory, which keeps full-project runs inside pod memory limits.</p>
					<p><strong style="color:#d8e0f0;">Vector tiling.</strong> Geospatial layers published as Mapbox vector tiles with tippecanoe for the web map viewer. Multi-source parcel and asset datasets are merged and normalised into a common schema, then matched against reference registers.</p>
					<p><strong style="color:#d8e0f0;">Reporting and BI.</strong> Client deliverables generated in Python as multi-sheet XLSX exports and PDF technical reports. Business intelligence dashboards built in Luzmo and refreshed daily through the API, with each tile validated against ground-truth source data rather than assumed correct.</p>
					<p><strong style="color:#d8e0f0;">Quality assurance.</strong> QA/QC procedures for large geodatabases in ArcGIS and FME, including LiDAR classification accuracy checks with LiDAR360. Spatial data is integrated with Monday via its API so deliverables stay traceable to the work item that produced them.</p>
					<span class="section-label"><i class="fas fa-check-circle" style="margin-right:0.4em;"></i>Key outcomes</span>
					<div class="outcome-grid">
						<div class="outcome-card"><p><i class="fas fa-clock"></i> Hand-run desktop workspaces replaced by scheduled, monitored Dagster jobs on Kubernetes</p></div>
						<div class="outcome-card"><p><i class="fas fa-project-diagram"></i> Per-work-item fan-out, so a full project run parallelises instead of queueing behind one process</p></div>
						<div class="outcome-card"><p><i class="fas fa-memory"></i> Memory-bounded delivery: workbooks streamed to stay within pod limits on the largest runs</p></div>
						<div class="outcome-card"><p><i class="fas fa-layer-group"></i> Vector tiling lets the web viewer serve datasets far too large to ship as raw GeoJSON</p></div>
						<div class="outcome-card"><p><i class="fas fa-check-double"></i> Dashboard tiles validated against source data instead of trusted by default</p></div>
						<div class="outcome-card"><p><i class="fas fa-link"></i> Deliverables traceable back to their work item through the project management integration</p></div>
					</div>
					<div class="built-with">
					<div class="built-with-label"><i class="fas fa-microchip" style="margin-right:0.4em;"></i>Built with</div>
					<div class="tech-stack"><span class="tech-chip">FME</span><span class="tech-chip">Dagster</span><span class="tech-chip">Kubernetes</span><span class="tech-chip">Python</span><span class="tech-chip">GeoPandas</span><span class="tech-chip">Pandas</span><span class="tech-chip">boto3</span><span class="tech-chip">openpyxl</span><span class="tech-chip">AWS S3</span><span class="tech-chip">PostgreSQL</span><span class="tech-chip">Mapbox GL</span><span class="tech-chip">tippecanoe</span><span class="tech-chip">Luzmo</span><span class="tech-chip">ArcGIS Pro</span><span class="tech-chip">ArcGIS Online</span><span class="tech-chip">LiDAR360</span><span class="tech-chip">Monday API</span></div>
				</div>"""


def main():
    p = ROOT / "work3.html"
    t = p.read_text(encoding="utf-8")

    m = re.search(r"<h1>.*?<div class=\"built-with\">.*?</div>\s*</div>", t, re.S)
    if not m:
        raise SystemExit("work3 body anchors not found; aborting without writing")
    t = t.replace(m.group(0), BODY, 1)

    t = re.sub(r"<title>.*?</title>", f"<title>{TITLE} | Andres Gordon</title>", t, count=1, flags=re.S)
    p.write_text(t, encoding="utf-8", newline="")
    print(f"work3.html rewritten, title -> {TITLE}")

    # Homepage tile
    p = ROOT / "index.html"
    t = p.read_text(encoding="utf-8")
    old_h2 = "<h2>FME Data Integration</h2>"
    if old_h2 in t:
        t = t.replace(old_h2, "<h2>Geospatial Data Engineering</h2>", 1)
        t = t.replace("Automating QA of vector deliveries and LiDAR tiles at Sharper Shape",
                      "Dagster on Kubernetes, FME, and Python delivery pipelines", 1)
        p.write_text(t, encoding="utf-8", newline="")
        print("index.html tile updated")

    # OG card definition
    p = ROOT / "tools" / "make_images.py"
    t = p.read_text(encoding="utf-8")
    old = '("work3", "FME Data Integration", "Automated QA at production scale", "professional", "fme.jpg"),'
    new = '("work3", "Geospatial Data Engineering", "Dagster, Kubernetes, FME, Python", "professional", "fme.jpg"),'
    if old in t:
        p.write_text(t.replace(old, new, 1), encoding="utf-8", newline="")
        print("make_images.py OG card updated")

    # Meta description
    p = ROOT / "tools" / "inject_meta.py"
    t = p.read_text(encoding="utf-8")
    old = ('"FME data integration at Sharper Shape: automating QA of vector deliveries and "\n'
           '              "LiDAR classification tiles into repeatable, auditable production workflows.",')
    new = ('"Geospatial data engineering at Sharper Shape: Dagster on Kubernetes, FME, "\n'
           '              "Python delivery pipelines to AWS S3, and Mapbox vector tiling.",')
    if old in t:
        p.write_text(t.replace(old, new, 1), encoding="utf-8", newline="")
        print("inject_meta.py description updated")
    else:
        print("WARNING: inject_meta description not matched, update by hand")


if __name__ == "__main__":
    main()
