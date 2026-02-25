"""Chromatic aberration (colour fringing) effect."""

from __future__ import annotations

import numpy as np
from PIL import Image


def chromatic_aberration(
    img: Image.Image,
    offset: int = 5,
    direction: str = "horizontal",
) -> Image.Image:
    """Simulate chromatic aberration by shifting colour channels.

    The red channel is shifted in one direction and the blue channel in
    the opposite direction by *offset* pixels, while the green channel
    stays centred.  This mimics the colour fringing caused by imperfect
    lens optics.

    Args:
        img: Source image (any mode; converted to RGB internally).
        offset: Shift distance in pixels for the red and blue channels.
        direction: ``"horizontal"`` shifts channels left/right;
            ``"vertical"`` shifts them up/down.

    Returns:
        RGB image with chromatic aberration applied.
    """
    img = img.convert("RGB")
    arr = np.array(img)
    h, w, _c = arr.shape

    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]

    if offset == 0:
        return img

    # For negative offset, swap shift direction by flipping which channel
    # shifts which way: use abs(offset) and swap r/b when negative.
    abs_off = abs(offset)
    if offset < 0:
        r, b = b, r

    if direction == "horizontal":
        # Shift red left, blue right.
        r_shifted = np.zeros_like(r)
        b_shifted = np.zeros_like(b)

        r_shifted[:, : w - abs_off] = r[:, abs_off:]
        r_shifted[:, w - abs_off :] = r[:, -1:]

        b_shifted[:, abs_off:] = b[:, : w - abs_off]
        b_shifted[:, :abs_off] = b[:, :1]
    elif direction == "vertical":
        # Shift red up, blue down.
        r_shifted = np.zeros_like(r)
        b_shifted = np.zeros_like(b)

        r_shifted[: h - abs_off, :] = r[abs_off:, :]
        r_shifted[h - abs_off :, :] = r[-1:, :]

        b_shifted[abs_off:, :] = b[: h - abs_off, :]
        b_shifted[:abs_off, :] = b[:1, :]
    else:
        raise ValueError(f"direction must be 'horizontal' or 'vertical', got {direction!r}")

    result = np.stack([r_shifted, g, b_shifted], axis=2)
    return Image.fromarray(result, mode="RGB")
