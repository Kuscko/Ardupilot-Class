# ArduPilot Parameter Configuration Guide

## Introduction

Parameters control every aspect of ArduPilot behavior. With 1000+ parameters available, understanding the most critical ones is essential for successful flight operations.

**Target Version:** Plane 4.5.7

> **Important:** Parameter availability and defaults can vary by vehicle type and firmware version. Always verify against official docs for your specific version.

---

## Parameter Basics

### Viewing Parameters

```bash
# Show all parameters matching pattern
param show TECS_*

# Show specific parameter
param show TECS_CLMB_MAX

# Show all parameters (WARNING: very long list)
param show *
```

### Setting Parameters

```bash
# Set a parameter
param set TECS_CLMB_MAX 15.0

# Some parameters require reboot
# Check parameter docs or reboot if behavior doesn't change
```

### Saving/Loading Parameters

```bash
# Save current parameters to file
param save ~/my_params.parm

# Load parameters from file
param load ~/my_params.parm

# Backup before making major changes!
param save ~/backup_$(date +%Y%m%d).parm
```

---

## Critical Parameter Categories

## 1. TECS (Total Energy Control System)

TECS manages altitude and airspeed by controlling pitch and throttle.

### Core TECS Parameters

| Parameter | Default | Description | Tuning Notes |
|-----------|---------|-------------|--------------|
| TECS_TIME_CONST | 5.0 | Response time constant (sec) | ↑ = slower, smoother response. Try 7-10 if oscillating |
| TECS_CLMB_MAX | 5.0 | Max climb rate (m/s) | Measure at full throttle, set to 80-90% of max |
| TECS_SINK_MAX | 5.0 | Max descent rate (m/s) | Set to safe descent rate without exceeding max airspeed |
| TECS_THR_DAMP | 0.5 | Throttle damping | ↑ if speed oscillates. Requires airspeed sensor |
| TECS_SPDWEIGHT | 1.0 | Speed vs altitude priority | 0=altitude priority, 2=speed priority, 1=balanced |
| TECS_PTCH_DAMP | 0.0 | Pitch damping | ↑ if altitude oscillates |

### TECS Testing in SITL

```bash
# Start SITL
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane -L CMAC --console --map

# Check current TECS settings
param show TECS_*

# Modify and test climb performance
param set TECS_CLMB_MAX 10.0
param set TECS_TIME_CONST 7.0

mode FBWA
arm throttle
rc 3 1800  # High throttle
# Observe climb rate and smoothness in console
```

---

## 2. Airspeed Parameters

Critical for stall prevention and optimal flight performance.

| Parameter | Default | Description | Notes |
|-----------|---------|-------------|-------|
| ARSPD_TYPE | 0 | Airspeed sensor type | 0=none, 1=analog, 2=MS4525, 8=SITL |
| ARSPD_USE | 1 | Use airspeed sensor | 1=use, 0=disable |
| ARSPD_FBW_MIN | 12 | Min airspeed in auto modes (m/s) | Set above stall speed |
| ARSPD_FBW_MAX | 22 | Max airspeed in auto modes (m/s) | Set below max safe speed |
| TRIM_ARSPD_CM | 1500 | Target cruise airspeed (cm/s) | 1500 = 15 m/s |
| ARSPD_RATIO | 2.0 | Calibration ratio | Adjust if airspeed reads incorrectly |

### Airspeed Tuning

```bash
# For SITL, airspeed is simulated
param show ARSPD_*

# Set conservative speeds
param set ARSPD_FBW_MIN 12  # m/s
param set ARSPD_FBW_MAX 25  # m/s
param set TRIM_ARSPD_CM 1700  # 17 m/s cruise
```

---

## 3. Throttle Parameters

Control engine power output.

| Parameter | Default | Description | Notes |
|-----------|---------|-------------|-------|
| THR_MIN | 0 | Minimum throttle (%) | Idle throttle |
| THR_MAX | 75 | Maximum throttle (%) | Limit for safety/efficiency |
| TRIM_THROTTLE | 45 | Cruise throttle (%) | Throttle for level flight at cruise speed |
| THR_SLEWRATE | 100 | Max throttle change rate (%/sec) | Lower = smoother throttle changes |
| THR_FAILSAFE | 1 | Enable throttle failsafe | 1=enabled |
| THR_FS_VALUE | 950 | Failsafe PWM threshold | Below this triggers failsafe |

### Throttle Testing

```bash
# Set throttle limits
param set THR_MAX 80
param set THR_MIN 5
param set TRIM_THROTTLE 50

# Test in flight
mode FBWA
arm throttle
rc 3 1700  # 70% throttle
# Observe actual throttle output in console
```

---

## 4. Control Surface Limits

Set maximum deflection angles for ailerons, elevator, rudder.

| Parameter | Default | Description | Notes |
|-----------|---------|-------------|-------|
| LIM_ROLL_CD | 6000 | Max roll angle (centidegrees) | 6000 = 60 degrees |
| LIM_PITCH_MAX | 2000 | Max pitch up (centidegrees) | 2000 = 20 degrees |
| LIM_PITCH_MIN | -2500 | Max pitch down (centidegrees) | -2500 = -25 degrees |

**Centidegrees:** 100 centidegrees = 1 degree

```bash
# Set conservative limits
param set LIM_ROLL_CD 4500  # 45 degrees max roll
param set LIM_PITCH_MAX 2000  # 20 degrees max pitch up
param set LIM_PITCH_MIN -2000  # 20 degrees max pitch down
```

---

## 5. Navigation Parameters

Control waypoint navigation behavior.

| Parameter | Default | Description | Notes |
|-----------|---------|-------------|-------|
| NAVL1_PERIOD | 18 | L1 controller period (sec) | ↓ = tighter turns, ↑ = gentler turns |
| WP_RADIUS | 90 | Waypoint acceptance radius (m) | Distance to consider waypoint "reached" |
| WP_LOITER_RAD | 60 | Default loiter radius (m) | Circle radius for LOITER mode |
| WP_MAX_RADIUS | 0 | Max waypoint radius (m) | 0 = no limit |

### Navigation Testing

```bash
# Tighter navigation
param set NAVL1_PERIOD 15  # Tighter turns
param set WP_RADIUS 50  # Must get closer to waypoints

# Test with mission
wp load mission_square.txt
mode AUTO
arm throttle
# Observe how tightly aircraft turns at waypoints
```

---

## 6. Failsafe Parameters

### RC Failsafe

| Parameter | Default | Description | Notes |
|-----------|---------|-------------|-------|
| THR_FAILSAFE | 1 | Enable RC failsafe | 1=enabled |
| THR_FS_VALUE | 950 | RC failsafe threshold (PWM) | Below triggers failsafe |
| FS_SHORT_ACTN | 0 | Short failsafe action | 0=none, 1=RTL, 2=FBWA |
| FS_SHORT_TIMEOUT | 1.5 | Short failsafe time (sec) | Time before short action |
| FS_LONG_ACTN | 0 | Long failsafe action | 0=none, 1=RTL, 2=Land |
| FS_LONG_TIMEOUT | 5.0 | Long failsafe time (sec) | Time before long action |

### Battery Failsafe

| Parameter | Default | Description | Notes |
|-----------|---------|-------------|-------|
| BATT_MONITOR | 0 | Battery monitor type | 4=analog voltage+current |
| BATT_CAPACITY | 0 | Battery capacity (mAh) | Total battery capacity |
| BATT_LOW_VOLT | 0 | Low battery voltage | Triggers low battery action |
| BATT_CRT_VOLT | 0 | Critical battery voltage | Triggers critical battery action |
| BATT_LOW_MAH | 0 | Low battery capacity (mAh) | Alternative to voltage |
| BATT_CRT_MAH | 0 | Critical battery capacity (mAh) | Alternative to voltage |
| BATT_FS_LOW_ACT | 0 | Low battery action | 0=none, 1=RTL, 2=Land |
| BATT_FS_CRT_ACT | 0 | Critical battery action | 0=none, 1=RTL, 2=Land |

### Geofence

| Parameter | Default | Description | Notes |
|-----------|---------|-------------|-------|
| FENCE_ENABLE | 0 | Enable geofence | 0=disabled, 1=enabled |
| FENCE_TYPE | 7 | Fence type bitmask | 1=altitude, 2=circle, 4=polygon |
| FENCE_ACTION | 0 | Breach action | 0=report only, 1=RTL, 2=Land |
| FENCE_ALT_MAX | 0 | Max altitude (m) | Altitude ceiling |
| FENCE_ALT_MIN | 0 | Min altitude (m) | Altitude floor |
| FENCE_RADIUS | 0 | Circular fence radius (m) | Max distance from home |

### Failsafe Configuration Example

```bash
# Configure RC failsafe
param set THR_FAILSAFE 1
param set FS_SHORT_ACTN 1  # RTL after 1.5 sec
param set FS_LONG_ACTN 2   # Land after 5 sec

# Configure battery failsafe (4S LiPo example)
param set BATT_MONITOR 4
param set BATT_CAPACITY 5000  # 5000mAh battery
param set BATT_LOW_VOLT 14.0  # Low at 3.5V/cell
param set BATT_CRT_VOLT 13.2  # Critical at 3.3V/cell
param set BATT_FS_LOW_ACT 1   # RTL on low
param set BATT_FS_CRT_ACT 2   # Land on critical

# Configure geofence
param set FENCE_ENABLE 1
param set FENCE_TYPE 3  # Altitude + circle
param set FENCE_ACTION 1  # RTL on breach
param set FENCE_ALT_MAX 150  # 150m max altitude
param set FENCE_ALT_MIN 30   # 30m min altitude
param set FENCE_RADIUS 500   # 500m max radius
```

---

## 7. Serial Port Configuration

Configure UART ports for GPS, telemetry, companion computers.

| Parameter | Pattern | Description |
|-----------|---------|-------------|
| SERIALn_PROTOCOL | 0-28+ | What's connected (1/2=MAVLink, 5=GPS, 28=Scripting) |
| SERIALn_BAUD | 1-2000 | Baud rate (57=57600, 115=115200, 921=921600) |
| SERIALn_OPTIONS | bitmask | Special options (usually 0) |

### Common Serial Configurations

```bash
# Telemetry radio on Serial 1 (TELEM1)
param set SERIAL1_PROTOCOL 2  # MAVLink2
param set SERIAL1_BAUD 57     # 57600 baud

# GPS on Serial 3
param set SERIAL3_PROTOCOL 5  # GPS
param set SERIAL3_BAUD 115    # 115200 baud

# Companion computer on Serial 2 (TELEM2)
param set SERIAL2_PROTOCOL 2  # MAVLink2
param set SERIAL2_BAUD 921    # 921600 baud
```

---

## 8. PID Tuning Parameters

Control surface response tuning (advanced).

| Parameter Group | Description |
|----------------|-------------|
| RLL2SRV_* | Roll controller (ailerons) |
| PTCH2SRV_* | Pitch controller (elevator) |
| YAW2SRV_* | Yaw controller (rudder) |
| STEER2SRV_* | Steering (ground steering, differential thrust) |

**Note:** PID tuning is complex. Use Auto Tune feature when possible.

---

## 9. Lua Scripting Parameters

| Parameter | Default | Description | Notes |
|-----------|---------|-------------|-------|
| SCR_ENABLE | 0 | Enable Lua scripting | 1=enabled (requires reboot) |
| SCR_HEAP_SIZE | 43008 | Script heap memory (bytes) | Increase if scripts fail to load |
| SCR_USER1 - SCR_USER6 | 0 | User parameters for scripts | Custom values scripts can read |

### Enable Scripting

```bash
# Enable scripting
param set SCR_ENABLE 1
# Restart SITL to create scripts/ directory

# After restart, scripts in ~/ardupilot/ArduPlane/scripts/ will load

# Increase memory if needed
param set SCR_HEAP_SIZE 100000
```

---

## Parameter Tuning Workflows

### 1. TECS Tuning for Altitude/Speed Control

**Goal:** Smooth altitude transitions without oscillation

```bash
# Start with defaults
param fetch

# Test current behavior
mode FBWA
arm throttle
rc 3 1700
# Observe altitude oscillation

# If oscillating: increase TIME_CONST
param set TECS_TIME_CONST 7.0

# If too slow: decrease TIME_CONST
param set TECS_TIME_CONST 4.0

# If airspeed varies too much: increase THR_DAMP
param set TECS_THR_DAMP 0.7
```

### 2. Navigation Tuning for Waypoint Tracking

**Goal:** Smooth waypoint navigation without overshooting

```bash
# Load test mission
wp load mission_square.txt

# Start mission
mode AUTO
arm throttle

# If overshooting waypoints: increase NAVL1_PERIOD
param set NAVL1_PERIOD 20

# If turns too wide: decrease NAVL1_PERIOD
param set NAVL1_PERIOD 15

# Adjust waypoint acceptance
param set WP_RADIUS 50  # Must get closer
# or
param set WP_RADIUS 100  # Accept farther away
```

### 3. Failsafe Testing

**Goal:** Verify safe behavior on RC loss or low battery

```bash
# Configure failsafes
param set FS_SHORT_ACTN 1  # RTL
param set FS_LONG_ACTN 2   # Land

# Test (manually trigger RTL to simulate)
mode FBWA
arm throttle
rc 3 1700
# Let it fly for a bit
mode RTL  # Simulate RC loss failsafe
# Observe: should return and land
```

---

## Parameter Safety Tips

### Before Modifying Parameters

1. **Backup current parameters:**
   ```bash
   param save ~/backup_$(date +%Y%m%d_%H%M%S).parm
   ```

2. **Understand the parameter:**
   - Read parameter documentation
   - Check units (degrees, centidegrees, m/s, cm/s)
   - Verify range (min/max values)

3. **Make small changes:**
   - Change one parameter at a time
   - Test after each change
   - Document what you changed and why

4. **Some parameters require reboot:**
   - SERIALn_PROTOCOL
   - SCR_ENABLE
   - CAN bus parameters
   - When in doubt, reboot

### Dangerous Parameter Changes

**Avoid these without deep understanding:**
- EKF parameters (can cause crashes)
- Safety parameters set to 0 without reason
- Extreme limit values (very high roll angles)
- Disabling arming checks (bypasses safety)

---

## Parameter Documentation

### Official Resources

- **Parameter Reference:** https://ardupilot.org/plane/docs/parameters.html
  - **USE VERSION SELECTOR** to match your firmware (Plane 4.5.7)
- **Parameter Metadata:** In ArduPilot source code
- **Mission Planner:** Full parameter editor with descriptions
- **QGroundControl:** Parameter editor

### Finding Parameter Info

```bash
# In MAVProxy, get help on parameter (if available)
param show TECS_CLMB_MAX

# Check documentation online with version selector
# https://ardupilot.org/plane/docs/parameters.html

# Search ArduPilot code
cd ~/ardupilot
grep -r "TECS_CLMB_MAX" --include="*.cpp" --include="*.h"
```

---

## Common Parameter Scenarios

### Scenario: Aircraft climbs/descends too aggressively

```bash
param set TECS_TIME_CONST 7.0  # Slower response
param set TECS_CLMB_MAX 8.0   # Limit climb rate
param set TECS_SINK_MAX 5.0   # Limit descent rate
```

### Scenario: Aircraft overshoots waypoints

```bash
param set NAVL1_PERIOD 20  # Gentler turns
param set WP_RADIUS 75     # Accept earlier
```

### Scenario: Speed varies too much

```bash
param set TECS_SPDWEIGHT 1.5  # Prioritize speed slightly
param set TECS_THR_DAMP 0.7   # More throttle damping
```

### Scenario: Enable scripting for custom behavior

```bash
param set SCR_ENABLE 1
# Restart SITL
# Place .lua files in scripts/ directory
```

---

## Next Steps

1. [ ] Review default parameters: `param show *`
2. [ ] Test TECS tuning in SITL
3. [ ] Configure failsafes
4. [ ] Experiment with navigation parameters
5. [ ] Try [Lua Scripting](../Lua_Scripts/) with SCR_* parameters

---

## Additional Resources

- [ArduPilot Parameter Docs](https://ardupilot.org/plane/docs/parameters.html)
- [TECS Tuning Guide](https://ardupilot.org/plane/docs/tecs-total-energy-control-system-for-speed-height-tuning-guide.html)
- [Failsafe Documentation](https://ardupilot.org/plane/docs/apms-failsafe-function.html)
- [Main Onboarding Guide](../../../Documents/ArduPilot_Onboarding_Guide.md)

---

**Last Updated:** 2026-02-03
**Target Version:** Plane 4.5.7
