"""
Performance Benchmark for FitTrack AI Kinematic Pipeline.
Measures latency for joint angle calculation and state machine transitions.
"""

import time
from exercises import SquatTracker, BicepCurlTracker, PushupTracker
from kinematics import calculate_angle


def run_kinematic_benchmark(iterations: int = 2000):
    print(f"[*] Benchmarking {iterations} iterations of athletic kinematic solvers...")

    a, b, c = (120, 240), (160, 320), (180, 440)
    t0 = time.perf_counter()
    for _ in range(iterations):
        _ = calculate_angle(a, b, c)
    angle_latency_ms = (time.perf_counter() - t0) * 1000 / iterations

    # Squat state machine
    tracker = SquatTracker()
    landmarks = {23: a, 25: b, 27: c, 11: (120, 100)}
    t0 = time.perf_counter()
    for _ in range(iterations):
        _ = tracker.process(landmarks)
    tracker_latency_ms = (time.perf_counter() - t0) * 1000 / iterations

    print(f"[-] Joint Vector Angle Solver: {angle_latency_ms:.5f} ms")
    print(f"[-] Full Exercise State Machine: {tracker_latency_ms:.5f} ms")
    total_latency = angle_latency_ms + tracker_latency_ms
    print(f"[+] Total Kinematic Compute:    {total_latency:.5f} ms ({1000/total_latency:.0f} FPS theoretical)")


if __name__ == "__main__":
    run_kinematic_benchmark()
