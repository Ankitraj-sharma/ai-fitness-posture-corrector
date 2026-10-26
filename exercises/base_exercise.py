"""
Abstract Base Class for Exercise State Machine Trackers.
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseExercise(ABC):
    """
    Standard interface for exercise rep counting, stage transitions, and feedback.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.reps: int = 0
        self.stage: str = "START"
        self.feedback: str = "Get into starting position"
        self.form_is_clean: bool = True
        self.current_angle: float = 180.0
        self.clean_reps: int = 0
        self.flagged_reps: int = 0

    @abstractmethod
    def process(self, landmarks_px: dict[int, tuple[int, int]]) -> dict:
        """
        Evaluate joint coordinates, update state machine, and return status metrics.
        """
        pass

    def reset(self) -> None:
        """Reset counters and stage states."""
        self.reps = 0
        self.stage = "START"
        self.feedback = "Ready"
        self.form_is_clean = True
        self.current_angle = 180.0
        self.clean_reps = 0
        self.flagged_reps = 0

    @property
    def accuracy_rate(self) -> int:
        """Percentage of reps performed with clean biomechanical form."""
        total = self.clean_reps + self.flagged_reps
        if total == 0:
            return 100
        return int((self.clean_reps / total) * 100)
