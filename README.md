# Portfolio — Andres Gordon

GIS and geospatial data engineering portfolio.
Live at **https://eandresge.github.io/Portfolio/**

15 projects across professional, academic and personal work: automated
production pipelines, spatial modelling, remote sensing and two interactive
web maps built from raw data.

## Layout

```
index.html              homepage, filterable project grid
academic.html           technical skills, each linked to the project proving it
education.html          degrees and certification
work.html               professional experience

geoqc.html              GeoQC Flow, pipeline QA tool (private repo)
treeforge.html          TreeForge, drone point cloud to forest inventory
powerornah.html         Power or Nah, IoT electricity price device
work1-4.html            professional projects
visibility.html         wind turbine viewshed, interactive MapLibre map
risk.html               avalanche risk model, interactive MapLibre map
MCDA / geo / batch / network / remote / pp1

assets/css/main.css     HTML5 UP Phantom template (vendor)
assets/css/main2.css    second template copy, used by 3 pages
assets/css/portfolio.css shared styles layered on top of both
maps/                   map data payloads (generated, base64 rasters inline)
images/og/              1200x630 Open Graph cards, one per page
tools/                  build and maintenance scripts
```

## Interactive maps

Two projects are real web maps rather than screenshots, both MapLibre GL with
a MapTiler basemap:

- **[visibility.html](visibility.html)** — viewsheds for three proposed wind
  turbine sites near Joensuu. Toggle sites, adjust overlay opacity, click a
  turbine or populated area for figures.
- **[risk.html](risk.html)** — avalanche risk across the Valais canton.

Map data lives in `maps/*/`. Viewshed rasters are embedded as base64 PNG image
sources so the pages need no tile server of their own.

## Tools

Everything under `tools/` is re-runnable and idempotent.

| Script | Purpose |
|---|---|
| `inject_meta.py` | SEO, Open Graph, Twitter, favicon and canonical tags on all 19 pages, plus `lang` and viewport fixes |
| `make_images.py` | favicons from `images/logo.png`, and the 19 OG cards |
| `make_sitemap.py` | `sitemap.xml` with `lastmod` from git, and `robots.txt` |
| `optimise_images.py` | caps images at a 1600 px long edge and re-encodes |
| `consolidate_css.py` | lifts CSS duplicated across pages into `portfolio.css` |
| `fix_tiles.py` | homepage tile titles and blurbs |
| `add_nav.py` | back-navigation link on every non-homepage page |
| `add_project_meta.py` | date / organisation / role line per project |
| `rebuild_skills.py` | evidence-linked skills page |
| `make_mcda_card.py` | generates `images/mcda.png` |

Typical flow after editing content:

```bash
python tools/inject_meta.py .     # resync metadata if a <title> changed
python tools/make_sitemap.py .    # refresh lastmod
python tools/make_images.py       # rebuild OG cards if a hero image changed
```

Local preview, which is required rather than optional:

```bash
python -m http.server 8765 --bind 127.0.0.1
```

Open http://127.0.0.1:8765/ — **not** the files directly. The MapTiler key is
origin-restricted, and `file://` sends no `Origin` header, so the maps fail
silently with 403s on tiles.

## Notes

- `robots.txt` is **inert**. This is a GitHub project page served under
  `/Portfolio/`, and `robots.txt` is only honoured at the origin root. Submit
  `sitemap.xml` directly in Google Search Console instead.
- The MapTiler key in `visibility.html` and `risk.html` is public by design but
  restricted to `eandresge.github.io`, `localhost` and `127.0.0.1`.
- `main.css` and `main2.css` are near-identical vendor copies. `main.css` has 17
  extra dead `button3` rules; the two differ in footer colours and three tile
  overlay colours. `portfolio.css` layers over both, so pages using either get
  the same shared components.

## Credits

Design based on [Phantom](https://html5up.net/phantom) by HTML5 UP, used under
the [CCA 3.0 licence](https://html5up.net/license). See `LICENSE.txt`.
Basemaps © [MapTiler](https://www.maptiler.com/) and
© [OpenStreetMap contributors](https://www.openstreetmap.org/copyright).
