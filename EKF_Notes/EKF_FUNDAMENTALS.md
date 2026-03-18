# Extended Kalman Filter (EKF) Fundamentals

## What is the EKF?

The Extended Kalman Filter (EKF) is a sensor fusion algorithm that combines GPS, IMU, barometer, compass, and other sensor data to estimate position, velocity, and orientation more accurately than any single sensor.

---

## Sensor Limitations and the Need for Fusion

| Sensor | Strength | Weakness |
|--------|----------|----------|
| **GPS** | Accurate absolute position | Slow (5-20 Hz), ~2m error, lag |
| **Accelerometer** | Very fast (400+ Hz) | Drifts over time, vibration-sensitive |
| **Gyroscope** | Measures rotation accurately | Drifts over time |
| **Barometer** | Good relative altitude | Affected by weather, temperature |
| **Compass** | Heading reference | Interference from magnets, metal |

The EKF combines all sensors, accounting for update rates, accuracy, physics constraints, and measurement correlation.

---

## How the EKF Works

### Predict + Update Cycle

**1. Prediction Step** (uses IMU):

```
Predicted Position = Previous Position + (Velocity × Time)
Predicted Velocity = Previous Velocity + (Acceleration × Time)
```

**2. Update Step** (correction against sensor measurements):

```
GPS says: "You're at 35.328°N, -119.003°W"
EKF predicted: "You're at 35.327°N, -119.004°W"

EKF combines both, weighted by confidence in each
Final estimate: "You're at 35.3278°N, -119.0035°W"
```

---

## EKF in ArduPilot

ArduPilot uses **EKF3** (`AP_NavEKF3` library).

### EKF3 State Estimates

| State | Description |
|-------|-------------|
| **Position** | Latitude, longitude, altitude |
| **Velocity** | North, East, Down |
| **Orientation** | Roll, pitch, yaw |
| **Angular Rates** | Roll, pitch, yaw rates |
| **IMU Biases** | Accelerometer and gyro drift correction |
| **Wind** | Speed and direction |
| **Magnetic Field** | Earth field + offsets |

### EKF3 Inputs

| Sensor | Provides | Update Rate |
|--------|----------|-------------|
| **IMU** | Acceleration, angular velocity | 400+ Hz |
| **GPS** | Position, velocity | 5-20 Hz |
| **Barometer** | Altitude | 20-100 Hz |
| **Compass** | Heading | 10-75 Hz |
| **Airspeed** | Forward airspeed | 10-50 Hz |
| **Rangefinder** | Height above ground | 10-50 Hz |
| **Optical Flow** | Velocity over ground | 10-30 Hz |

---

## EKF3 Parameters

### Core Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| **EK3_ENABLE** | 1 | Enable EKF3 |
| **EK3_IMU_MASK** | 3 | IMUs to use (bitmask) |
| **EK3_ALT_SOURCE** | 0 | Altitude source (0=baro, 1=rangefinder, 2=GPS, 3=beacon) |
| **EK3_GPS_TYPE** | 0 | GPS mode |

### Sensor Weighting

| Parameter | Default | Description | Effect |
|-----------|---------|-------------|--------|
| **EK3_ACC_P_NSE** | 0.35 | Accelerometer noise (m/s²) | ↑ = trust less |
| **EK3_GYRO_P_NSE** | 0.015 | Gyroscope noise (rad/s) | ↑ = trust less |
| **EK3_GPS_VACC_MAX** | 10.0 | Max GPS vertical accuracy (m) | GPS rejected if worse |
| **EK3_GPS_HACC_MAX** | 10.0 | Max GPS horizontal accuracy (m) | GPS rejected if worse |
| **EK3_BARO_ALT_NOISE** | 0.5 | Barometer altitude noise (m) | ↑ = trust less |
| **EK3_MAG_CAL** | 3 | Compass calibration mode | 0=none, 3=auto, 5=world magnetic model |

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

| Message | Cause | Solution |
|---------|-------|----------|
| **PreArm: EKF attitude variance** | Orientation uncertain | Wait for GPS lock, check compass calibration |
| **PreArm: EKF velocity variance** | Velocity uncertain | Wait longer, ensure GPS fix |
| **PreArm: EKF position variance** | Position uncertain | Wait for GPS lock, check antenna |
| **PreArm: EKF compass variance** | Compass inconsistent | Calibrate compass, check interference |

Arming is blocked if variances exceed thresholds.

---

## Common EKF Issues

### EKF Won't Allow Arming

**Causes:** GPS not locked, compass not calibrated, excessive vibration, vehicle moved before GPS lock

```bash
# Check GPS status
param show GPS_*

# Force arm in SITL
arm throttle force
```

### EKF Resets In Flight

**Symptoms:** Sudden position jumps, mode switches to LAND

**Causes:** GPS glitch/loss, excessive vibration, magnetic interference, sensor failure

**Solutions:** Review logs, check vibration levels, improve GPS antenna placement, calibrate sensors.

### Poor Position Hold

**Causes:** Poor GPS accuracy, incorrect compass calibration, wind estimation errors

```bash
# Stricter GPS accuracy, increased position noise
param set EK3_GPS_HACC_MAX 5.0
param set EK3_POSNE_M_NSE 1.0
```

---

## EKF Logging and Analysis

```bash
# Log everything (for debugging)
param set LOG_BITMASK 65535
```

### Key Log Messages

| Log Message | Contains |
|-------------|----------|
| **EKF1-5** | EKF status, variance, innovations |
| **GPS** | Fix, satellites, accuracy |
| **IMU** | Accelerometer, gyroscope data |
| **MAG** | Compass readings |
| **BARO** | Barometer altitude |

```bash
# View logs with MAVExplorer
mavexplorer.py logfile.bin
```

---

## EKF Tuning (Advanced)

**Generally: Don't tune EKF unless you have a specific problem.** Defaults work for most vehicles.

Tune only if: persistent pre-arm failures, poor position hold despite good GPS, EKF variances consistently high, or known sensor noise characteristics differ from defaults.

**Process:**

1. Identify the problem sensor from logs
2. Adjust the noise parameter for that sensor
3. Test and validate

```bash
# Vibration causing accelerometer issues — trust it less
param set EK3_ACC_P_NSE 0.5  # Default 0.35
```

---

## EKF vs AHRS

**AHRS:** Simpler, estimates attitude only (roll, pitch, yaw).

**EKF:** Full state estimator — position, velocity, attitude, biases, wind.

In ArduPilot, `AP_AHRS` is the interface to EKF output.

---

## EKF Math (Optional)

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

Where: `x̂`=state estimate, `P`=covariance, `F`=state transition, `H`=observation, `K`=Kalman gain, `Q`=process noise, `R`=measurement noise, `z`=measurement.

---

## Resources

- [EKF3 Overview](https://ardupilot.org/plane/docs/ekf3.html)
- [EKF Failsafe](https://ardupilot.org/plane/docs/ekf-failsafe.html)
- [Compass Calibration](https://ardupilot.org/plane/docs/common-compass-calibration-in-mission-planner.html)
- `libraries/AP_NavEKF3/` - EKF3 implementation
- `libraries/AP_AHRS/` - AHRS interface to EKF

---

**Last Updated:** 2026-02-03
**Target Version:** Plane 4.5.7
