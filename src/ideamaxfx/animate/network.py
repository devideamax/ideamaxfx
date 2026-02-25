"""Animated network graph build (nodes then edges)."""

from __future__ import annotations

from typing import Callable

from PIL import Image, ImageDraw

from ideamaxfx.animate.chart_utils import (
    _SS,
    COLOR_TEXT_MUTED,
    FONT_AXIS,
    FONT_DATA,
    draw_title,
    finalize_frame,
)
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
    title: str = "",
    subtitle: str = "",
    show_edge_weights: bool = False,
    sharpen: bool = True,
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
        title: Optional chart title.
        subtitle: Optional subtitle.
        show_edge_weights: Show weight labels at edge midpoints.
        sharpen: Apply UnsharpMask after downscale.

    Returns:
        List of PIL Image frames.
    """
    S = _SS

    # Title offset
    title_offset = 0
    if title or subtitle:
        title_offset = 30 * S
        if subtitle:
            title_offset += 16 * S

    margin = 50 * S
    chart_w = width * S - 2 * margin
    chart_h = height * S - 2 * margin - title_offset
    n_nodes = len(nodes)
    n_edges = len(edges)
    max_weight = max((w for _, _, w in edges), default=1.0)

    font = load_font(size=FONT_AXIS * S, path=font_path)
    weight_font = load_font(size=FONT_DATA * S, path=font_path)

    # Pixel positions for nodes
    y_base = margin + title_offset
    positions = [
        (margin + int(x * chart_w), y_base + int(y * chart_h)) for _, x, y in nodes
    ]

    def render(progress: float) -> Image.Image:
        img = Image.new("RGB", (width * S, height * S), bg_color)
        draw = ImageDraw.Draw(img)

        # Title
        if title or subtitle:
            draw_title(draw, title, subtitle, width * S, 8 * S, S, font_path)

        # First half: nodes appear. Second half: edges build.
        node_progress = min(1.0, progress * 2.0)
        edge_progress = max(0.0, (progress - 0.5) * 2.0)

        visible_nodes = max(0, int(n_nodes * node_progress))
        visible_edges = max(0, int(n_edges * edge_progress))

        # Draw edges
        for ei in range(visible_edges):
            src, tgt, weight = edges[ei]
            if src < visible_nodes and tgt < visible_nodes:
                lw = max(1 * S, int((1 + 3 * weight / max_weight) * S))
                draw.line([positions[src], positions[tgt]], fill=edge_color, width=lw)

                # Edge weight label at midpoint
                if show_edge_weights:
                    mx = (positions[src][0] + positions[tgt][0]) // 2
                    my = (positions[src][1] + positions[tgt][1]) // 2
                    wt = f"{weight:.1f}"
                    bbox = draw.textbbox((0, 0), wt, font=weight_font)
                    tw = bbox[2] - bbox[0]
                    th = bbox[3] - bbox[1]
                    draw.text(
                        (mx - tw // 2, my - th // 2),
                        wt,
                        fill=COLOR_TEXT_MUTED,
                        font=weight_font,
                    )

        # Draw nodes
        for ni in range(visible_nodes):
            px, py = positions[ni]
            r = node_radius * S
            draw.ellipse([px - r, py - r, px + r, py + r], fill=node_color)

            label = nodes[ni][0]
            bbox = draw.textbbox((0, 0), label, font=font)
            tw = bbox[2] - bbox[0]
            draw.text((px - tw // 2, py + r + 4 * S), label, fill=text_color, font=font)

        return finalize_frame(img, width, height, sharpen=sharpen)

    return generate_frames(
        render, fps=fps, duration=duration, hold_seconds=hold_seconds, easing=easing
    )
