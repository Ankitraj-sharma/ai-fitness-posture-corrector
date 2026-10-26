"""
Kinematic Vector Angle Solvers & Biomechanical Geometry.

Calculates joint interior angles, vertical torso inclination,
and collinearity checks for human pose evaluation.
"""

import math
from typing import Sequence


def calculate_angle(
    a: Sequence[float], b: Sequence[float], c: Sequence[float]
) -> float:
    """
    Compute 2D interior angle at vertex B formed by line segments BA and BC.

    Parameters
    ----------
    a, b, c : 2D coordinates (x, y) where B is the central joint/vertex.

    Returns
    -------
    float: Angle in degrees in range [0, 180].
    """
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])

    dot_product = ba[0] * bc[0] + ba[1] * bc[1]
    norm_ba = math.hypot(ba[0], ba[1])
    norm_bc = math.hypot(bc[0], bc[1])

    if norm_ba < 1e-6 or norm_bc < 1e-6:
        return 180.0

    cosine = dot_product / (norm_ba * norm_bc)
    # Clamp cosine to [-1.0, 1.0] to prevent math domain error
    cosine = max(-1.0, min(1.0, cosine))

    angle = math.degrees(math.acos(cosine))
    return round(float(angle), 1)


def calculate_3d_angle(
    a: Sequence[float], b: Sequence[float], c: Sequence[float]
) -> float:
    """
    Compute 3D interior angle at vertex B in 3D Euclidean space (x, y, z).
    """
    ba = (a[0] - b[0], a[1] - b[1], a[2] - b[2])
    bc = (c[0] - b[0], c[1] - b[1], c[2] - b[2])

    dot_product = ba[0] * bc[0] + ba[1] * bc[1] + ba[2] * bc[2]
    norm_ba = math.sqrt(ba[0] ** 2 + ba[1] ** 2 + ba[2] ** 2)
    norm_bc = math.sqrt(bc[0] ** 2 + bc[1] ** 2 + bc[2] ** 2)

    if norm_ba < 1e-6 or norm_bc < 1e-6:
        return 180.0

    cosine = max(-1.0, min(1.0, dot_product / (norm_ba * norm_bc)))
    return round(float(math.degrees(math.acos(cosine))), 1)


def calculate_vertical_inclination(a: Sequence[float], b: Sequence[float]) -> float:
    """
    Measures deviation of line segment AB against the vertical gravitational vector (y-axis).
    0 degrees means perfectly vertical; 90 degrees means horizontal.
    """
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    if dy < 1e-6:
        return 90.0
    rad = math.atan(dx / dy)
    return round(float(math.degrees(rad)), 1)


def check_collinearity(
    a: Sequence[float], b: Sequence[float], c: Sequence[float], tolerance_deg: float = 18.0
) -> bool:
    """
    Checks if points A, B, and C form a straight line within tolerance.
    Useful for ensuring spine/lumbar is straight during Planks and Pushups.
    """
    angle = calculate_angle(a, b, c)
    return abs(180.0 - angle) <= tolerance_deg
