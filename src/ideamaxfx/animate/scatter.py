"""Animated scatter plot fade-in."""

from __future__ import annotations

from typing import Callable

from PIL import Image, ImageDraw

from ideamaxfx.animate.chart_utils import (
    _SS,
    compute_margins,
    compute_nice_ticks,
    draw_axis_labels,
    draw_gridlines,
    draw_title,
    draw_x_axis,
    draw_y_axis,
    finalize_frame,
    format_number,
)
from ideamaxfx.animate.core import generate_frames


def scatter_fade(
    x_values: list[float],
    y_values: list[float],
    sizes: list[float] | None = None,
    color: tuple[int, int, int] = (0, 245, 212),
    width: int = 800,
    height: int = 500,
    bg_color: tuple[int, int, int] = (13, 17, 23),
    text_color: tuple[int, int, int] = (200, 200, 210),
    fps: int = 15,
    duration: float = 2.0,
    hold_seconds: float = 2.0,
    easing: str | Callable[[float], float] = "ease_out_cubic",
    title: str = "",
    subtitle: str = "",
    font_path: str | None = None,
    show_gridlines: bool = True,
    show_legend: bool = True,
    x_label: str = "",
    y_label: str = "",
    sharpen: bool = True,
) -> list[Image.Image]:
    """Generate animated scatter plot with points fading in.

    Args:
        x_values: X coordinates.
        y_values: Y coordinates.
        sizes: Point sizes. Uniform if None.
        color: Point color.
        width: Image width.
        height: Image height.
        bg_color: Background color.
        text_color: Text color.
        fps: Frames per second.
        duration: Animation duration.
        hold_seconds: Hold final frame.
        easing: Easing function name or callable.
        title: Optional chart title.
        subtitle: Optional subtitle.
        font_path: Optional font path.
        show_gridlines: Draw horizontal gridlines.
        show_legend: Show legend (reserved for future multi-group support).
        x_label: X-axis label.
        y_label: Y-axis label.
        sharpen: Apply UnsharpMask after downscale.

    Returns:
        List of PIL Image frames.
    """
    n = len(x_values)
    if sizes is None:
        sizes = [4.0] * n

    S = _SS

    # Data ranges
    x_min_data, x_max_data = min(x_values), max(x_values)
    y_min_data, y_max_data = min(y_values), max(y_values)

    # Nice ticks
    y_ticks = compute_nice_ticks(y_min_data, y_max_data)
    x_ticks = compute_nice_ticks(x_min_data, x_max_data, target_count=min(n, 8))
    y_min = y_ticks[0] if y_ticks else y_min_data
    y_max = y_ticks[-1] if y_ticks else y_max_data
    x_min = x_ticks[0] if x_ticks else x_min_data
    x_max = x_ticks[-1] if x_ticks else x_max_data
    x_range = x_max - x_min if x_max != x_min else 1.0
    y_range = y_max - y_min if y_max != y_min else 1.0

    x_labels_str = [format_number(t) for t in x_ticks]
    y_labels_str = [format_number(t) for t in y_ticks]

    # Dynamic margins
    tmp_img = Image.new("RGB", (width * S, height * S))
    tmp_draw = ImageDraw.Draw(tmp_img)
    margins = compute_margins(
        tmp_draw, y_labels_str, x_labels_str, title, subtitle, False, S, font_path
    )
    if x_label:
        margins["bottom"] += 18 * S
    if y_label:
        margins["left"] += 18 * S

    margin_left = margins["left"]
    margin_right = margins["right"]
    margin_top = margins["top"]
    margin_bottom = margins["bottom"]
    chart_w = width * S - margin_left - margin_right
    chart_h = height * S - margin_top - margin_bottom

    chart_area = {
        "left": margin_left,
        "top": margin_top,
        "bottom": margin_top + chart_h,
        "right_x": margin_left + chart_w,
    }

    def _to_pixel(xi: float, yi: float) -> tuple[int, int]:
        px = margin_left + int((xi - x_min) / x_range * chart_w)
        py = margin_top + chart_h - int((yi - y_min) / y_range * chart_h)
        return (px, py)

    def render(progress: float) -> Image.Image:
        img = Image.new("RGBA", (width * S, height * S), (*bg_color, 255))
        draw = ImageDraw.Draw(img)

        # Title
        draw_title(draw, title, subtitle, width * S, 8 * S, S, font_path)

        # Gridlines (behind points)
        if show_gridlines:
            draw_gridlines(draw, y_ticks, chart_area, y_min, y_max, S)

        # Axes with numbers
        draw_y_axis(draw, y_ticks, chart_area, y_min, y_max, S, font_path)
        x_positions = [_to_pixel(t, y_min)[0] for t in x_ticks]
        draw_x_axis(draw, x_labels_str, x_positions, chart_area, S, font_path)

        # Axis labels
        if x_label or y_label:
            draw_axis_labels(draw, x_label, y_label, chart_area, width * S, S, font_path)

        # Points appear progressively
        visible = max(0, int(n * progress))
        alpha = min(255, int(255 * progress * 1.5))

        for i in range(visible):
            px, py = _to_pixel(x_values[i], y_values[i])
            r = int(sizes[i]) * S
            draw.ellipse(
                [px - r, py - r, px + r, py + r],
                fill=(*color, alpha),
            )

        return finalize_frame(img, width, height, sharpen=sharpen)

    return generate_frames(
        render, fps=fps, duration=duration, hold_seconds=hold_seconds, easing=easing
    )
