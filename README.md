# 3D LiDAR Points Processor

This project is currently in the early data-understanding stage:

1. Read LiDAR point-cloud data from Parquet files.
2. Print basic data summaries.
3. Save a simple 3D plot of the point cloud.
4. Cluster points into likely wire groups.
5. Fit catenary curves to clustered wires.

The provided data files contain 3D points with these columns:

```text
x, y, z
```

Each row represents one point in the LiDAR point cloud.

## Requirements

Use Python 3 and install the required packages:

```bash
pip install pandas pyarrow matplotlib scikit-learn scipy
```

`pandas` is used to work with table data.

`pyarrow` is used by pandas to read `.parquet` files.

`matplotlib` is used to create simple plots.

`scikit-learn` is used for clustering.

`scipy` is used for fitting catenary curves.

## How To Run

Use `main.py` as the single entry point for the project.

From the project folder:

```bash
cd /Users/nolancui/3D-LiDAR-Points-Processer
```

### Read A Parquet File

Run:

```bash
python3 main.py read lidar_cable_points_easy.parquet
```

This prints the first few rows and the total number of rows.

Example output:

```text
          x          y          z
0  6.196634 -13.157755  10.582272
...
Rows: 1502
```

### Explore And Plot A Parquet File

Run:

```bash
python3 main.py explore lidar_cable_points_easy.parquet
```

This will:

1. Print the number of rows.
2. Print the column names.
3. Print summary statistics for `x`, `y`, and `z`.
4. Save a 3D scatter plot.

For the easy file, the plot will be saved as:

```text
explore_images/lidar_cable_points_easy.png
```

You can run the same script with the other files:

```bash
python3 main.py explore lidar_cable_points_medium.parquet
python3 main.py explore lidar_cable_points_hard.parquet
python3 main.py explore lidar_cable_points_extrahard.parquet
```

### Cluster Points Into Wires

Run:

```bash
python3 main.py cluster lidar_cable_points_easy.parquet
```

This will:

1. Estimate a local coordinate system from the 3D points.
2. Use DBSCAN clustering to group nearby points.
3. Print the number of points in each cluster.
4. Save a colored 3D cluster plot.

For the easy file, the cluster plot will be saved as:

```text
cluster_images/lidar_cable_points_easy_clusters.png
```

You can adjust the DBSCAN parameters if the clustering looks wrong:

```bash
python3 main.py cluster lidar_cable_points_easy.parquet --eps 0.4 --min-samples 10
```

`eps` controls how close points must be to belong together. Larger values merge more points into clusters. Smaller values split points into more clusters or mark more points as noise.

### Cluster All Data Files

Run:

```bash
python3 main.py cluster-all
```

This runs clustering for all files matching:

```text
lidar_cable_points_*.parquet
```

It saves:

```text
cluster_images/cluster_summary.csv
```

It also saves one cluster image per input file in the `cluster_images/` folder.

### Fit Catenary Curves

Run:

```bash
python3 main.py fit lidar_cable_points_easy.parquet
```

This will:

1. Cluster the point cloud into likely wires.
2. Fit one catenary curve to each detected cluster.
3. Print the fitted parameters and RMSE error.
4. Save a fit plot and CSV summary.

For the easy file, outputs will be saved as:

```text
fit_images/lidar_cable_points_easy_catenary_fits.png
fit_images/lidar_cable_points_easy_fit_summary.csv
```

## Current Code

The current code files are:

```text
main.py
src/read_data.py
src/explore_data.py
src/cluster_data.py
src/fit_catenary.py
```

`main.py` is the only file you run directly.

`src/read_data.py` contains:

```python
read_lidar_parquet(file_path)
```

This function:

1. Reads a Parquet file.
2. Checks that the file contains `x`, `y`, and `z` columns.
3. Returns the data as a pandas DataFrame.

`src/explore_data.py` adds:

1. Summary statistics.
2. A 3D scatter plot saved in the `explore_images/` folder.

`src/cluster_data.py` adds:

1. PCA-based local coordinates.
2. DBSCAN clustering.
3. A colored 3D cluster plot saved in the `cluster_images/` folder.

`src/fit_catenary.py` adds:

1. Catenary curve fitting for each cluster.
2. RMSE calculation for each fitted curve.
3. Fit plots and CSV summaries saved in the `fit_images/` folder.

## Available Data Files

```text
lidar_cable_points_easy.parquet
lidar_cable_points_medium.parquet
lidar_cable_points_hard.parquet
lidar_cable_points_extrahard.parquet
```

To read a different file, pass a different filename to `main.py`.
