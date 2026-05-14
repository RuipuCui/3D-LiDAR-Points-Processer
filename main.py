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

    input_file = Path(file_path)
    output_file = Path("explore_images") / f"{input_file.stem}.png"
    save_3d_plot(point_cloud, output_file)


def cluster_command(file_path, eps, min_samples):
    """Read, cluster, summarize, and plot a Parquet file."""
    from src.cluster_data import cluster_point_cloud, print_cluster_summary, save_cluster_plot

    point_cloud = read_lidar_parquet(file_path)
    clustered_data = cluster_point_cloud(point_cloud, eps=eps, min_samples=min_samples)
    print_cluster_summary(clustered_data)

    input_file = Path(file_path)
    output_file = Path("cluster_images") / f"{input_file.stem}_clusters.png"
    save_cluster_plot(clustered_data, output_file)


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

    cluster_parser = subparsers.add_parser(
        "cluster",
        help="Cluster points into likely wire groups and save a colored 3D plot.",
    )
    cluster_parser.add_argument("file", help="Path to a LiDAR Parquet file.")
    cluster_parser.add_argument(
        "--eps",
        type=float,
        default=0.35,
        help="DBSCAN neighborhood size. Larger values merge more points into clusters.",
    )
    cluster_parser.add_argument(
        "--min-samples",
        type=int,
        default=10,
        help="Minimum nearby points required to form a DBSCAN cluster.",
    )

    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()

    if args.command == "read":
        read_command(args.file)
    elif args.command == "explore":
        explore_command(args.file)
    elif args.command == "cluster":
        cluster_command(args.file, args.eps, args.min_samples)
