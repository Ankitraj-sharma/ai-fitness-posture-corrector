"""
Plank Isometric Hold Timer & Lumbar Posture Corrector.

Measures clean hold duration in seconds and validates spine collinearity.
"""

import time
from exercises.base_exercise import BaseExercise
from kinematics import calculate_angle


class PlankTracker(BaseExercise):
    """
    Evaluates isometric plank holds with second timer and core posture monitoring.
    """

    def __init__(self) -> None:
        super().__init__("Plank")
        self.hold_seconds: float = 0.0
        self._hold_start: float = 0.0
        self.is_holding: bool = False

    def process(self, landmarks_px: dict[int, tuple[int, int]]) -> dict:
        """
        Evaluate body alignment: Shoulder (11/12), Hip (23/24), Ankle (27/28).
        """
        if 11 in landmarks_px and 23 in landmarks_px and 27 in landmarks_px:
            shoulder = landmarks_px[11]
            hip = landmarks_px[23]
            ankle = landmarks_px[27]
        elif 12 in landmarks_px and 24 in landmarks_px and 28 in landmarks_px:
            shoulder = landmarks_px[12]
            hip = landmarks_px[24]
            ankle = landmarks_px[28]
        else:
            self._stop_timer()
            return {
                "reps": int(self.hold_seconds),
                "stage": "IDLE",
                "feedback": "Position side profile in camera frame",
                "angle": 180.0,
                "form_is_clean": True,
            }

        spine_angle = calculate_angle(shoulder, hip, ankle)
        self.current_angle = spine_angle

        # Clean plank posture check: 160 to 195 degrees
        if 160.0 <= spine_angle <= 195.0:
            self.form_is_clean = True
            self.stage = "HOLDING"
            self.feedback = "Perfect plank alignment! Hold strong!"
            if not self.is_holding:
                self.is_holding = True
                self._hold_start = time.time() - self.hold_seconds
            else:
                self.hold_seconds = round(time.time() - self._hold_start, 1)
                self.reps = int(self.hold_seconds)
                self.clean_reps = int(self.hold_seconds)
        else:
            self.form_is_clean = False
            self.stage = "IMPROPER"
            self.flagged_reps += 1
            if spine_angle < 160.0:
                self.feedback = "Hips are sagging! Lift pelvis into a straight line."
            else:
                self.feedback = "Hips are too high! Flatten your back."
            self._stop_timer()

        return {
            "reps": int(self.hold_seconds),
            "stage": self.stage,
            "feedback": self.feedback,
            "angle": self.current_angle,
            "form_is_clean": self.form_is_clean,
            "accuracy_rate": self.accuracy_rate,
        }

    def _stop_timer(self) -> None:
        self.is_holding = False

    def reset(self) -> None:
        super().reset()
        self.hold_seconds = 0.0
        self._hold_start = 0.0
        self.is_holding = False


# Backward compatibility alias
PlankExercise = PlankTracker

