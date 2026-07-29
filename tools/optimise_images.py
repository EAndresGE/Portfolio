"""Resize and re-encode oversized images.

The site shipped 8.7 MB of images into containers at most ~1000 px wide.
visibility.jpg alone was 3433 px wide and 789 KB, displayed at roughly 700 px.

Caps the long edge at 1600 px (comfortable 2x for the widest container) and
re-encodes. Photos go to progressive JPEG q82. PNGs stay PNG, because the ones
here are screenshots and JPEG would fringe the text.

Skips images/og/ and images/icons/ (already generated at their target size)
and anything already small enough.
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
IMG = ROOT / "images"
MAX_EDGE = 1600
JPEG_Q = 82
SKIP_DIRS = {"og", "icons"}
SKIP_FILES = {"logo.png"}          # favicon source, already small
MIN_SAVING = 0.03                  # ignore sub-3% wins, not worth the churn


def process(p):
    before = p.stat().st_size
    im = Image.open(p)
    w, h = im.size
    resized = ""

    if max(w, h) > MAX_EDGE:
        s = MAX_EDGE / max(w, h)
        im = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
        resized = f"{w}x{h} -> {im.width}x{im.height}"

    tmp = p.with_suffix(p.suffix + ".tmp")
    if p.suffix.lower() in (".jpg", ".jpeg"):
        im.convert("RGB").save(tmp, "JPEG", quality=JPEG_Q,
                               optimize=True, progressive=True)
    else:
        # These PNGs are maps and screenshots: keep PNG so labels stay crisp
        # (JPEG fringes text), but quantise to a 256-colour palette, which
        # maps tolerate well and which cuts size by roughly 60%.
        # Only safe when the alpha channel carries nothing.
        opaque = ("A" not in im.getbands()) or im.getchannel("A").getextrema()[0] == 255
        if opaque:
            im = im.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=256)
            resized = (resized + ", 256-colour palette").lstrip(", ")
        im.save(tmp, "PNG", optimize=True)

    after = tmp.stat().st_size
    if after >= before * (1 - MIN_SAVING):
        tmp.unlink()
        return before, before, f"kept ({resized or 'no gain'})"

    tmp.replace(p)
    return before, after, resized or "re-encoded"


if __name__ == "__main__":
    files = [p for p in sorted(IMG.rglob("*"))
             if p.is_file()
             and p.suffix.lower() in (".jpg", ".jpeg", ".png")
             and not (set(p.relative_to(IMG).parts[:-1]) & SKIP_DIRS)
             and p.name not in SKIP_FILES]

    tb = ta = 0
    print(f"{'file':26} {'before':>9} {'after':>9} {'saved':>7}  note")
    print("-" * 78)
    for p in files:
        b, a, note = process(p)
        tb += b
        ta += a
        pct = 0 if b == a else 100 * (b - a) / b
        print(f"{p.name:26} {b/1024:8.0f}K {a/1024:8.0f}K {pct:6.1f}%  {note}")
    print("-" * 78)
    print(f"{'TOTAL':26} {tb/1e6:8.2f}M {ta/1e6:8.2f}M "
          f"{100*(tb-ta)/tb if tb else 0:6.1f}%")
