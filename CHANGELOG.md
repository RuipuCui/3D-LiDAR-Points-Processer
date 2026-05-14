# Changelog

All notable changes to this project are documented here.

This project follows semantic versioning: `MAJOR.MINOR.PATCH`.

## 0.1.0 - 2026-05-14

- Added installable Python package structure under `src/lidar_catenary`.
- Added `lidar-catenary` command-line entry point.
- Added Parquet point-cloud loading with `x`, `y`, `z` validation.
- Added raw point-cloud exploration summaries and 3D plots.
- Added PCA-based local coordinate transformation.
- Added DBSCAN clustering for likely wire groups.
- Added catenary fitting for each detected cluster.
- Added RMSE fit metrics and CSV outputs.
- Added 3D reconstruction plots for fitted catenary curves.
- Added `cluster-all` and `fit-all` batch commands.
- Added basic tests and lint configuration.

