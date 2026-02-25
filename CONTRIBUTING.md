# Contributing to ideamaxfx

Thank you for your interest in contributing to ideamaxfx. This document provides guidelines and information for contributors.

## Development Setup

```bash
git clone https://github.com/devideamax/ideamaxfx.git
cd ideamaxfx
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

## Code Standards

### Style

- **Linter**: ruff (line length 100, target Python 3.9)
- **Type annotations**: PEP 484 on all public function signatures
- **Docstrings**: Google style on all public functions
- **Imports**: Use `from __future__ import annotations` in every module

Run before committing:

```bash
ruff check src/
ruff format src/
```

### Architecture Rules

1. **All effect functions** accept `PIL.Image.Image` and return `PIL.Image.Image`. Never mutate the input.
2. **Core dependencies** are Pillow, numpy, and imageio only. Do not add new required dependencies.
3. **Optional dependencies** (matplotlib, scipy) must be guarded with try/except or TYPE_CHECKING imports.
4. **No side effects on import.** Modules must not execute code, open files, or print on import.

### Testing

```bash
pytest tests/ -v
pytest tests/ --cov=ideamaxfx --cov-report=term-missing
```

Requirements:
- All new public functions must have tests
- Maintain 80%+ coverage on effects and animate modules
- Tests must be fast (use small images, short durations)
- Use fixtures from `tests/conftest.py`

## Pull Request Process

1. Fork the repository and create a feature branch from `main`
2. Write code following the standards above
3. Add or update tests for your changes
4. Ensure all tests pass and ruff reports no errors
5. Update CHANGELOG.md under an `## Unreleased` section
6. Submit a pull request with a clear description of the change

### PR Title Convention

```
feat: add glitch effect to effects module
fix: correct vignette alpha blending on RGBA input
docs: add radar_sweep usage example
test: add coverage for layout module
refactor: simplify blend mode numpy operations
```

## Adding a New Effect

1. Create `src/ideamaxfx/effects/your_effect.py`
2. Function signature: `def your_effect(img: Image.Image, ...) -> Image.Image`
3. Add Google-style docstring with Args, Returns sections
4. Export from `effects/__init__.py`
5. Add a method to `EffectsPipeline` in `effects/pipeline.py`
6. Write tests in `tests/test_effects.py`
7. Add a before/after example in `examples/gallery_generator.py`

## Adding a New Animation Type

1. Create `src/ideamaxfx/animate/your_anim.py`
2. Use `generate_frames()` from `animate/core.py` as the base loop
3. Accept `fps`, `duration`, `hold_seconds`, `easing` parameters
4. Return `list[Image.Image]`
5. Export from `animate/__init__.py`
6. Write tests in `tests/test_animate.py`

## Reporting Issues

When reporting bugs, please include:
- Python version and OS
- ideamaxfx version (`python -c "import ideamaxfx; print(ideamaxfx.__version__)"`)
- Minimal reproducible example
- Full traceback

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
