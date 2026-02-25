# Changelog

## 0.1.1 (2026-02-25)

### Added
- **WebP export** — `export_webp()` for 24-bit animated WebP (no 256-color limit). Pillow-native, zero new dependencies.
- **MP4 export** — `export_mp4()` for video output. Requires optional `imageio-ffmpeg` (`pip install ideamaxfx[video]`).
- **Shared chart infrastructure** — new internal `chart_utils` module with reusable drawing utilities.
- **Y-axis with formatted numbers** on bar, line, scatter charts (K/M suffix for large values).
- **X-axis with formatted numbers** on line, scatter charts.
- **Horizontal gridlines** on bar, line, scatter charts (`show_gridlines` param).
- **Dynamic margins** — all charts auto-adjust margins based on actual label widths.
- **Legend support** — line chart (multi-series), pie chart (right or bottom position).
- **Title + subtitle** support on all chart types.
- **Pie chart percentages** — `show_percentages=True` displays "45%" on each sector.
- **Pie label fade-in** — labels fade from progress 0.5 instead of popping at 0.8.
- **Heatmap color bar** — vertical gradient legend showing min→max value mapping.
- **Heatmap auto-contrast** — light text on dark cells, dark text on light cells (luminance check).
- **Radar ring values** — numbers on grid rings (e.g. "25", "50", "75", "100").
- **Counter thousands separator** — `$1,500,000` instead of `$1500000`.
- **Network edge weight labels** — optional weight display at edge midpoints.
- **D3 Category10 palette** — 10-color professional palette replaces the old 6-8 color defaults.
- **UnsharpMask sharpening** — `finalize_frame()` applies LANCZOS downscale + sharpening for crisp text.
- New optional dependency group: `video = ["imageio-ffmpeg>=0.4.9"]`.
- New test file `tests/test_chart_utils.py` with 25 utility tests.
- Backward compatibility tests for all chart types.

### Changed
- All charts now use `chart_utils._SS` as single supersampling constant (removed per-file `_SS`).
- Bar gap proportions: 40% of slot width (previously fixed `bar_gap=8*S`).
- Scatter default point size reduced from 6.0 to 4.0.
- Radar grid color brightened from `(50,50,60)` to `(68,68,68)` for better visibility.
- `[full]` optional dependency now includes `imageio-ffmpeg`.

### Fixed
- Unused variable `palette` in `export_gif` fallback path.

## 0.1.0 (2026-02-25)

### Added
- Initial release
- Post-production effects pipeline (grain, glow, halftone, scanlines, glass, duotone, vignette, chromatic, bloom, noise, patterns, blend)
- Animated chart build-up (bar, line, radar, scatter, counter, pie, heatmap, network, morph)
- Text effects (gradient, neon, outline, shadow, emboss)
- Layout components (stat card, progress bar, badge, legend, divider, callout)
- Color utilities (convert, palette, harmonies, adjust, interpolate, accessibility)
- Image composition (rounded, shadow, reflection, tilt shift, pixelate, overlay)
- Texture generators (perlin, grid, stripes, dots)
- Watermark tools (text mark, image mark, footer)
- GIF/APNG export with optimization
- 15 easing functions
