"""Arrow + text annotation callout component."""

from __future__ import annotations

import math

from PIL import Image, ImageDraw

from ideamaxfx.utils.fonts import load_font


def callout(
    text: str,
    anchor: tuple[int, int] = (0, 0),
    direction: str = "right",
    arrow_length: int = 40,
    text_color: tuple[int, int, int] = (255, 255, 255),
    line_color: tuple[int, int, int] = (0, 245, 212),
    bg_color: tuple[int, int, int, int] = (0, 0, 0, 0),
    font_size: int = 13,
    line_width: int = 2,
    canvas_size: tuple[int, int] = (400, 100),
    font_path: str | None = None,
) -> Image.Image:
    """Create an arrow + text annotation callout.

    Args:
        text: Annotation text.
        anchor: Point (x, y) where arrow starts on the canvas.
        direction: Arrow direction: "left", "right", "up", "down".
        arrow_length: Length of the arrow line.
        text_color: Text color RGB.
        line_color: Arrow/line color RGB.
        bg_color: Canvas background color RGBA.
        font_size: Text font size.
        line_width: Arrow line width.
        canvas_size: Total canvas (width, height).
        font_path: Optional path to a .ttf font file.

    Returns:
        RGBA PIL Image of the callout.
    """
    img = Image.new("RGBA", canvas_size, bg_color)
    draw = ImageDraw.Draw(img)
    font = load_font(size=font_size, path=font_path)

    ax, ay = anchor
    dx_map = {"right": 1, "left": -1, "up": 0, "down": 0}
    dy_map = {"right": 0, "left": 0, "up": -1, "down": 1}
    dx = dx_map.get(direction, 1)
    dy = dy_map.get(direction, 0)

    end_x = ax + dx * arrow_length
    end_y = ay + dy * arrow_length

    # Draw arrow line
    draw.line([(ax, ay), (end_x, end_y)], fill=line_color, width=line_width)

    # Draw arrowhead
    angle = math.atan2(dy, dx)
    head_len = 8
    for sign in (-1, 1):
        hx = end_x - head_len * math.cos(angle + sign * 0.4)
        hy = end_y - head_len * math.sin(angle + sign * 0.4)
        draw.line([(end_x, end_y), (int(hx), int(hy))], fill=line_color, width=line_width)

    # Draw dot at anchor
    dot_r = 3
    draw.ellipse(
        [ax - dot_r, ay - dot_r, ax + dot_r, ay + dot_r],
        fill=line_color,
    )

    # Draw text near end of arrow
    text_pad = 6
    if direction == "right":
        tx, ty = end_x + text_pad, end_y - font_size // 2
    elif direction == "left":
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        tx, ty = end_x - text_pad - tw, end_y - font_size // 2
    elif direction == "up":
        tx, ty = end_x + text_pad, end_y - font_size - 2
    else:
        tx, ty = end_x + text_pad, end_y + 4

    draw.text((tx, ty), text, fill=text_color, font=font)

    return img
