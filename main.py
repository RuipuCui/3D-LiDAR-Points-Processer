import argparse
from pathlib import Path

from src.explore_data import print_summary, save_3d_plot
from src.read_data import read_lidar_parquet


def read_command(file_path):
    """Read a Parquet file and print the first few rows."""
    point_cloud = read_lidar_parquet(file_path)
    print(point_cloud.head())
    print(f"Rows: {len(point_cloud)}")


def explore_command(file_path):
    """Read, summarize, and plot a Parquet file."""
    point_cloud = read_lidar_parquet(file_path)
    print_summary(point_cloud, file_path)

    output_file = Path(file_path).with_suffix(".png")
    save_3d_plot(point_cloud, output_file)


def build_parser():
    """Create the command line interface."""
    parser = argparse.ArgumentParser(description="Process 3D LiDAR point-cloud data.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    read_parser = subparsers.add_parser("read", help="Read a Parquet file and print sample rows.")
    read_parser.add_argument("file", help="Path to a LiDAR Parquet file.")

    explore_parser = subparsers.add_parser(
        "explore",
        help="Print summary statistics and save a 3D plot.",
    )
    explore_parser.add_argument("file", help="Path to a LiDAR Parquet file.")

    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()

    if args.command == "read":
        read_command(args.file)
    elif args.command == "explore":
        explore_command(args.file)
