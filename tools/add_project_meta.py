"""Add a date / organisation / role line under each project page's H1.

Nobody could tell whether the network analysis was ANU 2016 or UEF 2022, or
whether a project was coursework, paid work or a hobby. That ambiguity makes
strong professional work read as indistinguishable from an exercise.

Only pages with direct evidence are filled in here:
  work.html role dates          -> the four professional pages
  course folder "Spring term 2020" + numbered exercise PDFs -> four academic
  GitHub repo creation dates    -> the two published personal tools
  thesis.pdf title page         -> work2 is the MSc thesis, September 2022

Pages left alone because the year is genuinely unknown: batch, network,
remote, pp1, and geoqc's exact year. Guessing a date on a CV-adjacent page is
worse than omitting it.
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

# page: (date, organisation, role/context)
META = {
    "geoqc.html": ("Sharper Shape Group", "Geospatial Data Engineer",
                   "Internal production tooling"),
    "treeforge.html": ("2026", "Personal project",
                       "Sole author · published on GitHub"),
    "powerornah.html": ("2026", "Personal project",
                        "Sole author · published on GitHub"),

    "work3.html": ("October 2022 – present", "Sharper Shape Group",
                   "Geospatial Data Engineer"),
    "work2.html": ("2020 – 2022", "LUKE / University of Eastern Finland",
                   "MSc thesis, September 2022"),
    "work1.html": ("August 2021 – February 2022", "Luonnonvarakeskus (LUKE)",
                   "Research Assistant, GIS Specialist"),
    "work4.html": ("October 2020 – June 2021", "Luonnonvarakeskus (LUKE)",
                   "GIS Specialist Trainee"),

    "visibility.html": ("Spring 2020", "University of Eastern Finland",
                        "Advanced GIS coursework"),
    "risk.html": ("Spring 2020", "University of Eastern Finland",
                  "Advanced GIS coursework"),
    "geo.html": ("Spring 2020", "University of Eastern Finland",
                 "Advanced GIS coursework"),
    "MCDA.html": ("Spring 2020", "University of Eastern Finland",
                  "Advanced GIS coursework"),
}

CSS = """
			/* Date / organisation / role, so coursework is never mistaken for
			   paid work and vice versa. */
			.project-meta {
				display: flex;
				flex-wrap: wrap;
				gap: 0.5em 1.6em;
				margin: 0.4em 0 1.6em;
				padding-bottom: 1.2em;
				border-bottom: 1px solid #2d3855;
				font-size: 0.78em !important;
				color: #b8c4dc !important;
			}
			.project-meta span { display: inline-flex; align-items: center; gap: 0.5em; }
			.project-meta i { color: #7db8f0; font-size: 0.95em; }
"""


def build(date, org, role):
    return (
        '<p class="project-meta">'
        f'<span><i class="fas fa-calendar-alt" aria-hidden="true"></i>{date}</span>'
        f'<span><i class="fas fa-building" aria-hidden="true"></i>{org}</span>'
        f'<span><i class="fas fa-user-tie" aria-hidden="true"></i>{role}</span>'
        "</p>"
    )


def fix(path, date, org, role):
    src = path.read_text(encoding="utf-8")
    if "project-meta" in src:
        return f"{path.name:20} already present"

    m = re.search(r"(<h1>.*?</h1>)", src, re.S)
    if not m:
        return f"{path.name:20} NO <h1>, skipped"

    src = src.replace(m.group(1), m.group(1) + "\n\t\t\t\t\t" + build(date, org, role), 1)

    i = src.rfind("</style>")
    if i == -1:
        return f"{path.name:20} NO </style>, skipped"
    src = src[:i] + CSS + "\t\t" + src[i:]

    path.write_text(src, encoding="utf-8", newline="")
    return f"{path.name:20} {date}  |  {org}"


if __name__ == "__main__":
    for name, (d, o, r) in META.items():
        print("  " + fix(ROOT / name, d, o, r))
    todo = ["batch.html", "network.html", "remote.html", "pp1.html"]
    print(f"\nleft for confirmation (year unknown): {', '.join(todo)}")
