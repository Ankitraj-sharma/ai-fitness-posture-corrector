# FitTrack AI - Real-Time AI Fitness & Posture Form Corrector 🏋️‍♂️📊

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose%20Estimation-orange.svg)](https://developers.google.com/mediapipe)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](Dockerfile)

> **Real-time bio-mechanical posture assessment, dynamic repetition counter, and automated synthetic voice coach powered by 33-point MediaPipe BlazePose and mathematical vector kinematics.** Zero manual file uploads required—just click **START** on the webcam feed and begin training!

---

## 🎯 Key Capabilities

1. **Zero-Upload Continuous Webcam Stream:**
   - Powered by **Streamlit WebRTC (`streamlit-webrtc`)** and dual STUN server ICE negotiation.
   - Low-latency client-server frames processing at 25–30 FPS.
2. **Sub-Degree Vector Kinematics:**
   - Inner product vector calculations: $\theta = \arccos\left(\frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|}\right)$.
   - Real-time joint angle tracking (knee flexion, hip hinge, elbow flexion, lumbar collinearity, and vertical inclination).
3. **Multi-Exercise Finite-State Machine (FSM):**
   - **Squats:** Depth verification ($\le 95^\circ$), knee valgus/caving detection, chest inclination monitoring.
   - **Bicep Curls:** Full extension ($160^\circ$) to peak contraction ($\le 45^\circ$), momentum cheat/elbow swing detection.
   - **Push-ups:** Chest depth ($\le 90^\circ$), lumbar spine collinearity ($\ge 160^\circ$) to prevent back hyperextension.
   - **Planks:** Real-time isometric hold stopwatch, hip sag and butt pike detection.
4. **Autonomous Voice Coach:**
   - Client-side Web Speech API vocal cues (`"Chest up"`, `"Go lower"`, `"Keep back straight"`).
   - Audio synthesized locally in browser with zero cloud latency.
5. **Interactive Fitness Analytics:**
   - Dynamic calorie burn estimation using metabolic equivalents of task (MET).
   - Plotly interactive joint angle trajectory charts and rep breakdown logs.

---

## 📐 Vector Kinematics Mathematics

Joint angles are computed dynamically between three key landmark vectors: $A$ (proximal), $B$ (vertex joint), and $C$ (distal):

$$\mathbf{u} = A - B = [x_A - x_B, y_A - y_B]$$
$$\mathbf{v} = C - B = [x_C - x_B, y_C - y_B]$$

$$\theta = \arccos\left(\frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|}\right) \times \frac{180^\circ}{\pi}$$

### Spine Collinearity Index
To ensure spinal alignment during push-ups and planks, the angle formed by shoulder ($S$), hip ($H$), and ankle ($A$) must satisfy:

$$\theta_{\text{spine}} = \angle(S, H, A) \ge 160^\circ$$

Deviation below $150^\circ$ triggers an immediate **"Sagging Hips"** audio alert, while $\theta_{\text{spine}} \le 140^\circ$ with elevated hips triggers a **"Pike Hips"** alert.

---

## 🏋️‍♂️ Supported Exercises & Biomechanical Standards

| Exercise | Target Joint | Down / Rep Threshold | Up / Reset Threshold | Form Check Violations |
| :--- | :--- | :--- | :--- | :--- |
| **Squat** | Hip-Knee-Ankle | $\le 95^\circ$ (Deep) | $\ge 160^\circ$ (Standing) | Shallow depth, chest collapsed ($< 45^\circ$) |
| **Bicep Curl** | Shoulder-Elbow-Wrist | $\le 45^\circ$ (Contracted) | $\ge 155^\circ$ (Extended) | Elbow swing / momentum cheat ($> 30\text{ px}$) |
| **Push-Up** | Shoulder-Elbow-Wrist | $\le 85^\circ$ (Chest Down) | $\ge 160^\circ$ (Plank Lockout) | Spinal curvature / hip sag ($< 155^\circ$) |
| **Plank** | Shoulder-Hip-Ankle | Isometric Hold | Continuous Timer | Hip sagging ($< 155^\circ$), Butt piking ($< 150^\circ$) |

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/Ankitraj-sharma/ai-fitness-posture-corrector.git
cd ai-fitness-posture-corrector
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🐳 Docker Deployment

Run seamlessly in a containerized environment with hardware camera forwarding:

```bash
docker-compose up --build
```
The application will be served at `http://localhost:8501`.

---

## 🧪 Running Unit Tests & Benchmarks

```bash
# Run kinematics unit test suite
python -m unittest test_kinematics.py

# Run solver latency benchmark
python benchmark.py
```

---

## 📜 License
Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
