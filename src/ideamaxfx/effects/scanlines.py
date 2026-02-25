"""CRT scanline overlay effect."""

from __future__ import annotations

import numpy as np
from PIL import Image


def scanlines(
    img: Image.Image,
    spacing: int = 4,
    opacity: float = 0.3,
    color: tuple[int, int, int] = (0, 0, 0),
) -> Image.Image:
    """Overlay horizontal scanlines onto an image.

    Thin horizontal bars of *color* are drawn at regular intervals,
    simulating a CRT monitor.  Uses direct numpy array manipulation
    for speed.

    Args:
        img: Source image (any mode; converted to RGB internally).
        spacing: Vertical distance in pixels between scanlines.
            Every *spacing*-th row is darkened.
        opacity: Blending strength of the scanline colour (0.0 = invisible,
            1.0 = fully opaque).
        color: RGB colour of the scanline bars.

    Returns:
        RGB image with scanlines composited on top.
    """
    if spacing < 1:
        raise ValueError(f"spacing must be >= 1, got {spacing}")

    img = img.convert("RGB")
    arr = np.array(img, dtype=np.float64)
    h, _w, _c = arr.shape

    line_color = np.array(color, dtype=np.float64)

    # Build row indices that receive the scanline.
    rows = np.arange(0, h, spacing)

    # Blend scanline colour into every selected row.
    arr[rows] = arr[rows] * (1.0 - opacity) + line_color * opacity

    result = np.clip(arr, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(result, mode="RGB")
