import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares

from src.cluster_data import cluster_point_cloud, create_local_coordinates


def catenary_curve(s, s0, z0, c):
    """Calculate catenary height values for along-wire positions."""
    c = max(float(c), 1e-6)
    scaled_distance = np.clip((s - s0) / c, -50, 50)
    return z0 + c * (np.cosh(scaled_distance) - 1)


def fit_single_catenary(s, z):
    """Fit one catenary curve to along-wire positions and heights."""
    if len(s) < 5:
        raise ValueError("At least 5 points are required to fit a catenary.")

    lowest_point_index = int(np.argmin(z))
    s_range = max(float(np.ptp(s)), 1.0)
    z_range = max(float(np.ptp(z)), 1.0)

    initial_guess = np.array(
        [
            s[lowest_point_index],
            z[lowest_point_index],
            s_range * 5,
        ]
    )

    lower_bounds = np.array([s.min() - s_range, z.min() - z_range, 1e-3])
    upper_bounds = np.array([s.max() + s_range, z.max(), 1_000_000.0])

    def residuals(parameters):
        s0, z0, c = parameters
        return catenary_curve(s, s0, z0, c) - z

    result = least_squares(
        residuals,
        initial_guess,
        bounds=(lower_bounds, upper_bounds),
        loss="soft_l1",
    )

    fitted_z = catenary_curve(s, *result.x)
    rmse = float(np.sqrt(np.mean((fitted_z - z) ** 2)))

    return {
        "s0": float(result.x[0]),
        "z0": float(result.x[1]),
        "c": float(result.x[2]),
        "rmse": rmse,
        "point_count": len(s),
    }


def fit_catenaries_for_point_cloud(point_cloud, eps=0.35, min_samples=10):
    """Cluster a point cloud and fit one catenary to each cluster."""
    clustered_data = cluster_point_cloud(point_cloud, eps=eps, min_samples=min_samples)
    local_points = create_local_coordinates(point_cloud)

    fit_results = []
    for cluster_label in sorted(clustered_data["cluster"].unique()):
        if cluster_label == -1:
            continue

        cluster_mask = clustered_data["cluster"].to_numpy() == cluster_label
        s = local_points[cluster_mask, 0]
        z = clustered_data.loc[cluster_mask, "z"].to_numpy()

        fit_result = fit_single_catenary(s, z)
        fit_result["cluster"] = int(cluster_label)
        fit_results.append(fit_result)

    return clustered_data, local_points, fit_results


def print_fit_summary(fit_results):
    """Print catenary parameters and fit error for each cluster."""
    print("Catenary fit summary:")
    print(f"{'cluster':>7} {'points':>8} {'rmse':>10} {'s0':>10} {'z0':>10} {'c':>12}")
    for result in fit_results:
        print(
            f"{result['cluster']:>7} "
            f"{result['point_count']:>8} "
            f"{result['rmse']:>10.4f} "
            f"{result['s0']:>10.4f} "
            f"{result['z0']:>10.4f} "
            f"{result['c']:>12.4f}"
        )


def save_fit_summary_csv(fit_results, output_path):
    """Save catenary fit parameters to a CSV file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="") as csv_file:
        fieldnames = ["cluster", "point_count", "rmse", "s0", "z0", "c"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(fit_results)

    print(f"Saved fit summary: {output_path}")


def save_fit_plot(clustered_data, local_points, fit_results, output_path):
    """Save a 2D plot of clustered points and their fitted catenary curves."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 6))

    for result in fit_results:
        cluster_label = result["cluster"]
        cluster_mask = clustered_data["cluster"].to_numpy() == cluster_label
        s = local_points[cluster_mask, 0]
        z = clustered_data.loc[cluster_mask, "z"].to_numpy()

        ax.scatter(s, z, s=8, alpha=0.45, label=f"cluster {cluster_label} points")

        s_line = np.linspace(s.min(), s.max(), 200)
        z_line = catenary_curve(s_line, result["s0"], result["z0"], result["c"])
        ax.plot(s_line, z_line, linewidth=2, label=f"cluster {cluster_label} fit")

    ax.set_title("Catenary Fits")
    ax.set_xlabel("local position along wire")
    ax.set_ylabel("z height")
    ax.legend()
    ax.grid(True, alpha=0.25)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)

    print(f"Saved fit plot: {output_path}")
