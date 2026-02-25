"""animated_bar.py -- Generate 3 animated bar chart GIFs with different easing.

Creates three distinct animated bar charts that demonstrate the ``bar_grow``
animation function with different data sets and easing curves:

1. **Sports stats** (Goals, Assists, Passes) with ``ease_out_elastic``
2. **Quarterly revenue** with ``ease_out_cubic``
3. **Head-to-head comparison** with ``ease_out_bounce``

Each GIF is kept small and fast by using ``fps=10``, ``duration=1.5``, and
``hold_seconds=1.0``.

Run::

    python examples/animated_bar.py

Output files::

    examples/output/bar_sports.gif
    examples/output/bar_revenue.gif
    examples/output/bar_comparison.gif
"""

from __future__ import annotations

import os
import sys

# ---------------------------------------------------------------------------
# Ensure the library is importable when running from the repo root.
# ---------------------------------------------------------------------------
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO, "src"))

from ideamaxfx.animate import bar_grow, export_gif

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
FPS = 10
DURATION = 1.5
HOLD = 1.0
WIDTH = 800
HEIGHT = 500


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Sports statistics -- elastic easing gives a spring overshoot
    # ------------------------------------------------------------------
    print("1/3  Generating bar_sports.gif (ease_out_elastic) ...")
    frames_sports = bar_grow(
        labels=["Goals", "Assists", "Passes", "Tackles", "Saves"],
        values=[24, 18, 312, 47, 89],
        colors=[
            (212, 33, 61),   # red
            (0, 102, 51),    # green
            (0, 86, 160),    # blue
            (255, 165, 0),   # orange
            (148, 103, 189), # purple
        ],
        width=WIDTH,
        height=HEIGHT,
        title="Season Performance",
        easing="ease_out_elastic",
        fps=FPS,
        duration=DURATION,
        hold_seconds=HOLD,
    )
    path_sports = os.path.join(OUTPUT_DIR, "bar_sports.gif")
    export_gif(frames_sports, path_sports, fps=FPS)
    print(f"   Saved: {path_sports}  ({len(frames_sports)} frames)")

    # ------------------------------------------------------------------
    # 2. Quarterly revenue -- smooth cubic deceleration
    # ------------------------------------------------------------------
    print("2/3  Generating bar_revenue.gif (ease_out_cubic) ...")
    frames_revenue = bar_grow(
        labels=["Q1", "Q2", "Q3", "Q4"],
        values=[42_500, 58_300, 73_100, 91_200],
        colors=[
            (0, 245, 212),  # cyan
            (50, 205, 50),  # green
            (255, 165, 0),  # orange
            (212, 33, 61),  # red
        ],
        width=WIDTH,
        height=HEIGHT,
        title="Revenue by Quarter ($)",
        easing="ease_out_cubic",
        fps=FPS,
        duration=DURATION,
        hold_seconds=HOLD,
    )
    path_revenue = os.path.join(OUTPUT_DIR, "bar_revenue.gif")
    export_gif(frames_revenue, path_revenue, fps=FPS)
    print(f"   Saved: {path_revenue}  ({len(frames_revenue)} frames)")

    # ------------------------------------------------------------------
    # 3. Comparison chart -- bounce easing for a playful feel
    # ------------------------------------------------------------------
    print("3/3  Generating bar_comparison.gif (ease_out_bounce) ...")
    frames_compare = bar_grow(
        labels=["React", "Vue", "Angular", "Svelte", "Solid"],
        values=[78, 65, 52, 45, 38],
        colors=[
            (97, 218, 251),  # React cyan
            (66, 184, 131),  # Vue green
            (221, 0, 49),    # Angular red
            (255, 62, 0),    # Svelte orange
            (68, 107, 158),  # Solid blue
        ],
        width=WIDTH,
        height=HEIGHT,
        title="Framework Satisfaction (%)",
        easing="ease_out_bounce",
        fps=FPS,
        duration=DURATION,
        hold_seconds=HOLD,
    )
    path_compare = os.path.join(OUTPUT_DIR, "bar_comparison.gif")
    export_gif(frames_compare, path_compare, fps=FPS)
    print(f"   Saved: {path_compare}  ({len(frames_compare)} frames)")

    print(f"\nDone. 3 GIFs written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
