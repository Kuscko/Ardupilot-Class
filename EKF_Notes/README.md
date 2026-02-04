# Extended Kalman Filter (EKF)

## Overview

The Extended Kalman Filter is ArduPilot's primary state estimation system, fusing data from GPS, IMU, barometer, compass, and other sensors to provide accurate position, velocity, and attitude estimates [1]. EKF3 is the current implementation used in ArduPilot Plane 4.5.7, offering improved performance and reliability over previous versions.

## Prerequisites

Before starting this module, you should:

- Have completed SITL setup and be comfortable running simulations
- Understand basic flight dynamics (position, velocity, attitude)
- Be familiar with sensor types (GPS, IMU, barometer, compass)
- Know how to view and modify ArduPilot parameters

## What You'll Learn

By completing this module, you will:

- Understand how EKF works and why sensor fusion is important
- Identify the key sensors used by EKF3 and their roles
- Configure critical EKF parameters (EK3_* family)
- Diagnose EKF health issues and interpret status messages
- Resolve common pre-arm failures related to EKF
- Test EKF behavior in different scenarios (GPS-denied, sensor failures)

## Key Concepts

### Sensor Fusion

EKF combines multiple noisy sensor measurements to produce more accurate estimates than any single sensor could provide [2]. The fundamental principle is that different sensors have different strengths and weaknesses:

- **GPS:** Provides absolute position but updates slowly (5-10 Hz) and can be noisy
- **IMU (Inertial Measurement Unit):** High-rate updates (400+ Hz) for acceleration and rotation, but drifts over time
- **Barometer:** Measures altitude accurately but affected by weather and temperature
- **Compass:** Provides heading reference but susceptible to magnetic interference
- **Airspeed (planes):** Measures forward velocity, important for fixed-wing flight

By fusing these sensors, EKF can provide smooth, accurate estimates at high update rates [1].

### Prediction and Update Cycle

EKF operates in a continuous two-step process:

1. **Predict:** Use IMU measurements to predict state changes (position, velocity, attitude) based on vehicle motion
2. **Update:** When GPS, barometer, or compass measurements arrive, compare them to predictions and correct any errors
3. **Repeat:** Run this cycle continuously at high frequency (typically 400 Hz)

This approach combines the high-rate responsiveness of IMU with the absolute accuracy of GPS and other sensors [2].

### EKF Health Monitoring

ArduPilot continuously monitors EKF health through several checks:

- **Innovation Checks:** Detect when sensor measurements differ significantly from predictions (may indicate sensor failure)
- **Variance Tracking:** Monitor uncertainty in position/velocity estimates
- **Sensor Status:** Verify GPS quality, number of satellites, and sensor availability
- **Lane Switching:** EKF3 runs multiple parallel estimators and switches to the healthiest one [1]

## Hands-On Practice

### Exercise 1: Monitor EKF Health in SITL

Start SITL and observe EKF status:

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py -v ArduPlane
```

In MAVProxy console, check EKF status:

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

**Key Indicators:**
- **AIDING:** EKF is successfully using GPS for position updates
- **Low variance:** Position estimates are confident (<1.0 is good)
- **Primary lane 0:** Using the first of multiple parallel estimators

### Exercise 2: View EKF Parameters

List all EKF3 parameters:

```
param show EK3_*
```

**Key Parameters to Note:**
- `EK3_ENABLE`: Enable/disable EKF3 (should be 1)
- `EK3_SRC1_*`: Configure primary sensor sources
- `EK3_GPS_TYPE`: GPS usage mode
- `EK3_ALT_SOURCE`: Primary altitude source
- `EK3_MAG_CAL`: Magnetometer (compass) learning mode

### Exercise 3: GPS-Denied Environment

Test EKF behavior when GPS is unavailable:

```bash
# Load GPS-denied parameters
param load ekf_params_gps_denied.param
param set SIM_GPS_DISABLE 1
reboot
```

After reboot, check EKF status:

```
EKF3 CHECK 0
```

**Expected Behavior:**
- EKF will switch to non-GPS aiding modes
- May use optical flow, visual odometry, or other sensors if available
- Position accuracy will degrade without GPS

**Restore GPS:**
```
param set SIM_GPS_DISABLE 0
reboot
```

### Exercise 4: Monitor EKF with Python Script

Use the provided test script to monitor EKF status:

```bash
cd ~/Desktop/Work/AEVEX/EKF_Notes
python3 ekf_test.py --connect tcp:127.0.0.1:5760
```

This script displays real-time EKF status including variance levels, innovation checks, and sensor health.

## Configuration Files

This module includes several configuration files:

- **[ekf_params_default.param](ekf_params_default.param)** - Standard EKF3 configuration for typical flight
- **[ekf_params_gps_denied.param](ekf_params_gps_denied.param)** - Configuration for GPS-denied environments
- **[ekf_test.py](ekf_test.py)** - Python script for monitoring EKF status via MAVLink

## Complete Guide

See **[EKF_FUNDAMENTALS.md](EKF_FUNDAMENTALS.md)** for comprehensive documentation including:

- Detailed explanation of EKF theory
- Complete parameter reference
- Sensor configuration guidelines
- Advanced troubleshooting techniques
- Pre-arm check interpretation

## Common Issues

### Issue: "EKF3 IMU1 stopped aiding"

**Symptom:** Pre-arm check fails with "EKF stopped aiding" message

**Common Causes:**
- GPS signal lost (too few satellites, indoors)
- GPS quality degraded (high HDOP, poor geometry)
- Velocity innovations too high

**Solutions:**
1. Check GPS status: `gps 0` in MAVProxy
2. Verify minimum 6 satellites visible
3. Check HDOP < 2.0 for good GPS quality
4. Ensure GPS antenna has clear view of sky
5. Wait for GPS to stabilize after power-on

### Issue: "EKF variance high"

**Symptom:** EKF reports high position or velocity variance

**Common Causes:**
- Inconsistent sensor measurements
- Compass interference or poor calibration
- Excessive vibration affecting IMU
- Conflicting sensor inputs

**Solutions:**
1. Calibrate compass: `accelcal` in MAVProxy
2. Check for vibration in logs (should be <30 m/s²)
3. Verify compass orientation parameters
4. Check for magnetic interference (power wires, motors)
5. Consider disabling compass if unreliable: `EK3_MAG_CAL = 5`

### Issue: "EKF primary changed"

**Symptom:** EKF switches between lanes (parallel estimators)

**Cause:** EKF detected one lane is healthier than the current primary

**What it means:**
- Usually indicates temporary sensor issues
- EKF is working correctly by switching to best estimate
- Frequent switching may indicate sensor problems

**Solutions:**
1. Monitor which sensor is causing issues
2. Check logs for innovation failures
3. Verify all sensors are properly calibrated
4. Consider sensor-specific troubleshooting

### Issue: Pre-arm check fails: "EKF compass variance"

**Symptom:** Cannot arm vehicle due to compass variance

**Solutions:**
1. Perform compass calibration in multiple orientations
2. Move away from magnetic interference sources
3. Verify compass orientation with `COMPASS_ORIENT` parameter
4. Check compass health: `compassmot` test (hardware only)
5. As last resort, disable compass: `EK3_MAG_CAL = 5` (GPS heading only)

See **[EKF_FUNDAMENTALS.md](EKF_FUNDAMENTALS.md)** for complete troubleshooting guide.

## Additional Resources

### Official ArduPilot Documentation

- **[ArduPilot EKF3 Documentation](https://ardupilot.org/plane/docs/ekf3.html)** [1] - Overview and configuration
- **[EKF3 Parameters](https://ardupilot.org/plane/docs/parameters.html#ek3-parameters)** [2] - Complete parameter reference
- **[Extended Kalman Filter Theory](https://ardupilot.org/dev/docs/extended-kalman-filter.html)** [3] - Developer documentation
- **[Pre-arm Safety Checks](https://ardupilot.org/plane/docs/common-prearm-safety-checks.html)** [4] - Understanding pre-arm failures

### Understanding EKF in Depth

- **[Sensor Fusion Overview](https://ardupilot.org/dev/docs/sensor-fusion.html)** - How sensors work together
- **[GPS Configuration](https://ardupilot.org/plane/docs/common-gps-how-it-works.html)** - GPS setup and troubleshooting
- **[Compass Setup](https://ardupilot.org/plane/docs/common-compass-setup-advanced.html)** - Advanced compass configuration

### Community Resources

- [ArduPilot Discord](https://ardupilot.org/discord) - Real-time support
- [Discourse Forums: EKF Topics](https://discuss.ardupilot.org/c/arduplane/15) - Community Q&A
- [ArduPilot Blog: EKF Articles](https://ardupilot.org/dev/docs/common-blogs.html) - Technical deep dives

## Next Steps

After completing this EKF module:

1. **Practice in SITL** - Experiment with different EKF configurations and sensor failures
2. **Analyze Logs** - Learn to interpret EKF data in flight logs ([Flight Log Analysis](../Advanced_Topics/Flight_Log_Analysis/))
3. **Advanced Navigation** - Understand how EKF enables autonomous navigation ([Navigation Deep Dive](../Advanced_Topics/Navigation_Deep_Dive/))
4. **Hardware Testing** - Apply EKF knowledge to real flight controller hardware

---

**Sources:**

[1] https://ardupilot.org/plane/docs/ekf3.html
[2] https://ardupilot.org/plane/docs/parameters.html
[3] https://ardupilot.org/dev/docs/extended-kalman-filter.html
[4] https://ardupilot.org/plane/docs/common-prearm-safety-checks.html
