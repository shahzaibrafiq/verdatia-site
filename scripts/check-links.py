#!/usr/bin/env python3
"""Check every internal link and asset reference on the site resolves to a real file.

This site is raw HTML served straight from the repo root by GitHub Pages, with
no build step. Nothing sits between a typo and verdatia.com, so a mistyped href
is live the moment it is pushed and stays broken until a human happens to click
it.

Deliberately dependency-free (stdlib only) so CI needs no install step and this
can never break because of a package update.

Usage:  python3 scripts/check-links.py [site-root]
Exit:   0 all good, 1 broken references found
"""

import sys
import re
from pathlib import Path
from html.parser import HTMLParser

# Attributes that point at something which must exist.
REF_ATTRS = {"href", "src", "poster"}

# Schemes and forms that are not our problem.
EXTERNAL = re.compile(r"^(https?:|mailto:|tel:|data:|javascript:|#|//)", re.I)


class RefCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []  # (attr, value, line)

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in REF_ATTRS and value:
                self.refs.append((name, value.strip(), self.getpos()[0]))


def resolve(ref: str, page: Path, root: Path) -> Path | None:
    """Map an href to the file Pages would actually serve, or None if not ours."""
    if EXTERNAL.match(ref):
        return None

    # Strip fragment and query; neither affects which file is served.
    ref = ref.split("#", 1)[0].split("?", 1)[0]
    if not ref:
        return None

    if ref.startswith("/"):
        target = root / ref.lstrip("/")
    else:
        target = page.parent / ref

    # Pages serves a directory as its index.html. "/about/" and "/about" both
    # resolve to about/index.html.
    if ref.endswith("/") or (target.is_dir()):
        target = target / "index.html"
    elif not target.suffix:
        # Extensionless and not a real directory: Pages would try <name>.html
        # then <name>/index.html. Accept either.
        if (target.with_suffix(".html")).exists():
            target = target.with_suffix(".html")
        else:
            target = target / "index.html"

    try:
        return target.resolve()
    except OSError:
        return target


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    pages = sorted(p for p in root.rglob("*.html") if ".git" not in p.parts)

    if not pages:
        print(f"No HTML files found under {root}", file=sys.stderr)
        return 1

    broken: list[str] = []
    checked = 0

    for page in pages:
        collector = RefCollector()
        try:
            collector.feed(page.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:  # a parse failure is itself worth failing on
            broken.append(f"{page.relative_to(root)}: could not parse ({exc})")
            continue

        for attr, ref, line in collector.refs:
            target = resolve(ref, page, root)
            if target is None:
                continue
            checked += 1
            if not target.exists():
                broken.append(
                    f"{page.relative_to(root)}:{line}  {attr}=\"{ref}\"  ->  missing"
                )

    print(f"Checked {checked} internal references across {len(pages)} pages.")

    if broken:
        print(f"\n{len(broken)} broken reference(s):\n")
        for b in broken:
            print(f"  {b}")
        print("\nThese would be live on the site. Fix before merging.")
        return 1

    print("All internal links and assets resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
