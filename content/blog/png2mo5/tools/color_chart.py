#!/usr/bin/env python3
"""
color_chart.py — Render a list of RGB tuples as a labeled color chart PNG.

Input: JSON array of [R, G, B] tuples, either from a file argument or stdin.
Output: PNG with one row per color showing decimal values, hex code, and a swatch.

Usage:
    python tools/color_chart.py colors.json output.png
    echo '[[255,0,0],[0,255,0]]' | python tools/color_chart.py - output.png
    python tools/color_chart.py                         # uses built-in example

If the second argument is omitted, writes color_chart.png in the current directory.
"""

import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Layout constants
ROW_H      = 20
SWATCH_W   = 40
TEXT_PAD   = 6
IMG_W      = 210
FONT_SIZE  = 10

DEFAULT_INPUT = [
    (103, 1, 0), (101, 2, 0), (99, 2, 0), (100, 2, 0),
    (102, 2, 0), (104, 0, 0), (114, 4, 3), (118, 2, 2),
]


def load_colors(arg):
    import ast
    if arg == "-":
        data = sys.stdin.read()
    else:
        data = Path(arg).read_text()
    try:
        return [tuple(c) for c in json.loads(data)]
    except json.JSONDecodeError:
        return [tuple(c) for c in ast.literal_eval(data)]


def make_chart(colors, dst_path):
    h = ROW_H * len(colors)
    img = Image.new("RGB", (IMG_W, h), (240, 240, 240))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", FONT_SIZE)
    except Exception:
        font = ImageFont.load_default()

    for i, rgb in enumerate(colors):
        r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
        y = i * ROW_H

        # Color swatch on the left
        draw.rectangle([0, y, SWATCH_W, y + ROW_H - 1], fill=(r, g, b))

        # Text: decimal + hex
        label = f"({r:3d}, {g:3d}, {b:3d})   #{r:02X}{g:02X}{b:02X}"
        draw.text((SWATCH_W + TEXT_PAD, y + (ROW_H - FONT_SIZE) // 2),
                  label, fill=(20, 20, 20), font=font)

    img.save(dst_path)
    print(f"Saved {dst_path}  ({len(colors)} colors)")


def main():
    args = sys.argv[1:]

    if not args:
        colors = DEFAULT_INPUT
        dst = Path("color_chart.png")
    elif len(args) == 1:
        colors = load_colors(args[0])
        dst = Path("color_chart.png")
    else:
        colors = load_colors(args[0])
        dst = Path(args[1])

    make_chart(colors, dst)


if __name__ == "__main__":
    main()
