"""Radial vignette darkening effect."""

from __future__ import annotations

import numpy as np
from PIL import Image


def vignette(
    img: Image.Image,
    strength: float = 0.3,
    radius: float = 1.0,
) -> Image.Image:
    """Darken the edges of an image with a radial vignette.

    A distance-from-centre map is computed and used to attenuate the
    image brightness towards the edges.  *radius* controls how far the
    bright centre extends, and *strength* controls the maximum
    darkening at the corners.

    Args:
        img: Source image (any mode; converted to RGB internally).
        strength: Maximum darkening factor at the corners (0.0 = none,
            1.0 = fully black corners).
        radius: Normalised radius of the bright centre region.  Values
            above 1.0 push the darkening further towards the edges.

    Returns:
        RGB image with vignette applied.
    """
    img = img.convert("RGB")
    arr = np.array(img, dtype=np.float64)
    h, w, _c = arr.shape

    # Normalised coordinate grids centred on the image.
    y = np.linspace(-1.0, 1.0, h)
    x = np.linspace(-1.0, 1.0, w)
    xv, yv = np.meshgrid(x, y)

    # Distance from centre, normalised so corners are ~sqrt(2).
    dist = np.sqrt(xv**2 + yv**2)

    # Map distance to a darkening factor.  Inside *radius* the factor
    # is 1.0 (no darkening); beyond it the brightness falls off smoothly.
    factor = 1.0 - strength * np.clip((dist - radius * 0.5) / (1.414 - radius * 0.5), 0.0, 1.0)
    factor = factor[:, :, np.newaxis]

    result = np.clip(arr * factor, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(result, mode="RGB")
