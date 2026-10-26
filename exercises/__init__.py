"""
Exercise module exports with full backward compatibility aliases.
"""

from exercises.base_exercise import BaseExercise
from exercises.squat import SquatTracker, SquatExercise
from exercises.bicep_curl import BicepCurlTracker, BicepCurlExercise
from exercises.pushup import PushupTracker, PushupExercise
from exercises.plank import PlankTracker, PlankExercise
from exercises.lunges import LungeTracker

# Lunge alias
LungeExercise = LungeTracker

__all__ = [
    "BaseExercise",
    "SquatTracker",
    "SquatExercise",
    "BicepCurlTracker",
    "BicepCurlExercise",
    "PushupTracker",
    "PushupExercise",
    "PlankTracker",
    "PlankExercise",
    "LungeTracker",
    "LungeExercise",
]
