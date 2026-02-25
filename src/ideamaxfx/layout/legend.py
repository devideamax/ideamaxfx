"""Color legend block component."""

from __future__ import annotations

from PIL import Image, ImageDraw

from ideamaxfx.utils.fonts import load_font


def legend_block(
    items: list[tuple[str, tuple[int, int, int]]],
    orientation: str = "vertical",
    dot_size: int = 10,
    spacing: int = 8,
    text_color: tuple[int, int, int] = (255, 255, 255),
    bg_color: tuple[int, int, int, int] = (0, 0, 0, 0),
    font_size: int = 13,
    font_path: str | None = None,
) -> Image.Image:
    """Create a color-dot + text legend block.

    Args:
        items: List of (label, color_rgb) tuples.
        orientation: "vertical" or "horizontal".
        dot_size: Diameter of color dots.
        spacing: Space between items.
        text_color: Label text color.
        bg_color: Background color RGBA.
        font_size: Label font size.
        font_path: Optional path to a .ttf font file.

    Returns:
        RGBA PIL Image of the legend.
    """
    font = load_font(size=font_size, path=font_path)

    # Measure all items
    tmp = Image.new("RGB", (1, 1))
    tmp_draw = ImageDraw.Draw(tmp)
    item_sizes = []
    for label, _ in items:
        bbox = tmp_draw.textbbox((0, 0), label, font=font)
        item_sizes.append((bbox[2] - bbox[0], bbox[3] - bbox[1]))

    item_w = dot_size + 6  # dot + gap
    row_h = max(dot_size, max(h for _, h in item_sizes)) + 4

    if orientation == "vertical":
        total_w = item_w + max(w for w, _ in item_sizes) + 12
        total_h = len(items) * (row_h + spacing) - spacing + 8
    else:
        total_w = sum(item_w + w + spacing + 12 for w, _ in item_sizes) - spacing
        total_h = row_h + 8

    img = Image.new("RGBA", (total_w, total_h), bg_color)
    draw = ImageDraw.Draw(img)

    cx, cy = 4, 4
    for i, (label, color) in enumerate(items):
        dot_y = cy + (row_h - dot_size) // 2
        draw.ellipse(
            [cx, dot_y, cx + dot_size, dot_y + dot_size],
            fill=color,
        )
        text_x = cx + dot_size + 6
        text_y = cy + (row_h - item_sizes[i][1]) // 2
        draw.text((text_x, text_y), label, fill=text_color, font=font)

        if orientation == "vertical":
            cy += row_h + spacing
        else:
            cx += dot_size + 6 + item_sizes[i][0] + spacing + 12

    return img
