"""Animated pie/donut chart sector fill."""

from __future__ import annotations

import math
from typing import Callable

from PIL import Image, ImageDraw

from ideamaxfx.animate.chart_utils import (
    _SS,
    COLOR_TEXT_MUTED,
    FONT_DATA,
    FONT_LEGEND,
    draw_title,
    finalize_frame,
    parse_colors,
)
from ideamaxfx.animate.core import generate_frames
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
    title: str = "",
    subtitle: str = "",
    show_percentages: bool = True,
    show_legend: bool = True,
    legend_position: str = "right",
    label_style: str = "fade",
    sharpen: bool = True,
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
        title: Optional chart title.
        subtitle: Optional subtitle.
        show_percentages: Show percentage on sectors.
        show_legend: Show color legend.
        legend_position: "right" or "bottom".
        label_style: "fade" for gradual fade-in, "pop" for original behavior.
        sharpen: Apply UnsharpMask after downscale.

    Returns:
        List of PIL Image frames.
    """
    n = len(labels)
    total = sum(values)

    parsed_colors = parse_colors(colors, n)

    S = _SS

    # Title offset
    title_offset = 0
    if title or subtitle:
        title_offset = 30 * S
        if subtitle:
            title_offset += 16 * S

    # Legend space
    legend_right_space = 0
    legend_bottom_space = 0
    if show_legend:
        if legend_position == "right":
            legend_right_space = 120 * S
        else:
            legend_bottom_space = 30 * S

    # Pie center and radius
    avail_w = width * S - legend_right_space
    avail_h = height * S - title_offset - legend_bottom_space
    cx = avail_w // 2
    cy = title_offset + avail_h // 2
    radius = min(avail_w, avail_h) // 2 - 40 * S
    inner_r = int(radius * donut_ratio) if donut else 0

    font = load_font(size=FONT_DATA * S, path=font_path)
    pct_font = load_font(size=FONT_DATA * S, path=font_path)
    legend_font = load_font(size=FONT_LEGEND * S, path=font_path)

    # Precompute angles
    angles: list[float] = []
    acc = 0.0
    for v in values:
        angles.append(acc)
        acc += v / total * 360
    angles.append(360.0)

    def render(progress: float) -> Image.Image:
        img = Image.new("RGB", (width * S, height * S), bg_color)
        draw = ImageDraw.Draw(img)

        # Title
        if title or subtitle:
            draw_title(draw, title, subtitle, width * S, 8 * S, S, font_path)

        sweep_limit = 360 * progress

        for i in range(n):
            start_a = angles[i]
            end_a = angles[i + 1]

            if start_a >= sweep_limit:
                break

            actual_end = min(end_a, sweep_limit)
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

        # Labels + percentages
        if label_style == "fade":
            label_alpha = max(0.0, min(1.0, (progress - 0.5) * 2.0))
        else:
            label_alpha = 1.0 if progress > 0.8 else 0.0

        if label_alpha > 0:
            for i in range(n):
                mid_a = angles[i] + angles[i + 1]
                if mid_a / 2 > sweep_limit:
                    break
                mid_angle = mid_a / 2 - 90
                label_r = radius * 0.7 if not donut else (radius + inner_r) / 2
                lx = cx + int(label_r * math.cos(math.radians(mid_angle)))
                ly = cy + int(label_r * math.sin(math.radians(mid_angle)))

                # Auto-contrast: pick light or dark text based on sector color
                sc = parsed_colors[i]
                luminance = 0.299 * sc[0] + 0.587 * sc[1] + 0.114 * sc[2]
                base_color = (255, 255, 255) if luminance < 128 else (20, 20, 20)
                blended = tuple(
                    int(bg_color[c] + (base_color[c] - bg_color[c]) * label_alpha)
                    for c in range(3)
                )

                # Percentage text
                if show_percentages:
                    pct = f"{values[i] / total * 100:.0f}%"
                    bbox = draw.textbbox((0, 0), pct, font=pct_font)
                    tw = bbox[2] - bbox[0]
                    th = bbox[3] - bbox[1]
                    draw.text(
                        (lx - tw // 2, ly - th // 2),
                        pct,
                        fill=blended,
                        font=pct_font,
                    )
                else:
                    # Show label name
                    bbox = draw.textbbox((0, 0), labels[i], font=font)
                    tw = bbox[2] - bbox[0]
                    th = bbox[3] - bbox[1]
                    draw.text(
                        (lx - tw // 2, ly - th // 2),
                        labels[i],
                        fill=blended,
                        font=font,
                    )

        # Legend
        if show_legend:
            box_size = 10 * S
            if legend_position == "right":
                lx_start = avail_w + 16 * S
                ly = cy - (n * (box_size + 8 * S)) // 2
                for i in range(n):
                    draw.rectangle(
                        [lx_start, ly + 2 * S, lx_start + box_size, ly + 2 * S + box_size],
                        fill=parsed_colors[i],
                    )
                    draw.text(
                        (lx_start + box_size + 6 * S, ly),
                        labels[i],
                        fill=COLOR_TEXT_MUTED,
                        font=legend_font,
                    )
                    ly += box_size + 8 * S
            else:  # bottom
                total_w = 0
                for lbl in labels:
                    bbox = draw.textbbox((0, 0), lbl, font=legend_font)
                    total_w += box_size + 6 * S + (bbox[2] - bbox[0]) + 20 * S
                total_w -= 20 * S
                lx_cur = (width * S - total_w) // 2
                ly = height * S - legend_bottom_space
                for i in range(n):
                    draw.rectangle(
                        [lx_cur, ly + 2 * S, lx_cur + box_size, ly + 2 * S + box_size],
                        fill=parsed_colors[i],
                    )
                    draw.text(
                        (lx_cur + box_size + 6 * S, ly),
                        labels[i],
                        fill=COLOR_TEXT_MUTED,
                        font=legend_font,
                    )
                    bbox = draw.textbbox((0, 0), labels[i], font=legend_font)
                    lx_cur += box_size + 6 * S + (bbox[2] - bbox[0]) + 20 * S

        return finalize_frame(img, width, height, sharpen=sharpen)

    return generate_frames(
        render, fps=fps, duration=duration, hold_seconds=hold_seconds, easing=easing
    )
