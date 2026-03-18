# ArduPilot Parameter Configuration Guide

Parameters control every aspect of ArduPilot behavior. **Target Version:** Plane 4.5.7

> **Important:** Parameter availability and defaults vary by vehicle type and firmware version.

---

## Parameter Basics

```bash
param show TECS_*           # Show parameters matching pattern
param show TECS_CLMB_MAX    # Show specific parameter
param set TECS_CLMB_MAX 15.0
param save ~/my_params.parm
param load ~/my_params.parm
param save ~/backup_$(date +%Y%m%d).parm  # Backup before changes
```

---

## 1. TECS (Total Energy Control System)

TECS manages altitude and airspeed via pitch and throttle.

| Parameter | Default | Description | Tuning Notes |
|-----------|---------|-------------|--------------|
| TECS_TIME_CONST | 5.0 | Response time constant (sec) | ↑ = slower, smoother. Try 7-10 if oscillating |
| TECS_CLMB_MAX | 5.0 | Max climb rate (m/s) | Set to 80-90% of measured max |
| TECS_SINK_MAX | 5.0 | Max descent rate (m/s) | Safe descent without exceeding max airspeed |
| TECS_THR_DAMP | 0.5 | Throttle damping | ↑ if speed oscillates |
| TECS_SPDWEIGHT | 1.0 | Speed vs altitude priority | 0=altitude, 2=speed, 1=balanced |
| TECS_PTCH_DAMP | 0.0 | Pitch damping | ↑ if altitude oscillates |

```bash
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane -L CMAC --console --map

param show TECS_*
param set TECS_CLMB_MAX 10.0
param set TECS_TIME_CONST 7.0

mode FBWA
arm throttle
rc 3 1800
```

---

## 2. Airspeed Parameters

| Parameter | Default | Description | Notes |
|-----------|---------|-------------|-------|
| ARSPD_TYPE | 0 | Airspeed sensor type | 0=none, 1=analog, 2=MS4525, 8=SITL |
| ARSPD_USE | 1 | Use airspeed sensor | 1=use, 0=disable |
| ARSPD_FBW_MIN | 12 | Min airspeed in auto modes (m/s) | Set above stall speed |
| ARSPD_FBW_MAX | 22 | Max airspeed in auto modes (m/s) | Set below max safe speed |
| TRIM_ARSPD_CM | 1500 | Target cruise airspeed (cm/s) | 1500 = 15 m/s |
| ARSPD_RATIO | 2.0 | Calibration ratio | Adjust if airspeed reads incorrectly |

```bash
param set ARSPD_FBW_MIN 12
param set ARSPD_FBW_MAX 25
param set TRIM_ARSPD_CM 1700  # 17 m/s cruise
```

---

## 3. Throttle Parameters

| Parameter | Default | Description | Notes |
|-----------|---------|-------------|-------|
| THR_MIN | 0 | Minimum throttle (%) | Idle throttle |
| THR_MAX | 75 | Maximum throttle (%) | Limit for safety/efficiency |
| TRIM_THROTTLE | 45 | Cruise throttle (%) | Throttle for level flight at cruise speed |
| THR_SLEWRATE | 100 | Max throttle change rate (%/sec) | Lower = smoother |
| THR_FAILSAFE | 1 | Enable throttle failsafe | 1=enabled |
| THR_FS_VALUE | 950 | Failsafe PWM threshold | Below this triggers failsafe |

```bash
param set THR_MAX 80
param set THR_MIN 5
param set TRIM_THROTTLE 50
```

---

## 4. Control Surface Limits

| Parameter | Default | Description | Notes |
|-----------|---------|-------------|-------|
| LIM_ROLL_CD | 6000 | Max roll angle (centidegrees) | 6000 = 60° |
| LIM_PITCH_MAX | 2000 | Max pitch up (centidegrees) | 2000 = 20° |
| LIM_PITCH_MIN | -2500 | Max pitch down (centidegrees) | -2500 = -25° |

**Centidegrees:** 100 centidegrees = 1 degree

```bash
param set LIM_ROLL_CD 4500   # 45° max roll
param set LIM_PITCH_MAX 2000
param set LIM_PITCH_MIN -2000
```

---

## 5. Navigation Parameters

| Parameter | Default | Description | Notes |
|-----------|---------|-------------|-------|
| NAVL1_PERIOD | 18 | L1 controller period (sec) | ↓ = tighter turns, ↑ = gentler |
| WP_RADIUS | 90 | Waypoint acceptance radius (m) | Distance to consider WP "reached" |
| WP_LOITER_RAD | 60 | Default loiter radius (m) | Circle radius for LOITER mode |
| WP_MAX_RADIUS | 0 | Max waypoint radius (m) | 0 = no limit |

```bash
param set NAVL1_PERIOD 15
param set WP_RADIUS 50
wp load mission_square.txt
mode AUTO
arm throttle
```

---

## 6. Failsafe Parameters

### RC Failsafe

| Parameter | Default | Description | Notes |
|-----------|---------|-------------|-------|
| THR_FAILSAFE | 1 | Enable RC failsafe | 1=enabled |
| THR_FS_VALUE | 950 | RC failsafe threshold (PWM) | Below triggers failsafe |
| FS_SHORT_ACTN | 0 | Short failsafe action | 0=none, 1=RTL, 2=FBWA |
| FS_SHORT_TIMEOUT | 1.5 | Short failsafe time (sec) | |
| FS_LONG_ACTN | 0 | Long failsafe action | 0=none, 1=RTL, 2=Land |
| FS_LONG_TIMEOUT | 5.0 | Long failsafe time (sec) | |

### Battery Failsafe

| Parameter | Default | Description | Notes |
|-----------|---------|-------------|-------|
| BATT_MONITOR | 0 | Battery monitor type | 4=analog voltage+current |
| BATT_CAPACITY | 0 | Battery capacity (mAh) | |
| BATT_LOW_VOLT | 0 | Low battery voltage | Triggers low battery action |
| BATT_CRT_VOLT | 0 | Critical battery voltage | |
| BATT_FS_LOW_ACT | 0 | Low battery action | 0=none, 1=RTL, 2=Land |
| BATT_FS_CRT_ACT | 0 | Critical battery action | 0=none, 1=RTL, 2=Land |

### Geofence

| Parameter | Default | Description | Notes |
|-----------|---------|-------------|-------|
| FENCE_ENABLE | 0 | Enable geofence | 0=disabled, 1=enabled |
| FENCE_TYPE | 7 | Fence type bitmask | 1=altitude, 2=circle, 4=polygon |
| FENCE_ACTION | 0 | Breach action | 0=report only, 1=RTL, 2=Land |
| FENCE_ALT_MAX | 0 | Max altitude (m) | |
| FENCE_ALT_MIN | 0 | Min altitude (m) | |
| FENCE_RADIUS | 0 | Circular fence radius (m) | |

### Failsafe Configuration Example

```bash
# RC failsafe
param set THR_FAILSAFE 1
param set FS_SHORT_ACTN 1  # RTL after 1.5 sec
param set FS_LONG_ACTN 2   # Land after 5 sec

# Battery failsafe (4S LiPo)
param set BATT_MONITOR 4
param set BATT_CAPACITY 5000
param set BATT_LOW_VOLT 14.0   # 3.5V/cell
param set BATT_CRT_VOLT 13.2   # 3.3V/cell
param set BATT_FS_LOW_ACT 1    # RTL on low
param set BATT_FS_CRT_ACT 2    # Land on critical

# Geofence
param set FENCE_ENABLE 1
param set FENCE_TYPE 3         # Altitude + circle
param set FENCE_ACTION 1       # RTL on breach
param set FENCE_ALT_MAX 150
param set FENCE_ALT_MIN 30
param set FENCE_RADIUS 500
```

---

## 7. Serial Port Configuration

| Parameter | Pattern | Description |
|-----------|---------|-------------|
| SERIALn_PROTOCOL | 0-28+ | 1/2=MAVLink, 5=GPS, 28=Scripting |
| SERIALn_BAUD | 1-2000 | 57=57600, 115=115200, 921=921600 |
| SERIALn_OPTIONS | bitmask | Special options (usually 0) |

```bash
param set SERIAL1_PROTOCOL 2   # MAVLink2 on Telem1
param set SERIAL1_BAUD 57      # 57600 baud
param set SERIAL3_PROTOCOL 5   # GPS on Serial 3
param set SERIAL3_BAUD 115
param set SERIAL2_PROTOCOL 2   # Companion computer
param set SERIAL2_BAUD 921     # 921600 baud
```

---

## 8. PID Tuning Parameters

| Parameter Group | Description |
|----------------|-------------|
| RLL2SRV_* | Roll controller (ailerons) |
| PTCH2SRV_* | Pitch controller (elevator) |
| YAW2SRV_* | Yaw controller (rudder) |
| STEER2SRV_* | Steering (ground/differential thrust) |

**Note:** Use Auto Tune when possible.

---

## 9. Lua Scripting Parameters

| Parameter | Default | Description | Notes |
|-----------|---------|-------------|-------|
| SCR_ENABLE | 0 | Enable Lua scripting | 1=enabled (requires reboot) |
| SCR_HEAP_SIZE | 43008 | Script heap memory (bytes) | Increase if scripts fail to load |
| SCR_USER1-6 | 0 | User parameters for scripts | Custom values scripts can read |

```bash
param set SCR_ENABLE 1
# Restart SITL to create scripts/ directory
param set SCR_HEAP_SIZE 100000
```

---

## Parameter Tuning Workflows

### TECS Tuning

```bash
param fetch
mode FBWA
arm throttle
rc 3 1700

param set TECS_TIME_CONST 7.0  # If oscillating: increase
param set TECS_TIME_CONST 4.0  # If too slow: decrease
param set TECS_THR_DAMP 0.7    # If speed varies: increase
```

### Navigation Tuning

```bash
wp load mission_square.txt
mode AUTO
arm throttle

param set NAVL1_PERIOD 20  # Overshooting: increase
param set NAVL1_PERIOD 15  # Turns too wide: decrease
param set WP_RADIUS 50     # Must get closer
param set WP_RADIUS 100    # Accept farther away
```

### Failsafe Testing

```bash
param set FS_SHORT_ACTN 1
param set FS_LONG_ACTN 2
mode FBWA
arm throttle
rc 3 1700
mode RTL  # Simulate RC loss
```

---

## Parameter Safety Tips

1. **Backup first:** `param save ~/backup_$(date +%Y%m%d_%H%M%S).parm`
2. **Check units:** degrees vs centidegrees, m/s vs cm/s
3. **Change one at a time** and test after each change
4. **Parameters requiring reboot:** `SERIALn_PROTOCOL`, `SCR_ENABLE`, CAN bus parameters

**Avoid without deep understanding:**

- EKF parameters
- Setting safety parameters to 0
- Extreme limit values
- Disabling arming checks

---

## Common Parameter Scenarios

```bash
# Aircraft climbs/descends too aggressively
param set TECS_TIME_CONST 7.0
param set TECS_CLMB_MAX 8.0
param set TECS_SINK_MAX 5.0

# Aircraft overshoots waypoints
param set NAVL1_PERIOD 20
param set WP_RADIUS 75

# Speed varies too much
param set TECS_SPDWEIGHT 1.5
param set TECS_THR_DAMP 0.7

# Enable scripting
param set SCR_ENABLE 1
```

---

## Additional Resources

- [ArduPilot Parameter Docs](https://ardupilot.org/plane/docs/parameters.html) — use version selector for Plane 4.5.7
- [TECS Tuning Guide](https://ardupilot.org/plane/docs/tecs-total-energy-control-system-for-speed-height-tuning-guide.html)
- [Failsafe Documentation](https://ardupilot.org/plane/docs/apms-failsafe-function.html)
- [Main Onboarding Guide](../Onboarding_Documentation/ArduPilot_Onboarding_Guide.md)

---

**Last Updated:** 2026-02-03
**Target Version:** Plane 4.5.7
