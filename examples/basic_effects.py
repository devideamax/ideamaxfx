"""basic_effects.py -- Demonstrate every standalone effect and the EffectsPipeline.

Generates a synthetic gradient test image using numpy, applies each of the 8
core post-production effects to it individually, and saves the results to
``examples/output/effect_*.png``.  Then chains all effects together through
the ``EffectsPipeline`` fluent API and saves the combined result to
``examples/output/pipeline_combined.png``.

Run::

    python examples/basic_effects.py

Output files (created automatically)::

    examples/output/effect_grain.png
    examples/output/effect_glow.png
    examples/output/effect_halftone.png
    examples/output/effect_scanlines.png
    examples/output/effect_duotone.png
    examples/output/effect_vignette.png
    examples/output/effect_chromatic.png
    examples/output/effect_bloom.png
    examples/output/pipeline_combined.png
"""

from __future__ import annotations

import os
import sys

import numpy as np
from PIL import Image

# ---------------------------------------------------------------------------
# Ensure the library is importable when running from the repo root.
# ---------------------------------------------------------------------------
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO, "src"))

from ideamaxfx.effects import (
    grain,
    glow,
    halftone,
    scanlines,
    duotone,
    vignette,
    chromatic_aberration,
    bloom,
)
from ideamaxfx import EffectsPipeline

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 800, 500
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def _make_test_image(w: int = WIDTH, h: int = HEIGHT) -> Image.Image:
    """Create a colourful gradient test image with bright hotspots.

    The image has a diagonal RGB gradient overlaid with several bright
    elliptical spots so that glow / bloom effects have something to latch
    onto.
    """
    # Base diagonal gradient (dark blue -> magenta -> orange).
    y_idx = np.linspace(0, 1, h).reshape(h, 1)
    x_idx = np.linspace(0, 1, w).reshape(1, w)
    diag = (x_idx + y_idx) / 2.0  # 0..1

    r = np.clip(diag * 300, 0, 255)
    g = np.clip((1 - diag) * 200 + diag * 80, 0, 255)
    b = np.clip((1 - diag) * 255, 0, 255)

    arr = np.stack([r, g, b], axis=2).astype(np.uint8)

    # Add bright hotspots so glow/bloom have visible bright areas.
    img = Image.fromarray(arr, mode="RGB")
    from PIL import ImageDraw

    draw = ImageDraw.Draw(img)
    hotspots = [
        (200, 150, 60),
        (500, 100, 45),
        (350, 350, 50),
        (650, 300, 55),
    ]
    for cx, cy, radius in hotspots:
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=(255, 255, 240),
        )

    return img


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Generating test image ...")
    base = _make_test_image()
    base.save(os.path.join(OUTPUT_DIR, "effect_original.png"))
    print(f"  Saved: effect_original.png  ({base.size[0]}x{base.size[1]})")

    # ------------------------------------------------------------------
    # Individual effects
    # ------------------------------------------------------------------
    effects = [
        ("grain",     lambda img: grain(img, intensity=0.08, monochrome=True)),
        ("glow",      lambda img: glow(img, color=(0, 245, 212), radius=25, intensity=0.6)),
        ("halftone",  lambda img: halftone(img, dot_size=5, spacing=7, angle=45.0)),
        ("scanlines", lambda img: scanlines(img, spacing=4, opacity=0.35)),
        ("duotone",   lambda img: duotone(img, dark_color=(10, 10, 50), light_color=(255, 200, 50))),
        ("vignette",  lambda img: vignette(img, strength=0.5, radius=0.8)),
        ("chromatic", lambda img: chromatic_aberration(img, offset=6, direction="horizontal")),
        ("bloom",     lambda img: bloom(img, threshold=180, radius=20, intensity=0.5)),
    ]

    for name, fn in effects:
        result = fn(base)
        path = os.path.join(OUTPUT_DIR, f"effect_{name}.png")
        # halftone returns mode "L"; convert for consistent PNG output.
        result.convert("RGB").save(path)
        print(f"  Saved: effect_{name}.png")

    # ------------------------------------------------------------------
    # Pipeline: chain every effect in one fluent call
    # ------------------------------------------------------------------
    print("\nRunning EffectsPipeline (all effects chained) ...")
    pipeline_path = os.path.join(OUTPUT_DIR, "pipeline_combined.png")
    (
        EffectsPipeline(base)
        .grain(0.05)
        .glow(color=(0, 245, 212), radius=20, intensity=0.4)
        .halftone(dot_size=4, spacing=6)
        .scanlines(spacing=5, opacity=0.25)
        .duotone(dark=(15, 15, 50), light=(255, 210, 60))
        .vignette(strength=0.4, radius=0.9)
        .chromatic(offset=4, direction="horizontal")
        .bloom(threshold=190, radius=15, intensity=0.35)
        .export(pipeline_path)
    )
    print(f"  Saved: pipeline_combined.png")

    print(f"\nDone. {len(effects) + 2} images written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
