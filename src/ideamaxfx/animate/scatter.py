"""Animated scatter plot fade-in."""

from __future__ import annotations

from typing import Callable

from PIL import Image, ImageDraw

from ideamaxfx.animate.core import generate_frames
from ideamaxfx.utils.fonts import load_font


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
    font_path: str | None = None,
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
        font_path: Optional font path.

    Returns:
        List of PIL Image frames.
    """
    n = len(x_values)
    if sizes is None:
        sizes = [6.0] * n

    margin = {"left": 50, "right": 30, "top": 45 if title else 20, "bottom": 35}
    chart_w = width - margin["left"] - margin["right"]
    chart_h = height - margin["top"] - margin["bottom"]

    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values), max(y_values)
    x_range = x_max - x_min if x_max != x_min else 1.0
    y_range = y_max - y_min if y_max != y_min else 1.0

    title_font = load_font(size=18, path=font_path)

    def _to_pixel(xi: float, yi: float) -> tuple[int, int]:
        px = margin["left"] + int((xi - x_min) / x_range * chart_w)
        py = margin["top"] + chart_h - int((yi - y_min) / y_range * chart_h)
        return (px, py)

    def render(progress: float) -> Image.Image:
        img = Image.new("RGBA", (width, height), (*bg_color, 255))
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
            [(margin["left"], margin["top"]), (margin["left"], base_y)], fill=(60, 60, 70), width=1
        )

        # Points appear progressively
        visible = max(0, int(n * progress))
        alpha = min(255, int(255 * progress * 1.5))

        for i in range(visible):
            px, py = _to_pixel(x_values[i], y_values[i])
            r = int(sizes[i])
            draw.ellipse(
                [px - r, py - r, px + r, py + r],
                fill=(*color, alpha),
            )

        return img.convert("RGB")

    return generate_frames(
        render, fps=fps, duration=duration, hold_seconds=hold_seconds, easing=easing
    )
