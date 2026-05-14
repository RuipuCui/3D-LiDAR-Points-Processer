# Current Approach And Method

This document explains the current LiDAR wire-detection and catenary-fitting method implemented in this repository.

The project goal is to process drone LiDAR point-cloud files, identify individual overhead wire groups, and fit a catenary model to each detected wire.

## Input Data

The expected input is a Parquet file containing one row per LiDAR point:

```text
x, y, z
```

In this project:

- `x` and `y` describe horizontal/spatial location.
- `z` is treated as height/elevation.
- Each row is one sampled point from the point cloud.

The loader in `src/lidar_catenary/read_data.py` validates that all three required columns exist before returning the data.

## End-To-End Pipeline

The current pipeline is:

```text
Parquet file
    -> read x/y/z points
    -> optionally inspect and plot raw points
    -> create PCA-based local coordinates
    -> cluster points into wire groups with DBSCAN
    -> fit one catenary curve per cluster
    -> reconstruct fitted curves back into 3D
    -> save plots and CSV summaries
```

The main command-line entry point is:

```bash
lidar-catenary
```

The most complete command is:

```bash
lidar-catenary fit-all
```

It runs catenary fitting for all files matching:

```text
lidar_cable_points_*.parquet
```

## Step 1: Read The Point Cloud

Implemented in:

```text
src/lidar_catenary/read_data.py
```

The function:

```python
read_lidar_parquet(file_path)
```

does three things:

1. Reads the Parquet file with pandas.
2. Checks that `x`, `y`, and `z` columns exist.
3. Returns only those columns.

This keeps the rest of the pipeline independent of any extra columns that may appear in future datasets.

## Step 2: Explore The Raw Data

Implemented in:

```text
src/lidar_catenary/explore_data.py
```

The exploration step prints:

- file name
- row count
- column names
- summary statistics for `x`, `y`, and `z`

It also saves a raw 3D scatter plot.

Example:

```bash
lidar-catenary explore lidar_cable_points_easy.parquet
```

Output image:

```text
explore_images/lidar_cable_points_easy.png
```

This is mainly a visual sanity check before clustering.

## Step 3: Create Local Coordinates With PCA

Implemented in:

```text
src/lidar_catenary/cluster_data.py
```

The key function is:

```python
create_local_frame(point_cloud)
```

It converts original `x`, `y`, `z` points into a PCA-based local coordinate system.

### Why Local Coordinates Are Needed

The original axes are arbitrary for this task. A wire may not run along the raw `x` axis or raw `y` axis. It may run diagonally through the scene.

The catenary and clustering steps become easier if we define a local coordinate system where:

- local axis 0 is the dominant wire-span direction
- local axes 1 and 2 describe separation across the wire group

For mostly parallel overhead wires, this is a reasonable approximation.

### How The PCA Frame Is Created

The code first extracts the points:

```python
points = point_cloud[["x", "y", "z"]].to_numpy()
```

Then it computes the point-cloud center:

```python
center = points.mean(axis=0)
```

Then it centers the points:

```python
centered_points = points - center
```

Centering means every point is measured relative to the average point of the cloud.

Then SVD is used:

```python
_, _, directions = np.linalg.svd(centered_points, full_matrices=False)
```

For this project, `directions` contains the PCA axes. Each row is a unit vector in original `x`, `y`, `z` space:

```text
directions[0] = direction of largest spread
directions[1] = direction of second-largest spread
directions[2] = direction of remaining spread
```

For mostly parallel wires, the largest spread is usually along the long wire span.

Finally, points are projected into that coordinate system:

```python
local_points = centered_points @ directions.T
```

The result is:

```text
local_points[:, 0] = coordinate along PCA direction 0
local_points[:, 1] = coordinate along PCA direction 1
local_points[:, 2] = coordinate along PCA direction 2
```

Important distinction:

- `directions` are the axes.
- `local_points` are point coordinates measured on those axes.

So `local_points[:, 0]` is not a direction. It is the position of each point along `directions[0]`.

## Step 4: Cluster Points Into Wire Groups

Implemented in:

```text
src/lidar_catenary/cluster_data.py
```

The main function is:

```python
cluster_point_cloud(point_cloud, eps=0.35, min_samples=10)
```

The current method uses DBSCAN from scikit-learn.

Before clustering, the point cloud is transformed into local PCA coordinates:

```python
local_points = create_local_coordinates(point_cloud)
```

The clustering features are:

```python
clustering_features = local_points[:, 1:3]
```

This uses local columns 1 and 2, while ignoring local column 0.

### Why Ignore Local Column 0

Local column 0 is the estimated position along the wire span.

Two points on the same wire can be far apart along the span:

```text
left end of wire  ----------------  right end of wire
```

They should still belong to the same wire. If clustering used this along-span coordinate, one physical wire could be split into many clusters.

Different parallel wires are usually separated across the span, not along it. That separation is represented better by local columns 1 and 2.

### DBSCAN Parameters

The current defaults are:

```text
eps = 0.35
min_samples = 10
```

`eps` controls the neighborhood radius. Larger values merge more nearby points. Smaller values split clusters more aggressively.

`min_samples` controls how many nearby points are required to form a dense cluster.

DBSCAN labels outliers as:

```text
-1
```

The current datasets produce no noise points with the default parameters, but the code handles `-1` labels.

## Step 5: Fit A Catenary To Each Cluster

Implemented in:

```text
src/lidar_catenary/fit_catenary.py
```

The fitted equation is:

```text
z(s) = z0 + c * [cosh((s - s0) / c) - 1]
```

Where:

- `s` is local position along the estimated wire span.
- `z` is elevation from the original point cloud.
- `s0` is the fitted along-span position of the lowest point.
- `z0` is the fitted lowest elevation.
- `c` is the curvature parameter.

The project document writes the equation as a 2D catenary. This implementation adapts it by using:

```text
s = local along-wire coordinate
z = original elevation
```

For each cluster, the code extracts:

```python
s = local_points[cluster_mask, 0]
z = clustered_data.loc[cluster_mask, "z"].to_numpy()
```

Then it fits the parameters with:

```python
scipy.optimize.least_squares
```

The optimizer minimizes the residual:

```text
predicted z - observed z
```

A robust loss is used:

```python
loss="soft_l1"
```

This reduces the influence of occasional noisy points.

## Step 6: Calculate Fit Quality

For each fitted cluster, the code calculates RMSE:

```text
RMSE = sqrt(mean((predicted_z - observed_z)^2))
```

RMSE measures the typical vertical error between the fitted catenary curve and the observed LiDAR points.

Lower RMSE means a closer fit.

The fit summary CSV contains:

```text
cluster, point_count, rmse, s0, z0, c
```

Example interpretation:

```text
cluster 0, 492 points, rmse 0.028
```

means cluster 0 was fitted using 492 points, and the average vertical fit error is roughly 0.028 in the dataset coordinate units.

## Step 7: Reconstruct The Fit In 3D

The 2D catenary fit is performed in local coordinates, but the final visualisation is reconstructed in original 3D coordinates.

Implemented in:

```python
reconstruct_catenary_curve_3d(...)
```

The code creates a smooth set of local along-span positions:

```python
s_line = np.linspace(cluster_min_s, cluster_max_s, 200)
```

Then it evaluates the fitted catenary height:

```python
fitted_z = catenary_curve(s_line, s0, z0, c)
```

The local curve is created with:

```text
local_0 = s_line
local_1 = average local_1 of the cluster
local_2 = average local_2 of the cluster
```

Then it is transformed back into original `x`, `y`, `z` space:

```python
world_curve = local_curve @ directions + center
```

Finally, the fitted catenary height is assigned to the original `z` coordinate:

```python
world_curve[:, 2] = fitted_z
```

This gives a 3D line that can be plotted over the original LiDAR points.

## Outputs

Raw exploration images:

```text
explore_images/
```

Cluster plots and cluster summaries:

```text
cluster_images/
```

Catenary fit plots, 3D fit plots, and fit summaries:

```text
fit_images/
```

Useful commands:

```bash
lidar-catenary cluster-all
lidar-catenary fit-all
```

## Current Results Summary

Using default clustering parameters:

```text
easy       -> 3 detected wire clusters
medium     -> 7 detected wire clusters
hard       -> 3 detected wire clusters
extrahard  -> 3 detected wire clusters
```

The fitted RMSE values observed so far are approximately around:

```text
0.027 to 0.031
```

This indicates the fitted catenary curves closely match the provided point clusters under the current model assumptions.

## Assumptions

The current approach assumes:

1. The point cloud mostly contains wire points.
2. Wires in a file are mostly parallel.
3. The wire set has one dominant span direction.
4. `z` is the elevation/height coordinate.
5. Each detected cluster can be modeled by a single catenary.
6. The catenary can be fitted as `z` against local along-span position `s`.

These assumptions are reasonable for the provided test files, but they are not universally true for all power-line LiDAR scenes.

## Limitations

The most important limitation is the single global PCA frame.

The current method works best when the scene looks roughly like parallel wires from above:

```text
----------------
----------------
----------------
```

It is less reliable if the scene has multiple independent wire directions, for example an X-shaped crossing:

```text
\        /
 \      /
  \    /
   \  /
   /  \
  /    \
 /      \
/        \
```

In that case, one global PCA direction becomes a compromise and may not represent the span direction of every wire. The result could be merged clusters, split clusters, or poor catenary fits.

Other limitations:

- DBSCAN parameters are fixed defaults, not automatically tuned.
- The reconstruction uses average local cross-section coordinates per cluster.
- The method does not use pole/tower locations or physical line constraints.
- The current output is a fitted model and visualisation, not an engineering-grade asset format.

## Possible Future Improvements

Potential improvements include:

1. Add automatic DBSCAN parameter tuning.
2. Add 2D projection plots for easier visual diagnosis.
3. Detect multiple span-direction groups before clustering.
4. Use RANSAC or local tangent estimation for crossing/multi-direction wires.
5. Add more robust outlier filtering before fitting.
6. Export reconstructed catenary model points as CSV or GeoJSON.
7. Add quantitative validation if ground-truth labels become available.
8. Package example synthetic data so CI can test the full CLI without private assessment data.

## Interview Explanation

A concise explanation of the approach:

```text
I first load the LiDAR points from Parquet and validate the x/y/z columns.
Then I use PCA to define a local coordinate frame where the first axis is the dominant wire-span direction.
I cluster points with DBSCAN using the two coordinates perpendicular to that span direction, because points on the same wire can be far apart along the span but close in cross-section.
For each cluster, I fit a 2D catenary model using local along-span position as the independent variable and z elevation as the dependent variable.
Finally, I reconstruct the fitted curve back into original 3D coordinates and save plots and CSV summaries.
```

