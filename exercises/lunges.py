"""
Lunge exercise tracker module.
Tracks front knee angle, rear knee angle, and torso vertical inclination.
"""

from typing import Dict, Any, Tuple
from exercises.base_exercise import BaseExercise
from kinematics import calculate_angle_2d, calculate_vertical_inclination


class LungeExercise(BaseExercise):
    """
    State machine for tracking Lunges (Forward / Reverse).
    Monitors front knee depth (~90 deg) and torso posture.
    """

    def __init__(self):
        super().__init__("Lunges")
        self.stage = "up"
        self.front_knee_target = 90.0  # target depth
        self.standing_angle = 160.0    # standing reset
        self.min_torso_angle = 70.0    # upright torso requirement

    def process(self, landmarks: Dict[str, Tuple[float, float]], frame_shape: Tuple[int, int]) -> Dict[str, Any]:
        h, w = frame_shape
        alerts = []

        # Determine dominant side based on visibility or default to left
        left_hip = landmarks.get("left_hip")
        left_knee = landmarks.get("left_knee")
        left_ankle = landmarks.get("left_ankle")
        left_shoulder = landmarks.get("left_shoulder")

        right_hip = landmarks.get("right_hip")
        right_knee = landmarks.get("right_knee")
        right_ankle = landmarks.get("right_ankle")
        right_shoulder = landmarks.get("right_shoulder")

        if not (left_hip and left_knee and left_ankle and left_shoulder):
            return {
                "counter": self.counter,
                "stage": self.stage,
                "feedback": "Step back into camera view",
                "form_ok": False,
                "primary_angle": 180.0,
                "metrics": {},
                "alert": None
            }

        # Calculate front knee flexion (left leg)
        knee_angle = calculate_angle_2d(left_hip, left_knee, left_ankle)
        
        # Calculate torso vertical inclination
        torso_angle = calculate_vertical_inclination(left_shoulder, left_hip)

        # Repetition State Machine
        form_ok = True
        feedback = "Good Form"

        if torso_angle < self.min_torso_angle:
            alerts.append("Keep torso upright")
            feedback = "Torso Leaning Forward"
            form_ok = False

        if knee_angle > self.standing_angle:
            self.stage = "up"
            feedback = "Step forward into lunge"
        elif knee_angle <= self.front_knee_target and self.stage == "up":
            self.stage = "down"
            self.counter += 1
            if form_ok:
                self.correct_reps += 1
                feedback = "Great Depth! Rise Up"
            else:
                self.incorrect_reps += 1

        # Calculate progress completion percentage (160 -> 90)
        progress = max(0.0, min(100.0, (self.standing_angle - knee_angle) / (self.standing_angle - self.front_knee_target) * 100.0))

        return {
            "counter": self.counter,
            "stage": self.stage,
            "feedback": feedback,
            "form_ok": form_ok,
            "primary_angle": round(knee_angle, 1),
            "progress": round(progress, 1),
            "metrics": {
                "knee_angle": round(knee_angle, 1),
                "torso_angle": round(torso_angle, 1),
                "accuracy": self.get_accuracy()
            },
            "alert": alerts[0] if alerts else None
        }
