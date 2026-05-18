"""
mo5_common.py — Shared MO5 palette, helpers, and color-pair selection.
"""

DAMP = 1.0  # Error diffusion damping factor (fraction of error passed to neighbours)

from collections import Counter
from PIL import Image

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

MO5_W, MO5_H = 320, 200


def nearest_palette_index(r, g, b):
    """Return the index of the closest MO5 palette entry (squared RGB distance)."""
    best_idx, best_dist = 0, float('inf')
    for i, (pr, pg, pb) in enumerate(MO5_PALETTE):
        d = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
        if d < best_dist:
            best_dist, best_idx = d, i
    return best_idx


def color_distance_sq(r, g, b, palette_idx):
    pr, pg, pb = MO5_PALETTE[palette_idx]
    return (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2


def fit_320x200(img: Image.Image) -> Image.Image:
    """Scale + centre-crop img to exactly 320×200, preserving aspect ratio."""
    src_w, src_h = img.size
    scale = max(MO5_W / src_w, MO5_H / src_h)
    new_w = round(src_w * scale)
    new_h = round(src_h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - MO5_W) // 2
    top  = (new_h - MO5_H) // 2
    return img.crop((left, top, left + MO5_W, top + MO5_H))


def pick_top2(block_pixels):
    """Return the best two palette color indices for an 8-pixel block.

    block_pixels: list of 8 (r, g, b) tuples (original or error-adjusted).

    Strategy:
      - Snap every pixel to its nearest palette color.
      - Return the two most frequent palette indices.
      - If all pixels snap to the same color (solid block), find the runner-up:
        the palette color (other than the winner) with the smallest total
        squared RGB distance to the block's actual pixels.
    """
    indices = [nearest_palette_index(r, g, b) for r, g, b in block_pixels]
    top2 = [idx for idx, _ in Counter(indices).most_common(2)]
    if len(top2) == 1:
        winner = top2[0]
        best_idx, best_dist = -1, float('inf')
        for idx in range(len(MO5_PALETTE)):
            if idx == winner:
                continue
            d = sum(color_distance_sq(r, g, b, idx) for r, g, b in block_pixels)
            if d < best_dist:
                best_dist, best_idx = d, idx
        top2.append(best_idx)
    return top2[0], top2[1]
