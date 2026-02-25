"""Staggered delay calculator for multi-element animations."""

from __future__ import annotations


def stagger_delays(
    count: int,
    total_duration: float = 1.0,
    overlap: float = 0.5,
    order: str = "sequential",
) -> list[float]:
    """Calculate staggered start delays for multiple elements.

    Args:
        count: Number of elements.
        total_duration: Total stagger window in seconds.
        overlap: Overlap factor (0=no overlap, 1=all start together).
        order: "sequential", "reverse", "center_out" (center elements first).

    Returns:
        List of start delay times in seconds.
    """
    if count <= 0:
        return []
    if count == 1:
        return [0.0]

    step = total_duration * (1.0 - overlap) / (count - 1)
    delays = [i * step for i in range(count)]

    if order == "reverse":
        delays = delays[::-1]
    elif order == "center_out":
        center = count // 2
        indices = sorted(range(count), key=lambda i: abs(i - center))
        reordered = [0.0] * count
        for rank, idx in enumerate(indices):
            reordered[idx] = rank * step
        delays = reordered

    return delays
