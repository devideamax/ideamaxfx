"""Animated heatmap cell-by-cell reveal."""

from __future__ import annotations

from typing import Callable

import numpy as np
from PIL import Image, ImageDraw

from ideamaxfx.animate.core import generate_frames
from ideamaxfx.utils.fonts import load_font


def heatmap_reveal(
    data: list[list[float]],
    row_labels: list[str] | None = None,
    col_labels: list[str] | None = None,
    colormap: str = "warm",
    width: int = 600,
    height: int = 500,
    bg_color: tuple[int, int, int] = (13, 17, 23),
    text_color: tuple[int, int, int] = (200, 200, 210),
    fps: int = 15,
    duration: float = 2.0,
    hold_seconds: float = 2.0,
    easing: str | Callable[[float], float] = "ease_out_cubic",
    font_path: str | None = None,
) -> list[Image.Image]:
    """Generate animated heatmap with cell-by-cell reveal.

    Args:
        data: 2D list of values (rows x cols).
        row_labels: Labels for rows.
        col_labels: Labels for columns.
        colormap: Color scheme: "warm" (blue-red), "cool" (green-blue), "mono" (black-white).
        width: Image width.
        height: Image height.
        bg_color: Background color.
        text_color: Text color.
        fps: Frames per second.
        duration: Animation duration.
        hold_seconds: Hold final frame.
        easing: Easing function name or callable.
        font_path: Optional font path.

    Returns:
        List of PIL Image frames.
    """
    rows = len(data)
    cols = len(data[0]) if data else 0
    total_cells = rows * cols
    arr = np.array(data, dtype=float)
    vmin, vmax = float(arr.min()), float(arr.max())
    vrange = vmax - vmin if vmax != vmin else 1.0

    colormaps = {
        "warm": ((30, 60, 180), (220, 40, 40)),
        "cool": ((20, 140, 60), (30, 80, 200)),
        "mono": ((20, 20, 20), (240, 240, 240)),
    }
    c_low, c_high = colormaps.get(colormap, colormaps["warm"])

    margin_left = 80 if row_labels else 20
    margin_top = 40 if col_labels else 20
    margin_right = 20
    margin_bottom = 20
    chart_w = width - margin_left - margin_right
    chart_h = height - margin_top - margin_bottom
    cell_w = chart_w // max(1, cols)
    cell_h = chart_h // max(1, rows)

    font = load_font(size=10, path=font_path)

    def _color_for(val: float) -> tuple[int, int, int]:
        t = (val - vmin) / vrange
        return (
            int(c_low[0] + (c_high[0] - c_low[0]) * t),
            int(c_low[1] + (c_high[1] - c_low[1]) * t),
            int(c_low[2] + (c_high[2] - c_low[2]) * t),
        )

    def render(progress: float) -> Image.Image:
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        visible_cells = max(0, int(total_cells * progress))

        # Row-by-row reveal
        cell_idx = 0
        for r in range(rows):
            for c in range(cols):
                x = margin_left + c * cell_w
                y = margin_top + r * cell_h

                if cell_idx < visible_cells:
                    color = _color_for(data[r][c])
                    draw.rectangle([x, y, x + cell_w - 1, y + cell_h - 1], fill=color)

                    # Value text in cell
                    val_text = f"{data[r][c]:.0f}"
                    bbox = draw.textbbox((0, 0), val_text, font=font)
                    tw = bbox[2] - bbox[0]
                    th = bbox[3] - bbox[1]
                    draw.text(
                        (x + (cell_w - tw) // 2, y + (cell_h - th) // 2),
                        val_text,
                        fill=text_color,
                        font=font,
                    )
                else:
                    draw.rectangle(
                        [x, y, x + cell_w - 1, y + cell_h - 1],
                        fill=bg_color,
                        outline=(40, 40, 50),
                    )

                cell_idx += 1

        # Row labels
        if row_labels:
            for r, lbl in enumerate(row_labels):
                y = margin_top + r * cell_h + (cell_h - 12) // 2
                draw.text((4, y), lbl, fill=text_color, font=font)

        # Col labels
        if col_labels:
            for c, lbl in enumerate(col_labels):
                x = margin_left + c * cell_w
                bbox = draw.textbbox((0, 0), lbl, font=font)
                tw = bbox[2] - bbox[0]
                draw.text((x + (cell_w - tw) // 2, 4), lbl, fill=text_color, font=font)

        return img

    return generate_frames(
        render, fps=fps, duration=duration, hold_seconds=hold_seconds, easing=easing
    )
