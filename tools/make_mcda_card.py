"""Build a distinct image for the MCDA project page.

MCDA.html and batch.html both used images/batch.jpg, so the homepage showed
the same picture twice, and neither page's image related to what it described.
No biathlon-school map export survives, so this draws the four competing
criteria from the Exercise 4 brief instead.

Palette matches the site's academic category (teal #1a9ea6).
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "images" / "mcda.png"

W, H = 1600, 1000
BG = (27, 32, 48)
CARD = (36, 45, 66)
BORDER = (45, 56, 85)
TEAL = (26, 158, 166)
TEAL_HI = (94, 214, 220)
TEXT = (216, 224, 240)
MUTED = (184, 196, 220)

FONTS = Path("C:/Windows/Fonts")
F_B, F_R = FONTS / "segoeuib.ttf", FONTS / "segoeui.ttf"

# (direction, criterion, detail)
CRITERIA = [
    ("MAX", "Distance to existing high schools", "avoid competing with current provision"),
    ("MIN", "Distance to training facilities", "shooting range and ski trails within reach"),
    ("MAX", "Youth population within 3 km", "catchment of potential students"),
    ("AVOID", "Within 100 m of inland water", "hard exclusion applied as a mask"),
]


def f(p, s):
    return ImageFont.truetype(str(p), s)


im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)

pad = 90
d.rectangle([pad, pad, pad + 80, pad + 8], fill=TEAL)

d.text((pad, pad + 34), "FOUR COMPETING CRITERIA", font=f(F_B, 34), fill=TEAL_HI)

# Four criteria rows. No project title here: the homepage tile overlays its own
# label and MCDA.html has an <h1> directly above, so a baked-in title showed up
# twice on top of itself.
top = pad + 110
row_h = 158
gap = 22
badge_w = 128

for i, (direction, name, detail) in enumerate(CRITERIA):
    y = top + i * (row_h + gap)
    d.rounded_rectangle([pad, y, W - pad, y + row_h], radius=10,
                        fill=CARD, outline=BORDER, width=2)
    # Left accent stripe.
    d.rounded_rectangle([pad, y, pad + 6, y + row_h], radius=3, fill=TEAL)

    bx = pad + 34
    by = y + row_h // 2 - 21
    d.rounded_rectangle([bx, by, bx + badge_w, by + 42], radius=6,
                        fill=(18, 58, 62), outline=TEAL, width=2)
    fb = f(F_B, 22)
    tw = d.textlength(direction, font=fb)
    d.text((bx + (badge_w - tw) / 2, by + 9), direction, font=fb, fill=TEAL_HI)

    tx = bx + badge_w + 42
    d.text((tx, y + 44), name, font=f(F_B, 42), fill=TEXT)
    d.text((tx, y + 100), detail, font=f(F_R, 29), fill=MUTED)

    # Criterion number, right aligned.
    fn = f(F_B, 44)
    num = str(i + 1)
    d.text((W - pad - 46 - d.textlength(num, font=fn) / 2, y + row_h // 2 - 30),
           num, font=fn, fill=(58, 72, 104))

foot = "Weighted overlay in ArcGIS Pro Model Builder  \u00b7  Cost Surface  \u00b7  Cost Distance"
d.text((pad, H - pad + 6), foot, font=f(F_R, 25), fill=(120, 134, 168))

im.save(OUT, "PNG", optimize=True)
im.convert("P", palette=Image.ADAPTIVE, colors=128).save(OUT, "PNG", optimize=True)
print(f"{OUT.relative_to(ROOT)}  {W}x{H}  {OUT.stat().st_size / 1024:.0f} KB")
