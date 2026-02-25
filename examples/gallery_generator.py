"""gallery_generator.py -- Generate the full ideamaxfx visual gallery.

Produces three categories of output:

**Before/After comparisons** (10 effects, side-by-side PNGs)
    Each image pairs the original test image on the left with the effected
    version on the right, with a thin divider and labels.

**Animation GIFs** (8 chart types)
    bar, line, radar, scatter, counter, pie, heatmap, network -- each saved
    as a short looping GIF.

**Text effect showcase**
    All 5 text effects rendered onto a single dark canvas.

Everything is saved under ``examples/output/gallery/``.

Run::

    python examples/gallery_generator.py

Output directory::

    examples/output/gallery/
        before_after_grain.png
        before_after_glow.png
        ...  (10 total)
        anim_bar.gif
        anim_line.gif
        ...  (8 total)
        text_effects.png
"""

from __future__ import annotations

import os
import sys
import time

import numpy as np
from PIL import Image, ImageDraw

# ---------------------------------------------------------------------------
# Ensure the library is importable when running from the repo root.
# ---------------------------------------------------------------------------
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO, "src"))

from ideamaxfx.effects import (
    grain, glow, halftone, scanlines, duotone,
    vignette, chromatic_aberration, bloom, glass_card, pattern_overlay,
)
from ideamaxfx.animate import (
    bar_grow, line_draw, radar_sweep, scatter_fade,
    counter_roll, pie_fill, heatmap_reveal, network_build,
    export_gif,
)
from ideamaxfx.text import gradient_text, neon_text, outline_text, shadow_text, emboss_text
from ideamaxfx.utils.fonts import load_font

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
GALLERY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "gallery")
IMG_W, IMG_H = 400, 250          # Per-side size for before/after panels.
ANIM_W, ANIM_H = 800, 500       # Animation frame size.
TEXT_W, TEXT_H = 520, 420        # Text showcase size.
FPS = 10
DURATION = 1.5
HOLD = 1.0


# ===================================================================
# Helper utilities
# ===================================================================

def _make_test_image(w: int = IMG_W, h: int = IMG_H) -> Image.Image:
    """Synthetic gradient with bright hotspots."""
    y_idx = np.linspace(0, 1, h).reshape(h, 1)
    x_idx = np.linspace(0, 1, w).reshape(1, w)
    diag = (x_idx + y_idx) / 2.0

    r = np.clip(diag * 300, 0, 255)
    g = np.clip((1 - diag) * 200 + diag * 80, 0, 255)
    b = np.clip((1 - diag) * 255, 0, 255)

    arr = np.stack([r, g, b], axis=2).astype(np.uint8)
    img = Image.fromarray(arr, mode="RGB")

    draw = ImageDraw.Draw(img)
    spots = [(100, 70, 30), (250, 50, 25), (180, 180, 28), (330, 160, 32)]
    for cx, cy, rad in spots:
        draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
                     fill=(255, 255, 240))
    return img


def _side_by_side(
    original: Image.Image,
    effected: Image.Image,
    label: str,
) -> Image.Image:
    """Place original and effected images side by side with a divider."""
    divider_w = 4
    w = original.width + effected.width + divider_w
    header_h = 28
    h = max(original.height, effected.height) + header_h

    canvas = Image.new("RGB", (w, h), (13, 17, 23))
    draw = ImageDraw.Draw(canvas)
    font = load_font(size=12)

    # Header text
    draw.text((10, 6), f"Before", fill=(160, 160, 170), font=font)
    draw.text((original.width + divider_w + 10, 6), f"After: {label}",
              fill=(0, 245, 212), font=font)

    # Images
    orig_rgb = original.convert("RGB")
    eff_rgb = effected.convert("RGB")
    canvas.paste(orig_rgb, (0, header_h))
    canvas.paste(eff_rgb, (original.width + divider_w, header_h))

    # Divider line
    draw.rectangle(
        [original.width, header_h, original.width + divider_w - 1, h],
        fill=(0, 245, 212),
    )

    return canvas


# ===================================================================
# Part 1: Before / After comparisons (10 effects)
# ===================================================================

def generate_before_after(output_dir: str) -> list[str]:
    """Generate before/after images for 10 effects. Returns list of paths."""
    base = _make_test_image()

    effects: list[tuple[str, Image.Image]] = [
        ("grain",     grain(base, intensity=0.08)),
        ("glow",      glow(base, color=(0, 245, 212), radius=20, intensity=0.6)),
        ("halftone",  halftone(base, dot_size=5, spacing=7).convert("RGB")),
        ("scanlines", scanlines(base, spacing=4, opacity=0.35)),
        ("duotone",   duotone(base, dark_color=(10, 10, 50), light_color=(255, 200, 50))),
        ("vignette",  vignette(base, strength=0.5, radius=0.8)),
        ("chromatic", chromatic_aberration(base, offset=6)),
        ("bloom",     bloom(base, threshold=180, radius=18, intensity=0.5)),
        ("glass_card", glass_card(base, x=50, y=40, w=300, h=160, blur=12).convert("RGB")),
        ("pattern",   pattern_overlay(base, pattern="grid", spacing=20, opacity=0.15).convert("RGB")),
    ]

    paths: list[str] = []
    for name, effected in effects:
        panel = _side_by_side(base, effected, name)
        path = os.path.join(output_dir, f"before_after_{name}.png")
        panel.save(path)
        paths.append(path)
        print(f"    before_after_{name}.png")

    return paths


# ===================================================================
# Part 2: Animation GIFs (8 chart types)
# ===================================================================

def generate_animations(output_dir: str) -> list[str]:
    """Generate 8 animated chart GIFs. Returns list of paths."""
    paths: list[str] = []

    # --- 1. Bar chart ---
    print("    anim_bar.gif ...")
    frames = bar_grow(
        labels=["Jan", "Feb", "Mar", "Apr", "May"],
        values=[120, 340, 250, 480, 390],
        title="Monthly Sales",
        width=ANIM_W, height=ANIM_H,
        fps=FPS, duration=DURATION, hold_seconds=HOLD,
        easing="ease_out_cubic",
    )
    p = os.path.join(output_dir, "anim_bar.gif")
    export_gif(frames, p, fps=FPS)
    paths.append(p)

    # --- 2. Line chart ---
    print("    anim_line.gif ...")
    frames = line_draw(
        x_values=[1, 2, 3, 4, 5, 6, 7],
        y_values=[[10, 25, 18, 42, 35, 60, 52],
                  [5, 15, 30, 28, 45, 38, 70]],
        labels=["Revenue", "Costs"],
        title="Revenue vs Costs",
        colors=[(0, 245, 212), (212, 33, 61)],
        width=ANIM_W, height=ANIM_H,
        fps=FPS, duration=DURATION, hold_seconds=HOLD,
        easing="ease_out_cubic",
    )
    p = os.path.join(output_dir, "anim_line.gif")
    export_gif(frames, p, fps=FPS)
    paths.append(p)

    # --- 3. Radar chart ---
    print("    anim_radar.gif ...")
    frames = radar_sweep(
        categories=["Speed", "Power", "Range", "Armor", "Stealth"],
        values=[85, 70, 60, 90, 45],
        width=500, height=500,
        fps=FPS, duration=DURATION, hold_seconds=HOLD,
        easing="ease_out_elastic",
    )
    p = os.path.join(output_dir, "anim_radar.gif")
    export_gif(frames, p, fps=FPS)
    paths.append(p)

    # --- 4. Scatter plot ---
    print("    anim_scatter.gif ...")
    rng = np.random.default_rng(42)
    sx = rng.normal(50, 15, 30).tolist()
    sy = [x * 0.8 + rng.normal(0, 8) for x in sx]
    sizes = rng.uniform(4, 12, 30).tolist()
    frames = scatter_fade(
        x_values=sx,
        y_values=sy,
        sizes=sizes,
        title="Correlation Plot",
        width=ANIM_W, height=ANIM_H,
        fps=FPS, duration=DURATION, hold_seconds=HOLD,
        easing="ease_out_cubic",
    )
    p = os.path.join(output_dir, "anim_scatter.gif")
    export_gif(frames, p, fps=FPS)
    paths.append(p)

    # --- 5. Counter ---
    print("    anim_counter.gif ...")
    frames = counter_roll(
        start=0, end=12_450,
        prefix="$", suffix="",
        label="Total Revenue",
        width=400, height=200,
        fps=FPS, duration=DURATION, hold_seconds=HOLD,
        easing="ease_out_expo",
    )
    p = os.path.join(output_dir, "anim_counter.gif")
    export_gif(frames, p, fps=FPS)
    paths.append(p)

    # --- 6. Pie chart ---
    print("    anim_pie.gif ...")
    frames = pie_fill(
        labels=["Chrome", "Safari", "Firefox", "Edge", "Other"],
        values=[64.7, 18.6, 3.2, 5.1, 8.4],
        donut=True,
        donut_ratio=0.5,
        width=500, height=500,
        fps=FPS, duration=DURATION, hold_seconds=HOLD,
        easing="ease_out_cubic",
    )
    p = os.path.join(output_dir, "anim_pie.gif")
    export_gif(frames, p, fps=FPS)
    paths.append(p)

    # --- 7. Heatmap ---
    print("    anim_heatmap.gif ...")
    heat_data = [
        [72, 85, 90, 65, 78],
        [45, 92, 88, 54, 67],
        [83, 61, 74, 96, 82],
        [58, 77, 69, 81, 93],
    ]
    frames = heatmap_reveal(
        data=heat_data,
        row_labels=["Q1", "Q2", "Q3", "Q4"],
        col_labels=["Web", "Mobile", "API", "IoT", "Cloud"],
        colormap="warm",
        width=600, height=ANIM_H,
        fps=FPS, duration=DURATION, hold_seconds=HOLD,
        easing="ease_out_cubic",
    )
    p = os.path.join(output_dir, "anim_heatmap.gif")
    export_gif(frames, p, fps=FPS)
    paths.append(p)

    # --- 8. Network graph ---
    print("    anim_network.gif ...")
    nodes = [
        ("API",      0.5, 0.15),
        ("Auth",     0.2, 0.4),
        ("DB",       0.8, 0.4),
        ("Cache",    0.35, 0.7),
        ("Queue",    0.65, 0.7),
        ("Worker",   0.5, 0.9),
    ]
    edges = [
        (0, 1, 1.0), (0, 2, 1.0),
        (1, 3, 0.7), (2, 4, 0.8),
        (3, 5, 0.6), (4, 5, 0.9),
        (1, 2, 0.4), (3, 4, 0.5),
    ]
    frames = network_build(
        nodes=nodes, edges=edges,
        width=600, height=ANIM_H,
        fps=FPS, duration=DURATION, hold_seconds=HOLD,
        easing="ease_out_cubic",
    )
    p = os.path.join(output_dir, "anim_network.gif")
    export_gif(frames, p, fps=FPS)
    paths.append(p)

    return paths


# ===================================================================
# Part 3: Text effect showcase
# ===================================================================

def generate_text_showcase(output_dir: str) -> str:
    """Create a composite image with all 5 text effects. Returns path."""
    font = load_font(size=28)
    small_font = load_font(size=11)

    canvas = Image.new("RGB", (TEXT_W, TEXT_H), (13, 17, 23))
    draw = ImageDraw.Draw(canvas)
    draw.text((15, 8), "ideamaxfx -- Text Effects", fill=(100, 100, 120), font=small_font)
    draw.line([(15, 26), (TEXT_W - 15, 26)], fill=(40, 40, 55), width=1)

    y = 40
    step = 55

    canvas = gradient_text(
        canvas, 20, y, "Gradient Text", font,
        color_start=(0, 245, 212), color_end=(212, 33, 180),
        direction="horizontal",
    )
    y += step

    canvas = neon_text(
        canvas, 20, y, "Neon Glow", font,
        color=(0, 245, 212), passes=5, spread=2.0,
    )
    y += step

    canvas = neon_text(
        canvas, 20, y, "Magenta Neon", font,
        color=(212, 33, 180), passes=5, spread=2.0,
    )
    y += step

    canvas = outline_text(
        canvas, 20, y, "Outlined Text", font,
        fill_color=(255, 255, 255), outline_color=(0, 200, 180),
        outline_width=2,
    )
    y += step

    canvas = shadow_text(
        canvas, 20, y, "Drop Shadow", font,
        text_color=(240, 240, 250), shadow_color=(0, 0, 0),
        offset=(4, 4), blur_radius=6,
    )
    y += step

    canvas = emboss_text(
        canvas, 20, y, "Embossed 3D", font,
        color=(180, 180, 200), depth=2,
    )

    path = os.path.join(output_dir, "text_effects.png")
    canvas.convert("RGB").save(path)
    print(f"    text_effects.png")
    return path


# ===================================================================
# Main
# ===================================================================

def main() -> None:
    os.makedirs(GALLERY_DIR, exist_ok=True)

    all_files: list[str] = []
    t0 = time.time()

    # --- Before/After ---
    print("\n=== Before / After comparisons (10 effects) ===")
    all_files.extend(generate_before_after(GALLERY_DIR))

    # --- Animations ---
    print("\n=== Animation GIFs (8 chart types) ===")
    all_files.extend(generate_animations(GALLERY_DIR))

    # --- Text showcase ---
    print("\n=== Text effect showcase ===")
    all_files.append(generate_text_showcase(GALLERY_DIR))

    elapsed = time.time() - t0

    # --- Summary ---
    print("\n" + "=" * 60)
    print(f"Gallery generation complete in {elapsed:.1f}s")
    print(f"Total files: {len(all_files)}")
    print(f"Output directory: {GALLERY_DIR}")
    print("-" * 60)

    ba_files = [f for f in all_files if "before_after" in f]
    anim_files = [f for f in all_files if "anim_" in f]
    text_files = [f for f in all_files if "text_" in f]

    print(f"\n  Before/After PNGs:  {len(ba_files)}")
    for f in ba_files:
        print(f"    - {os.path.basename(f)}")

    print(f"\n  Animation GIFs:     {len(anim_files)}")
    for f in anim_files:
        size_kb = os.path.getsize(f) / 1024
        print(f"    - {os.path.basename(f)}  ({size_kb:.0f} KB)")

    print(f"\n  Text showcase:      {len(text_files)}")
    for f in text_files:
        print(f"    - {os.path.basename(f)}")

    print("=" * 60)


if __name__ == "__main__":
    main()
