# Safety and Geofencing

ArduPilot safety systems provide automated protection against common failure modes and keep operations within designated boundaries.

## Geofence Types

- **Circular:** Radius-based boundary centered on home (`FENCE_RADIUS`)
- **Polygon:** Complex multi-point boundary, up to 84 vertices
- **Altitude:** Max/min altitude limits for regulatory compliance

## Geofence Actions

When breached: Report Only, RTL, Land, SmartRTL, or Brake (copter).

## Exercises

### Exercise 1: Configure Circular Geofence

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --map

param set FENCE_ENABLE 1
param set FENCE_TYPE 1          # Circular only
param set FENCE_RADIUS 300
param set FENCE_ALT_MAX 120
param set FENCE_ALT_MIN 10
param set FENCE_ACTION 1        # RTL
param set FENCE_MARGIN 10
param write
reboot
```

### Exercise 2: Create Polygon Geofence

**Using Mission Planner:** FLIGHT PLAN → right-click → Draw Polygon → Add Polygon Point → Upload.

```python
# polygon_fence.py
from pymavlink import mavutil
import time

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()

fence_points = [
    (35.3632, 149.1652),
    (35.3632, 149.1752),
    (35.3532, 149.1752),
    (35.3532, 149.1652),
    (35.3632, 149.1652),  # Close polygon
]

master.mav.fence_fetch_point_send(
    master.target_system, master.target_component, 0)

for idx, (lat, lon) in enumerate(fence_points):
    master.mav.fence_point_send(
        master.target_system, master.target_component,
        idx, len(fence_points), lat, lon)
    time.sleep(0.1)

print(f"Uploaded {len(fence_points)} fence points")
```

```bash
param set FENCE_ENABLE 1
param set FENCE_TYPE 3          # Circle + polygon
param set FENCE_ACTION 1
param write
```

### Exercise 3: Set Up Rally Points

**Using Mission Planner:** FLIGHT PLAN → right-click → Rally Points → Set Rally Point.

```python
# rally_points.py
from pymavlink import mavutil

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()

rally_points = [
    (35.3632, 149.1652, 50),
    (35.3532, 149.1752, 50),
    (35.3432, 149.1652, 50),
]

for idx, (lat, lon, alt) in enumerate(rally_points):
    master.mav.rally_point_send(
        master.target_system, master.target_component,
        idx, len(rally_points),
        int(lat * 1e7), int(lon * 1e7), int(alt * 100),
        0, 0, 0)
```

```bash
param set RALLY_TOTAL 3
param set RALLY_LIMIT_KM 2
param set RALLY_INCL_HOME 1
param write
```

### Exercise 4: Enable Terrain Following

```bash
param set TERRAIN_ENABLE 1
param set TERRAIN_FOLLOW 1
param set TERRAIN_SPACING 100
param write
reboot
```

```python
# Terrain-relative waypoints (frame 10 = GLOBAL_TERRAIN_ALT)
waypoints = [
    (35.3632, 149.1652, 100, 22),         # Absolute takeoff
    (35.3632, 149.1752, 50, 16, 10),      # 50m AGL
    (35.3532, 149.1752, 50, 16, 10),
    (35.3532, 149.1652, 50, 16, 10),
    (35.3632, 149.1652, 0, 21),
]
```

### Exercise 5: Configure Parachute System

```bash
param set CHUTE_ENABLED 1
param set CHUTE_TYPE 0          # 0=relay, 1=servo
param set SERVO9_FUNCTION 27    # Parachute servo
param set CHUTE_CRT_SINK 10     # Deploy at >10m/s sink rate
param set CHUTE_ALT_MIN 10
param set CHUTE_DELAY_MS 500
param set RC7_OPTION 24         # Manual release on CH7
param write
reboot

# Ground test only:
servo set 9 2000  # Deploy
servo set 9 1000  # Reset
```

### Exercise 6: Configure Pre-Arm Safety Checks

```bash
param set ARMING_CHECK 1        # All checks enabled

# Check bit values: 1=all, 2=baro, 4=compass, 8=GPS, 16=INS,
# 32=params, 64=RC, 128=voltage, 256=battery, 512=airspeed

# Example: Skip compass for indoor testing
param set ARMING_CHECK 65531

param set BATT_ARM_VOLT 14.5    # Min voltage to arm (4S)
param write
```

Common pre-arm failures: GPS not healthy, compass not calibrated, RC not calibrated, accelerometers not calibrated.

### Exercise 7: Test Safety Systems

```bash
# Geofence test
mode GUIDED
arm throttle
# Command position outside fence
# Expected: RTL triggers at boundary

# Altitude fence test
param set FENCE_ALT_MAX 50
mode GUIDED
arm throttle
# Command altitude > 50m
# Expected: Vehicle stops at 50m
```

## Common Issues

### Geofence False Triggers

```bash
param set FENCE_MARGIN 20
# Wait for GPS HDop < 2.0 before arming
# For indoor testing:
param set FENCE_ENABLE 0
```

### Rally Points Not Working

```bash
rally list
param show RALLY_TOTAL
param set RALLY_LIMIT_KM 5
```

### Terrain Following Not Working

```bash
param show TERRAIN_ENABLE
param set TERRAIN_ENABLE 1
param set TERRAIN_SPACING 50
# Verify waypoints use frame 10 (GLOBAL_TERRAIN_ALT)
```

### Parachute False Deploys

```bash
param set CHUTE_CRT_SINK 15
param set CHUTE_ALT_MIN 20
param set CHUTE_ENABLED 0  # Disable if causing problems
```

### Pre-Arm Checks Blocking Flight

```bash
# GPS: Wait 60+ seconds for lock
# Compass: Calibrate away from metal
# Battery: Charge battery
# RC: Re-calibrate channels
param set ARMING_CHECK 1  # Reset to all checks after fixing
```

## Layered Safety Configuration

```bash
# Layer 1: Geofence
param set FENCE_ENABLE 1
param set FENCE_TYPE 3
param set FENCE_ACTION 1

# Layer 2: Rally points
param set RALLY_TOTAL 3
param set RALLY_INCL_HOME 1

# Layer 3: Failsafes
param set FS_THR_ENABLE 1
param set FS_GCS_ENABLE 1

# Layer 4: Emergency systems
param set CHUTE_ENABLED 1
param set RC9_OPTION 31         # Emergency stop

# Layer 5: Pre-arm checks
param set ARMING_CHECK 1
```

## SmartRTL

```bash
param set SRTL_ENABLE 1
param set SRTL_POINTS 200
param set SRTL_ACCURACY 2
param set FENCE_ACTION 5        # SmartRTL on breach
param set FS_THR_ACTION 3       # SmartRTL on RC loss
```

## Regulatory Compliance Examples

```bash
# FAA Part 107 (USA)
param set FENCE_ALT_MAX 120     # 400ft = ~122m
param set FENCE_RADIUS 2000     # Visual line of sight

# EASA (Europe)
param set FENCE_ALT_MAX 120
param set FENCE_ENABLE 1
```

---

- [Safety Systems Guide](SAFETY_SYSTEMS_GUIDE.md)
- [Pre-Flight Safety Checklist](SAFETY_CHECKLIST.md)
- [Geofencing Overview](https://ardupilot.org/copter/docs/common-geofencing-landing-page.html)
- [Rally Points](https://ardupilot.org/copter/docs/common-rally-points.html)
- [Terrain Following](https://ardupilot.org/plane/docs/common-terrain-following.html)
- [Parachute Setup](https://ardupilot.org/copter/docs/common-parachute.html)
