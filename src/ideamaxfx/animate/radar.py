"""Animated radar/spider chart polygon sweep."""

from __future__ import annotations

import math
from typing import Callable

from PIL import Image, ImageDraw

from ideamaxfx.animate.core import generate_frames
from ideamaxfx.utils.fonts import load_font


def radar_sweep(
    categories: list[str],
    values: list[float],
    max_value: float | None = None,
    color: tuple[int, int, int] = (0, 245, 212),
    fill_opacity: int = 60,
    width: int = 500,
    height: int = 500,
    bg_color: tuple[int, int, int] = (13, 17, 23),
    text_color: tuple[int, int, int] = (200, 200, 210),
    fps: int = 15,
    duration: float = 2.0,
    hold_seconds: float = 2.0,
    easing: str | Callable[[float], float] = "ease_out_cubic",
    font_path: str | None = None,
) -> list[Image.Image]:
    """Generate animated radar chart with polygon sweep.

    Args:
        categories: Axis labels.
        values: Values for each axis.
        max_value: Maximum value for scaling. Auto-detected if None.
        color: Polygon edge color.
        fill_opacity: Polygon fill alpha (0-255).
        width: Image width.
        height: Image height.
        bg_color: Background color.
        text_color: Label text color.
        fps: Frames per second.
        duration: Animation duration.
        hold_seconds: Hold final frame.
        easing: Easing function name or callable.
        font_path: Optional font path.

    Returns:
        List of PIL Image frames.
    """
    n = len(categories)
    if max_value is None:
        max_value = max(values) * 1.1

    cx, cy = width // 2, height // 2
    radius = min(cx, cy) - 60
    angles = [math.pi / 2 + 2 * math.pi * i / n for i in range(n)]

    font = load_font(size=12, path=font_path)

    def _point(angle: float, val: float) -> tuple[int, int]:
        r = radius * (val / max_value)
        return (int(cx + r * math.cos(angle)), int(cy - r * math.sin(angle)))

    def render(progress: float) -> Image.Image:
        img = Image.new("RGBA", (width, height), (*bg_color, 255))
        draw = ImageDraw.Draw(img)

        # Grid rings
        for ring in range(1, 5):
            ring_r = radius * ring / 4
            pts = []
            for a in angles:
                pts.append((int(cx + ring_r * math.cos(a)), int(cy - ring_r * math.sin(a))))
            pts.append(pts[0])
            draw.line(pts, fill=(50, 50, 60), width=1)

        # Axis lines
        for a in angles:
            end = (int(cx + radius * math.cos(a)), int(cy - radius * math.sin(a)))
            draw.line([(cx, cy), end], fill=(50, 50, 60), width=1)

        # Category labels
        for i, cat in enumerate(categories):
            lx = int(cx + (radius + 25) * math.cos(angles[i]))
            ly = int(cy - (radius + 25) * math.sin(angles[i]))
            bbox = draw.textbbox((0, 0), cat, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            draw.text((lx - tw // 2, ly - th // 2), cat, fill=text_color, font=font)

        # Animated polygon
        animated_vals = [v * progress for v in values]
        points = [_point(angles[i], animated_vals[i]) for i in range(n)]

        if len(points) >= 3:
            # Fill
            fill_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            fill_draw = ImageDraw.Draw(fill_layer)
            fill_draw.polygon(points, fill=(*color, fill_opacity))
            img = Image.alpha_composite(img, fill_layer)

            # Edge
            draw2 = ImageDraw.Draw(img)
            edge_pts = points + [points[0]]
            draw2.line(edge_pts, fill=(*color, 255), width=2)

            # Dots
            for p in points:
                draw2.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=(*color, 255))

        return img.convert("RGB")

    return generate_frames(
        render, fps=fps, duration=duration, hold_seconds=hold_seconds, easing=easing
    )
