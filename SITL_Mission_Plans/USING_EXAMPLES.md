# Using Mission and Parameter Examples

This guide explains how to use the example missions and parameter files for hands-on learning.

## Quick Start

### 1. Load a Mission File

```bash
# In MAVProxy
wp load SITL_Mission_Plans/simple_flight.waypoints
wp list
mode AUTO
arm throttle
```

### 2. Load Parameter File

```bash
# In MAVProxy
param load SITL_Mission_Plans/params_conservative.param
param show TECS_*
```

---

## Example Missions

### mission_template.waypoints
**Purpose:** Template showing all fields and common commands

**Usage:**
- Copy this file to create custom missions
- Modify waypoints, commands, and parameters
- Reference for command IDs and field meanings

### simple_flight.waypoints
**Purpose:** Basic flight for testing SITL setup

**Profile:**
- Takeoff to 100m
- Two waypoints
- Return and land

**Duration:** ~5 minutes

**Good for:**
- First SITL flight
- Verifying installation
- Learning MAVProxy commands

**Commands to try:**
```bash
wp load SITL_Mission_Plans/simple_flight.waypoints
mode AUTO
arm throttle
# Watch the flight
wp set 2    # Skip to waypoint 2
mode RTL    # Return early
```

### square_pattern.waypoints
**Purpose:** Navigation accuracy testing

**Profile:**
- 500m x 500m square
- 80m altitude
- Tests turning precision

**Duration:** ~8 minutes

**Good for:**
- Navigation tuning
- L1 controller testing
- Wind compensation
- GPS accuracy validation

**Watch for:**
- How well aircraft follows corners
- Overshoot/undershoot
- Wind drift compensation

### altitude_test.waypoints
**Purpose:** TECS climb/descent testing

**Profile:**
- Progressive altitude changes
- 50m → 100m → 150m → 200m → descend

**Duration:** ~10 minutes

**Good for:**
- TECS tuning
- Climb/sink rate validation
- Airspeed control testing

**Parameters to monitor:**
```bash
param show TECS_CLMB_MAX
param show TECS_SINK_MAX
param show TECS_TIME_CONST
```

**Try modifying:**
```bash
param set TECS_CLMB_MAX 3.0  # Slower climb
param set TECS_TIME_CONST 8.0  # More conservative
```

### loiter_test.waypoints
**Purpose:** Loiter behavior testing

**Profile:**
- Loiter 3 turns at waypoint
- Loiter 30 seconds at another waypoint

**Duration:** ~8 minutes

**Good for:**
- Loiter radius accuracy
- Circle tracking
- Bank angle limits
- Position hold testing

**Parameters to adjust:**
```bash
param show WP_LOITER_RAD
param set WP_LOITER_RAD 100  # Larger circle
param show LIM_ROLL_CD
```

### speed_test.waypoints
**Purpose:** Airspeed control testing

**Profile:**
- Changes speed: 12 m/s → 18 m/s → 15 m/s
- Tests TECS speed/altitude coupling

**Duration:** ~7 minutes

**Good for:**
- TECS_SPDWEIGHT tuning
- Throttle response
- Airspeed sensor validation

**Watch for:**
- Altitude changes during speed changes
- Throttle response
- Speed tracking accuracy

---

## Example Parameter Files

### params_conservative.param
**Purpose:** Safe parameters for initial flights

**Characteristics:**
- Gentle climb/descent (3/2 m/s)
- Limited throttle (70%)
- Gentle turns (30° bank)
- All failsafes enabled

**Usage:**
```bash
param load SITL_Mission_Plans/params_conservative.param
param show TECS_*
```

**Use when:**
- First flights
- Testing new code
- Unfamiliar aircraft
- Windy conditions

### params_performance.param
**Purpose:** Aggressive flight parameters

**Characteristics:**
- Fast climb/descent (8/6 m/s)
- Full throttle (100%)
- Aggressive turns (60° bank)
- Wide speed range

**WARNING:** Only use after testing conservative parameters!

**Usage:**
```bash
param load SITL_Mission_Plans/params_performance.param
# Test in SITL first!
```

**Use when:**
- Performance testing
- Racing scenarios
- Advanced tuning
- After successful conservative testing

### params_tecs_tuning.param
**Purpose:** TECS parameter tuning baseline

**Includes:**
- Baseline TECS parameters
- Logging enabled
- Fixed airspeed for consistency
- Tuning guidelines in comments

**Usage:**
```bash
param load SITL_Mission_Plans/params_tecs_tuning.param
wp load SITL_Mission_Plans/altitude_test.waypoints
mode AUTO
# Observe behavior, adjust one parameter at a time
```

**Tuning workflow:**
1. Load tuning parameters
2. Load altitude_test mission
3. Fly mission and observe
4. Adjust ONE parameter
5. Fly again and compare
6. Repeat

---

## Hands-On Exercises

### Exercise 1: Your First Mission
```bash
# Start SITL
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map

# Load and fly simple mission
wp load SITL_Mission_Plans/simple_flight.waypoints
wp list
mode AUTO
arm throttle

# Observe flight, take notes
```

### Exercise 2: Compare Parameters
```bash
# Test 1: Conservative
param load SITL_Mission_Plans/params_conservative.param
wp load SITL_Mission_Plans/altitude_test.waypoints
mode AUTO
arm throttle
# Note: climb rate, time to altitude

# Test 2: Performance
param load SITL_Mission_Plans/params_performance.param
wp load SITL_Mission_Plans/altitude_test.waypoints
mode AUTO
arm throttle
# Compare: How much faster? More aggressive?
```

### Exercise 3: Create Custom Mission
```bash
# Copy template
cp SITL_Mission_Plans/mission_template.waypoints my_mission.waypoints

# Edit waypoints in text editor
# Change lat/lon/alt values
# Modify commands

# Test your mission
wp load my_mission.waypoints
wp list
mode AUTO
arm throttle
```

### Exercise 4: TECS Tuning
```bash
# Load tuning baseline
param load SITL_Mission_Plans/params_tecs_tuning.param

# Fly altitude test
wp load SITL_Mission_Plans/altitude_test.waypoints
mode AUTO
arm throttle

# Observe: How fast does it climb? Overshoot?

# Adjust TIME_CONST
param set TECS_TIME_CONST 3.0  # More aggressive
# Fly again, compare

param set TECS_TIME_CONST 8.0  # More conservative
# Fly again, compare

# Which is best for your goals?
```

---

## Tips for Success

### Mission Files
- Always check `wp list` after loading
- Verify home position (waypoint 0)
- Check altitude is reasonable
- Test in SITL before real flights

### Parameters
- **Save before changes:** `param save backup.param`
- Change ONE parameter at a time
- Document what you changed
- Some parameters need reboot

### Testing
- Start conservative, work toward aggressive
- Use altitude_test for TECS tuning
- Use square_pattern for navigation tuning
- Use loiter_test for position hold tuning

### Troubleshooting
- Mission won't load? Check file format
- Won't arm? Check pre-arm errors
- Doesn't follow mission? Check AUTO mode
- Parameters not taking effect? Try rebooting

---

## Creating Your Own Examples

### Custom Mission
1. Copy `mission_template.waypoints`
2. Modify waypoints for your test area
3. Add/remove waypoints as needed
4. Test in SITL thoroughly
5. Document purpose and usage

### Custom Parameters
1. Start with existing param file
2. Modify specific parameters
3. Add comments explaining changes
4. Test each change in SITL
5. Document expected behavior

---

**Author:** Patrick Kelly (@Kuscko)
**Version:** 1.0
