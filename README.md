# ideamaxfx

**Post-production effects, animated chart build-up, and visual toolkit for Python.**

[![PyPI version](https://img.shields.io/pypi/v/ideamaxfx)](https://pypi.org/project/ideamaxfx/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-376%20passed-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen)]()
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000)](https://github.com/astral-sh/ruff)

---

## What It Does

- **Post-Production Effects Pipeline** -- Chainable API for cinematic finishing: grain, glow, scanlines, vignette, chromatic aberration, bloom, halftone, duotone, glass card, pattern overlays, and blend modes. Every method returns `self` so you can build complex multi-effect stacks in a single expression.

- **Animated Chart Build-Up** -- Generate GIF/APNG/WebP/MP4 sequences where chart elements appear progressively with easing: bar, line, radar, scatter, pie, counter, heatmap, network, and morph transitions. Every chart renders with Y/X axes, gridlines, formatted numbers, legends, and title/subtitle support. Ships with 15 built-in easing functions, D3 Category10 palette, and 2x supersampling with UnsharpMask sharpening.

- **Visual Toolkit** -- Text effects (neon, gradient, outline, shadow, emboss), layout components (stat cards, progress bars, badges), color utilities, image composition, texture generators, and watermark tools. Pure Pillow core with optional matplotlib/scipy for advanced use cases.

---

## Installation

```bash
pip install ideamaxfx
```

Optional extras:

```bash
pip install ideamaxfx[video]  # MP4 export (imageio-ffmpeg)
pip install ideamaxfx[full]   # everything: matplotlib + scipy + video
```

---

## Quick Start

### Effects Pipeline

```python
from ideamaxfx import EffectsPipeline
from PIL import Image

img = Image.open("chart.png")
result = (EffectsPipeline(img)
          .grain(0.06)
          .glow(color=(0, 245, 212))
          .scanlines(spacing=4)
          .vignette(0.3)
          .export("finished.png"))
```

### Animated Bar Chart

```python
from ideamaxfx.animate import bar_grow, export_gif, export_webp

frames = bar_grow(
    labels=['Revenue', 'Costs', 'Profit'],
    values=[1_500_000, 850_000, 650_000],
    title='Q4 Financial Summary',
    subtitle='All values in USD',
    show_gridlines=True,
    show_values=True,
    easing='ease_out_elastic'
)
export_gif(frames, 'chart.gif')
export_webp(frames, 'chart.webp', quality=85)  # 24-bit color, ~66% smaller
```

### Text Effects

```python
from ideamaxfx.text import neon_text, gradient_text
from ideamaxfx.utils import load_font

font = load_font(size=48)
img = neon_text(canvas, 20, 20, "ELITE", font=font, color=(0, 245, 212))
```

---

## Modules

| Module | Description | Key Functions |
|--------|-------------|---------------|
| `effects` | Post-production effects | `grain`, `glow`, `glow_border`, `halftone`, `scanlines`, `glass_card`, `duotone`, `vignette`, `chromatic_aberration`, `bloom`, `blue_noise`, `pattern_overlay`, `blend`, `EffectsPipeline` |
| `animate` | Animated build-up | `bar_grow`, `line_draw`, `radar_sweep`, `scatter_fade`, `counter_roll`, `pie_fill`, `heatmap_reveal`, `network_build`, `morph`, `stagger_delays`, `compose_animations`, `export_gif`, `export_apng`, `export_webp`, `export_mp4` |
| `text` | Text effects | `gradient_text`, `neon_text`, `outline_text`, `shadow_text`, `emboss_text` |
| `color` | Color utilities | `hex_to_rgb`, `rgb_to_hex`, `rgb_to_hsl`, `hsl_to_rgb`, `interpolate_colors`, `complementary`, `triadic`, `analogous`, `extract_palette`, `contrast_ratio`, `wcag_check` |
| `layout` | UI components | `stat_card`, `progress_bar`, `badge`, `legend_block`, `divider`, `callout` |
| `compose` | Image composition | `rounded_corners`, `drop_shadow`, `mirror_reflection`, `tilt_shift`, `pixelate`, `color_overlay` |
| `texture` | Pattern generators | `perlin_noise`, `grid_pattern`, `stripe_pattern`, `dot_pattern` |
| `watermark` | Branding tools | `text_watermark`, `image_watermark`, `footer_bar` |
| `utils` | Helpers | `load_font`, `mpl_to_pil`, `numpy_to_pil`, `pil_to_numpy` |

---

## Effects Pipeline API

`EffectsPipeline` wraps a PIL `Image` and returns `self` from every effect method, enabling fluent call chains. Call `.export(path)` to save the result to disk, or access the `.image` property to get the current frame without writing a file. The pipeline operates on an internal copy, so the original image is never mutated.

```python
pipeline = EffectsPipeline(img)
```

| Method | Parameters | Description |
|--------|-----------|-------------|
| `.grain(intensity, monochrome)` | `intensity: float = 0.06`, `monochrome: bool = True` | Film grain noise overlay |
| `.glow(color, radius, intensity)` | `color: (R,G,B) = (0,245,212)`, `radius: int = 20`, `intensity: float = 0.5` | Bright-area glow with RGB tint |
| `.halftone(dot_size, spacing, angle)` | `dot_size: int = 6`, `spacing: int = 8`, `angle: float = 45.0` | Halftone dot pattern conversion |
| `.scanlines(spacing, opacity, color)` | `spacing: int = 4`, `opacity: float = 0.3`, `color: (R,G,B) = (0,0,0)` | CRT scanline overlay |
| `.glass(x, y, w, h, blur, tint, radius)` | `x, y, w, h: int`, `blur: int = 15`, `tint: (R,G,B,A) = (20,25,40,160)`, `radius: int = 12` | Glassmorphism card region |
| `.duotone(dark, light)` | `dark: (R,G,B) = (10,10,40)`, `light: (R,G,B) = (255,200,50)` | Two-tone color mapping |
| `.vignette(strength, radius)` | `strength: float = 0.3`, `radius: float = 1.0` | Edge darkening |
| `.chromatic(offset, direction)` | `offset: int = 5`, `direction: str = "horizontal"` | Channel-shift chromatic aberration |
| `.bloom(threshold, radius, intensity)` | `threshold: int = 200`, `radius: int = 15`, `intensity: float = 0.4` | Bloom glow on bright regions |
| `.export(path, quality)` | `path: str`, `quality: int = 95` | Save to disk, returns `Image` |
| `.image` | property | Current image copy (no save) |

### Example: full chain

```python
from ideamaxfx import EffectsPipeline
from PIL import Image

result = (EffectsPipeline(Image.open("input.png"))
          .grain(0.04)
          .bloom(threshold=180, radius=20, intensity=0.5)
          .chromatic(offset=3)
          .scanlines(spacing=3, opacity=0.2)
          .vignette(0.35)
          .export("cinematic.png"))
```

---

## Animation Export

The `animate` module produces a list of PIL `Image` frames. Four export formats are available:

| Format | Function | Colors | Size | Dependencies |
|--------|----------|--------|------|--------------|
| **GIF** | `export_gif` | 256 max | Large | None |
| **APNG** | `export_apng` | Full 24-bit | Medium | None |
| **WebP** | `export_webp` | Full 24-bit | Small (~66% of GIF) | None |
| **MP4** | `export_mp4` | Full 24-bit | Smallest | `imageio-ffmpeg` |

```python
from ideamaxfx.animate import export_gif, export_apng, export_webp, export_mp4

export_gif(frames, "output.gif", fps=15)         # universal compatibility
export_apng(frames, "output.png", fps=15)         # lossless, modern browsers
export_webp(frames, "output.webp", quality=85)    # best web balance
export_mp4(frames, "output.mp4", fps=15)          # video platforms
```

**`export_gif` parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `frames` | `list[Image]` | required | PIL Image frame sequence |
| `output_path` | `str` | required | Destination file path |
| `fps` | `int` | `15` | Frames per second |
| `max_colors` | `int` | `256` | Maximum palette colors |
| `max_kb` | `int` | `2000` | Target max file size in KB |
| `lossy` | `int` | `0` | gifsicle lossy level (0-200) |
| `optimize` | `bool` | `True` | Use gifsicle if available |

When gifsicle is installed, `export_gif` runs a two-pass optimization: first at the requested settings, then a more aggressive pass if the file exceeds `max_kb`. Without gifsicle it falls back to Pillow's built-in GIF writer with adaptive palette quantization.

**`export_webp` parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `frames` | `list[Image]` | required | PIL Image frame sequence |
| `output_path` | `str` | required | Destination file path |
| `fps` | `int` | `15` | Frames per second |
| `quality` | `int` | `80` | WebP quality (1-100) |
| `lossless` | `bool` | `False` | Use lossless compression |

**`export_mp4` parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `frames` | `list[Image]` | required | PIL Image frame sequence |
| `output_path` | `str` | required | Destination file path |
| `fps` | `int` | `15` | Frames per second |
| `codec` | `str` | `"libx264"` | Video codec |
| `quality` | `int` | `23` | CRF value (lower = better, 0-51) |

MP4 export requires `imageio-ffmpeg`. Install with `pip install ideamaxfx[video]`.

**`export_apng` parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `frames` | `list[Image]` | required | PIL Image frame sequence |
| `output_path` | `str` | required | Destination file path |
| `fps` | `int` | `15` | Frames per second |

---

## Easing Functions

All 15 easing functions accept `t` in the range `[0.0, 1.0]` and return the eased value. Pass the function name as a string to any `easing` parameter in the `animate` module, or call `get_easing(name)` to retrieve the callable directly.

| Name | Description |
|------|-------------|
| `linear` | Constant speed, no acceleration |
| `ease_in_quad` | Quadratic ease-in (accelerating) |
| `ease_out_quad` | Quadratic ease-out (decelerating) |
| `ease_in_out_quad` | Quadratic ease-in then ease-out |
| `ease_in_cubic` | Cubic ease-in |
| `ease_out_cubic` | Cubic ease-out |
| `ease_in_out_cubic` | Cubic ease-in then ease-out |
| `ease_in_quart` | Quartic ease-in |
| `ease_out_quart` | Quartic ease-out |
| `ease_in_out_quart` | Quartic ease-in then ease-out |
| `ease_out_elastic` | Spring overshoot with oscillation |
| `ease_out_bounce` | Bouncing ball decay |
| `ease_out_back` | Slight overshoot past target |
| `ease_in_expo` | Exponential ease-in |
| `ease_out_expo` | Exponential ease-out |

Use by name:

```python
from ideamaxfx.animate import bar_grow

frames = bar_grow(labels=["A", "B"], values=[80, 60], easing="ease_out_bounce")
```

Or retrieve the function directly:

```python
from ideamaxfx.animate import get_easing

fn = get_easing("ease_out_elastic")
value = fn(0.5)  # returns eased float in 0.0-1.0
```

---

## Chart Parameters (v0.1.1)

All chart functions (`bar_grow`, `line_draw`, `scatter_fade`, `radar_sweep`, `pie_fill`, `counter_roll`, `heatmap_reveal`, `network_build`) share common new parameters. All are optional with sensible defaults — existing code works without changes.

| Parameter | Available on | Default | Description |
|-----------|-------------|---------|-------------|
| `subtitle` | all | `""` | Subtitle below the title |
| `show_gridlines` | bar, line, scatter | `True` | Horizontal gridlines at tick positions |
| `show_values` | bar, heatmap | `True` | Value labels on chart elements |
| `value_format` | bar | `"auto"` | `"auto"`, `"raw"`, `"K"`, `"M"`, `"comma"` |
| `show_legend` | line, scatter, pie | `True` | Color legend for multi-series data |
| `legend_position` | pie | `"right"` | `"right"` or `"bottom"` |
| `show_percentages` | pie | `True` | Percentage labels on sectors |
| `label_style` | pie | `"fade"` | `"fade"` (gradual) or `"pop"` (instant at 80%) |
| `show_points` | line | `True` | Data point dots |
| `point_radius` | line | `None` | Point size (None = auto) |
| `x_label`, `y_label` | line, scatter | `""` | Axis labels |
| `show_ring_values` | radar | `True` | Numbers on grid rings |
| `ring_count` | radar | `4` | Number of concentric rings |
| `grid_color` | radar | `(68,68,68)` | Grid line color |
| `show_color_bar` | heatmap | `True` | Vertical gradient min→max legend |
| `show_edge_weights` | network | `False` | Weight labels at edge midpoints |
| `thousands_separator` | counter | `","` | Thousand separator (`","` → `1,500,000`) |
| `sharpen` | all | `True` | UnsharpMask after LANCZOS downscale |

### Example: line chart with all features

```python
from ideamaxfx.animate import line_draw, export_webp

frames = line_draw(
    x_values=[1, 2, 3, 4, 5, 6],
    y_values=[[10, 25, 18, 30, 22, 35], [5, 15, 12, 20, 18, 28]],
    labels=['Series A', 'Series B'],
    title='Monthly Trends',
    subtitle='Jan-Jun 2026',
    show_gridlines=True,
    show_legend=True,
    show_points=True,
)
export_webp(frames, 'trends.webp', quality=85)
```

---

## Standalone Effects

Each effect is also available as a standalone function that takes a PIL `Image` and returns a new `Image`. Use these when you need a single effect without the pipeline wrapper.

```python
from ideamaxfx.effects import grain, vignette, bloom

img = grain(img, intensity=0.05)
img = bloom(img, threshold=190, radius=12, intensity=0.3)
img = vignette(img, strength=0.25)
img.save("output.png")
```

Additional standalone functions not exposed on the pipeline:

| Function | Module | Description |
|----------|--------|-------------|
| `glow_border(img, color, width, radius)` | `effects` | Glowing border around image edges |
| `blue_noise(width, height)` | `effects` | Generate blue noise dither pattern |
| `pattern_overlay(img, pattern, opacity)` | `effects` | Tile a pattern over an image |
| `blend(base, overlay, mode, opacity)` | `effects` | Photoshop-style blend modes |

---

## Color Utilities

The `color` module provides conversion, harmony, palette extraction, and accessibility checking.

```python
from ideamaxfx.color import hex_to_rgb, complementary, contrast_ratio, wcag_check

rgb = hex_to_rgb("#d4213d")                    # (212, 33, 61)
comp = complementary(rgb)                       # complementary hue
ratio = contrast_ratio((255, 255, 255), rgb)    # WCAG contrast ratio
passes = wcag_check((255, 255, 255), rgb)       # AA/AAA compliance dict
```

---

## Requirements

**Core** (installed automatically):

| Package | Version |
|---------|---------|
| Python | >= 3.9 |
| Pillow | >= 10.0 |
| numpy | >= 1.24 |
| imageio | >= 2.31 |

**Optional** (install via `pip install ideamaxfx[full]`):

| Package | Version | Purpose | Extra |
|---------|---------|---------|-------|
| matplotlib | >= 3.7 | Chart rendering backends | `[full]` |
| scipy | >= 1.10 | Advanced interpolation and filters | `[full]` |
| imageio-ffmpeg | >= 0.4.9 | MP4 video export | `[video]`, `[full]` |

**Optional system tool:**

| Tool | Purpose |
|------|---------|
| [gifsicle](https://www.lcdf.org/gifsicle/) | GIF optimization (auto-detected at export time) |

---

## Development

```bash
git clone https://github.com/devideamax/ideamaxfx.git
cd ideamaxfx
pip install -e ".[dev]"
pytest tests/
ruff check src/
```

The `[dev]` extra installs `pytest`, `pytest-cov`, `ruff`, and `mypy`.

Run the type checker:

```bash
mypy src/
```

---

## Contributing

1. Fork the repository.
2. Create a feature branch from `main`.
3. Add tests for new functionality.
4. Ensure `pytest tests/` and `ruff check src/` pass.
5. Open a pull request.

---

## License

MIT License. Copyright (c) 2026 [IDEAMAX](https://ideamax.eu).

See [LICENSE](LICENSE) for the full text.

---

## Links

- **PyPI:** [pypi.org/project/ideamaxfx](https://pypi.org/project/ideamaxfx/)
- **GitHub:** [github.com/devideamax/ideamaxfx](https://github.com/devideamax/ideamaxfx)
- **Changelog:** [CHANGELOG.md](./CHANGELOG.md)
- **Company:** [ideamax.eu](https://ideamax.eu) — Web Development & SEO
- **Author:** [biko.bg](https://biko.bg)
