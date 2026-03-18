# PID Tuning

PID controllers maintain desired vehicle attitude. Proper tuning is critical for stable, responsive flight.

## Key Parameters

| Parameter        | Function                   | Typical Range |
| ---------------- | -------------------------- | ------------- |
| ATC_RAT_RLL_P    | Roll rate proportional     | 0.05 - 0.30   |
| ATC_RAT_RLL_I    | Roll rate integral         | 0.05 - 0.30   |
| ATC_RAT_RLL_D    | Roll rate derivative       | 0.001 - 0.015 |
| ATC_RAT_PIT_P    | Pitch rate proportional    | 0.05 - 0.30   |
| ATC_RAT_YAW_P    | Yaw rate proportional      | 0.10 - 0.50   |

## Exercises

### Exercise 1: Baseline Configuration Check

```bash
cd ~/ardupilot/ArduCopter
sim_vehicle.py --console --map

param show ATC_RAT_RLL_P
param show ATC_RAT_RLL_I
param show ATC_RAT_RLL_D
param show ATC_RAT_PIT_P
param show ATC_RAT_PIT_I
param show ATC_RAT_PIT_D
param show INS_GYRO_FILTER
param show ATC_RAT_RLL_FLTD
param show ATC_RAT_RLL_FLTT

param save baseline_params.txt
```

### Exercise 2: Auto-Tune Procedure

```bash
param set AUTOTUNE_AXES 7        # All axes: roll, pitch, yaw
param set AUTOTUNE_AGGR 0.05
param set AUTOTUNE_MIN_D 0.001
param write
reboot

mode LOITER
arm throttle
# Climb to 50m+ AGL

mode AUTOTUNE
# Keep in AUTOTUNE for 5-15 minutes

mode LAND
# Auto-tune params saved automatically
```

**Abort if:** violent oscillations, loss of control, or excessive drift — switch to STABILIZE immediately.

### Exercise 3: Manual PID Tuning - Roll Axis

```bash
param set ATC_RAT_RLL_P 0.10
param set ATC_RAT_RLL_I 0.10
param set ATC_RAT_RLL_D 0.003
param set ATC_RAT_RLL_FLTD 20
param write
reboot

mode STABILIZE
arm throttle
# Hover at 2-3m AGL, make sharp roll inputs
```

Increase P by 50% increments until slight oscillation, then reduce by 25%. Tune D to dampen oscillations (typically D = 10-15% of P). Set I = P as starting point.

### Exercise 4: Analyze Tuning from Logs

```python
# analyze_pid_performance.py
from pymavlink import mavutil
import matplotlib.pyplot as plt

def analyze_pid_response(logfile):
    """Analyze PID performance from flight log"""
    mlog = mavutil.mavlink_connection(logfile)

    time = []
    desired_roll = []
    actual_roll = []

    while True:
        msg = mlog.recv_match(type='ATT', blocking=False)
        if msg is None:
            break

        time.append(msg.TimeUS / 1e6)
        desired_roll.append(msg.DesRoll)
        actual_roll.append(msg.Roll)

    plt.figure(figsize=(12, 6))
    plt.plot(time, desired_roll, label='Desired Roll', linewidth=2)
    plt.plot(time, actual_roll, label='Actual Roll', linewidth=1)
    plt.xlabel('Time (s)')
    plt.ylabel('Roll (degrees)')
    plt.title('PID Response Analysis')
    plt.legend()
    plt.grid(True)
    plt.savefig('pid_analysis.png')
    plt.show()

    import numpy as np
    desired = np.array(desired_roll)
    actual = np.array(actual_roll)
    error = actual - desired

    print(f"PID Performance Metrics:")
    print(f"  Mean Error: {np.mean(np.abs(error)):.2f}°")
    print(f"  Max Error: {np.max(np.abs(error)):.2f}°")
    print(f"  RMS Error: {np.sqrt(np.mean(error**2)):.2f}°")

analyze_pid_response("test_flight.BIN")
```

Good indicators: desired and actual closely track, overshoot < 5°, response time < 0.1s, no oscillation.

### Exercise 5: Diagnose Common Tuning Issues

```bash
# Oscillation (P too high or D too low)
param set ATC_RAT_RLL_P 0.12  # Reduce by 20%
# OR
param set ATC_RAT_RLL_D 0.006  # Increase D

# Sluggish response
param set ATC_RAT_RLL_P 0.18  # Increase by 20%

# Overshoot
param set ATC_RAT_RLL_P 0.12
param set ATC_RAT_RLL_I 0.10

param write
```

### Exercise 6: Create Parameter Sets

```bash
param set ATC_RAT_RLL_P 0.10
param set ATC_RAT_RLL_I 0.10
param set ATC_RAT_RLL_D 0.003
param set ATC_RAT_PIT_P 0.10
param set ATC_RAT_PIT_I 0.10
param set ATC_RAT_PIT_D 0.003
param save conservative_tune.param

param set ATC_RAT_RLL_P 0.25
param set ATC_RAT_RLL_I 0.25
param set ATC_RAT_RLL_D 0.008
param set ATC_RAT_PIT_P 0.25
param set ATC_RAT_PIT_I 0.25
param set ATC_RAT_PIT_D 0.008
param save aggressive_tune.param

param set ATC_RAT_RLL_P 0.15
param set ATC_RAT_RLL_I 0.15
param set ATC_RAT_RLL_D 0.005
param set ATC_SLEW_YAW 1000
param save cinematic_tune.param

param load conservative_tune.param
```

### Exercise 7: Advanced Tuning - Notch Filters

```bash
param set INS_HNTCH_ENABLE 1
param set INS_HNTCH_FREQ 80
param set INS_HNTCH_BW 40
param set INS_HNTCH_REF 0.15
param set INS_HNTCH_MODE 1       # Throttle-based
# Or dynamic notch (tracks motor RPM)
param set INS_HNTCH_MODE 3       # ESC telemetry based
param set INS_HNTCH_OPTS 2
param write
reboot
```

## Common Issues

### Persistent Oscillation

```bash
param set ATC_RAT_RLL_P 0.08
param set ATC_RAT_RLL_I 0.08
param set ATC_RAT_RLL_D 0.002
param set INS_GYRO_FILTER 40
param set ATC_RAT_RLL_FLTD 15
```

Check for loose props, bent motor shafts, and vibration before adjusting gains.

### Different Tuning on Each Axis

```bash
param set ATC_RAT_PIT_P 0.12
param set ATC_RAT_PIT_D 0.004
```

Check for CG offset, asymmetric frame, or different motor spacing.

### Tuning Changes with Battery Level

```bash
param set MOT_THST_EXPO 0.65
param set MOT_BAT_VOLT_MIN 14.4  # 4S min
param set MOT_BAT_VOLT_MAX 16.8  # 4S max
param set BATT_ARM_VOLT 15.0
```

### Auto-Tune Fails or Produces Bad Results

```bash
param set AUTOTUNE_AGGR 0.03
```

Requires: calm wind (< 5 m/s), good GPS lock, 50m+ altitude, fully charged battery.

### Tuning Good in SITL, Bad on Real Hardware

Real hardware has vibration, frame flex, ESC/motor delays, and prop imbalance. Start 30-50% more conservative than SITL; fix mechanical issues first.

---

- [PID Tuning Guide](PID_TUNING_GUIDE.md)
- [ArduPilot PID Tuning](https://ardupilot.org/copter/docs/tuning.html)
- [AutoTune](https://ardupilot.org/copter/docs/autotune.html)
- [IMU Notch Filtering](https://ardupilot.org/copter/docs/common-imu-notch-filtering.html)
