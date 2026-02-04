# Safety and Geofencing

## Overview

Master advanced safety systems and geofencing in ArduPilot to protect your vehicle, comply with regulations, and prevent flyaways. Safety systems provide automated protection against common failure modes and ensure operations remain within designated boundaries [1].

This module covers geofence configuration, rally points, terrain following, parachute systems, and comprehensive pre-arm safety checks.

## Prerequisites

Before starting this module, you should have:

- Completed basic mission planning and flight operations
- Understanding of ArduPilot parameters and failsafes
- GPS-equipped flight controller
- Mission Planner or QGroundControl installed
- Safe testing environment for failsafe validation

## What You'll Learn

By completing this module, you will:

- Configure circular, polygon, and altitude geofences
- Set up geofence breach actions and recovery behaviors
- Create and manage rally points for safe return locations
- Enable and test terrain following capabilities
- Integrate parachute and emergency systems
- Configure comprehensive pre-arm safety checks
- Test and validate safety system responses

## Key Concepts

### Geofence Types

ArduPilot supports multiple geofence types [1]:

**Circular Geofence:**
- Simple radius-based boundary
- Centered on home location
- Easy to configure
- Single parameter (FENCE_RADIUS)

**Polygon Geofence:**
- Complex multi-point boundary
- Define specific flight area
- Up to 84 vertices
- Follows terrain contours

**Altitude Geofence:**
- Maximum altitude limit
- Minimum altitude floor
- Prevents ceiling violations
- Regulatory compliance

### Geofence Actions

When geofence breached [2]:

- **Report Only:** Log violation, continue flight
- **RTL (Return to Launch):** Navigate to home
- **Land:** Descend and land immediately
- **SmartRTL:** Return via safe recorded path
- **Brake:** Stop in place (copter only)

### Rally Points

Safe landing alternatives to home [3]:

- Multiple safe landing locations
- Closer than home in emergencies
- Predefined safe zones
- Terrain-aware positioning

## Hands-On Practice

### Exercise 1: Configure Circular Geofence

Set up basic radius-based geofence:

```bash
# Start SITL or connect to flight controller
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --map

# Enable geofence
param set FENCE_ENABLE 1        # Enable fence
param set FENCE_TYPE 1          # 1=circular only

# Set circular fence radius
param set FENCE_RADIUS 300      # 300 meters from home

# Set altitude limits
param set FENCE_ALT_MAX 120     # 120m maximum altitude
param set FENCE_ALT_MIN 10      # 10m minimum altitude (copter)

# Configure breach action
param set FENCE_ACTION 1        # 0=Report, 1=RTL, 2=Land, 4=Brake

# Set fence margin for warnings
param set FENCE_MARGIN 10       # Warning 10m before breach

param write
reboot
```

**Expected behavior:**
- Vehicle prevented from flying beyond 300m radius
- Altitude constrained between 10m and 120m
- RTL triggers automatically on breach
- Warning before actual breach

### Exercise 2: Create Polygon Geofence

Define complex flight boundary:

**Using Mission Planner:**

1. Go to FLIGHT PLAN tab
2. Right-click → Draw Polygon → Add Polygon Point
3. Click map to define boundary vertices
4. Right-click → Polygon → Fence
5. Upload fence to flight controller

**Manual parameter configuration:**

```python
# polygon_fence.py - Create fence programmatically
from pymavlink import mavutil
import time

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()

# Define polygon vertices (lat, lon)
fence_points = [
    (35.3632, 149.1652),  # Point 1
    (35.3632, 149.1752),  # Point 2
    (35.3532, 149.1752),  # Point 3
    (35.3532, 149.1652),  # Point 4
    (35.3632, 149.1652),  # Close polygon
]

# Upload fence
master.mav.fence_fetch_point_send(
    master.target_system,
    master.target_component,
    0)  # Start upload

for idx, (lat, lon) in enumerate(fence_points):
    master.mav.fence_point_send(
        master.target_system,
        master.target_component,
        idx,
        len(fence_points),
        lat, lon)
    time.sleep(0.1)

print(f"Uploaded {len(fence_points)} fence points")
```

**Configure polygon fence:**

```bash
# Enable polygon fence
param set FENCE_ENABLE 1
param set FENCE_TYPE 3          # 1=circle, 2=polygon, 3=both
param set FENCE_ACTION 1        # RTL on breach

param write
```

### Exercise 3: Set Up Rally Points

Create safe return locations:

**Using Mission Planner:**

1. Go to FLIGHT PLAN tab
2. Right-click map → Rally Points → Set Rally Point
3. Click locations to add rally points
4. Upload to flight controller

**Manual rally point configuration:**

```python
# rally_points.py
from pymavlink import mavutil

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()

# Define rally points (lat, lon, alt)
rally_points = [
    (35.3632, 149.1652, 50),   # Rally point 1
    (35.3532, 149.1752, 50),   # Rally point 2
    (35.3432, 149.1652, 50),   # Rally point 3
]

# Upload rally points
for idx, (lat, lon, alt) in enumerate(rally_points):
    master.mav.rally_point_send(
        master.target_system,
        master.target_component,
        idx,
        len(rally_points),
        int(lat * 1e7),  # Convert to int32
        int(lon * 1e7),
        int(alt * 100),  # Altitude in cm
        0, 0, 0)  # Break, land_dir, flags

print(f"Uploaded {len(rally_points)} rally points")
```

**Configure rally point behavior:**

```bash
# Enable rally points
param set RALLY_TOTAL 3         # Number of rally points
param set RALLY_LIMIT_KM 2      # Max 2km from home
param set RALLY_INCL_HOME 1     # Include home as rally point

# Use rally points for RTL
param set RTL_ALT 50            # RTL altitude
param set RALLY_NAVL1_PERIOD 20 # Navigation to rally

param write
```

**Expected behavior:**
- RTL navigates to nearest rally point
- Safer than single home location
- Accounts for wind drift to landing

### Exercise 4: Enable Terrain Following

Maintain consistent altitude above ground:

```bash
# Enable terrain data
param set TERRAIN_ENABLE 1      # Enable terrain system
param set TERRAIN_FOLLOW 1      # Enable terrain following

# Configure terrain spacing
param set TERRAIN_SPACING 100   # Grid spacing (meters)

# Set terrain data source
param set TERRAIN_SOURCE 1      # 0=Mission Planner, 1=GCS

# Terrain following options
param set TERRAIN_OFS_MAX 100   # Max offset from terrain (m)

param write
reboot
```

**Create terrain-following mission:**

```python
# Use terrain-relative waypoints
# MAV_FRAME_GLOBAL_TERRAIN_ALT = 10

waypoints = [
    # Takeoff
    (35.3632, 149.1652, 100, 22),  # Absolute altitude

    # Switch to terrain frame
    # Waypoint at 50m AGL (Above Ground Level)
    (35.3632, 149.1752, 50, 16, 10),  # Frame 10 = terrain

    # Follows terrain contours at 50m AGL
    (35.3532, 149.1752, 50, 16, 10),
    (35.3532, 149.1652, 50, 16, 10),

    # Land
    (35.3632, 149.1652, 0, 21),
]
```

**Expected behavior:**
- Vehicle maintains consistent height above terrain
- Climbs over hills, descends into valleys
- Safer in varying terrain

### Exercise 5: Configure Parachute System

Set up emergency parachute deployment:

```bash
# Enable parachute
param set CHUTE_ENABLED 1       # Enable parachute
param set CHUTE_TYPE 0          # 0=relay, 1=servo

# Configure trigger
param set SERVO9_FUNCTION 27    # Servo 9 = parachute
param set CHUTE_CRT_SINK 10     # Deploy at >10m/s sink rate

# Parachute deployment conditions
param set CHUTE_ALT_MIN 10      # Min altitude to deploy (m)
param set CHUTE_DELAY_MS 500    # Delay after trigger (ms)

# Manual release on RC channel
param set RC7_OPTION 24         # Channel 7 = parachute release

param write
reboot
```

**Test parachute (ground test only!):**

```bash
# Manual trigger test
servo set 9 2000  # Deploy
# Verify mechanism activates
servo set 9 1000  # Reset
```

**Expected behavior:**
- Auto-deploys on critical sink rate
- Manual override via RC channel
- Minimum altitude prevents ground deployment

### Exercise 6: Configure Pre-Arm Safety Checks

Comprehensive safety checks before arming:

```bash
# Enable pre-arm checks
param set ARMING_CHECK 1        # Enable all checks

# Individual check bits (bitmask):
# 1 = All checks
# 2 = Barometer
# 4 = Compass
# 8 = GPS
# 16 = INS (inertial nav)
# 32 = Parameters
# 64 = RC channels
# 128 = Board voltage
# 256 = Battery
# 512 = Airspeed
# 1024 = Logging
# 2048 = Switch (mode switch position)

# Example: Skip compass check (sometimes needed indoors)
param set ARMING_CHECK 65531    # All except compass (1 - 4)

# Require GPS for arming
param set GPS_NAVL1_PERIOD 20
param set ARMING_REQUIRE 1      # Require GPS

# Battery checks
param set BATT_ARM_VOLT 14.5    # Min voltage to arm (4S)
param set BATT_ARM_MAH 0        # Min capacity to arm

# Accelerometer calibration required
param set INS_ENABLE_MASK 127   # Enable all IMUs

param write
```

**Pre-arm check meanings:**

```
Common pre-arm failures:
- "PreArm: GPS not healthy" - Wait for GPS lock
- "PreArm: Compass not calibrated" - Calibrate compass
- "PreArm: Barometer not healthy" - Check barometer
- "PreArm: Accelerometers not calibrated" - Calibrate accels
- "PreArm: RC not calibrated" - Calibrate RC
- "PreArm: Check Compass" - Compass variance too high
```

### Exercise 7: Test Safety Systems

Validate safety system responses:

**Geofence Test:**

```bash
# Arm and takeoff in SITL
mode GUIDED
arm throttle

# Command position outside fence
# Watch for geofence breach and RTL trigger

# Expected: Vehicle stops at fence boundary, initiates RTL
```

**Rally Point Test:**

```bash
# Arm and fly away from home
mode LOITER
# Navigate to different location

# Trigger RTL
mode RTL

# Expected: Vehicle flies to nearest rally point, not home
```

**Altitude Fence Test:**

```bash
# Set low altitude fence
param set FENCE_ALT_MAX 50

# Arm and climb
mode GUIDED
arm throttle
# Command altitude > 50m

# Expected: Vehicle stops at 50m, may trigger fence action
```

**Terrain Following Test:**

```bash
# Create terrain mission
# Fly over varying terrain
# Monitor altitude AGL

# Expected: Constant height above ground
```

## Common Issues

### Issue 1: Geofence False Triggers

**Symptoms:**
- Geofence triggers immediately after arm
- Random fence violations
- Fence triggers indoors

**Solutions:**

```bash
# Increase fence margin
param set FENCE_MARGIN 20       # Larger margin

# Check GPS accuracy
# Verify HDOP < 2.0
# Wait for GPS lock before arming

# Disable fence for indoor testing
param set FENCE_ENABLE 0

# Check home position set correctly
# Home should be set after GPS lock
```

### Issue 2: Rally Points Not Working

**Symptoms:**
- RTL goes to home, not rally point
- Rally points not uploaded
- Rally point errors

**Solutions:**

```bash
# Verify rally points uploaded
rally list

# Check rally point parameters
param show RALLY_TOTAL
param show RALLY_INCL_HOME

# Ensure rally points within range
param set RALLY_LIMIT_KM 5      # Increase limit

# Check RTL mode uses rally
param show RTL_ALT
# Rally points used automatically in RTL
```

### Issue 3: Terrain Following Not Working

**Symptoms:**
- No terrain data available
- Vehicle ignores terrain
- Altitude not adjusted

**Solutions:**

```bash
# Check terrain enabled
param show TERRAIN_ENABLE
param set TERRAIN_ENABLE 1

# Verify terrain data loaded
# Mission Planner: Check terrain elevation display

# Use correct waypoint frame
# Frame 10 = GLOBAL_TERRAIN_ALT

# Check terrain spacing
param set TERRAIN_SPACING 50    # Denser terrain grid

# Verify GCS sending terrain data
# Mission Planner automatically sends terrain
```

### Issue 4: Parachute Deploys Incorrectly

**Symptoms:**
- Parachute deploys during normal flight
- Won't deploy when needed
- False triggers

**Solutions:**

```bash
# Adjust sink rate threshold
param show CHUTE_CRT_SINK
param set CHUTE_CRT_SINK 15     # Higher threshold

# Check altitude minimum
param set CHUTE_ALT_MIN 20      # Only deploy above 20m

# Verify servo/relay works
servo set 9 2000  # Test deployment

# Disable if causing problems
param set CHUTE_ENABLED 0

# Check for sensor errors
# Bad barometer can cause false sink rate
```

### Issue 5: Pre-Arm Checks Blocking Flight

**Symptoms:**
- Cannot arm vehicle
- Pre-arm check failures
- All systems appear good

**Solutions:**

```bash
# Check specific pre-arm error message
# Displayed in GCS

# Temporarily disable problematic checks
# Example: Skip compass for indoor testing
param set ARMING_CHECK 65531    # All except compass

# Common fixes:
# GPS: Wait longer for lock (60s+)
# Compass: Calibrate away from metal
# Barometer: Check for damage
# RC: Re-calibrate RC channels
# Battery: Charge battery

# Reset arming checks to default
param set ARMING_CHECK 1        # All checks enabled
```

## Safety System Best Practices

### Layered Safety Approach

```bash
# Layer 1: Geofence (prevent going too far)
param set FENCE_ENABLE 1
param set FENCE_TYPE 3          # Circle + polygon
param set FENCE_ACTION 1        # RTL

# Layer 2: Rally points (safe return locations)
param set RALLY_TOTAL 3
param set RALLY_INCL_HOME 1

# Layer 3: Failsafes (handle signal loss)
param set FS_THR_ENABLE 1       # RC failsafe
param set FS_GCS_ENABLE 1       # Telemetry failsafe

# Layer 4: Emergency systems (last resort)
param set CHUTE_ENABLED 1       # Parachute
param set RC9_OPTION 31         # Emergency stop

# Layer 5: Pre-arm checks (prevent bad takeoff)
param set ARMING_CHECK 1        # All checks
```

### Testing Safety Systems

```bash
# 1. Test on bench first
#    - Verify parameters
#    - Check servo/relay outputs
#    - Test RC switches

# 2. Test in SITL
#    - Simulate fence breaches
#    - Test rally point navigation
#    - Validate failsafe behavior

# 3. Ground test with hardware
#    - Arm and immediately trigger safety
#    - Verify correct responses
#    - Check motor shutoff works

# 4. Low altitude flight test
#    - Test fence boundaries (carefully!)
#    - Verify RTL to rally points
#    - Validate terrain following

# 5. Full mission validation
#    - Fly complete mission
#    - Monitor safety systems
#    - Log all events
```

### Regulatory Compliance

```bash
# FAA Part 107 (USA) example
param set FENCE_ALT_MAX 120     # 400ft = ~122m
param set FENCE_RADIUS 2000     # Visual line of sight

# EASA (Europe) example
param set FENCE_ALT_MAX 120     # A1/A2/A3 categories
param set FENCE_ENABLE 1        # Required for most operations

# Set registration ID
# Mission Planner → CONFIG → Planner
# Set registration number in vehicle info
```

## Advanced Safety Features

### SmartRTL

Enhanced RTL with path memory:

```bash
# Enable SmartRTL
param set SRTL_ENABLE 1         # Enable SmartRTL
param set SRTL_POINTS 200       # Path points to store
param set SRTL_ACCURACY 2       # Position accuracy (m)

# Use SmartRTL as failsafe action
param set FENCE_ACTION 5        # SmartRTL on breach
param set FS_THR_ACTION 3       # SmartRTL on RC loss

param write
```

**SmartRTL benefits:**
- Returns via safe recorded path
- Avoids obstacles on return
- More efficient than straight-line RTL

### Advanced Geofence Options

```bash
# Auto-enable on arming
param set FENCE_AUTOENABLE 1    # Enable when armed

# Manual enable via RC
param set RC6_OPTION 11         # Fence enable switch

# Floor and ceiling fence
param set FENCE_TYPE 5          # Alt + polygon
param set FENCE_ALT_MIN 20      # No flight below 20m
param set FENCE_ALT_MAX 150     # No flight above 150m

# Action on return to fence
param set FENCE_RESTORE 1       # Resume mission after breach
```

## Additional Resources

- [Geofencing Overview](https://ardupilot.org/copter/docs/common-geofencing-landing-page.html) [1] - Complete geofence guide
- [Rally Points](https://ardupilot.org/copter/docs/common-rally-points.html) [3] - Rally point setup
- [Terrain Following](https://ardupilot.org/plane/docs/common-terrain-following.html) [2] - Terrain system details
- [Safety Features](https://ardupilot.org/copter/docs/safety-features.html) - Comprehensive safety guide

### Emergency Systems

- [Parachute Setup](https://ardupilot.org/copter/docs/common-parachute.html) - Parachute configuration
- [Motor Emergency Stop](https://ardupilot.org/copter/docs/common-escs-and-motors.html) - Emergency cutoff

## Next Steps

After mastering safety and geofencing:

1. **Advanced Failsafe Logic** - Custom failsafe behaviors with Lua
2. **Multi-Vehicle Safety** - Coordinated safety systems
3. **Redundant Systems** - Backup GPS, power, communications
4. **Regulatory Compliance** - Region-specific requirements

---

**Sources:**

[1] https://ardupilot.org/copter/docs/common-geofencing-landing-page.html
[2] https://ardupilot.org/plane/docs/common-terrain-following.html
[3] https://ardupilot.org/copter/docs/common-rally-points.html
