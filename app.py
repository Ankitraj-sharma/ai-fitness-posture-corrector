"""
FitTrack AI — Real-Time Workout Rep Counter & Posture Corrector
================================================================
A production-grade computer vision fitness application utilizing MediaPipe 33 3D
skeletal landmarks, vector joint trigonometry, and audio feedback to count reps
and enforce strict biomechanical form in real time.

Author : Computer Vision Biomechanics & Health AI Team
Stack  : Streamlit · MediaPipe · OpenCV · WebRTC · Web Speech API · Plotly
"""

from collections import deque
import time
from PIL import Image
import streamlit as st

from analytics import estimate_calories_burned, form_accuracy_gauge, joint_angle_time_series
from audio_coach import speak_coach_cue
from exercises import BicepCurlTracker, PlankTracker, PushupTracker, SquatTracker
from live_stream import RTC_CONFIGURATION, LiveWorkoutProcessor
from pose_tracker import PoseTracker
from streamlit_webrtc import WebRtcMode, webrtc_streamer

# ═══════════════════════════════════════════════════════════════════════
#  Page Setup & Neon Cyberpunk Fitness Styling
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="FitTrack AI · Biomechanical Workout Coach",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* ── Hero Banner ───────────────────────────────────────────────── */
    .hero-banner {
        background: linear-gradient(135deg, #0A0F1D 0%, #0F1E2E 50%, #081622 100%);
        padding: 2.2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.8rem;
        border: 1px solid rgba(0, 245, 212, 0.35);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
    .hero-banner h1 {
        color: #00F5D4;
        font-size: 2.3rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .hero-banner p {
        color: #9FB3C8;
        font-size: 1.05rem;
        margin: 0.5rem 0 0 0;
    }

    /* ── Telemetry KPI Card ────────────────────────────────────────── */
    .telemetry-card {
        background: linear-gradient(145deg, #161B22 0%, #0D1117 100%);
        border: 1px solid rgba(0, 245, 212, 0.25);
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        transition: transform 0.2s, border-color 0.2s;
    }
    .telemetry-card:hover {
        transform: translateY(-2px);
        border-color: rgba(0, 245, 212, 0.6);
    }
    .telemetry-val {
        font-size: 2.5rem;
        font-weight: 800;
        color: #00F5D4;
    }
    .telemetry-label {
        font-size: 0.82rem;
        color: #8B949E;
        margin-top: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Coaching Banner */
    .coach-feedback-box {
        background: rgba(0, 245, 212, 0.08);
        border-left: 4px solid #00F5D4;
        padding: 14px 20px;
        border-radius: 8px;
        margin: 15px 0;
        font-size: 1.15rem;
        font-weight: 600;
        color: #F0F6FC;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════════════
#  Session State Initialization
# ═══════════════════════════════════════════════════════════════════════
if "angle_history" not in st.session_state:
    st.session_state.angle_history = deque([180.0] * 50, maxlen=60)
if "standalone_pose_tracker" not in st.session_state:
    st.session_state.standalone_pose_tracker = PoseTracker()
if "workout_history_log" not in st.session_state:
    st.session_state.workout_history_log = []
if "total_session_reps" not in st.session_state:
    st.session_state.total_session_reps = 0
if "last_coached_rep" not in st.session_state:
    st.session_state.last_coached_rep = 0

# ═══════════════════════════════════════════════════════════════════════
#  Hero Header
# ═══════════════════════════════════════════════════════════════════════
st.markdown(
    """
    <div class="hero-banner">
        <h1>💪 FitTrack AI — Workout Rep Counter & Posture Corrector</h1>
        <p>Real-time edge AI biomechanics tracking 33 skeletal landmarks, joint angle kinematics,
        MET calorie burning, and instant vocal form correction directly from your webcam.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════════════
#  Sidebar Controls
# ═══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🏋️ Workout Settings")
    st.markdown("---")

    selected_exercise = st.selectbox(
        "🎯 Select Exercise Routine",
        ["Squats", "Bicep Curls", "Push-ups", "Planks"],
        index=0,
    )

    user_weight = st.number_input(
        "⚖️ Your Bodyweight (kg)",
        min_value=40.0,
        max_value=150.0,
        value=70.0,
        step=1.0,
        help="Used to compute personalized MET calorie consumption.",
    )

    target_reps = st.slider(
        "🏁 Target Rep Goal",
        min_value=5,
        max_value=50,
        value=15,
        step=1,
    )

    enable_voice_coach = st.checkbox("🗣️ Audio Coach Vocal Cues", value=True)

    st.markdown("---")
    st.markdown("### 🏆 Session Cumulative Stats")
    st.metric("Total Reps Completed", st.session_state.total_session_reps)
    cal_burned = estimate_calories_burned(selected_exercise, st.session_state.total_session_reps, user_weight)
    st.metric("Estimated Calories Burned", f"{cal_burned} kcal")

    st.markdown("---")
    if st.button("🗑️ Reset Session Counters", use_container_width=True):
        st.session_state.total_session_reps = 0
        st.session_state.workout_history_log = []
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════
#  Application Tabs
# ═══════════════════════════════════════════════════════════════════════
tab_live, tab_snap, tab_analytics, tab_guide, tab_math = st.tabs(
    [
        "🔴 Live Workout Arena",
        "📸 Snapshot Posture Diagnostic",
        "📊 Session Analytics & Pace",
        "📖 Exercise Form Guide",
        "🔬 Biomechanical Mathematics",
    ]
)

# ─────────────────────────────────────────────────────────────────────
#  TAB 1 : Real-Time Live Workout Arena (Zero Upload Needed!)
# ─────────────────────────────────────────────────────────────────────
with tab_live:
    st.markdown(f"### 🔴 Live Tracking: **{selected_exercise}**")
    st.markdown(
        """
        <div style="background: rgba(0, 245, 212, 0.08); border-left: 4px solid #00F5D4; padding: 12px 18px; border-radius: 8px; margin-bottom: 20px;">
            <b style="color: #00F5D4; font-size: 1.05rem;">✨ Continuous Live Video — Zero File Uploads Needed!</b><br>
            Click <b>START</b> below. Stand in full view so your joints are visible. The AI automatically counts reps and provides instant vocal coaching!
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_vid, col_kpi = st.columns([1.5, 1.0])

    with col_vid:
        ctx = webrtc_streamer(
            key="fittrack-live-stream",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=RTC_CONFIGURATION,
            video_processor_factory=LiveWorkoutProcessor,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )

        if ctx.video_processor:
            ctx.video_processor.set_exercise(selected_exercise)

    with col_kpi:
        st.markdown("#### ⚡ Live Biomechanical Telemetry")

        if ctx.state.playing and ctx.video_processor:
            data = ctx.video_processor.get_telemetry()
            current_reps = data["reps"]
            current_stage = data["stage"]
            feedback_msg = data["feedback"]
            joint_angle = data["angle"]
            clean_form = data["form_is_clean"]
            acc_rate = data["accuracy_rate"]

            st.session_state.angle_history.append(joint_angle)

            # Vocal coach on new rep
            if data["new_rep"] is not None and enable_voice_coach:
                rep_num = data["new_rep"]
                st.session_state.total_session_reps += 1
                if rep_num == target_reps:
                    speak_coach_cue(f"Target goal of {target_reps} reps reached! Fantastic work!")
                else:
                    speak_coach_cue(f"Rep {rep_num}! {feedback_msg}")

            # Telemetry Cards
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(
                    f"""
                    <div class="telemetry-card">
                        <div class="telemetry-val">{current_reps}</div>
                        <div class="telemetry-label">Completed Reps</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(
                    f"""
                    <div class="telemetry-card">
                        <div class="telemetry-val" style="font-size: 1.8rem; color: {'#00F5D4' if current_stage == 'UP' else '#FEE440'};">{current_stage}</div>
                        <div class="telemetry-label">Movement Phase</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                f"""
                <div class="coach-feedback-box">
                    {'🟢' if clean_form else '⚠️'} Coach: {feedback_msg}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Accuracy score gauge
            st.plotly_chart(form_accuracy_gauge(acc_rate), use_container_width=True, key="live_acc_gauge")

            st.caption(f"⚡ Processing Cadence: **{data['fps']} FPS** | Joint Angle: **{int(joint_angle)}°**")

        else:
            st.markdown(
                """
                <div class="telemetry-card">
                    <div style="font-size: 2.5rem;">🏋️</div>
                    <div class="telemetry-val" style="color: #8B949E;">Camera Inactive</div>
                    <div class="telemetry-label">Click START on the left to begin your workout</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.plotly_chart(form_accuracy_gauge(100), use_container_width=True, key="idle_acc_gauge")

# ─────────────────────────────────────────────────────────────────────
#  TAB 2 : Snapshot Posture Diagnostic
# ─────────────────────────────────────────────────────────────────────
with tab_snap:
    st.markdown("### 📸 Biomechanical Photo Diagnostic")
    st.caption("Upload or capture a still photo to inspect 33 full-body landmarks, joint angles, and symmetry.")

    col_cam, col_up = st.columns(2)
    with col_cam:
        snap_cam = st.camera_input("Capture Athlete Pose", key="pose_cam_snap")
    with col_up:
        snap_up = st.file_uploader("Or Upload Pose Photo", type=["jpg", "png", "jpeg", "webp"])

    chosen_image = snap_cam or snap_up
    if chosen_image is not None:
        import numpy as np
        import cv2

        pil_img = Image.open(chosen_image).convert("RGB")
        bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        tracker = st.session_state.standalone_pose_tracker
        with st.spinner("Analyzing joint kinematics..."):
            annotated_frame, pose_data = tracker.process_frame(bgr, draw=True)

        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown("#### 🎯 33-Point Biomechanical Skeleton")
            st.image(annotated_frame, channels="BGR", use_container_width=True)

        with sc2:
            st.markdown("#### 📋 Kinematic Angle Measurements")
            if pose_data and pose_data.get("visible"):
                pts = pose_data["landmarks_px"]

                # Calculate left & right knee angles
                from kinematics import calculate_angle

                l_knee_angle = calculate_angle(pts.get(23, (0, 0)), pts.get(25, (0, 0)), pts.get(27, (0, 0))) if (23 in pts and 25 in pts and 27 in pts) else 180.0
                r_knee_angle = calculate_angle(pts.get(24, (0, 0)), pts.get(26, (0, 0)), pts.get(28, (0, 0))) if (24 in pts and 26 in pts and 28 in pts) else 180.0
                l_elbow_angle = calculate_angle(pts.get(11, (0, 0)), pts.get(13, (0, 0)), pts.get(15, (0, 0))) if (11 in pts and 13 in pts and 15 in pts) else 180.0

                m1, m2 = st.columns(2)
                m1.metric("Left Knee Angle", f"{l_knee_angle:.1f}°")
                m2.metric("Right Knee Angle", f"{r_knee_angle:.1f}°")

                st.metric("Left Elbow Angle", f"{l_elbow_angle:.1f}°")
                st.success("✅ Skeletal joints localized and mapped successfully!")
            else:
                st.warning("No athlete pose detected. Please ensure full body is visible in the frame.")

# ─────────────────────────────────────────────────────────────────────
#  TAB 3 : Session Analytics & Pace
# ─────────────────────────────────────────────────────────────────────
with tab_analytics:
    st.markdown("### 📊 Workout Kinematics & Caloric Telemetry")
    st.caption("Real-time joint extension trajectories and energy expenditure analysis.")

    st.plotly_chart(
        joint_angle_time_series(list(st.session_state.angle_history), selected_exercise),
        use_container_width=True,
    )

    c_met1, c_met2, c_met3 = st.columns(3)
    c_met1.metric("Total Completed Reps", st.session_state.total_session_reps)
    c_met2.metric("Target Goal Progress", f"{min(100, int((st.session_state.total_session_reps / max(1, target_reps)) * 100))}%")
    c_met3.metric("Energy Burned (kcal)", f"{estimate_calories_burned(selected_exercise, st.session_state.total_session_reps, user_weight)} kcal")

# ─────────────────────────────────────────────────────────────────────
#  TAB 4 : Exercise Form Guide
# ─────────────────────────────────────────────────────────────────────
with tab_guide:
    st.markdown("### 📖 Exercise Movement & Biomechanics Standards")

    guide_cols = st.columns(2)
    with guide_cols[0]:
        st.markdown(
            """
            #### 🏋️ Squats
            - **Starting Position**: Stand upright with knees extended (`> 160°`).
            - **Bottom Position**: Descend until thigh is parallel to floor (`< 95°`).
            - **Form Standard**: Keep chest upright; avoid excessive forward torso inclination (`< 45°`).
            ---
            #### 💪 Bicep Curls
            - **Starting Position**: Arms fully extended at side (`> 155°`).
            - **Top Position**: Curl dumbbell up towards shoulders (`< 40°`).
            - **Form Standard**: Pin elbows to ribcage; do not swing upper body.
            """
        )
    with guide_cols[1]:
        st.markdown(
            """
            #### 🧘 Push-ups
            - **Top Position**: Full arm lock-out (`> 160°`).
            - **Bottom Position**: Chest lowers to floor level (`< 90°`).
            - **Form Standard**: Maintain straight collinear line through shoulder, hip, and ankle.
            ---
            #### ⏱️ Planks
            - **Hold Alignment**: Spine angle between `160° - 195°`.
            - **Form Standard**: Engage glutes and core; do not let hips sag or pike upwards.
            """
        )

# ─────────────────────────────────────────────────────────────────────
#  TAB 5 : Biomechanical Mathematics
# ─────────────────────────────────────────────────────────────────────
with tab_math:
    st.markdown(
        """
        ### 🔬 Kinematic Vector Trigonometry Formulations

        #### 1. Joint Interior Angle Formulation
        Let vertex joint $B$ be connected to adjacent anatomical keypoints $A$ and $C$.
        We construct directional displacement vectors:

        $$\\mathbf{u} = A - B = (x_A - x_B, y_A - y_B)$$
        $$\\mathbf{v} = C - B = (x_C - x_B, y_C - y_B)$$

        The interior angle $\\theta$ is calculated via the inner product:

        $$\\theta = \\arccos\\left(\\frac{\\mathbf{u} \\cdot \\mathbf{v}}{\\|\\mathbf{u}\\| \\|\\mathbf{v}\\|}\\right) = \\arccos\\left(\\frac{u_x v_x + u_y v_y}{\\sqrt{u_x^2 + u_y^2} \\sqrt{v_x^2 + v_y^2}}\\right)$$

        ---

        #### 2. Spine & Core Collinearity Assessment
        To ensure zero lumbar hyperextension during pushups and planks, collinearity of
        Shoulder ($S$), Hip ($H$), and Ankle ($A$) is monitored:

        $$\\text{Spine Angle} = \\angle(S, H, A) \\in [160^\\circ, 195^\\circ]$$

        ---

        <div style="text-align: center; color: #8B949E; padding: 1rem;">
            Built with ❤️ for Biomechanics, Physiotherapy & Athletic AI · 2026
        </div>
        """,
        unsafe_allow_html=True,
    )
