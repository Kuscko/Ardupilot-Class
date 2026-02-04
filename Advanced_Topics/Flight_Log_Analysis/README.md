# Flight Log Analysis

## Overview

Master the art of analyzing ArduPilot flight logs to diagnose issues, tune performance, validate flight behavior, and investigate incidents. Flight logs contain detailed telemetry from sensors, controllers, and vehicle state, providing invaluable insights for troubleshooting and optimization [1].

This module covers log configuration, retrieval, and analysis using multiple tools including Mission Planner, MAVExplorer, and Python scripts.

## Prerequisites

Before starting this module, you should have:

- Completed SITL setup and basic flight testing
- Understanding of ArduPilot parameters
- Familiarity with basic flight dynamics
- Downloaded sample flight logs or generated logs from SITL
- Mission Planner or QGroundControl installed (for log review)

## What You'll Learn

By completing this module, you will:

- Configure logging parameters for comprehensive data capture
- Download logs from flight controller or SITL
- Use Mission Planner for log visualization and analysis
- Analyze logs with MAVExplorer for advanced investigation
- Identify common issues: vibration, EKF problems, PID tuning needs
- Create Python scripts for automated log analysis
- Understand key log messages and their meanings

## Key Concepts

### DataFlash Logging

ArduPilot logs data to onboard flash memory (or SD card) [1]:

- **High-rate logging:** IMU, attitude, control outputs (100-400Hz)
- **Medium-rate logging:** GPS, battery, EKF (5-10Hz)
- **Low-rate logging:** Parameters, events, messages (1Hz)

### Log Message Types

Key log message types [2]:

- **IMU** - Accelerometer and gyroscope data
- **GPS** - Position, velocity, satellite count
- **ATT** - Attitude (roll, pitch, yaw)
- **CTUN** - Control/tuning data
- **EKF** - Extended Kalman Filter status
- **BAT** - Battery voltage and current
- **VIBE** - Vibration levels

## Hands-On Practice

### Exercise 1: Enable Logging in SITL

Configure comprehensive logging:

```bash
# Start SITL
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console

# In MAVProxy, configure logging
param set LOG_BACKEND_TYPE 1     # DataFlash logging
param set LOG_DISARMED 1         # Log when disarmed
param set LOG_REPLAY 1           # Enable replay
param set LOG_FILE_DSRMROT 0     # Don't rotate logs when disarmed
param write
reboot
```

**Run a test flight:**
```
# Arm and takeoff
mode FBWA
arm throttle
# Fly around
# Land
disarm
```

### Exercise 2: Download and View Logs

Retrieve logs from SITL:

```bash
# Logs stored in SITL logs directory
cd ~/ardupilot/ArduPlane/logs

# List logs
ls -lh

# Latest log
ls -lt | head -n 2

# Copy to analysis directory
cp $(ls -t *.BIN | head -1) ~/flight_logs/test_flight.BIN
```

**View in Mission Planner:**
1. Open Mission Planner
2. Flight Data → DataFlash Logs
3. "Review a Log" button
4. Load .BIN file
5. Explore graphs and data

### Exercise 3: Analyze Vibration

Check for vibration issues:

**In Mission Planner Log Viewer:**
1. Load log file
2. Graph: IMU.AccX, IMU.AccY, IMU.AccZ
3. Check vibration levels (should be < 30 m/s²)
4. Graph: VIBE.VibeX, VIBE.VibeY, VIBE.VibeZ
5. Ideal values: < 15

**High vibration symptoms:**
- EKF errors
- Poor altitude hold
- Toilet-bowling in loiter
- Twitchy control responses

**Solutions:**
- Balance propellers
- Check motor mounts
- Add vibration dampening
- Secure loose components

### Exercise 4: Analyze EKF Health

Check Extended Kalman Filter performance:

**Key metrics:**
1. **EKF.IVN** - Innovation (difference between predicted and measured)
2. **EKF.IV** - Innovation variance
3. **EKF.Flags** - EKF status flags

**In Mission Planner:**
```
Graph: EKF1.IVN (Innovation North), EKF1.IVE (Innovation East)
- Should be small (< 2.0)
- Large spikes indicate GPS issues or sensor problems

Graph: EKF1.PN, EKF1.PE (Position uncertainty)
- Should be < 5 meters
- Growing uncertainty indicates degraded accuracy
```

**Common EKF issues:**
- GPS glitches (large IVN/IVE spikes)
- Compass interference (yaw innovation problems)
- Barometer issues (altitude jumps)

### Exercise 5: MAVExplorer Advanced Analysis

Use MAVExplorer for detailed analysis:

```bash
# Install MAVExplorer
pip3 install MAVProxy

# Open log with MAVExplorer
mavexplorer.py ~/flight_logs/test_flight.BIN

# MAVExplorer commands:
# graph ATT.Roll ATT.Pitch                    # Plot attitude
# graph GPS.Alt BARO.Alt                      # Compare altitudes
# graph CTUN.NavRoll CTUN.Roll               # Desired vs actual roll
# graph IMU.GyrX IMU.GyrY IMU.GyrZ          # Gyro rates
```

**Useful graphs:**
```python
# Altitude tracking
graph CTUN.Alt CTUN.TAlt

# Speed tracking
graph GPS.Spd CTUN.TSpd

# Battery monitoring
graph BAT.Volt BAT.Curr

# Control outputs
graph RCOU.C1 RCOU.C2 RCOU.C3 RCOU.C4
```

### Exercise 6: Python Log Analysis Script

Create automated analysis script:

```python
# analyze_log.py
from pymavlink import mavutil

def analyze_log(filename):
    print(f"Analyzing: {filename}")
    mlog = mavutil.mavlink_connection(filename)

    # Statistics
    max_altitude = 0
    max_speed = 0
    total_current = 0
    count = 0

    while True:
        msg = mlog.recv_match(blocking=False)
        if msg is None:
            break

        msg_type = msg.get_type()

        if msg_type == "GPS":
            if msg.Spd > max_speed:
                max_speed = msg.Spd

        elif msg_type == "CTUN":
            if msg.Alt > max_altitude:
                max_altitude = msg.Alt

        elif msg_type == "BAT":
            total_current += msg.Curr
            count += 1

    avg_current = total_current / count if count > 0 else 0

    print(f"Max Altitude: {max_altitude:.1f}m")
    print(f"Max Speed: {max_speed:.1f}m/s")
    print(f"Avg Current: {avg_current:.1f}A")

# Usage
analyze_log("test_flight.BIN")
```

### Exercise 7: PID Tuning Analysis

Analyze PID performance from logs:

**In Mission Planner:**
```
Graph: PIDR.P, PIDR.D (Roll PID terms)
Graph: ATT.DesRoll, ATT.Roll (Desired vs actual)

Look for:
- Oscillation: P too high
- Sluggish response: P too low
- High-frequency noise: D too high
- Overshoot: I too high
```

**Optimal response:**
- Quick convergence to desired value
- Minimal overshoot
- No sustained oscillation

## Common Analysis Tasks

### Diagnose Crash or Incident

**1. Check last messages:**
```python
# Find MODE changes before crash
graph MODE.Mode

# Check for errors
messages | grep ERR

# Final altitude and attitude
graph ATT.Roll ATT.Pitch ATT.Yaw | tail
```

**2. Look for:**
- Mode changes (did it switch to failsafe?)
- Battery voltage drop (brownout?)
- EKF errors (navigation failure?)
- Control saturation (loss of control authority?)

### Validate Flight Performance

```
# Waypoint following accuracy
graph NTUN.WpDist (distance to waypoint)

# Altitude hold performance
graph CTUN.Alt CTUN.TAlt (actual vs target)

# Airspeed control (planes)
graph ARSP.Airspeed TECS.sp (actual vs setpoint)
```

### Analyze Battery Performance

```
graph BAT.Volt BAT.Curr BAT.CurrTot

# Calculate flight time vs capacity
# Check voltage sag under load
# Verify current sensor calibration
```

## Log Configuration Parameters

Key logging parameters [1]:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| LOG_BACKEND_TYPE | 1 | Enable DataFlash logging |
| LOG_BITMASK | 176126 | Default: log most messages |
| LOG_DISARMED | 0/1 | Log when disarmed |
| LOG_REPLAY | 1 | Enable log replay |
| LOG_FILE_DSRMROT | 1 | Rotate logs when disarmed |

**For detailed logging:**
```
LOG_BITMASK 2293759  # Log everything (uses more flash)
```

## Additional Resources

- [ArduPilot Log Analysis](https://ardupilot.org/copter/docs/common-logs.html) [1] - Official log guide
- [Log Messages](https://ardupilot.org/copter/docs/logmessages.html) [2] - Message reference
- [Mission Planner Logs](https://ardupilot.org/planner/docs/common-mission-planner-telemetry-logs.html) [3] - Mission Planner guide
- [MAVExplorer](https://ardupilot.org/dev/docs/using-mavexplorer-for-log-analysis.html) [4] - MAVExplorer docs

### Analysis Tools

- [UAV Log Viewer](https://plot.ardupilot.org/) - Web-based log viewer
- [DataFlash Log Downloader](https://ardupilot.org/copter/docs/common-downloading-and-analyzing-data-logs-in-mission-planner.html) - Download guide

## Next Steps

After mastering log analysis:

1. **PID Tuning** - Use logs to tune flight controllers
2. **Performance Optimization** - Identify performance bottlenecks
3. **Safety Analysis** - Validate safety systems work correctly
4. **Automated Testing** - Create test scenarios and validate with logs

---

**Sources:**

[1] https://ardupilot.org/copter/docs/common-logs.html
[2] https://ardupilot.org/copter/docs/logmessages.html
[3] https://ardupilot.org/planner/docs/common-mission-planner-telemetry-logs.html
[4] https://ardupilot.org/dev/docs/using-mavexplorer-for-log-analysis.html
