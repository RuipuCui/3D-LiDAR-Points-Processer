import matplotlib.pyplot as plt


def print_summary(point_cloud, file_path):
    """Print useful basic information about a LiDAR point cloud."""
    print(f"File: {file_path}")
    print(f"Rows: {len(point_cloud)}")
    print(f"Columns: {list(point_cloud.columns)}")
    print()
    print("Coordinate summary:")
    print(point_cloud.describe())


def save_3d_plot(point_cloud, output_path):
    """Save a 3D scatter plot of the LiDAR point cloud."""
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    ax.scatter(
        point_cloud["x"],
        point_cloud["y"],
        point_cloud["z"],
        s=5,
        alpha=0.7,
    )

    ax.set_title("LiDAR Point Cloud")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)

    print(f"Saved plot: {output_path}")
