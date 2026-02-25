"""Glassmorphism card effect."""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter


def glass_card(
    img: Image.Image,
    x: int,
    y: int,
    w: int,
    h: int,
    blur: int = 15,
    tint: tuple[int, int, int, int] = (20, 25, 40, 160),
    radius: int = 12,
) -> Image.Image:
    """Apply a glassmorphism card to a rectangular region.

    The region at ``(x, y, w, h)`` is cropped, blurred, tinted, given
    a subtle bright border highlight, and pasted back to produce the
    characteristic frosted-glass look.

    Args:
        img: Source image (any mode; converted to RGBA internally).
        x: Left edge of the glass card in pixels.
        y: Top edge of the glass card in pixels.
        w: Width of the glass card in pixels.
        h: Height of the glass card in pixels.
        blur: Gaussian blur radius for the frosted effect.
        tint: RGBA colour overlaid on the blurred region.
        radius: Corner rounding radius for the card shape.

    Returns:
        RGBA image with the glass card composited in place.
    """
    img = img.convert("RGBA")
    iw, ih = img.size

    # Clamp region to image bounds.
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(iw, x + w)
    y2 = min(ih, y + h)
    cw = x2 - x1
    ch = y2 - y1
    if cw <= 0 or ch <= 0:
        return img

    # --- Frosted background ---
    region = img.crop((x1, y1, x2, y2))
    region = region.filter(ImageFilter.GaussianBlur(radius=blur))

    # --- Rounded-rectangle mask ---
    mask = Image.new("L", (cw, ch), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        [0, 0, cw - 1, ch - 1],
        radius=radius,
        fill=255,
    )

    # --- Tint overlay ---
    tint_layer = Image.new("RGBA", (cw, ch), tint)
    region = Image.alpha_composite(region.convert("RGBA"), tint_layer)

    # --- Border highlight ---
    border_layer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(border_layer)
    # Top and left edges get a bright line, bottom and right get a dim one,
    # giving a subtle light-source effect.
    border_draw.rounded_rectangle(
        [0, 0, cw - 1, ch - 1],
        radius=radius,
        outline=(255, 255, 255, 60),
        width=1,
    )
    region = Image.alpha_composite(region, border_layer)

    # --- Composite back using rounded mask ---
    result = img.copy()
    result.paste(region, (x1, y1), mask)

    return result
