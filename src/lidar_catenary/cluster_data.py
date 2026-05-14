from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import DBSCAN


def create_local_coordinates(point_cloud):
    """Convert xyz points into a PCA-based local coordinate system."""
    local_points, _, _ = create_local_frame(point_cloud)
    return local_points


def create_local_frame(point_cloud):
    """Create local PCA coordinates and return data needed to convert back to xyz."""
    points = point_cloud[["x", "y", "z"]].to_numpy()
    center = points.mean(axis=0)
    centered_points = points - center

    _, _, directions = np.linalg.svd(centered_points, full_matrices=False)
    local_points = centered_points @ directions.T

    return local_points, center, directions


def cluster_point_cloud(point_cloud, eps=0.35, min_samples=10):
    """Cluster LiDAR points into likely wire groups using DBSCAN."""
    local_points = create_local_coordinates(point_cloud)

    # Use the two coordinates perpendicular to the main wire direction.
    # This helps group points that belong to the same parallel wire.
    clustering_features = local_points[:, 1:3]

    model = DBSCAN(eps=eps, min_samples=min_samples)
    labels = model.fit_predict(clustering_features)

    clustered_data = point_cloud.copy()
    clustered_data["cluster"] = labels

    return clustered_data


def get_cluster_summary(clustered_data):
    """Return basic cluster counts for one clustered point cloud."""
    cluster_counts = clustered_data["cluster"].value_counts().sort_index()
    wire_count = len([label for label in cluster_counts.index if label != -1])
    noise_points = int(cluster_counts.get(-1, 0))

    return {
        "total_points": len(clustered_data),
        "wire_clusters": wire_count,
        "noise_points": noise_points,
        "cluster_counts": cluster_counts.to_dict(),
    }


def print_cluster_summary(clustered_data):
    """Print the number of points in each cluster."""
    summary = get_cluster_summary(clustered_data)
    cluster_counts = summary["cluster_counts"]

    print("Cluster summary:")
    for cluster_label, count in cluster_counts.items():
        if cluster_label == -1:
            print(f"Noise/outliers: {count} points")
        else:
            print(f"Cluster {cluster_label}: {count} points")

    print(f"Detected wire clusters: {summary['wire_clusters']}")


def save_cluster_plot(clustered_data, output_path):
    """Save a 3D scatter plot colored by cluster label."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    scatter = ax.scatter(
        clustered_data["x"],
        clustered_data["y"],
        clustered_data["z"],
        c=clustered_data["cluster"],
        cmap="tab10",
        s=5,
        alpha=0.8,
    )

    ax.set_title("Clustered LiDAR Point Cloud")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    fig.colorbar(scatter, ax=ax, label="cluster")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)

    print(f"Saved cluster plot: {output_path}")

