"""Generate sitemap.xml and robots.txt.

lastmod comes from each file's last git commit date, so it reflects reality
rather than a hand-typed guess.

Note on robots.txt: this site is a GitHub project page served under
/Portfolio/, but robots.txt is only read from the origin root
(eandresge.github.io/robots.txt). The file written here is therefore inert
until the site moves to a custom domain or a user page. Submit sitemap.xml
directly in Google Search Console instead.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
BASE = "https://eandresge.github.io/Portfolio"

# Higher priority for the entry point and the strongest project pages.
PRIORITY = {
    "index": "1.0",
    "geoqc": "0.9", "treeforge": "0.9", "powerornah": "0.9",
    "work": "0.8", "academic": "0.8", "education": "0.8",
    "visibility": "0.8", "risk": "0.8",
}
DEFAULT_PRIORITY = "0.6"


def last_commit_date(path):
    r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", path.name],
                       cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() or None


def main():
    pages = sorted(p for p in ROOT.glob("*.html") if not p.name.startswith("_"))

    rows = []
    for p in pages:
        slug = p.stem
        loc = f"{BASE}/" if slug == "index" else f"{BASE}/{p.name}"
        rows.append((loc, last_commit_date(p), PRIORITY.get(slug, DEFAULT_PRIORITY)))

    # index first, then by descending priority, then alphabetically.
    rows.sort(key=lambda r: (r[0] != f"{BASE}/", -float(r[2]), r[0]))

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, mod, pri in rows:
        out.append("  <url>")
        out.append(f"    <loc>{loc}</loc>")
        if mod:
            out.append(f"    <lastmod>{mod}</lastmod>")
        out.append(f"    <priority>{pri}</priority>")
        out.append("  </url>")
    out.append("</urlset>")
    out.append("")

    sm = ROOT / "sitemap.xml"
    sm.write_text("\n".join(out), encoding="utf-8", newline="\n")

    robots = f"""# This site is a GitHub project page served under /Portfolio/.
# robots.txt is only honoured at the origin root, so this file is INERT until
# the site moves to a custom domain or a user page. Until then, submit
# sitemap.xml directly in Google Search Console.
User-agent: *
Allow: /

Sitemap: {BASE}/sitemap.xml
"""
    rb = ROOT / "robots.txt"
    rb.write_text(robots, encoding="utf-8", newline="\n")

    print(f"sitemap.xml  {len(rows)} urls, {sm.stat().st_size} bytes")
    for loc, mod, pri in rows:
        print(f"  {pri}  {mod or '(no date)'}  {loc}")
    print(f"\nrobots.txt   {rb.stat().st_size} bytes (inert on a project page)")


if __name__ == "__main__":
    main()
