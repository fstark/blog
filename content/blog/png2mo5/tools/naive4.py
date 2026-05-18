#!/usr/bin/env python3
"""
naive4_mo5.py — MO5 converter: brute-force best pair + damped Floyd-Steinberg

For each 8-pixel horizontal block:
  1. Compute the "effective" pixel values = original RGB + accumulated FS error.
  2. Try all 136 possible color pairs from the MO5 palette.
  3. For each pair, simulate Floyd-Steinberg dithering within the 8 pixels,
     using only those two colors, and measure the total *outgoing* error
     (the error that would spill out of the block to its neighbours).
  4. Pick the pair with the minimum outgoing error.
  5. Commit: re-run the simulation with the winner, write the output pixels,
     and propagate the quantization error to the real error buffer (damped 0.9).

This is essentially the algorithm described in the blog post.

Usage:
    python tools/naive4_mo5.py input.png [output.png]

If output is omitted, writes <input_basename>_mo5.png next to the input.
"""

import sys
from pathlib import Path
from PIL import Image
from mo5_common import DAMP

# ---------------------------------------------------------------------------
# MO5 palette  (index → (R, G, B))
# ---------------------------------------------------------------------------
MO5_PALETTE = [
    (  0,   0,   0),  #  0  Black
    (255,   0,   0),  #  1  Red
    (  0, 255,   0),  #  2  Green
    (255, 255,   0),  #  3  Yellow
    (  0,   0, 255),  #  4  Blue
    (255,   0, 255),  #  5  Magenta
    (  0, 255, 255),  #  6  Cyan
    (255, 255, 255),  #  7  White
    (128, 128, 128),  #  8  Gray
    (255, 128, 128),  #  9  Pink
    (128, 255, 128),  # 10  Light Green
    (255, 255, 128),  # 11  Light Yellow
    (128, 128, 255),  # 12  Light Blue
    (255, 128, 255),  # 13  Purple
    (128, 255, 255),  # 14  Light Cyan
    (255, 128,   0),  # 15  Orange
]

# All 136 pairs: (i, j) with i <= j
ALL_PAIRS = [(i, j) for i in range(16) for j in range(i, 16)]

MO5_W, MO5_H = 320, 200

def nearest_of_two(r, g, b, c0, c1):
    pr0, pg0, pb0 = MO5_PALETTE[c0]
    pr1, pg1, pb1 = MO5_PALETTE[c1]
    d0 = (r - pr0) ** 2 + (g - pg0) ** 2 + (b - pb0) ** 2
    d1 = (r - pr1) ** 2 + (g - pg1) ** 2 + (b - pb1) ** 2
    return c0 if d0 <= d1 else c1


def clamp(v):
    return max(0.0, min(255.0, v))


def fit_320x200(img: Image.Image) -> Image.Image:
    src_w, src_h = img.size
    scale = max(MO5_W / src_w, MO5_H / src_h)
    new_w = round(src_w * scale)
    new_h = round(src_h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - MO5_W) // 2
    top  = (new_h - MO5_H) // 2
    return img.crop((left, top, left + MO5_W, top + MO5_H))


def score_pair(block, c0, c1):
    """Simulate FS within the 8-pixel block; return total outgoing squared error."""
    scratch = list(block)  # list of (r, g, b) floats
    outgoing = 0.0
    for i in range(8):
        r, g, b = scratch[i]
        chosen = nearest_of_two(r, g, b, c0, c1)
        pr, pg, pb = MO5_PALETTE[chosen]
        er, eg, eb = r - pr, g - pg, b - pb
        err_sq = er*er + eg*eg + eb*eb
        if i < 7:
            # Rightward stays inside the block
            nr, ng, nb = scratch[i + 1]
            scratch[i + 1] = (nr + er * 7/16, ng + eg * 7/16, nb + eb * 7/16)
            # The downward 9/16 is outgoing
            outgoing += err_sq * 9/16
        else:
            # Last pixel: everything (rightward + downward) leaves the block
            outgoing += err_sq
    return outgoing


def convert(src_path: Path, dst_path: Path) -> None:
    img = Image.open(src_path).convert("RGB")
    img = fit_320x200(img)
    pixels = img.load()

    out = Image.new("RGB", (MO5_W, MO5_H))
    out_px = out.load()

    # Floating-point FS error buffer
    err = [[(0.0, 0.0, 0.0)] * MO5_W for _ in range(MO5_H)]

    for y in range(MO5_H):
        for bx in range(0, MO5_W, 8):

            # --- Effective pixel values (original + accumulated error) -------
            block = []
            for x in range(bx, bx + 8):
                r0, g0, b0 = pixels[x, y]
                er, eg, eb = err[y][x]
                block.append((clamp(r0 + er), clamp(g0 + eg), clamp(b0 + eb)))

            # --- Find best pair (minimum outgoing error) ----------------------
            best_pair = ALL_PAIRS[0]
            best_score = float('inf')
            for pair in ALL_PAIRS:
                s = score_pair(block, pair[0], pair[1])
                if s < best_score:
                    best_score = s
                    best_pair = pair

            c0, c1 = best_pair

            # --- Commit: re-run FS with winner, write pixels, update err buf --
            scratch = list(block)
            for i in range(8):
                x = bx + i
                r, g, b = scratch[i]
                chosen = nearest_of_two(r, g, b, c0, c1)
                pr, pg, pb = MO5_PALETTE[chosen]
                out_px[x, y] = (pr, pg, pb)

                er, eg, eb = r - pr, g - pg, b - pb

                # Intra-block rightward (updates scratch for next pixel)
                if i < 7:
                    nr, ng, nb = scratch[i + 1]
                    scratch[i + 1] = (nr + er * 7/16, ng + eg * 7/16, nb + eb * 7/16)
                else:
                    # Last pixel: rightward goes to next block via error buffer
                    if x + 1 < MO5_W:
                        e = err[y][x + 1]
                        err[y][x + 1] = (e[0] + er * 7/16 * DAMP,
                                         e[1] + eg * 7/16 * DAMP,
                                         e[2] + eb * 7/16 * DAMP)

                # Downward neighbours (always outgoing, all pixels)
                if y + 1 < MO5_H:
                    if x - 1 >= 0:
                        e = err[y + 1][x - 1]
                        err[y + 1][x - 1] = (e[0] + er * 3/16 * DAMP,
                                              e[1] + eg * 3/16 * DAMP,
                                              e[2] + eb * 3/16 * DAMP)
                    e = err[y + 1][x]
                    err[y + 1][x] = (e[0] + er * 5/16 * DAMP,
                                     e[1] + eg * 5/16 * DAMP,
                                     e[2] + eb * 5/16 * DAMP)
                    if x + 1 < MO5_W:
                        e = err[y + 1][x + 1]
                        err[y + 1][x + 1] = (e[0] + er * 1/16 * DAMP,
                                              e[1] + eg * 1/16 * DAMP,
                                              e[2] + eb * 1/16 * DAMP)

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
