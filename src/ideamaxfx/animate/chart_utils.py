"""Shared drawing infrastructure for all chart types."""

from __future__ import annotations

import math

from PIL import Image, ImageDraw, ImageFilter

from ideamaxfx.color.convert import hex_to_rgb
from ideamaxfx.utils.fonts import load_font

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SS = 2  # supersampling factor — single source of truth

# Typography scale (base px, before SS multiplication)
FONT_TITLE = 20
FONT_SUBTITLE = 13
FONT_AXIS = 12
FONT_DATA = 11
FONT_LEGEND = 13

# Dark-theme color tokens
COLOR_TEXT = (255, 255, 255)
COLOR_TEXT_MUTED = (179, 179, 179)
COLOR_GRIDLINE = (68, 68, 68)
COLOR_AXIS = (102, 102, 102)

# D3 Category10 professional palette
D3_CATEGORY10: list[tuple[int, int, int]] = [
    (31, 119, 180),
    (255, 127, 14),
    (44, 160, 44),
    (214, 39, 40),
    (148, 103, 189),
    (140, 86, 75),
    (227, 119, 194),
    (127, 127, 127),
    (188, 189, 34),
    (23, 190, 207),
]


# ---------------------------------------------------------------------------
# Number formatting
# ---------------------------------------------------------------------------


def format_number(value: float, decimals: int = 0) -> str:
    """Format large numbers with K/M suffixes.

    ``1500000 -> "1.5M"``, ``45000 -> "45K"``, ``999 -> "999"``
    """
    abs_val = abs(value)
    sign = "-" if value < 0 else ""
    if abs_val >= 1_000_000:
        formatted = f"{abs_val / 1_000_000:.1f}".rstrip("0").rstrip(".")
        return f"{sign}{formatted}M"
    if abs_val >= 10_000:
        formatted = f"{abs_val / 1_000:.1f}".rstrip("0").rstrip(".")
        return f"{sign}{formatted}K"
    if decimals == 0:
        return f"{sign}{int(abs_val)}"
    return f"{sign}{abs_val:.{decimals}f}"


def format_number_commas(value: float, decimals: int = 0, sep: str = ",") -> str:
    """Format with thousands separator. ``1000000 -> "1,000,000"``."""
    if decimals == 0:
        int_part = str(int(abs(value)))
    else:
        int_part, _, frac_part = f"{abs(value):.{decimals}f}".partition(".")
    sign = "-" if value < 0 else ""
    # Insert separators from right
    groups: list[str] = []
    while len(int_part) > 3:
        groups.append(int_part[-3:])
        int_part = int_part[:-3]
    groups.append(int_part)
    result = sep.join(reversed(groups))
    if decimals > 0:
        result += "." + frac_part  # type: ignore[possibly-undefined]
    return sign + result


# ---------------------------------------------------------------------------
# Tick computation
# ---------------------------------------------------------------------------

_NICE_STEPS = [1, 2, 2.5, 5, 10]


def compute_nice_ticks(
    data_min: float, data_max: float, target_count: int = 6
) -> list[float]:
    """Return a list of 'nice' round tick values spanning *data_min* .. *data_max*."""
    if data_min == data_max:
        if data_min == 0:
            return [0.0]
        return [data_min - abs(data_min) * 0.1, data_min, data_min + abs(data_min) * 0.1]

    raw_range = data_max - data_min
    rough_step = raw_range / max(target_count - 1, 1)
    magnitude = 10 ** math.floor(math.log10(rough_step))

    best_step = magnitude
    for ns in _NICE_STEPS:
        candidate = ns * magnitude
        if candidate >= rough_step:
            best_step = candidate
            break

    tick_min = math.floor(data_min / best_step) * best_step
    tick_max = math.ceil(data_max / best_step) * best_step

    ticks: list[float] = []
    t = tick_min
    while t <= tick_max + best_step * 0.01:
        ticks.append(round(t, 10))
        t += best_step
    return ticks


# ---------------------------------------------------------------------------
# Margin computation
# ---------------------------------------------------------------------------


def compute_margins(
    draw: ImageDraw.ImageDraw,
    y_labels: list[str],
    x_labels: list[str],
    title: str,
    subtitle: str,
    has_legend: bool,
    S: int,
    font_path: str | None,
) -> dict[str, int]:
    """Compute dynamic margins based on actual text widths."""
    axis_font = load_font(size=FONT_AXIS * S, path=font_path)
    title_font = load_font(size=FONT_TITLE * S, path=font_path)

    # Left margin: based on widest Y-axis label
    max_y_w = 0
    for lbl in y_labels:
        bbox = draw.textbbox((0, 0), lbl, font=axis_font)
        max_y_w = max(max_y_w, bbox[2] - bbox[0])
    left = max_y_w + 18 * S  # label + tick mark + gap

    # Right margin
    right = 20 * S
    if has_legend:
        right = 30 * S  # legend handled separately

    # Top margin
    top = 16 * S
    if title:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        top += bbox[3] - bbox[1] + 6 * S
    if subtitle:
        sub_font = load_font(size=FONT_SUBTITLE * S, path=font_path)
        bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
        top += bbox[3] - bbox[1] + 4 * S

    # Bottom margin: x labels + tick marks
    max_x_h = 0
    for lbl in x_labels:
        bbox = draw.textbbox((0, 0), lbl, font=axis_font)
        max_x_h = max(max_x_h, bbox[3] - bbox[1])
    bottom = max_x_h + 18 * S

    return {"left": left, "right": right, "top": top, "bottom": bottom}


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------


def draw_title(
    draw: ImageDraw.ImageDraw,
    title: str,
    subtitle: str,
    canvas_width: int,
    y_start: int,
    S: int,
    font_path: str | None,
) -> int:
    """Draw centered title + subtitle. Returns Y position after title block."""
    y = y_start
    if title:
        font = load_font(size=FONT_TITLE * S, path=font_path)
        bbox = draw.textbbox((0, 0), title, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((canvas_width - tw) // 2, y), title, fill=COLOR_TEXT, font=font)
        y += bbox[3] - bbox[1] + 4 * S
    if subtitle:
        font = load_font(size=FONT_SUBTITLE * S, path=font_path)
        bbox = draw.textbbox((0, 0), subtitle, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((canvas_width - tw) // 2, y), subtitle, fill=COLOR_TEXT_MUTED, font=font)
        y += bbox[3] - bbox[1] + 4 * S
    return y


def draw_y_axis(
    draw: ImageDraw.ImageDraw,
    ticks: list[float],
    chart_area: dict[str, int],
    data_min: float,
    data_max: float,
    S: int,
    font_path: str | None,
    format_fn: object = None,
) -> None:
    """Draw Y-axis line, tick marks, and formatted numbers."""
    if format_fn is None:
        format_fn = format_number
    font = load_font(size=FONT_AXIS * S, path=font_path)
    left = chart_area["left"]
    top = chart_area["top"]
    bottom = chart_area["bottom"]
    chart_h = bottom - top
    d_range = data_max - data_min if data_max != data_min else 1.0

    # Axis line
    draw.line([(left, top), (left, bottom)], fill=COLOR_AXIS, width=max(1, S))

    for t in ticks:
        if data_min <= t <= data_max or abs(t - data_min) < d_range * 0.01 or abs(t - data_max) < d_range * 0.01:
            y = bottom - int((t - data_min) / d_range * chart_h)
            y = max(top, min(bottom, y))
            # Tick mark
            draw.line([(left - 4 * S, y), (left, y)], fill=COLOR_AXIS, width=max(1, S))
            # Label
            label = format_fn(t)  # type: ignore[operator]
            bbox = draw.textbbox((0, 0), label, font=font)
            lw = bbox[2] - bbox[0]
            lh = bbox[3] - bbox[1]
            draw.text((left - 6 * S - lw, y - lh // 2), label, fill=COLOR_TEXT_MUTED, font=font)


def draw_x_axis(
    draw: ImageDraw.ImageDraw,
    labels: list[str],
    positions: list[int],
    chart_area: dict[str, int],
    S: int,
    font_path: str | None,
) -> None:
    """Draw X-axis line, tick marks, and labels."""
    font = load_font(size=FONT_AXIS * S, path=font_path)
    left = chart_area["left"]
    right = chart_area["right_x"]
    bottom = chart_area["bottom"]

    # Axis line
    draw.line([(left, bottom), (right, bottom)], fill=COLOR_AXIS, width=max(1, S))

    for lbl, px in zip(labels, positions):
        # Tick mark
        draw.line([(px, bottom), (px, bottom + 4 * S)], fill=COLOR_AXIS, width=max(1, S))
        # Label
        bbox = draw.textbbox((0, 0), lbl, font=font)
        lw = bbox[2] - bbox[0]
        draw.text((px - lw // 2, bottom + 6 * S), lbl, fill=COLOR_TEXT_MUTED, font=font)


def draw_gridlines(
    draw: ImageDraw.ImageDraw,
    ticks: list[float],
    chart_area: dict[str, int],
    data_min: float,
    data_max: float,
    S: int,
    color: tuple[int, int, int] | None = None,
) -> None:
    """Draw horizontal gridlines at tick positions."""
    if color is None:
        color = COLOR_GRIDLINE
    left = chart_area["left"]
    right_x = chart_area["right_x"]
    top = chart_area["top"]
    bottom = chart_area["bottom"]
    chart_h = bottom - top
    d_range = data_max - data_min if data_max != data_min else 1.0

    for t in ticks:
        if data_min <= t <= data_max or abs(t - data_min) < d_range * 0.01:
            y = bottom - int((t - data_min) / d_range * chart_h)
            y = max(top, min(bottom, y))
            if y != bottom:  # skip baseline
                draw.line([(left, y), (right_x, y)], fill=color, width=max(1, S // 2))


def draw_legend(
    draw: ImageDraw.ImageDraw,
    items: list[str],
    colors: list[tuple[int, int, int]],
    chart_area: dict[str, int],
    canvas_width: int,
    S: int,
    font_path: str | None,
    position: str = "bottom",
) -> None:
    """Draw color squares + labels as a legend."""
    font = load_font(size=FONT_LEGEND * S, path=font_path)
    box_size = 10 * S
    gap = 16 * S
    item_gap = 20 * S

    if position == "bottom":
        # Compute total width
        total_w = 0
        for item in items:
            bbox = draw.textbbox((0, 0), item, font=font)
            total_w += box_size + 6 * S + (bbox[2] - bbox[0]) + item_gap
        total_w -= item_gap  # no trailing gap

        x = (canvas_width - total_w) // 2
        y = chart_area["bottom"] + gap
        for i, item in enumerate(items):
            c = colors[i % len(colors)]
            draw.rectangle([x, y, x + box_size, y + box_size], fill=c)
            bbox = draw.textbbox((0, 0), item, font=font)
            draw.text((x + box_size + 6 * S, y - 1 * S), item, fill=COLOR_TEXT_MUTED, font=font)
            x += box_size + 6 * S + (bbox[2] - bbox[0]) + item_gap
    else:  # right
        x = chart_area["right_x"] + 16 * S
        y = chart_area["top"]
        for i, item in enumerate(items):
            c = colors[i % len(colors)]
            draw.rectangle([x, y + 2 * S, x + box_size, y + 2 * S + box_size], fill=c)
            draw.text(
                (x + box_size + 6 * S, y), item, fill=COLOR_TEXT_MUTED, font=font
            )
            bbox = draw.textbbox((0, 0), item, font=font)
            y += max(box_size, bbox[3] - bbox[1]) + 8 * S


# ---------------------------------------------------------------------------
# Frame finalization
# ---------------------------------------------------------------------------


def finalize_frame(
    img: Image.Image,
    width: int,
    height: int,
    sharpen: bool = True,
) -> Image.Image:
    """LANCZOS downscale + optional UnsharpMask for crisp text."""
    result = img.convert("RGB").resize((width, height), Image.LANCZOS)
    if sharpen:
        result = result.filter(ImageFilter.UnsharpMask(radius=1.0, percent=40, threshold=2))
    return result


# ---------------------------------------------------------------------------
# Color parsing
# ---------------------------------------------------------------------------


def parse_colors(
    colors: list[str] | list[tuple[int, int, int]] | None,
    n: int,
    default_palette: list[tuple[int, int, int]] | None = None,
) -> list[tuple[int, int, int]]:
    """Parse hex/RGB color list, cycling the palette when needed."""
    if default_palette is None:
        default_palette = D3_CATEGORY10
    if colors:
        parsed: list[tuple[int, int, int]] = []
        for c in colors:
            if isinstance(c, str):
                parsed.append(hex_to_rgb(c))
            else:
                parsed.append(c)
        # Cycle if fewer colors than needed
        while len(parsed) < n:
            parsed.append(parsed[len(parsed) % len(parsed)] if parsed else default_palette[0])
        return parsed[:n]
    return [default_palette[i % len(default_palette)] for i in range(n)]
