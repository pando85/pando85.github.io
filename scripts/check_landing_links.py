#!/usr/bin/env python3
"""Smoke-check the rendered landing page's local URLs and navigation anchors."""
from html.parser import HTMLParser
from pathlib import Path
import struct
from urllib.parse import unquote, urlsplit
import sys


class LandingLinks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = set()
        self.images = []
        self.meta = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag in ("a", "link") and "href" in attrs:
            self.links.append((tag, attrs["href"]))
        if tag in ("script", "img") and "src" in attrs:
            self.links.append((tag, attrs["src"]))
        if tag == "img":
            self.images.append(attrs)
        if tag == "meta":
            key = attrs.get("property") or attrs.get("name")
            if key:
                self.meta[key] = attrs.get("content", "")


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site").resolve()
    homepage = root / "index.html"
    if not homepage.is_file():
        raise SystemExit(f"Landing HTML missing: {homepage}")

    parser = LandingLinks()
    parser.feed(homepage.read_text(encoding="utf-8"))
    errors = []
    for tag, href in parser.links:
        if not href.strip():
            errors.append(f"{tag} has an empty URL")
            continue
        url = urlsplit(href)
        if url.scheme in ("https", "http", "mailto", "tel") or url.netloc:
            continue
        if url.scheme or href.startswith("//"):
            errors.append(f"Unsupported URL: {href}")
            continue
        path = unquote(url.path)
        if ".." in Path(path).parts:
            errors.append(f"Unsafe relative path: {href}")
            continue
        target = root / path.lstrip("/") if path.startswith("/") else homepage.parent / path
        if not path:
            target = homepage
        if target.is_dir():
            target /= "index.html"
        if not target.exists():
            errors.append(f"Broken local URL: {href}")
        if url.fragment and target == homepage and url.fragment not in parser.ids:
            errors.append(f"Missing landing anchor: {href}")

    if not any(tag == "a" and href.endswith("#features") for tag, href in parser.links):
        errors.append("Features navigation is missing")
    if not any(tag == "a" and href.endswith("#quickstart") for tag, href in parser.links):
        errors.append("Quickstart navigation is missing")
    if not parser.images or any("alt" not in image for image in parser.images):
        errors.append("Images must have alt attributes")

    social = parser.meta.get("og:image", "")
    if not social.endswith("/images/kaniop-social.png"):
        errors.append(f"Wrong Open Graph image: {social}")
    elif parser.meta.get("twitter:image") != social:
        errors.append("Twitter and Open Graph images differ")

    if parser.meta.get("twitter:card") != "summary_large_image":
        errors.append("Missing wide social card configuration")
    if not parser.meta.get("og:image:alt"):
        errors.append("Missing social image alt text")

    preview = root / "images/kaniop-social.png"
    if not preview.is_file():
        errors.append(f"Missing generated social preview: {preview}")
    else:
        header = preview.read_bytes()[:24]
        if len(header) != 24 or not header.startswith(bytes.fromhex("89504e470d0a1a0a")):
            errors.append("Social image is not a valid PNG")
        else:
            width, height = struct.unpack(">II", header[16:24])
            if (width, height) != (1200, 630):
                errors.append(f"Wrong social image dimensions: {width}x{height}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        raise SystemExit(1)
    print(f"Checked {len(parser.links)} landing links/resources and local anchors: OK")


if __name__ == "__main__":
    main()
