"""
WebRTC Video Stream Processor for AI Fitness Coaching.

Ingests webcam frames, runs 33-point pose landmark extraction, executes
exercise state machines, and overlays a live cybernetic workout HUD.
"""

import threading
import time
from typing import Optional

import av
import cv2
from streamlit_webrtc import RTCConfiguration, VideoProcessorBase

from exercises import BaseExercise, BicepCurlTracker, PlankTracker, PushupTracker, SquatTracker, LungeTracker
from pose_tracker import PoseTracker

# Public STUN servers for WebRTC NAT traversal on Streamlit Cloud
RTC_CONFIGURATION = RTCConfiguration(
    {
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},
            {"urls": ["stun:stun1.l.google.com:19302"]},
            {"urls": ["stun:stun2.l.google.com:19302"]},
            {"urls": ["stun:stun3.l.google.com:19302"]},
        ]
    }
)


class LiveWorkoutProcessor(VideoProcessorBase):
    """
    Asynchronous WebRTC processor executing real-time biomechanical workout tracking.
    """

    def __init__(self) -> None:
        self.tracker = PoseTracker()
        self.active_exercise: BaseExercise = SquatTracker()

        # Thread synchronization
        self._lock = threading.Lock()
        self.fps: float = 0.0
        self.reps: int = 0
        self.stage: str = "START"
        self.feedback: str = "Ready"
        self.angle: float = 180.0
        self.form_is_clean: bool = True
        self.accuracy_rate: int = 100
        self.rep_increment_event: Optional[int] = None
        self._last_reps = 0

        # Frame rate monitoring
        self._frame_count = 0
        self._last_time = time.time()

    def set_exercise(self, exercise_name: str) -> None:
        """Switch active exercise tracker dynamically from UI."""
        with self._lock:
            if exercise_name == "Squats":
                self.active_exercise = SquatTracker()
            elif exercise_name == "Bicep Curls":
                self.active_exercise = BicepCurlTracker()
            elif exercise_name == "Push-ups":
                self.active_exercise = PushupTracker()
            elif exercise_name == "Planks":
                self.active_exercise = PlankTracker()
            elif exercise_name == "Lunges":
                self.active_exercise = LungeTracker()
            self.reps = 0
            self._last_reps = 0

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        """Process incoming video frame and overlay augmented fitness HUD."""
        img = frame.to_ndarray(format="bgr24")
        h, w = img.shape[:2]

        # Calculate FPS
        now = time.time()
        self._frame_count += 1
        elapsed = now - self._last_time
        if elapsed >= 1.0:
            self.fps = round(self._frame_count / elapsed, 1)
            self._frame_count = 0
            self._last_time = now

        # Run pose tracking
        annotated, pose_data = self.tracker.process_frame(img, draw=True)

        reps_val = 0
        stage_val = "IDLE"
        feedback_val = "Position full body in camera frame"
        angle_val = 180.0
        clean_val = True
        accuracy_val = 100

        if pose_data and pose_data.get("visible"):
            res = self.active_exercise.process(pose_data["landmarks_px"])
            reps_val = res["reps"]
            stage_val = res["stage"]
            feedback_val = res["feedback"]
            angle_val = res["angle"]
            clean_val = res["form_is_clean"]
            accuracy_val = res.get("accuracy_rate", 100)

            # Detect new rep event
            if reps_val > self._last_reps:
                self.rep_increment_event = reps_val
                self._last_reps = reps_val

            # Draw HUD
            self._draw_workout_hud(
                annotated, reps_val, stage_val, feedback_val, angle_val, clean_val, w, h
            )

        with self._lock:
            self.reps = reps_val
            self.stage = stage_val
            self.feedback = feedback_val
            self.angle = angle_val
            self.form_is_clean = clean_val
            self.accuracy_rate = accuracy_val

        return av.VideoFrame.from_ndarray(annotated, format="bgr24")

    def _draw_workout_hud(
        self,
        img,
        reps: int,
        stage: str,
        feedback: str,
        angle: float,
        is_clean: bool,
        w: int,
        h: int,
    ) -> None:
        """Render high-tech cybernetic fitness telemetry onto video feed."""
        # Top translucent ribbon
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (w, 85), (13, 17, 23), -1)
        cv2.addWeighted(overlay, 0.85, img, 0.15, 0, img)

        accent = (0, 245, 212) if is_clean else (0, 71, 255)
        cv2.line(img, (0, 85), (w, 85), accent, 3)

        # Rep Counter
        cv2.putText(
            img,
            f"REPS: {reps}",
            (25, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.4,
            accent,
            3,
            cv2.LINE_AA,
        )

        # Stage & Joint Angle
        cv2.putText(
            img,
            f"STAGE: {stage} | {int(angle)} DEG",
            (260, 52),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (240, 246, 252),
            2,
            cv2.LINE_AA,
        )

        # Bottom coaching feedback bar
        cv2.rectangle(img, (20, h - 50), (w - 20, h - 15), (13, 17, 23), -1)
        cv2.rectangle(img, (20, h - 50), (w - 20, h - 15), accent, 1)
        cv2.putText(
            img,
            f"COACH: {feedback}",
            (35, h - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            accent,
            2,
            cv2.LINE_AA,
        )

    def get_telemetry(self) -> dict:
        """Thread-safe retrieval of state metrics."""
        with self._lock:
            event = self.rep_increment_event
            self.rep_increment_event = None
            return {
                "reps": self.reps,
                "stage": self.stage,
                "feedback": self.feedback,
                "angle": self.angle,
                "form_is_clean": self.form_is_clean,
                "accuracy_rate": self.accuracy_rate,
                "fps": self.fps,
                "new_rep": event,
            }
