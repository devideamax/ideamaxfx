"""Animated pie/donut chart sector fill."""

from __future__ import annotations

import math
from typing import Callable

from PIL import Image, ImageDraw

from ideamaxfx.animate.core import generate_frames
from ideamaxfx.color.convert import hex_to_rgb
from ideamaxfx.utils.fonts import load_font


def pie_fill(
    labels: list[str],
    values: list[float],
    colors: list[str] | list[tuple[int, int, int]] | None = None,
    donut: bool = False,
    donut_ratio: float = 0.5,
    width: int = 500,
    height: int = 500,
    bg_color: tuple[int, int, int] = (13, 17, 23),
    text_color: tuple[int, int, int] = (220, 220, 230),
    fps: int = 15,
    duration: float = 2.0,
    hold_seconds: float = 2.0,
    easing: str | Callable[[float], float] = "ease_out_cubic",
    font_path: str | None = None,
) -> list[Image.Image]:
    """Generate animated pie/donut chart frames.

    Args:
        labels: Sector labels.
        values: Sector values.
        colors: Hex strings or RGB tuples per sector.
        donut: If True, draw as donut chart.
        donut_ratio: Inner radius ratio (0-1) for donut.
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
    n = len(labels)
    total = sum(values)

    default_palette = [
        (212, 33, 61),
        (0, 102, 51),
        (0, 86, 160),
        (255, 165, 0),
        (148, 103, 189),
        (0, 245, 212),
        (255, 99, 71),
        (50, 205, 50),
    ]
    parsed_colors: list[tuple[int, int, int]] = []
    if colors:
        for c in colors:
            parsed_colors.append(hex_to_rgb(c) if isinstance(c, str) else c)
    else:
        parsed_colors = [default_palette[i % len(default_palette)] for i in range(n)]

    cx, cy = width // 2, height // 2
    radius = min(cx, cy) - 40
    inner_r = int(radius * donut_ratio) if donut else 0

    font = load_font(size=11, path=font_path)

    # Precompute angles
    angles: list[float] = []
    acc = 0.0
    for v in values:
        angles.append(acc)
        acc += v / total * 360
    angles.append(360.0)

    def render(progress: float) -> Image.Image:
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        sweep_limit = 360 * progress

        for i in range(n):
            start_a = angles[i]
            end_a = angles[i + 1]

            if start_a >= sweep_limit:
                break

            actual_end = min(end_a, sweep_limit)
            # PIL pieslice uses 0° at 3 o'clock, going clockwise
            draw.pieslice(
                [cx - radius, cy - radius, cx + radius, cy + radius],
                start=start_a - 90,
                end=actual_end - 90,
                fill=parsed_colors[i],
            )

        # Donut hole
        if donut and inner_r > 0:
            draw.ellipse(
                [cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
                fill=bg_color,
            )

        # Labels at final positions (only when enough progress)
        if progress > 0.8:
            for i in range(n):
                mid_angle = (angles[i] + angles[i + 1]) / 2 - 90
                label_r = radius * 0.7 if not donut else (radius + inner_r) / 2
                lx = cx + int(label_r * math.cos(math.radians(mid_angle)))
                ly = cy + int(label_r * math.sin(math.radians(mid_angle)))
                bbox = draw.textbbox((0, 0), labels[i], font=font)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
                draw.text((lx - tw // 2, ly - th // 2), labels[i], fill=text_color, font=font)

        return img

    return generate_frames(
        render, fps=fps, duration=duration, hold_seconds=hold_seconds, easing=easing
    )
