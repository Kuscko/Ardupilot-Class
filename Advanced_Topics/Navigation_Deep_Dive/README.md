# Navigation Deep Dive

## Overview

Master advanced navigation and path planning in ArduPilot by understanding the L1 controller, waypoint navigation, and complex mission patterns. Navigation is at the heart of autonomous flight, determining how the vehicle follows paths, handles turns, and transitions between waypoints [1].

This module covers the mathematical foundations of ArduPilot's navigation algorithms, tuning parameters for precision path following, and creating complex mission patterns for real-world applications.

## Prerequisites

Before starting this module, you should have:

- Completed basic mission planning and waypoint navigation
- Understanding of ArduPilot flight modes (AUTO, GUIDED)
- Familiarity with MAVLink mission commands
- SITL environment set up for testing
- Basic understanding of control theory and navigation concepts

## What You'll Learn

By completing this module, you will:

- Understand the L1 controller and its role in path following
- Configure NAVL1_* parameters for optimal navigation
- Create complex mission patterns with advanced waypoint commands
- Implement smooth transitions between waypoints
- Use conditional commands (DO_JUMP, DO_SET_ROI)
- Optimize navigation for speed, precision, and efficiency
- Analyze navigation performance from flight logs

## Key Concepts

### L1 Controller

ArduPilot uses the L1 nonlinear guidance law for path following [1]:

- **Lateral acceleration control:** Generates smooth curved paths
- **Period parameter (NAVL1_PERIOD):** Controls how aggressively vehicle turns
- **Damping ratio (NAVL1_DAMPING):** Reduces oscillation around path
- **Look-ahead distance:** Dynamically calculated based on speed and turn radius

**L1 Controller Benefits:**
- Handles varying speeds gracefully
- Optimal performance at different altitudes
- Smooth curved paths vs sharp turns
- Predictable behavior in wind

### Path Planning Algorithms

ArduPilot implements several path planning strategies [2]:

- **Waypoint navigation:** Point-to-point straight lines
- **Spline waypoints:** Smooth curves through waypoints
- **Loiter turns:** Circular holding patterns
- **Survey grids:** Automated coverage patterns

### Navigation Parameters

Key parameters affecting navigation [3]:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| NAVL1_PERIOD | 20 | L1 controller period (seconds) |
| NAVL1_DAMPING | 0.75 | L1 damping ratio |
| WP_RADIUS | 90 | Waypoint acceptance radius (meters) |
| WP_LOITER_RAD | 75 | Loiter radius (meters) |
| NAVL1_XTRACK_I | 0.02 | Cross-track error integrator gain |

## Hands-On Practice

### Exercise 1: Configure L1 Controller

Tune L1 parameters for your vehicle:

```bash
# Start SITL
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --map

# Configure L1 controller
param set NAVL1_PERIOD 20        # Default: 20 seconds
param set NAVL1_DAMPING 0.75     # Default: 0.75
param set NAVL1_XTRACK_I 0.02    # Cross-track integrator
param write
reboot
```

**Parameter effects:**
- **NAVL1_PERIOD** smaller = tighter turns, more aggressive
- **NAVL1_PERIOD** larger = wider turns, smoother
- **NAVL1_DAMPING** lower = faster response, may oscillate
- **NAVL1_DAMPING** higher = smoother, less overshoot

### Exercise 2: Test Basic Waypoint Navigation

Create a simple mission to baseline navigation performance:

```python
# simple_mission.py
from pymavlink import mavutil
import time

# Connect
master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()

# Clear existing mission
master.mav.mission_clear_all_send(
    master.target_system,
    master.target_component)

# Define waypoints
waypoints = [
    # Takeoff to 100m
    (0, 0, 100, 22),  # MAV_CMD_NAV_TAKEOFF
    # Fly square pattern
    (35.3632, 149.1652, 100, 16),  # WAYPOINT
    (35.3632, 149.1752, 100, 16),
    (35.3532, 149.1752, 100, 16),
    (35.3532, 149.1652, 100, 16),
    # Return and land
    (35.3632, 149.1652, 100, 16),
    (0, 0, 0, 21),  # MAV_CMD_NAV_LAND
]

# Upload mission
master.mav.mission_count_send(
    master.target_system,
    master.target_component,
    len(waypoints))

# Send each waypoint
for i, wp in enumerate(waypoints):
    master.mav.mission_item_send(
        master.target_system,
        master.target_component,
        i,  # seq
        0,  # frame (MAV_FRAME_GLOBAL)
        wp[3],  # command
        0, 0, 0, 0, 0, 0,  # params
        wp[0], wp[1], wp[2])  # x, y, z

    # Wait for ACK
    ack = master.recv_match(type='MISSION_ACK', blocking=True, timeout=5)
    print(f"Waypoint {i} uploaded")

print("Mission uploaded!")
```

**Expected behavior:**
- Smooth transitions between waypoints
- Consistent turn radius
- Arrives within WP_RADIUS of each waypoint

### Exercise 3: Speed and Altitude Transitions

Control speed changes during navigation:

```python
# Speed change example waypoints
waypoints = [
    # Takeoff
    (35.3632, 149.1652, 100, 22),  # TAKEOFF

    # Cruise at normal speed
    (35.3632, 149.1752, 100, 16),  # WAYPOINT

    # Change speed to 20 m/s
    (178, 1, 20, 0, 0, 0, 0),  # DO_CHANGE_SPEED (airspeed)

    # Next waypoint at 20 m/s
    (35.3532, 149.1752, 100, 16),

    # Climb to 200m
    (35.3532, 149.1652, 200, 16),

    # Descend back to 100m
    (35.3632, 149.1652, 100, 16),

    # Land
    (35.3632, 149.1652, 0, 21),  # LAND
]
```

**Key commands:**
- **MAV_CMD_DO_CHANGE_SPEED (178):** Change airspeed or groundspeed
- **MAV_CMD_DO_SET_HOME (179):** Update home position
- **MAV_CMD_DO_SET_ROI (201):** Point camera at location

### Exercise 4: Complex Mission Pattern - Survey Grid

Create an automated survey pattern:

```python
# survey_grid.py
def generate_survey_grid(start_lat, start_lon, altitude,
                        spacing, num_lines, line_length):
    """Generate lawn-mower survey pattern"""
    waypoints = []

    # Takeoff
    waypoints.append((start_lat, start_lon, altitude, 22))

    # Generate grid lines
    for i in range(num_lines):
        # Calculate line endpoints
        north_offset = i * spacing / 111111  # meters to degrees

        if i % 2 == 0:  # Even lines: west to east
            wp1 = (start_lat + north_offset, start_lon, altitude, 16)
            wp2 = (start_lat + north_offset,
                   start_lon + line_length / 111111, altitude, 16)
        else:  # Odd lines: east to west
            wp1 = (start_lat + north_offset,
                   start_lon + line_length / 111111, altitude, 16)
            wp2 = (start_lat + north_offset, start_lon, altitude, 16)

        waypoints.append(wp1)
        waypoints.append(wp2)

        # Camera trigger between waypoints
        if i < num_lines - 1:
            # DO_SET_CAM_TRIGG_DIST - trigger every 10m
            waypoints.append((206, 10, 0, 0, 0, 0, 0, 0))

    # Return to launch
    waypoints.append((20, 0, 0, 0, 0, 0, 0, 0))  # RTL command

    return waypoints

# Generate 5-line survey, 50m spacing, 500m lines
grid = generate_survey_grid(35.3632, 149.1652, 100, 50, 5, 500)
```

**Expected output:**
- Parallel lines with consistent spacing
- Efficient turns between lines
- Camera triggers at specified intervals

### Exercise 5: Conditional Waypoints - DO_JUMP

Create repeating patterns:

```python
# Orbit pattern with DO_JUMP
waypoints = [
    # Takeoff
    (35.3632, 149.1652, 100, 22),

    # Start of loop (waypoint 1)
    (35.3632, 149.1752, 100, 16),

    # Loiter 3 circles
    (35.3632, 149.1752, 100, 17, -1, 3, 75, 0),  # LOITER_TURNS

    # Next waypoint
    (35.3532, 149.1652, 100, 16),

    # Jump back to waypoint 1, repeat 3 times
    (177, 1, 3, 0, 0, 0, 0),  # DO_JUMP

    # After loops complete, land
    (35.3632, 149.1652, 0, 21),
]
```

**DO_JUMP parameters:**
- Param1: Waypoint number to jump to
- Param2: Number of times to repeat (-1 = infinite)

### Exercise 6: Analyze Navigation Performance

Evaluate navigation precision from logs:

```python
# analyze_navigation.py
from pymavlink import mavutil
import math

def analyze_crosstrack_error(logfile):
    """Calculate cross-track error statistics"""
    mlog = mavutil.mavlink_connection(logfile)

    errors = []

    while True:
        msg = mlog.recv_match(type='NTUN', blocking=False)
        if msg is None:
            break

        # NTUN.XTrack contains cross-track error in meters
        errors.append(abs(msg.XTrack))

    if errors:
        print(f"Cross-track error:")
        print(f"  Mean: {sum(errors)/len(errors):.2f}m")
        print(f"  Max: {max(errors):.2f}m")
        print(f"  95th percentile: {sorted(errors)[int(len(errors)*0.95)]:.2f}m")

# Usage
analyze_crosstrack_error("test_flight.BIN")
```

**Good navigation indicators:**
- Mean cross-track error < 5m
- Max cross-track error < 15m
- Smooth transitions without overshoots

### Exercise 7: Optimize for Tight Spaces

Configure for precise navigation in confined areas:

```bash
# Tight navigation parameters
param set NAVL1_PERIOD 15        # Tighter turns
param set WP_RADIUS 30           # Smaller acceptance radius
param set NAVL1_DAMPING 0.85     # Higher damping for stability
param set CRUISE_SPEED 12        # Slower speed for precision
param write
```

**Use cases:**
- Warehouse inspections
- Bridge inspections
- Flying between obstacles
- Precision landing approaches

## Common Issues

### Issue 1: Vehicle Overshoots Waypoints

**Symptoms:**
- Vehicle circles back to waypoints
- Excessive cross-track error
- Unstable navigation

**Solutions:**
```bash
# Increase L1 period for smoother turns
param set NAVL1_PERIOD 25

# Increase waypoint radius
param set WP_RADIUS 100

# Reduce cruise speed
param set CRUISE_SPEED 15
```

### Issue 2: Wavy Path Following

**Symptoms:**
- S-curves instead of straight lines
- Oscillation around desired path
- High cross-track error variance

**Solutions:**
```bash
# Increase damping
param set NAVL1_DAMPING 0.85

# Check for compass issues (log analysis)
# Check for EKF problems

# Reduce wind sensitivity
param set NAVL1_PERIOD 22
```

### Issue 3: Poor Turn Performance

**Symptoms:**
- Wide turns miss waypoints
- Inconsistent turn radius
- Difficulty completing loiters

**Solutions:**
```bash
# Tune L1 period for bank angle
param set NAVL1_PERIOD 18

# Set appropriate max bank angle
param set LIM_ROLL_CD 4500  # 45 degrees

# Check airspeed control
param set ARSPD_FBW_MIN 12
param set ARSPD_FBW_MAX 22
```

### Issue 4: Mission Doesn't Start

**Symptoms:**
- Vehicle arms but doesn't take off
- Mission counter doesn't advance
- Stuck at first waypoint

**Solutions:**
```bash
# Check mission uploaded correctly
mission list

# Verify AUTO mode enabled
mode AUTO

# Check takeoff command parameters
# Ensure altitude > 0
# Verify home position set

# Check pre-arm failures
arm check
```

### Issue 5: Altitude Instability During Navigation

**Symptoms:**
- Altitude oscillates
- Doesn't maintain target altitude
- TECS warnings in logs

**Solutions:**
```bash
# Tune TECS parameters
param set TECS_PITCH_MAX 20
param set TECS_PITCH_MIN -20
param set TECS_TIME_CONST 5.0

# Check barometer health
# Analyze TECS logs
# Verify airspeed sensor calibration
```

## Advanced Navigation Techniques

### Spline Waypoints

Smooth curved paths through waypoints:

```python
# Use MAV_CMD_NAV_SPLINE_WAYPOINT (82) instead of (16)
waypoints = [
    (35.3632, 149.1652, 100, 22),  # Takeoff
    (35.3632, 149.1752, 100, 82),  # Spline waypoint
    (35.3532, 149.1752, 100, 82),  # Spline waypoint
    (35.3532, 149.1652, 100, 82),  # Spline waypoint
    (35.3632, 149.1652, 100, 16),  # Regular waypoint
]
```

**Benefits:**
- Smoother flight
- More efficient (less speed loss in turns)
- Better for photography/videography

### Terrain Following

Enable terrain following for consistent AGL altitude [4]:

```bash
# Enable terrain following
param set TERRAIN_ENABLE 1
param set TERRAIN_FOLLOW 1

# Set terrain spacing
param set TERRAIN_SPACING 100

# In mission, use terrain frame
# MAV_FRAME_GLOBAL_TERRAIN_ALT = 10
```

### Dynamic Speed Control

Adjust speed based on mission phase:

```python
# Fast transit, slow precision
waypoints = [
    # Fast to area of interest
    (178, 1, 25, 0, 0, 0, 0),  # 25 m/s cruise
    (35.3632, 149.1752, 100, 16),

    # Slow down for survey
    (178, 1, 12, 0, 0, 0, 0),  # 12 m/s survey
    # ... survey waypoints ...

    # Speed up for return
    (178, 1, 25, 0, 0, 0, 0),  # 25 m/s return
]
```

## Additional Resources

- [Navigation Code Overview](https://ardupilot.org/dev/docs/navigation-code-overview.html) [1] - Developer guide to navigation
- [Automatic Landing](https://ardupilot.org/plane/docs/automatic-landing.html) [2] - Advanced landing techniques
- [Terrain Following](https://ardupilot.org/plane/docs/common-terrain-following.html) [4] - Terrain following setup
- [Mission Command List](https://ardupilot.org/plane/docs/common-mavlink-mission-command-messages-mav_cmd.html) [5] - Complete MAVLink command reference

### Navigation Tuning Guides

- [L1 Controller Tuning](https://ardupilot.org/plane/docs/navigation-tuning.html) [3] - Parameter optimization
- [Mission Planning Best Practices](https://ardupilot.org/planner/docs/common-planning-a-mission-with-waypoints-and-events.html) - Mission design guide

## Next Steps

After mastering navigation:

1. **Payload Integration** - Trigger cameras and sensors during missions
2. **Terrain Following** - Maintain consistent altitude over varying terrain
3. **Precision Landing** - Advanced landing techniques for accuracy
4. **Multi-Vehicle Coordination** - Coordinate multiple vehicles in missions

---

**Sources:**

[1] https://ardupilot.org/dev/docs/navigation-code-overview.html
[2] https://ardupilot.org/plane/docs/automatic-landing.html
[3] https://ardupilot.org/plane/docs/navigation-tuning.html
[4] https://ardupilot.org/plane/docs/common-terrain-following.html
[5] https://ardupilot.org/plane/docs/common-mavlink-mission-command-messages-mav_cmd.html
