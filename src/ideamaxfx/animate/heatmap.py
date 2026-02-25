"""Animated heatmap cell-by-cell reveal."""

from __future__ import annotations

from typing import Callable

import numpy as np
from PIL import Image, ImageDraw

from ideamaxfx.animate.chart_utils import (
    _SS,
    COLOR_TEXT_MUTED,
    FONT_AXIS,
    FONT_DATA,
    draw_title,
    finalize_frame,
    format_number,
)
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
    title: str = "",
    subtitle: str = "",
    show_color_bar: bool = True,
    show_values: bool = True,
    sharpen: bool = True,
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
        title: Optional chart title.
        subtitle: Optional subtitle.
        show_color_bar: Show vertical gradient legend at right.
        show_values: Show values inside cells.
        sharpen: Apply UnsharpMask after downscale.

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

    S = _SS

    # Title offset
    title_offset = 0
    if title or subtitle:
        title_offset = 30 * S
        if subtitle:
            title_offset += 16 * S

    margin_left = (80 if row_labels else 20) * S
    margin_top = (40 if col_labels else 20) * S + title_offset
    margin_right = (60 if show_color_bar else 20) * S
    margin_bottom = 20 * S
    chart_w = width * S - margin_left - margin_right
    chart_h = height * S - margin_top - margin_bottom
    cell_w = chart_w // max(1, cols)
    cell_h = chart_h // max(1, rows)

    font = load_font(size=FONT_DATA * S, path=font_path)
    label_font = load_font(size=FONT_AXIS * S, path=font_path)

    def _color_for(val: float) -> tuple[int, int, int]:
        t = (val - vmin) / vrange
        return (
            int(c_low[0] + (c_high[0] - c_low[0]) * t),
            int(c_low[1] + (c_high[1] - c_low[1]) * t),
            int(c_low[2] + (c_high[2] - c_low[2]) * t),
        )

    def _text_color_for(cell_color: tuple[int, int, int]) -> tuple[int, int, int]:
        """Auto contrast: light text on dark cells, dark text on light cells."""
        luminance = 0.299 * cell_color[0] + 0.587 * cell_color[1] + 0.114 * cell_color[2]
        return (255, 255, 255) if luminance < 128 else (20, 20, 20)

    def render(progress: float) -> Image.Image:
        img = Image.new("RGB", (width * S, height * S), bg_color)
        draw = ImageDraw.Draw(img)

        # Title
        if title or subtitle:
            draw_title(draw, title, subtitle, width * S, 8 * S, S, font_path)

        visible_cells = max(0, int(total_cells * progress))

        # Row-by-row reveal
        cell_idx = 0
        for r in range(rows):
            for c in range(cols):
                x = margin_left + c * cell_w
                y = margin_top + r * cell_h

                if cell_idx < visible_cells:
                    cell_color = _color_for(data[r][c])
                    draw.rectangle([x, y, x + cell_w - 1, y + cell_h - 1], fill=cell_color)

                    # Value text in cell with auto contrast
                    if show_values:
                        val_text = f"{data[r][c]:.0f}"
                        bbox = draw.textbbox((0, 0), val_text, font=font)
                        tw = bbox[2] - bbox[0]
                        th = bbox[3] - bbox[1]
                        t_color = _text_color_for(cell_color)
                        draw.text(
                            (x + (cell_w - tw) // 2, y + (cell_h - th) // 2),
                            val_text,
                            fill=t_color,
                            font=font,
                        )
                else:
                    draw.rectangle(
                        [x, y, x + cell_w - 1, y + cell_h - 1],
                        fill=bg_color,
                        outline=(40, 40, 50),
                        width=max(1, S),
                    )

                cell_idx += 1

        # Row labels
        if row_labels:
            for r, lbl in enumerate(row_labels):
                y = margin_top + r * cell_h
                bbox = draw.textbbox((0, 0), lbl, font=label_font)
                lh = bbox[3] - bbox[1]
                lw = bbox[2] - bbox[0]
                draw.text(
                    (margin_left - lw - 8 * S, y + (cell_h - lh) // 2),
                    lbl,
                    fill=COLOR_TEXT_MUTED,
                    font=label_font,
                )

        # Col labels
        if col_labels:
            for c, lbl in enumerate(col_labels):
                x = margin_left + c * cell_w
                bbox = draw.textbbox((0, 0), lbl, font=label_font)
                tw = bbox[2] - bbox[0]
                draw.text(
                    (x + (cell_w - tw) // 2, margin_top - 18 * S),
                    lbl,
                    fill=COLOR_TEXT_MUTED,
                    font=label_font,
                )

        # Color bar (vertical gradient legend at right)
        if show_color_bar:
            bar_x = margin_left + chart_w + 16 * S
            bar_w = 12 * S
            bar_top = margin_top
            bar_bottom = margin_top + chart_h
            bar_height = bar_bottom - bar_top

            for py in range(bar_height):
                t = 1.0 - py / max(1, bar_height - 1)
                c_r = int(c_low[0] + (c_high[0] - c_low[0]) * t)
                c_g = int(c_low[1] + (c_high[1] - c_low[1]) * t)
                c_b = int(c_low[2] + (c_high[2] - c_low[2]) * t)
                draw.line(
                    [(bar_x, bar_top + py), (bar_x + bar_w, bar_top + py)],
                    fill=(c_r, c_g, c_b),
                )

            # Min/max labels
            max_label = format_number(vmax)
            min_label = format_number(vmin)
            small_font = load_font(size=(FONT_DATA - 1) * S, path=font_path)
            draw.text(
                (bar_x + bar_w + 4 * S, bar_top),
                max_label,
                fill=COLOR_TEXT_MUTED,
                font=small_font,
            )
            bbox = draw.textbbox((0, 0), min_label, font=small_font)
            lh = bbox[3] - bbox[1]
            draw.text(
                (bar_x + bar_w + 4 * S, bar_bottom - lh),
                min_label,
                fill=COLOR_TEXT_MUTED,
                font=small_font,
            )

        return finalize_frame(img, width, height, sharpen=sharpen)

    return generate_frames(
        render, fps=fps, duration=duration, hold_seconds=hold_seconds, easing=easing
    )
