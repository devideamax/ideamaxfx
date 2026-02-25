"""Gradient-fade divider line component."""

from __future__ import annotations

import numpy as np
from PIL import Image


def divider(
    width: int = 600,
    height: int = 3,
    color: tuple[int, int, int] = (0, 245, 212),
    style: str = "fade",
    bg_color: tuple[int, int, int, int] = (0, 0, 0, 0),
) -> Image.Image:
    """Create a gradient-fade divider line.

    Args:
        width: Divider width in pixels.
        height: Divider height/thickness in pixels.
        color: Line color RGB.
        style: "fade" (center bright, edges fade), "solid", or "dashed".
        bg_color: Background color RGBA.

    Returns:
        RGBA PIL Image of the divider.
    """
    img = Image.new("RGBA", (width, height), bg_color)

    if style == "solid":
        arr = np.zeros((height, width, 4), dtype=np.uint8)
        arr[:, :, 0] = color[0]
        arr[:, :, 1] = color[1]
        arr[:, :, 2] = color[2]
        arr[:, :, 3] = 255
        img = Image.fromarray(arr, mode="RGBA")

    elif style == "dashed":
        arr = np.zeros((height, width, 4), dtype=np.uint8)
        dash_len = 12
        gap_len = 6
        pattern_len = dash_len + gap_len
        for x in range(width):
            if (x % pattern_len) < dash_len:
                arr[:, x, 0] = color[0]
                arr[:, x, 1] = color[1]
                arr[:, x, 2] = color[2]
                arr[:, x, 3] = 255
        img = Image.fromarray(arr, mode="RGBA")

    else:  # fade
        arr = np.zeros((height, width, 4), dtype=np.uint8)
        center = width / 2
        for x in range(width):
            dist = abs(x - center) / center
            alpha = int(255 * (1.0 - dist * dist))
            arr[:, x, 0] = color[0]
            arr[:, x, 1] = color[1]
            arr[:, x, 2] = color[2]
            arr[:, x, 3] = alpha
        img = Image.fromarray(arr, mode="RGBA")

    return img
