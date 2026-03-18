# Payload Integration

ArduPilot supports camera triggering, servo control, gimbal integration, relay outputs, and Lua-scripted payload sequences.

## Exercises

### Exercise 1: Basic Camera Triggering

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --map

param set RELAY1_PIN 54
param set RELAY1_DEFAULT 0
param set CAM_DURATION 10
param write
reboot
```

```python
# camera_mission.py
from pymavlink import mavutil

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()

waypoints = [
    (35.3632, 149.1652, 100, 22),  # Takeoff
    (35.3632, 149.1752, 100, 16),  # Waypoint 1
    (0, 0, 0, 203),                # DO_DIGICAM_CONTROL
    (35.3532, 149.1752, 100, 16),  # Waypoint 2
    (0, 0, 0, 203),                # Trigger camera again
    (35.3632, 149.1652, 0, 21),    # Land
]
```

### Exercise 2: Distance-Based Camera Triggering

```bash
param set CAM_TRIGG_TYPE 1
param set CAM1_TYPE 1
param write
```

```python
waypoints = [
    (35.3632, 149.1652, 100, 22),
    (35.3632, 149.1752, 100, 16),
    (0, 25, 0, 0, 0, 0, 0, 206),   # DO_SET_CAM_TRIGG_DIST (25m)
    (35.3532, 149.1752, 100, 16),
    (35.3532, 149.1852, 100, 16),
    (35.3432, 149.1852, 100, 16),
    (0, 0, 0, 0, 0, 0, 0, 206),    # Stop triggering
    (35.3632, 149.1652, 100, 16),
    (35.3632, 149.1652, 0, 21),
]
```

### Exercise 3: Servo-Controlled Payload Release

```bash
param set SERVO9_FUNCTION 10
param set SERVO9_MIN 1000
param set SERVO9_MAX 2000
param set SERVO9_TRIM 1000
param write
reboot
```

```python
waypoints = [
    (35.3632, 149.1652, 100, 22),
    (35.3532, 149.1752, 100, 16),
    (9, 2000, 0, 0, 0, 0, 0, 183),  # DO_SET_SERVO open
    (1, 0, 0, 0, 0, 0, 0, 93),      # NAV_DELAY 1s
    (9, 1000, 0, 0, 0, 0, 0, 183),  # DO_SET_SERVO close
    (35.3632, 149.1652, 100, 16),
    (35.3632, 149.1652, 0, 21),
]
```

### Exercise 4: Gimbal Configuration

```bash
param set MNT1_TYPE 1             # 1=Servo, 3=Alexmos, 4=SToRM32 MAVLink
param set MNT1_DEFLT_MODE 3       # 3=RC targeting, 6=GPS point

param set SERVO10_FUNCTION 8      # Mount1 Roll
param set SERVO11_FUNCTION 7      # Mount1 Pitch
param set SERVO12_FUNCTION 6      # Mount1 Yaw

param set SERVO10_MIN 1000
param set SERVO10_MAX 2000
param set SERVO11_MIN 1000
param set SERVO11_MAX 2000
param set SERVO12_MIN 1000
param set SERVO12_MAX 2000

param set MNT1_ROLL_MIN -4500
param set MNT1_ROLL_MAX 4500
param set MNT1_PITCH_MIN -9000
param set MNT1_PITCH_MAX 2500
param set MNT1_YAW_MIN -9000
param set MNT1_YAW_MAX 9000
param write
reboot
```

### Exercise 5: Gimbal Point of Interest (ROI)

```python
waypoints = [
    (35.3632, 149.1652, 100, 22),
    (35.3532, 149.1752, 50, 201),   # DO_SET_ROI
    (35.3632, 149.1752, 100, 16),
    (35.3632, 149.1852, 100, 16),
    (35.3532, 149.1852, 100, 16),
    (35.3532, 149.1752, 100, 16),
    (0, 0, 0, 197),                 # DO_SET_ROI_NONE
    (35.3632, 149.1652, 0, 21),
]
```

### Exercise 6: Advanced Payload Sequence

```python
waypoints = [
    (35.3632, 149.1652, 100, 22),
    (3, 2000, 0, 0, 0, 0, 0, 183),  # Retract landing gear
    (0, -90, 0, 0, 0, 0, 2, 205),   # DO_MOUNT_CONTROL pitch -90
    (0, 30, 0, 0, 0, 0, 0, 206),    # Start triggers every 30m
    (35.3632, 149.1752, 100, 16),
    (35.3532, 149.1752, 100, 16),
    (35.3532, 149.1852, 100, 16),
    (0, 0, 0, 0, 0, 0, 0, 206),     # Stop triggers
    (0, 0, 0, 0, 0, 0, 2, 205),     # Gimbal forward
    (35.3632, 149.1652, 100, 16),
    (3, 1000, 0, 0, 0, 0, 0, 183),  # Extend landing gear
    (35.3632, 149.1652, 0, 21),
]
```

### Exercise 7: Lua Script Payload Control

```lua
-- payload_control.lua
local RELAY_PIN = 1
local SERVO_NUM = 9
local UPDATE_RATE_HZ = 10

function update()
    local alt = ahrs:get_position():alt() * 0.01
    local mode = vehicle:get_mode()

    if mode == 10 and alt < 50 then  -- AUTO, below 50m
        relay:on(RELAY_PIN)
        SRV_Channels:set_output_pwm(SERVO_NUM, 2000)
        gcs:send_text(0, "Payload deployed at " .. tostring(alt) .. "m")
    else
        relay:off(RELAY_PIN)
        SRV_Channels:set_output_pwm(SERVO_NUM, 1000)
    end

    return update, 1000 // UPDATE_RATE_HZ
end

return update()
```

```bash
param set SCR_ENABLE 1
param set SCR_VM_I_COUNT 100000
param write
reboot
```

## Common Issues

### Camera Not Triggering

```bash
param show RELAY1_PIN
param set RELAY1_PIN 54
param show CAM_TRIGG_TYPE
param set CAM_TRIGG_TYPE 1
relay set 1 1  # Test relay manually
relay set 1 0
```

### Servo Not Moving

```bash
param show SERVO9_FUNCTION
param set SERVO9_FUNCTION 10
param set SERVO9_MIN 1000
param set SERVO9_MAX 2000
servo set 9 1500
servo set 9 2000
param set BRD_PWM_COUNT 8
```

### Gimbal Erratic or Not Stabilizing

```bash
param show MNT1_TYPE
param set MNT1_TYPE 1
param show SERVO10_FUNCTION  # Should be 8 (Mount1Roll)
param show SERVO11_FUNCTION  # Should be 7 (Mount1Pitch)
param set MNT1_STAB_ROLL 1
param set MNT1_STAB_TILT 1
```

### Distance Trigger Not Working

```bash
param set CAM_TRIGG_TYPE 1
param set CAM_LOG 1
# Verify GPS lock > 6 satellites and vehicle is moving
```

### Payload Release Timing Issues

Add `NAV_DELAY` before release; account for vehicle speed and wind drift; position upwind of target.

## Payload Examples

### Survey Photography

```python
import math
altitude = 100
camera_fov = 60
ground_coverage = 2 * altitude * math.tan(math.radians(camera_fov/2))
trigger_distance = ground_coverage * 0.3  # 70% overlap

waypoints = [
    (35.3632, 149.1652, altitude, 22),
    (35.3632, 149.1752, altitude, 16),
    (0, trigger_distance, 0, 0, 0, 0, 0, 206),
    # ... survey lines ...
    (0, 0, 0, 0, 0, 0, 0, 206),
]
```

### Package Delivery

```python
waypoints = [
    (35.3632, 149.1652, 100, 22),
    (35.3532, 149.1752, 100, 16),
    (35.3532, 149.1752, 30, 16),    # Descend to drop altitude
    (0, 5, 0, 0, 0, 0, 0, 93),      # Wait 5s to stabilize
    (9, 2000, 0, 0, 0, 0, 0, 183),  # Release
    (0, 2, 0, 0, 0, 0, 0, 93),      # Wait 2s
    (9, 1000, 0, 0, 0, 0, 0, 183),  # Close
    (35.3532, 149.1752, 100, 16),
    (0, 0, 0, 0, 0, 0, 0, 20),      # RTL
]
```

---

- [Payload Integration Guide](PAYLOAD_INTEGRATION_GUIDE.md)
- [Camera and Gimbal Setup](https://ardupilot.org/copter/docs/common-cameras-and-gimbals.html)
- [Servo Output Functions](https://ardupilot.org/plane/docs/common-rcoutput-mapping.html)
- [Mount Configuration](https://ardupilot.org/copter/docs/common-mount-targeting.html)
- [MAVLink Commands](https://mavlink.io/en/messages/common.html)
