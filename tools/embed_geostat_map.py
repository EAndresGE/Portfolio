"""Embed the standalone geostatistics map into geo.html.

The source (geostatistics/webmap/site/geostat_map.html) is a full standalone
page. Dropping its CSS into the portfolio raw would break in three ways:

1. `.row` collides with Phantom's grid, which sets margin-left:-2em on .row and
   padding-left:2em on its children. The map's checkbox rows would visibly
   break. Renamed to .gm-row.
2. Generic ids (#panel, #stats, #reset, #op, #loading, #map) risk colliding
   with the page or template. All prefixed gm-.
3. This map uses LIGHT furniture (white panel, dataviz-light basemap), but
   portfolio.css sets `p, li` and `h1..h4` to #d8e0f0 for the dark site. Any
   unclassed text inside the panel would go near-white on white. Every rule is
   scoped under #gm-wrap, which also raises specificity above the template.

Also swaps the API key for the origin-restricted one and demotes the panel's
<h1> to <h2>, since geo.html already has an h1.

Transformation, not transcription: re-run it if the source map changes.
"""
import re
import sys
from pathlib import Path

SRC = Path(r"C:\Users\andog\Documents\geostatistics\webmap\site\geostat_map.html")
ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
TARGET = ROOT / "geo.html"

OLD_KEY = "UuDqdYQZsiCZCO3rPNQt"
NEW_KEY = "YvOMYo8YmDtoVsNSbaqF"

IDS = ["map-wrap", "map", "panel", "p-head", "p-body", "stats", "loading",
       "seg-surf", "tg-samples", "op-val", "op", "reset"]
CLASSES = ["row"]          # the only genuine collision found
WRAP = "gm-wrap"

# Selectors that must NOT be scoped under #gm-wrap.
NO_SCOPE = re.compile(r"^(html|body|\*|:root|#gm-wrap|\.maplibregl-)")


def rename_ids(s):
    out = s
    for i in IDS:
        out = re.sub(r'getElementById\("' + re.escape(i) + r'"\)',
                     f'getElementById("gm-{i}")', out)
        out = re.sub(r'\bid="' + re.escape(i) + r'"', f'id="gm-{i}"', out)
        out = re.sub(r'container:\s*"' + re.escape(i) + r'"',
                     f'container: "gm-{i}"', out)
        # CSS selectors: #id followed by a non-identifier char
        out = re.sub(r'#' + re.escape(i) + r'(?![\w-])', f'#gm-{i}', out)
    return out


def rename_classes(s):
    out = s
    for c in CLASSES:
        out = re.sub(r'\.' + re.escape(c) + r'(?![\w-])', f'.gm-{c}', out)          # CSS
        out = re.sub(r'class="' + re.escape(c) + r'(?=["\s])', f'class="gm-{c}', out)  # static
        out = re.sub(r"'(\s*)" + re.escape(c) + r"(\s*)'", r"'\1gm-" + c + r"\2'", out)
        out = out.replace(f'class=\\"{c}', f'class=\\"gm-{c}')
        out = out.replace(f"'<label class=\"{c}", f"'<label class=\"gm-{c}")
        out = out.replace(f'"{c}"', f'"gm-{c}"') if f'classList' in out else out
    return out


def scope_css(css):
    """Prefix every rule with #gm-wrap so nothing leaks either direction."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out, i, n = [], 0, len(css)
    while i < n:
        at, brace = css.find("@", i), css.find("{", i)
        if brace == -1:
            break
        if at != -1 and at < brace:                      # at-rule: recurse inside
            j = css.find("{", at)
            d, k = 0, j
            while k < n:
                if css[k] == "{":
                    d += 1
                elif css[k] == "}":
                    d -= 1
                    if d == 0:
                        break
                k += 1
            head = css[at:j].strip()
            out.append(head + " {\n" + scope_css(css[j + 1:k]) + "\n}")
            i = k + 1
            continue
        end = css.find("}", brace)
        if end == -1:
            break
        sel = re.sub(r"\s+", " ", css[i:brace]).strip()
        decl = re.sub(r"\s+", " ", css[brace + 1:end]).strip()
        i = end + 1
        if not sel or not decl:
            continue

        parts = []
        for p in (x.strip() for x in sel.split(",")):
            if not p:
                continue
            if p.startswith("body.standalone"):
                parts = []                                # standalone shell: drop
                break
            if p in ("html, body", "html", "body"):
                parts = []
                break
            if p == ":root":
                parts.append(f"#{WRAP}")                  # scope the custom props
            elif p == "*":
                parts.append(f"#{WRAP} *")
            elif NO_SCOPE.match(p):
                parts.append(p)
            else:
                parts.append(f"#{WRAP} {p}")
        if parts:
            out.append(", ".join(parts) + " { " + decl + " }")
    return "\n\t\t\t".join(out)


def main():
    src = SRC.read_text(encoding="utf-8")

    css = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
    body = re.search(r'(<div id="map-wrap">.*?</div>\s*)(?=<script)', src, re.S).group(1)
    js = re.findall(r"<script>(.*?)</script>", src, re.S)[-1]

    css, body, js = (rename_ids(x) for x in (css, body, js))
    css, body, js = (rename_classes(x) for x in (css, body, js))

    js = js.replace(OLD_KEY, NEW_KEY)
    body = body.replace("<h1>", "<h2>").replace("</h1>", "</h2>")
    css = css.replace(".gm-p-head h1", ".gm-p-head h2").replace(".p-head h1", ".p-head h2")

    scoped = scope_css(css)
    scoped = (f"#{WRAP} {{ position: relative; width: 100%; height: 620px; "
              f"margin: 1em 0 0.8em; border-radius: 8px; overflow: hidden; "
              f"border: 1px solid #2d3855; background: #fff; }}\n"
              f"\t\t\t@media (max-width: 980px) {{ #{WRAP} {{ height: 560px; }} }}\n"
              f"\t\t\t@media (max-width: 640px) {{ #{WRAP} {{ height: 470px; }} }}\n"
              f"\t\t\t/* This map has light furniture; the site's dark text rules must not\n"
              f"\t\t\t   bleed into the white panel. */\n"
              f"\t\t\t#{WRAP} p, #{WRAP} li, #{WRAP} h1, #{WRAP} h2, #{WRAP} h3 "
              f"{{ color: inherit; }}\n\t\t\t" + scoped)

    t = TARGET.read_text(encoding="utf-8")
    if "gm-wrap" in t:
        raise SystemExit("geo.html already has the map; nothing done")

    # maplibre CSS
    t = t.replace('<link rel="stylesheet" href="assets/css/fontawesome-all.min.css" />',
                  '<link rel="stylesheet" href="assets/css/fontawesome-all.min.css" />\n'
                  '\t\t<link rel="stylesheet" href="https://unpkg.com/maplibre-gl@5.24.0/dist/maplibre-gl.css" />',
                  1)

    # CSS into the page's own style block
    i = t.rfind("</style>")
    t = t[:i] + "\n\t\t\t/* ===== Interactive geostatistics map (MapLibre GL) ===== */\n\t\t\t" \
        + scoped + "\n\t\t" + t[i:]

    # Markup replaces the static image, which becomes the noscript fallback
    old_img = re.search(r'\t*<img src="images/pre\.jpg"[^>]*/>', t)
    if not old_img:
        raise SystemExit("static image anchor not found in geo.html")
    caption = ('\n\t\t\t\t\t<span class="gm-caption"><i class="fas fa-hand-pointer" '
               'aria-hidden="true"></i>Switch between the original grid, Kriging, IDW and '
               'their difference. Toggle the 10 km samples and click one for its '
               'leave-one-out residual.</span>'
               '\n\t\t\t\t\t<noscript>\n\t\t\t\t\t\t' + old_img.group(0).strip() + '\n\t\t\t\t\t</noscript>')
    t = t.replace(old_img.group(0), "\t\t\t\t\t" + body.strip() + caption, 1)

    # Scripts at the end
    t = t.replace("\t\t<script src=\"assets/js/main.js\"></script>",
                  "\t\t<script src=\"assets/js/main.js\"></script>\n\n"
                  "\t\t<!-- Interactive geostatistics map -->\n"
                  "\t\t<script src=\"https://unpkg.com/maplibre-gl@5.24.0/dist/maplibre-gl.js\"></script>\n"
                  "\t\t<script src=\"maps/geostat/geostat_data.js\"></script>\n"
                  "\t\t<script>\n" + js.strip() + "\n\t\t</script>", 1)

    TARGET.write_text(t, encoding="utf-8", newline="")
    print(f"geo.html: map embedded")
    print(f"  scoped CSS rules : {scoped.count('{')}")
    print(f"  ids prefixed     : {len(IDS)}")
    print(f"  classes renamed  : {CLASSES}")
    print(f"  api key swapped  : {OLD_KEY[:8]}... -> {NEW_KEY[:8]}...")
    print(f"  key leaked?      : {OLD_KEY in t}")


if __name__ == "__main__":
    main()
