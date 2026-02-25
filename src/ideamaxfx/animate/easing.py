"""15 easing functions for animations.

All functions take t (0.0-1.0) and return an eased value (0.0-1.0).
"""

from __future__ import annotations

import math
from typing import Callable


def linear(t: float) -> float:
    """Linear interpolation (no easing)."""
    return t


def ease_in_quad(t: float) -> float:
    """Quadratic ease-in (accelerating)."""
    return t * t


def ease_out_quad(t: float) -> float:
    """Quadratic ease-out (decelerating)."""
    return t * (2 - t)


def ease_in_out_quad(t: float) -> float:
    """Quadratic ease-in-out."""
    if t < 0.5:
        return 2 * t * t
    return -1 + (4 - 2 * t) * t


def ease_in_cubic(t: float) -> float:
    """Cubic ease-in."""
    return t * t * t


def ease_out_cubic(t: float) -> float:
    """Cubic ease-out."""
    u = t - 1
    return u * u * u + 1


def ease_in_out_cubic(t: float) -> float:
    """Cubic ease-in-out."""
    if t < 0.5:
        return 4 * t * t * t
    u = 2 * t - 2
    return 0.5 * u * u * u + 1


def ease_in_quart(t: float) -> float:
    """Quartic ease-in."""
    return t * t * t * t


def ease_out_quart(t: float) -> float:
    """Quartic ease-out."""
    u = t - 1
    return 1 - u * u * u * u


def ease_in_out_quart(t: float) -> float:
    """Quartic ease-in-out."""
    if t < 0.5:
        return 8 * t * t * t * t
    u = t - 1
    return 1 - 8 * u * u * u * u


def ease_out_elastic(t: float) -> float:
    """Elastic ease-out (spring overshoot)."""
    if t == 0 or t == 1:
        return t
    return math.pow(2, -10 * t) * math.sin((t - 0.075) * (2 * math.pi) / 0.3) + 1


def ease_out_bounce(t: float) -> float:
    """Bounce ease-out."""
    if t < 1 / 2.75:
        return 7.5625 * t * t
    elif t < 2 / 2.75:
        t -= 1.5 / 2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5 / 2.75:
        t -= 2.25 / 2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625 / 2.75
        return 7.5625 * t * t + 0.984375


def ease_out_back(t: float) -> float:
    """Back ease-out (slight overshoot past target)."""
    c1 = 1.70158
    c3 = c1 + 1
    u = t - 1
    return 1 + c3 * u * u * u + c1 * u * u


def ease_in_expo(t: float) -> float:
    """Exponential ease-in."""
    if t == 0:
        return 0.0
    return math.pow(2, 10 * (t - 1))


def ease_out_expo(t: float) -> float:
    """Exponential ease-out."""
    if t == 1:
        return 1.0
    return 1 - math.pow(2, -10 * t)


_EASING_MAP: dict[str, Callable[[float], float]] = {
    "linear": linear,
    "ease_in_quad": ease_in_quad,
    "ease_out_quad": ease_out_quad,
    "ease_in_out_quad": ease_in_out_quad,
    "ease_in_cubic": ease_in_cubic,
    "ease_out_cubic": ease_out_cubic,
    "ease_in_out_cubic": ease_in_out_cubic,
    "ease_in_quart": ease_in_quart,
    "ease_out_quart": ease_out_quart,
    "ease_in_out_quart": ease_in_out_quart,
    "ease_out_elastic": ease_out_elastic,
    "ease_out_bounce": ease_out_bounce,
    "ease_out_back": ease_out_back,
    "ease_in_expo": ease_in_expo,
    "ease_out_expo": ease_out_expo,
}


def get_easing(name: str) -> Callable[[float], float]:
    """Get an easing function by name.

    Args:
        name: Name of the easing function.

    Returns:
        The easing callable.

    Raises:
        ValueError: If the name is not recognized.
    """
    func = _EASING_MAP.get(name)
    if func is None:
        valid = ", ".join(sorted(_EASING_MAP.keys()))
        raise ValueError(f"Unknown easing '{name}'. Valid: {valid}")
    return func
