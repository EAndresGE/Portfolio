"""Two performance fixes.

1. Self-host Font Awesome. Every page loaded it from cdnjs while an identical
   local copy (5.15.4, all 75 icons used by the site, all webfonts present)
   sat unused in assets/css/. A blocked or slow CDN erased the entire filter
   bar, every section heading icon and both social links.

2. loading="lazy" on the homepage project tiles below the fold. 15 tile
   images were all fetched eagerly on first paint. The first three are left
   eager so the largest contentful paint is unaffected.

Idempotent.
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

CDN = re.compile(
    r'<link\s+rel="stylesheet"\s+href="https://cdnjs\.cloudflare\.com/ajax/libs/'
    r'font-awesome/[\d.]+/css/all\.min\.css"\s*/?>')
LOCAL = '<link rel="stylesheet" href="assets/css/fontawesome-all.min.css" />'

EAGER_TILES = 3   # leave the first N tile images eager for LCP


def swap_fontawesome():
    n = 0
    for f in sorted(ROOT.glob("*.html")):
        src = f.read_text(encoding="utf-8")
        out, k = CDN.subn(LOCAL, src)
        if k:
            f.write_text(out, encoding="utf-8", newline="")
            n += 1
            print(f"  {f.name:22} {k} link(s) -> local")
    return n


def lazy_tiles():
    f = ROOT / "index.html"
    src = f.read_text(encoding="utf-8")

    m = re.search(r'(<section class="tiles">)(.*?)(</section>)', src, re.S)
    if not m:
        print("  index.html: no <section class=\"tiles\"> found, skipped")
        return 0

    head, body, tail = m.groups()
    imgs = list(re.finditer(r"<img\b[^>]*>", body))
    added = 0
    out = body
    # Work backwards so earlier offsets stay valid.
    for i in range(len(imgs) - 1, -1, -1):
        if i < EAGER_TILES:
            continue
        tag = imgs[i].group(0)
        if "loading=" in tag:
            continue
        new = tag[:-1].rstrip()
        new = new[:-1].rstrip() + ' loading="lazy" decoding="async" />' \
            if new.endswith("/") else new + ' loading="lazy" decoding="async" />'
        out = out[:imgs[i].start()] + new + out[imgs[i].end():]
        added += 1

    if added:
        f.write_text(src.replace(head + body + tail, head + out + tail),
                     encoding="utf-8", newline="")
    print(f"  index.html: {len(imgs)} tile images, "
          f"{added} marked lazy, first {EAGER_TILES} left eager")
    return added


if __name__ == "__main__":
    print("self-hosting Font Awesome")
    n = swap_fontawesome()
    print(f"  {n} pages updated\n")

    print("lazy-loading below-fold tiles")
    lazy_tiles()

    left = sum(1 for f in ROOT.glob("*.html")
               if "cdnjs.cloudflare.com" in f.read_text(encoding="utf-8"))
    print(f"\npages still referencing cdnjs: {left}")
