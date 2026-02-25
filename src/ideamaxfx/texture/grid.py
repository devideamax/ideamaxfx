"""Grid pattern generator with multiple style options."""

from __future__ import annotations

from PIL import Image, ImageDraw


def grid_pattern(
    width: int = 512,
    height: int = 512,
    spacing: int = 20,
    line_width: int = 1,
    color: tuple[int, int, int] = (100, 100, 100),
    bg_color: tuple[int, int, int] = (0, 0, 0),
    style: str = "lines",
) -> Image.Image:
    """Generate a grid pattern image.

    Supports three visual styles for the grid: continuous lines,
    dots at intersections, or cross marks at intersections.

    Args:
        width: Output image width in pixels.
        height: Output image height in pixels.
        spacing: Distance in pixels between grid lines / intersections.
        line_width: Stroke width for lines or size factor for dots/crosses.
        color: RGB colour of the grid elements.
        bg_color: RGB background colour.
        style: One of ``"lines"``, ``"dots"``, or ``"crosses"``.

    Returns:
        RGB PIL Image of size (width, height).

    Raises:
        ValueError: If *style* is not one of the accepted values.
    """
    valid_styles = ("lines", "dots", "crosses")
    if style not in valid_styles:
        raise ValueError(f"Unknown style {style!r}. Choose from {valid_styles}.")

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    if style == "lines":
        _draw_lines(draw, width, height, spacing, line_width, color)
    elif style == "dots":
        _draw_dots(draw, width, height, spacing, line_width, color)
    elif style == "crosses":
        _draw_crosses(draw, width, height, spacing, line_width, color)

    return img


def _draw_lines(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    spacing: int,
    line_width: int,
    color: tuple[int, int, int],
) -> None:
    """Draw continuous horizontal and vertical grid lines.

    Args:
        draw: PIL ImageDraw instance.
        width: Canvas width.
        height: Canvas height.
        spacing: Pixel distance between parallel lines.
        line_width: Stroke width.
        color: RGB line colour.
    """
    # Vertical lines
    x = 0
    while x < width:
        draw.line([(x, 0), (x, height - 1)], fill=color, width=line_width)
        x += spacing

    # Horizontal lines
    y = 0
    while y < height:
        draw.line([(0, y), (width - 1, y)], fill=color, width=line_width)
        y += spacing


def _draw_dots(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    spacing: int,
    line_width: int,
    color: tuple[int, int, int],
) -> None:
    """Draw dots at grid intersection points.

    The dot radius is derived from *line_width* so that thicker
    settings produce larger dots.

    Args:
        draw: PIL ImageDraw instance.
        width: Canvas width.
        height: Canvas height.
        spacing: Pixel distance between intersection points.
        line_width: Size factor (radius = max(1, line_width)).
        color: RGB dot colour.
    """
    radius = max(1, line_width)
    x = 0
    while x < width:
        y = 0
        while y < height:
            draw.ellipse(
                [x - radius, y - radius, x + radius, y + radius],
                fill=color,
            )
            y += spacing
        x += spacing


def _draw_crosses(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    spacing: int,
    line_width: int,
    color: tuple[int, int, int],
) -> None:
    """Draw small ``+`` cross marks at grid intersection points.

    Each arm of the cross extends *arm_length* pixels from the centre.

    Args:
        draw: PIL ImageDraw instance.
        width: Canvas width.
        height: Canvas height.
        spacing: Pixel distance between intersection points.
        line_width: Stroke width of each arm.
        color: RGB cross colour.
    """
    arm_length = max(2, spacing // 6)
    x = 0
    while x < width:
        y = 0
        while y < height:
            # Horizontal arm
            draw.line(
                [(x - arm_length, y), (x + arm_length, y)],
                fill=color,
                width=line_width,
            )
            # Vertical arm
            draw.line(
                [(x, y - arm_length), (x, y + arm_length)],
                fill=color,
                width=line_width,
            )
            y += spacing
        x += spacing
