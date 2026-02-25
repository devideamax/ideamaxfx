"""Animated bar chart grow."""

from __future__ import annotations

from typing import Callable

from PIL import Image, ImageDraw

from ideamaxfx.animate.chart_utils import (
    _SS,
    COLOR_AXIS,
    COLOR_TEXT_MUTED,
    FONT_AXIS,
    FONT_DATA,
    compute_margins,
    compute_nice_ticks,
    draw_gridlines,
    draw_title,
    draw_y_axis,
    finalize_frame,
    format_number,
    parse_colors,
)
from ideamaxfx.animate.core import generate_frames
from ideamaxfx.utils.fonts import load_font


def bar_grow(
    labels: list[str],
    values: list[float],
    colors: list[str] | list[tuple[int, int, int]] | None = None,
    width: int = 800,
    height: int = 500,
    bg_color: tuple[int, int, int] = (13, 17, 23),
    text_color: tuple[int, int, int] = (220, 220, 230),
    fps: int = 15,
    duration: float = 2.0,
    hold_seconds: float = 2.0,
    easing: str | Callable[[float], float] = "ease_out_cubic",
    title: str = "",
    subtitle: str = "",
    font_path: str | None = None,
    show_gridlines: bool = True,
    show_values: bool = True,
    value_format: str = "auto",
    sharpen: bool = True,
) -> list[Image.Image]:
    """Generate animated bar chart frames where bars grow from zero.

    Args:
        labels: Bar labels.
        values: Bar values.
        colors: Hex strings or RGB tuples per bar. Auto-generated if None.
        width: Image width.
        height: Image height.
        bg_color: Background color.
        text_color: Label/value text color.
        fps: Frames per second.
        duration: Animation duration in seconds.
        hold_seconds: Hold final frame duration.
        easing: Easing function name or callable.
        title: Optional chart title.
        subtitle: Optional subtitle below title.
        font_path: Optional font path.
        show_gridlines: Draw horizontal gridlines.
        show_values: Show value labels above bars.
        value_format: "auto", "raw", "K", "M", or "comma".
        sharpen: Apply UnsharpMask after downscale.

    Returns:
        List of PIL Image frames.
    """
    if len(labels) != len(values):
        raise ValueError(
            f"labels ({len(labels)}) and values ({len(values)}) must have same length"
        )

    n = len(labels)
    max_val = max(values) if values else 1.0
    if max_val == 0:
        max_val = 1.0

    parsed_colors = parse_colors(colors, n)

    S = _SS

    # Compute nice ticks for Y-axis
    ticks = compute_nice_ticks(0, max_val)
    tick_max = ticks[-1] if ticks else max_val

    # Format function based on value_format
    def _fmt(v: float) -> str:
        if value_format == "comma":
            from ideamaxfx.animate.chart_utils import format_number_commas

            return format_number_commas(v)
        return format_number(v)

    # Compute dynamic margins
    tmp_img = Image.new("RGB", (width * S, height * S))
    tmp_draw = ImageDraw.Draw(tmp_img)
    y_labels_str = [_fmt(t) for t in ticks]
    margins = compute_margins(
        tmp_draw, y_labels_str, labels, title, subtitle, False, S, font_path
    )

    margin_left = margins["left"]
    margin_right = margins["right"]
    margin_top = margins["top"]
    margin_bottom = margins["bottom"]
    chart_w = width * S - margin_left - margin_right
    chart_h = height * S - margin_top - margin_bottom

    # Bar proportions: gap = 40% of slot width
    slot_w = chart_w // max(1, n)
    bar_gap = int(slot_w * 0.2)
    bar_w = slot_w - 2 * bar_gap

    label_font = load_font(size=FONT_AXIS * S, path=font_path)
    value_font = load_font(size=FONT_DATA * S, path=font_path)

    chart_area = {
        "left": margin_left,
        "top": margin_top,
        "bottom": margin_top + chart_h,
        "right_x": margin_left + chart_w,
    }

    def render(progress: float) -> Image.Image:
        img = Image.new("RGB", (width * S, height * S), bg_color)
        draw = ImageDraw.Draw(img)

        # Title
        draw_title(draw, title, subtitle, width * S, 8 * S, S, font_path)

        base_y = margin_top + chart_h

        # Gridlines (behind bars)
        if show_gridlines:
            draw_gridlines(draw, ticks, chart_area, 0, tick_max, S)

        # Y-axis
        draw_y_axis(draw, ticks, chart_area, 0, tick_max, S, font_path, _fmt)

        # X-axis baseline
        draw.line(
            [(margin_left, base_y), (margin_left + chart_w, base_y)],
            fill=COLOR_AXIS,
            width=max(1, S),
        )

        for i in range(n):
            x = margin_left + i * slot_w + bar_gap
            bar_h = int((values[i] / tick_max) * chart_h * progress)
            y_top = base_y - bar_h

            if bar_h > 0:
                draw.rectangle([x, y_top, x + bar_w, base_y], fill=parsed_colors[i])

            # Label
            lbl = labels[i]
            lbbox = draw.textbbox((0, 0), lbl, font=label_font)
            lw = lbbox[2] - lbbox[0]
            draw.text(
                (x + (bar_w - lw) // 2, base_y + 6 * S),
                lbl,
                fill=COLOR_TEXT_MUTED,
                font=label_font,
            )

            # Value above bar
            if show_values and progress > 0.1:
                val_text = _fmt(values[i] * progress)
                vbbox = draw.textbbox((0, 0), val_text, font=value_font)
                vw = vbbox[2] - vbbox[0]
                draw.text(
                    (x + (bar_w - vw) // 2, y_top - 14 * S),
                    val_text,
                    fill=text_color,
                    font=value_font,
                )

        return finalize_frame(img, width, height, sharpen=sharpen)

    return generate_frames(
        render, fps=fps, duration=duration, hold_seconds=hold_seconds, easing=easing
    )
