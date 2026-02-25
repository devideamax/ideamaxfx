"""Pixelation composition effect."""

from __future__ import annotations

from PIL import Image


def pixelate(
    img: Image.Image,
    block_size: int = 10,
    region: tuple[int, int, int, int] | None = None,
) -> Image.Image:
    """Pixelate an image or a rectangular region of it.

    Down-scales and then up-scales with nearest-neighbour interpolation
    to produce the classic mosaic / pixelation look.

    Args:
        img: Source image (any mode).
        block_size: Side length of each pixel block.  Larger values
            produce coarser pixelation.  Clamped to at least 1.
        region: Optional ``(x1, y1, x2, y2)`` rectangle to pixelate.
            If *None* the entire image is pixelated.

    Returns:
        RGBA image with the pixelation applied.
    """
    img = img.convert("RGBA")
    block_size = max(1, block_size)

    if region is None:
        return _pixelate_region(img, (0, 0, img.width, img.height), block_size)

    # Clamp region to image bounds.
    x1 = max(0, region[0])
    y1 = max(0, region[1])
    x2 = min(img.width, region[2])
    y2 = min(img.height, region[3])

    if x2 <= x1 or y2 <= y1:
        return img.copy()

    result = img.copy()
    cropped = result.crop((x1, y1, x2, y2))
    pixelated = _pixelate_region(cropped, (0, 0, cropped.width, cropped.height), block_size)
    result.paste(pixelated, (x1, y1))
    return result


def _pixelate_region(
    img: Image.Image,
    box: tuple[int, int, int, int],
    block_size: int,
) -> Image.Image:
    """Pixelate a specific box within an image.

    Args:
        img: Source RGBA image.
        box: ``(x1, y1, x2, y2)`` rectangle (used only for width/height
            calculation; the image should already be cropped if needed).
        block_size: Pixel block side length.

    Returns:
        Pixelated RGBA image at the original dimensions.
    """
    x1, y1, x2, y2 = box
    rw = x2 - x1
    rh = y2 - y1

    small_w = max(1, rw // block_size)
    small_h = max(1, rh // block_size)

    small = img.resize((small_w, small_h), Image.NEAREST)
    return small.resize((rw, rh), Image.NEAREST)
