"""Tilt-shift (miniature-effect) composition."""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter


def tilt_shift(
    img: Image.Image,
    focus_y: float = 0.5,
    focus_height: float = 0.2,
    blur_amount: int = 8,
) -> Image.Image:
    """Simulate a tilt-shift lens effect.

    Keeps a horizontal strip of the image in focus while progressively
    blurring the regions above and below it.  A smooth gradient mask is
    used so the transition looks natural.

    Args:
        img: Source image (any mode).
        focus_y: Vertical centre of the in-focus strip as a fraction of
            image height (0.0 = top, 1.0 = bottom).
        focus_height: Height of the fully sharp strip as a fraction of
            image height.
        blur_amount: Gaussian blur radius applied to out-of-focus areas.

    Returns:
        RGBA image with the tilt-shift effect applied.
    """
    img = img.convert("RGBA")
    w, h = img.size

    # Create the blurred version.
    blurred = img.filter(ImageFilter.GaussianBlur(radius=blur_amount))

    # Build a gradient mask where white = sharp, black = blurred.
    # The sharp region is centred at focus_y with total height
    # focus_height (as fractions of image height).
    centre_px = int(h * focus_y)
    half_band = int(h * focus_height / 2)
    top_edge = max(centre_px - half_band, 0)
    bot_edge = min(centre_px + half_band, h)

    # Create per-row alpha array: 255 inside the band, linear ramp
    # outside.  Fully vectorised with numpy.
    rows = np.arange(h, dtype=np.float64)

    mask_arr = np.full(h, 255.0, dtype=np.float64)

    # Above the focus band: ramp from 0 at y=0 up to 255 at top_edge.
    above = rows < top_edge
    if top_edge > 0:
        mask_arr[above] = 255.0 * rows[above] / top_edge

    # Below the focus band: ramp from 255 at bot_edge down to 0 at y=h.
    below = rows > bot_edge
    remaining = h - bot_edge
    if remaining > 0:
        mask_arr[below] = 255.0 * (1.0 - (rows[below] - bot_edge) / remaining)

    mask_arr = np.clip(mask_arr, 0, 255).astype(np.uint8)

    # Expand to full image dimensions (same value across each row).
    mask_2d = np.tile(mask_arr[:, np.newaxis], (1, w))
    mask_img = Image.fromarray(mask_2d, mode="L")

    # Composite: sharp where mask is white, blurred where black.
    result = Image.composite(img, blurred, mask_img)
    return result.convert("RGBA")
