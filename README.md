# 3D LiDAR Points Processor

This project is currently in the early data-understanding stage:

1. Read LiDAR point-cloud data from Parquet files.
2. Print basic data summaries.
3. Save a simple 3D plot of the point cloud.

The provided data files contain 3D points with these columns:

```text
x, y, z
```

Each row represents one point in the LiDAR point cloud.

## Requirements

Use Python 3 and install the required packages:

```bash
pip install pandas pyarrow matplotlib
```

`pandas` is used to work with table data.

`pyarrow` is used by pandas to read `.parquet` files.

`matplotlib` is used to create simple plots.

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
lidar_cable_points_easy.png
```

You can run the same script with the other files:

```bash
python3 main.py explore lidar_cable_points_medium.parquet
python3 main.py explore lidar_cable_points_hard.parquet
python3 main.py explore lidar_cable_points_extrahard.parquet
```

## Current Code

The current code files are:

```text
main.py
src/read_data.py
src/explore_data.py
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
2. A 3D scatter plot saved as a `.png` file.

## Available Data Files

```text
lidar_cable_points_easy.parquet
lidar_cable_points_medium.parquet
lidar_cable_points_hard.parquet
lidar_cable_points_extrahard.parquet
```

To read a different file, pass a different filename to `main.py`.
