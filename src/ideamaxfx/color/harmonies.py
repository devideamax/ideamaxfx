"""Color harmony generators based on hue-wheel rotations."""

from __future__ import annotations

from ideamaxfx.color.convert import hex_to_rgb, rgb_to_hsl, hsl_to_rgb


def _ensure_rgb(color: str | tuple[int, int, int]) -> tuple[int, int, int]:
    """Normalise a color that may be a hex string or an RGB tuple.

    Args:
        color: Either a hex string (e.g. ``"#ff0000"``) or an
            ``(r, g, b)`` tuple.

    Returns:
        An ``(r, g, b)`` tuple.
    """
    if isinstance(color, str):
        return hex_to_rgb(color)
    return color


def _rotate_hue(
    color: tuple[int, int, int],
    degrees: float,
) -> tuple[int, int, int]:
    """Rotate the hue of *color* by *degrees* on the colour wheel.

    Args:
        color: An ``(r, g, b)`` tuple.
        degrees: Rotation in degrees (positive = counter-clockwise).

    Returns:
        A new ``(r, g, b)`` tuple.
    """
    h, s, l = rgb_to_hsl(*color)
    h = (h + degrees) % 360.0
    return hsl_to_rgb(h, s, l)


def complementary(
    color: str | tuple[int, int, int],
) -> list[tuple[int, int, int]]:
    """Return the complementary colour (180 degrees opposite on the hue wheel).

    Args:
        color: Input colour as hex string or ``(r, g, b)`` tuple.

    Returns:
        A single-element list containing the complementary ``(r, g, b)``
        tuple.
    """
    rgb = _ensure_rgb(color)
    return [_rotate_hue(rgb, 180.0)]


def triadic(
    color: str | tuple[int, int, int],
) -> list[tuple[int, int, int]]:
    """Return the two triadic colours (each 120 degrees apart).

    Args:
        color: Input colour as hex string or ``(r, g, b)`` tuple.

    Returns:
        A list of two ``(r, g, b)`` tuples.
    """
    rgb = _ensure_rgb(color)
    return [
        _rotate_hue(rgb, 120.0),
        _rotate_hue(rgb, 240.0),
    ]


def analogous(
    color: str | tuple[int, int, int],
    angle: float = 30.0,
) -> list[tuple[int, int, int]]:
    """Return two analogous colours (symmetric offset from the input hue).

    Args:
        color: Input colour as hex string or ``(r, g, b)`` tuple.
        angle: Offset angle in degrees.  Defaults to 30.

    Returns:
        A list of two ``(r, g, b)`` tuples (``-angle`` and ``+angle``).
    """
    rgb = _ensure_rgb(color)
    return [
        _rotate_hue(rgb, -angle),
        _rotate_hue(rgb, angle),
    ]


def split_complementary(
    color: str | tuple[int, int, int],
) -> list[tuple[int, int, int]]:
    """Return two split-complementary colours (150 and 210 degrees).

    Args:
        color: Input colour as hex string or ``(r, g, b)`` tuple.

    Returns:
        A list of two ``(r, g, b)`` tuples.
    """
    rgb = _ensure_rgb(color)
    return [
        _rotate_hue(rgb, 150.0),
        _rotate_hue(rgb, 210.0),
    ]
