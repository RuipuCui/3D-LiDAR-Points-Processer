import argparse
import csv
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


def cluster_all_command(eps, min_samples):
    """Cluster all LiDAR Parquet files and save a CSV summary."""
    from src.cluster_data import cluster_point_cloud, get_cluster_summary, save_cluster_plot

    parquet_files = sorted(Path(".").glob("lidar_cable_points_*.parquet"))
    if not parquet_files:
        raise FileNotFoundError("No lidar_cable_points_*.parquet files found.")

    summary_rows = []
    for file_path in parquet_files:
        point_cloud = read_lidar_parquet(file_path)
        clustered_data = cluster_point_cloud(point_cloud, eps=eps, min_samples=min_samples)
        summary = get_cluster_summary(clustered_data)

        output_file = Path("cluster_images") / f"{file_path.stem}_clusters.png"
        save_cluster_plot(clustered_data, output_file)

        summary_rows.append(
            {
                "file": file_path.name,
                "total_points": summary["total_points"],
                "wire_clusters": summary["wire_clusters"],
                "noise_points": summary["noise_points"],
                "cluster_counts": summary["cluster_counts"],
            }
        )

    print("Clustering summary:")
    print(f"{'file':45} {'points':>8} {'clusters':>8} {'noise':>8}")
    for row in summary_rows:
        print(
            f"{row['file']:45} "
            f"{row['total_points']:>8} "
            f"{row['wire_clusters']:>8} "
            f"{row['noise_points']:>8}"
        )

    output_csv = Path("cluster_images") / "cluster_summary.csv"
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="") as csv_file:
        fieldnames = ["file", "total_points", "wire_clusters", "noise_points", "cluster_counts"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"Saved summary: {output_csv}")


def fit_command(file_path, eps, min_samples):
    """Cluster a point cloud and fit catenary curves to each cluster."""
    from src.fit_catenary import (
        fit_catenaries_for_point_cloud,
        print_fit_summary,
        save_fit_plot,
        save_fit_summary_csv,
    )

    point_cloud = read_lidar_parquet(file_path)
    clustered_data, local_points, fit_results = fit_catenaries_for_point_cloud(
        point_cloud,
        eps=eps,
        min_samples=min_samples,
    )

    print_fit_summary(fit_results)

    input_file = Path(file_path)
    output_plot = Path("fit_images") / f"{input_file.stem}_catenary_fits.png"
    output_csv = Path("fit_images") / f"{input_file.stem}_fit_summary.csv"
    save_fit_plot(clustered_data, local_points, fit_results, output_plot)
    save_fit_summary_csv(fit_results, output_csv)


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

    cluster_all_parser = subparsers.add_parser(
        "cluster-all",
        help="Cluster all lidar_cable_points_*.parquet files and save a summary CSV.",
    )
    cluster_all_parser.add_argument(
        "--eps",
        type=float,
        default=0.35,
        help="DBSCAN neighborhood size. Larger values merge more points into clusters.",
    )
    cluster_all_parser.add_argument(
        "--min-samples",
        type=int,
        default=10,
        help="Minimum nearby points required to form a DBSCAN cluster.",
    )

    fit_parser = subparsers.add_parser(
        "fit",
        help="Cluster a file and fit one catenary curve per cluster.",
    )
    fit_parser.add_argument("file", help="Path to a LiDAR Parquet file.")
    fit_parser.add_argument(
        "--eps",
        type=float,
        default=0.35,
        help="DBSCAN neighborhood size used before fitting.",
    )
    fit_parser.add_argument(
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
    elif args.command == "cluster-all":
        cluster_all_command(args.eps, args.min_samples)
    elif args.command == "fit":
        fit_command(args.file, args.eps, args.min_samples)
