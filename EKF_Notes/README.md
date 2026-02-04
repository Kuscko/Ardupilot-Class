# EKF Notes — Agent Onboarding

## Purpose
Document key concepts, findings, and troubleshooting related to ArduPilot's Extended Kalman Filter (EKF) as you onboard.

## Agent Instructions & TODO List

### 1. EKF Fundamentals
- [x] Summarize what the EKF does in ArduPilot (see onboarding guide Week 2)
- [x] List the main sensors used by EKF (GPS, IMU, Barometer, Compass)
- [x] Explain how EKF fuses sensor data and why it is important

### 2. EKF Parameters & Tuning
- [x] Identify key EKF parameters (EK3_*) and their functions
- [x] Document any parameter changes made during SITL or flight testing

### 3. Troubleshooting
- [x] Record any EKF-related issues encountered (e.g., pre-arm failures, sensor errors)
- [x] Add solutions or references for resolving EKF issues

**Deliverables:** [EKF_FUNDAMENTALS.md](EKF_FUNDAMENTALS.md), [ekf_params_default.param](ekf_params_default.param), [ekf_params_gps_denied.param](ekf_params_gps_denied.param), [ekf_test.py](ekf_test.py)

### 4. References
- [EKF Overview in Onboarding Guide](../../Onboarding_Documentation/ArduPilot_Onboarding_Guide.md)
- [ArduPilot EKF3 Documentation](https://ardupilot.org/plane/docs/ekf3.html)

---
**Update this README as you learn and test EKF features.**