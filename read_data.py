from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = ["x", "y", "z"]


def read_lidar_parquet(file_path):
    """Read a LiDAR Parquet file and return a pandas DataFrame."""
    file_path = Path(file_path)
    data = pd.read_parquet(file_path)

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    return data[REQUIRED_COLUMNS]


if __name__ == "__main__":
    point_cloud = read_lidar_parquet("lidar_cable_points_easy.parquet")
    print(point_cloud.head())
    print(f"Rows: {len(point_cloud)}")
