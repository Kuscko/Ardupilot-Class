# Payload Integration Guide

## Camera Triggering

### DO_DIGICAM_CONTROL

**Mission command:**
```
Command: 203 (DO_DIGICAM_CONTROL)
Param 5: 1 (trigger camera)
```

**Or via distance:**
```bash
param set CAM_TRIGG_TYPE 2      # Distance trigger
param set CAM_TRIGG_DIST 50     # Trigger every 50m
param set CAM_RELAY_ON 1        # Use relay
```

### Relay Control

```bash
param set RELAY_PIN 54          # Pixhawk AUX5
param set RELAY_DEFAULT 0       # Off by default
```

**In mission:**
```
Command: 181 (DO_SET_RELAY)
Param 1: 0 (relay number)
Param 2: 1 (on) or 0 (off)
```

## Servo Control

### PWM Output Setup

```bash
param set SERVO9_FUNCTION 0     # GPIO/manual control
param set SERVO9_MIN 1000       # Min PWM
param set SERVO9_MAX 2000       # Max PWM
param set SERVO9_TRIM 1500      # Center
```

### Mission Control

**DO_SET_SERVO command:**
```
Command: 183
Param 1: 9 (servo channel)
Param 2: 1800 (PWM value)
```

### Lua Script Control

```lua
-- Servo sweep example
function update()
    servo:set_output_pwm(9, 1500)  -- Channel 9, 1500 PWM
    return update, 100  -- 10Hz
end
return update()
```

## Gimbal Control

### Mount Setup

```bash
param set MNT_TYPE 1            # Servo gimbal
param set MNT_DEFLT_MODE 3      # MAVLink targeting
param set MNT_ANGMIN_ROL -45    # Min roll angle
param set MNT_ANGMAX_ROL 45     # Max roll angle
param set MNT_ANGMIN_TIL -90    # Min tilt
param set MNT_ANGMAX_TIL 0      # Max tilt
param set MNT_RC_RATE 30        # Control rate
```

### Servo Channels

```bash
param set MNT_ROLL_SV 9         # Roll servo channel
param set MNT_TILT_SV 10        # Tilt servo channel
param set MNT_PAN_SV 11         # Pan servo channel (optional)
```

## Payload Release

### Servo Release

```bash
param set SERVO10_FUNCTION 0    # Manual control
param set SERVO10_MIN 1000
param set SERVO10_MAX 2000
```

**In mission (release):**
```
Command: 183 (DO_SET_SERVO)
Param 1: 10
Param 2: 2000  # Full open
```

**Lua Script Example:**
```lua
-- Drop payload at waypoint 5
function update()
    local wpnum = mission:get_current_nav_index()
    if wpnum == 5 then
        servo:set_output_pwm(10, 2000)  -- Release
        gcs:send_text(6, "Payload released!")
    end
    return update, 500
end
return update()
```

**Author:** Patrick Kelly (@Kuscko)
