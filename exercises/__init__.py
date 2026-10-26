"""
Exercise state machine modules for rep counting and form analysis.
"""

from exercises.base_exercise import BaseExercise
from exercises.squat import SquatTracker
from exercises.bicep_curl import BicepCurlTracker
from exercises.pushup import PushupTracker
from exercises.plank import PlankTracker

__all__ = ["BaseExercise", "SquatTracker", "BicepCurlTracker", "PushupTracker", "PlankTracker"]
