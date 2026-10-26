"""
Unit tests for kinematic angle solvers, biomechanical collinearity checks,
lunge movement transitions, and report exporters.
"""

from kinematics import (
    calculate_angle,
    calculate_3d_angle,
    calculate_vertical_inclination,
    check_collinearity,
)
from exercises.lunges import LungeTracker
from export_utils import export_session_to_csv, export_session_to_json


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


def test_3d_angle():
    # Test 3D orthogonal coordinate angle
    a = (1.0, 0.0, 0.0)
    b = (0.0, 0.0, 0.0)
    c = (0.0, 1.0, 0.0)
    angle = calculate_3d_angle(a, b, c)
    assert abs(angle - 90.0) < 0.1, f"Expected 90 deg in 3D, got {angle}"


def test_lunge_state_machine():
    lunge = LungeTracker()
    assert lunge.stage == "START"
    assert lunge.reps == 0

    # Simulate deep lunge landmarks (Left leg: hip 23, knee 25, ankle 27)
    # Hip at (100, 200), Knee at (100, 300), Ankle at (200, 300) -> 90 deg right angle
    landmarks = {
        23: (100, 200),
        25: (100, 300),
        27: (200, 300),
        11: (100, 100),
    }
    result = lunge.process(landmarks)
    assert result["stage"] == "DOWN"

    # Now rise back up to standing (180 deg)
    standing_landmarks = {
        23: (100, 150),
        25: (100, 250),
        27: (100, 350),
        11: (100, 50),
    }
    res_up = lunge.process(standing_landmarks)
    assert res_up["stage"] == "UP"
    assert res_up["reps"] == 1


def test_export_utilities():
    records = [
        {"timestamp": "2026-10-26T12:00:00", "exercise": "Squats", "reps": 10, "correct_reps": 8, "incorrect_reps": 2, "accuracy": 80.0, "calories": 14.5}
    ]
    csv_str = export_session_to_csv(records)
    assert "Squats" in csv_str
    assert "accuracy_pct" in csv_str

    json_str = export_session_to_json({"user": "Athlete"}, records)
    assert "FitTrack AI" in json_str
    assert "Athlete" in json_str


if __name__ == "__main__":
    test_right_angle()
    test_straight_line()
    test_collinearity_failure()
    test_vertical_inclination()
    test_3d_angle()
    test_lunge_state_machine()
    test_export_utilities()
    print("All extended kinematic unit tests passed successfully!")
