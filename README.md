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
visibility.html         wind turbine viewshed, interactive map
risk.html               avalanche risk model, interactive map
geo.html                interpolation comparison, interactive map
MCDA / batch / network / remote / pp1

assets/css/site.css     the design system: tokens, components, motion
assets/js/site.js       filter and scroll reveal, progressive enhancement
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
| `inject_meta.py` | SEO, Open Graph, Twitter, favicon and canonical tags on all 19 pages |
| `make_images.py` | favicons from `images/logo.png`, and the 19 OG cards, via ImageMagick |
| `make_sitemap.py` | `sitemap.xml` with `lastmod` from git, and `robots.txt` |
| `optimise_images.py` | caps images at a 1600 px long edge and re-encodes |

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

## The stylesheet

The site was built on the HTML5 UP Phantom template and no longer is. Every
page loads `assets/css/site.css` and nothing else, so there are no template
overrides, no `!important`, and no per-page `<style>` block. The template's
CSS, its jQuery bundle and the SCSS sources were removed once the last page
stopped referencing them, along with the one-off scripts that had migrated the
old markup.

`make_images.py` wants the site's own fonts in `tools/fonts/` (gitignored, see
the script header for where to get them) and falls back to Noto without them.

## Notes

- `robots.txt` is **inert**. This is a GitHub project page served under
  `/Portfolio/`, and `robots.txt` is only honoured at the origin root. Submit
  `sitemap.xml` directly in Google Search Console instead.
- The MapTiler key in `visibility.html`, `risk.html` and `geo.html` is public by
  design but restricted to `eandresge.github.io`, `localhost` and `127.0.0.1`.
  It 403s from `file://`, so the maps only render over a served origin.

## Credits

The site began as [Phantom](https://html5up.net/phantom) by HTML5 UP, under the
[CCA 3.0 licence](https://html5up.net/license). No template code remains: the
markup and stylesheet were replaced, and the last of the vendor files were
removed once nothing referenced them.
Type is [Source Serif 4](https://fonts.google.com/specimen/Source+Serif+4) and
[Source Sans 3](https://fonts.google.com/specimen/Source+Sans+3), both OFL.
Icons are [Font Awesome Free](https://fontawesome.com/license/free).
Basemaps © [MapTiler](https://www.maptiler.com/) and
© [OpenStreetMap contributors](https://www.openstreetmap.org/copyright).
