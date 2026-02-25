"""Geometric pattern overlay effects."""

from __future__ import annotations

from PIL import Image, ImageDraw


def pattern_overlay(
    img: Image.Image,
    pattern: str = "grid",
    spacing: int = 20,
    opacity: float = 0.1,
    color: tuple[int, int, int] = (255, 255, 255),
) -> Image.Image:
    """Overlay a geometric pattern onto an image.

    Supported pattern types:

    * ``"grid"`` -- horizontal and vertical lines.
    * ``"dots"`` -- evenly spaced filled circles.
    * ``"crosshatch"`` -- diagonal lines in both directions.
    * ``"diagonal"`` -- diagonal lines in one direction (top-left to
      bottom-right).

    The pattern is drawn on a transparent layer and composited onto the
    source image with the given *opacity*.

    Args:
        img: Source image (any mode; converted to RGBA internally).
        pattern: Pattern type name (see list above).
        spacing: Distance in pixels between pattern elements.
        opacity: Overall transparency of the pattern layer (0.0 -- 1.0).
        color: RGB colour of the pattern lines/dots.

    Returns:
        RGBA image with the pattern composited on top.

    Raises:
        ValueError: If *pattern* is not one of the supported types.
    """
    if spacing < 1:
        raise ValueError(f"spacing must be >= 1, got {spacing}")

    img = img.convert("RGBA")
    w, h = img.size

    alpha = int(opacity * 255)
    fill = (*color, alpha)

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    if pattern == "grid":
        _draw_grid(draw, w, h, spacing, fill)
    elif pattern == "dots":
        _draw_dots(draw, w, h, spacing, fill)
    elif pattern == "crosshatch":
        _draw_crosshatch(draw, w, h, spacing, fill)
    elif pattern == "diagonal":
        _draw_diagonal(draw, w, h, spacing, fill)
    else:
        raise ValueError(
            f"Unknown pattern {pattern!r}. Choose from 'grid', 'dots', 'crosshatch', 'diagonal'."
        )

    result = Image.alpha_composite(img, layer)
    return result


# ---------------------------------------------------------------------------
# Internal pattern drawing helpers
# ---------------------------------------------------------------------------


def _draw_grid(
    draw: ImageDraw.ImageDraw,
    w: int,
    h: int,
    spacing: int,
    fill: tuple[int, int, int, int],
) -> None:
    """Draw a grid of horizontal and vertical lines."""
    for x in range(0, w, spacing):
        draw.line([(x, 0), (x, h - 1)], fill=fill, width=1)
    for y in range(0, h, spacing):
        draw.line([(0, y), (w - 1, y)], fill=fill, width=1)


def _draw_dots(
    draw: ImageDraw.ImageDraw,
    w: int,
    h: int,
    spacing: int,
    fill: tuple[int, int, int, int],
) -> None:
    """Draw evenly spaced filled circles."""
    dot_radius = max(1, spacing // 10)
    for y in range(0, h, spacing):
        for x in range(0, w, spacing):
            draw.ellipse(
                [x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius],
                fill=fill,
            )


def _draw_crosshatch(
    draw: ImageDraw.ImageDraw,
    w: int,
    h: int,
    spacing: int,
    fill: tuple[int, int, int, int],
) -> None:
    """Draw diagonal lines in both directions."""
    diagonal = w + h
    for offset in range(-diagonal, diagonal, spacing):
        # Top-left to bottom-right.
        draw.line([(offset, 0), (offset + h, h)], fill=fill, width=1)
        # Top-right to bottom-left.
        draw.line([(w - offset, 0), (w - offset - h, h)], fill=fill, width=1)


def _draw_diagonal(
    draw: ImageDraw.ImageDraw,
    w: int,
    h: int,
    spacing: int,
    fill: tuple[int, int, int, int],
) -> None:
    """Draw diagonal lines from top-left to bottom-right."""
    diagonal = w + h
    for offset in range(-diagonal, diagonal, spacing):
        draw.line([(offset, 0), (offset + h, h)], fill=fill, width=1)
