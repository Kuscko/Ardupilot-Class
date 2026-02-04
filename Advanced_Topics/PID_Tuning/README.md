# PID Tuning

## Overview

Master PID (Proportional-Integral-Derivative) controller tuning to achieve optimal flight performance in ArduPilot. PID tuning is essential for responsive, stable flight control across different vehicle types, sizes, and configurations [1].

This module covers PID fundamentals, auto-tune procedures, manual tuning techniques, and log analysis for diagnosing and resolving control issues.

## Prerequisites

Before starting this module, you should have:

- Completed SITL setup and basic flight operations
- Understanding of flight dynamics and control surfaces
- Familiarity with flight log analysis
- Mission Planner or QGroundControl installed
- Safe test environment (SITL or controlled flight area)

## What You'll Learn

By completing this module, you will:

- Understand PID controller principles and tuning parameters
- Execute auto-tune procedures safely and effectively
- Manually tune PIDs for specific performance goals
- Analyze logs to identify tuning issues
- Diagnose oscillations, overshoot, and sluggish response
- Create parameter sets for different flight profiles
- Optimize performance for racing, photography, or endurance

## Key Concepts

### PID Controller Basics

PID controllers maintain desired vehicle attitude [1]:

**Proportional (P):**
- Generates output proportional to error
- Higher P = more aggressive response
- Too high = oscillation
- Too low = sluggish response

**Integral (I):**
- Corrects steady-state error over time
- Eliminates long-term drift
- Too high = overshoot, slow settling
- Too low = steady error remains

**Derivative (D):**
- Dampens rapid changes
- Reduces overshoot
- Too high = noise amplification
- Too low = bouncy, oscillating response

### ArduPilot Control Loops

Multi-layer control architecture [2]:

**Rate Controller (Inner Loop):**
- Controls angular rates (roll/pitch/yaw rate)
- Fastest loop, runs at 400Hz
- Parameters: ATC_RAT_*

**Attitude Controller (Outer Loop):**
- Controls angles (roll/pitch/yaw angle)
- Runs at 100Hz
- Parameters: ATC_ANG_*

**Navigation Controller:**
- Controls position and velocity
- Runs at 50Hz
- Uses L1 controller for planes

### Key Parameters

Critical tuning parameters [3]:

| Parameter | Function | Typical Range |
| --------- | -------- | ------------- |
| ATC_RAT_RLL_P | Roll rate proportional | 0.05 - 0.30 |
| ATC_RAT_RLL_I | Roll rate integral | 0.05 - 0.30 |
| ATC_RAT_RLL_D | Roll rate derivative | 0.001 - 0.015 |
| ATC_RAT_PIT_P | Pitch rate proportional | 0.05 - 0.30 |
| ATC_RAT_YAW_P | Yaw rate proportional | 0.10 - 0.50 |

## Hands-On Practice

### Exercise 1: Baseline Configuration Check

Verify starting parameters before tuning:

```bash
# Start SITL
cd ~/ardupilot/ArduCopter
sim_vehicle.py --console --map

# Check current PID values
param show ATC_RAT_RLL_P
param show ATC_RAT_RLL_I
param show ATC_RAT_RLL_D
param show ATC_RAT_PIT_P
param show ATC_RAT_PIT_I
param show ATC_RAT_PIT_D

# Check filter settings
param show INS_GYRO_FILTER
param show ATC_RAT_RLL_FLTD
param show ATC_RAT_RLL_FLTT

# Save current parameters as backup
param save baseline_params.txt
```

**Document baseline values** - You'll compare against these after tuning.

### Exercise 2: Auto-Tune Procedure

Use ArduPilot's auto-tune feature for initial tuning:

```bash
# Enable auto-tune
param set AUTOTUNE_AXES 7        # All axes: roll, pitch, yaw
param set AUTOTUNE_AGGR 0.05     # Aggressiveness (0.05-0.10)
param set AUTOTUNE_MIN_D 0.001   # Minimum D gain

param write
reboot

# Fly to safe altitude
mode LOITER
arm throttle
# Climb to 50m+ AGL

# Activate auto-tune
mode AUTOTUNE

# Auto-tune will:
# 1. Twitch vehicle in each axis
# 2. Measure response
# 3. Calculate optimal PIDs
# 4. Apply and test new values

# Keep vehicle in AUTOTUNE mode for 5-15 minutes
# Stay in safe area, monitor behavior

# When complete, land and save
mode LAND
# After landing, auto-tune params are saved automatically
```

**Expected behavior during auto-tune:**
- Systematic twitches in roll, pitch, yaw
- Progressively faster oscillations
- Vehicle remains stable throughout
- May hear motors speed up/down rhythmically

**Warning signs to abort:**
- Violent oscillations
- Loss of control
- Excessive drift
- Switch to STABILIZE immediately if unsafe

### Exercise 3: Manual PID Tuning - Roll Axis

Step-by-step manual tuning process:

```bash
# Start with known-good defaults or auto-tune results
# Tune roll rate controller first

# Step 1: Set conservative starting values
param set ATC_RAT_RLL_P 0.10
param set ATC_RAT_RLL_I 0.10
param set ATC_RAT_RLL_D 0.003
param set ATC_RAT_RLL_FLTD 20    # D-term filter (Hz)

param write
reboot

# Step 2: Test in STABILIZE mode
mode STABILIZE
arm throttle
# Hover at 2-3m AGL
# Make sharp roll inputs
# Observe response
```

**Tuning procedure:**

1. **Increase P-gain:**

```bash
# Increase P by 50% increments
param set ATC_RAT_RLL_P 0.15
param write
# Test: Sharp roll input, observe response

# Continue increasing until:
# - Fast, responsive control
# - Slight oscillation appears
# - Then reduce P by 25%

# Example: If oscillation at P=0.20
param set ATC_RAT_RLL_P 0.15  # Reduce by 25%
```

2. **Tune D-gain:**

```bash
# Increase D to dampen oscillations
param set ATC_RAT_RLL_D 0.005
# Test

# Continue increasing until:
# - Oscillations eliminated
# - Response is crisp
# - No motor noise (too much D)

# Typical D is 10-15% of P
```

3. **Set I-gain:**

```bash
# Set I equal to P (starting point)
param set ATC_RAT_RLL_I 0.15

# I-gain eliminates steady-state error
# Usually I ≈ P for multicopters
```

### Exercise 4: Analyze Tuning from Logs

Use logs to verify tuning quality:

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

    # Plot desired vs actual
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

    # Calculate tracking error
    import numpy as np
    desired = np.array(desired_roll)
    actual = np.array(actual_roll)
    error = actual - desired

    print(f"PID Performance Metrics:")
    print(f"  Mean Error: {np.mean(np.abs(error)):.2f}°")
    print(f"  Max Error: {np.max(np.abs(error)):.2f}°")
    print(f"  RMS Error: {np.sqrt(np.mean(error**2)):.2f}°")

# Usage
analyze_pid_response("test_flight.BIN")
```

**Good PID tuning indicators:**
- Desired and actual closely track
- No overshoot (< 5 degrees)
- Fast response (< 0.1s to reach target)
- No oscillation around setpoint

### Exercise 5: Diagnose Common Tuning Issues

Identify problems from flight behavior:

**Oscillation (Too Much P or Not Enough D):**

```bash
# Symptoms in flight:
# - Rapid back-and-forth motion
# - Buzzing or grinding motor sounds
# - Jello in video

# Solutions:
param show ATC_RAT_RLL_P
# Reduce P by 20%
param set ATC_RAT_RLL_P 0.12  # If was 0.15

# OR increase D
param show ATC_RAT_RLL_D
param set ATC_RAT_RLL_D 0.006  # If was 0.004

param write
# Test again
```

**Sluggish Response (Not Enough P):**

```bash
# Symptoms:
# - Slow to respond to inputs
# - Drifts during maneuvers
# - Feels "mushy"

# Solution:
param show ATC_RAT_RLL_P
# Increase P by 20%
param set ATC_RAT_RLL_P 0.18  # If was 0.15

param write
```

**Overshoot (Too Much P or I):**

```bash
# Symptoms:
# - Overshoots desired angle
# - Bounces back and forth
# - Slow to settle

# Solutions:
# Reduce P
param set ATC_RAT_RLL_P 0.12

# OR reduce I
param set ATC_RAT_RLL_I 0.10

param write
```

### Exercise 6: Create Parameter Sets

Save optimized parameters for different scenarios:

```bash
# Conservative (stable, smooth)
param set ATC_RAT_RLL_P 0.10
param set ATC_RAT_RLL_I 0.10
param set ATC_RAT_RLL_D 0.003
param set ATC_RAT_PIT_P 0.10
param set ATC_RAT_PIT_I 0.10
param set ATC_RAT_PIT_D 0.003
param save conservative_tune.param

# Aggressive (racing, acro)
param set ATC_RAT_RLL_P 0.25
param set ATC_RAT_RLL_I 0.25
param set ATC_RAT_RLL_D 0.008
param set ATC_RAT_PIT_P 0.25
param set ATC_RAT_PIT_I 0.25
param set ATC_RAT_PIT_D 0.008
param save aggressive_tune.param

# Cinematic (smooth video)
param set ATC_RAT_RLL_P 0.15
param set ATC_RAT_RLL_I 0.15
param set ATC_RAT_RLL_D 0.005
param set ATC_SLEW_YAW 1000      # Limit yaw rate
param save cinematic_tune.param

# Load saved parameters
param load conservative_tune.param
```

### Exercise 7: Advanced Tuning - Notch Filters

Eliminate specific vibration frequencies:

```bash
# Identify problem frequency from FFT analysis
# (requires log with INS_LOG_BAT_MASK enabled)

# Configure notch filter for 80Hz vibration
param set INS_HNTCH_ENABLE 1     # Enable harmonic notch
param set INS_HNTCH_FREQ 80      # Center frequency
param set INS_HNTCH_BW 40        # Bandwidth
param set INS_HNTCH_REF 0.15     # Reference value
param set INS_HNTCH_MODE 1       # Throttle-based

# Or use dynamic notch (tracks motor RPM)
param set INS_HNTCH_MODE 3       # ESC telemetry based
param set INS_HNTCH_OPTS 2       # Update in-flight

param write
reboot
```

## Common Issues

### Issue 1: Persistent Oscillation

**Symptoms:**
- Won't stop oscillating regardless of tuning
- High-frequency buzz
- Hot motors

**Solutions:**

```bash
# Check for mechanical issues first:
# - Loose props
# - Bent motor shafts
# - Soft-mounted flight controller

# Reduce overall gains
param set ATC_RAT_RLL_P 0.08
param set ATC_RAT_RLL_I 0.08
param set ATC_RAT_RLL_D 0.002

# Enable/tune filters
param set INS_GYRO_FILTER 40     # Lower if needed
param set ATC_RAT_RLL_FLTD 15    # Lower D-term filter

# Check for vibration issues
# Analyze VIBE messages in logs
```

### Issue 2: Different Tuning on Each Axis

**Symptoms:**
- Roll feels good, pitch oscillates
- One axis sluggish, others responsive

**Solutions:**

```bash
# Tune each axis independently
# Roll and pitch may need different values

# Example: Pitch needs less gain
param set ATC_RAT_PIT_P 0.12  # Lower than roll
param set ATC_RAT_PIT_D 0.004

# Check for:
# - CG offset
# - Asymmetric frame
# - Different motor spacing
```

### Issue 3: Tuning Changes with Battery Level

**Symptoms:**
- Good when battery full
- Oscillates when battery low
- Different response throughout flight

**Solutions:**

```bash
# Enable voltage compensation
param set MOT_THST_EXPO 0.65     # Thrust curve expo
param set MOT_BAT_VOLT_MIN 14.4  # Minimum voltage (4S)
param set MOT_BAT_VOLT_MAX 16.8  # Maximum voltage (4S)

# Tune with half-depleted battery
# Compromise between full and empty

# Or use battery voltage scaling
param set BATT_ARM_VOLT 15.0     # Don't arm below this
```

### Issue 4: Auto-Tune Fails or Produces Bad Results

**Symptoms:**
- Auto-tune doesn't complete
- Result worse than starting values
- Vehicle unstable during auto-tune

**Solutions:**

```bash
# Ensure good conditions:
# - Calm wind (< 5 m/s)
# - Good GPS lock
# - Sufficient altitude (50m+)
# - Fully charged battery

# Adjust aggressiveness
param set AUTOTUNE_AGGR 0.03     # Less aggressive

# Start with better baseline
# Manually tune to "acceptable" first
# Then use auto-tune to optimize

# Check vehicle weight/power
# Underpowered = poor auto-tune results
```

### Issue 5: Tuning Good in SITL, Bad on Real Hardware

**Symptoms:**
- SITL flight perfect
- Real hardware oscillates or unstable

**Solutions:**

```bash
# SITL is idealized - real hardware differs
# Always tune on real hardware

# Real-world factors:
# - Vibration
# - Flex in frame
# - ESC/motor response delay
# - Propeller balance

# Start more conservative than SITL
# Reduce gains by 30-50% initially

# Fix mechanical issues first
# Balance props, check motor timing, dampen vibration
```

## Tuning Workflows

### Quick Tune Workflow

```bash
# 1. Auto-tune for baseline
mode AUTOTUNE
# Wait for completion

# 2. Test in normal flight
mode STABILIZE
# Fly patterns, assess feel

# 3. Fine-tune manually
# Adjust P +/- 10% for feel

# 4. Verify with logs
# Check tracking performance

# 5. Save parameters
param save final_tune.param
```

### From-Scratch Manual Tune

```bash
# 1. Set conservative defaults
P = 0.10, I = 0.10, D = 0.003

# 2. Hover test
# Verify stable

# 3. Increase P until oscillation
# Reduce by 25%

# 4. Add D to dampen
# Start with D = P * 0.10

# 5. Set I = P
# Test for drift correction

# 6. Fine tune all three
# Iterative adjustments

# 7. Test flight patterns
# Verify performance

# 8. Analyze logs
# Confirm tracking quality
```

## Additional Resources

- [PID Tuning Guide](https://ardupilot.org/copter/docs/tuning.html) [1] - Official tuning documentation
- [AutoTune](https://ardupilot.org/copter/docs/autotune.html) [2] - Auto-tune procedure details
- [PID Theory](https://ardupilot.org/dev/docs/apmcopter-programming-attitude-control-2.html) [3] - Controller architecture
- [Log Analysis for Tuning](https://ardupilot.org/copter/docs/common-logs.html) - Using logs to tune

### Tuning Tools

- [PID Analyzer](https://github.com/Plasmatree/PID-Analyzer) - Automated log analysis tool
- [Filter Tool](https://ardupilot.org/copter/docs/common-imu-notch-filtering.html) - FFT analysis and filter setup

## Next Steps

After mastering PID tuning:

1. **Advanced Filtering** - Notch filters and vibration isolation
2. **Performance Optimization** - Squeeze maximum performance
3. **Acrobatic Flight** - Tune for advanced maneuvers
4. **Autonomous Missions** - Optimize for waypoint accuracy

---

**Sources:**

[1] https://ardupilot.org/copter/docs/tuning.html
[2] https://ardupilot.org/copter/docs/autotune.html
[3] https://ardupilot.org/dev/docs/apmcopter-programming-attitude-control-2.html
