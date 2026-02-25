"""Animated line chart progressive draw."""

from __future__ import annotations

from typing import Callable

from PIL import Image, ImageDraw

from ideamaxfx.animate.chart_utils import (
    _SS,
    compute_margins,
    compute_nice_ticks,
    draw_gridlines,
    draw_legend,
    draw_title,
    draw_x_axis,
    draw_y_axis,
    finalize_frame,
    format_number,
    parse_colors,
)
from ideamaxfx.animate.core import generate_frames


def line_draw(
    x_values: list[float],
    y_values: list[float] | list[list[float]],
    colors: list[str] | list[tuple[int, int, int]] | None = None,
    labels: list[str] | None = None,
    width: int = 800,
    height: int = 500,
    bg_color: tuple[int, int, int] = (13, 17, 23),
    text_color: tuple[int, int, int] = (220, 220, 230),
    line_width: int = 3,
    fps: int = 15,
    duration: float = 2.0,
    hold_seconds: float = 2.0,
    easing: str | Callable[[float], float] = "ease_out_cubic",
    title: str = "",
    subtitle: str = "",
    font_path: str | None = None,
    show_gridlines: bool = True,
    show_points: bool = True,
    point_radius: int | None = None,
    show_legend: bool = True,
    x_label: str = "",
    y_label: str = "",
    sharpen: bool = True,
) -> list[Image.Image]:
    """Generate animated line chart frames with progressive drawing.

    Args:
        x_values: X-axis values.
        y_values: Single series or list of series.
        colors: Colors for each series.
        labels: Series labels.
        width: Image width.
        height: Image height.
        bg_color: Background color.
        text_color: Text color.
        line_width: Line thickness.
        fps: Frames per second.
        duration: Animation duration.
        hold_seconds: Hold final frame.
        easing: Easing function name or callable.
        title: Optional chart title.
        subtitle: Optional subtitle.
        font_path: Optional font path.
        show_gridlines: Draw horizontal gridlines.
        show_points: Draw data points.
        point_radius: Point radius (None = auto).
        show_legend: Show legend when multiple series with labels.
        x_label: X-axis label.
        y_label: Y-axis label.
        sharpen: Apply UnsharpMask after downscale.

    Returns:
        List of PIL Image frames.
    """
    if not x_values:
        raise ValueError("x_values must not be empty")

    # Normalize to list of series
    series: list[list[float]]
    if y_values and isinstance(y_values[0], (list, tuple)):
        series = [list(s) for s in y_values]  # type: ignore[union-attr]
    else:
        series = [list(y_values)]  # type: ignore[arg-type]

    n_series = len(series)
    n_points = len(x_values)

    parsed_colors = parse_colors(colors, n_series)

    S = _SS

    # Data ranges
    all_y = [v for s in series for v in s]
    y_min_data = min(all_y)
    y_max_data = max(all_y)
    x_min = min(x_values)
    x_max = max(x_values)
    x_range = x_max - x_min if x_max != x_min else 1.0

    # Nice ticks for Y-axis
    y_ticks = compute_nice_ticks(y_min_data, y_max_data)
    y_min = y_ticks[0] if y_ticks else y_min_data
    y_max = y_ticks[-1] if y_ticks else y_max_data
    y_range = y_max - y_min if y_max != y_min else 1.0

    # X-axis labels
    x_ticks = compute_nice_ticks(x_min, x_max, target_count=min(n_points, 8))
    x_labels_str = [format_number(t) for t in x_ticks]
    y_labels_str = [format_number(t) for t in y_ticks]

    # Determine if legend needed
    has_legend = show_legend and labels is not None and n_series > 1

    # Compute dynamic margins
    tmp_img = Image.new("RGB", (width * S, height * S))
    tmp_draw = ImageDraw.Draw(tmp_img)
    margins = compute_margins(
        tmp_draw, y_labels_str, x_labels_str, title, subtitle, has_legend, S, font_path
    )
    if has_legend:
        margins["bottom"] += 20 * S  # space for legend below

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

    # Point radius
    pr = point_radius if point_radius is not None else max(2, line_width)

    def _to_pixel(xi: float, yi: float) -> tuple[int, int]:
        px = margin_left + int((xi - x_min) / x_range * chart_w)
        py = margin_top + chart_h - int((yi - y_min) / y_range * chart_h)
        return (px, py)

    def render(progress: float) -> Image.Image:
        img = Image.new("RGB", (width * S, height * S), bg_color)
        draw = ImageDraw.Draw(img)

        # Title
        draw_title(draw, title, subtitle, width * S, 8 * S, S, font_path)

        # Gridlines (behind data)
        if show_gridlines:
            draw_gridlines(draw, y_ticks, chart_area, y_min, y_max, S)

        # Axes with numbers
        draw_y_axis(draw, y_ticks, chart_area, y_min, y_max, S, font_path)

        # X-axis
        x_positions = [_to_pixel(t, y_min)[0] for t in x_ticks]
        draw_x_axis(draw, x_labels_str, x_positions, chart_area, S, font_path)

        # Draw each series
        visible_points = max(1, int(n_points * progress))
        for si, s in enumerate(series):
            points = [_to_pixel(x_values[j], s[j]) for j in range(visible_points)]
            if len(points) >= 2:
                draw.line(points, fill=parsed_colors[si], width=line_width * S)
            if show_points:
                for p in points:
                    r = pr * S
                    draw.ellipse(
                        [p[0] - r, p[1] - r, p[0] + r, p[1] + r],
                        fill=parsed_colors[si],
                    )

        # Legend
        if has_legend and labels:
            draw_legend(
                draw, labels, parsed_colors, chart_area, width * S, S, font_path
            )

        return finalize_frame(img, width, height, sharpen=sharpen)

    return generate_frames(
        render, fps=fps, duration=duration, hold_seconds=hold_seconds, easing=easing
    )
