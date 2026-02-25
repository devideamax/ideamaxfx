"""Footer bar with logo, text, and line."""

from __future__ import annotations

from PIL import Image, ImageDraw

from ideamaxfx.utils.fonts import load_font


def footer_bar(
    img: Image.Image,
    text: str = "",
    logo: Image.Image | None = None,
    height: int = 40,
    bg_color: tuple[int, int, int] = (15, 15, 20),
    text_color: tuple[int, int, int] = (160, 160, 170),
    line_color: tuple[int, int, int] = (0, 245, 212),
    line_height: int = 2,
    font_size: int = 11,
    font_path: str | None = None,
) -> Image.Image:
    """Add a footer bar with optional logo, text, and accent line.

    Args:
        img: Source image.
        text: Footer text (e.g. source attribution).
        logo: Optional small logo image.
        height: Footer bar height.
        bg_color: Footer background color RGB.
        text_color: Footer text color RGB.
        line_color: Accent line color at top of footer.
        line_height: Accent line thickness.
        font_size: Footer text font size.
        font_path: Optional path to a .ttf font file.

    Returns:
        PIL Image with footer appended.
    """
    base = img.convert("RGB")
    w = base.width
    total_h = base.height + height

    result = Image.new("RGB", (w, total_h), bg_color)
    result.paste(base, (0, 0))

    draw = ImageDraw.Draw(result)

    # Accent line
    footer_top = base.height
    draw.rectangle([0, footer_top, w, footer_top + line_height], fill=line_color)

    content_y = footer_top + line_height
    pad = 12
    cx = pad

    # Logo
    if logo is not None:
        logo_rgba = logo.convert("RGBA")
        logo_h = height - line_height - 8
        logo_w = max(1, int(logo_rgba.width * logo_h / max(1, logo_rgba.height)))
        logo_resized = logo_rgba.resize((logo_w, logo_h), Image.LANCZOS)
        logo_y = content_y + (height - line_height - logo_h) // 2
        result.paste(logo_resized, (cx, logo_y), logo_resized)
        cx += logo_w + 8

    # Text
    if text:
        font = load_font(size=font_size, path=font_path)
        text_y = content_y + (height - line_height - font_size) // 2
        draw.text((cx, text_y), text, fill=text_color, font=font)

    return result
