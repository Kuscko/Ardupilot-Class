# SITL Mission Plans & Testing

## Overview

SITL (Software-In-The-Loop) simulation allows you to test ArduPilot Plane without physical hardware, providing a safe environment to develop missions, tune parameters, and validate behaviors before real flights [1]. This module teaches you to create, run, and analyze mission plans in SITL, covering autonomous flight modes, parameter tuning, and troubleshooting.

**Why SITL is Essential:**
- Test dangerous or complex missions safely
- Validate parameter changes without risk
- Develop and debug custom code
- Learn flight modes and behaviors
- Save time and cost compared to field testing

## Prerequisites

Before starting this module, you should:

- Have completed ArduPilot build and SITL setup
- Understand basic flight modes (MANUAL, FBWA, AUTO, RTL)
- Be familiar with MAVProxy commands
- Know how to view and modify parameters
- Understand waypoint mission concepts

## What You'll Learn

By completing this module, you will:

- Start and configure SITL for ArduPilot Plane
- Create and upload waypoint missions
- Fly autonomous missions (takeoff, waypoint navigation, landing)
- Switch between flight modes and understand their behaviors
- Tune critical parameters (TECS, navigation, failsafes)
- Test edge cases and failure scenarios
- Analyze flight logs to verify mission performance
- Use advanced SITL features (wind, GPS denial, sensor failures)

## Quick Start

### Starting SITL

Launch ArduPilot Plane SITL with console and map:

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --map
```

**Expected Windows:**
- **Console:** Command interface (MAVProxy)
- **Map:** Visual display of vehicle location
- **Servo Output:** (optional) Servo positions

### Basic Flight Test

Perform a simple manual flight:

```bash
# In MAVProxy console

# 1. Check pre-arm status
status

# 2. Arm vehicle
arm throttle

# 3. Set throttle (channel 3)
rc 3 1700

# 4. Control pitch (channel 2)
rc 2 1400  # Pitch up

# 5. Disarm when done
disarm
```

### First Autonomous Mission

Run a simple AUTO mission:

```bash
# 1. Load example mission
wp load ~/Desktop/Work/AEVEX/SITL_Mission_Plans/missions/simple_circuit.txt

# 2. Switch to AUTO mode
mode AUTO

# 3. Arm and takeoff
arm throttle

# Watch the vehicle follow waypoints on the map
```

## Key Concepts

### SITL Architecture

SITL simulates the entire flight controller in software [1]:

```
[ArduPlane Binary] <--> [Physics Simulator] <--> [MAVProxy/GCS]
       |                       |
       |                   Simulates:
   Simulates:            - Aircraft dynamics
   - Sensors (GPS,       - Wind effects
     IMU, baro)          - Ground interactions
   - Actuators           - Sensor readings
   - Flight code
```

### Flight Modes for Fixed-Wing

**Manual Modes:**
- **MANUAL:** Direct RC control (no stabilization)
- **FBWA (Fly-By-Wire A):** Stabilized flight, pilot controls roll/pitch
- **FBWB (Fly-By-Wire B):** Stabilized with altitude hold
- **CRUISE:** Maintains altitude and heading

**Autonomous Modes:**
- **AUTO:** Follows waypoint missions
- **RTL (Return-To-Launch):** Automatically returns home
- **GUIDED:** External computer control
- **LOITER:** Circles at current location

See [Flight Modes Documentation](https://ardupilot.org/plane/docs/flight-modes.html) [2] for complete descriptions.

### Mission Commands

Waypoint missions consist of navigation and control commands [3]:

**NAV_WAYPOINT:** Fly to coordinates
**NAV_TAKEOFF:** Automatic takeoff
**NAV_LAND:** Automatic landing
**NAV_LOITER_TIME:** Circle for specified time
**NAV_LOITER_UNLIM:** Circle indefinitely
**DO_SET_SERVO:** Control servo outputs
**DO_CHANGE_SPEED:** Modify airspeed

### TECS (Total Energy Control System)

TECS manages the tradeoff between altitude and airspeed [4]:

- **TECS_PITCH_MAX/MIN:** Pitch angle limits
- **TECS_THR_MAX/MIN:** Throttle limits
- **TECS_CLMB_MAX:** Maximum climb rate
- **TECS_SINK_MAX:** Maximum sink rate
- **TECS_SPDWEIGHT:** Speed vs altitude priority

Proper TECS tuning is critical for smooth, predictable flight.

## Hands-On Practice

### Exercise 1: Basic SITL Operation

Start SITL and familiarize yourself with the interface:

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --map

# In console:
mode FBWA          # Set mode
arm throttle       # Arm
rc 3 1600          # Throttle
rc 1 1600          # Roll right
rc 2 1400          # Pitch up
disarm             # Disarm when done
```

**Practice:** Fly stable figure-8s in FBWA mode

### Exercise 2: Simple Circuit Mission

Load and fly the basic circuit mission:

```bash
# Load mission
wp load ~/Desktop/Work/AEVEX/SITL_Mission_Plans/missions/simple_circuit.txt

# List waypoints
wp list

# Switch to AUTO
mode AUTO
arm throttle

# Monitor progress
watch MISSION_CURRENT
```

**Mission includes:** Takeoff, 4 waypoints in rectangle, return, land

### Exercise 3: Test RTL (Return-To-Launch)

Simulate emergency return:

```bash
# Takeoff and fly away
mode FBWA
arm throttle
rc 3 1700
# Fly for 30 seconds

# Trigger RTL
mode RTL

# Vehicle should:
# 1. Climb to RTL_ALTITUDE
# 2. Fly to home location
# 3. Loiter or land (based on RTL_AUTOLAND)
```

### Exercise 4: Parameter Exploration - TECS Tuning

Experiment with TECS parameters:

```bash
# Load TECS parameter set
param load ~/Desktop/Work/AEVEX/SITL_Mission_Plans/parameters/tecs_aggressive.param

# Fly mission and observe behavior
mode AUTO
arm throttle

# Try conservative parameters
param load ~/Desktop/Work/AEVEX/SITL_Mission_Plans/parameters/tecs_conservative.param

# Compare climb rates, speed control
```

### Exercise 5: Failsafe Testing

Test failsafe behaviors:

```bash
# Set failsafe parameters
param set FS_SHORT_ACTN 1  # Short failsafe: RTL
param set FS_LONG_ACTN 1   # Long failsafe: RTL

# Simulate RC signal loss
rc override 3 1000  # Throttle low (triggers failsafe)

# Vehicle should enter RTL mode
# Restore control
rc override 0  # Clear overrides
```

### Exercise 6: GPS Denied Flight

Test behavior without GPS:

```bash
# Disable GPS mid-flight
param set SIM_GPS_DISABLE 1

# Observe EKF response
# Vehicle should continue with dead reckoning

# Restore GPS
param set SIM_GPS_DISABLE 0
```

### Exercise 7: Wind Simulation

Add environmental challenges:

```bash
# Set wind (north 10 m/s, gusts 5 m/s)
param set SIM_WIND_DIR 0
param set SIM_WIND_SPD 10
param set SIM_WIND_TURB 5

# Fly mission and observe compensation
mode AUTO
arm throttle
```

## Example Missions

This module includes several sample missions:

| Mission | Description | Complexity | Duration |
|---------|-------------|------------|----------|
| [simple_circuit.txt](missions/simple_circuit.txt) | Basic rectangle pattern | Beginner | 5 min |
| [long_range.txt](missions/long_range.txt) | Extended flight path | Beginner | 15 min |
| [survey_pattern.txt](missions/survey_pattern.txt) | Grid survey mission | Intermediate | 20 min |
| [loiter_test.txt](missions/loiter_test.txt) | Multiple loiter points | Intermediate | 10 min |
| [emergency_land.txt](missions/emergency_land.txt) | Forced landing scenario | Advanced | 5 min |

## Complete Guides

This module includes detailed documentation:

- **[SITL_QUICK_START.md](SITL_QUICK_START.md)** - Getting started with SITL
- **[EXAMPLE_MISSIONS.md](EXAMPLE_MISSIONS.md)** - Mission walkthroughs
- **[PARAMETER_GUIDE.md](PARAMETER_GUIDE.md)** - Parameter tuning reference
- **[USING_EXAMPLES.md](USING_EXAMPLES.md)** - How to use example files

## Parameter Categories

See **[PARAMETER_GUIDE.md](PARAMETER_GUIDE.md)** for comprehensive parameter documentation:

**TECS Parameters** (`parameters/tecs_*.param`):
- Default, aggressive, conservative configurations
- Climb rate and speed control tuning

**Failsafe Parameters** (`parameters/failsafe_*.param`):
- Battery failsafe configuration
- RC signal loss handling
- GPS failure responses

**Navigation Parameters** (`parameters/navigation_*.param`):
- Waypoint acceptance radius
- Loiter radius
- Approach speeds

**Hardware/Serial Parameters** (`parameters/hardware_serial_*.param`):
- Serial port configuration
- Peripheral device setup

## Common Issues

### Issue: SITL fails to start

**Symptom:** `sim_vehicle.py` exits with errors

**Solutions:**
1. Ensure ArduPilot is built: `cd ~/ardupilot && ./waf plane`
2. Check Python dependencies: `pip3 list | grep pymavlink`
3. Try clean rebuild: `./waf clean && ./waf configure --board sitl && ./waf plane`
4. Verify working directory: Must run from `~/ardupilot/ArduPlane`

### Issue: Map window doesn't appear

**Symptom:** Console starts but no map displayed

**Solutions (WSL2):**
1. Verify X server running on Windows
2. Check DISPLAY variable: `echo $DISPLAY`
3. Set DISPLAY: `export DISPLAY=:0`
4. Test X11: `xeyes &`
5. See [X Server Setup Guide](../Installation_Scripts/setup_x_server.md)

### Issue: Vehicle won't arm

**Symptom:** `arm throttle` fails with pre-arm checks

**Solutions:**
```bash
# Check pre-arm status
status

# Common issues:
# - EKF not initialized: Wait 10-15 seconds
# - GPS no fix: Wait for GPS lock (status gps)
# - Safety switch: Set ARMING_CHECK to bypass (testing only)

# Bypass specific checks (SITL only)
param set ARMING_CHECK 0  # Disable all checks (use cautiously)
```

### Issue: Vehicle crashes immediately after takeoff

**Symptom:** Aircraft enters uncontrolled descent after launch

**Common Causes:**
- TECS parameters too aggressive
- Insufficient throttle
- Center of gravity incorrect

**Solutions:**
1. Check TECS_THR_MAX is high enough (default 100%)
2. Verify TRIM_THROTTLE adequate for level flight
3. Adjust TECS_PITCH_MAX/MIN for gentler climbs
4. Review TECS parameters in **[PARAMETER_GUIDE.md](PARAMETER_GUIDE.md)**

### Issue: Mission waypoints not followed accurately

**Symptom:** Vehicle misses waypoints or takes wide turns

**Solutions:**
1. Increase WP_RADIUS (waypoint acceptance radius)
2. Reduce WP_LOITER_RAD for tighter circles
3. Check NAVL1_PERIOD (L1 controller navigation tuning)
4. Lower airspeed for tighter turns: `param set TRIM_ARSPD_CM 1200`
5. Review navigation parameters in **[PARAMETER_GUIDE.md](PARAMETER_GUIDE.md)**

### Issue: Vehicle oscillates in AUTO mode

**Symptom:** Roll or pitch oscillations during autonomous flight

**Solutions:**
1. Check TECS tuning (TECS_SPDWEIGHT, TECS_TIME_CONST)
2. Verify L1 controller: NAVL1_PERIOD, NAVL1_DAMPING
3. Review PID tuning (RLL2SRV_*, PTCH2SRV_*)
4. See [PID Tuning Guide](../Advanced_Topics/PID_Tuning/)

See **[SITL_QUICK_START.md](SITL_QUICK_START.md)** for detailed troubleshooting.

## Advanced SITL Features

### Replay Flight Logs

Replay previous flights in SITL:

```bash
sim_vehicle.py --replay <logfile.BIN>
```

### Multi-Vehicle Simulation

Run multiple vehicles simultaneously:

```bash
sim_vehicle.py --instance 0 --out 127.0.0.1:14550
sim_vehicle.py --instance 1 --out 127.0.0.1:14551
```

### Custom Start Location

Begin simulation at specific coordinates:

```bash
sim_vehicle.py --location CMAC  # Predefined location
sim_vehicle.py -L 51.8,-35.4,0,0  # Custom lat,lon,alt,heading
```

See [SITL Advanced Features](../Advanced_Topics/SITL_Advanced_Features/) for more.

## Additional Resources

### Official ArduPilot Documentation

- **[SITL Simulator](https://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html)** [1] - SITL overview
- **[Flight Modes](https://ardupilot.org/plane/docs/flight-modes.html)** [2] - Mode descriptions
- **[Mission Planning](https://ardupilot.org/plane/docs/common-planning-a-mission-with-waypoints-and-events.html)** [3] - Mission creation
- **[TECS Tuning](https://ardupilot.org/plane/docs/tecs-total-energy-control-system-for-speed-height-tuning-guide.html)** [4] - TECS guide
- **[Parameter List](https://ardupilot.org/plane/docs/parameters.html)** - Complete parameter reference

### MAVProxy Documentation

- **[MAVProxy Commands](https://ardupilot.org/mavproxy/docs/getting_started/cheatsheet.html)** - Command reference
- **[MAVProxy Modules](https://ardupilot.org/mavproxy/docs/modules/index.html)** - Available modules
- **[Scripting MAVProxy](https://ardupilot.org/mavproxy/docs/development/scripting.html)** - Automation

### Mission Planning Tools

- **[Mission Planner](https://ardupilot.org/planner/)** - Windows GCS with mission planner
- **[QGroundControl](http://qgroundcontrol.com/)** - Cross-platform GCS
- **[MAVProxy wp editor](https://ardupilot.org/mavproxy/docs/modules/wp.html)** - Command-line mission editing

### Community Resources

- [ArduPilot Discord: Plane Channel](https://ardupilot.org/discord)
- [Discourse: Plane Topics](https://discuss.ardupilot.org/c/arduplane/15)
- [GitHub: SITL Issues](https://github.com/ArduPilot/ardupilot/labels/SITL)

## Next Steps

After completing this SITL mission planning module:

1. **PID Tuning** - Fine-tune flight characteristics ([PID Tuning Guide](../Advanced_Topics/PID_Tuning/))
2. **Navigation Deep Dive** - Master advanced navigation ([Navigation Guide](../Advanced_Topics/Navigation_Deep_Dive/))
3. **Failsafe Testing** - Implement robust safety features ([Safety & Geofencing](../Advanced_Topics/Safety_Geofencing/))
4. **Hardware Testing** - Transfer knowledge to real aircraft (HITL or flight testing)
5. **Log Analysis** - Analyze flight data ([Flight Log Analysis](../Advanced_Topics/Flight_Log_Analysis/))

---

**Sources:**

[1] https://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html
[2] https://ardupilot.org/plane/docs/flight-modes.html
[3] https://ardupilot.org/plane/docs/common-planning-a-mission-with-waypoints-and-events.html
[4] https://ardupilot.org/plane/docs/tecs-total-energy-control-system-for-speed-height-tuning-guide.html
