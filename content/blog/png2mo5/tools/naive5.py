#!/usr/bin/env python3
"""
naive5_mo5.py — MO5 converter: brute-force best pair + damped FS in CIELAB

Same algorithm as naive4_mo5.py, but all color comparisons and error diffusion
are done in CIELAB color space instead of RGB. CIELAB distances correspond to
perceived color differences, so we optimize for what the human eye actually sees.

Conversion pipeline (per the blog post):
    sRGB → Linear RGB (undo gamma) → CIE XYZ → CIELAB

Error diffusion accumulates in Lab space; effective pixel values are the
original Lab + accumulated Lab error. Distances at every step use squared
Euclidean distance in Lab space.

Usage:
    python tools/naive5_mo5.py input.png [output.png]

If output is omitted, writes <input_basename>_mo5.png next to the input.
"""

import sys
import math
from pathlib import Path
from PIL import Image
from mo5_common import DAMP

# ---------------------------------------------------------------------------
# MO5 palette  (index → (R, G, B))
# ---------------------------------------------------------------------------
MO5_PALETTE_RGB = [
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

ALL_PAIRS = [(i, j) for i in range(16) for j in range(i, 16)]

MO5_W, MO5_H = 320, 200
# D65 reference white
XN, YN, ZN = 0.95047, 1.00000, 1.08883


# ---------------------------------------------------------------------------
# Color space conversions
# ---------------------------------------------------------------------------

def srgb_to_linear(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_xyz(r, g, b):
    x = 0.4124564 * r + 0.3575761 * g + 0.1804375 * b
    y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    z = 0.0193339 * r + 0.1191920 * g + 0.9503041 * b
    return x, y, z


def xyz_f(t):
    d = 6.0 / 29.0
    return t ** (1.0/3.0) if t > d**3 else t / (3 * d*d) + 4.0/29.0


def xyz_to_lab(x, y, z):
    fy = xyz_f(y / YN)
    L = 116.0 * fy - 16.0
    a = 500.0 * (xyz_f(x / XN) - fy)
    b = 200.0 * (fy - xyz_f(z / ZN))
    return L, a, b


def rgb_to_lab(r, g, b):
    rl = srgb_to_linear(r)
    gl = srgb_to_linear(g)
    bl = srgb_to_linear(b)
    return xyz_to_lab(*linear_to_xyz(rl, gl, bl))


# Pre-compute MO5 palette in Lab
MO5_PALETTE_LAB = [rgb_to_lab(*rgb) for rgb in MO5_PALETTE_RGB]


def lab_dist_sq(L1, a1, b1, L2, a2, b2):
    return (L1-L2)**2 + (a1-a2)**2 + (b1-b2)**2


def nearest_of_two_lab(L, a, b, c0, c1):
    L0, a0, b0 = MO5_PALETTE_LAB[c0]
    L1, a1, b1 = MO5_PALETTE_LAB[c1]
    d0 = lab_dist_sq(L, a, b, L0, a0, b0)
    d1 = lab_dist_sq(L, a, b, L1, a1, b1)
    return c0 if d0 <= d1 else c1


def fit_320x200(img: Image.Image) -> Image.Image:
    src_w, src_h = img.size
    scale = max(MO5_W / src_w, MO5_H / src_h)
    new_w = round(src_w * scale)
    new_h = round(src_h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - MO5_W) // 2
    top  = (new_h - MO5_H) // 2
    return img.crop((left, top, left + MO5_W, top + MO5_H))


def score_pair_lab(block, c0, c1):
    """Simulate FS in Lab space; return total outgoing squared Lab error."""
    scratch = list(block)  # (L, a, b) floats
    outgoing = 0.0
    for i in range(8):
        L, a, b = scratch[i]
        chosen = nearest_of_two_lab(L, a, b, c0, c1)
        pL, pa, pb = MO5_PALETTE_LAB[chosen]
        eL, ea, eb = L - pL, a - pa, b - pb
        err_sq = eL*eL + ea*ea + eb*eb
        if i < 7:
            nL, na, nb = scratch[i + 1]
            scratch[i + 1] = (nL + eL * 7/16, na + ea * 7/16, nb + eb * 7/16)
            outgoing += err_sq * 9/16
        else:
            outgoing += err_sq
    return outgoing


def convert(src_path: Path, dst_path: Path) -> None:
    img = Image.open(src_path).convert("RGB")
    img = fit_320x200(img)
    pixels = img.load()

    # Pre-convert all pixels to Lab
    lab_pixels = [
        [rgb_to_lab(*pixels[x, y]) for x in range(MO5_W)]
        for y in range(MO5_H)
    ]

    out = Image.new("RGB", (MO5_W, MO5_H))
    out_px = out.load()

    # Lab error buffer
    err = [[(0.0, 0.0, 0.0)] * MO5_W for _ in range(MO5_H)]

    for y in range(MO5_H):
        for bx in range(0, MO5_W, 8):

            # Effective Lab values: original Lab + accumulated Lab error
            block = []
            for x in range(bx, bx + 8):
                L0, a0, b0 = lab_pixels[y][x]
                eL, ea, eb = err[y][x]
                block.append((L0 + eL, a0 + ea, b0 + eb))

            # Find best pair (minimum outgoing Lab error)
            best_pair = ALL_PAIRS[0]
            best_score = float('inf')
            for pair in ALL_PAIRS:
                s = score_pair_lab(block, pair[0], pair[1])
                if s < best_score:
                    best_score = s
                    best_pair = pair

            c0, c1 = best_pair

            # Commit: re-run with winner, write pixels, propagate error
            scratch = list(block)
            for i in range(8):
                x = bx + i
                L, a, b = scratch[i]
                chosen = nearest_of_two_lab(L, a, b, c0, c1)
                out_px[x, y] = MO5_PALETTE_RGB[chosen]

                pL, pa, pb = MO5_PALETTE_LAB[chosen]
                eL, ea, eb = L - pL, a - pa, b - pb

                if i < 7:
                    nL, na, nb = scratch[i + 1]
                    scratch[i + 1] = (nL + eL * 7/16, na + ea * 7/16, nb + eb * 7/16)
                else:
                    if x + 1 < MO5_W:
                        e = err[y][x + 1]
                        err[y][x + 1] = (e[0] + eL * 7/16 * DAMP,
                                         e[1] + ea * 7/16 * DAMP,
                                         e[2] + eb * 7/16 * DAMP)

                if y + 1 < MO5_H:
                    if x - 1 >= 0:
                        e = err[y + 1][x - 1]
                        err[y + 1][x - 1] = (e[0] + eL * 3/16 * DAMP,
                                              e[1] + ea * 3/16 * DAMP,
                                              e[2] + eb * 3/16 * DAMP)
                    e = err[y + 1][x]
                    err[y + 1][x] = (e[0] + eL * 5/16 * DAMP,
                                     e[1] + ea * 5/16 * DAMP,
                                     e[2] + eb * 5/16 * DAMP)
                    if x + 1 < MO5_W:
                        e = err[y + 1][x + 1]
                        err[y + 1][x + 1] = (e[0] + eL * 1/16 * DAMP,
                                              e[1] + ea * 1/16 * DAMP,
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
