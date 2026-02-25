"""Color interpolation between two endpoints."""

from __future__ import annotations

from ideamaxfx.color.convert import hex_to_rgb


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


def interpolate_colors(
    color1: str | tuple[int, int, int],
    color2: str | tuple[int, int, int],
    steps: int = 5,
) -> list[tuple[int, int, int]]:
    """Generate evenly-spaced colors between two endpoints (inclusive).

    The returned list always contains *steps* colours.  The first element
    equals *color1* and the last equals *color2*.

    Args:
        color1: Start color as hex string or ``(r, g, b)`` tuple.
        color2: End color as hex string or ``(r, g, b)`` tuple.
        steps: Total number of colours to produce (including both
            endpoints).  Must be at least 2.  Defaults to 5.

    Returns:
        A list of ``(r, g, b)`` tuples of length *steps*.

    Raises:
        ValueError: If *steps* is less than 2.
    """
    if steps < 2:
        raise ValueError(f"steps must be >= 2, got {steps}")

    r1, g1, b1 = _ensure_rgb(color1)
    r2, g2, b2 = _ensure_rgb(color2)

    result: list[tuple[int, int, int]] = []
    for i in range(steps):
        t = i / (steps - 1)
        r = round(r1 + (r2 - r1) * t)
        g = round(g1 + (g2 - g1) * t)
        b = round(b1 + (b2 - b1) * t)
        result.append((r, g, b))

    return result
