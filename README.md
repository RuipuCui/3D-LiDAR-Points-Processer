# 3D LiDAR Points Processor

This project is currently at the first step: reading LiDAR point-cloud data from Parquet files.

The provided data files contain 3D points with these columns:

```text
x, y, z
```

Each row represents one point in the LiDAR point cloud.

## Requirements

Use Python 3 and install the required packages:

```bash
pip install pandas pyarrow
```

`pandas` is used to work with table data.

`pyarrow` is used by pandas to read `.parquet` files.

## How To Run

From the project folder:

```bash
cd /Users/nolancui/3D-LiDAR-Points-Processer
python3 read_data.py
```

The script currently reads:

```text
lidar_cable_points_easy.parquet
```

It prints the first few rows and the total number of rows.

Example output:

```text
          x          y          z
0  6.196634 -13.157755  10.582272
...
Rows: 1502
```

## Current Code

The main file is:

```text
read_data.py
```

It contains:

```python
read_lidar_parquet(file_path)
```

This function:

1. Reads a Parquet file.
2. Checks that the file contains `x`, `y`, and `z` columns.
3. Returns the data as a pandas DataFrame.

## Available Data Files

```text
lidar_cable_points_easy.parquet
lidar_cable_points_medium.parquet
lidar_cable_points_hard.parquet
lidar_cable_points_extrahard.parquet
```

To read a different file, change this line in `read_data.py`:

```python
point_cloud = read_lidar_parquet("lidar_cable_points_easy.parquet")
```

For example:

```python
point_cloud = read_lidar_parquet("lidar_cable_points_medium.parquet")
```

