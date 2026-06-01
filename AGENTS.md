# Repository Guidelines

This file gives coding agents project-specific context. Human-facing usage docs are at https://auscope.github.io/AuScope-Cat/.

## Project Structure & Module Organization

`src/auscopecat/` contains the Python package. Key modules are `api.py`, `network.py`, `analytics.py`, `nvcl.py`, and `auscopecat_types.py`. Tests live in `tests/`, with helpers in `tests/helpers.py`. Sphinx docs are under `docs/source/`. Example notebooks are in `jupyter-notebooks/`. QGIS plugin code is isolated in `QGIS-Plugin/auscopecatQGIS/`.

## Package Usage Notes

The import package is `auscopecat`; source code lives in `src/auscopecat/`. NVCL and TSG functionality is in `src/auscopecat/nvcl.py`; 

Common imports:

- `from auscopecat.api import search, download, search_records`
- `from auscopecat.auscopecat_types import ServiceType, DownloadType`
- `from auscopecat.nvcl import search_tsg, download_tsg`

If an import is unclear, inspect `pyproject.toml`, `src/auscopecat/__init__.py`, and the relevant module first.

## Build, Test, and Development Commands

- `uv sync --all-extras --dev`: install package and dev dependencies.
- `uv run pytest`: run the test suite.
- `uv run pytest --cov=src --cov-report=term`: run tests with coverage, matching CI coverage scope.
- `uv run ruff check .`: lint Python code.
- `uv run ruff check . --fix`: apply safe Ruff fixes.
- `cd docs && make html`: build Sphinx docs into `docs/build/html`.

Install pre-commit hooks with `uv run pre-commit install` before opening a pull request.

## Coding Style & Naming Conventions

Use Python 3.10+ features while preserving versions listed in `pyproject.toml`. Ruff enforces a Black-compatible style: 4-space indentation, 88-character lines, double quotes, sorted imports, pycodestyle, Pyflakes, warnings, and naming checks. Prefer snake_case for functions, variables, and modules; use PascalCase for classes and enums. Document user-facing `api.py` changes in `docs/source/api_reference/`.

## Testing Guidelines

Tests use `pytest`, `pytest-mock`, and `pytest-cov`. Place tests in `tests/test_<module>.py` and name functions `test_<behavior>`. Reuse `tests/helpers.py` for shared fixtures or sample responses. Mock HTTP calls instead of depending on live services. Update coverage when changing search, download, parsing, or NVCL behavior.

## Commit & Pull Request Guidelines

Recent commits commonly use an issue key plus imperative summary, for example `AUS-4502 Update README with citation`. Pull requests should include a brief description, linked issue when available, test evidence such as `uv run pytest`, and docs or notebook updates for user-visible behavior.

## Security & Configuration Tips

Do not commit credentials, API tokens, downloaded datasets, virtual environments, coverage HTML, or generated docs. Keep dependency changes synchronized with `uv.lock`. Treat catalogue responses as external input and validate fields before assuming shape.
