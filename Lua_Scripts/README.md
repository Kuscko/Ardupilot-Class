# Lua Scripting in ArduPilot

## Overview

ArduPilot supports Lua scripting for custom vehicle behaviors — reading sensors, controlling outputs, modifying parameters, and sending messages — without modifying C++ firmware.

## Prerequisites

- SITL setup complete and comfortable running simulations
- Familiar with ArduPilot parameters and flight modes
- Basic programming knowledge (Lua is beginner-friendly)

## Getting Started

### Enable Scripting in SITL

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py
```

In MAVProxy console:
```
param set SCR_ENABLE 1
param set SCR_HEAP_SIZE 80000
reboot
```

After reboot, verify: `param show SCR_*`

### Script Location

**SITL:** `~/ardupilot/scripts/`

**Hardware:** SD card at `/APM/scripts/`

Scripts must have `.lua` extension and load automatically at startup.

## Key Concepts

### Lua Script Structure

```lua
-- Script initialization (runs once at startup)
local count = 0

-- Update function (called repeatedly)
function update()
    count = count + 1
    gcs:send_text(6, string.format("Update %d", count))
    return update, 1000  -- Call again in 1000ms
end

-- Register the update function
return update()
```

### Common API Functions

```lua
gcs:send_text(6, "Hello from Lua")          -- MAV_SEVERITY_INFO = 6

local altitude = ahrs:get_relative_altitude()

local location = ahrs:get_position()
if location then
    local lat = location:lat() / 10000000
    local lon = location:lng() / 10000000
end

SRV_Channels:set_output_pwm(9, 1500)        -- Servo 9, 1500µs
```

See [Lua API Reference](https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_Scripting/docs).

## Hands-On Exercises

### Exercise 1: Hello World

```bash
cd ~/ardupilot/scripts
nano hello_world.lua
```

Copy content from **[hello_world.lua](hello_world.lua)**, save, and start SITL. Expected: "Hello from Lua!" every 5 seconds.

### Exercise 2: Altitude Monitor

```bash
cp ~/Desktop/Work/AEVEX/Lua_Scripts/altitude_monitor.lua ~/ardupilot/scripts/
```

```
mode FBWA
arm throttle
rc 3 1700
```

Expected: warnings when altitude < 50m.

### Exercise 3: Battery Monitor

```bash
cp ~/Desktop/Work/AEVEX/Lua_Scripts/battery_monitor.lua ~/ardupilot/scripts/
reboot
```

### Exercise 4: Custom Mode Switching

```bash
cp ~/Desktop/Work/AEVEX/Lua_Scripts/auto_mode_switch.lua ~/ardupilot/scripts/
reboot
```

### Exercise 5: Waypoint Logger

```bash
cp ~/Desktop/Work/AEVEX/Lua_Scripts/waypoint_logger.lua ~/ardupilot/scripts/
reboot
```

Load a mission and run in AUTO mode to see waypoint updates.

### Exercise 6: Servo Sweep (Advanced)

```bash
cp ~/Desktop/Work/AEVEX/Lua_Scripts/servo_sweep.lua ~/ardupilot/scripts/
reboot
```

## Example Scripts

| Script | Purpose | Difficulty | Key Concepts |
|--------|---------|------------|--------------|
| [hello_world.lua](hello_world.lua) | Basic script structure | Beginner | Function return, GCS messages |
| [altitude_monitor.lua](altitude_monitor.lua) | Read sensors, send messages | Beginner | AHRS API, conditionals |
| [battery_monitor.lua](battery_monitor.lua) | Monitor battery levels | Beginner | Battery API, formatting |
| [auto_mode_switch.lua](auto_mode_switch.lua) | Automatic mode changes | Intermediate | Mode control, state tracking |
| [waypoint_logger.lua](waypoint_logger.lua) | Log waypoint data | Intermediate | Mission API, navigation |
| [servo_sweep.lua](servo_sweep.lua) | Control servos | Advanced | Servo control, math functions |

See **[LUA_SCRIPTING_GUIDE.md](LUA_SCRIPTING_GUIDE.md)** for full API documentation and advanced techniques.

## Common Issues

### Script not loading
1. `param show SCR_ENABLE` should be 1
2. `param show SCR_HEAP_SIZE` (80000+ recommended)
3. Verify script location
4. Check for Lua syntax errors in console
5. Reboot after parameter changes

### "not enough memory" error
```
param set SCR_HEAP_SIZE 120000
```

### Script runs but output unexpected
1. Add debug messages: `gcs:send_text(6, "Debug: value")`
2. Verify `return update, DELAY` is correct
3. Test incrementally

## Script Performance Guidelines

| Concern | Guideline |
|---------|-----------|
| General monitoring | 1000ms interval |
| Sensor reading | 100-500ms |
| Critical control | 50-100ms minimum |
| Minimum interval | Never < 20ms |
| Heap size | Keep < 150KB |

Scripts share CPU with flight code — keep them lightweight and test in SITL before hardware deployment.

## Safety Considerations

Before running scripts on hardware:
1. Test thoroughly in SITL
2. Start with read-only scripts (no control outputs)
3. Have a failsafe plan (RC mode switch)
4. Always include `nil` checks
5. Never disable safety features

## Additional Resources

- **[ArduPilot Lua Scripting](https://ardupilot.org/plane/docs/common-lua-scripts.html)**
- **[Lua API Reference](https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_Scripting/docs)**
- **[Lua Applets Library](https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_Scripting/applets)**
- **[Lua 5.3 Reference Manual](https://www.lua.org/manual/5.3/)**
- [Community Scripting Forum](https://discuss.ardupilot.org/c/arducopter/scripting/73)

## Next Steps

1. Create custom scripts for your use case
2. Integrate with MAVLink ([MAVLink Guide](../MAVLink_MavlinkRouter/))
3. Deploy scripts to real flight controllers
