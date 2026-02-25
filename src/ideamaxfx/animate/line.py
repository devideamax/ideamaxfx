"""Animated line chart progressive draw."""

from __future__ import annotations

from typing import Callable

from PIL import Image, ImageDraw

from ideamaxfx.animate.core import generate_frames
from ideamaxfx.color.convert import hex_to_rgb
from ideamaxfx.utils.fonts import load_font


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
    font_path: str | None = None,
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
        font_path: Optional font path.

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

    default_palette = [
        (0, 245, 212),
        (212, 33, 61),
        (0, 86, 160),
        (255, 165, 0),
        (148, 103, 189),
        (50, 205, 50),
    ]
    parsed_colors: list[tuple[int, int, int]] = []
    if colors:
        for c in colors:
            parsed_colors.append(hex_to_rgb(c) if isinstance(c, str) else c)
    else:
        parsed_colors = [default_palette[i % len(default_palette)] for i in range(n_series)]

    margin = {"left": 60, "right": 30, "top": 50 if title else 25, "bottom": 40}
    chart_w = width - margin["left"] - margin["right"]
    chart_h = height - margin["top"] - margin["bottom"]

    all_y = [v for s in series for v in s]
    y_min = min(all_y)
    y_max = max(all_y)
    y_range = y_max - y_min if y_max != y_min else 1.0
    x_min = min(x_values)
    x_max = max(x_values)
    x_range = x_max - x_min if x_max != x_min else 1.0

    title_font = load_font(size=18, path=font_path)

    def _to_pixel(xi: float, yi: float) -> tuple[int, int]:
        px = margin["left"] + int((xi - x_min) / x_range * chart_w)
        py = margin["top"] + chart_h - int((yi - y_min) / y_range * chart_h)
        return (px, py)

    def render(progress: float) -> Image.Image:
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        if title:
            bbox = draw.textbbox((0, 0), title, font=title_font)
            tw = bbox[2] - bbox[0]
            draw.text(((width - tw) // 2, 8), title, fill=text_color, font=title_font)

        # Axes
        base_y = margin["top"] + chart_h
        draw.line(
            [(margin["left"], base_y), (margin["left"] + chart_w, base_y)],
            fill=(60, 60, 70),
            width=1,
        )
        draw.line(
            [(margin["left"], margin["top"]), (margin["left"], base_y)],
            fill=(60, 60, 70),
            width=1,
        )

        # Draw each series
        visible_points = max(1, int(n_points * progress))
        for si, s in enumerate(series):
            points = [_to_pixel(x_values[j], s[j]) for j in range(visible_points)]
            if len(points) >= 2:
                draw.line(points, fill=parsed_colors[si], width=line_width)
            for p in points:
                r = line_width + 1
                draw.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=parsed_colors[si])

        return img

    return generate_frames(
        render, fps=fps, duration=duration, hold_seconds=hold_seconds, easing=easing
    )
