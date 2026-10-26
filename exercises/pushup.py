"""
Push-up Repetition Counter & Spine Alignment Analyzer.

Measures chest-to-floor depth via elbow flexion and enforces strict
shoulder-hip-ankle collinearity to prevent lumbar hyperextension/sagging.
"""

from exercises.base_exercise import BaseExercise
from kinematics import calculate_angle, check_collinearity


class PushupTracker(BaseExercise):
    """
    Evaluates push-ups with depth thresholds and full-body core alignment checks.
    """

    def __init__(self) -> None:
        super().__init__("Push-up")
        self.pushup_down_thresh: float = 90.0
        self.pushup_up_thresh: float = 160.0
        self._rep_form_flaw: bool = False

    def process(self, landmarks_px: dict[int, tuple[int, int]]) -> dict:
        """
        Evaluate frame joints: Left Shoulder (11), Elbow (13), Wrist (15), Hip (23), Ankle (27).
        """
        if 11 in landmarks_px and 13 in landmarks_px and 15 in landmarks_px:
            shoulder = landmarks_px[11]
            elbow = landmarks_px[13]
            wrist = landmarks_px[15]
            hip = landmarks_px.get(23)
            ankle = landmarks_px.get(27)
        elif 12 in landmarks_px and 14 in landmarks_px and 16 in landmarks_px:
            shoulder = landmarks_px[12]
            elbow = landmarks_px[14]
            wrist = landmarks_px[16]
            hip = landmarks_px.get(24)
            ankle = landmarks_px.get(28)
        else:
            return {
                "reps": self.reps,
                "stage": self.stage,
                "feedback": "Position body horizontally in camera view",
                "angle": 180.0,
                "form_is_clean": True,
            }

        elbow_angle = calculate_angle(shoulder, elbow, wrist)
        self.current_angle = elbow_angle

        # Check spine alignment (Shoulder - Hip - Ankle collinearity)
        spine_straight = True
        spine_angle = 180.0
        if hip is not None and ankle is not None:
            spine_angle = calculate_angle(shoulder, hip, ankle)
            if spine_angle < 155.0:
                self.feedback = "Hips are sagging! Tighten your core and glutes."
                spine_straight = False
                self._rep_form_flaw = True
                self.form_is_clean = False
            elif spine_angle > 200.0:
                self.feedback = "Hips are too high! Lower hips into a straight plank line."
                spine_straight = False
                self._rep_form_flaw = True
                self.form_is_clean = False

        if elbow_angle > self.pushup_up_thresh:
            if self.stage == "DOWN":
                self.reps += 1
                if self._rep_form_flaw:
                    self.flagged_reps += 1
                    self.feedback = "Rep counted, but keep your back flat!"
                else:
                    self.clean_reps += 1
                    self.feedback = "Solid pushup! Perfect form."
                self._rep_form_flaw = False
            self.stage = "UP"

        elif elbow_angle < self.pushup_down_thresh:
            self.stage = "DOWN"
            if spine_straight:
                self.feedback = "Great depth! Push the floor away."
                self.form_is_clean = True
        else:
            if self.stage == "UP":
                self.feedback = "Lower chest with control..."
            elif self.stage == "DOWN":
                self.feedback = "Push up to full lockout..."

        return {
            "reps": self.reps,
            "stage": self.stage,
            "feedback": self.feedback,
            "angle": self.current_angle,
            "form_is_clean": self.form_is_clean,
            "accuracy_rate": self.accuracy_rate,
        }
