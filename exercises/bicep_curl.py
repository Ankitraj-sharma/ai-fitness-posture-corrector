"""
Bicep Curl Repetition Counter & Elbow Stability Analyzer.

Tracks Shoulder-Elbow-Wrist flexion and prevents momentum swinging/cheating.
"""

from exercises.base_exercise import BaseExercise
from kinematics import calculate_angle


class BicepCurlTracker(BaseExercise):
    """
    Evaluates arm curls with full contraction, extension, and elbow stability.
    """

    def __init__(self, arm_side: str = "auto") -> None:
        super().__init__("Bicep Curl")
        self.arm_side = arm_side
        self.curl_up_thresh: float = 40.0
        self.curl_down_thresh: float = 155.0
        self._rep_form_flaw: bool = False

    def process(self, landmarks_px: dict[int, tuple[int, int]]) -> dict:
        """
        Evaluate arm joints: Shoulder (11/12), Elbow (13/14), Wrist (15/16).
        """
        # Auto-detect side or pick Left arm (11, 13, 15) vs Right arm (12, 14, 16)
        if (self.arm_side in ("auto", "left")) and (11 in landmarks_px and 13 in landmarks_px and 15 in landmarks_px):
            shoulder = landmarks_px[11]
            elbow = landmarks_px[13]
            wrist = landmarks_px[15]
        elif 12 in landmarks_px and 14 in landmarks_px and 16 in landmarks_px:
            shoulder = landmarks_px[12]
            elbow = landmarks_px[14]
            wrist = landmarks_px[16]
        else:
            return {
                "reps": self.reps,
                "stage": self.stage,
                "feedback": "Position arm clearly in camera frame",
                "angle": 180.0,
                "form_is_clean": True,
            }

        elbow_angle = calculate_angle(shoulder, elbow, wrist)
        self.current_angle = elbow_angle

        # Check elbow drift (elbow swinging forward or backward excessively)
        elbow_drift = abs(elbow[0] - shoulder[0])

        if elbow_angle > self.curl_down_thresh:
            if self.stage == "UP":
                self.reps += 1
                if self._rep_form_flaw:
                    self.flagged_reps += 1
                    self.feedback = "Rep completed! Pin your elbow to your side."
                else:
                    self.clean_reps += 1
                    self.feedback = "Great curl! Full extension achieved."
                self._rep_form_flaw = False
            self.stage = "DOWN"

        elif elbow_angle < self.curl_up_thresh:
            self.stage = "UP"
            if elbow_drift > 80:
                self.feedback = "Don't swing your elbow forward!"
                self._rep_form_flaw = True
                self.form_is_clean = False
            else:
                self.feedback = "Great peak contraction! Squeeze and lower slowly."
                self.form_is_clean = True
        else:
            if self.stage == "DOWN":
                self.feedback = "Curl up to the top..."
            elif self.stage == "UP":
                self.feedback = "Lower down with control..."

        return {
            "reps": self.reps,
            "stage": self.stage,
            "feedback": self.feedback,
            "angle": self.current_angle,
            "form_is_clean": self.form_is_clean,
            "accuracy_rate": self.accuracy_rate,
        }


# Backward compatibility alias
BicepCurlExercise = BicepCurlTracker

