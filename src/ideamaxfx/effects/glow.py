"""Glow and glow-border effects."""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def glow(
    img: Image.Image,
    color: tuple[int, int, int] = (0, 245, 212),
    radius: int = 20,
    intensity: float = 0.5,
) -> Image.Image:
    """Apply a bloom-style glow tinted with *color*.

    Bright areas (luminance > 200) are extracted, tinted, blurred, and
    screen-blended back onto the original image.

    Args:
        img: Source image (any mode; converted to RGB internally).
        color: RGB tint colour for the glow.  Defaults to a cyan-green.
        radius: Gaussian blur radius for the glow spread.
        intensity: Blend strength for the glow layer (0.0 -- 1.0).

    Returns:
        RGB image with the glow applied.
    """
    img = img.convert("RGB")
    arr = np.array(img, dtype=np.float64)

    # Extract bright areas using luminance.
    gray = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    mask = (gray > 200).astype(np.float64)

    # Build a tinted glow layer.
    glow_layer = np.zeros_like(arr)
    for ch in range(3):
        glow_layer[:, :, ch] = mask * color[ch]

    glow_img = Image.fromarray(glow_layer.astype(np.uint8), mode="RGB")
    glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=radius))

    # Screen blend: result = 1 - (1 - base) * (1 - overlay)
    base = arr / 255.0
    overlay = np.array(glow_img, dtype=np.float64) / 255.0 * intensity
    blended = 1.0 - (1.0 - base) * (1.0 - overlay)

    result = np.clip(blended * 255.0, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(result, mode="RGB")


def glow_border(
    img: Image.Image,
    points: list[tuple[int, int]],
    color: tuple[int, int, int] = (0, 245, 212),
    passes: list[tuple[int, int]] | None = None,
) -> Image.Image:
    """Draw a multi-pass glowing outline along a polygon.

    Each pass draws the polygon outline at a different line width and
    alpha, then Gaussian-blurs the result.  Stacking several passes
    creates a convincing neon-glow effect around the shape.

    Args:
        img: Source image (any mode; converted to RGBA internally).
        points: Polygon vertices as ``(x, y)`` pairs.
        color: RGB colour of the glow outline.
        passes: List of ``(line_width, alpha)`` tuples.  Wider / more
            transparent passes form the outer haze while narrow / opaque
            passes form the bright core.  Defaults to five pre-tuned
            passes.

    Returns:
        RGBA image with the glowing border composited on top.
    """
    if passes is None:
        passes = [(12, 15), (8, 30), (5, 50), (3, 80), (2, 200)]

    img = img.convert("RGBA")
    w, h = img.size

    for line_width, alpha in passes:
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        draw.polygon(
            points,
            outline=(*color, alpha),
            width=line_width,
        )
        # Blur radius proportional to line width for natural falloff.
        blur_radius = max(1, line_width)
        layer = layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        img = Image.alpha_composite(img, layer)

    return img
