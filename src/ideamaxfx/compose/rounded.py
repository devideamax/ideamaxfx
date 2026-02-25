"""Rounded corners composition effect."""

from __future__ import annotations

from PIL import Image, ImageDraw


def rounded_corners(
    img: Image.Image,
    radius: int = 20,
    bg_color: tuple[int, int, int, int] = (0, 0, 0, 0),
) -> Image.Image:
    """Apply rounded corners to an image using an alpha mask.

    Draws a rounded-rectangle mask at the image dimensions and composites
    the original onto a background filled with *bg_color*.

    Args:
        img: Source image (any mode).
        radius: Corner radius in pixels.  Clamped to half the shortest
            side so the mask always fits.
        bg_color: Background RGBA colour visible where corners are cut.

    Returns:
        RGBA image with rounded corners applied.
    """
    img = img.convert("RGBA")
    w, h = img.size

    # Clamp radius so it never exceeds half the shortest side.
    radius = min(radius, w // 2, h // 2)

    # Build a grayscale mask with a rounded rectangle.
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (w - 1, h - 1)], radius=radius, fill=255)

    # Create background, paste source through the mask.
    result = Image.new("RGBA", (w, h), bg_color)
    result.paste(img, (0, 0), mask)
    return result
