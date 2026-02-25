---
name: sportviz-engine
description: Production-grade data visualization engine. Generates ESPN/CNN/Bloomberg-quality static charts (PNG), animated GIFs, SVG diagrams, and interactive HTML infographics. Includes ideamaxfx - an open-source Python library for post-production effects and animated chart build-up. Use for any visual content creation involving charts, data, or infographics.
---

# Sports Visualization Engine - Claude Code Reference

---

## SECTION 1: ENVIRONMENT SETUP

Run once at project start:

```bash
pip install \
  matplotlib seaborn numpy scipy pandas \
  mplsoccer squarify networkx \
  plotly kaleido \
  plotnine pywaffle wordcloud \
  python-ternary \
  pillow imageio \
  svgwrite drawsvg \
  bokeh altair \
  pygal cairosvg \
  geopandas shapely contextily folium \
  manim moviepy \
  opencv-python-headless scikit-image \
  pycairo \
  matplotlib-venn upsetplot \
  adjustText bezier mplcyberpunk \
  --break-system-packages -q

apt-get install -y gifsicle graphviz fonts-dejavu-core
```

---

## SECTION 2: LIBRARY REFERENCE

You know these libraries. This section only maps WHAT each one is for so you pick the right tool.

### Chart Libraries
| Library | Use For |
|---------|---------|
| **matplotlib** | Everything. Polar, 3D, custom patches, path effects, GridSpec, FuncAnimation. Base layer for 80% of charts. |
| **seaborn** | Statistical: heatmap, violin, pair plot, KDE, joint plot, box plot. Better defaults than raw matplotlib. |
| **mplsoccer** | Football-specific: Pitch, VerticalPitch, PyPizza, Bumpy. Shot maps, pass networks, heatmaps on pitch. |
| **plotly** | Interactive HTML: scatter3d, sunburst, treemap, funnel, sankey, parallel_coordinates, choropleth, indicator. `fig.write_html()` for self-contained output. |
| **plotnine** | ggplot2 grammar for Python. Faceted plots, declarative syntax. Quick exploration. |
| **bokeh** | Interactive HTML without heavy JS. Linked brushing, streaming. `save(p)` for self-contained HTML. |
| **altair** | Declarative via Vega-Lite. Concise syntax. `chart.save('out.html')`. |
| **pygal** | SVG charts with built-in hover tooltips. No JS dependency. `chart.render_to_file('out.svg')`. |
| **squarify** | Treemap rectangle layouts. |
| **networkx** | Graph/network: pass networks, formations, tactical connections. |
| **python-ternary** | Triangle plots. Three axes summing to 100%. |
| **pywaffle** | Waffle charts (unit grids). |
| **wordcloud** | Word clouds from frequency dicts. |
| **matplotlib-venn** | Venn diagrams (2-3 sets). |
| **upsetplot** | UpSet plots for 4+ set intersections (modern Venn). |
| **mplcyberpunk** | Glow + underglow on matplotlib lines. Limited scope. |
| **adjustText** | Auto-reposition text labels to avoid overlap on scatter plots. |

### Geographic
| Library | Use For |
|---------|---------|
| **geopandas** | Read/plot GeoJSON, shapefiles. Choropleth. `.plot(column='val', cmap='YlOrRd')`. |
| **shapely** | Geometric ops: buffer, intersection, convex hull. Player zone calculations. |
| **contextily** | Real map tiles (OSM, CartoDB) as basemap behind geopandas plots. |
| **folium** | Interactive Leaflet maps in HTML. `m.save('map.html')`. |

### Animation
| Library | Use For |
|---------|---------|
| **matplotlib.animation** | `FuncAnimation` - animate any matplotlib chart frame-by-frame. Export GIF/MP4. |
| **manim** | Cinematic 3Blue1Brown-style animations. Morphing, camera, reveals. Video output. |
| **moviepy** | Video editing: concatenate clips, transitions, text overlays. |
| **imageio** | Read/write GIF/APNG frames. Lower level than FuncAnimation. |
| **PIL/Pillow** | Frame-by-frame GIF with full pixel control + custom easing. |

### Image Processing
| Library | Use For |
|---------|---------|
| **PIL/Pillow** | Drawing, text, filters, blend modes, composition, channel manipulation. |
| **OpenCV** | Perspective transforms, edge detection, morphology, AR overlays. |
| **scikit-image** | Noise, thresholding, geometric transforms, ridge detection. |
| **pycairo** | Professional 2D vector rendering. Smoother curves/text than PIL. PDF/SVG/PNG output. |

### SVG Generation
| Library | Use For |
|---------|---------|
| **svgwrite** | Programmatic SVG creation. Responsive web diagrams. |
| **drawsvg** | Higher-level SVG with CSS/SMIL animations built in. |
| **cairosvg** | Convert SVG to PNG/PDF at any resolution. |

---

## SECTION 3: CHART TYPE DECISION TREE

67 chart types total. Use this tree to pick the right one.

```
WHAT DO YOU NEED TO SHOW?
|
+-- ONE NUMBER (KPI, %) ----------> Gauge/Arc, Isotype
|
+-- RANKING (ordered list) --------> Lollipop, Radial Bar, Cleveland Dot Plot
|
+-- COMPARISON (A vs B)
|   +-- 2 entities, many metrics --> Dumbbell, Grouped Bar, Radar
|   +-- Before vs After -----------> Slope, Butterfly/Population Pyramid
|   +-- vs Target -----------------> Bullet Chart
|
+-- TIME SERIES
|   +-- One entity, trend ---------> Step Chart, Line+area, Connected Scatterplot
|   +-- Many entities ranking -----> Bump Chart
|   +-- Many entities compact -----> Small Multiples, Sparklines Grid, Horizon Chart
|   +-- Cumulative layers ---------> Stacked Area, Waterfall
|   +-- Calendar view -------------> Calendar Heatmap
|   +-- Duration/availability -----> Gantt Chart
|   +-- Volatility ----------------> Candlestick/OHLC
|
+-- DISTRIBUTION
|   +-- Shape comparison ----------> Violin, Ridgeline/Joy Plot
|   +-- Individual points ---------> Beeswarm, Raincloud (violin+box+strip)
|   +-- Summary stats -------------> Box Plot
|   +-- Spatial density -----------> Hexbin, Contour/Topographic, Heatmap on pitch
|   +-- Correlation ---------------> Scatter+annotations, Pair Plot, Correlation Matrix
|   +-- Three-way proportion ------> Ternary Plot
|
+-- PROPORTION
|   +-- Simple parts --------------> Donut, Waffle
|   +-- Hierarchical --------------> Sunburst (nested pie), Treemap
|   +-- Two dimensions ------------> Marimekko/Mosaic
|   +-- Pictorial -----------------> Isotype (each icon = 1 unit)
|   +-- Nested circles ------------> Circular Packing
|   +-- Circular layout -----------> Radial Bar, Polar Bar
|
+-- FLOW / CONNECTION
|   +-- Between positions ---------> Chord Diagram, Network Graph, Arc Diagram
|   +-- Sequential funnel ---------> Funnel, Sankey
|   +-- Categorical transition ----> Alluvial Diagram
|   +-- On pitch ------------------> Pass Network (mplsoccer), Streamplot
|   +-- Directional field ---------> Quiver/Vector Field
|
+-- SPATIAL (football pitch)
|   +-- Shots --------------------> Shot Map (mplsoccer VerticalPitch)
|   +-- Player positions ---------> Heatmap (mplsoccer + gaussian_filter)
|   +-- Pass connections ---------> Pass Network (mplsoccer Pitch)
|   +-- Pressure/threat ----------> Contour, Quiver, Streamplot
|
+-- PLAYER PROFILE
|   +-- Percentile ranks ---------> Pizza Chart (mplsoccer PyPizza)
|   +-- Multi-attribute ----------> Radar
|   +-- Over time ----------------> Bumpy Chart (mplsoccer Bumpy)
|   +-- vs Peers -----------------> Beeswarm with highlighted player
|
+-- CLUSTERING / SIMILARITY
|   +-- Hierarchical -------------> Dendrogram (scipy)
|   +-- Set overlaps -------------> Venn, UpSet Plot
|   +-- Multi-dimensional --------> Parallel Coordinates
|
+-- TEXT / KEYWORDS --------------> Word Cloud
|
+-- GEOGRAPHIC
|   +-- Region shading -----------> Choropleth (geopandas)
|   +-- Point locations ----------> Point Map (geopandas+contextily), Folium
|   +-- Newsroom/military style --> PIL Custom Map (glow borders, stat boxes)
```

---

## SECTION 4: CUSTOM TECHNIQUES

These are patterns NOT in any library documentation. Standard matplotlib/seaborn/plotly usage is not included here - you already know those APIs.

### 4.1 Beeswarm - Manual No-Overlap Algorithm
```python
sorted_vals = np.sort(values)
y_offsets = np.zeros(len(sorted_vals))
for j in range(1, len(sorted_vals)):
    for k in range(j):
        if abs(sorted_vals[j] - sorted_vals[k]) < threshold:
            y_offsets[j] = max(y_offsets[j], y_offsets[k] + step)
y_offsets -= y_offsets.max() / 2
ax.scatter(sorted_vals, category_y + y_offsets, s=25)
```

### 4.2 Chord Diagram - Custom Bezier Through Center
```python
# Outer arcs proportional to total flow
angles = np.cumsum(totals / totals.sum() * 360)
angles = np.insert(angles, 0, 0)
for i in range(n):
    theta1 = np.radians(90 - angles[i])
    theta2 = np.radians(90 - angles[i+1])
    arc_pts = np.linspace(theta1, theta2, 50)
    x_out = radius * np.cos(arc_pts); y_out = radius * np.sin(arc_pts)
    x_in = inner_r * np.cos(arc_pts); y_in = inner_r * np.sin(arc_pts)
    verts = list(zip(x_out, y_out)) + list(zip(x_in[::-1], y_in[::-1]))
    ax.add_patch(plt.Polygon(verts, facecolor=colors[i], alpha=0.85))
# Inner chords: quadratic bezier through (0,0)
for src, dst, weight in connections:
    mid_s = np.radians(90 - (angles[src] + angles[src+1])/2)
    mid_d = np.radians(90 - (angles[dst] + angles[dst+1])/2)
    x1, y1 = inner_r * np.cos(mid_s), inner_r * np.sin(mid_s)
    x2, y2 = inner_r * np.cos(mid_d), inner_r * np.sin(mid_d)
    path = Path([(x1,y1), (0,0), (x2,y2)], [Path.MOVETO, Path.CURVE3, Path.CURVE3])
    ax.add_patch(mpatches.PathPatch(path, facecolor='none', edgecolor=color,
                linewidth=1+4*(weight/max_w), alpha=0.1+0.5*(weight/max_w)))
```

### 4.3 PIL Glow Border - Multi-Pass (CNN/Military Map Style)
```python
def glow_border(img, points, color=(0, 245, 212),
                passes=[(12, 15), (8, 30), (5, 50), (3, 80), (2, 200)]):
    base = img.convert('RGBA')
    for line_width, alpha in passes:
        layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]], fill=(*color, alpha), width=line_width)
        base = Image.alpha_composite(base, layer)
    return base.convert('RGB')
```

### 4.4 PIL Glassmorphism Card
```python
def glass_card(img, x, y, w, h, blur=15, tint=(20, 25, 40, 160)):
    region = img.crop((x, y, x+w, y+h))
    blurred = region.filter(ImageFilter.GaussianBlur(radius=blur))
    tint_layer = Image.new('RGBA', (w, h), tint)
    result = Image.alpha_composite(blurred.convert('RGBA'), tint_layer)
    border_draw = ImageDraw.Draw(result)
    border_draw.rounded_rectangle([0, 0, w-1, h-1], radius=12,
                                   outline=(255, 255, 255, 60), width=1)
    border_draw.line([(12, 1), (w-12, 1)], fill=(255, 255, 255, 25), width=1)
    img.paste(result.convert('RGB'), (x, y))
    return img
```

### 4.5 PIL Gradient Text (CSS background-clip equivalent)
```python
def gradient_text(img, x, y, text, font, color_start, color_end, direction='horizontal'):
    # 1. Draw text as white on black mask
    mask = Image.new('L', img.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.text((x, y), text, fill=255, font=font)
    bbox = mask.getbbox()
    if not bbox: return img
    # 2. Create gradient image
    gw, gh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    gradient = Image.new('RGB', img.size, (0, 0, 0))
    grad_draw = ImageDraw.Draw(gradient)
    for i in range(gw if direction == 'horizontal' else gh):
        t = i / max(1, (gw if direction == 'horizontal' else gh) - 1)
        r = int(color_start[0] + (color_end[0] - color_start[0]) * t)
        g = int(color_start[1] + (color_end[1] - color_start[1]) * t)
        b = int(color_start[2] + (color_end[2] - color_start[2]) * t)
        if direction == 'horizontal':
            grad_draw.line([(bbox[0]+i, bbox[1]), (bbox[0]+i, bbox[3])], fill=(r, g, b))
        else:
            grad_draw.line([(bbox[0], bbox[1]+i), (bbox[2], bbox[1]+i)], fill=(r, g, b))
    # 3. Composite: gradient visible only where text mask is white
    return Image.composite(gradient, img, mask)
```

### 4.6 PIL Neon Text
```python
def neon_text(img, x, y, text, font, color, passes=5, spread=2.0):
    base = img.convert('RGBA')
    for i in range(passes, 0, -1):
        layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        alpha = int(20 + 40 * (passes - i) / passes)
        d.text((x, y), text, fill=(*color, alpha), font=font)
        layer = layer.filter(ImageFilter.GaussianBlur(radius=i * spread))
        base = Image.alpha_composite(base, layer)
    # Sharp text on top
    d = ImageDraw.Draw(base)
    d.text((x, y), text, fill=(*color, 255), font=font)
    return base.convert('RGB')
```

### 4.7 matplotlib Figure to PIL Image
```python
import io
def mpl_to_pil(fig, dpi=150):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                facecolor=fig.get_facecolor(), edgecolor='none', pad_inches=0.3)
    buf.seek(0)
    return Image.open(buf).convert('RGB')
```

---

## SECTION 5: THE ideamaxfx LIBRARY

GitHub: `github.com/devideamax/ideamaxfx`
PyPI: `pip install ideamaxfx`
License: MIT

This is an open-source library that does NOT exist elsewhere. Two core capabilities + extended visual toolkit.

### 5.1 What It Does

**A. Post-Production Effects Pipeline** - takes any PIL Image (from matplotlib, seaborn, plotly, PIL, photo, anything) and applies cinematic finishing effects. Chainable API.

**B. Animated Build-Up** - takes chart data and generates animated GIF/APNG where elements appear progressively with easing functions.

**C. Visual Toolkit** - text effects, layout components, color utilities, image composition, texture generators, watermark/branding tools that PIL should have but doesn't.

### 5.2 Package Structure

```
ideamaxfx/
├── pyproject.toml
├── README.md
├── LICENSE                       # MIT
├── CHANGELOG.md
├── src/
│   └── ideamaxfx/
│       ├── __init__.py           # Version, top-level imports
│       ├── py.typed              # PEP 561
│       │
│       ├── effects/              # POST-PRODUCTION EFFECTS
│       │   ├── __init__.py
│       │   ├── grain.py          # Film grain / noise texture
│       │   ├── glow.py           # Neon glow on bright areas + glow borders
│       │   ├── halftone.py       # Print-style dot pattern
│       │   ├── scanlines.py      # CRT / broadcast horizontal lines
│       │   ├── glass.py          # Glassmorphism frosted card
│       │   ├── duotone.py        # Two-color image remap
│       │   ├── vignette.py       # Darkened edges / corners
│       │   ├── chromatic.py      # RGB channel offset (glitch)
│       │   ├── bloom.py          # Soft bright area bleed
│       │   ├── noise.py          # Perlin noise, blue noise generators
│       │   ├── patterns.py       # Stripe, dot, crosshatch, grid fills
│       │   ├── blend.py          # Screen, multiply, overlay blend modes
│       │   └── pipeline.py       # EffectsPipeline chainable class
│       │
│       ├── animate/              # ANIMATED BUILD-UP
│       │   ├── __init__.py
│       │   ├── easing.py         # 15 easing functions
│       │   ├── core.py           # Base animation loop, frame gen
│       │   ├── bar.py            # Bar chart grow
│       │   ├── line.py           # Line progressive draw
│       │   ├── radar.py          # Radar polygon sweep
│       │   ├── scatter.py        # Scatter point fade-in
│       │   ├── counter.py        # Number counter roll
│       │   ├── pie.py            # Pie/donut sector fill
│       │   ├── heatmap.py        # Cell-by-cell reveal
│       │   ├── network.py        # Nodes then edges build
│       │   ├── morph.py          # Morph between two chart states
│       │   ├── stagger.py        # Staggered delay calculator
│       │   ├── composer.py       # Combine multiple animations
│       │   └── export.py         # GIF/APNG export + gifsicle optimization
│       │
│       ├── text/                 # TEXT EFFECTS
│       │   ├── __init__.py
│       │   ├── gradient.py       # Gradient-filled text
│       │   ├── neon.py           # Neon glow text
│       │   ├── outline.py        # Stroked/outlined text
│       │   ├── shadow.py         # Drop shadow text
│       │   └── emboss.py         # 3D embossed text
│       │
│       ├── layout/               # LAYOUT COMPONENTS
│       │   ├── __init__.py
│       │   ├── stat_card.py      # Number + label + accent bar card
│       │   ├── progress_bar.py   # Horizontal bar with %, optional glow
│       │   ├── badge.py          # Pill-shaped colored label
│       │   ├── legend.py         # Color dot + text legend block
│       │   ├── divider.py        # Gradient-fade divider line
│       │   └── callout.py        # Arrow + text annotation
│       │
│       ├── color/                # COLOR UTILITIES
│       │   ├── __init__.py
│       │   ├── convert.py        # hex/rgb/hsl conversions
│       │   ├── palette.py        # Extract palette from image (k-means)
│       │   ├── harmonies.py      # Complementary, triadic, analogous
│       │   ├── adjust.py         # Darken, lighten, saturate, desaturate
│       │   ├── interpolate.py    # Generate N colors between two colors
│       │   └── accessibility.py  # WCAG contrast check + suggestions
│       │
│       ├── compose/              # IMAGE COMPOSITION
│       │   ├── __init__.py
│       │   ├── rounded.py        # Rounded corners on image
│       │   ├── shadow.py         # Drop shadow behind image
│       │   ├── reflection.py     # Mirror reflection with fade
│       │   ├── tilt_shift.py     # Selective focus (miniature effect)
│       │   ├── pixelate.py       # Mosaic / pixelation of region
│       │   └── overlay.py        # Color overlay with blend mode
│       │
│       ├── texture/              # TEXTURE GENERATORS
│       │   ├── __init__.py
│       │   ├── perlin.py         # Perlin noise (pure numpy)
│       │   ├── grid.py           # Grid pattern (dots, lines, crosses)
│       │   ├── stripes.py        # Diagonal/horizontal/vertical stripes
│       │   └── dots.py           # Polka dot pattern
│       │
│       ├── watermark/            # WATERMARK & BRANDING
│       │   ├── __init__.py
│       │   ├── text_mark.py      # Semi-transparent diagonal text
│       │   ├── image_mark.py     # Logo overlay with alpha
│       │   └── footer.py         # Footer bar with logo + text + line
│       │
│       └── utils/
│           ├── __init__.py
│           ├── convert.py        # mpl_to_pil, numpy_to_pil, pil_to_numpy
│           └── fonts.py          # PIL font loading with system fallbacks
│
├── tests/
│   ├── test_effects.py
│   ├── test_animate.py
│   ├── test_text.py
│   ├── test_color.py
│   └── conftest.py
│
└── examples/
    ├── basic_effects.py
    ├── animated_bar.py
    ├── text_showcase.py
    ├── full_pipeline.py
    └── gallery_generator.py
```

### 5.3 pyproject.toml

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "ideamaxfx"
version = "0.1.0"
description = "Post-production effects, animated build-up, and visual toolkit for data visualizations"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.9"
authors = [{name = "IDEAMAX", email = "info@ideamax.eu"}]
keywords = ["visualization", "data-viz", "effects", "animation", "charts", "post-production", "pillow"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering :: Visualization",
    "Topic :: Multimedia :: Graphics",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Typing :: Typed",
]
dependencies = [
    "Pillow>=10.0",
    "numpy>=1.24",
    "imageio>=2.31",
]

[project.optional-dependencies]
matplotlib = ["matplotlib>=3.7"]
full = ["matplotlib>=3.7", "scipy>=1.10"]
dev = ["pytest>=7.0", "pytest-cov", "ruff", "mypy"]

[project.urls]
Homepage = "https://github.com/devideamax/ideamaxfx"
Documentation = "https://ideamaxfx.readthedocs.io"
Repository = "https://github.com/devideamax/ideamaxfx"
Changelog = "https://github.com/devideamax/ideamaxfx/blob/main/CHANGELOG.md"

[tool.setuptools.packages.find]
where = ["src"]

[tool.ruff]
line-length = 100
target-version = "py39"

[tool.mypy]
python_version = "3.9"
strict = true
```

### 5.4 Core Dependencies

| Package | Version | Why |
|---------|---------|-----|
| Pillow | >=10.0 | All effects, text, composition, frame generation |
| numpy | >=1.24 | Noise arrays, pixel math, color interpolation |
| imageio | >=2.31 | GIF/APNG frame writing |

matplotlib is NOT required. The library works with any PIL Image from any source.

### 5.5 Easing Functions (animate/easing.py)

All take t (0.0-1.0) and return eased value (0.0-1.0):

```python
linear, ease_in_quad, ease_out_quad, ease_in_out_quad,
ease_in_cubic, ease_out_cubic, ease_in_out_cubic,
ease_in_quart, ease_out_quart, ease_in_out_quart,
ease_out_elastic, ease_out_bounce, ease_out_back,
ease_in_expo, ease_out_expo
```

### 5.6 GIF Export with Optimization (animate/export.py)

```python
def frames_to_gif(frames, output_path, fps=15, max_colors=128, max_size_kb=500, lossy=40):
    raw_path = output_path.replace('.gif', '_raw.gif')
    imageio.mimsave(raw_path, [np.array(f) for f in frames], fps=fps, loop=0)
    subprocess.run(['gifsicle', '-O3', f'--lossy={lossy}', f'--colors={max_colors}',
                    '-o', output_path, raw_path], check=True)
    size_kb = os.path.getsize(output_path) / 1024
    if size_kb > max_size_kb:
        subprocess.run(['gifsicle', '-O3', '--lossy=80', '--colors=64',
                        '-o', output_path, raw_path], check=True)
    os.remove(raw_path)
    return output_path
```

---

## SECTION 6: QUALITY STANDARDS

- Line width >= 2px (thin lines = amateur)
- Font size >= 10px for labels, >= 14px for titles
- Color contrast >= 3:1 for text on background
- Dark themes: use #0a0e17 or #0d1117, NEVER pure #000000
- Light themes: use #f8fafc or #faf7f2, NEVER pure #ffffff
- Always cite data sources in footer (10-11px, muted color)
- GIF: gifsicle -O3 optimized, under 500KB, 10-15 fps
- PNG: 150 DPI minimum, 1200px+ wide
- EVERY number in a visualization must come from user input or web search. NEVER invent statistics.
- If data is uncertain, use placeholder: "INSERT DATA"

---

## SECTION 7: EXECUTION CHECKLIST

When asked to create a visualization:

1. **Identify chart type** from decision tree (Section 3)
2. **Gather data** - ask user or search. Never invent.
3. **Generate chart** with appropriate library
4. **Apply post-production** via ideamaxfx EffectsPipeline (if available) or manual PIL effects from Section 4
5. **If GIF requested:** generate animated build-up, optimize with gifsicle
6. **Export** at correct resolution with source attribution

---

## SECTION 8: FIRST TASK FOR CLAUDE CODE

Build the `ideamaxfx` package as specified in Section 5. All code must be:

- Type-annotated (PEP 484)
- Documented (Google-style docstrings)
- Tested (pytest, minimum 80% coverage on effects and animate modules)
- Linted (ruff)
- pip-installable: `pip install ./ideamaxfx`

After building, generate a visual gallery:
- Before/after for each effect (10 pairs)
- Sample GIF for each animation type (8 GIFs)
- Text effect showcase (5 examples)
- Include all gallery images in README.md

The library must work with this minimal example:

```python
from ideamaxfx import EffectsPipeline
from ideamaxfx.animate import bar_grow, export_gif
from ideamaxfx.text import gradient_text, neon_text
from ideamaxfx.color import hex_to_rgb, interpolate_colors

# Post-production
from PIL import Image
img = Image.open("my_chart.png")
result = (EffectsPipeline(img)
          .grain(0.06)
          .glow(color=(0, 245, 212))
          .scanlines(spacing=4)
          .vignette(0.3)
          .export("finished.png"))

# Animation
frames = bar_grow(
    labels=['A', 'B', 'C'],
    values=[68, 72, 45],
    colors=['#d4213d', '#006633', '#0056a0'],
    fps=15, duration=2.0, hold_seconds=2,
    easing='ease_out_elastic'
)
export_gif(frames, 'animated.gif', max_kb=500)
```
