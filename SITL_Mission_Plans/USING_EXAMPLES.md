# Using Mission and Parameter Examples

## Quick Start

```bash
# Load and fly a mission
wp load SITL_Mission_Plans/simple_flight.waypoints
wp list
mode AUTO
arm throttle

# Load a parameter file
param load SITL_Mission_Plans/params_conservative.param
param show TECS_*
```

---

## Example Missions

### mission_template.waypoints

Template showing all fields and common commands. Copy this to create custom missions.

### simple_flight.waypoints

**Profile:** Takeoff to 100m → two waypoints → land | **Duration:** ~5 min

```bash
wp load SITL_Mission_Plans/simple_flight.waypoints
mode AUTO
arm throttle
wp set 2    # Skip to waypoint 2
mode RTL    # Return early
```

### square_pattern.waypoints

**Profile:** 500m × 500m square at 80m | **Duration:** ~8 min

Good for navigation tuning, L1 controller testing, wind compensation.

Watch for: corner overshoot/undershoot, wind drift compensation.

### altitude_test.waypoints

**Profile:** 50m → 100m → 150m → 200m → descend | **Duration:** ~10 min

Good for TECS tuning, climb/sink rate validation.

```bash
param show TECS_CLMB_MAX
param show TECS_SINK_MAX
param show TECS_TIME_CONST

param set TECS_CLMB_MAX 3.0   # Slower climb
param set TECS_TIME_CONST 8.0  # More conservative
```

### loiter_test.waypoints

**Profile:** Loiter 3 turns at one point, 30 seconds at another | **Duration:** ~8 min

Good for loiter radius, circle tracking, bank angle limits.

```bash
param show WP_LOITER_RAD
param set WP_LOITER_RAD 100
```

### speed_test.waypoints

**Profile:** Speed changes 12 → 18 → 15 m/s | **Duration:** ~7 min

Good for `TECS_SPDWEIGHT` tuning, throttle response, airspeed validation.

Watch for: altitude changes during speed changes, throttle hunting.

---

## Example Parameter Files

### params_conservative.param

Gentle climb/descent (3/2 m/s), 70% throttle, 30° bank, all failsafes enabled.

```bash
param load SITL_Mission_Plans/params_conservative.param
```

Use for: first flights, new code, unfamiliar aircraft, windy conditions.

### params_performance.param

Fast climb/descent (8/6 m/s), 100% throttle, 60° bank, wide speed range.

> **WARNING:** Only use after testing conservative parameters!

```bash
param load SITL_Mission_Plans/params_performance.param
```

### params_tecs_tuning.param

TECS baseline for systematic tuning. Change one parameter at a time and fly `altitude_test` to compare.

```bash
param load SITL_Mission_Plans/params_tecs_tuning.param
wp load SITL_Mission_Plans/altitude_test.waypoints
mode AUTO
# Observe, adjust ONE parameter, fly again
```

---

## Hands-On Exercises

### Exercise 1: Your First Mission

```bash
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map

wp load SITL_Mission_Plans/simple_flight.waypoints
wp list
mode AUTO
arm throttle
```

### Exercise 2: Compare Parameters

```bash
# Test 1: Conservative
param load SITL_Mission_Plans/params_conservative.param
wp load SITL_Mission_Plans/altitude_test.waypoints
mode AUTO
arm throttle

# Test 2: Performance
param load SITL_Mission_Plans/params_performance.param
wp load SITL_Mission_Plans/altitude_test.waypoints
mode AUTO
arm throttle
```

### Exercise 3: Create Custom Mission

```bash
cp SITL_Mission_Plans/mission_template.waypoints my_mission.waypoints
# Edit waypoints in text editor
wp load my_mission.waypoints
wp list
mode AUTO
arm throttle
```

### Exercise 4: TECS Tuning

```bash
param load SITL_Mission_Plans/params_tecs_tuning.param
wp load SITL_Mission_Plans/altitude_test.waypoints
mode AUTO
arm throttle

param set TECS_TIME_CONST 3.0  # More aggressive — fly and compare
param set TECS_TIME_CONST 8.0  # More conservative — fly and compare
```

---

## Tips for Success

**Missions:** Always `wp list` after loading. Verify WP 0 and altitude. Test in SITL before real flights.

**Parameters:** `param save backup.param` before changes. Change one at a time. Some need reboot.

**Testing:** Use `altitude_test` for TECS, `square_pattern` for navigation, `loiter_test` for position hold.

**Troubleshooting:**

- Mission won't load → check file format
- Won't arm → check pre-arm errors
- Doesn't follow mission → verify AUTO mode
- Parameters not taking effect → reboot

---

## Creating Your Own Examples

**Custom Mission:** Copy template, modify waypoints, test in SITL, document purpose.

**Custom Parameters:** Start with an existing param file, modify specific parameters, add comments, test each change.

---

**Author:** Patrick Kelly (@Kuscko)
**Version:** 1.0
