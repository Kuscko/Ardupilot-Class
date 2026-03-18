# Flight Log Analysis

ArduPilot flight logs contain detailed telemetry from sensors, controllers, and vehicle state. This module covers log configuration, retrieval, and analysis.

## Key Concepts

### DataFlash Logging

- **High-rate:** IMU, attitude, control outputs (100–400Hz)
- **Medium-rate:** GPS, battery, EKF (5–10Hz)
- **Low-rate:** Parameters, events, messages (1Hz)

### Key Log Message Types

- **IMU** - Accelerometer and gyroscope data
- **GPS** - Position, velocity, satellite count
- **ATT** - Attitude (roll, pitch, yaw)
- **CTUN** - Control/tuning data
- **EKF** - Extended Kalman Filter status
- **BAT** - Battery voltage and current
- **VIBE** - Vibration levels

## Log Configuration Parameters

| Parameter          | Value  | Purpose                        |
| ------------------ | ------ | ------------------------------ |
| LOG_BACKEND_TYPE   | 1      | Enable DataFlash logging       |
| LOG_BITMASK        | 176126 | Default: log most messages     |
| LOG_DISARMED       | 0/1    | Log when disarmed              |
| LOG_REPLAY         | 1      | Enable log replay              |
| LOG_FILE_DSRMROT   | 1      | Rotate logs when disarmed      |

For detailed logging: `LOG_BITMASK 2293759`

## Exercises

### Exercise 1: Enable Logging in SITL

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console

param set LOG_BACKEND_TYPE 1
param set LOG_DISARMED 1
param set LOG_FILE_DSRMROT 0
param write
reboot
```

Fly a test flight, then check `~/ardupilot/ArduPlane/logs/`.

### Exercise 2: Download and View Logs

```bash
cd ~/ardupilot/ArduPlane/logs
ls -lh
cp $(ls -t *.BIN | head -1) ~/flight_logs/test_flight.BIN
```

In Mission Planner: Flight Data → DataFlash Logs → Review a Log → load .BIN file.

### Exercise 3: Analyze Vibration

In Mission Planner Log Viewer, graph:

- `IMU.AccX/Y/Z` — should be < 30 m/s²
- `VIBE.VibeX/Y/Z` — ideal < 15

High vibration fixes: balance propellers, check motor mounts, add vibration dampening.

### Exercise 4: Analyze EKF Health

```text
Graph: EKF1.IVN, EKF1.IVE  — should be < 2.0
Graph: EKF1.PN, EKF1.PE    — should be < 5 meters
```

Large spikes indicate GPS issues or sensor problems.

### Exercise 5: MAVExplorer Advanced Analysis

```bash
pip3 install MAVProxy
mavexplorer.py ~/flight_logs/test_flight.BIN
```

```text
graph ATT.Roll ATT.Pitch
graph GPS.Alt BARO.Alt
graph CTUN.NavRoll CTUN.Roll
graph IMU.GyrX IMU.GyrY IMU.GyrZ
```

### Exercise 6: Python Log Analysis

```python
# analyze_log.py
from pymavlink import mavutil

def analyze_log(filename):
    mlog = mavutil.mavlink_connection(filename)
    max_altitude = 0
    max_speed = 0

    while True:
        msg = mlog.recv_match(blocking=False)
        if msg is None:
            break
        if msg.get_type() == "GPS" and msg.Spd > max_speed:
            max_speed = msg.Spd
        elif msg.get_type() == "CTUN" and msg.Alt > max_altitude:
            max_altitude = msg.Alt

    print(f"Max Altitude: {max_altitude:.1f}m")
    print(f"Max Speed: {max_speed:.1f}m/s")

analyze_log("test_flight.BIN")
```

### Exercise 7: PID Tuning Analysis

In Mission Planner, graph:

- `PIDR.P`, `PIDR.D` — roll PID terms
- `ATT.DesRoll`, `ATT.Roll` — desired vs actual

Oscillation = P too high | Sluggish = P too low | High-freq noise = D too high

## Common Analysis Tasks

### Diagnose Crash or Incident

```text
graph MODE.Mode
messages | grep ERR
graph ATT.Roll ATT.Pitch ATT.Yaw
```

Look for: mode changes (failsafe?), battery voltage drop (brownout?), EKF errors, control saturation.

### Validate Flight Performance

```text
graph NTUN.WpDist       # Waypoint following accuracy
graph CTUN.Alt CTUN.TAlt  # Altitude hold
graph ARSP.Airspeed TECS.sp  # Airspeed control
```

---

- [LOGGING_SETUP_GUIDE.md](LOGGING_SETUP_GUIDE.md)
- [LOG_RETRIEVAL_GUIDE.md](LOG_RETRIEVAL_GUIDE.md)
- [LOG_ANALYSIS_GUIDE.md](LOG_ANALYSIS_GUIDE.md)
- [TECS_ANALYSIS_TUTORIAL.md](TECS_ANALYSIS_TUTORIAL.md)
- [VIBRATION_ANALYSIS_TUTORIAL.md](VIBRATION_ANALYSIS_TUTORIAL.md)
- [ArduPilot Log Analysis](https://ardupilot.org/copter/docs/common-logs.html)
