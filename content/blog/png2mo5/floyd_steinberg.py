"""
Floyd-Steinberg Dithering Animation for the MO5
================================================
Visualizes Floyd-Steinberg error diffusion with the MO5's 2-color-per-8-pixel constraint.

Run:  manim -pqh floyd_steinberg.py FloydSteinbergDithering
"""

from pathlib import Path
import numpy as np
from PIL import Image
from manim import *

# ---------------------------------------------------------------------------
# MO5 PALETTE
# ---------------------------------------------------------------------------
MO5_PALETTE = [
    (0, 0, 0),        #  0  Black
    (255, 0, 0),      #  1  Red
    (0, 255, 0),      #  2  Green
    (255, 255, 0),    #  3  Yellow
    (0, 0, 255),      #  4  Blue
    (255, 0, 255),    #  5  Magenta
    (0, 255, 255),    #  6  Cyan
    (255, 255, 255),  #  7  White
    (128, 128, 128),  #  8  Gray
    (255, 128, 128),  #  9  Pink
    (128, 255, 128),  # 10  Light Green
    (255, 255, 128),  # 11  Light Yellow
    (128, 128, 255),  # 12  Light Blue
    (255, 128, 255),  # 13  Purple
    (128, 255, 255),  # 14  Light Cyan
    (255, 128, 0),    # 15  Orange
]

MO5_PALETTE_NP = np.array(MO5_PALETTE, dtype=np.float64)

# Floyd-Steinberg diffusion weights and offsets (dx, dy, weight)
FS_WEIGHTS = [
    (1, 0, 7 / 16),   # right
    (-1, 1, 3 / 16),  # below-left
    (0, 1, 5 / 16),   # below
    (1, 1, 1 / 16),   # below-right
]

# ---------------------------------------------------------------------------
# IMAGE SETUP
# ---------------------------------------------------------------------------
IMG_PATH = Path(__file__).parent / "img" / "birds-320.png"
CROP_X, CROP_Y = 200, 78
GRID_W, GRID_H = 16, 16

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def rgb_to_manim(r, g, b):
    """Convert 0-255 RGB to Manim color."""
    return rgb_to_color((r / 255, g / 255, b / 255))


def closest_palette_color(pixel_rgb):
    """Find the palette index closest to pixel_rgb (Euclidean RGB)."""
    diffs = MO5_PALETTE_NP - np.array(pixel_rgb)
    dists = np.sum(diffs ** 2, axis=1)
    return int(np.argmin(dists))


def pick_block_pair(pixels_rgb):
    """
    Delayed color selection: given 8 (error-modified) pixel colors,
    pick the 2 palette colors that minimize total squared error.
    Tries all 136 pairs.
    """
    best_pair = (0, 7)
    best_cost = float("inf")
    for i in range(16):
        for j in range(i, 16):
            ci = MO5_PALETTE_NP[i]
            cj = MO5_PALETTE_NP[j]
            cost = 0
            for px in pixels_rgb:
                p = np.array(px)
                di = np.sum((p - ci) ** 2)
                dj = np.sum((p - cj) ** 2)
                cost += min(di, dj)
            if cost < best_cost:
                best_cost = cost
                best_pair = (i, j)
    return best_pair


def load_pixel_grid():
    """Load the 16x16 pixel region from birds-320.png."""
    img = Image.open(IMG_PATH).convert("RGB")
    pixels = []
    for y in range(GRID_H):
        row = []
        for x in range(GRID_W):
            r, g, b = img.getpixel((CROP_X + x, CROP_Y + y))
            row.append([float(r), float(g), float(b)])
        pixels.append(row)
    return pixels


# ---------------------------------------------------------------------------
# SCENE
# ---------------------------------------------------------------------------

class FloydSteinbergDithering(Scene):
    def construct(self):
        # --- Load data ---
        original_pixels = load_pixel_grid()
        # Working copy (will accumulate error)
        pixels = [[list(c) for c in row] for row in original_pixels]

        # --- Layout constants ---
        PIXEL_SIZE = 0.38          # full size of a processed pixel
        SMALL_RATIO = 0.8          # unprocessed pixels are smaller
        SMALL_SIZE = PIXEL_SIZE * SMALL_RATIO
        GRID_LEFT = -4.5           # left edge of pixel grid
        GRID_TOP = 3.0             # top edge of pixel grid
        PALETTE_X = 4.5            # palette center X
        PALETTE_TOP = 3.0

        # --- Phase 1: Show full image and zoom ---
        self.phase_zoom(GRID_LEFT, GRID_TOP, PIXEL_SIZE, SMALL_SIZE, original_pixels)

        # --- Phase 2: Build grid + palette ---
        pixel_squares = {}
        error_fragments = {}  # (x, y) -> list of fragment mobjects sitting on that pixel

        for y in range(GRID_H):
            for x in range(GRID_W):
                r, g, b = original_pixels[y][x]
                sq = Square(side_length=SMALL_SIZE, stroke_width=0)
                sq.set_fill(rgb_to_manim(r, g, b), opacity=1)
                sq.move_to(self.grid_pos(x, y, GRID_LEFT, GRID_TOP, PIXEL_SIZE))
                pixel_squares[(x, y)] = sq
                error_fragments[(x, y)] = []

        grid_group = VGroup(*pixel_squares.values())

        # Block gridlines (subtle)
        gridlines = VGroup()
        for bx in range(1, GRID_W // 8 + 1):
            x_pos = GRID_LEFT + bx * 8 * PIXEL_SIZE
            if bx < GRID_W // 8:
                line = Line(
                    start=[x_pos, GRID_TOP, 0],
                    end=[x_pos, GRID_TOP - GRID_H * PIXEL_SIZE, 0],
                    stroke_width=1, stroke_opacity=0.3, color=GRAY
                )
                gridlines.add(line)
        for by in range(1, GRID_H):
            y_pos = GRID_TOP - by * PIXEL_SIZE
            line = Line(
                start=[GRID_LEFT, y_pos, 0],
                end=[GRID_LEFT + GRID_W * PIXEL_SIZE, y_pos, 0],
                stroke_width=0.5, stroke_opacity=0.15, color=GRAY
            )
            gridlines.add(line)

        # Palette swatches (single column)
        palette_group = VGroup()
        palette_swatches = []
        swatch_size = 0.35
        for i, (r, g, b) in enumerate(MO5_PALETTE):
            sw = Square(side_length=swatch_size, stroke_width=1, stroke_color=GRAY)
            sw.set_fill(rgb_to_manim(r, g, b), opacity=1)
            sw.move_to([
                PALETTE_X,
                PALETTE_TOP - i * (swatch_size + 0.05),
                0
            ])
            palette_swatches.append(sw)
            palette_group.add(sw)

        # Active pair indicator (will be positioned next to the active block)
        pair_swatch_size = swatch_size * 1.3
        pair_sq0 = Square(side_length=pair_swatch_size, stroke_width=2, stroke_color=WHITE)
        pair_sq1 = Square(side_length=pair_swatch_size, stroke_width=2, stroke_color=WHITE)
        pair_sq0.set_fill(BLACK, opacity=1)
        pair_sq1.set_fill(BLACK, opacity=1)
        pair_group = VGroup(pair_sq0, pair_sq1)
        pair_group.arrange(DOWN, buff=0.05)
        # Start off-screen, will be positioned per block
        pair_group.move_to([GRID_LEFT - 1, GRID_TOP, 0])

        self.add(grid_group, gridlines, palette_group, pair_group)

        # --- Phase 3: Process blocks ---
        block_order = [(0, 0), (1, 0), (0, 1), (1, 1)]
        block_border = Square(
            side_length=8 * PIXEL_SIZE,
            stroke_width=3, stroke_color=YELLOW
        ).set_fill(opacity=0)

        first_pixel_global = True

        for block_idx, (bx, by) in enumerate(block_order):
            # Position block border
            block_center = self.grid_pos(
                bx * 8 + 3.5, by + 0, GRID_LEFT, GRID_TOP, PIXEL_SIZE
            )
            # Block border is 8 wide × 1 tall
            block_rect = Rectangle(
                width=8 * PIXEL_SIZE, height=PIXEL_SIZE,
                stroke_width=3, stroke_color=YELLOW
            ).set_fill(opacity=0)
            block_rect.move_to(block_center)

            if block_idx == 0:
                self.play(Create(block_rect), run_time=0.5)
            else:
                self.play(block_rect.animate.move_to(block_center), run_time=0.4)
                # Re-create since we can't easily move across blocks
                new_rect = Rectangle(
                    width=8 * PIXEL_SIZE, height=PIXEL_SIZE,
                    stroke_width=3, stroke_color=YELLOW
                ).set_fill(opacity=0).move_to(block_center)
                self.play(
                    ReplacementTransform(block_rect, new_rect), run_time=0.3
                )
                block_rect = new_rect

            # Get current pixel colors (with accumulated error)
            block_pixels = []
            for px in range(8):
                x = bx * 8 + px
                y = by
                block_pixels.append(pixels[y][x])

            # Pick the 2 palette colors
            c0_idx, c1_idx = pick_block_pair(block_pixels)
            c0_rgb = MO5_PALETTE[c0_idx]
            c1_rgb = MO5_PALETTE[c1_idx]

            # Position pair indicator next to the block
            block_center_y = GRID_TOP - (by + 0.5) * PIXEL_SIZE
            if bx == 0:
                pair_x = GRID_LEFT - pair_swatch_size - 0.15
            else:
                pair_x = GRID_LEFT + GRID_W * PIXEL_SIZE + pair_swatch_size + 0.15
            pair_target = np.array([pair_x, block_center_y, 0])

            # Animate palette selection + move pair indicator
            self.play(
                pair_group.animate.move_to(pair_target),
                pair_sq0.animate.set_fill(rgb_to_manim(*c0_rgb), opacity=1),
                pair_sq1.animate.set_fill(rgb_to_manim(*c1_rgb), opacity=1),
                Flash(palette_swatches[c0_idx], color=WHITE, flash_radius=0.2),
                Flash(palette_swatches[c1_idx], color=WHITE, flash_radius=0.2),
                run_time=0.6
            )

            # Process each pixel in the block
            for px in range(8):
                x = bx * 8 + px
                y = by

                # Determine speed based on block and pixel index
                if block_idx == 0 and px < 3:
                    speed = "slow"
                elif block_idx == 0:
                    speed = "medium"
                elif block_idx == 1:
                    speed = "medium"
                else:
                    speed = "fast"

                self.process_pixel(
                    x, y, pixels, pixel_squares, error_fragments,
                    c0_idx, c1_idx, PIXEL_SIZE, SMALL_SIZE,
                    GRID_LEFT, GRID_TOP, speed, first_pixel_global
                )
                first_pixel_global = False

            # Remove block border after each block
            self.play(FadeOut(block_rect), run_time=0.3)

        # --- Phase 4: Fast remaining rows (rows 2-15) ---
        self.process_remaining_rows(
            pixels, pixel_squares, error_fragments,
            PIXEL_SIZE, SMALL_SIZE, GRID_LEFT, GRID_TOP,
            pair_sq0, pair_sq1, pair_group, pair_swatch_size, palette_swatches
        )

        # --- Ending hold ---
        self.wait(2)

    def grid_pos(self, x, y, grid_left, grid_top, pixel_size):
        """Get center position for pixel (x, y)."""
        return np.array([
            grid_left + (x + 0.5) * pixel_size,
            grid_top - (y + 0.5) * pixel_size,
            0
        ])

    def process_remaining_rows(
        self, pixels, pixel_squares, error_fragments,
        pixel_size, small_size, grid_left, grid_top,
        pair_sq0, pair_sq1, pair_group, pair_swatch_size, palette_swatches
    ):
        """Process rows 2-15 quickly: show pixels appearing with error accumulation, no flying."""
        for y in range(2, GRID_H):
            for bx in range(GRID_W // 8):
                # Get current pixel colors (with accumulated error)
                block_pixels = []
                for px in range(8):
                    x = bx * 8 + px
                    block_pixels.append(pixels[y][x])

                # Pick the 2 palette colors
                c0_idx, c1_idx = pick_block_pair(block_pixels)
                c0_rgb = np.array(MO5_PALETTE[c0_idx], dtype=np.float64)
                c1_rgb = np.array(MO5_PALETTE[c1_idx], dtype=np.float64)

                # Move pair indicator next to block (instant, no animation)
                block_center_y = grid_top - (y + 0.5) * pixel_size
                if bx == 0:
                    pair_x = grid_left - pair_swatch_size - 0.15
                else:
                    pair_x = grid_left + GRID_W * pixel_size + pair_swatch_size + 0.15
                pair_group.move_to([pair_x, block_center_y, 0])
                pair_sq0.set_fill(rgb_to_manim(*MO5_PALETTE[c0_idx]), opacity=1)
                pair_sq1.set_fill(rgb_to_manim(*MO5_PALETTE[c1_idx]), opacity=1)

                # Process all 8 pixels in this block simultaneously
                anims = []
                for px in range(8):
                    x = bx * 8 + px
                    cur = np.array(pixels[y][x])

                    # Remove any accumulated error fragments visually
                    for frag in error_fragments[(x, y)]:
                        self.remove(frag)
                    error_fragments[(x, y)] = []

                    # Choose closest palette color
                    d0 = np.sum((cur - c0_rgb) ** 2)
                    d1 = np.sum((cur - c1_rgb) ** 2)
                    chosen_rgb = c0_rgb if d0 <= d1 else c1_rgb

                    # Compute and diffuse error
                    error = cur - chosen_rgb
                    for dx, dy, weight in FS_WEIGHTS:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                            pixels[ny][nx][0] += error[0] * weight
                            pixels[ny][nx][1] += error[1] * weight
                            pixels[ny][nx][2] += error[2] * weight

                    # Update pixel data
                    pixels[y][x] = list(chosen_rgb)

                    # Animate pixel snap
                    sq = pixel_squares[(x, y)]
                    pos = self.grid_pos(x, y, grid_left, grid_top, pixel_size)
                    chosen_color = rgb_to_manim(
                        *[int(max(0, min(255, v))) for v in chosen_rgb]
                    )
                    anims.append(
                        sq.animate.set_width(pixel_size)
                        .set_fill(chosen_color, opacity=1)
                        .move_to(pos)
                    )

                    # Show small error fragments on neighbors (no flight, just appear)
                    if np.sum(error ** 2) > 1:
                        err_display = [max(0, min(255, 128 + v / 2)) for v in error]
                        tiny_size = small_size / 4
                        for dx, dy, weight in FS_WEIGHTS:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                                target_pos = self.grid_pos(
                                    nx, ny, grid_left, grid_top, pixel_size
                                )
                                offset = np.array([
                                    np.random.uniform(-0.03, 0.03),
                                    np.random.uniform(-0.03, 0.03), 0
                                ])
                                tiny = Square(
                                    side_length=tiny_size * 0.9, stroke_width=0
                                )
                                tiny.set_fill(
                                    rgb_to_manim(*[int(v) for v in err_display]),
                                    opacity=0.7
                                )
                                tiny.move_to(target_pos + offset)
                                self.add(tiny)
                                error_fragments[(nx, ny)].append(tiny)

                # Animate the whole block at once
                if anims:
                    self.play(*anims, run_time=0.15)

    def phase_zoom(self, grid_left, grid_top, pixel_size, small_size, original_pixels):
        """Show full image, highlight region, zoom into the grid."""
        img_path = str(IMG_PATH)
        full_img = ImageMobject(img_path)
        # Scale to reasonable screen size (birds-320 is 320x200)
        full_img.set_height(5)
        full_img.move_to(ORIGIN)

        self.play(FadeIn(full_img), run_time=0.8)
        self.wait(0.5)

        # Highlight rectangle over the 16x16 region
        # Image is 320x200, displayed at height=5 → scale = 5/200 = 0.025 per pixel
        scale = full_img.get_height() / 200
        img_left = full_img.get_left()[0]
        img_top = full_img.get_top()[1]
        rect_x = img_left + (CROP_X + GRID_W / 2) * scale
        rect_y = img_top - (CROP_Y + GRID_H / 2) * scale
        rect_w = GRID_W * scale
        rect_h = GRID_H * scale

        highlight = Rectangle(
            width=rect_w, height=rect_h,
            stroke_width=2, stroke_color=YELLOW
        ).set_fill(opacity=0)
        highlight.move_to([rect_x, rect_y, 0])

        self.play(Create(highlight), run_time=0.5)
        self.wait(0.5)

        # Target: where the grid will live
        target_w = GRID_W * pixel_size
        target_h = GRID_H * pixel_size
        target_center = np.array([
            grid_left + target_w / 2,
            grid_top - target_h / 2,
            0
        ])

        # Compute zoom factor: how much larger the target is than the highlight
        zoom_factor = target_w / rect_w

        # Group image + highlight so they zoom together
        # We scale around the highlight center, then shift to target center
        zoom_group = Group(full_img, highlight)
        highlight_center = highlight.get_center()

        # Animate: scale the group so the highlighted region fills the grid area
        self.play(
            zoom_group.animate
                .scale(zoom_factor, about_point=highlight_center)
                .move_to(target_center + (highlight_center - zoom_group.get_center()) * 0),
            run_time=1.5,
            rate_func=smooth
        )
        # After scaling, reposition so the highlight is exactly at target_center
        # (the scale moved things around the highlight center, so now shift the group)
        offset = target_center - highlight.get_center()
        if np.linalg.norm(offset) > 0.01:
            zoom_group.shift(offset)

        self.wait(0.3)

        # Fade out the zoomed image, leaving space for the pixel grid
        self.play(
            FadeOut(full_img),
            FadeOut(highlight),
            run_time=0.6
        )

    def process_pixel(
        self, x, y, pixels, pixel_squares, error_fragments,
        c0_idx, c1_idx, pixel_size, small_size,
        grid_left, grid_top, speed, show_labels
    ):
        """Process a single pixel: choose color, show error, diffuse."""
        run_times = {"slow": 1.5, "medium": 0.5, "fast": 0.25}
        rt = run_times[speed]

        sq = pixel_squares[(x, y)]
        pos = self.grid_pos(x, y, grid_left, grid_top, pixel_size)

        # Current pixel value (with accumulated error)
        cur_r, cur_g, cur_b = pixels[y][x]
        # Clamp for display
        cur_r_c = max(0, min(255, cur_r))
        cur_g_c = max(0, min(255, cur_g))
        cur_b_c = max(0, min(255, cur_b))

        # Merge accumulated fragments into the pixel visually
        frags = error_fragments[(x, y)]
        if frags:
            self.play(
                *[FadeOut(f, run_time=rt * 0.4) for f in frags],
                sq.animate.set_fill(rgb_to_manim(cur_r_c, cur_g_c, cur_b_c), opacity=1),
                run_time=rt * 0.5
            )
            error_fragments[(x, y)] = []

        # Choose closest of the two palette colors
        c0_rgb = np.array(MO5_PALETTE[c0_idx], dtype=np.float64)
        c1_rgb = np.array(MO5_PALETTE[c1_idx], dtype=np.float64)
        cur = np.array([cur_r, cur_g, cur_b])
        d0 = np.sum((cur - c0_rgb) ** 2)
        d1 = np.sum((cur - c1_rgb) ** 2)
        if d0 <= d1:
            chosen_rgb = c0_rgb
        else:
            chosen_rgb = c1_rgb

        # Compute error
        error = cur - chosen_rgb  # can be negative

        # Animate: pixel grows to full size and snaps to palette color
        chosen_color = rgb_to_manim(*[max(0, min(255, v)) for v in chosen_rgb])
        self.play(
            sq.animate.set_width(pixel_size).set_fill(chosen_color, opacity=1).move_to(pos),
            run_time=rt
        )

        # Update pixel data
        pixels[y][x] = list(chosen_rgb)

        # --- Error visualization ---
        if np.sum(error ** 2) < 1:
            return  # negligible error, skip

        # Show error square
        err_color_clamped = [max(0, min(255, abs(v))) for v in error]
        # Use the actual error color (shifted to visible range)
        err_display = [max(0, min(255, 128 + v / 2)) for v in error]
        error_sq = Square(side_length=small_size, stroke_width=0.5, stroke_color=WHITE)
        error_sq.set_fill(rgb_to_manim(*[int(v) for v in err_display]), opacity=0.9)
        error_sq.move_to(pos + RIGHT * pixel_size * 0.1 + UP * pixel_size * 0.1)

        if speed == "slow":
            self.play(FadeIn(error_sq), run_time=rt * 0.3)
        else:
            self.add(error_sq)
            self.wait(rt * 0.2)

        # Subdivide into 4x4 = 16 tiny squares
        tiny_size = small_size / 4
        tiny_squares = []
        for ty in range(4):
            for tx in range(4):
                tiny = Square(side_length=tiny_size * 0.9, stroke_width=0)
                tiny.set_fill(error_sq.get_fill_color(), opacity=0.9)
                tiny.move_to(
                    error_sq.get_corner(UL)
                    + RIGHT * (tx + 0.5) * tiny_size
                    + DOWN * (ty + 0.5) * tiny_size
                )
                tiny_squares.append(tiny)

        # Replace error square with tiny squares
        tiny_group = VGroup(*tiny_squares)
        if speed == "slow":
            self.play(
                FadeOut(error_sq),
                FadeIn(tiny_group),
                run_time=rt * 0.3
            )
        else:
            self.remove(error_sq)
            self.add(tiny_group)

        # Assign pieces to neighbors: 7 right, 3 below-left, 5 below, 1 below-right
        assignments = []  # (tiny_square, target_x, target_y, weight_fraction)
        piece_idx = 0
        for dx, dy, weight in FS_WEIGHTS:
            nx, ny = x + dx, y + dy
            count = round(weight * 16)  # 7, 3, 5, 1
            for _ in range(count):
                if piece_idx < 16:
                    assignments.append((tiny_squares[piece_idx], nx, ny, weight))
                    piece_idx += 1

        # Show weight labels on first pixel only
        labels = []
        if show_labels:
            label_texts = ["7/16", "3/16", "5/16", "1/16"]
            label_offsets = [RIGHT * 1.2, DL * 1.0, DOWN * 1.2, DR * 1.0]
            for i, (dx, dy, w) in enumerate(FS_WEIGHTS):
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                    target_pos = self.grid_pos(nx, ny, grid_left, grid_top, pixel_size)
                    lbl = Text(label_texts[i], font_size=14, color=WHITE)
                    lbl.move_to(target_pos + label_offsets[i] * pixel_size * 0.6)
                    labels.append(lbl)
            if labels:
                self.play(*[FadeIn(l) for l in labels], run_time=0.4)

        # Animate pieces flying to their targets
        animations = []
        for tiny, nx, ny, _ in assignments:
            if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                target_pos = self.grid_pos(nx, ny, grid_left, grid_top, pixel_size)
                # Slight random offset so they don't all stack perfectly
                offset = np.array([
                    np.random.uniform(-0.03, 0.03),
                    np.random.uniform(-0.03, 0.03),
                    0
                ])
                animations.append(tiny.animate.move_to(target_pos + offset))
            else:
                # Off grid — fade out
                animations.append(FadeOut(tiny))

        fly_time = {"slow": 0.8, "medium": 0.4, "fast": 0.2}[speed]
        if animations:
            self.play(*animations, run_time=fly_time)

        # Register landed fragments and update pixel error values
        for tiny, nx, ny, _ in assignments:
            if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                error_fragments[(nx, ny)].append(tiny)
            else:
                if tiny in self.mobjects:
                    self.remove(tiny)

        # Diffuse error into pixel data
        for dx, dy, weight in FS_WEIGHTS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                pixels[ny][nx][0] += error[0] * weight
                pixels[ny][nx][1] += error[1] * weight
                pixels[ny][nx][2] += error[2] * weight

        # Fade out labels
        if labels:
            self.play(*[FadeOut(l) for l in labels], run_time=0.3)
