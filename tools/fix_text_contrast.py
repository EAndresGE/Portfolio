"""Raise text contrast site-wide.

Body text was #8896b8: 5.48:1 on the page background and 4.64:1 on cards,
barely over the WCAG AA floor of 4.5 and unreadable under screen reflection.

Two tiers, so hierarchy survives instead of everything flattening to one value:

  body / reading text   -> #d8e0f0   12.22:1 page, 10.36:1 card
  secondary micro-text  -> #b8c4dc    9.23:1 page,  7.83:1 card

Decorative icons move with the secondary tier so they do not look dim beside
brighter text. Idempotent: re-running changes nothing.
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
SKIP = {"_contrast-preview.html"}

BODY = "#d8e0f0"
MUTED = "#b8c4dc"

# Selectors whose text is primary reading content.
BODY_SELECTORS = {
    "p, li",
    "#main p",
    ".outcome-card p",
    ".feature-card p",
    ".usecase-card p",
    ".stages-table td",
    ".edu-detail",
    ".job-duties li",
    ".remark-text",
}

OLD = re.compile(r"#(?:8896b8|c8d4e8)", re.I)
RULE = re.compile(r"([^{}\n]+)\{([^}]*)\}")


def fix_file(path):
    src = path.read_text(encoding="utf-8")
    body_hits = muted_hits = 0

    def rule_sub(m):
        nonlocal body_hits, muted_hits
        sel_raw, decls = m.group(1), m.group(2)
        if not OLD.search(decls):
            return m.group(0)
        sel = re.sub(r"\s+", " ", sel_raw.strip())
        target = BODY if sel in BODY_SELECTORS else MUTED
        new, n = OLD.subn(target, decls)
        if target == BODY:
            body_hits += n
        else:
            muted_hits += n
        return sel_raw + "{" + new + "}"

    out = RULE.sub(rule_sub, src)

    # Inline style attributes. The 1.05em lead paragraphs are body text; any
    # other inline use is small print.
    def inline_sub(m):
        nonlocal body_hits, muted_hits
        s = m.group(0)
        if not OLD.search(s):
            return s
        target = BODY if "1.05em" in s else MUTED
        new, n = OLD.subn(target, s)
        if target == BODY:
            body_hits += n
        else:
            muted_hits += n
        return new

    out = re.sub(r'style="[^"]*"', inline_sub, out)

    if out != src:
        path.write_text(out, encoding="utf-8", newline="")
    return body_hits, muted_hits


if __name__ == "__main__":
    tb = tm = 0
    print(f"{'file':22} {'body':>6} {'muted':>6}")
    print("-" * 36)
    for f in sorted(ROOT.glob("*.html")):
        if f.name in SKIP:
            continue
        b, m = fix_file(f)
        tb += b
        tm += m
        if b or m:
            print(f"{f.name:22} {b:>6} {m:>6}")
    print("-" * 36)
    print(f"{'TOTAL':22} {tb:>6} {tm:>6}   ({tb + tm} replacements)")

    left = sum(len(OLD.findall(f.read_text(encoding='utf-8')))
               for f in ROOT.glob("*.html") if f.name not in SKIP)
    print(f"\nremaining #8896b8 / #c8d4e8 in site files: {left}")
