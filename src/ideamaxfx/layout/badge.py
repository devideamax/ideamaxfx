"""Pill-shaped badge component."""

from __future__ import annotations

from PIL import Image, ImageDraw

from ideamaxfx.utils.fonts import load_font


def badge(
    text: str,
    bg_color: tuple[int, int, int] = (0, 245, 212),
    text_color: tuple[int, int, int] = (0, 0, 0),
    font_size: int = 14,
    padding_x: int = 16,
    padding_y: int = 6,
    font_path: str | None = None,
) -> Image.Image:
    """Create a pill-shaped colored badge.

    Args:
        text: Badge label text.
        bg_color: Background color RGB.
        text_color: Text color RGB.
        font_size: Font size in pixels.
        padding_x: Horizontal padding.
        padding_y: Vertical padding.
        font_path: Optional path to a .ttf font file.

    Returns:
        RGBA PIL Image of the badge.
    """
    font = load_font(size=font_size, path=font_path)

    # Measure text
    tmp = Image.new("RGB", (1, 1))
    tmp_draw = ImageDraw.Draw(tmp)
    bbox = tmp_draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    w = text_w + padding_x * 2
    h = text_h + padding_y * 2
    radius = h // 2

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=bg_color)

    text_x = (w - text_w) // 2
    text_y = (h - text_h) // 2 - 1
    draw.text((text_x, text_y), text, fill=text_color, font=font)

    return img
