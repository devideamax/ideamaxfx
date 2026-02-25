"""Drop-shadow composition effect."""

from __future__ import annotations

from PIL import Image, ImageFilter


def drop_shadow(
    img: Image.Image,
    offset: tuple[int, int] = (10, 10),
    blur_radius: int = 15,
    shadow_color: tuple[int, int, int] = (0, 0, 0),
    opacity: int = 128,
) -> Image.Image:
    """Add a drop shadow behind an image.

    Creates a canvas large enough to hold the original image plus the
    shadow offset and blur margin, draws the shadow, blurs it, and
    composites the original on top.

    Args:
        img: Source image (any mode).
        offset: ``(x, y)`` pixel offset of the shadow relative to the
            image.  Positive values move the shadow right/down.
        blur_radius: Gaussian blur radius applied to the shadow.
        shadow_color: RGB colour of the shadow.
        opacity: Shadow alpha value (0-255).

    Returns:
        RGBA image with the drop shadow applied.
    """
    img = img.convert("RGBA")
    w, h = img.size

    # Extra padding so the blurred shadow never clips.
    margin = blur_radius * 2
    canvas_w = w + abs(offset[0]) + margin * 2
    canvas_h = h + abs(offset[1]) + margin * 2

    # Position of the original image on the canvas (always fully visible).
    img_x = margin + max(-offset[0], 0)
    img_y = margin + max(-offset[1], 0)

    # Position of the shadow on the canvas.
    shadow_x = img_x + offset[0]
    shadow_y = img_y + offset[1]

    # Build the shadow layer.
    shadow = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    shadow_shape = Image.new(
        "RGBA",
        (w, h),
        (*shadow_color, opacity),
    )

    # Use the source alpha as the shadow shape so transparent areas stay
    # transparent in the shadow as well.
    shadow.paste(shadow_shape, (shadow_x, shadow_y), img.split()[3])

    # Blur the shadow.
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    # Composite the original on top.
    shadow.paste(img, (img_x, img_y), img)
    return shadow
