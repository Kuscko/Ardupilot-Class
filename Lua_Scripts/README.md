# Lua Scripts — Agent Onboarding

## Purpose
Learn, create, and document Lua scripts for ArduPilot (Plane 4.5.7). Capture all experiments, findings, and best practices during onboarding.

## Agent Instructions & TODO List

### 1. Lua Scripting Basics
- [x] Enable scripting in SITL (`param set SCR_ENABLE 1`)
- [x] Place scripts in the correct directory and restart SITL
- [x] Run and test example Lua scripts (see onboarding guide Day 10)

### 2. Script Development
- [x] Create a Lua script to monitor altitude and send a warning to GCS (see onboarding guide exercise)
- [x] Experiment with reading/writing parameters, controlling outputs, and sending messages
- [x] Document all scripts and their results

### 3. Troubleshooting
- [x] Record any issues with script loading or execution
- [x] Add solutions for common Lua scripting problems

**Deliverables:** [LUA_SCRIPTING_GUIDE.md](LUA_SCRIPTING_GUIDE.md), [hello_world.lua](hello_world.lua), [altitude_monitor.lua](altitude_monitor.lua), [battery_monitor.lua](battery_monitor.lua), [auto_mode_switch.lua](auto_mode_switch.lua), [waypoint_logger.lua](waypoint_logger.lua), [servo_sweep.lua](servo_sweep.lua)

### 4. References
- [Onboarding Guide: Lua Scripting](../../Onboarding_Documentation/ArduPilot_Onboarding_Guide.md)
- [ArduPilot Lua Scripting Docs](https://ardupilot.org/plane/docs/common-lua-scripts.html)

---
**Update this README as you develop and test Lua scripts.**