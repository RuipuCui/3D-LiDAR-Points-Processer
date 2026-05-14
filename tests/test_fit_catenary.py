import numpy as np

from lidar_catenary.fit_catenary import catenary_curve, fit_single_catenary


def test_fit_single_catenary_recovers_synthetic_curve():
    s = np.linspace(-10, 10, 120)
    z = catenary_curve(s, s0=1.5, z0=8.0, c=50.0)

    result = fit_single_catenary(s, z)

    assert result["rmse"] < 1e-6
    assert abs(result["s0"] - 1.5) < 1e-3
    assert abs(result["z0"] - 8.0) < 1e-3

