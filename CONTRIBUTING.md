# Contributing

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Checks

Run these before opening a pull request or creating a release:

```bash
pytest
ruff check .
```

## Data Handling

Do not commit private assessment datasets, generated plots, generated CSV summaries, or original assessment documents unless redistribution permission is explicit.

Expected local-only files include:

```text
lidar_cable_points_*.parquet
Python Developer - Technical Test.docx
copyright.txt
```

## Versioning

Use semantic versioning:

- Patch release: bug fixes only, for example `0.1.1`
- Minor release: new backward-compatible features, for example `0.2.0`
- Major release: breaking changes, for example `1.0.0`

Update both:

```text
pyproject.toml
src/lidar_catenary/__init__.py
```

and add a `CHANGELOG.md` entry before tagging a release.

