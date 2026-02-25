"""WCAG colour-accessibility helpers."""

from __future__ import annotations


def _relative_luminance(color: tuple[int, int, int]) -> float:
    """Compute the WCAG relative luminance of an sRGB colour.

    Reference: https://www.w3.org/TR/WCAG21/#dfn-relative-luminance

    Args:
        color: An ``(r, g, b)`` tuple with values in 0-255.

    Returns:
        Relative luminance in the range 0.0 (black) to 1.0 (white).
    """
    channels: list[float] = []
    for c in color:
        c_norm = c / 255.0
        if c_norm <= 0.04045:
            channels.append(c_norm / 12.92)
        else:
            channels.append(((c_norm + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast_ratio(
    color1: tuple[int, int, int],
    color2: tuple[int, int, int],
) -> float:
    """Calculate the WCAG contrast ratio between two colours.

    The result is always >= 1.0 (identical colours yield 1.0, black vs.
    white yields 21.0).

    Args:
        color1: First colour as ``(r, g, b)``.
        color2: Second colour as ``(r, g, b)``.

    Returns:
        The contrast ratio rounded to two decimal places.
    """
    l1 = _relative_luminance(color1)
    l2 = _relative_luminance(color2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)


def wcag_check(
    fg: tuple[int, int, int],
    bg: tuple[int, int, int],
    level: str = "AA",
) -> bool:
    """Check whether a foreground/background pair meets a WCAG contrast level.

    Args:
        fg: Foreground (text) colour as ``(r, g, b)``.
        bg: Background colour as ``(r, g, b)``.
        level: ``"AA"`` requires a ratio >= 4.5:1; ``"AAA"`` requires
            >= 7:1.  Defaults to ``"AA"``.

    Returns:
        ``True`` if the contrast ratio meets or exceeds the threshold for
        the requested level.

    Raises:
        ValueError: If *level* is not ``"AA"`` or ``"AAA"``.
    """
    level_upper = level.upper()
    if level_upper == "AA":
        threshold = 4.5
    elif level_upper == "AAA":
        threshold = 7.0
    else:
        raise ValueError(f"level must be 'AA' or 'AAA', got {level!r}")

    return contrast_ratio(fg, bg) >= threshold


def suggest_readable(
    bg: tuple[int, int, int],
) -> tuple[int, int, int]:
    """Suggest black or white text for maximum readability on *bg*.

    Args:
        bg: Background colour as ``(r, g, b)``.

    Returns:
        ``(0, 0, 0)`` (black) or ``(255, 255, 255)`` (white), whichever
        gives a higher contrast ratio against *bg*.
    """
    ratio_black = contrast_ratio((0, 0, 0), bg)
    ratio_white = contrast_ratio((255, 255, 255), bg)
    if ratio_black >= ratio_white:
        return (0, 0, 0)
    return (255, 255, 255)
