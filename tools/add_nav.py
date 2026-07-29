"""Add a visible "All projects" back link to every non-homepage page.

Before this, the only way back to the index was an unlabelled 80x80 logo
fixed at top:10px right:10px, which also overlapped content on narrow
screens. A decorative image should not be the sole navigation affordance.

Two page shapes exist:
  project pages   header already has <ul class="actions"> holding the
                  category badge -> prepend a link item to it
  section pages   header .inner is empty -> insert the list

Also tags the logo so it can shrink on small screens, where the text link
now carries navigation anyway.
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
SKIP = {"index.html"}

LINK = ('<li><a href="index.html" class="back-link">'
        '<i class="fas fa-arrow-left" aria-hidden="true"></i> All projects</a></li>')

CSS = """
			/* Visible back navigation. The logo alone was the only way home. */
			.back-link {
				display: inline-flex;
				align-items: center;
				gap: 0.5em;
				padding: 0.4em 0.95em;
				border: 1.5px solid #2d3855;
				border-radius: 4px;
				background: #242d42;
				color: #b8c4dc !important;
				font-size: 0.72em;
				font-weight: 700;
				letter-spacing: 0.09em;
				text-transform: uppercase;
				text-decoration: none;
				transition: background 0.18s, border-color 0.18s, color 0.18s;
			}
			.back-link:hover {
				background: #2d7dd2;
				border-color: #2d7dd2;
				color: #ffffff !important;
			}
			.home-logo { transition: width 0.2s, height 0.2s; }
			@media screen and (max-width: 736px) {
				.home-logo { width: 46px !important; height: 46px !important; top: 6px !important; right: 6px !important; }
			}
"""


def fix(path):
    src = path.read_text(encoding="utf-8")
    notes = []

    if "back-link" in src:
        return f"{path.name:22} already done"

    # 1. tag the fixed logo
    new = re.sub(r'(<img\s+src="images/logo\.png"\s+alt="Home")',
                 r'\1 class="home-logo"', src, count=1)
    if new != src:
        src = new
        notes.append("logo tagged")

    # 2. inject the link
    hdr = re.search(r'(<header id="header">\s*<div class="inner">)(.*?)(</div>\s*</header>)',
                    src, re.S)
    if not hdr:
        return f"{path.name:22} NO header/.inner, skipped"

    open_tag, inner, close_tag = hdr.groups()
    ul = re.search(r'(<ul class="actions">)(\s*)', inner)
    if ul:
        new_inner = inner.replace(ul.group(0), ul.group(1) + ul.group(2) + LINK + ul.group(2), 1)
        notes.append("link prepended to badge row")
    else:
        indent = "\n\t\t\t\t\t"
        new_inner = (inner.rstrip() + indent + '<ul class="actions">' +
                     indent + "\t" + LINK + indent + "</ul>\n\t\t\t\t")
        notes.append("actions list created")
    src = src.replace(open_tag + inner + close_tag, open_tag + new_inner + close_tag, 1)

    # 3. append CSS to the page's own style block
    i = src.rfind("</style>")
    if i == -1:
        return f"{path.name:22} NO </style>, skipped"
    src = src[:i] + CSS + "\t\t" + src[i:]
    notes.append("css")

    path.write_text(src, encoding="utf-8", newline="")
    return f"{path.name:22} " + ", ".join(notes)


if __name__ == "__main__":
    n = 0
    for f in sorted(ROOT.glob("*.html")):
        if f.name in SKIP:
            continue
        print("  " + fix(f))
        n += 1
    print(f"\n{n} pages processed")
