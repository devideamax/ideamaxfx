"""Animated bar chart grow."""

from __future__ import annotations

from typing import Callable

from PIL import Image, ImageDraw

from ideamaxfx.animate.core import generate_frames
from ideamaxfx.color.convert import hex_to_rgb
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
    font_path: str | None = None,
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
        font_path: Optional font path.

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

    # Default colors
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
    if colors is not None:
        for c in colors:
            if isinstance(c, str):
                parsed_colors.append(hex_to_rgb(c))
            else:
                parsed_colors.append(c)
    else:
        parsed_colors = [default_palette[i % len(default_palette)] for i in range(n)]

    margin_left = 80
    margin_right = 40
    margin_top = 60 if title else 30
    margin_bottom = 50
    chart_w = width - margin_left - margin_right
    chart_h = height - margin_top - margin_bottom
    bar_gap = 8
    bar_w = max(4, (chart_w - bar_gap * (n + 1)) // n)

    label_font = load_font(size=12, path=font_path)
    value_font = load_font(size=11, path=font_path)
    title_font = load_font(size=18, path=font_path)

    def render(progress: float) -> Image.Image:
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        # Title
        if title:
            bbox = draw.textbbox((0, 0), title, font=title_font)
            tw = bbox[2] - bbox[0]
            draw.text(((width - tw) // 2, 12), title, fill=text_color, font=title_font)

        # Baseline
        base_y = margin_top + chart_h
        draw.line(
            [(margin_left, base_y), (margin_left + chart_w, base_y)],
            fill=(60, 60, 70),
            width=1,
        )

        for i in range(n):
            x = margin_left + bar_gap + i * (bar_w + bar_gap)
            bar_h = int((values[i] / max_val) * chart_h * progress)
            y_top = base_y - bar_h

            if bar_h > 0:
                draw.rectangle([x, y_top, x + bar_w, base_y], fill=parsed_colors[i])

            # Label
            lbl = labels[i]
            lbbox = draw.textbbox((0, 0), lbl, font=label_font)
            lw = lbbox[2] - lbbox[0]
            draw.text(
                (x + (bar_w - lw) // 2, base_y + 6),
                lbl,
                fill=text_color,
                font=label_font,
            )

            # Value
            if progress > 0.1:
                val_text = f"{values[i] * progress:.0f}"
                vbbox = draw.textbbox((0, 0), val_text, font=value_font)
                vw = vbbox[2] - vbbox[0]
                draw.text(
                    (x + (bar_w - vw) // 2, y_top - 16),
                    val_text,
                    fill=text_color,
                    font=value_font,
                )

        return img

    return generate_frames(
        render, fps=fps, duration=duration, hold_seconds=hold_seconds, easing=easing
    )
