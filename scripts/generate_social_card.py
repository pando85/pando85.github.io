#!/usr/bin/env python3
"""Render the static 1200×630 Kaniop social card with the project's real crab logo.

This script is deterministic and intended to be run when the source branding changes.
Do not fetch remote assets at build/deploy time.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
LOGO = ROOT / "images" / "logo.png"
OUTPUT = ROOT / "images" / "kaniop-social.png"
WIDTH, HEIGHT = 1200, 630


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = (
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"]
        if bold else
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"]
    )
    return ImageFont.truetype(next(path for path in names if Path(path).exists()), size)


def main() -> None:
    card = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = card.load()
    # Navy-to-cyan gradient, subtle and readable in social embeds.
    for y in range(HEIGHT):
        for x in range(WIDTH):
            t = 0.62 * x / WIDTH + 0.38 * y / HEIGHT
            pixels[x, y] = (
                round(10 + 7*t), round(29 + 47*t), round(55 + 70*t)
            )

    draw = ImageDraw.Draw(card, "RGBA")
    draw.ellipse((745, -210, 1460, 500), outline=(112, 231, 240, 53), width=4)
    draw.ellipse((808, -145, 1360, 410), outline=(112, 231, 240, 38), width=3)
    draw.ellipse((840, 140, 1350, 650), fill=(236, 251, 255, 29))
    draw.rounded_rectangle((67, 58, 274, 102), radius=22, fill=(17, 170, 159, 55),
                           outline=(100, 225, 211, 160), width=2)
    draw.text((91, 66), "OPEN SOURCE", font=font(18, True), fill=(151, 252, 232, 255))

    draw.text((65, 143), "Kaniop", font=font(78, True), fill="white")
    draw.text((66, 271), "Identity management", font=font(40, True), fill=(240, 253, 255, 255))
    draw.text((66, 325), "the Kubernetes way.", font=font(40, True), fill=(139, 227, 247, 255))
    draw.text((68, 418), "Deploy Kanidm. Reconcile identities.", font=font(22), fill=(215, 236, 245, 255))
    draw.text((68, 452), "Manage everything with GitOps.", font=font(22), fill=(215, 236, 245, 255))

    draw.line((68, 539, 700, 539), fill=(190, 229, 239, 80), width=2)
    draw.text((69, 557), "github.com/pando85/kaniop", font=font(19),
              fill=(145, 225, 229, 255))

    logo = Image.open(LOGO).convert("RGBA")
    alpha = logo.getchannel("A")
    bbox = alpha.point(lambda a: 255 if a > 12 else 0).getbbox()
    if not bbox:
        raise RuntimeError("Crab logo is transparent or empty")
    crab = logo.crop(bbox)
    crab.thumbnail((395, 355), Image.Resampling.LANCZOS)
    # Branded pale disc retains contrast for the orange/yellow mascot.
    cx, cy = 993, 315
    draw.ellipse((cx-213, cy-213, cx+213, cy+213), fill=(250, 254, 255, 244))
    draw.ellipse((cx-213, cy-213, cx+213, cy+213), outline=(153, 244, 242, 225), width=4)
    card.paste(crab, (cx - crab.width // 2, cy - crab.height // 2), crab)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    card.save(OUTPUT, format="PNG", optimize=True)
    with Image.open(OUTPUT) as verified:
        assert verified.size == (WIDTH, HEIGHT)
    print(f"Rendered {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
