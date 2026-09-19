"""Generate favicons and 1200x630 Open Graph cards for the portfolio.

Favicons come from images/logo.png. OG cards are built from each page's own
hero image where one exists, cropped to fill 1200x630, darkened, with a bottom
scrim and the page title. Pages with no usable photo (SVG-only logos) get a
flat card in the site palette.

Category accent colours match the site's existing system:
  professional #2d7dd2   academic #1a9ea6   personal #2ea855

Re-runnable: overwrites its outputs, touches nothing else.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "images"
OG = IMG / "og"
ICONS = IMG / "icons"

W, H = 1200, 630
BG = (14, 15, 17)          # #0e0f11
TEXT = (255, 255, 255)
MUTED = (136, 150, 184)    # #8896b8

ACCENT = {
    "professional": (45, 125, 210),   # #2d7dd2
    "academic": (26, 158, 166),       # #1a9ea6
    "personal": (46, 168, 85),        # #2ea855
}

FONTS = Path("C:/Windows/Fonts")
F_BOLD = FONTS / "segoeuib.ttf"
F_REG = FONTS / "segoeui.ttf"

# page, title, subtitle, category, source image (None = flat card)
PAGES = [
    ("index", "Andres Gordon", "Geospatial Data Engineer", "professional", "banner.jpg"),
    ("work", "Professional Experience", "Sharper Shape / LUKE / UEF", "professional", "banner.jpg"),
    ("education", "Education", "MSc Environmental Informatics, UEF", "professional", "banner.jpg"),
    ("academic", "Technical Skills", "ArcGIS Pro / QGIS / FME / Python / R", "professional", "banner.jpg"),

    ("geoqc", "GeoQC Flow", "Automated pipeline QC and reporting", "professional", None),
    ("treeforge", "TreeForge", "Drone point cloud to forest inventory", "personal", None),
    ("powerornah", "Power or Nah", "Live electricity price at a glance", "personal", "powerornah.jpg"),
    ("pp1", "Paper-Cut Cartography of Quito", "Andean topography as layered paper", "personal", "Quito_paper_cut.jpg"),

    ("work1", "Public Participation GIS", "Social use vs flying squirrel habitat", "professional", "professional1.jpg"),
    ("work2", "Moose-Vehicle Collision Analysis", "Forest structure and collision density", "professional", "mvc.jpg"),
    ("work3", "Geospatial Data Engineering", "Dagster, Kubernetes, FME, Python", "professional", "fme.jpg"),
    ("work4", "GIS Database Administration", "LUKE Rantalaidun project", "professional", "r3.png"),

    ("visibility", "Wind Turbine Visibility Analysis", "Viewshed modelling, Joensuu", "academic", "visibility.jpg"),
    ("risk", "Avalanche Risk Modelling", "Valais canton, Switzerland", "academic", "risk.jpg"),
    ("MCDA", "Multi-Criteria Site Selection", "Siting a biathlon high school, Joensuu", "academic", "mcda.png"),
    ("geo", "Geostatistical Interpolation", "Kriging and IDW compared", "academic", "pre.jpg"),
    ("batch", "Batch Processing Forest Data", "Python and R over open inventory", "academic", "batch.jpg"),
    ("network", "Light Rail Accessibility", "Network analysis, Canberra", "academic", "pro.png"),
    ("remote", "Remote Sensing and Fire Impact", "MATLAB over NCI NetCDF, Australia", "academic", "remote.jpg"),
]


def font(path, size):
    return ImageFont.truetype(str(path), size)


def crop_fill(im, w, h):
    """Scale and centre-crop to exactly w x h."""
    im = im.convert("RGB")
    s = max(w / im.width, h / im.height)
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                   Image.LANCZOS)
    left, top = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((left, top, left + w, top + h))


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def make_card(slug, title, subtitle, category, src):
    accent = ACCENT[category]

    if src and (IMG / src).exists():
        base = crop_fill(Image.open(IMG / src), W, H)
        # Darken so text always reads.
        base = Image.blend(base, Image.new("RGB", (W, H), BG), 0.55)
    else:
        base = Image.new("RGB", (W, H), BG)

    # Bottom scrim, strongest at the very bottom.
    scrim = Image.new("L", (1, H))
    for y in range(H):
        t = max(0.0, (y - H * 0.35) / (H * 0.65))
        scrim.putpixel((0, y), int(235 * (t ** 1.5)))
    base = Image.composite(Image.new("RGB", (W, H), BG),
                           base, scrim.resize((W, H)))

    d = ImageDraw.Draw(base)
    pad = 72

    # Accent bar, top left.
    d.rectangle([pad, pad, pad + 64, pad + 7], fill=accent)

    # Title, wrapped, sitting above the subtitle.
    size = 76 if len(title) <= 22 else (62 if len(title) <= 34 else 54)
    f_title = font(F_BOLD, size)
    lines = wrap(d, title, f_title, W - 2 * pad)
    f_sub = font(F_REG, 30)

    line_h = int(size * 1.18)
    block_h = len(lines) * line_h + 46
    y = H - pad - block_h

    for ln in lines:
        d.text((pad, y), ln, font=f_title, fill=TEXT)
        y += line_h
    d.text((pad, y + 8), subtitle, font=f_sub, fill=MUTED)

    # Byline, top right. Skipped where the title is already the name.
    if title != "Andres Gordon":
        f_by = font(F_BOLD, 26)
        label = "ANDRES GORDON"
        d.text((W - pad - d.textlength(label, font=f_by), pad - 4),
               label, font=f_by, fill=(216, 224, 240))

    OG.mkdir(parents=True, exist_ok=True)
    # JPEG: these are photographic and get fetched by every crawler that sees
    # the page, so size matters more than lossless text edges.
    out = OG / f"{slug}.jpg"
    base.save(out, "JPEG", quality=85, optimize=True, progressive=True)
    return out


def make_favicons():
    ICONS.mkdir(parents=True, exist_ok=True)
    logo = Image.open(IMG / "logo.png").convert("RGBA")

    made = []
    for size, name in [(32, "favicon-32.png"), (192, "favicon-192.png"),
                       (180, "apple-touch-icon.png")]:
        im = logo.resize((size, size), Image.LANCZOS)
        if name == "apple-touch-icon.png":
            # iOS ignores transparency and composites on black, so flatten.
            flat = Image.new("RGB", (size, size), BG)
            flat.paste(im, (0, 0), im)
            im = flat
        p = ICONS / name
        im.save(p, "PNG", optimize=True)
        made.append(p)

    ico = ROOT / "favicon.ico"
    logo.save(ico, sizes=[(16, 16), (32, 32), (48, 48)])
    made.append(ico)
    return made


if __name__ == "__main__":
    print("favicons")
    for p in make_favicons():
        print(f"  {p.relative_to(ROOT)}  {p.stat().st_size / 1024:.1f} KB")

    print(f"\nOG cards ({W}x{H})")
    total = 0
    for slug, title, sub, cat, src in PAGES:
        p = make_card(slug, title, sub, cat, src)
        kb = p.stat().st_size / 1024
        total += kb
        print(f"  {p.name:22} {cat:12} {kb:6.1f} KB  <- {src or 'flat'}")
    print(f"\n  {len(PAGES)} cards, {total / 1024:.2f} MB total")
