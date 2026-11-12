#!/usr/bin/env python3
"""Read-only bilingual / asset sanity checks for AL SAAB GROUP review pages."""
from __future__ import annotations
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["index.html", "housing.html", "hotels.html"]
ARABIC = re.compile(r"[\u0600-\u06FF]")

class Inspector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.errors = []
        self.images = []
        self.headings = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "data-ar" in a or "data-en" in a:
            if not a.get("data-ar", "").strip() or not a.get("data-en", "").strip():
                self.errors.append("Incomplete Arabic/English text pair")
            if ARABIC.search(a.get("data-en", "")):
                self.errors.append("Untranslated Arabic found in data-en")
        if tag in ("h1", "h2", "h3"):
            self.headings += 1
            if not a.get("data-ar") or not a.get("data-en"):
                self.errors.append(f"Missing bilingual heading: {tag}")
        if tag == "img":
            self.images.append(a.get("src", ""))

def main():
    for page in PAGES:
        path = ROOT / page
        if not path.is_file():
            raise SystemExit(f"Missing page: {page}")
        text = path.read_text(encoding="utf-8")
        parser = Inspector()
        parser.feed(text)
        if parser.headings < 1 or parser.errors:
            raise SystemExit(f"{page}: bilingual issues: {parser.errors}")
        for image in parser.images:
            if image and not image.startswith(("http://", "https://", "data:")) and not (ROOT / image.split("?")[0]).is_file():
                raise SystemExit(f"{page}: missing image: {image}")
        if "lang=" not in text or "dir=" not in text:
            raise SystemExit(f"{page}: language/direction handling missing")
        if "#D4AF37" not in text or "#101e30" not in text:
            raise SystemExit(f"{page}: institutional palette missing")
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    for href in ('href="housing.html"', 'href="hotels.html"', "https://alsaabb.github.io/KARIM-SAAB-WEB-LAB/dist/index.html"):
        if href not in index:
            raise SystemExit(f"Missing group destination: {href}")
    print("AL SAAB GROUP draft: 3 bilingual pages and asset references checked. This does not approve text, logos or deployment.")

if __name__ == "__main__":
    main()
