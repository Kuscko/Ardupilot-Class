# Lua Scripting in ArduPilot

## Overview

ArduPilot supports Lua scripting for custom vehicle behaviors, allowing you to read sensors, control outputs, modify parameters, and send messages without modifying C++ code [1]. Lua scripts run within the ArduPilot flight controller, providing powerful customization capabilities while maintaining safety and reliability.

**Key Benefits:**
- Add custom functionality without recompiling firmware
- Rapid prototyping and testing of new features
- Read sensor data and control actuators in real-time
- Implement custom flight modes or behaviors
- Create automated sequences and mission logic

## Prerequisites

Before starting this module, you should:

- Have completed SITL setup and be comfortable running simulations
- Understand basic programming concepts (variables, functions, loops)
- Be familiar with ArduPilot parameters and flight modes
- Know how to upload files to flight controllers or SITL

**Programming Experience:** Basic programming knowledge in any language is helpful, but Lua is beginner-friendly.

## What You'll Learn

By completing this module, you will:

- Enable and configure Lua scripting in ArduPilot
- Understand Lua script structure and lifecycle
- Use common Lua API functions to interact with ArduPilot
- Read sensor data (altitude, GPS, battery, attitude)
- Send messages to ground control stations
- Control outputs (servos, LEDs, relays)
- Debug Lua scripts and handle errors
- Test scripts safely in SITL before hardware deployment

## Getting Started

### Enable Scripting in SITL

1. Start SITL:
```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py
```

2. Enable scripting (in MAVProxy console):
```
param set SCR_ENABLE 1
param set SCR_HEAP_SIZE 80000
reboot
```

3. After reboot, verify scripting is enabled:
```
param show SCR_*
```

### Script Location

**SITL:** Place scripts in `~/ardupilot/scripts/`

**Hardware:** Place scripts on SD card at `/APM/scripts/`

Scripts must have `.lua` extension and are loaded automatically at startup.

## Key Concepts

### Lua Script Structure

Every Lua script follows this basic pattern [2]:

```lua
-- Script initialization (runs once at startup)
local count = 0

-- Update function (called repeatedly)
function update()
    -- Your code here
    count = count + 1
    gcs:send_text(6, string.format("Update %d", count))

    -- Return time in milliseconds until next call
    return update, 1000  -- Call again in 1000ms (1 second)
end

-- Register the update function
return update()
```

**Key Points:**
- Script must return a function and delay time
- Delay controls how frequently the function runs
- Use `return update, 1000` for 1-second intervals
- Lower delays (100ms) for time-critical tasks

### Common API Functions

**Sending Messages:**
```lua
gcs:send_text(6, "Hello from Lua")  -- MAV_SEVERITY_INFO = 6
```

**Reading Altitude:**
```lua
local altitude = ahrs:get_relative_altitude()
```

**Reading GPS:**
```lua
local location = ahrs:get_position()
if location then
    local lat = location:lat() / 10000000
    local lon = location:lng() / 10000000
end
```

**Reading Battery:**
```lua
local battery = battery()
if battery then
    local voltage = battery:voltage()
    local remaining = battery:capacity_remaining_pct()
end
```

**Controlling Servos:**
```lua
SRV_Channels:set_output_pwm(9, 1500)  -- Servo 9, 1500us pulse width
```

See [Lua API Reference](https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_Scripting/docs) [2] for complete function list.

## Hands-On Practice

### Exercise 1: Hello World

Create your first Lua script:

```bash
cd ~/ardupilot/scripts
nano hello_world.lua
```

Copy content from **[hello_world.lua](hello_world.lua)**, save, and start SITL.

**Expected Result:** GCS messages showing "Hello from Lua!" every 5 seconds

**Verify:**
```
# In MAVProxy console, watch for messages
```

### Exercise 2: Altitude Monitor

Create a script that monitors altitude and warns when low:

```bash
cd ~/ardupilot/scripts
cp ~/Desktop/Work/AEVEX/Lua_Scripts/altitude_monitor.lua .
```

Start SITL and takeoff:
```
mode FBWA
arm throttle
rc 3 1700
```

**Expected Result:** When altitude < 50m, see warning messages in GCS

### Exercise 3: Battery Monitor

Monitor battery voltage and warn when low:

```bash
cp ~/Desktop/Work/AEVEX/Lua_Scripts/battery_monitor.lua ~/ardupilot/scripts/
reboot
```

**Expected Result:** Messages showing battery voltage and warnings if < 11.1V

### Exercise 4: Custom Mode Switching

Implement automatic mode switching based on conditions:

```bash
cp ~/Desktop/Work/AEVEX/Lua_Scripts/auto_mode_switch.lua ~/ardupilot/scripts/
reboot
```

This script demonstrates reading vehicle state and triggering mode changes.

### Exercise 5: Waypoint Logger

Log waypoint progress during missions:

```bash
cp ~/Desktop/Work/AEVEX/Lua_Scripts/waypoint_logger.lua ~/ardupilot/scripts/
reboot
```

Load a mission and run it in AUTO mode to see waypoint updates.

### Exercise 6: Servo Sweep (Advanced)

Control servos with smooth motion:

```bash
cp ~/Desktop/Work/AEVEX/Lua_Scripts/servo_sweep.lua ~/ardupilot/scripts/
reboot
```

Watch servo 9 sweep back and forth automatically.

## Example Scripts

This module includes several example scripts with increasing complexity:

| Script | Purpose | Difficulty | Key Concepts |
|--------|---------|------------|--------------|
| [hello_world.lua](hello_world.lua) | Basic script structure | Beginner | Function return, GCS messages |
| [altitude_monitor.lua](altitude_monitor.lua) | Read sensors, send messages | Beginner | AHRS API, conditionals |
| [battery_monitor.lua](battery_monitor.lua) | Monitor battery levels | Beginner | Battery API, formatting |
| [auto_mode_switch.lua](auto_mode_switch.lua) | Automatic mode changes | Intermediate | Mode control, state tracking |
| [waypoint_logger.lua](waypoint_logger.lua) | Log waypoint data | Intermediate | Mission API, navigation |
| [servo_sweep.lua](servo_sweep.lua) | Control servos | Advanced | Servo control, math functions |

## Complete Guide

See **[LUA_SCRIPTING_GUIDE.md](LUA_SCRIPTING_GUIDE.md)** for comprehensive documentation including:

- Detailed Lua language reference
- Complete API documentation
- Advanced scripting techniques
- Performance optimization
- Error handling best practices
- Hardware deployment guide

## Common Issues

### Issue: Script not loading

**Symptom:** No messages from Lua script in GCS

**Solutions:**
1. Verify scripting enabled: `param show SCR_ENABLE` (should be 1)
2. Check heap size sufficient: `param show SCR_HEAP_SIZE` (80000+ recommended)
3. Verify script location: SITL uses `~/ardupilot/scripts/`, hardware uses SD card `/APM/scripts/`
4. Check script syntax: Look for Lua syntax errors in console
5. Reboot after parameter changes: `reboot`

### Issue: "not enough memory" error

**Symptom:** Script fails to load with memory error

**Solutions:**
1. Increase heap size: `param set SCR_HEAP_SIZE 120000`
2. Reduce script complexity or number of scripts
3. Optimize memory usage in script (avoid large tables/strings)
4. Check available RAM on flight controller

### Issue: Script runs but output unexpected

**Symptom:** Script loads but doesn't work as expected

**Debug Steps:**
1. Add debug messages: `gcs:send_text(6, "Debug: variable value")`
2. Check return value: Ensure `return update, DELAY` is correct
3. Verify API calls: Check function exists and parameters correct
4. Test incrementally: Start simple, add features gradually

### Issue: "function not found" error

**Symptom:** Script reports unknown function

**Cause:** API function not available in current ArduPilot version or vehicle type

**Solutions:**
1. Check API documentation for your version
2. Verify function available for vehicle type (Plane vs Copter)
3. Update ArduPilot to newer version if needed
4. Use alternative API function

### Issue: Scripts interfere with each other

**Symptom:** Multiple scripts cause conflicts or crashes

**Solutions:**
1. Reduce total script complexity
2. Increase heap size to accommodate all scripts
3. Ensure scripts don't control same outputs
4. Use longer update intervals to reduce CPU load

## Script Performance Guidelines

**Update Intervals:**
- General monitoring: 1000ms (1 second)
- Sensor reading: 100-500ms
- Critical control: 50-100ms (minimum)
- Never use delays < 20ms

**Memory Management:**
- Keep heap size < 150KB on most boards
- Avoid creating new objects in update loop
- Use local variables when possible
- Reuse tables and strings

**CPU Usage:**
- Scripts share CPU with flight code (priority: flight safety)
- Keep scripts lightweight and efficient
- Test in SITL before hardware deployment

## Additional Resources

### Official ArduPilot Documentation

- **[ArduPilot Lua Scripting](https://ardupilot.org/plane/docs/common-lua-scripts.html)** [1] - Official scripting guide
- **[Lua API Reference](https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_Scripting/docs)** [2] - Complete API documentation
- **[Lua Applets Library](https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_Scripting/applets)** [3] - Community-contributed scripts
- **[Scripting Parameters](https://ardupilot.org/plane/docs/parameters.html#scr-parameters)** - SCR_* parameter reference

### Lua Language Resources

- **[Lua 5.3 Reference Manual](https://www.lua.org/manual/5.3/)** - Official Lua documentation
- **[Learn Lua in 15 Minutes](https://learnxinyminutes.com/docs/lua/)** - Quick Lua tutorial
- **[Programming in Lua](https://www.lua.org/pil/)** - Comprehensive Lua guide

### Example Scripts and Tutorials

- **[ArduPilot Scripting Examples](https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_Scripting/examples)** - Official examples
- **[Community Scripting Forum](https://discuss.ardupilot.org/c/arducopter/scripting/73)** - Q&A and script sharing
- **[Scripting Blog Posts](https://ardupilot.org/dev/docs/common-blogs.html)** - Technical articles

## Safety Considerations

**Before running scripts on hardware:**

1. Test thoroughly in SITL first
2. Understand what the script does
3. Have a failsafe plan (e.g., RC mode switch)
4. Start with read-only scripts (no control outputs)
5. Monitor behavior carefully during initial tests
6. Keep manual control available at all times

**Script Safety Rules:**
- Never disable safety features
- Always include error checking
- Test edge cases and failures
- Use appropriate update intervals
- Monitor CPU and memory usage

## Next Steps

After completing this Lua scripting module:

1. **Create Custom Scripts** - Implement your own vehicle behaviors
2. **Integrate with MAVLink** - Combine Lua with custom MAVLink messages ([MAVLink Guide](../MAVLink_MavlinkRouter/))
3. **Advanced Navigation** - Use Lua to implement custom navigation logic ([Navigation Deep Dive](../Advanced_Topics/Navigation_Deep_Dive/))
4. **Hardware Deployment** - Deploy scripts to real flight controllers
5. **Contribute** - Share useful scripts with the community

---

**Sources:**

[1] https://ardupilot.org/plane/docs/common-lua-scripts.html
[2] https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_Scripting/docs
[3] https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_Scripting/applets
