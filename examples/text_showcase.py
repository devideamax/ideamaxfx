"""text_showcase.py -- Demonstrate all 5 text effects on a single dark canvas.

Renders each text effect at a different vertical position on a 400x200 dark
canvas:

- ``gradient_text`` with horizontal direction (cyan to magenta)
- ``gradient_text`` with vertical direction (gold to orange)
- ``neon_text`` with cyan glow
- ``neon_text`` with magenta glow
- ``outline_text`` with white fill and cyan outline
- ``shadow_text`` with a soft dark shadow
- ``emboss_text`` with a 3-D chiseled look

All effects are composited onto a single showcase image.

Run::

    python examples/text_showcase.py

Output::

    examples/output/text_showcase.png
"""

from __future__ import annotations

import os
import sys

from PIL import Image

# ---------------------------------------------------------------------------
# Ensure the library is importable when running from the repo root.
# ---------------------------------------------------------------------------
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO, "src"))

from ideamaxfx.text import gradient_text, neon_text, outline_text, shadow_text, emboss_text
from ideamaxfx.utils.fonts import load_font

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 520, 420
BG_COLOR = (13, 17, 23)
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    font = load_font(size=28)
    small_font = load_font(size=11)

    # Start with a dark canvas.
    canvas = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)

    # Add a subtle title.
    from PIL import ImageDraw
    draw = ImageDraw.Draw(canvas)
    draw.text((15, 8), "ideamaxfx -- Text Effects Showcase", fill=(100, 100, 120), font=small_font)
    draw.line([(15, 26), (WIDTH - 15, 26)], fill=(40, 40, 55), width=1)

    y_cursor = 40
    y_step = 55

    # ------------------------------------------------------------------
    # 1. Gradient text -- horizontal (cyan -> magenta)
    # ------------------------------------------------------------------
    canvas = gradient_text(
        canvas, x=20, y=y_cursor,
        text="Gradient (Horizontal)",
        font=font,
        color_start=(0, 245, 212),
        color_end=(212, 33, 180),
        direction="horizontal",
    )
    y_cursor += y_step

    # ------------------------------------------------------------------
    # 2. Gradient text -- vertical (gold -> orange)
    # ------------------------------------------------------------------
    canvas = gradient_text(
        canvas, x=20, y=y_cursor,
        text="Gradient (Vertical)",
        font=font,
        color_start=(255, 215, 0),
        color_end=(255, 100, 20),
        direction="vertical",
    )
    y_cursor += y_step

    # ------------------------------------------------------------------
    # 3. Neon text -- cyan glow
    # ------------------------------------------------------------------
    canvas = neon_text(
        canvas, x=20, y=y_cursor,
        text="Neon Cyan Glow",
        font=font,
        color=(0, 245, 212),
        passes=5,
        spread=2.0,
    )
    y_cursor += y_step

    # ------------------------------------------------------------------
    # 4. Neon text -- magenta glow
    # ------------------------------------------------------------------
    canvas = neon_text(
        canvas, x=20, y=y_cursor,
        text="Neon Magenta Glow",
        font=font,
        color=(212, 33, 180),
        passes=5,
        spread=2.0,
    )
    y_cursor += y_step

    # ------------------------------------------------------------------
    # 5. Outline text
    # ------------------------------------------------------------------
    canvas = outline_text(
        canvas, x=20, y=y_cursor,
        text="Outlined Text",
        font=font,
        fill_color=(255, 255, 255),
        outline_color=(0, 200, 180),
        outline_width=2,
    )
    y_cursor += y_step

    # ------------------------------------------------------------------
    # 6. Shadow text
    # ------------------------------------------------------------------
    canvas = shadow_text(
        canvas, x=20, y=y_cursor,
        text="Drop Shadow",
        font=font,
        text_color=(240, 240, 250),
        shadow_color=(0, 0, 0),
        offset=(4, 4),
        blur_radius=6,
    )
    y_cursor += y_step

    # ------------------------------------------------------------------
    # 7. Emboss text
    # ------------------------------------------------------------------
    canvas = emboss_text(
        canvas, x=20, y=y_cursor,
        text="Embossed 3D",
        font=font,
        color=(180, 180, 200),
        depth=2,
    )

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------
    # Convert from RGBA back to RGB for a clean PNG.
    output_path = os.path.join(OUTPUT_DIR, "text_showcase.png")
    canvas.convert("RGB").save(output_path)
    print(f"Saved: {output_path}  ({WIDTH}x{HEIGHT})")
    print("7 text effects rendered on a single canvas.")


if __name__ == "__main__":
    main()
