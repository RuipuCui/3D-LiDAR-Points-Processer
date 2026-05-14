# 3D LiDAR Points Processor

Python package for detecting overhead electricity wires in drone LiDAR point clouds and fitting catenary models to each detected wire.

The input files are Parquet tables with 3D point coordinates:

```text
x, y, z
```

Each row is one LiDAR point.

## Project Pipeline

The current implementation follows this pipeline:

1. Read LiDAR point-cloud data from Parquet files.
2. Inspect point counts and coordinate summaries.
3. Visualise the raw 3D point cloud.
4. Transform points into PCA-based local coordinates.
5. Cluster points into likely individual wires using DBSCAN.
6. Fit one catenary curve to each detected wire cluster.
7. Reconstruct fitted catenary curves back into original 3D space.
8. Save plots and CSV summaries.

## Setup

From the project folder:

```bash
cd /Users/nolancui/3D-LiDAR-Points-Processer
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

This installs the package in editable mode and exposes the command:

```bash
lidar-catenary
```

## Usage

### Read Data

```bash
lidar-catenary read lidar_cable_points_easy.parquet
```

Prints the first few rows and row count.

### Explore Data

```bash
lidar-catenary explore lidar_cable_points_easy.parquet
```

Saves a raw 3D point-cloud plot:

```text
explore_images/lidar_cable_points_easy.png
```

### Cluster One File

```bash
lidar-catenary cluster lidar_cable_points_easy.parquet
```

Saves a colored cluster plot:

```text
cluster_images/lidar_cable_points_easy_clusters.png
```

Optional DBSCAN parameters:

```bash
lidar-catenary cluster lidar_cable_points_easy.parquet --eps 0.35 --min-samples 10
```

### Cluster All Files

```bash
lidar-catenary cluster-all
```

Processes all files matching:

```text
lidar_cable_points_*.parquet
```

and saves:

```text
cluster_images/cluster_summary.csv
```

### Fit Catenary Curves For One File

```bash
lidar-catenary fit lidar_cable_points_easy.parquet
```

Saves:

```text
fit_images/lidar_cable_points_easy_catenary_fits.png
fit_images/lidar_cable_points_easy_3d_catenary_fits.png
fit_images/lidar_cable_points_easy_fit_summary.csv
```

### Fit All Files

```bash
lidar-catenary fit-all
```

Fits all files matching `lidar_cable_points_*.parquet` and saves:

```text
fit_images/fit_summary.csv
```

## Local Development Shortcut

After installing dependencies, this also works from the repository root:

```bash
python3 main.py fit lidar_cable_points_easy.parquet
```

`main.py` is a thin wrapper around the package CLI.

## Code Structure

```text
pyproject.toml
main.py
src/
  lidar_catenary/
    cli.py
    read_data.py
    explore_data.py
    cluster_data.py
    fit_catenary.py
```

Key modules:

- `read_data.py`: reads Parquet files and validates `x`, `y`, `z` columns.
- `explore_data.py`: prints summaries and saves raw 3D plots.
- `cluster_data.py`: creates PCA local coordinates and clusters points with DBSCAN.
- `fit_catenary.py`: fits catenary curves, calculates RMSE, and reconstructs fitted curves in 3D.
- `cli.py`: command-line entry point.

## Algorithm Summary

The point cloud is first centered and transformed with PCA/SVD. The first local axis is treated as the dominant wire-span direction. Clustering is then performed on the two remaining local coordinates, which represent cross-section separation between wires.

For each detected cluster, the package fits:

```text
z(s) = z0 + c * [cosh((s - s0) / c) - 1]
```

where:

- `s` is local position along the wire span
- `z` is elevation
- `s0` is the fitted lowest-point position
- `z0` is the fitted lowest height
- `c` controls curvature/sag

The fitted curve is then reconstructed back into original `x, y, z` space for 3D visualisation.

## Data Note

The provided Parquet files and original test document are assessment materials. Check `copyright.txt` before publishing or redistributing the data. A public submission should usually include code and instructions, not private assessment data, unless permission is given.

## Development Checks

```bash
pytest
ruff check .
```
