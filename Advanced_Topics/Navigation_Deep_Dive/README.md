# Navigation Deep Dive

## Key Concepts

### Navigation Parameters

| Parameter        | Default | Purpose                           |
| ---------------- | ------- | --------------------------------- |
| NAVL1_PERIOD     | 20      | L1 controller period (seconds)    |
| NAVL1_DAMPING    | 0.75    | L1 damping ratio                  |
| WP_RADIUS        | 90      | Waypoint acceptance radius (m)    |
| WP_LOITER_RAD    | 75      | Loiter radius (m)                 |
| NAVL1_XTRACK_I   | 0.02    | Cross-track error integrator gain |

### Path Planning

- **Waypoint navigation:** Point-to-point straight lines
- **Spline waypoints:** Smooth curves through waypoints
- **Loiter turns:** Circular holding patterns
- **Survey grids:** Automated coverage patterns

## Exercises

### Exercise 1: Configure L1 Controller

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --map

param set NAVL1_PERIOD 20
param set NAVL1_DAMPING 0.75
param set NAVL1_XTRACK_I 0.02
param write
reboot
```

**Parameter effects:**

- **NAVL1_PERIOD** smaller = tighter turns, more aggressive
- **NAVL1_PERIOD** larger = wider turns, smoother
- **NAVL1_DAMPING** lower = faster response, may oscillate
- **NAVL1_DAMPING** higher = smoother, less overshoot

### Exercise 2: Test Basic Waypoint Navigation

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

### Exercise 3: Speed and Altitude Transitions

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

### Exercise 5: Conditional Waypoints - DO_JUMP

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

Good navigation indicators: mean cross-track error < 5m, max < 15m, smooth transitions.

### Exercise 7: Optimize for Tight Spaces

```bash
param set NAVL1_PERIOD 15
param set WP_RADIUS 30
param set NAVL1_DAMPING 0.85
param set CRUISE_SPEED 12
param write
```

## Common Issues

### Vehicle Overshoots Waypoints

```bash
param set NAVL1_PERIOD 25
param set WP_RADIUS 100
param set CRUISE_SPEED 15
```

### Wavy Path Following

```bash
param set NAVL1_DAMPING 0.85
param set NAVL1_PERIOD 22
```

### Poor Turn Performance

```bash
param set NAVL1_PERIOD 18
param set LIM_ROLL_CD 4500  # 45 degrees
param set ARSPD_FBW_MIN 12
param set ARSPD_FBW_MAX 22
```

### Mission Doesn't Start

```bash
mission list
mode AUTO
arm check
```

### Altitude Instability During Navigation

```bash
param set TECS_PITCH_MAX 20
param set TECS_PITCH_MIN -20
param set TECS_TIME_CONST 5.0
```

## Advanced Navigation Techniques

### Spline Waypoints

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

### Terrain Following

```bash
param set TERRAIN_ENABLE 1
param set TERRAIN_FOLLOW 1
param set TERRAIN_SPACING 100
# In mission, use terrain frame: MAV_FRAME_GLOBAL_TERRAIN_ALT = 10
```

### Dynamic Speed Control

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

---

- [L1 Controller Guide](L1_CONTROLLER_GUIDE.md)
- [ArduPilot Navigation](https://ardupilot.org/dev/docs/navigation-code-overview.html)
- [L1 Controller Tuning](https://ardupilot.org/plane/docs/navigation-tuning.html)
- [Mission Command List](https://ardupilot.org/plane/docs/common-mavlink-mission-command-messages-mav_cmd.html)
- [Terrain Following](https://ardupilot.org/plane/docs/common-terrain-following.html)
