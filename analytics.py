"""
Workout Session Analytics, Calorie Estimation & Plotly Kinematic Curves.
"""

from collections import deque
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# MET (Metabolic Equivalent of Task) values per rep / second
MET_ENERGY_MAP = {
    "Squats": 0.32,      # kcal per full rep
    "Push-ups": 0.45,    # kcal per full rep
    "Bicep Curls": 0.20, # kcal per full rep
    "Planks": 0.08,      # kcal per second held
}


def estimate_calories_burned(exercise: str, reps_or_secs: int, user_weight_kg: float = 70.0) -> float:
    """
    Estimate burned calories adjusted for bodyweight.
    """
    base_kcal = MET_ENERGY_MAP.get(exercise, 0.30) * reps_or_secs
    weight_factor = user_weight_kg / 70.0
    return round(base_kcal * weight_factor, 1)


def joint_angle_time_series(angle_history: list[float], exercise: str) -> go.Figure:
    """Plotly live rolling curve of joint angles with target inflection zones."""
    fig = go.Figure()
    frames = list(range(len(angle_history)))

    fig.add_trace(
        go.Scatter(
            x=frames,
            y=angle_history,
            mode="lines",
            name="Joint Angle (°)",
            line=dict(color="#00F5D4", width=3),
        )
    )

    # Add reference zone for target contraction
    target_down = 90.0 if exercise in ("Squats", "Push-ups") else 40.0
    fig.add_hline(
        y=target_down,
        line_dash="dash",
        line_color="#FF007F",
        annotation_text=f"Target Contraction ({int(target_down)}°)",
        annotation_position="bottom right",
    )

    fig.update_layout(
        title=f"Live Kinematic Trajectory — {exercise}",
        xaxis_title="Recent Movement Frames",
        yaxis_title="Angle (Degrees)",
        height=270,
        margin=dict(l=0, r=0, t=35, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F0F6FC"),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)")
    return fig


def form_accuracy_gauge(accuracy_pct: int) -> go.Figure:
    """Circular gauge displaying clean biomechanical rep accuracy."""
    color = "#00F5D4" if accuracy_pct >= 85 else ("#FEE440" if accuracy_pct >= 65 else "#FF007F")
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=accuracy_pct,
            title={"text": "Form Accuracy Score", "font": {"size": 17, "color": color}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#888"},
                "bar": {"color": color},
                "bgcolor": "rgba(255,255,255,0.05)",
                "steps": [
                    {"range": [0, 65], "color": "rgba(255, 0, 127, 0.25)"},
                    {"range": [65, 85], "color": "rgba(254, 228, 64, 0.25)"},
                    {"range": [85, 100], "color": "rgba(0, 245, 212, 0.25)"},
                ],
            },
        )
    )
    fig.update_layout(
        height=220,
        margin=dict(l=20, r=20, t=40, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F0F6FC"),
    )
    return fig
