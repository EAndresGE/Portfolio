"""Generate favicons and 1200x630 Open Graph cards.

Rendered with ImageMagick rather than Pillow: Pillow is not installed on every
machine this repo gets cloned to, and `magick` is.

Fonts: the site's own faces, looked for in tools/fonts/ first, then on the
system, then falling back to Noto. They are not vendored because 1.1 MB of
TTF to regenerate nineteen JPEGs is a poor trade. To match the committed
cards exactly, drop these into tools/fonts/:

    SourceSerif4Display-Semibold.ttf   adobe-fonts/source-serif  (Desktop zip)
    SourceSans3-Regular.ttf            adobe-fonts/source-sans   (TTF zip)
    SourceSans3-Semibold.ttf           adobe-fonts/source-sans   (TTF zip)

Re-runnable: overwrites its outputs, touches nothing else.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "images"
OG = IMG / "og"
ICONS = IMG / "icons"
FONTDIR = Path(__file__).resolve().parent / "fonts"

W, H = 1200, 630
BG = "#0e0f11"
TEXT = "#f2efe9"
MUTED = "#a9a49c"
FAINT = "#8d8882"
ACCENT = "#d08b4f"

MAGICK = shutil.which("magick") or shutil.which("convert")


def font(*candidates):
    """First of the named faces that actually exists, else a Noto fallback."""
    for name in candidates:
        local = FONTDIR / name
        if local.exists():
            return str(local)
    for name in candidates:
        stem = Path(name).stem
        out = subprocess.run(["fc-match", "-f", "%{file}", stem],
                             capture_output=True, text=True).stdout.strip()
        if out and Path(out).exists() and stem.split("-")[0].lower() in Path(out).stem.lower():
            return out
    fallback = "Noto Serif" if "Serif" in candidates[0] else "Noto Sans"
    return subprocess.run(["fc-match", "-f", "%{file}", fallback],
                          capture_output=True, text=True).stdout.strip()


F_TITLE = font("SourceSerif4Display-Semibold.ttf")
F_SUB = font("SourceSans3-Regular.ttf")
F_BY = font("SourceSans3-Semibold.ttf")

# page, title, subtitle, source image (None = flat card)
PAGES = [
    ("index", "Andres Gordon", "Geospatial data engineer", "banner.jpg"),
    ("work", "Professional Experience", "Sharper Shape / LUKE / UEF", "banner.jpg"),
    ("education", "Education", "MSc Environmental Informatics, UEF", "banner.jpg"),
    ("academic", "Technical Skills", "ArcGIS Pro / QGIS / FME / Python / R", "banner.jpg"),

    ("geoqc", "GeoQC Flow", "Automated pipeline QC and reporting", "geoqc_preview.svg"),
    ("agol", "Asset Tracking Dashboards", "Captured against delivered, on ArcGIS Online", "agol_preview.svg"),
    ("treeforge", "TreeForge", "Drone point cloud to forest inventory", "treeforge_tile.jpg"),
    ("powerornah", "Power or Nah", "Live electricity price at a glance", "powerornah.jpg"),
    ("pp1", "Paper-Cut Cartography of Quito", "Andean topography as layered paper", "Quito_paper_cut.jpg"),

    ("work1", "Public Participation GIS", "Social use vs flying squirrel habitat", "professional1.jpg"),
    ("work2", "Moose-Vehicle Collision Analysis", "Forest structure and collision density", "mvc.jpg"),
    ("work3", "Geospatial Data Engineering", "Dagster, Kubernetes, FME, Python", "fme.jpg"),
    ("work4", "Geodatabase Administration for Rantalaidun", "LUKE, pasture digitisation", "r3.png"),

    ("visibility", "Visibility Analysis of Wind Turbines", "Viewshed modelling, Joensuu", "visibility.jpg"),
    ("risk", "Avalanche Risk Modelling in Valais", "Valais canton, Switzerland", "risk.jpg"),
    ("MCDA", "Multi-Criteria Site Selection", "Siting a biathlon high school, Joensuu", "mcda.png"),
    ("geo", "Interpolating Precipitation and Air Pollution", "Kriging and IDW compared", "pre.jpg"),
    ("batch", "Batch Processing Forest Data", "Python and R over open inventory", "batch.jpg"),
    ("network", "Light Rail Accessibility in Canberra", "Network analysis, Canberra", "pro.png"),
    ("remote", "Remote Sensing of Fire Impact in Australia", "MATLAB over NCI NetCDF", "remote.jpg"),
]

PAD = 72


def run(args):
    subprocess.run([MAGICK] + args, check=True)


def make_card(slug, title, subtitle, src):
    out = OG / f"{slug}.jpg"
    OG.mkdir(parents=True, exist_ok=True)

    size = 68 if len(title) <= 22 else (56 if len(title) <= 34 else 46)
    # The title block sits on the baseline of the card, subtitle under it.
    title_w = W - 2 * PAD

    args = []
    photo = IMG / src if src else None
    if photo and photo.exists():
        args += [str(photo), "-resize", f"{W}x{H}^", "-gravity", "center",
                 "-extent", f"{W}x{H}", "-colorspace", "sRGB"]
    else:
        args += ["-size", f"{W}x{H}", f"xc:{BG}"]

    args += [
        # Darken the photo so type always reads, then a bottom scrim.
        "(", "-size", f"{W}x{H}", f"xc:{BG}", ")",
        "-compose", "blend", "-define", "compose:args=62", "-composite",
        "(", "-size", f"{W}x{H}", f"gradient:none-{BG}", "-function", "polynomial", "2.2,-1.2,0.05", ")",
        "-compose", "over", "-composite",
        # Accent rule, top left.
        "-fill", ACCENT, "-draw", f"rectangle {PAD},{PAD} {PAD+64},{PAD+7}",
        # Title, auto-wrapped, anchored bottom left above the subtitle.
        # -gravity west inside the parens: left-align the wrapped lines,
        # otherwise caption: centres them within its box.
        "(", "-background", "none", "-fill", TEXT, "-font", F_TITLE,
        "-pointsize", str(size), "-size", f"{title_w}x", "-interline-spacing", "6",
        "-gravity", "west", f"caption:{title}", ")",
        "-gravity", "southwest", "-geometry", f"+{PAD}+{PAD+52}", "-composite",
        # Subtitle.
        "-font", F_SUB, "-pointsize", "28", "-fill", MUTED,
        "-annotate", f"+{PAD}+{PAD}", subtitle,
    ]
    if title != "Andres Gordon":
        args += ["-gravity", "northeast", "-font", F_BY, "-pointsize", "24",
                 "-fill", FAINT, "-annotate", f"+{PAD}+{PAD}", "ANDRES GORDON"]

    args += ["-quality", "85", "-interlace", "Plane", "-strip", str(out)]
    run(args)
    return out


def make_favicons():
    ICONS.mkdir(parents=True, exist_ok=True)
    logo = IMG / "logo.png"
    made = []
    for px, name in [(32, "favicon-32.png"), (192, "favicon-192.png")]:
        p = ICONS / name
        run([str(logo), "-resize", f"{px}x{px}", "-strip", str(p)])
        made.append(p)
    # iOS ignores transparency and composites on black, so flatten onto the
    # page colour instead.
    p = ICONS / "apple-touch-icon.png"
    run([str(logo), "-resize", "180x180", "-background", BG,
         "-flatten", "-strip", str(p)])
    made.append(p)
    ico = ROOT / "favicon.ico"
    run([str(logo), "-define", "icon:auto-resize=48,32,16", str(ico)])
    made.append(ico)
    return made


if __name__ == "__main__":
    if not MAGICK:
        sys.exit("ImageMagick not found: install it, or use `magick -version` to check.")
    print(f"title    {Path(F_TITLE).name}\nsubtitle {Path(F_SUB).name}\nbyline   {Path(F_BY).name}\n")

    for p in make_favicons():
        print(f"  {p.relative_to(ROOT)}  {p.stat().st_size / 1024:.1f} KB")

    print(f"\nOG cards ({W}x{H})")
    total = 0
    for slug, title, sub, src in PAGES:
        p = make_card(slug, title, sub, src)
        kb = p.stat().st_size / 1024
        total += kb
        print(f"  {p.name:18} {kb:6.1f} KB  <- {src or 'flat'}")
    print(f"\n  {len(PAGES)} cards, {total / 1024:.2f} MB")
