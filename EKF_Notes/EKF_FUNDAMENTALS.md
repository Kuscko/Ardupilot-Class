# Extended Kalman Filter (EKF) Fundamentals

## What is the EKF?

The Extended Kalman Filter (EKF) is a sensor fusion algorithm that combines data from multiple sensors to estimate the vehicle's state (position, velocity, orientation) more accurately than any single sensor can provide.

**In simple terms:** The EKF is the "brain" that figures out where the aircraft is and how it's moving by intelligently combining GPS, IMU, barometer, compass, and other sensor data.

---

## Why Do We Need the EKF?

### The Problem: Sensor Imperfections

Every sensor has weaknesses:

| Sensor | Strength | Weakness |
|--------|----------|----------|
| **GPS** | Accurate absolute position | Slow update rate (5-20 Hz), ~2m error, lag |
| **Accelerometer** | Very fast (400+ Hz), sensitive | Drifts over time, affected by vibration |
| **Gyroscope** | Fast, measures rotation accurately | Drifts over time |
| **Barometer** | Good relative altitude | Affected by weather, temperature |
| **Compass** | Provides heading reference | Interference from magnets, metal |

### The Solution: Sensor Fusion

The EKF combines all sensors, accounting for:
- Each sensor's update rate
- Each sensor's accuracy (measurement noise)
- Physics constraints (aircraft can't teleport)
- Correlation between measurements

**Result:** Position/orientation estimate that's better than any single sensor.

---

## How the EKF Works

### Core Concept: Predict + Update

The EKF runs in two steps:

#### 1. **Prediction Step**

Use physics and previous state to predict current state:

```
Predicted Position = Previous Position + (Velocity × Time)
Predicted Velocity = Previous Velocity + (Acceleration × Time)
```

This uses **IMU data** (accelerometers and gyroscopes).

#### 2. **Update Step (Correction)**

Compare prediction with actual sensor measurements:

```
GPS says: "You're at 35.328°N, -119.003°W"
EKF predicted: "You're at 35.327°N, -119.004°W"

EKF combines both, weighted by confidence in each
Final estimate: "You're at 35.3278°N, -119.0035°W"
```

The EKF "trusts" sensors based on their expected accuracy.

---

## EKF in ArduPilot

ArduPilot uses **EKF3** (third generation Extended Kalman Filter), located in the `AP_NavEKF3` library.

### What EKF3 Estimates

EKF3 provides these critical estimates:

| State | Description |
|-------|-------------|
| **Position** | Latitude, longitude, altitude |
| **Velocity** | North, East, Down velocities |
| **Orientation** | Roll, pitch, yaw (attitude) |
| **Angular Rates** | Roll rate, pitch rate, yaw rate |
| **IMU Biases** | Accelerometer and gyro biases (drift correction) |
| **Wind** | Estimated wind speed and direction |
| **Magnetic Field** | Earth magnetic field + offsets |

### EKF3 Inputs (Sensors)

| Sensor | Provides | Update Rate |
|--------|----------|-------------|
| **IMU** | Acceleration, angular velocity | 400+ Hz |
| **GPS** | Position, velocity | 5-20 Hz |
| **Barometer** | Altitude | 20-100 Hz |
| **Compass** | Heading | 10-75 Hz |
| **Airspeed** | Forward airspeed | 10-50 Hz |
| **Rangefinder** | Height above ground | 10-50 Hz (if equipped) |
| **Optical Flow** | Velocity over ground | 10-30 Hz (if equipped) |

---

## EKF3 Parameters

### Core EKF3 Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| **EK3_ENABLE** | 1 | Enable EKF3 (1=enabled) |
| **EK3_IMU_MASK** | 3 | Which IMUs to use (bitmask) |
| **EK3_ALT_SOURCE** | 0 | Primary altitude source (0=baro, 1=rangefinder, 2=GPS, 3=beacon) |
| **EK3_GPS_TYPE** | 0 | GPS mode (0=3D fix, 1=2D fix, 2=no GPS, 3=fallback) |

### Sensor Weighting

These parameters control how much the EKF trusts each sensor:

| Parameter | Default | Description | Effect |
|-----------|---------|-------------|--------|
| **EK3_ACC_P_NSE** | 0.35 | Accelerometer noise (m/s²) | ↑ = trust accel less |
| **EK3_GYRO_P_NSE** | 0.015 | Gyroscope noise (rad/s) | ↑ = trust gyro less |
| **EK3_GPS_VACC_MAX** | 10.0 | Max GPS vertical accuracy (m) | GPS rejected if worse |
| **EK3_GPS_HACC_MAX** | 10.0 | Max GPS horizontal accuracy (m) | GPS rejected if worse |
| **EK3_BARO_ALT_NOISE** | 0.5 | Barometer altitude noise (m) | ↑ = trust baro less |
| **EK3_MAG_CAL** | 3 | Compass calibration mode | 0=no calibration, 3=auto, 5=use world magnetic model |

### Innovation Limits

"Innovation" = difference between prediction and measurement

| Parameter | Default | Description |
|-----------|---------|-------------|
| **EK3_POSNE_M_NSE** | 0.5 | GPS horizontal position noise (m) |
| **EK3_VELD_M_NSE** | 0.7 | GPS vertical velocity noise (m/s) |
| **EK3_VELNE_M_NSE** | 0.5 | GPS horizontal velocity noise (m/s) |

---

## EKF Health Monitoring

### Pre-Arm Checks

Before arming, ArduPilot checks EKF health. Common pre-arm failures:

| Message | Cause | Solution |
|---------|-------|----------|
| **PreArm: EKF attitude variance** | Orientation estimate uncertain | Wait for GPS lock, check compass calibration |
| **PreArm: EKF velocity variance** | Velocity estimate uncertain | Wait longer, ensure GPS has good fix |
| **PreArm: EKF position variance** | Position estimate uncertain | Wait for GPS lock, check GPS antenna |
| **PreArm: EKF compass variance** | Compass inconsistent | Calibrate compass, check for interference |

### EKF Variance

**Variance = measure of uncertainty**

- Low variance = confident estimate
- High variance = uncertain estimate

The EKF tracks variance for:
- Position
- Velocity
- Attitude (orientation)
- Compass

Arming is blocked if variances exceed thresholds.

---

## Common EKF Issues

### Issue: EKF Won't Allow Arming

**Symptoms:** "PreArm: EKF variance" errors

**Causes:**
- GPS not locked or poor signal
- Compass not calibrated
- Excessive vibration
- Vehicle moved before GPS lock

**Solutions:**
```bash
# Wait for good GPS
# Console should show "GPS: 3D Fix"

# Check GPS status
param show GPS_*

# Calibrate compass (in GCS)
# Or force arm in SITL
arm throttle force
```

### Issue: EKF Resets In Flight

**Symptoms:** Sudden position jumps, mode switches to LAND

**Causes:**
- GPS glitch or loss
- Excessive vibration
- Magnetic interference
- Sensor failure

**Solutions:**
- Review logs for sensor health
- Check vibration levels
- Improve GPS antenna placement
- Calibrate sensors properly

### Issue: Poor Position Hold

**Symptoms:** Aircraft drifts in LOITER or position-based modes

**Causes:**
- Poor GPS accuracy
- Incorrect compass calibration
- Wind estimation errors
- EKF not trusting GPS enough

**Solutions:**
- Verify GPS HDOP < 2.0 (good accuracy)
- Recalibrate compass away from metal/magnets
- Adjust EK3_GPS_HACC_MAX if GPS is actually good

---

## EKF Logging and Analysis

### Enable EKF Logging

```bash
# Log EKF data
param set LOG_BITMASK 65535  # Log everything (for debugging)
```

### Key Log Messages

When analyzing EKF issues in logs:

| Log Message | Contains |
|-------------|----------|
| **EKF1-5** | EKF status, variance, innovations |
| **GPS** | GPS fix, satellites, accuracy |
| **IMU** | Accelerometer, gyroscope data |
| **MAG** | Compass readings |
| **BARO** | Barometer altitude |

### Viewing Logs

**Mission Planner:**
- Connect to vehicle or load log file
- Review EKF messages in log browser
- Check for variance spikes

**MAVExplorer:**
```bash
# In SITL or with log files
mavexplorer.py logfile.bin
# Plot EKF variance over time
```

---

## EKF Tuning (Advanced)

### When to Tune EKF

**Generally: Don't tune EKF unless you have a specific problem.**

Defaults work well for most vehicles. Tune only if:
- Persistent pre-arm failures
- Position hold is poor despite good GPS
- EKF variances too high in flight
- Known sensor noise characteristics differ from defaults

### How to Tune

**Process:**
1. **Identify the problem sensor** from logs
2. **Adjust noise parameter** for that sensor
3. **Test and validate**

**Example:** GPS is glitchy, EKF trusts it too much

```bash
# Increase GPS noise (trust it less)
param set EK3_GPS_HACC_MAX 5.0  # Stricter GPS accuracy requirement
param set EK3_POSNE_M_NSE 1.0   # Increase GPS position noise
```

**Example:** Vibration causing accelerometer issues

```bash
# Increase accelerometer noise (trust less)
param set EK3_ACC_P_NSE 0.5  # Default 0.35
```

---

## EKF vs AHRS

**AHRS (Attitude Heading Reference System):** Simpler algorithm, only estimates attitude (roll, pitch, yaw).

**EKF:** Full state estimator, estimates position, velocity, attitude, biases, wind.

**In ArduPilot:**
- EKF provides all navigation data
- AHRS uses EKF output for attitude
- `AP_AHRS` library is the interface to EKF

---

## EKF Math (Optional Deep Dive)

### Kalman Filter Equations

**State prediction:**
```
x̂(k|k-1) = F(k) × x̂(k-1|k-1) + B(k) × u(k)
P(k|k-1) = F(k) × P(k-1|k-1) × F(k)ᵀ + Q(k)
```

**Update (correction):**
```
K(k) = P(k|k-1) × H(k)ᵀ × [H(k) × P(k|k-1) × H(k)ᵀ + R(k)]⁻¹
x̂(k|k) = x̂(k|k-1) + K(k) × [z(k) - H(k) × x̂(k|k-1)]
P(k|k) = [I - K(k) × H(k)] × P(k|k-1)
```

**Where:**
- `x̂` = state estimate
- `P` = covariance (uncertainty)
- `F` = state transition matrix
- `H` = observation matrix
- `K` = Kalman gain
- `Q` = process noise
- `R` = measurement noise
- `z` = measurement

**Extended Kalman Filter:** Uses linearization for non-linear systems (like aircraft dynamics).

---

## Resources

### ArduPilot EKF Documentation

- [EKF3 Overview](https://ardupilot.org/plane/docs/ekf3.html)
- [EKF Failsafe](https://ardupilot.org/plane/docs/ekf-failsafe.html)
- [Compass Calibration](https://ardupilot.org/plane/docs/common-compass-calibration-in-mission-planner.html)

### Academic Resources

- Kalman Filter explanation: https://www.kalmanfilter.net/
- Extended Kalman Filter tutorial
- Sensor fusion theory

### Code Reference

- `libraries/AP_NavEKF3/` - EKF3 implementation
- `libraries/AP_AHRS/` - AHRS interface to EKF

---

## Summary

**Key Takeaways:**

1. **EKF combines all sensors** to estimate position, velocity, and orientation
2. **Each sensor has noise parameters** that control trust level
3. **Pre-arm checks verify EKF confidence** before allowing flight
4. **Default parameters work for most vehicles** - tune only if needed
5. **Logs contain EKF data** for troubleshooting issues
6. **Good GPS and compass calibration** are critical for EKF performance

**For new engineers:**
- Focus on understanding what EKF does (sensor fusion)
- Learn to interpret pre-arm messages
- Practice compass and accelerometer calibration
- Review logs after flights
- Don't modify EKF parameters without good reason

---

**Last Updated:** 2026-02-03
**Target Version:** Plane 4.5.7
