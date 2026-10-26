"""
Squat Repetition Counter & Biomechanical Form Analyzer.

Tracks Hip-Knee-Ankle extension and Torso alignment to evaluate squat depth,
cadence, and lumbar posture in real time.
"""

from exercises.base_exercise import BaseExercise
from kinematics import calculate_angle, calculate_vertical_inclination


class SquatTracker(BaseExercise):
    """
    Evaluates squats with knee flexion thresholds and chest inclination validation.
    """

    def __init__(self) -> None:
        super().__init__("Squat")
        self.knee_down_thresh: float = 95.0
        self.knee_up_thresh: float = 160.0
        self._rep_form_flaw: bool = False

    def process(self, landmarks_px: dict[int, tuple[int, int]]) -> dict:
        """
        Evaluate frame keypoints: Left Hip (23), Left Knee (25), Left Ankle (27).
        """
        # Determine better visible leg (default Left leg 23, 25, 27)
        if 23 in landmarks_px and 25 in landmarks_px and 27 in landmarks_px:
            hip = landmarks_px[23]
            knee = landmarks_px[25]
            ankle = landmarks_px[27]
            shoulder = landmarks_px.get(11, (hip[0], hip[1] - 100))
        elif 24 in landmarks_px and 26 in landmarks_px and 28 in landmarks_px:
            hip = landmarks_px[24]
            knee = landmarks_px[26]
            ankle = landmarks_px[28]
            shoulder = landmarks_px.get(12, (hip[0], hip[1] - 100))
        else:
            return {
                "reps": self.reps,
                "stage": self.stage,
                "feedback": "Step back so legs are visible",
                "angle": 180.0,
                "form_is_clean": True,
            }

        knee_angle = calculate_angle(hip, knee, ankle)
        self.current_angle = knee_angle

        # Check chest/torso inclination
        torso_tilt = calculate_vertical_inclination(shoulder, hip)

        # State machine transitions
        if knee_angle > self.knee_up_thresh:
            if self.stage == "DOWN":
                self.reps += 1
                if self._rep_form_flaw:
                    self.flagged_reps += 1
                    self.feedback = "Rep counted, but watch your chest posture!"
                else:
                    self.clean_reps += 1
                    self.feedback = "Excellent squat! Keep it up!"
                self._rep_form_flaw = False
            self.stage = "UP"

        elif knee_angle < self.knee_down_thresh:
            self.stage = "DOWN"
            if torso_tilt > 45.0:
                self.feedback = "Keep chest UP! Avoid bending forward."
                self._rep_form_flaw = True
                self.form_is_clean = False
            else:
                self.feedback = "Good depth! Now push up through your heels."
                self.form_is_clean = True
        else:
            if self.stage == "UP":
                self.feedback = "Lower down into squat..."
            elif self.stage == "DOWN":
                self.feedback = "Drive up..."

        return {
            "reps": self.reps,
            "stage": self.stage,
            "feedback": self.feedback,
            "angle": self.current_angle,
            "form_is_clean": self.form_is_clean,
            "accuracy_rate": self.accuracy_rate,
        }


# Backward compatibility alias
SquatExercise = SquatTracker

