"""Progress bar layout component."""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter

from ideamaxfx.utils.fonts import load_font


def progress_bar(
    value: float,
    width: int = 300,
    height: int = 30,
    bg_color: tuple[int, int, int] = (40, 44, 52),
    fill_color: tuple[int, int, int] = (0, 245, 212),
    text_color: tuple[int, int, int] = (255, 255, 255),
    show_percent: bool = True,
    glow: bool = False,
    radius: int = 8,
    font_path: str | None = None,
) -> Image.Image:
    """Create a horizontal progress bar.

    Args:
        value: Progress value between 0.0 and 1.0.
        width: Bar width in pixels.
        height: Bar height in pixels.
        bg_color: Background color RGB.
        fill_color: Fill color RGB.
        text_color: Percentage text color RGB.
        show_percent: Whether to show percentage text.
        glow: Whether to add a glow effect to the bar.
        radius: Corner radius.
        font_path: Optional path to a .ttf font file.

    Returns:
        PIL Image of the progress bar.
    """
    value = max(0.0, min(1.0, value))
    pad = 10 if glow else 0
    canvas_w = width + pad * 2
    canvas_h = height + pad * 2

    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background bar
    draw.rounded_rectangle(
        [pad, pad, pad + width, pad + height],
        radius=radius,
        fill=bg_color,
    )

    # Filled portion
    fill_w = max(radius * 2, int(width * value))
    if value > 0:
        draw.rounded_rectangle(
            [pad, pad, pad + fill_w, pad + height],
            radius=radius,
            fill=fill_color,
        )

    # Glow effect
    if glow and value > 0:
        glow_layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)
        glow_draw.rounded_rectangle(
            [pad, pad, pad + fill_w, pad + height],
            radius=radius,
            fill=(*fill_color, 80),
        )
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=8))
        img = Image.alpha_composite(glow_layer, img)

    # Percentage text
    if show_percent:
        font = load_font(size=max(10, height - 10), path=font_path)
        pct_text = f"{int(value * 100)}%"
        draw2 = ImageDraw.Draw(img)
        bbox = draw2.textbbox((0, 0), pct_text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = pad + (width - text_w) // 2
        text_y = pad + (height - text_h) // 2 - 1
        draw2.text((text_x, text_y), pct_text, fill=text_color, font=font)

    return img
