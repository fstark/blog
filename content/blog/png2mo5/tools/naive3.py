#!/usr/bin/env python3
"""
naive3_mo5.py — MO5 converter: 2-color block selection + damped Floyd-Steinberg

Same as naive2_mo5.py, but with 0.9 damping on the error diffusion: only 90%
of each quantization error is passed to neighbours. The remaining 10% is
discarded, so long-range error accumulation decays exponentially down the
image. This prevents "orphan error" from snowballing — a bad block near the
top can no longer push false colors all the way to the bottom.

The color pair is still chosen from the original (not error-adjusted) pixels.

Usage:
    python tools/naive3_mo5.py input.png [output.png]

If output is omitted, writes <input_basename>_mo5.png next to the input.
"""

import sys
from pathlib import Path
from PIL import Image
from mo5_common import MO5_PALETTE, MO5_W, MO5_H, fit_320x200, pick_top2, DAMP


def nearest_of_two(r, g, b, c0, c1):
    pr0, pg0, pb0 = MO5_PALETTE[c0]
    pr1, pg1, pb1 = MO5_PALETTE[c1]
    d0 = (r - pr0) ** 2 + (g - pg0) ** 2 + (b - pb0) ** 2
    d1 = (r - pr1) ** 2 + (g - pg1) ** 2 + (b - pb1) ** 2
    return c0 if d0 <= d1 else c1


def convert(src_path: Path, dst_path: Path) -> None:
    img = Image.open(src_path).convert("RGB")
    img = fit_320x200(img)
    pixels = img.load()

    out = Image.new("RGB", (MO5_W, MO5_H))
    out_px = out.load()

    # Floating-point FS error buffer: err[y][x] = (er, eg, eb)
    err = [[(0.0, 0.0, 0.0)] * MO5_W for _ in range(MO5_H)]

    # Floyd-Steinberg pass — color pair chosen from error-adjusted pixels
    for y in range(MO5_H):
        for x in range(MO5_W):
            bx = (x // 8) * 8

            # At the start of each block, pick the pair from current (error-adjusted) values
            if x == bx:
                block_pixels = []
                for xi in range(bx, bx + 8):
                    r0, g0, b0 = pixels[xi, y]
                    er, eg, eb = err[y][xi]
                    block_pixels.append((
                        max(0.0, min(255.0, r0 + er)),
                        max(0.0, min(255.0, g0 + eg)),
                        max(0.0, min(255.0, b0 + eb)),
                    ))
                c0, c1 = pick_top2([(int(r), int(g), int(b)) for r, g, b in block_pixels])

            r0, g0, b0 = pixels[x, y]
            er, eg, eb = err[y][x]
            r = max(0.0, min(255.0, r0 + er))
            g = max(0.0, min(255.0, g0 + eg))
            b = max(0.0, min(255.0, b0 + eb))

            chosen = nearest_of_two(r, g, b, c0, c1)
            pr, pg, pb = MO5_PALETTE[chosen]
            out_px[x, y] = (pr, pg, pb)

            qer = r - pr
            qeg = g - pg
            qeb = b - pb

            def add_err(tx, ty, w):
                e = err[ty][tx]
                err[ty][tx] = (e[0] + qer * w * DAMP, e[1] + qeg * w * DAMP, e[2] + qeb * w * DAMP)

            if x + 1 < MO5_W:
                add_err(x + 1, y,     7/16)
            if y + 1 < MO5_H:
                if x - 1 >= 0:
                    add_err(x - 1, y + 1, 3/16)
                add_err(x,     y + 1, 5/16)
                if x + 1 < MO5_W:
                    add_err(x + 1, y + 1, 1/16)

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
