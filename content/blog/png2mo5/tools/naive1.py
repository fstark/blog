#!/usr/bin/env python3
"""
naive_mo5.py — Naive MO5 image converter (simplest approach)

For each 8-pixel horizontal block:
  1. Map every pixel to its nearest MO5 palette color.
  2. Find the two palette colors that appear most often in the block.
  3. Re-map each pixel to whichever of those two is closest.

Input is any PNG (or common image format); output is a 320×200 PNG using
only MO5 colors, with at most 2 distinct colors per 8-pixel row slice.

Usage:
    python tools/naive_mo5.py input.png [output.png]

If output is omitted, writes <input_basename>_mo5.png next to the input.
"""

import sys
from pathlib import Path
from PIL import Image
from mo5_common import MO5_PALETTE, MO5_W, MO5_H, color_distance_sq, fit_320x200, pick_top2


def convert(src_path: Path, dst_path: Path) -> None:
    img = Image.open(src_path).convert("RGB")
    img = fit_320x200(img)
    pixels = img.load()

    out = Image.new("RGB", (MO5_W, MO5_H))
    out_px = out.load()

    for y in range(MO5_H):
        for bx in range(0, MO5_W, 8):
            # --- Steps 1+2: pick the two best palette colors for this block --
            c0, c1 = pick_top2([pixels[x, y] for x in range(bx, bx + 8)])

            if bx==27*8 and y==118:
                print(f"DEBUG: block at y={y}, bx={bx} has colors {c0} and {c1}")
                print(f"{[pixels[x, y] for x in range(bx, bx + 8)]}")
                print(f"{MO5_PALETTE}")

            # --- Step 3: re-map each pixel to the closer of the two ----------
            for i, x in enumerate(range(bx, bx + 8)):
                r, g, b = pixels[x, y]
                d0 = color_distance_sq(r, g, b, c0)
                d1 = color_distance_sq(r, g, b, c1)
                chosen = c0 if d0 <= d1 else c1
                out_px[x, y] = MO5_PALETTE[chosen]


    out.save(dst_path)
    print(f"Saved {dst_path}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    src = Path(sys.argv[1])
    if not src.exists():
        print(f"Error: {src} not found", file=sys.stderr)
        sys.exit(1)

    dst = Path(sys.argv[2]) if len(sys.argv) >= 3 else src.with_name(src.stem + "_mo5.png")
    convert(src, dst)


if __name__ == "__main__":
    main()
