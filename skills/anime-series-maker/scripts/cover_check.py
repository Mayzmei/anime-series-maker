#!/usr/bin/env python3
"""Preview how a 9:16 cover looks on the Instagram profile grid (3:4 center crop).

    python3 cover_check.py cover.png [-o cover_check.png]

Left: full cover with the crop lines (red) and the 15% no-text bands (shaded).
Right: what the grid actually shows. Look for titles/faces under the shaded bands and for
white / faded strips near the top edge. Needs Pillow (python3 -m pip install pillow).
"""
import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("ERROR: needs Pillow — python3 -m pip install pillow")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cover")
    ap.add_argument("-o", "--out")
    args = ap.parse_args()

    im = Image.open(args.cover).convert("RGB")
    w, h = im.size
    crop_h = round(w * 4 / 3)
    if crop_h >= h:
        print(f"note: {w}x{h} is already 3:4 or wider — nothing gets cropped")
        crop_h = h
    top = (h - crop_h) // 2
    band = round(h * 0.15)

    marked = im.copy()
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rectangle([0, 0, w, band], fill=(255, 0, 0, 60))
    d.rectangle([0, h - band, w, h], fill=(255, 0, 0, 60))
    marked = Image.alpha_composite(marked.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(marked)
    lw = max(3, w // 200)
    d.line([0, top, w, top], fill=(255, 0, 0), width=lw)
    d.line([0, top + crop_h, w, top + crop_h], fill=(255, 0, 0), width=lw)

    cropped = im.crop((0, top, w, top + crop_h))
    gap = w // 20
    sheet = Image.new("RGB", (w * 2 + gap, h), "white")
    sheet.paste(marked, (0, 0))
    sheet.paste(cropped, (w + gap, (h - crop_h) // 2))
    out = Path(args.out) if args.out else Path(args.cover).with_name(Path(args.cover).stem + "_check.png")
    sheet.save(out)
    print(f"OK {out}  (grid crop removes {top}px top and bottom = {top / h:.1%} each)")


if __name__ == "__main__":
    main()
