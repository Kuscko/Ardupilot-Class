# ArduPilot Onboarding Environment - Master Guide

This repository contains a complete onboarding environment for new engineers learning ArduPilot Plane 4.5.7: build instructions, installation scripts, example missions, Lua scripts, documentation, and presentation materials.

**Target Firmware:** Plane 4.5.7 (commit: 0358a9c210bc6c965006f5d6029239b7033616df)
**Platform:** Ubuntu 22.04 LTS (WSL2) — Python 3.10, WSLg GUI support (Windows 11)

---

## Quick Start

1. Read [ArduPilot Onboarding Guide](Onboarding_Documentation/ArduPilot_Onboarding_Guide.md)
2. Follow the folder structure below in order
3. Track progress with [Onboarding Checklist](Slides_Notes/ONBOARDING_CHECKLIST.md) and [Quick Reference Card](Slides_Notes/QUICK_REFERENCE_CARD.md)

---

## 1. ArduPilot Build Instructions

**Key Files:**

- [BUILD_GUIDE.md](ArduPilot_Build_Instructions/BUILD_GUIDE.md)
- [TROUBLESHOOTING.md](ArduPilot_Build_Instructions/TROUBLESHOOTING.md)

**Time estimate:** 1-2 hours

---

## 2. Installation Scripts

**Key Files:**

- [INSTALLATION_GUIDE.md](Installation_Scripts/INSTALLATION_GUIDE.md)
- [install_ardupilot_plane_4.5.7.sh](Installation_Scripts/install_ardupilot_plane_4.5.7.sh)
- [install_mavproxy.sh](Installation_Scripts/install_mavproxy.sh)
- [setup_x_server.md](Installation_Scripts/setup_x_server.md)

**Time estimate:** 30 minutes (plus 15-30 min installation)

---

## 3. SITL Mission Plans

**Key Files:**

- [SITL_QUICK_START.md](SITL_Mission_Plans/SITL_QUICK_START.md)
- [EXAMPLE_MISSIONS.md](SITL_Mission_Plans/EXAMPLE_MISSIONS.md)
- [PARAMETER_GUIDE.md](SITL_Mission_Plans/PARAMETER_GUIDE.md)

**Time estimate:** 3-5 hours

---

## 4. Lua Scripts

**Key Files:**

- [LUA_SCRIPTING_GUIDE.md](Lua_Scripts/LUA_SCRIPTING_GUIDE.md)
- [hello_world.lua](Lua_Scripts/hello_world.lua)
- [altitude_monitor.lua](Lua_Scripts/altitude_monitor.lua)
- [battery_monitor.lua](Lua_Scripts/battery_monitor.lua)
- [auto_mode_switch.lua](Lua_Scripts/auto_mode_switch.lua)
- [waypoint_logger.lua](Lua_Scripts/waypoint_logger.lua)
- [servo_sweep.lua](Lua_Scripts/servo_sweep.lua)

**Time estimate:** 2-3 hours

---

## 5. MAVLink & Mavlink Router

**Key Files:**

- [MAVLINK_GUIDE.md](MAVLink_MavlinkRouter/MAVLINK_GUIDE.md)
- [MAVLINK_ROUTER_GUIDE.md](MAVLink_MavlinkRouter/MAVLINK_ROUTER_GUIDE.md)
- [example_configs/](MAVLink_MavlinkRouter/example_configs/)
- [example_python_scripts/](MAVLink_MavlinkRouter/example_python_scripts/)

**Time estimate:** 2-3 hours

---

## 6. EKF Notes

**Key Files:**

- [EKF_FUNDAMENTALS.md](EKF_Notes/EKF_FUNDAMENTALS.md)

**Time estimate:** 1-2 hours

---

## 7. Sensor Drivers

**Key Files:**

- [SENSOR_DRIVER_GUIDE.md](Sensor_Drivers/SENSOR_DRIVER_GUIDE.md)

**Time estimate:** 1-2 hours

---

## 8. Slides & Notes

**Key Files:**

- [ONBOARDING_PRESENTATION_OUTLINE.md](Slides_Notes/ONBOARDING_PRESENTATION_OUTLINE.md)
- [QUICK_REFERENCE_CARD.md](Slides_Notes/QUICK_REFERENCE_CARD.md)
- [ONBOARDING_CHECKLIST.md](Slides_Notes/ONBOARDING_CHECKLIST.md)

---

## Recommended Learning Path

### Week 1: Foundation

**Day 1-2:**

1. Read [ArduPilot Onboarding Guide](Onboarding_Documentation/ArduPilot_Onboarding_Guide.md) (Week 1 sections)
2. Follow [BUILD_GUIDE.md](ArduPilot_Build_Instructions/BUILD_GUIDE.md)
3. Run [install_ardupilot_plane_4.5.7.sh](Installation_Scripts/install_ardupilot_plane_4.5.7.sh)
4. Start SITL and complete first flight

**Day 3-4:**

1. Study [SITL_QUICK_START.md](SITL_Mission_Plans/SITL_QUICK_START.md) and [PARAMETER_GUIDE.md](SITL_Mission_Plans/PARAMETER_GUIDE.md)
2. Practice flight modes, TECS parameters, and failsafe configuration

**Day 5:**

1. Study [EXAMPLE_MISSIONS.md](SITL_Mission_Plans/EXAMPLE_MISSIONS.md)
2. Create and execute missions

### Week 2: Advanced Topics

**Day 6-7:**

1. Read [ArduPilot Onboarding Guide](Onboarding_Documentation/ArduPilot_Onboarding_Guide.md) (Week 2 sections)
2. Build ArduPilot from source and explore codebase

**Day 8-9:**

1. Study [MAVLINK_GUIDE.md](MAVLink_MavlinkRouter/MAVLINK_GUIDE.md) and [MAVLINK_ROUTER_GUIDE.md](MAVLink_MavlinkRouter/MAVLINK_ROUTER_GUIDE.md)
2. Practice pymavlink examples and set up mavlink-router

**Day 10:**

1. Study [LUA_SCRIPTING_GUIDE.md](Lua_Scripts/LUA_SCRIPTING_GUIDE.md)
2. Test example Lua scripts and write a custom script

### Week 3: Deep Dives

1. Study [EKF_FUNDAMENTALS.md](EKF_Notes/EKF_FUNDAMENTALS.md)
2. Study [SENSOR_DRIVER_GUIDE.md](Sensor_Drivers/SENSOR_DRIVER_GUIDE.md)
3. Review [ONBOARDING_CHECKLIST.md](Slides_Notes/ONBOARDING_CHECKLIST.md)

---

## Advanced Topics Learning Path

### Phase 1: Development Fundamentals (Weeks 3-4)

1. **[Code Contribution Workflow](Advanced_Topics/Code_Contribution_Workflow/)** - Git workflows, code style, PR process
2. **[Custom Build Configurations](Advanced_Topics/Custom_Build_Configurations/)** - Build for specific hardware
3. **[Debugging Tools](Advanced_Topics/Debugging_Tools/)** - GDB and debugging techniques

### Phase 2: Vehicle Behavior & Tuning (Weeks 4-5)

1. **[PID Tuning](Advanced_Topics/PID_Tuning/)** - Tune flight controllers for stable flight
2. **[Navigation Deep Dive](Advanced_Topics/Navigation_Deep_Dive/)** - Waypoint navigation and path planning
3. **[Performance Optimization](Advanced_Topics/Performance_Optimization/)** - Optimize code and reduce latency

### Phase 3: Safety & Testing (Weeks 5-6)

1. **[Safety & Geofencing](Advanced_Topics/Safety_Geofencing/)** - Safety features and geofences
2. **[Testing & CI/CD](Advanced_Topics/Testing_CI_CD/)** - Write tests and automate validation
3. **[HITL Testing](Advanced_Topics/HITL_Testing/)** - Test with real hardware in the loop

### Phase 4: Integration & Customization (Weeks 6-7)

1. **[Companion Computer](Advanced_Topics/Companion_Computer/)** - Integrate companion computers (Raspberry Pi, Jetson)
2. **[Custom MAVLink Messages](Advanced_Topics/Custom_MAVLink_Messages/)** - Create custom telemetry messages
3. **[Payload Integration](Advanced_Topics/Payload_Integration/)** - Control cameras, gimbals, and payloads

### Phase 5: Advanced Features (Weeks 7-8)

1. **[OSD Configuration](Advanced_Topics/OSD_Configuration/)** - Configure on-screen displays
2. **[Telemetry Radio Setup](Advanced_Topics/Telemetry_Radio_Setup/)** - Optimize radio links and range
3. **[RC Calibration](Advanced_Topics/RC_Calibration/)** - Advanced RC setup and mixing
4. **[Flight Log Analysis](Advanced_Topics/Flight_Log_Analysis/)** - Analyze logs to diagnose issues

### Phase 6: SITL Advanced Features (Week 8+)

1. **[SITL Advanced Features](Advanced_Topics/SITL_Advanced_Features/)** - Multi-vehicle simulation, sensor simulation, custom scenarios

### Advanced Topics Resources

- [ArduPilot Developer Documentation](https://ardupilot.org/dev/)
- [Contributing Guide](https://ardupilot.org/dev/docs/contributing.html)
- [Code Overview](https://ardupilot.org/dev/docs/code-overview.html)

---

## Quick Links

### Essential Documentation

- [Main Onboarding Guide](Onboarding_Documentation/ArduPilot_Onboarding_Guide.md)
- [Quick Reference Card](Slides_Notes/QUICK_REFERENCE_CARD.md)
- [Onboarding Checklist](Slides_Notes/ONBOARDING_CHECKLIST.md)

### Getting Started

- [Build Guide](ArduPilot_Build_Instructions/BUILD_GUIDE.md)
- [Installation Scripts](Installation_Scripts/INSTALLATION_GUIDE.md)
- [SITL Quick Start](SITL_Mission_Plans/SITL_QUICK_START.md)

### Guides

- [Parameter Guide](SITL_Mission_Plans/PARAMETER_GUIDE.md)
- [Lua Scripting Guide](Lua_Scripts/LUA_SCRIPTING_GUIDE.md)
- [MAVLink Guide](MAVLink_MavlinkRouter/MAVLINK_GUIDE.md)
- [EKF Fundamentals](EKF_Notes/EKF_FUNDAMENTALS.md)
- [Sensor Driver Guide](Sensor_Drivers/SENSOR_DRIVER_GUIDE.md)

### Examples

- [Example Missions](SITL_Mission_Plans/EXAMPLE_MISSIONS.md)
- [Lua Scripts](Lua_Scripts/)
- [Python MAVLink Scripts](MAVLink_MavlinkRouter/example_python_scripts/)
- [mavlink-router Configs](MAVLink_MavlinkRouter/example_configs/)

---

## External Resources

### ArduPilot Official

- **Plane Documentation:** [https://ardupilot.org/plane/](https://ardupilot.org/plane/)
- **Developer Documentation:** [https://ardupilot.org/dev/](https://ardupilot.org/dev/)
- **Parameter Reference:** [https://ardupilot.org/plane/docs/parameters.html](https://ardupilot.org/plane/docs/parameters.html)
- **GitHub Repository:** [https://github.com/ArduPilot/ardupilot](https://github.com/ArduPilot/ardupilot)
- **Discourse Forum:** [https://discuss.ardupilot.org/](https://discuss.ardupilot.org/)
- **Discord:** [https://ardupilot.org/discord](https://ardupilot.org/discord)

### MAVLink

- **MAVLink Protocol:** [https://mavlink.io/en/](https://mavlink.io/en/)
- **Common Messages:** [https://mavlink.io/en/messages/common.html](https://mavlink.io/en/messages/common.html)
- **pymavlink:** [https://mavlink.io/en/mavgen_python/](https://mavlink.io/en/mavgen_python/)

### Tools

- **Mission Planner:** [https://ardupilot.org/planner/](https://ardupilot.org/planner/)
- **QGroundControl:** [https://docs.qgroundcontrol.com/](https://docs.qgroundcontrol.com/)
- **mavlink-router:** [https://github.com/mavlink-router/mavlink-router](https://github.com/mavlink-router/mavlink-router)

---

## Getting Help

1. Review onboarding documentation and [TROUBLESHOOTING.md](ArduPilot_Build_Instructions/TROUBLESHOOTING.md)
2. Search [ArduPilot Discourse](https://discuss.ardupilot.org/) or [GitHub Issues](https://github.com/ArduPilot/ardupilot/issues)
3. Ask team members

---

## Version Information

**Target ArduPilot Version:** Plane 4.5.7
**Git Tag:** Plane-4.5.7
**Commit:** 0358a9c210bc6c965006f5d6029239b7033616df
**Binaries:** [https://firmware.ardupilot.org/Plane/stable-4.5.7/](https://firmware.ardupilot.org/Plane/stable-4.5.7/)
**Last Updated:** 2026-02-04

---

## License

This onboarding documentation follows GPLv3 (same as ArduPilot). Example code and scripts are provided as-is for educational purposes.

ArduPilot: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)
