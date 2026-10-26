"""
Unit tests for kinematic angle solvers and biomechanical collinearity checks.
"""

from kinematics import (
    calculate_angle,
    calculate_3d_angle,
    calculate_vertical_inclination,
    check_collinearity,
)


def test_right_angle():
    # 90-degree right angle (e.g. elbow at 90 degrees)
    a = (0.0, 1.0)
    b = (0.0, 0.0)
    c = (1.0, 0.0)
    angle = calculate_angle(a, b, c)
    assert abs(angle - 90.0) < 0.1, f"Expected 90 degrees, got {angle}"


def test_straight_line():
    # 180-degree straight arm
    a = (0.0, 2.0)
    b = (0.0, 1.0)
    c = (0.0, 0.0)
    angle = calculate_angle(a, b, c)
    assert abs(angle - 180.0) < 0.1, f"Expected 180 degrees, got {angle}"
    assert check_collinearity(a, b, c, tolerance_deg=5.0)


def test_collinearity_failure():
    # Non-collinear points (arched back)
    a = (0.0, 0.0)
    b = (1.0, 1.5)
    c = (2.0, 0.0)
    assert not check_collinearity(a, b, c, tolerance_deg=15.0)


def test_vertical_inclination():
    # Perfectly vertical segment
    a = (5.0, 10.0)
    b = (5.0, 0.0)
    incl = calculate_vertical_inclination(a, b)
    assert incl == 0.0, f"Expected 0 degrees vertical, got {incl}"


if __name__ == "__main__":
    test_right_angle()
    test_straight_line()
    test_collinearity_failure()
    test_vertical_inclination()
    print("All kinematic unit tests passed successfully!")
