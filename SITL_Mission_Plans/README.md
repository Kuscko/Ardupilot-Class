# SITL Mission Plans & Testing

## Overview

SITL (Software-In-The-Loop) runs ArduPilot firmware on your computer, providing a safe environment to develop missions, tune parameters, and validate behaviors before real flights.

## Prerequisites

- ArduPilot build and SITL setup complete
- Familiar with basic flight modes (MANUAL, FBWA, AUTO, RTL)
- Comfortable with MAVProxy commands and parameters

## Quick Start

### Starting SITL

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --map
```

### Basic Flight Test

```bash
status
arm throttle
rc 3 1700
rc 2 1400  # Pitch up
disarm
```

### First Autonomous Mission

```bash
wp load ~/Desktop/Work/AEVEX/SITL_Mission_Plans/missions/simple_circuit.txt
mode AUTO
arm throttle
```

## Key Concepts

### SITL Architecture

```
[ArduPlane Binary] <--> [Physics Simulator] <--> [MAVProxy/GCS]
       |                       |
   Simulates:             Simulates:
   - Sensors (GPS,        - Aircraft dynamics
     IMU, baro)           - Wind effects
   - Actuators            - Ground interactions
   - Flight code          - Sensor readings
```

### Flight Modes

**Manual:** MANUAL, FBWA (stabilized), FBWB (altitude hold), CRUISE

**Autonomous:** AUTO (waypoints), RTL (return home), GUIDED, LOITER

See [Flight Modes Documentation](https://ardupilot.org/plane/docs/flight-modes.html).

### Mission Commands

- **NAV_WAYPOINT:** Fly to coordinates
- **NAV_TAKEOFF:** Automatic takeoff
- **NAV_LAND:** Automatic landing
- **NAV_LOITER_TIME:** Circle for specified time
- **DO_CHANGE_SPEED:** Modify airspeed

### TECS Parameters

TECS manages the tradeoff between altitude and airspeed: `TECS_CLMB_MAX`, `TECS_SINK_MAX`, `TECS_SPDWEIGHT`, `TECS_TIME_CONST`.

## Hands-On Exercises

### Exercise 1: Basic SITL Operation

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --map

mode FBWA
arm throttle
rc 3 1600
rc 1 1600  # Roll right
rc 2 1400  # Pitch up
disarm
```

### Exercise 2: Simple Circuit Mission

```bash
wp load ~/Desktop/Work/AEVEX/SITL_Mission_Plans/missions/simple_circuit.txt
wp list
mode AUTO
arm throttle
```

Mission includes: takeoff, 4 waypoints in rectangle, return, land.

### Exercise 3: Test RTL

```bash
mode FBWA
arm throttle
rc 3 1700
mode RTL
# Vehicle climbs to RTL_ALTITUDE, returns home, loiters or lands
```

### Exercise 4: TECS Tuning

```bash
param load ~/Desktop/Work/AEVEX/SITL_Mission_Plans/parameters/tecs_aggressive.param
mode AUTO
arm throttle

param load ~/Desktop/Work/AEVEX/SITL_Mission_Plans/parameters/tecs_conservative.param
# Compare climb rates and speed control
```

### Exercise 5: Failsafe Testing

```bash
param set FS_SHORT_ACTN 1
param set FS_LONG_ACTN 1
rc override 3 1000   # Throttle low (triggers failsafe)
rc override 0        # Clear overrides
```

### Exercise 6: GPS Denied Flight

```bash
param set SIM_GPS_DISABLE 1
# Observe EKF response / dead reckoning
param set SIM_GPS_DISABLE 0
```

### Exercise 7: Wind Simulation

```bash
param set SIM_WIND_DIR 0
param set SIM_WIND_SPD 10
param set SIM_WIND_TURB 5
mode AUTO
arm throttle
```

## Example Missions

| Mission | Description | Complexity | Duration |
|---------|-------------|------------|----------|
| [simple_circuit.txt](missions/simple_circuit.txt) | Basic rectangle pattern | Beginner | 5 min |
| [long_range.txt](missions/long_range.txt) | Extended flight path | Beginner | 15 min |
| [survey_pattern.txt](missions/survey_pattern.txt) | Grid survey mission | Intermediate | 20 min |
| [loiter_test.txt](missions/loiter_test.txt) | Multiple loiter points | Intermediate | 10 min |
| [emergency_land.txt](missions/emergency_land.txt) | Forced landing scenario | Advanced | 5 min |

## Complete Guides

- **[SITL_QUICK_START.md](SITL_QUICK_START.md)** - Getting started with SITL
- **[EXAMPLE_MISSIONS.md](EXAMPLE_MISSIONS.md)** - Mission walkthroughs
- **[PARAMETER_GUIDE.md](PARAMETER_GUIDE.md)** - Parameter tuning reference
- **[USING_EXAMPLES.md](USING_EXAMPLES.md)** - How to use example files

## Parameter Categories

See **[PARAMETER_GUIDE.md](PARAMETER_GUIDE.md)** for details.

- **TECS** (`parameters/tecs_*.param`): climb rate, speed control
- **Failsafe** (`parameters/failsafe_*.param`): battery, RC loss, GPS failure
- **Navigation** (`parameters/navigation_*.param`): waypoint radius, loiter, approach speeds
- **Hardware/Serial** (`parameters/hardware_serial_*.param`): port and peripheral config

## Common Issues

### SITL fails to start
1. Build ArduPilot: `cd ~/ardupilot && ./waf plane`
2. Check dependencies: `pip3 list | grep pymavlink`
3. Verify working directory: `~/ardupilot/ArduPlane`

### Map window doesn't appear
1. Verify X server running on Windows
2. Check `echo $DISPLAY`; set with `export DISPLAY=:0`
3. See [X Server Setup Guide](../Installation_Scripts/setup_x_server.md)

### Vehicle won't arm
```bash
status
# EKF not initialized: wait 10-15 sec
# GPS no fix: wait for lock (status gps)
param set ARMING_CHECK 0  # Bypass checks (SITL testing only)
```

### Mission waypoints not followed accurately
1. Increase `WP_RADIUS`
2. Check `NAVL1_PERIOD`
3. Lower airspeed: `param set TRIM_ARSPD_CM 1200`
4. See **[PARAMETER_GUIDE.md](PARAMETER_GUIDE.md)**

## Advanced SITL Features

```bash
sim_vehicle.py --replay <logfile.BIN>          # Replay flight logs

sim_vehicle.py --instance 0 --out 127.0.0.1:14550  # Multi-vehicle
sim_vehicle.py --instance 1 --out 127.0.0.1:14551

sim_vehicle.py --location CMAC                 # Predefined location
sim_vehicle.py -L 51.8,-35.4,0,0              # Custom lat,lon,alt,heading
```

## Additional Resources

- **[SITL Simulator](https://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html)**
- **[Flight Modes](https://ardupilot.org/plane/docs/flight-modes.html)**
- **[TECS Tuning](https://ardupilot.org/plane/docs/tecs-total-energy-control-system-for-speed-height-tuning-guide.html)**
- **[MAVProxy Commands](https://ardupilot.org/mavproxy/docs/getting_started/cheatsheet.html)**
- **[Mission Planner](https://ardupilot.org/planner/)** | **[QGroundControl](http://qgroundcontrol.com/)**
- [ArduPilot Discord](https://ardupilot.org/discord) | [Discourse](https://discuss.ardupilot.org/c/arduplane/15)

## Next Steps

1. **PID Tuning** - Fine-tune flight characteristics ([PID Tuning Guide](../Advanced_Topics/PID_Tuning/))
2. **Failsafe Testing** - Implement robust safety features ([Safety & Geofencing](../Advanced_Topics/Safety_Geofencing/))
3. **Hardware Testing** - Transfer knowledge to real aircraft
4. **Log Analysis** - Analyze flight data ([Flight Log Analysis](../Advanced_Topics/Flight_Log_Analysis/))
