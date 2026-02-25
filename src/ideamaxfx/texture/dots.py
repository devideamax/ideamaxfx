"""Regular polka-dot pattern generator."""

from __future__ import annotations

from PIL import Image, ImageDraw


def dot_pattern(
    width: int = 512,
    height: int = 512,
    spacing: int = 20,
    radius: int = 3,
    color: tuple[int, int, int] = (255, 255, 255),
    bg_color: tuple[int, int, int] = (0, 0, 0),
) -> Image.Image:
    """Generate a regular polka-dot grid image.

    Dots are placed on a rectangular grid with the given *spacing*.
    Each dot is a filled circle drawn with ``ImageDraw.ellipse``.

    Args:
        width: Output image width in pixels.
        height: Output image height in pixels.
        spacing: Distance in pixels between dot centres (both axes).
        radius: Radius of each dot in pixels.
        color: RGB colour of the dots.
        bg_color: RGB background colour.

    Returns:
        RGB PIL Image of size (width, height).
    """
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    x = 0
    while x < width:
        y = 0
        while y < height:
            draw.ellipse(
                [x - radius, y - radius, x + radius, y + radius],
                fill=color,
            )
            y += spacing
        x += spacing

    return img
