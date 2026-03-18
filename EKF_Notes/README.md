# Extended Kalman Filter (EKF)

## Overview

EKF3 is ArduPilot's primary state estimation system, fusing GPS, IMU, barometer, compass, and other sensors to produce accurate position, velocity, and attitude estimates. It is the current implementation in ArduPilot Plane 4.5.7.

## Prerequisites

- Completed SITL setup
- Familiar with sensor types (GPS, IMU, barometer, compass)
- Know how to view and modify ArduPilot parameters

## Key Concepts

### Sensor Fusion

Different sensors have complementary strengths: GPS gives absolute position at low rate; IMU gives high-rate motion data but drifts; barometer gives altitude but is weather-sensitive; compass gives heading but is interference-prone. EKF combines all of them for accurate, high-rate estimates.

### Prediction and Update Cycle

1. **Predict:** Use IMU to predict state changes
2. **Update:** Correct predictions using GPS, barometer, or compass
3. **Repeat:** At high frequency (~400 Hz)

### EKF Health Monitoring

- **Innovation Checks:** Detect large sensor-vs-prediction discrepancies
- **Variance Tracking:** Monitor uncertainty in estimates
- **Sensor Status:** Verify GPS quality and sensor availability
- **Lane Switching:** EKF3 runs multiple parallel estimators and selects the healthiest

## Hands-On Practice

### Exercise 1: Monitor EKF Health in SITL

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py -v ArduPlane
```

In MAVProxy console:

```
EKF3 CHECK 0
```

**Expected Output:**
```
EKF3 IMU0 is using GPS
EKF3 lanes: primary=0 AIDING
EKF3 variance: horizontal=0.5 vertical=0.8
EKF3 origin: 51.8 deg, -35.4 deg
```

### Exercise 2: View EKF Parameters

```
param show EK3_*
```

Key parameters: `EK3_ENABLE`, `EK3_SRC1_*`, `EK3_GPS_TYPE`, `EK3_ALT_SOURCE`, `EK3_MAG_CAL`

### Exercise 3: GPS-Denied Environment

```bash
param set SIM_GPS_DISABLE 1
reboot
```

Check EKF status after reboot — it switches to non-GPS aiding modes and position accuracy degrades.

```
param set SIM_GPS_DISABLE 0
reboot
```

### Exercise 4: Monitor EKF with Python Script

```bash
cd ~/Desktop/Work/AEVEX/EKF_Notes
python3 ekf_test.py --connect tcp:127.0.0.1:5760
```

## Configuration Files

- **[ekf_params_default.param](ekf_params_default.param)** - Standard EKF3 configuration
- **[ekf_params_gps_denied.param](ekf_params_gps_denied.param)** - GPS-denied configuration
- **[ekf_test.py](ekf_test.py)** - Python EKF monitoring script

## Complete Guide

See **[EKF_FUNDAMENTALS.md](EKF_FUNDAMENTALS.md)** for full parameter reference, theory, and troubleshooting.

## Common Issues

### "EKF3 IMU1 stopped aiding"

**Causes:** GPS lost, too few satellites, high HDOP

**Solutions:**

1. Check GPS: `gps 0` in MAVProxy
2. Verify 6+ satellites visible and HDOP < 2.0
3. Ensure GPS antenna has clear sky view

### "EKF variance high"

**Causes:** Inconsistent sensors, compass interference, excessive vibration

**Solutions:**
1. Calibrate compass: `accelcal` in MAVProxy
2. Check vibration in logs (< 30 m/s²)
3. Check for magnetic interference (power wires, motors)
4. Consider `EK3_MAG_CAL = 5` if compass is unreliable

### "EKF primary changed"

EKF switched to a healthier parallel estimator — usually a temporary sensor issue. Frequent switching indicates a sensor problem; check logs for innovation failures.

### Pre-arm: "EKF compass variance"

1. Perform compass calibration in multiple orientations
2. Move away from interference sources
3. Verify `COMPASS_ORIENT`
4. Last resort: `EK3_MAG_CAL = 5` (GPS heading only)

## Additional Resources

- [ArduPilot EKF3 Documentation](https://ardupilot.org/plane/docs/ekf3.html)
- [EKF3 Parameters](https://ardupilot.org/plane/docs/parameters.html#ek3-parameters)
- [Extended Kalman Filter Theory](https://ardupilot.org/dev/docs/extended-kalman-filter.html)
- [Pre-arm Safety Checks](https://ardupilot.org/plane/docs/common-prearm-safety-checks.html)
- [GPS Configuration](https://ardupilot.org/plane/docs/common-gps-how-it-works.html)
- [Compass Setup](https://ardupilot.org/plane/docs/common-compass-setup-advanced.html)

## Next Steps

1. Analyze flight logs — [Flight Log Analysis](../Advanced_Topics/Flight_Log_Analysis/)
2. Advanced navigation — [Navigation Deep Dive](../Advanced_Topics/Navigation_Deep_Dive/)
3. Apply EKF knowledge to real flight controller hardware

---

**Sources:**

[1] https://ardupilot.org/plane/docs/ekf3.html
[2] https://ardupilot.org/plane/docs/parameters.html
[3] https://ardupilot.org/dev/docs/extended-kalman-filter.html
[4] https://ardupilot.org/plane/docs/common-prearm-safety-checks.html
