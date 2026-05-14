import pandas as pd
import numpy as np

from lidar_catenary.cluster_data import create_local_frame


def test_create_local_frame_can_reconstruct_points():
    point_cloud = pd.DataFrame(
        {
            "x": [0.0, 1.0, 2.0, 3.0],
            "y": [0.0, 2.0, 4.0, 6.0],
            "z": [1.0, 1.5, 2.0, 2.5],
        }
    )

    local_points, center, directions = create_local_frame(point_cloud)
    reconstructed = local_points @ directions + center

    np.testing.assert_allclose(reconstructed, point_cloud[["x", "y", "z"]].to_numpy(), atol=1e-12)

