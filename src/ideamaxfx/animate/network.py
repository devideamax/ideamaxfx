"""Animated network graph build (nodes then edges)."""

from __future__ import annotations

from typing import Callable

from PIL import Image, ImageDraw

from ideamaxfx.animate.core import generate_frames
from ideamaxfx.utils.fonts import load_font


def network_build(
    nodes: list[tuple[str, float, float]],
    edges: list[tuple[int, int, float]],
    node_color: tuple[int, int, int] = (0, 245, 212),
    edge_color: tuple[int, int, int] = (80, 80, 100),
    node_radius: int = 12,
    width: int = 600,
    height: int = 500,
    bg_color: tuple[int, int, int] = (13, 17, 23),
    text_color: tuple[int, int, int] = (200, 200, 210),
    fps: int = 15,
    duration: float = 3.0,
    hold_seconds: float = 2.0,
    easing: str | Callable[[float], float] = "ease_out_cubic",
    font_path: str | None = None,
) -> list[Image.Image]:
    """Generate animated network graph with nodes appearing then edges building.

    Args:
        nodes: List of (label, x_fraction, y_fraction) where fractions are 0-1.
        edges: List of (source_idx, target_idx, weight).
        node_color: Node fill color.
        edge_color: Edge line color.
        node_radius: Radius of node circles.
        width: Image width.
        height: Image height.
        bg_color: Background color.
        text_color: Label color.
        fps: Frames per second.
        duration: Total animation duration.
        hold_seconds: Hold final frame.
        easing: Easing function name or callable.
        font_path: Optional font path.

    Returns:
        List of PIL Image frames.
    """
    margin = 50
    chart_w = width - 2 * margin
    chart_h = height - 2 * margin
    n_nodes = len(nodes)
    n_edges = len(edges)
    max_weight = max((w for _, _, w in edges), default=1.0)

    font = load_font(size=10, path=font_path)

    # Pixel positions for nodes
    positions = [(margin + int(x * chart_w), margin + int(y * chart_h)) for _, x, y in nodes]

    def render(progress: float) -> Image.Image:
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        # First half: nodes appear. Second half: edges build.
        node_progress = min(1.0, progress * 2.0)
        edge_progress = max(0.0, (progress - 0.5) * 2.0)

        visible_nodes = max(0, int(n_nodes * node_progress))
        visible_edges = max(0, int(n_edges * edge_progress))

        # Draw edges
        for ei in range(visible_edges):
            src, tgt, weight = edges[ei]
            if src < visible_nodes and tgt < visible_nodes:
                lw = max(1, int(1 + 3 * weight / max_weight))
                draw.line([positions[src], positions[tgt]], fill=edge_color, width=lw)

        # Draw nodes
        for ni in range(visible_nodes):
            px, py = positions[ni]
            r = node_radius
            draw.ellipse([px - r, py - r, px + r, py + r], fill=node_color)

            label = nodes[ni][0]
            bbox = draw.textbbox((0, 0), label, font=font)
            tw = bbox[2] - bbox[0]
            draw.text((px - tw // 2, py + r + 4), label, fill=text_color, font=font)

        return img

    return generate_frames(
        render, fps=fps, duration=duration, hold_seconds=hold_seconds, easing=easing
    )
