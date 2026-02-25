"""Stripe pattern generator with horizontal, vertical, and diagonal support."""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw


def stripe_pattern(
    width: int = 512,
    height: int = 512,
    spacing: int = 10,
    thickness: int = 2,
    color: tuple[int, int, int] = (255, 255, 255),
    bg_color: tuple[int, int, int] = (0, 0, 0),
    direction: str = "diagonal",
) -> Image.Image:
    """Generate a repeating stripe pattern image.

    Horizontal and vertical stripes are drawn with PIL for crisp
    pixel-aligned results.  Diagonal (45 degree) stripes use a numpy
    modular-arithmetic approach for smooth rendering.

    Args:
        width: Output image width in pixels.
        height: Output image height in pixels.
        spacing: Distance in pixels between stripe centres.
        thickness: Width of each stripe in pixels.
        color: RGB colour of the stripes.
        bg_color: RGB background colour.
        direction: One of ``"horizontal"``, ``"vertical"``, or
            ``"diagonal"`` (45 degrees).

    Returns:
        RGB PIL Image of size (width, height).

    Raises:
        ValueError: If *direction* is not one of the accepted values.
    """
    valid_directions = ("horizontal", "vertical", "diagonal")
    if direction not in valid_directions:
        raise ValueError(f"Unknown direction {direction!r}. Choose from {valid_directions}.")

    if direction == "diagonal":
        return _diagonal_stripes(width, height, spacing, thickness, color, bg_color)

    return _straight_stripes(width, height, spacing, thickness, color, bg_color, direction)


def _straight_stripes(
    width: int,
    height: int,
    spacing: int,
    thickness: int,
    color: tuple[int, int, int],
    bg_color: tuple[int, int, int],
    direction: str,
) -> Image.Image:
    """Draw horizontal or vertical stripes using PIL.

    Args:
        width: Canvas width.
        height: Canvas height.
        spacing: Distance between stripe centres.
        thickness: Stripe width in pixels.
        color: RGB stripe colour.
        bg_color: RGB background colour.
        direction: ``"horizontal"`` or ``"vertical"``.

    Returns:
        RGB PIL Image.
    """
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    half = thickness // 2

    if direction == "horizontal":
        y = 0
        while y < height:
            y0 = max(0, y - half)
            y1 = min(height - 1, y - half + thickness - 1)
            draw.rectangle([(0, y0), (width - 1, y1)], fill=color)
            y += spacing
    else:  # vertical
        x = 0
        while x < width:
            x0 = max(0, x - half)
            x1 = min(width - 1, x - half + thickness - 1)
            draw.rectangle([(x0, 0), (x1, height - 1)], fill=color)
            x += spacing

    return img


def _diagonal_stripes(
    width: int,
    height: int,
    spacing: int,
    thickness: int,
    color: tuple[int, int, int],
    bg_color: tuple[int, int, int],
) -> Image.Image:
    """Draw 45-degree diagonal stripes using numpy modular arithmetic.

    For each pixel the value ``(x + y) mod spacing`` determines whether
    the pixel falls inside a stripe band.

    Args:
        width: Canvas width.
        height: Canvas height.
        spacing: Repeat period along the diagonal.
        thickness: Stripe width within each period.
        color: RGB stripe colour.
        bg_color: RGB background colour.

    Returns:
        RGB PIL Image.
    """
    xs = np.arange(width, dtype=np.int32)
    ys = np.arange(height, dtype=np.int32)
    # x_grid shape: (height, width)
    x_grid, y_grid = np.meshgrid(xs, ys)

    # Ensure spacing is at least 1 to avoid division by zero
    period = max(1, spacing)

    # Distance along the diagonal, modulo the period
    diag = (x_grid + y_grid) % period

    # Stripe mask: pixels within half-thickness of position 0 in the period
    mask = diag < thickness

    # Build RGB image from mask
    bg = np.array(bg_color, dtype=np.uint8)
    fg = np.array(color, dtype=np.uint8)

    pixels = np.where(mask[..., np.newaxis], fg, bg).astype(np.uint8)
    return Image.fromarray(pixels, mode="RGB")
