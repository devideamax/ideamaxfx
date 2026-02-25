"""Color adjustment helpers — darken, lighten, saturate, desaturate."""

from __future__ import annotations

from ideamaxfx.color.convert import rgb_to_hsl, hsl_to_rgb


def darken(
    color: tuple[int, int, int],
    amount: float = 0.2,
) -> tuple[int, int, int]:
    """Darken a color by reducing its lightness.

    Args:
        color: An ``(r, g, b)`` tuple with values in 0-255.
        amount: How much to reduce lightness, from 0.0 (no change)
            to 1.0 (fully dark).  Defaults to 0.2.

    Returns:
        A new ``(r, g, b)`` tuple.
    """
    h, s, l = rgb_to_hsl(*color)
    l = max(0.0, l - amount)
    return hsl_to_rgb(h, s, l)


def lighten(
    color: tuple[int, int, int],
    amount: float = 0.2,
) -> tuple[int, int, int]:
    """Lighten a color by increasing its lightness.

    Args:
        color: An ``(r, g, b)`` tuple with values in 0-255.
        amount: How much to increase lightness, from 0.0 (no change)
            to 1.0 (fully light).  Defaults to 0.2.

    Returns:
        A new ``(r, g, b)`` tuple.
    """
    h, s, l = rgb_to_hsl(*color)
    l = min(1.0, l + amount)
    return hsl_to_rgb(h, s, l)


def saturate(
    color: tuple[int, int, int],
    amount: float = 0.2,
) -> tuple[int, int, int]:
    """Increase the saturation of a color.

    Args:
        color: An ``(r, g, b)`` tuple with values in 0-255.
        amount: How much to increase saturation, from 0.0 (no change)
            to 1.0 (fully saturated).  Defaults to 0.2.

    Returns:
        A new ``(r, g, b)`` tuple.
    """
    h, s, l = rgb_to_hsl(*color)
    s = min(1.0, s + amount)
    return hsl_to_rgb(h, s, l)


def desaturate(
    color: tuple[int, int, int],
    amount: float = 0.2,
) -> tuple[int, int, int]:
    """Decrease the saturation of a color.

    Args:
        color: An ``(r, g, b)`` tuple with values in 0-255.
        amount: How much to decrease saturation, from 0.0 (no change)
            to 1.0 (fully desaturated / grey).  Defaults to 0.2.

    Returns:
        A new ``(r, g, b)`` tuple.
    """
    h, s, l = rgb_to_hsl(*color)
    s = max(0.0, s - amount)
    return hsl_to_rgb(h, s, l)
