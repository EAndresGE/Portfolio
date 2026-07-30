"""Recolour treeforge.html and powerornah.html from green to the blue scheme.

Both pages used the personal-category green throughout, which read as a
different site rather than a different category. Remapped onto the exact
palette geoqc.html uses so the project pages look like one system.

The homepage tiles and filter chips keep their green, because that is the
category colour-coding and it still works there. Only the page interiors change.

Mapping is explicit rather than a hue rotation so nothing semantic moves:
amber/orange chips (JSON, PDF, prototype badge) and the purple negative-price
colour on Power or Nah are deliberately left alone.
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
FILES = ["treeforge.html", "powerornah.html"]

# green -> geoqc blue equivalent
MAP = {
    "#2ea855": "#2d7dd2",   # accent            -> geoqc accent
    "#69f0ae": "#5ba3f5",   # bright accent     -> geoqc bright accent
    "#2d4a2f": "#2d3855",   # card border       -> geoqc border
    "#1a2a1c": "#242d42",   # card background   -> geoqc card
    "#122014": "#1a2d4a",   # emphasis card     -> geoqc engine node
    "#0d1f0e": "#111827",   # preview panel     -> geoqc report preview
    "#0a1a0b": "#003049",   # gradient start    -> geoqc report header
    "#060f07": "#0d1117",   # code block bg     -> geoqc cli block
    "#4a6b4c": "#b8c4dc",   # code comment      -> site muted text
    "#1e2d20": "#1f2739",   # table row rule
    "#141f15": "#1a2235",   # table stripe
    "#1e3a20": "#1a2d4a",   # emphasis block
    "#7aadcc": "#b8c4dc",   # stray label colour, already off-palette
    "#0b1a0c": "#111827",   # logo tile backdrop
}

# Anything matching this after the remap is reported, not changed.
GREENISH = re.compile(r"#(?:[0-9a-f]{2})?(?:[4-9a-f][0-9a-f])(?:[0-9a-f]{2})?$", re.I)


def greenish(hexcol):
    """True if the green channel clearly dominates."""
    h = hexcol.lstrip("#")
    if len(h) != 6:
        return False
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return g > r + 18 and g > b + 18


def main():
    for name in FILES:
        p = ROOT / name
        t = p.read_text(encoding="utf-8")
        before = dict((c, len(re.findall(c, t, re.I))) for c in MAP)

        out = t
        for src, dst in MAP.items():
            out = re.sub(re.escape(src), dst, out, flags=re.I)

        p.write_text(out, encoding="utf-8", newline="")
        n = sum(before.values())
        print(f"{name}: {n} colour instances remapped")

        left = sorted({c for c in re.findall(r"#[0-9a-fA-F]{6}", out) if greenish(c)})
        print(f"  green-dominant colours remaining: {left if left else 'none'}")


if __name__ == "__main__":
    main()
