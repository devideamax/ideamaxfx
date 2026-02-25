"""Logo overlay watermark with alpha."""

from __future__ import annotations

from PIL import Image


def image_watermark(
    img: Image.Image,
    logo: Image.Image,
    position: str = "bottom-right",
    opacity: float = 0.5,
    margin: int = 20,
    scale: float = 1.0,
) -> Image.Image:
    """Overlay a logo watermark on an image.

    Args:
        img: Source image.
        logo: Logo image (RGBA recommended).
        position: Placement: "bottom-right", "bottom-left", "top-right",
            "top-left", "center".
        opacity: Logo opacity (0.0-1.0).
        margin: Pixel margin from edges.
        scale: Scale factor for the logo.

    Returns:
        Watermarked PIL Image.
    """
    base = img.convert("RGBA")
    mark = logo.convert("RGBA")

    # Scale logo
    if scale != 1.0:
        new_w = max(1, int(mark.width * scale))
        new_h = max(1, int(mark.height * scale))
        mark = mark.resize((new_w, new_h), Image.LANCZOS)

    # Apply opacity
    if opacity < 1.0:
        r, g, b, a = mark.split()
        a = a.point(lambda p: int(p * opacity))
        mark = Image.merge("RGBA", (r, g, b, a))

    # Calculate position
    bw, bh = base.size
    mw, mh = mark.size

    positions = {
        "bottom-right": (bw - mw - margin, bh - mh - margin),
        "bottom-left": (margin, bh - mh - margin),
        "top-right": (bw - mw - margin, margin),
        "top-left": (margin, margin),
        "center": ((bw - mw) // 2, (bh - mh) // 2),
    }
    x, y = positions.get(position, positions["bottom-right"])

    base.paste(mark, (x, y), mark)
    return base.convert("RGB")
