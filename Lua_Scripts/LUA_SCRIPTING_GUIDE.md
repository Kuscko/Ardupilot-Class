# Lua Scripting for ArduPilot

Lua scripting adds custom behaviors to ArduPilot without modifying C++ source code. Scripts can read sensors, modify parameters, control servos, change flight modes, and send GCS messages.

**Target Version:** Plane 4.5.7

---

## Enabling Lua Scripting

```bash
# Enable scripting
param set SCR_ENABLE 1

# Restart SITL to create scripts/ directory
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane -L CMAC --console --map
```

Place `.lua` files in `~/ardupilot/ArduPlane/scripts/`. Scripts load at startup — restart SITL after adding new scripts.

On hardware, place scripts on SD card at `/APM/scripts/`.

Check console for: `Loaded script: my_script.lua`

---

## Lua Script Structure

```lua
-- Script name: example.lua
-- Description: What this script does

function update()
    -- Your code here
    gcs:send_text(6, "Script running!")

    -- Return function and interval (ms)
    return update, 1000  -- Call again in 1000ms
end

-- Start the script
return update, 1000  -- Initial call after 1000ms
```

Key points: script must return a function and interval; interval is in milliseconds; `return update, 0` stops the script.

---

## Example Scripts

### Example 1: Hello World

**File:** `hello_world.lua`

```lua
-- Hello World Script
-- Sends a message to GCS every 5 seconds

function update()
    gcs:send_text(6, "Hello from Lua!")
    return update, 5000  -- Run every 5 seconds
end

return update, 5000
```

Place in `~/ardupilot/ArduPlane/scripts/hello_world.lua`, restart SITL, watch console.

---

### Example 2: Altitude Monitor

**File:** `altitude_monitor.lua`

```lua
-- Altitude Monitor
-- Warns when altitude exceeds SCR_USER1 parameter

function update()
    -- Get current location
    local location = ahrs:get_location()

    if not location then
        -- No position fix yet
        return update, 1000
    end

    -- Get altitude in meters (relative to home)
    local altitude = location:alt() * 0.01  -- Convert cm to m

    -- Get warning threshold from SCR_USER1
    local threshold = param:get('SCR_USER1')

    if threshold and altitude > threshold then
        gcs:send_text(4, string.format("WARNING: Altitude %.1fm exceeds %.1fm!", altitude, threshold))
    end

    return update, 1000  -- Check every second
end

return update, 1000
```

```bash
param set SCR_USER1 120  # Warn above 120m
mode FBWA
arm throttle
rc 3 1800  # Climb to test
```

---

### Example 3: Battery Monitor

**File:** `battery_monitor.lua`

```lua
-- Battery Monitor
-- Sends warnings at different voltage levels

local warned_low = false
local warned_critical = false

function update()
    -- Get battery voltage
    local voltage = battery:voltage(0)  -- Battery 0

    if not voltage then
        return update, 1000
    end

    -- Critical: < 13.2V (4S LiPo)
    if voltage < 13.2 and not warned_critical then
        gcs:send_text(1, string.format("CRITICAL BATTERY: %.2fV", voltage))
        warned_critical = true
    end

    -- Low: < 14.0V (4S LiPo)
    if voltage < 14.0 and not warned_low then
        gcs:send_text(4, string.format("Low battery: %.2fV", voltage))
        warned_low = true
    end

    return update, 2000  -- Check every 2 seconds
end

return update, 2000
```

**Message Severity Levels:** 0=Emergency, 1=Alert, 2=Critical, 3=Error, 4=Warning, 5=Notice, 6=Info, 7=Debug

---

### Example 4: Automatic Mode Switch

**File:** `auto_mode_switch.lua`

```lua
-- Automatic Mode Switch
-- Switches to RTL if battery below threshold and not already in RTL

function update()
    local voltage = battery:voltage(0)

    if not voltage then
        return update, 1000
    end

    -- Get current mode
    local current_mode = vehicle:get_mode()

    -- RTL mode number is 11 for Plane
    local RTL_MODE = 11

    -- If voltage critical and not in RTL, switch to RTL
    if voltage < 13.5 and current_mode ~= RTL_MODE then
        gcs:send_text(1, string.format("Auto RTL: Battery %.2fV", voltage))
        vehicle:set_mode(RTL_MODE)
    end

    return update, 2000
end

return update, 2000
```

**Flight Mode Numbers (Plane):** 0=MANUAL, 1=CIRCLE, 2=STABILIZE, 5=FBWA, 6=FBWB, 10=AUTO, 11=RTL, 12=LOITER, 15=GUIDED

---

### Example 5: Waypoint Logger

**File:** `waypoint_logger.lua`

```lua
-- Waypoint Logger
-- Logs when waypoints are reached

local last_waypoint = -1

function update()
    -- Get current waypoint number in AUTO mode
    local current_wp = mission:get_current_nav_index()

    if current_wp and current_wp ~= last_waypoint then
        local location = ahrs:get_location()

        if location then
            local lat = location:lat() * 1e-7
            local lon = location:lng() * 1e-7
            local alt = location:alt() * 0.01

            gcs:send_text(6, string.format("WP %d reached: %.6f, %.6f, %.1fm",
                current_wp, lat, lon, alt))
        end

        last_waypoint = current_wp
    end

    return update, 500  -- Check twice per second
end

return update, 500
```

---

### Example 6: Servo Control

**File:** `servo_sweep.lua`

```lua
-- Servo Sweep
-- Sweeps servo 9 back and forth
-- Useful for testing servos or payload deployment

local servo_num = 9
local min_pwm = 1000
local max_pwm = 2000
local current_pwm = min_pwm
local direction = 1  -- 1 = increasing, -1 = decreasing
local step = 10

function update()
    -- Set servo position
    SRV_Channels:set_output_pwm_chan_timeout(servo_num, current_pwm, 100)

    -- Update position
    current_pwm = current_pwm + (step * direction)

    -- Reverse direction at limits
    if current_pwm >= max_pwm then
        direction = -1
    elseif current_pwm <= min_pwm then
        direction = 1
    end

    return update, 50  -- Update every 50ms
end

return update, 50
```

---

## Common Lua API Functions

### GCS Communication

```lua
gcs:send_text(severity, "Message")
-- Severity: 0=emergency, 4=warning, 6=info
```

### AHRS (Attitude/Heading Reference)

```lua
local location = ahrs:get_location()
if location then
    local lat = location:lat() * 1e-7  -- Degrees
    local lon = location:lng() * 1e-7  -- Degrees
    local alt = location:alt() * 0.01  -- Meters
end

local roll, pitch, yaw = ahrs:get_roll(), ahrs:get_pitch(), ahrs:get_yaw()
-- Returns radians
```

### Battery

```lua
local voltage = battery:voltage(0)
local current = battery:current_amps(0)
local remaining = battery:capacity_remaining_pct(0)  -- Percentage
```

### Parameters

```lua
local value = param:get('PARAM_NAME')
param:set('PARAM_NAME', value)
param:set_and_save('PARAM_NAME', value)
```

### Vehicle Control

```lua
local mode = vehicle:get_mode()
vehicle:set_mode(11)  -- RTL for Plane
local armed = arming:is_armed()
```

### Servo Control

```lua
-- servo_num: 1-16, pwm: 1000-2000, timeout_ms: hold duration
SRV_Channels:set_output_pwm_chan_timeout(servo_num, pwm, timeout_ms)
```

### Mission

```lua
local wp = mission:get_current_nav_index()
local count = mission:num_commands()
mission:set_current_cmd(wp_num)
```

### GPS

```lua
local gps_status = gps:status(0)  -- 0=No GPS, 1=No fix, 2=2D, 3=3D
local gps_loc = gps:location(0)
local num_sats = gps:num_sats(0)
```

---

## Script User Parameters

Scripts can use `SCR_USER1` through `SCR_USER6` for configurable values.

```lua
local threshold = param:get('SCR_USER1')
```

```bash
param set SCR_USER1 100
```

---

## Debugging Lua Scripts

```lua
gcs:send_text(6, "Debug: variable = " .. tostring(variable))
```

**Script not loading causes:** syntax error, `SCR_ENABLE` not set, insufficient memory, wrong directory, SITL not restarted.

```bash
param show SCR_*        # SCR_ENABLE should be 1
param set SCR_HEAP_SIZE 100000
```

---

## Best Practices

```lua
-- Use appropriate update intervals
return update, 1000   -- Most scripts: 1 second
return update, 5000   -- Infrequent checks

-- Always check for nil
local location = ahrs:get_location()
if not location then
    return update, 1000
end

-- Use string formatting
gcs:send_text(6, string.format("Alt: %.1fm, Speed: %.1fm/s", alt, speed))

-- Never block ArduPilot
-- BAD: while true do ... end
-- GOOD: use return interval pattern

-- Track state with variables
local last_state = false
function update()
    if condition and not last_state then
        do_something()
        last_state = true
    elseif not condition then
        last_state = false
    end
    return update, 1000
end
```

---

## Advanced Topics

### Accessing Parameters

```lua
local val = param:get('PARAM_NAME')
local val = Parameter('PARAM_NAME'):get()
Parameter('PARAM_NAME'):set(value)
```

### RC Channels

```lua
local rc_val = rc:get_pwm(3)  -- Channel 3 (throttle)
rc:override(3, 1500)
```

### Location Objects

```lua
local home = ahrs:get_home()
local current = ahrs:get_location()
if home and current then
    local dist = home:get_distance(current)
    local bearing = home:get_bearing(current)
end
```

---

## Example Use Cases

### Payload Release at Waypoint

```lua
local target_wp = 5
local released = false

function update()
    local current_wp = mission:get_current_nav_index()

    if current_wp == target_wp and not released then
        -- Release payload (servo 9 to 2000 PWM)
        SRV_Channels:set_output_pwm_chan_timeout(9, 2000, 1000)
        gcs:send_text(6, "Payload released at WP " .. target_wp)
        released = true
    end

    return update, 500
end

return update, 500
```

### Geofence Alert

```lua
local max_distance = 500  -- meters

function update()
    local home = ahrs:get_home()
    local current = ahrs:get_location()

    if home and current then
        local dist = home:get_distance(current)

        if dist > max_distance then
            gcs:send_text(4, string.format("WARNING: %.0fm from home", dist))
        end
    end

    return update, 2000
end

return update, 2000
```

---

## Testing Scripts in SITL

1. Write script and place in `~/ardupilot/ArduPlane/scripts/`
2. Restart SITL to load script
3. Check console for "Loaded script" message
4. Trigger script behavior (fly, change modes, etc.)
5. Observe output in console, modify and repeat

```bash
# Edit script in another terminal
nano ~/ardupilot/ArduPlane/scripts/my_script.lua
# In SITL: Ctrl+C to stop, up arrow + Enter to restart
```

---

## Script Library Layout

```bash
~/ardupilot/ArduPlane/scripts/
├── hello_world.lua
├── altitude_monitor.lua
├── battery_monitor.lua
├── auto_mode_switch.lua
├── waypoint_logger.lua
└── servo_sweep.lua
```

---

## Additional Resources

- [ArduPilot Lua Scripting Docs](https://ardupilot.org/plane/docs/common-lua-scripts.html)
- [Lua Scripting Applets](https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_Scripting/applets)
- [Lua Bindings Reference](https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_Scripting/docs/docs.lua)
- [Main Onboarding Guide](../Onboarding_Documentation/ArduPilot_Onboarding_Guide.md)

---

**Last Updated:** 2026-02-03
**Target Version:** Plane 4.5.7
