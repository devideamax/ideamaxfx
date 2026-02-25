"""Base animation loop and frame generation."""

from __future__ import annotations

from typing import Callable

from PIL import Image

from ideamaxfx.animate.easing import get_easing


def generate_frames(
    render_fn: Callable[[float], Image.Image],
    fps: int = 15,
    duration: float = 2.0,
    hold_seconds: float = 1.0,
    easing: str | Callable[[float], float] = "ease_out_cubic",
) -> list[Image.Image]:
    """Generate animation frames using a render function.

    Args:
        render_fn: A callable that takes progress (0.0-1.0) and returns a PIL Image.
        fps: Frames per second.
        duration: Duration of the animation phase in seconds.
        hold_seconds: Duration to hold the final frame.
        easing: Easing function name or callable.

    Returns:
        List of PIL Image frames.
    """
    if fps <= 0:
        raise ValueError(f"fps must be positive, got {fps}")
    if duration < 0:
        raise ValueError(f"duration must be non-negative, got {duration}")

    ease_fn: Callable[[float], float]
    if isinstance(easing, str):
        ease_fn = get_easing(easing)
    else:
        ease_fn = easing

    n_anim = max(1, int(fps * duration))
    n_hold = max(1, int(fps * hold_seconds))

    frames: list[Image.Image] = []

    # Animation frames
    for i in range(n_anim):
        t = i / max(1, n_anim - 1)
        progress = ease_fn(t)
        frame = render_fn(progress)
        frames.append(frame)

    # Hold frames (repeat last)
    if frames:
        last = frames[-1]
        for _ in range(n_hold):
            frames.append(last)

    return frames
