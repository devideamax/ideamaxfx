"""Animated radar/spider chart polygon sweep."""

from __future__ import annotations

import math
from typing import Callable

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
    title: str = "",
    subtitle: str = "",
    show_ring_values: bool = True,
    ring_count: int = 4,
    grid_color: tuple[int, int, int] = (68, 68, 68),
    sharpen: bool = True,
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
        title: Optional chart title.
        subtitle: Optional subtitle.
        show_ring_values: Show numbers on grid rings.
        ring_count: Number of concentric grid rings.
        grid_color: Color of grid lines.
        sharpen: Apply UnsharpMask after downscale.

    Returns:
        List of PIL Image frames.
    """
    n = len(categories)
    if max_value is None:
        max_value = max(values) * 1.1

    S = _SS

    # Title offset
    title_offset = 0
    if title or subtitle:
        title_offset = 30 * S
        if subtitle:
            title_offset += 16 * S

    cx, cy = (width * S) // 2, (height * S + title_offset) // 2
    radius = min(cx, cy - title_offset // 2) - 60 * S
    angles = [math.pi / 2 + 2 * math.pi * i / n for i in range(n)]

    font = load_font(size=FONT_AXIS * S, path=font_path)
    ring_font = load_font(size=FONT_DATA * S, path=font_path)

    def _point(angle: float, val: float) -> tuple[int, int]:
        r = radius * (val / max_value)
        return (int(cx + r * math.cos(angle)), int(cy - r * math.sin(angle)))

    def render(progress: float) -> Image.Image:
        img = Image.new("RGBA", (width * S, height * S), (*bg_color, 255))
        draw = ImageDraw.Draw(img)

        # Title
        if title or subtitle:
            draw_title(draw, title, subtitle, width * S, 8 * S, S, font_path)

        # Grid rings
        for ring in range(1, ring_count + 1):
            ring_r = radius * ring / ring_count
            pts = []
            for a in angles:
                pts.append((int(cx + ring_r * math.cos(a)), int(cy - ring_r * math.sin(a))))
            pts.append(pts[0])
            draw.line(pts, fill=grid_color, width=max(1, S))

            # Ring value labels near 12-o'clock axis
            if show_ring_values:
                ring_val = max_value * ring / ring_count
                label = format_number(ring_val)
                # Position slightly offset from the vertical axis
                lx = cx + 6 * S
                ly = int(cy - ring_r) - 2 * S
                bbox = draw.textbbox((0, 0), label, font=ring_font)
                lh = bbox[3] - bbox[1]
                draw.text((lx, ly - lh // 2), label, fill=COLOR_TEXT_MUTED, font=ring_font)

        # Axis lines
        for a in angles:
            end = (int(cx + radius * math.cos(a)), int(cy - radius * math.sin(a)))
            draw.line([(cx, cy), end], fill=grid_color, width=max(1, S))

        # Category labels
        for i, cat in enumerate(categories):
            lx = int(cx + (radius + 25 * S) * math.cos(angles[i]))
            ly = int(cy - (radius + 25 * S) * math.sin(angles[i]))
            bbox = draw.textbbox((0, 0), cat, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            draw.text((lx - tw // 2, ly - th // 2), cat, fill=text_color, font=font)

        # Animated polygon
        animated_vals = [v * progress for v in values]
        points = [_point(angles[i], animated_vals[i]) for i in range(n)]

        if len(points) >= 3:
            # Fill
            fill_layer = Image.new("RGBA", (width * S, height * S), (0, 0, 0, 0))
            fill_draw = ImageDraw.Draw(fill_layer)
            fill_draw.polygon(points, fill=(*color, fill_opacity))
            img = Image.alpha_composite(img, fill_layer)

            # Edge
            draw2 = ImageDraw.Draw(img)
            edge_pts = points + [points[0]]
            draw2.line(edge_pts, fill=(*color, 255), width=2 * S)

            # Dots
            for p in points:
                r = 4 * S
                draw2.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=(*color, 255))

        return finalize_frame(img, width, height, sharpen=sharpen)

    return generate_frames(
        render, fps=fps, duration=duration, hold_seconds=hold_seconds, easing=easing
    )
