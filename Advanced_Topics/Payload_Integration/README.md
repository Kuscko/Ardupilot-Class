# Payload Integration

## Overview

Master payload integration in ArduPilot to control cameras, servos, gimbals, and other mission-critical equipment. Payload control enables autonomous photography, sensor deployment, package delivery, and specialized mission operations [1].

This module covers camera triggering, servo control, gimbal integration, relay outputs, and creating automated payload control sequences for complex missions.

## Prerequisites

Before starting this module, you should have:

- Completed basic mission planning
- Understanding of MAVLink mission commands
- Familiarity with ArduPilot parameters
- SITL environment for testing (or hardware with connected payloads)
- Knowledge of PWM signals and servo control

## What You'll Learn

By completing this module, you will:

- Configure camera triggering (DO_DIGICAM_CONTROL)
- Set up interval-based and distance-based camera triggers
- Control servos and relays for payload deployment
- Integrate and configure gimbals for camera stabilization
- Create automated payload sequences in missions
- Use Lua scripts for advanced payload control
- Troubleshoot common payload integration issues

## Key Concepts

### Camera Triggering

ArduPilot supports multiple camera trigger methods [1]:

- **DO_DIGICAM_CONTROL:** Single shot trigger command
- **DO_SET_CAM_TRIGG_DIST:** Distance-based interval triggering
- **Relay trigger:** Direct relay output control
- **Servo trigger:** PWM pulse to camera trigger pin
- **MAVLink trigger:** Camera control via MAVLink protocol

### Servo Outputs

Servos can be configured for various payload functions [2]:

- **Camera shutter:** Trigger camera via servo movement
- **Payload release:** Drop mechanisms, parachute deployment
- **Sensor positioning:** Pan/tilt mounts, antenna trackers
- **Landing gear:** Retractable landing gear control
- **Gripper:** Pick and place mechanisms

### Gimbal Integration

Gimbal stabilization for smooth aerial footage [3]:

- **2-axis gimbals:** Pitch and roll stabilization
- **3-axis gimbals:** Full pitch, roll, yaw control
- **MAVLink gimbals:** Direct MAVLink communication
- **PWM gimbals:** Traditional servo-controlled gimbals
- **DO_MOUNT_CONTROL:** Point gimbal at locations or track targets

## Hands-On Practice

### Exercise 1: Basic Camera Triggering

Configure single-shot camera trigger:

```bash
# Start SITL
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --map

# Configure relay for camera trigger
param set RELAY1_PIN 54           # GPIO pin for relay 1
param set RELAY1_DEFAULT 0        # Default off
param set CAM_DURATION 10         # Trigger pulse duration (0.1s units)

param write
reboot
```

**Create mission with camera triggers:**

```python
# camera_mission.py
from pymavlink import mavutil

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()

waypoints = [
    # Takeoff
    (35.3632, 149.1652, 100, 22),  # MAV_CMD_NAV_TAKEOFF

    # Waypoint 1
    (35.3632, 149.1752, 100, 16),

    # Trigger camera
    (0, 0, 0, 203),  # DO_DIGICAM_CONTROL (session, zoom, focus, shoot, cmd, id, mode)

    # Waypoint 2
    (35.3532, 149.1752, 100, 16),

    # Trigger camera again
    (0, 0, 0, 203),

    # Land
    (35.3632, 149.1652, 0, 21),
]

# Upload mission (similar to previous examples)
```

**Expected result:**
- Camera triggers at specified waypoints
- Relay activates for configured duration

### Exercise 2: Distance-Based Camera Triggering

Automatic camera triggering at regular intervals:

```bash
# Configure distance-based triggering
param set CAM_TRIGG_TYPE 1        # 0=servo, 1=relay
param set CAM1_TYPE 1             # Camera type

param write
```

**Mission with distance trigger:**

```python
waypoints = [
    # Takeoff
    (35.3632, 149.1652, 100, 22),

    # Start of survey line
    (35.3632, 149.1752, 100, 16),

    # Enable distance triggering - photo every 25 meters
    (0, 25, 0, 0, 0, 0, 0, 206),  # DO_SET_CAM_TRIGG_DIST

    # Survey lines - camera triggers automatically
    (35.3532, 149.1752, 100, 16),
    (35.3532, 149.1852, 100, 16),
    (35.3432, 149.1852, 100, 16),

    # Disable triggering
    (0, 0, 0, 0, 0, 0, 0, 206),   # DO_SET_CAM_TRIGG_DIST (0 = off)

    # Return and land
    (35.3632, 149.1652, 100, 16),
    (35.3632, 149.1652, 0, 21),
]
```

**Expected behavior:**
- Camera triggers every 25 meters during survey
- Stops triggering after survey complete
- Consistent photo spacing for mapping

### Exercise 3: Servo-Controlled Payload Release

Configure servo for payload drop:

```bash
# Configure servo 9 for payload release
param set SERVO9_FUNCTION 10      # RCPassThru function
param set SERVO9_MIN 1000         # PWM min (closed)
param set SERVO9_MAX 2000         # PWM max (open)
param set SERVO9_TRIM 1000        # Default position (closed)

param write
reboot
```

**Mission with payload release:**

```python
waypoints = [
    # Takeoff
    (35.3632, 149.1652, 100, 22),

    # Fly to drop location
    (35.3532, 149.1752, 100, 16),

    # Drop payload - set servo 9 to 2000 PWM
    (9, 2000, 0, 0, 0, 0, 0, 183),  # DO_SET_SERVO (servo 9, PWM 2000)

    # Wait 1 second
    (1, 0, 0, 0, 0, 0, 0, 93),  # NAV_DELAY

    # Close mechanism
    (9, 1000, 0, 0, 0, 0, 0, 183),  # DO_SET_SERVO (servo 9, PWM 1000)

    # Return home
    (35.3632, 149.1652, 100, 16),
    (35.3632, 149.1652, 0, 21),
]
```

**Expected result:**
- Servo opens at drop location
- Payload releases
- Servo closes after delay

### Exercise 4: Gimbal Configuration

Set up 3-axis gimbal control:

```bash
# Configure gimbal mount
param set MNT1_TYPE 1             # 1=Servo, 3=Alexmos, 4=SToRM32 MAVLink
param set MNT1_DEFLT_MODE 3       # 3=RC targeting, 6=GPS point

# Assign servos for gimbal axes
param set SERVO10_FUNCTION 8      # Mount1 Roll
param set SERVO11_FUNCTION 7      # Mount1 Pitch
param set SERVO12_FUNCTION 6      # Mount1 Yaw

# Configure servo ranges (depends on gimbal)
param set SERVO10_MIN 1000
param set SERVO10_MAX 2000
param set SERVO11_MIN 1000
param set SERVO11_MAX 2000
param set SERVO12_MIN 1000
param set SERVO12_MAX 2000

# Set gimbal angle limits (degrees * 100)
param set MNT1_ROLL_MIN -4500     # -45 degrees
param set MNT1_ROLL_MAX 4500      # +45 degrees
param set MNT1_PITCH_MIN -9000    # -90 degrees (down)
param set MNT1_PITCH_MAX 2500     # +25 degrees (up)
param set MNT1_YAW_MIN -9000      # -90 degrees
param set MNT1_YAW_MAX 9000       # +90 degrees

param write
reboot
```

**Expected result:**
- Gimbal stabilizes camera during flight
- Responds to RC inputs or mission commands

### Exercise 5: Gimbal Point of Interest (ROI)

Point gimbal at specific locations:

```python
waypoints = [
    # Takeoff
    (35.3632, 149.1652, 100, 22),

    # Set ROI - point camera at this location
    (35.3532, 149.1752, 50, 201),  # DO_SET_ROI (lat, lon, alt)

    # Orbit around ROI while camera tracks it
    (35.3632, 149.1752, 100, 16),
    (35.3632, 149.1852, 100, 16),
    (35.3532, 149.1852, 100, 16),
    (35.3532, 149.1752, 100, 16),

    # Cancel ROI - return to default gimbal mode
    (0, 0, 0, 197),  # DO_SET_ROI_NONE

    # Land
    (35.3632, 149.1652, 0, 21),
]
```

**Expected behavior:**
- Gimbal continuously points at ROI location
- Camera tracks target during orbit
- Smooth pan as vehicle moves around ROI

### Exercise 6: Advanced Payload Sequence

Combine multiple payload actions:

```python
# Complex payload mission
waypoints = [
    # Takeoff
    (35.3632, 149.1652, 100, 22),

    # Deploy landing gear (retract)
    (3, 2000, 0, 0, 0, 0, 0, 183),  # DO_SET_SERVO (servo 3 = gear)

    # Point gimbal down for survey
    (0, -90, 0, 0, 0, 0, 2, 205),  # DO_MOUNT_CONTROL (pitch -90 deg)

    # Start distance-based camera triggering
    (0, 30, 0, 0, 0, 0, 0, 206),  # Every 30m

    # Survey grid
    (35.3632, 149.1752, 100, 16),
    (35.3532, 149.1752, 100, 16),
    (35.3532, 149.1852, 100, 16),

    # Stop camera triggering
    (0, 0, 0, 0, 0, 0, 0, 206),

    # Point gimbal forward
    (0, 0, 0, 0, 0, 0, 2, 205),

    # Return to land
    (35.3632, 149.1652, 100, 16),

    # Deploy landing gear (extend)
    (3, 1000, 0, 0, 0, 0, 0, 183),

    # Land
    (35.3632, 149.1652, 0, 21),
]
```

**Expected sequence:**
1. Retract landing gear after takeoff
2. Point camera down
3. Trigger photos every 30m during survey
4. Return camera to forward view
5. Extend landing gear
6. Land

### Exercise 7: Lua Script Payload Control

Create custom payload control logic:

```lua
-- payload_control.lua
-- Advanced payload control script

local RELAY_PIN = 1
local SERVO_NUM = 9
local UPDATE_RATE_HZ = 10

function update()
    -- Get current altitude
    local alt = ahrs:get_position():alt() * 0.01  -- convert cm to m

    -- Get vehicle mode
    local mode = vehicle:get_mode()

    -- Auto-deploy payload based on altitude and mode
    if mode == 10 and alt < 50 then  -- Mode 10 = AUTO, below 50m
        -- Activate relay
        relay:on(RELAY_PIN)

        -- Open servo
        SRV_Channels:set_output_pwm(SERVO_NUM, 2000)

        gcs:send_text(0, "Payload deployed at " .. tostring(alt) .. "m")
    else
        -- Deactivate
        relay:off(RELAY_PIN)
        SRV_Channels:set_output_pwm(SERVO_NUM, 1000)
    end

    -- Run at UPDATE_RATE_HZ
    return update, 1000 // UPDATE_RATE_HZ
end

return update()
```

**Install and enable:**

```bash
# Copy script to scripts folder
# In ArduPilot: /APM/scripts/ on SD card

# Enable scripting
param set SCR_ENABLE 1
param set SCR_VM_I_COUNT 100000
param write
reboot
```

**Expected behavior:**
- Script monitors altitude and mode
- Automatically deploys payload when conditions met
- Provides status messages to GCS

## Common Issues

### Issue 1: Camera Not Triggering

**Symptoms:**
- No camera trigger pulse
- Relay/servo not activating
- Mission advances but no camera action

**Solutions:**

```bash
# Verify relay pin configured
param show RELAY1_PIN
param set RELAY1_PIN 54  # Set to valid GPIO pin

# Check camera trigger type
param show CAM_TRIGG_TYPE
param set CAM_TRIGG_TYPE 1  # 1=relay

# Verify relay function
# Test manually
relay set 1 1  # Turn on relay 1
relay set 1 0  # Turn off relay 1

# Check mission command parameters
# DO_DIGICAM_CONTROL: cmd=203, param5=1 (shoot)
```

### Issue 2: Servo Not Moving

**Symptoms:**
- Servo connected but doesn't respond
- No movement when commanded
- Wrong range of motion

**Solutions:**

```bash
# Check servo function assigned
param show SERVO9_FUNCTION
param set SERVO9_FUNCTION 10  # RCPassThru or custom function

# Verify min/max range
param set SERVO9_MIN 1000
param set SERVO9_MAX 2000

# Test servo output manually
servo set 9 1500  # Mid position
servo set 9 1000  # Min
servo set 9 2000  # Max

# Check servo power supply
# Ensure servo rail has power
# Verify servo connection to correct output

# Enable servo output
param set BRD_PWM_COUNT 8  # Enable 8 servo outputs
```

### Issue 3: Gimbal Erratic or Not Stabilizing

**Symptoms:**
- Gimbal jitters or oscillates
- Doesn't stabilize properly
- Wrong pointing direction

**Solutions:**

```bash
# Check mount type
param show MNT1_TYPE
param set MNT1_TYPE 1  # Servo gimbal

# Verify servo assignments
param show SERVO10_FUNCTION  # Should be 8 (Mount1Roll)
param show SERVO11_FUNCTION  # Should be 7 (Mount1Pitch)
param show SERVO12_FUNCTION  # Should be 6 (Mount1Yaw)

# Adjust stabilization gains (if supported)
param set MNT1_STAB_ROLL 1   # Enable roll stabilization
param set MNT1_STAB_TILT 1   # Enable pitch stabilization
param set MNT1_STAB_PAN 0    # Disable yaw stabilization

# Check gimbal angle limits
# Ensure limits match physical gimbal range

# For MAVLink gimbals, verify protocol
param set MNT1_TYPE 4  # MAVLink gimbal
```

### Issue 4: Distance Trigger Not Working

**Symptoms:**
- Camera not triggering at intervals
- Inconsistent trigger spacing
- No triggers during mission

**Solutions:**

```bash
# Verify GPS lock (required for distance calculation)
# Check GPS satellite count > 6

# Configure camera trigger
param set CAM_TRIGG_TYPE 1
param set CAM1_TYPE 1

# Check mission command
# DO_SET_CAM_TRIGG_DIST: param1=distance(m), others=0

# Enable logging
param set CAM_LOG 1  # Log camera triggers

# Verify speed > 0
# Distance trigger requires vehicle movement

# Check trigger feedback in logs
# TRIG messages show each trigger event
```

### Issue 5: Payload Release Timing Issues

**Symptoms:**
- Payload drops at wrong location
- Early or late release
- Inconsistent release

**Solutions:**

```bash
# Add delay before release
# Use NAV_DELAY command

# Account for vehicle speed
# Calculate lead time for moving targets

# Use loiter before release
# MAV_CMD_NAV_LOITER_UNLIM until ready

# Adjust servo timing
param set SERVO9_TRIM 1500  # Adjust neutral

# Test release mechanism
# Verify mechanical operation
# Check for binding or resistance

# Consider wind drift
# Position upwind of target
```

## Payload Integration Examples

### Survey Photography

```python
# Automated survey with optimal camera overlap
spacing = 30  # meters between photos
altitude = 100  # meters
camera_fov = 60  # degrees field of view

# Calculate required spacing for 70% overlap
import math
ground_coverage = 2 * altitude * math.tan(math.radians(camera_fov/2))
trigger_distance = ground_coverage * 0.3  # 70% overlap

waypoints = [
    (35.3632, 149.1652, altitude, 22),  # Takeoff
    (35.3632, 149.1752, altitude, 16),  # Start
    (0, trigger_distance, 0, 0, 0, 0, 0, 206),  # Start triggers
    # ... survey lines ...
    (0, 0, 0, 0, 0, 0, 0, 206),  # Stop triggers
]
```

### Package Delivery

```python
# Precision payload drop with verification
waypoints = [
    (35.3632, 149.1652, 100, 22),  # Takeoff
    (35.3532, 149.1752, 100, 16),  # Navigate to target
    (35.3532, 149.1752, 30, 16),   # Descend to drop altitude
    (0, 5, 0, 0, 0, 0, 0, 93),     # Wait 5 seconds to stabilize
    (9, 2000, 0, 0, 0, 0, 0, 183), # Release payload
    (0, 2, 0, 0, 0, 0, 0, 93),     # Wait 2 seconds
    (9, 1000, 0, 0, 0, 0, 0, 183), # Close mechanism
    (35.3532, 149.1752, 100, 16),  # Climb
    (0, 0, 0, 0, 0, 0, 0, 20),     # Return to launch
]
```

## Additional Resources

- [Camera and Gimbal Setup](https://ardupilot.org/copter/docs/common-cameras-and-gimbals.html) [1] - Official camera/gimbal guide
- [Servo Output Functions](https://ardupilot.org/plane/docs/common-rcoutput-mapping.html) [2] - Servo configuration reference
- [Mount Configuration](https://ardupilot.org/copter/docs/common-mount-targeting.html) [3] - Gimbal targeting and control
- [MAVLink Commands](https://mavlink.io/en/messages/common.html) - Complete command reference

### Payload Examples

- [Survey Grid Calculator](https://ardupilot.org/planner/docs/common-camera-control-and-auto-missions-in-mission-planner.html) - Mission Planner survey tool
- [Gripper Control](https://ardupilot.org/copter/docs/common-gripper-landingpage.html) - Servo gripper setup

## Next Steps

After mastering payload integration:

1. **Advanced Mission Planning** - Complex multi-payload missions
2. **Lua Scripting** - Custom payload automation logic
3. **Computer Vision** - Integrate companion computer for intelligent targeting
4. **Multi-Vehicle Coordination** - Synchronized payload operations

---

**Sources:**

[1] https://ardupilot.org/copter/docs/common-cameras-and-gimbals.html
[2] https://ardupilot.org/plane/docs/common-rcoutput-mapping.html
[3] https://ardupilot.org/copter/docs/common-mount-targeting.html
