"""Halftone dot-screen effect."""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw


def halftone(
    img: Image.Image,
    dot_size: int = 6,
    spacing: int = 8,
    angle: float = 45.0,
) -> Image.Image:
    """Convert an image to a halftone dot pattern.

    The image is first converted to grayscale.  A rotated grid is laid
    over the image, and at each grid point a filled circle is drawn
    whose radius is proportional to the darkness of the underlying pixel.

    Args:
        img: Source image (any mode; converted to grayscale internally).
        dot_size: Maximum circle radius in pixels.
        spacing: Distance between grid sample points in pixels.
        angle: Rotation angle of the dot grid in degrees.

    Returns:
        Grayscale (mode ``L``) image with the halftone pattern.
    """
    if spacing < 1:
        raise ValueError(f"spacing must be >= 1, got {spacing}")

    gray = img.convert("L")
    arr = np.array(gray, dtype=np.float64)
    h, w = arr.shape

    canvas = Image.new("L", (w, h), 255)
    draw = ImageDraw.Draw(canvas)

    angle_rad = math.radians(angle)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    # Compute bounding range for rotated grid so every pixel is covered.
    diagonal = int(math.hypot(w, h))
    start = -diagonal
    end = diagonal

    for gy in range(start, end, spacing):
        for gx in range(start, end, spacing):
            # Rotate grid coordinates back to image space.
            px = int(gx * cos_a - gy * sin_a + w / 2)
            py = int(gx * sin_a + gy * cos_a + h / 2)

            if 0 <= px < w and 0 <= py < h:
                darkness = 1.0 - arr[py, px] / 255.0
                radius = max(1, int(darkness * dot_size))
                draw.ellipse(
                    [px - radius, py - radius, px + radius, py + radius],
                    fill=0,
                )

    return canvas
