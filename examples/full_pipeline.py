"""full_pipeline.py -- Complete real-world workflow from chart to finished image.

Shows the end-to-end production pipeline that a user would typically follow:

1. **Create a chart** -- tries matplotlib first; falls back to a PIL-drawn
   chart if matplotlib is not installed.
2. **Apply post-production effects** via ``EffectsPipeline``.
3. **Add text overlay** using the ``shadow_text`` effect.
4. **Add a branded footer** using ``footer_bar``.
5. **Export** the final composited image.

Run::

    python examples/full_pipeline.py

Output::

    examples/output/full_pipeline.png
"""

from __future__ import annotations

import io
import os
import sys

from PIL import Image, ImageDraw

# ---------------------------------------------------------------------------
# Ensure the library is importable when running from the repo root.
# ---------------------------------------------------------------------------
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO, "src"))

from ideamaxfx import EffectsPipeline
from ideamaxfx.text import shadow_text
from ideamaxfx.watermark.footer import footer_bar
from ideamaxfx.utils.fonts import load_font

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 800, 500
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


# ---------------------------------------------------------------------------
# Step 1: Create a chart image
# ---------------------------------------------------------------------------

def _chart_with_matplotlib() -> Image.Image:
    """Render a simple bar chart using matplotlib and return it as a PIL Image."""
    import matplotlib
    matplotlib.use("Agg")  # non-interactive backend
    import matplotlib.pyplot as plt

    categories = ["Web", "Mobile", "Desktop", "API", "IoT"]
    values = [68, 54, 42, 87, 31]
    colors = ["#00F5D4", "#D42145", "#0056A0", "#FFA500", "#9467BD"]

    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
    fig.patch.set_facecolor("#0D1117")
    ax.set_facecolor("#0D1117")
    ax.bar(categories, values, color=colors, edgecolor="none", width=0.6)
    ax.set_ylabel("Uptime %", color="#DCDCE6", fontsize=12)
    ax.set_title("Service Uptime by Platform", color="#DCDCE6", fontsize=16)
    ax.tick_params(colors="#DCDCE6")
    for spine in ax.spines.values():
        spine.set_color("#3C3C46")
    ax.set_ylim(0, 100)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB").resize((WIDTH, HEIGHT), Image.LANCZOS)


def _chart_with_pil() -> Image.Image:
    """Draw a basic bar chart using only PIL (fallback when matplotlib is absent)."""
    img = Image.new("RGB", (WIDTH, HEIGHT), (13, 17, 23))
    draw = ImageDraw.Draw(img)

    categories = ["Web", "Mobile", "Desktop", "API", "IoT"]
    values = [68, 54, 42, 87, 31]
    colors = [
        (0, 245, 212),
        (212, 33, 69),
        (0, 86, 160),
        (255, 165, 0),
        (148, 103, 189),
    ]

    font = load_font(size=13)
    title_font = load_font(size=18)

    # Title
    title = "Service Uptime by Platform"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2, 15), title, fill=(220, 220, 230), font=title_font)

    margin_left, margin_right = 80, 40
    margin_top, margin_bottom = 55, 50
    chart_w = WIDTH - margin_left - margin_right
    chart_h = HEIGHT - margin_top - margin_bottom
    n = len(categories)
    gap = 20
    bar_w = max(8, (chart_w - gap * (n + 1)) // n)
    max_val = 100.0
    base_y = margin_top + chart_h

    # Baseline
    draw.line([(margin_left, base_y), (margin_left + chart_w, base_y)],
              fill=(60, 60, 70), width=1)

    for i in range(n):
        x = margin_left + gap + i * (bar_w + gap)
        bar_h = int((values[i] / max_val) * chart_h)
        y_top = base_y - bar_h
        draw.rectangle([x, y_top, x + bar_w, base_y], fill=colors[i])

        # Label
        lbl = categories[i]
        lbbox = draw.textbbox((0, 0), lbl, font=font)
        lw = lbbox[2] - lbbox[0]
        draw.text((x + (bar_w - lw) // 2, base_y + 6), lbl,
                  fill=(220, 220, 230), font=font)

        # Value above bar
        val_text = f"{values[i]}%"
        vbbox = draw.textbbox((0, 0), val_text, font=font)
        vw = vbbox[2] - vbbox[0]
        draw.text((x + (bar_w - vw) // 2, y_top - 18), val_text,
                  fill=(220, 220, 230), font=font)

    return img


def create_chart() -> Image.Image:
    """Create a chart image, preferring matplotlib but falling back to PIL."""
    try:
        return _chart_with_matplotlib()
    except ImportError:
        print("  matplotlib not found -- using PIL fallback chart.")
        return _chart_with_pil()


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Step 1: Chart
    print("Step 1/4  Creating chart ...")
    chart = create_chart()

    # Step 2: Post-production pipeline
    print("Step 2/4  Applying post-production effects ...")
    processed = (
        EffectsPipeline(chart)
        .grain(0.04)
        .vignette(strength=0.35, radius=0.9)
        .scanlines(spacing=5, opacity=0.2)
        .bloom(threshold=200, radius=12, intensity=0.3)
        .image  # get the PIL Image without saving
    )

    # Step 3: Text overlay
    print("Step 3/4  Adding text overlay ...")
    overlay_font = load_font(size=14)
    processed = shadow_text(
        processed,
        x=WIDTH - 220, y=HEIGHT - 35,
        text="ideamaxfx demo",
        font=overlay_font,
        text_color=(180, 180, 200),
        shadow_color=(0, 0, 0),
        offset=(2, 2),
        blur_radius=4,
    )

    # Step 4: Footer bar
    print("Step 4/4  Adding branded footer ...")
    final = footer_bar(
        processed,
        text="Generated with ideamaxfx  |  github.com/ideamax/ideamaxfx",
        height=36,
        bg_color=(10, 10, 15),
        text_color=(120, 120, 140),
        line_color=(0, 245, 212),
        line_height=2,
        font_size=11,
    )

    # Export
    output_path = os.path.join(OUTPUT_DIR, "full_pipeline.png")
    final.convert("RGB").save(output_path, quality=95)
    print(f"\nSaved: {output_path}  ({final.size[0]}x{final.size[1]})")
    print("Complete workflow: chart -> effects -> text -> footer -> export")


if __name__ == "__main__":
    main()
