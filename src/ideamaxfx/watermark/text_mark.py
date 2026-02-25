"""Semi-transparent diagonal text watermark."""

from __future__ import annotations

import math

from PIL import Image, ImageDraw

from ideamaxfx.utils.fonts import load_font


def text_watermark(
    img: Image.Image,
    text: str = "DRAFT",
    opacity: int = 40,
    font_size: int = 60,
    color: tuple[int, int, int] = (255, 255, 255),
    angle: float = -30.0,
    spacing: int = 200,
    font_path: str | None = None,
) -> Image.Image:
    """Apply a repeating semi-transparent diagonal text watermark.

    Args:
        img: Source image.
        text: Watermark text.
        opacity: Text opacity (0-255).
        font_size: Font size in pixels.
        color: Text color RGB.
        angle: Rotation angle in degrees.
        spacing: Spacing between repeated text instances.
        font_path: Optional path to a .ttf font file.

    Returns:
        Watermarked PIL Image.
    """
    base = img.convert("RGBA")
    w, h = base.size

    # Create a larger canvas for rotated text tiling
    diag = int(math.sqrt(w * w + h * h))
    txt_layer = Image.new("RGBA", (diag * 2, diag * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_layer)
    font = load_font(size=font_size, path=font_path)

    # Tile text across the canvas
    for y_pos in range(0, diag * 2, spacing):
        for x_pos in range(0, diag * 2, spacing):
            draw.text((x_pos, y_pos), text, fill=(*color, opacity), font=font)

    # Rotate and crop to original size
    txt_layer = txt_layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    cx = (txt_layer.width - w) // 2
    cy = (txt_layer.height - h) // 2
    txt_layer = txt_layer.crop((cx, cy, cx + w, cy + h))

    result = Image.alpha_composite(base, txt_layer)
    return result.convert("RGB")
