"""Hex / RGB / HSL color-space conversions."""

from __future__ import annotations


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert a hex color string to an RGB tuple.

    Args:
        hex_color: A hex color string, with or without the leading ``#``.
            Examples: ``"#ff0000"``, ``"ff0000"``.

    Returns:
        A tuple of ``(r, g, b)`` integers in the range 0-255.

    Raises:
        ValueError: If the hex string is not exactly 6 hex digits
            (after stripping ``#``).
    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError(f"Expected 6 hex digits, got {len(hex_color)}: {hex_color!r}")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB integers to a hex color string.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        A lowercase hex string in the form ``"#rrggbb"``.

    Raises:
        ValueError: If any channel is outside the 0-255 range.
    """
    for name, val in (("r", r), ("g", g), ("b", b)):
        if not 0 <= val <= 255:
            raise ValueError(f"{name} must be 0-255, got {val}")
    return f"#{r:02x}{g:02x}{b:02x}"


def rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    """Convert RGB to HSL.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        A tuple of ``(h, s, l)`` where *h* is 0-360 and *s*, *l* are 0.0-1.0.
    """
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    c_max = max(r_norm, g_norm, b_norm)
    c_min = min(r_norm, g_norm, b_norm)
    delta = c_max - c_min

    # Lightness
    l = (c_max + c_min) / 2.0

    if delta == 0.0:
        h = 0.0
        s = 0.0
    else:
        # Saturation
        s = delta / (1.0 - abs(2.0 * l - 1.0))

        # Hue
        if c_max == r_norm:
            h = 60.0 * (((g_norm - b_norm) / delta) % 6.0)
        elif c_max == g_norm:
            h = 60.0 * (((b_norm - r_norm) / delta) + 2.0)
        else:
            h = 60.0 * (((r_norm - g_norm) / delta) + 4.0)

    # Clamp hue to [0, 360)
    h = h % 360.0

    return (h, s, l)


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    """Convert HSL to RGB.

    Args:
        h: Hue in degrees (0-360).
        s: Saturation (0.0-1.0).
        l: Lightness (0.0-1.0).

    Returns:
        A tuple of ``(r, g, b)`` integers in the range 0-255.
    """
    s = max(0.0, min(1.0, s))
    l = max(0.0, min(1.0, l))
    h = h % 360.0

    c = (1.0 - abs(2.0 * l - 1.0)) * s
    x = c * (1.0 - abs((h / 60.0) % 2.0 - 1.0))
    m = l - c / 2.0

    if h < 60.0:
        r1, g1, b1 = c, x, 0.0
    elif h < 120.0:
        r1, g1, b1 = x, c, 0.0
    elif h < 180.0:
        r1, g1, b1 = 0.0, c, x
    elif h < 240.0:
        r1, g1, b1 = 0.0, x, c
    elif h < 300.0:
        r1, g1, b1 = x, 0.0, c
    else:
        r1, g1, b1 = c, 0.0, x

    r = round((r1 + m) * 255.0)
    g = round((g1 + m) * 255.0)
    b = round((b1 + m) * 255.0)

    return (
        max(0, min(255, r)),
        max(0, min(255, g)),
        max(0, min(255, b)),
    )
