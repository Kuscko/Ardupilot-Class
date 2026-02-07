# ArduPilot Onboarding Environment - Master Guide

## Welcome!

This repository contains a complete onboarding environment for new engineers learning ArduPilot Plane 4.5.7. Everything you need to get started is here: build instructions, installation scripts, example missions, Lua scripts, documentation, and presentation materials.

**Target Firmware:** Plane 4.5.7 (commit: 0358a9c210bc6c965006f5d6029239b7033616df)

**Platform:** Ubuntu 24.04 LTS (WSL2)
- **Verified Working** on Ubuntu 24.04 LTS as of 2026-02-06
- Python 3.12.3 fully compatible
- WSLg GUI support out-of-the-box (Windows 11)

---

## Quick Start

### For New Engineers

1. **Read the main onboarding guide first:**
   - [ArduPilot Onboarding Guide](Onboarding_Documentation/ArduPilot_Onboarding_Guide.md)

2. **Follow the folder structure below in order:**
   - Start with [ArduPilot Build Instructions](#1-ardupilot-build-instructions)
   - Use [Installation Scripts](#2-installation-scripts) for automated setup
   - Practice with [SITL Mission Plans](#3-sitl-mission-plans)
   - Experiment with [Lua Scripts](#4-lua-scripts)
   - Learn [MAVLink & Mavlink Router](#5-mavlink--mavlink-router)
   - Study [EKF Notes](#6-ekf-notes)
   - Explore [Sensor Drivers](#7-sensor-drivers)
   - Review [Slides & Notes](#8-slides--notes) for presentation materials

3. **Track your progress:**
   - Use [Onboarding Checklist](Slides_Notes/ONBOARDING_CHECKLIST.md)
   - Keep [Quick Reference Card](Slides_Notes/QUICK_REFERENCE_CARD.md) handy

---

## 1. ArduPilot Build Instructions

**Purpose:** Learn to build ArduPilot from source in WSL2/Ubuntu 24.04

**Key Files:**
- [BUILD_GUIDE.md](ArduPilot_Build_Instructions/BUILD_GUIDE.md) - Complete step-by-step build guide
- [TROUBLESHOOTING.md](ArduPilot_Build_Instructions/TROUBLESHOOTING.md) - Common build issues and solutions

**What you'll learn:**
- WSL2 setup
- Cloning ArduPilot repository
- Checking out Plane 4.5.7
- Installing dependencies
- Building for SITL
- Building for hardware targets
- Troubleshooting build errors

**Time estimate:** 1-2 hours

---

## 2. Installation Scripts

**Purpose:** Automated installation of ArduPilot development environment

**Key Files:**
- [INSTALLATION_GUIDE.md](Installation_Scripts/INSTALLATION_GUIDE.md) - Script usage guide
- [install_ardupilot_plane_4.5.7.sh](Installation_Scripts/install_ardupilot_plane_4.5.7.sh) - Main installer
- [install_mavproxy.sh](Installation_Scripts/install_mavproxy.sh) - MAVProxy installer
- [setup_x_server.md](Installation_Scripts/setup_x_server.md) - X server setup

**What you'll learn:**
- Automated setup process
- Installation script usage
- X server configuration
- Troubleshooting installation issues

**Time estimate:** 30 minutes (plus installation time: 15-30 min)

---

## 3. SITL Mission Plans

**Purpose:** Learn SITL, flight modes, parameters, and mission planning

**Key Files:**
- [SITL_QUICK_START.md](SITL_Mission_Plans/SITL_QUICK_START.md) - Getting started with SITL
- [EXAMPLE_MISSIONS.md](SITL_Mission_Plans/EXAMPLE_MISSIONS.md) - Example mission files
- [PARAMETER_GUIDE.md](SITL_Mission_Plans/PARAMETER_GUIDE.md) - Parameter configuration reference

**What you'll learn:**
- Starting SITL
- Essential MAVProxy commands
- Flight modes (MANUAL, FBWA, AUTO, RTL, etc.)
- RC channel control
- Mission planning and execution
- Parameter configuration (TECS, airspeed, throttle, failsafes)
- Parameter tuning workflows

**Time estimate:** 3-5 hours

---

## 4. Lua Scripts

**Purpose:** Learn Lua scripting for custom ArduPilot behaviors

**Key Files:**
- [LUA_SCRIPTING_GUIDE.md](Lua_Scripts/LUA_SCRIPTING_GUIDE.md) - Complete Lua scripting guide
- [hello_world.lua](Lua_Scripts/hello_world.lua) - Simplest example
- [altitude_monitor.lua](Lua_Scripts/altitude_monitor.lua) - Altitude warning example
- [battery_monitor.lua](Lua_Scripts/battery_monitor.lua) - Battery monitoring
- [auto_mode_switch.lua](Lua_Scripts/auto_mode_switch.lua) - Automatic mode switching
- [waypoint_logger.lua](Lua_Scripts/waypoint_logger.lua) - Waypoint logging
- [servo_sweep.lua](Lua_Scripts/servo_sweep.lua) - Servo control example

**What you'll learn:**
- Enabling Lua scripting
- Lua script structure
- Common Lua API functions
- Reading sensor data
- Controlling vehicle
- Sending messages to GCS
- Testing scripts in SITL

**Time estimate:** 2-3 hours

---

## 5. MAVLink & Mavlink Router

**Purpose:** Learn MAVLink protocol and routing telemetry

**Key Files:**
- [MAVLINK_GUIDE.md](MAVLink_MavlinkRouter/MAVLINK_GUIDE.md) - MAVLink protocol guide
- [MAVLINK_ROUTER_GUIDE.md](MAVLink_MavlinkRouter/MAVLINK_ROUTER_GUIDE.md) - mavlink-router setup
- [example_configs/](MAVLink_MavlinkRouter/example_configs/) - Router configuration examples
- [example_python_scripts/](MAVLink_MavlinkRouter/example_python_scripts/) - Python examples (arm_disarm.py, mavlink_monitor.py, telemetry_logger.py)

**What you'll learn:**
- MAVLink message structure
- Essential MAVLink messages
- System ID and component ID
- Connecting with pymavlink
- Reading telemetry
- Sending commands
- mavlink-router installation
- Routing to multiple endpoints
- Configuration files

**Time estimate:** 2-3 hours

---

## 6. EKF Notes

**Purpose:** Understand the Extended Kalman Filter and sensor fusion

**Key Files:**
- [EKF_FUNDAMENTALS.md](EKF_Notes/EKF_FUNDAMENTALS.md) - EKF fundamentals guide

**What you'll learn:**
- What EKF does (sensor fusion)
- Why sensor fusion is needed
- EKF predict + update cycle
- EKF3 in ArduPilot
- Key EKF parameters
- EKF health monitoring
- Pre-arm checks
- Common EKF issues
- EKF tuning basics

**Time estimate:** 1-2 hours

---

## 7. Sensor Drivers

**Purpose:** Understand ArduPilot sensor driver architecture

**Key Files:**
- [SENSOR_DRIVER_GUIDE.md](Sensor_Drivers/SENSOR_DRIVER_GUIDE.md) - Sensor driver architecture

**What you'll learn:**
- Front-end/back-end architecture
- Key sensor libraries (GPS, IMU, Baro, Compass, Airspeed)
- Sensor driver code locations
- How sensors are initialized
- SITL sensor simulation
- Sensor calibration
- Troubleshooting sensor issues

**Time estimate:** 1-2 hours

---

## 8. Slides & Notes

**Purpose:** Presentation materials for onboarding others

**Key Files:**
- [ONBOARDING_PRESENTATION_OUTLINE.md](Slides_Notes/ONBOARDING_PRESENTATION_OUTLINE.md) - Full presentation
- [QUICK_REFERENCE_CARD.md](Slides_Notes/QUICK_REFERENCE_CARD.md) - Quick reference
- [ONBOARDING_CHECKLIST.md](Slides_Notes/ONBOARDING_CHECKLIST.md) - Progress tracking

**What you'll find:**
- Presentation outline for structured learning sessions
- Slide content for each topic
- Hands-on exercise plans
- Quick reference card for daily use
- Onboarding checklist to track progress

**Use for:**
- Presenting to new team members
- Creating slide decks
- Self-study structure
- Tracking progress

---

## Recommended Learning Path

### Week 1: Foundation

**Day 1-2:**
1. Read [ArduPilot Onboarding Guide](Onboarding_Documentation/ArduPilot_Onboarding_Guide.md) (Week 1 sections)
2. Follow [BUILD_GUIDE.md](ArduPilot_Build_Instructions/BUILD_GUIDE.md)
3. Run [install_ardupilot_plane_4.5.7.sh](Installation_Scripts/install_ardupilot_plane_4.5.7.sh)
4. Start SITL and complete first flight

**Day 3-4:**
1. Study [SITL_QUICK_START.md](SITL_Mission_Plans/SITL_QUICK_START.md)
2. Study [PARAMETER_GUIDE.md](SITL_Mission_Plans/PARAMETER_GUIDE.md)
3. Practice flight modes
4. Experiment with TECS parameters
5. Configure failsafes

**Day 5:**
1. Study [EXAMPLE_MISSIONS.md](SITL_Mission_Plans/EXAMPLE_MISSIONS.md)
2. Create and execute missions
3. Test different mission commands

### Week 2: Advanced Topics

**Day 6-7:**
1. Read [ArduPilot Onboarding Guide](Onboarding_Documentation/ArduPilot_Onboarding_Guide.md) (Week 2 sections)
2. Build ArduPilot from source
3. Explore codebase structure
4. Review sensor driver code

**Day 8-9:**
1. Study [MAVLINK_GUIDE.md](MAVLink_MavlinkRouter/MAVLINK_GUIDE.md)
2. Practice pymavlink examples
3. Study [MAVLINK_ROUTER_GUIDE.md](MAVLink_MavlinkRouter/MAVLINK_ROUTER_GUIDE.md)
4. Set up mavlink-router

**Day 10:**
1. Study [LUA_SCRIPTING_GUIDE.md](Lua_Scripts/LUA_SCRIPTING_GUIDE.md)
2. Test example Lua scripts
3. Write custom Lua script

### Week 3: Deep Dives

**As needed:**
1. Study [EKF_FUNDAMENTALS.md](EKF_Notes/EKF_FUNDAMENTALS.md)
2. Study [SENSOR_DRIVER_GUIDE.md](Sensor_Drivers/SENSOR_DRIVER_GUIDE.md)
3. Complete practical exercises
4. Review [ONBOARDING_CHECKLIST.md](Slides_Notes/ONBOARDING_CHECKLIST.md)

---

## Advanced Topics Learning Path

After completing the core onboarding (Weeks 1-3), explore these advanced topics to deepen your ArduPilot expertise. We recommend following this progression to build a strong foundational understanding.

### Phase 1: Development Fundamentals (Weeks 3-4)

Start with understanding the development workflow and codebase:

1. **[Code Contribution Workflow](Advanced_Topics/Code_Contribution_Workflow/)** - Learn Git workflows, code style, and PR process [1]
2. **[Custom Build Configurations](Advanced_Topics/Custom_Build_Configurations/)** - Build for specific hardware and customize features [2]
3. **[Debugging Tools](Advanced_Topics/Debugging_Tools/)** - Master GDB and debugging techniques [3]

**Why this order:** Understanding how to contribute and debug prepares you for deeper technical work.

### Phase 2: Vehicle Behavior & Tuning (Weeks 4-5)

Learn to optimize vehicle performance:

1. **[PID Tuning](Advanced_Topics/PID_Tuning/)** - Tune flight controllers for stable flight [4]
2. **[Navigation Deep Dive](Advanced_Topics/Navigation_Deep_Dive/)** - Master waypoint navigation and path planning [5]
3. **[Performance Optimization](Advanced_Topics/Performance_Optimization/)** - Optimize code and reduce latency [6]

**Why this order:** Start with flight characteristics, then dive into navigation, then optimize performance.

### Phase 3: Safety & Testing (Week 5-6)

Ensure safe and reliable operation:

1. **[Safety & Geofencing](Advanced_Topics/Safety_Geofencing/)** - Implement safety features and geofences [7]
2. **[Testing & CI/CD](Advanced_Topics/Testing_CI_CD/)** - Write tests and automate validation [8]
3. **[HITL Testing](Advanced_Topics/HITL_Testing/)** - Test with real hardware in the loop [9]

**Why this order:** Build safety systems first, then validate with comprehensive testing.

### Phase 4: Integration & Customization (Week 6-7)

Extend ArduPilot capabilities:

1. **[Companion Computer](Advanced_Topics/Companion_Computer/)** - Integrate companion computers (Raspberry Pi, Jetson) [10]
2. **[Custom MAVLink Messages](Advanced_Topics/Custom_MAVLink_Messages/)** - Create custom telemetry messages [11]
3. **[Payload Integration](Advanced_Topics/Payload_Integration/)** - Control cameras, gimbals, and custom payloads [12]

**Why this order:** Start with basic integration, then add custom communications, then integrate hardware payloads.

### Phase 5: Advanced Features (Week 7-8)

Master specialized capabilities:

1. **[OSD Configuration](Advanced_Topics/OSD_Configuration/)** - Configure on-screen displays [13]
2. **[Telemetry Radio Setup](Advanced_Topics/Telemetry_Radio_Setup/)** - Optimize radio links and range [14]
3. **[RC Calibration](Advanced_Topics/RC_Calibration/)** - Advanced RC setup and mixing [15]
4. **[Flight Log Analysis](Advanced_Topics/Flight_Log_Analysis/)** - Analyze logs to diagnose issues [16]

**Why this order:** These topics build on previous knowledge and are often needed for specific use cases.

### Phase 6: SITL Advanced Features (Week 8+)

Leverage simulation for development:

1. **[SITL Advanced Features](Advanced_Topics/SITL_Advanced_Features/)** - Multi-vehicle simulation, sensor simulation, custom scenarios [17]

**Why last:** Advanced SITL features are most useful after understanding the system deeply.

### Learning Tips

- **Don't rush** - Each topic takes 2-4 hours minimum to understand properly
- **Complete hands-on exercises** - Practical experience solidifies theoretical knowledge
- **Test in SITL first** - Always validate concepts in simulation before hardware
- **Review official documentation** - Cross-reference with ArduPilot docs for deeper understanding
- **Join the community** - Get help on [ArduPilot Discord](https://ardupilot.org/discord) and [Discourse forums](https://discuss.ardupilot.org/)
- **Document your learning** - Keep notes of issues encountered and solutions found
- **Build progressively** - Each phase builds on previous knowledge

### Advanced Topics Resources

- [ArduPilot Developer Documentation](https://ardupilot.org/dev/) [18]
- [Contributing Guide](https://ardupilot.org/dev/docs/contributing.html) [19]
- [Code Overview](https://ardupilot.org/dev/docs/code-overview.html) [20]

**Sources:**
[1-20] Official ArduPilot Documentation: https://ardupilot.org/

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
- **Plane Documentation:** https://ardupilot.org/plane/
- **Developer Documentation:** https://ardupilot.org/dev/
- **Parameter Reference:** https://ardupilot.org/plane/docs/parameters.html (use version selector for 4.5.7)
- **GitHub Repository:** https://github.com/ArduPilot/ardupilot
- **Discourse Forum:** https://discuss.ardupilot.org/
- **Discord:** https://ardupilot.org/discord

### MAVLink
- **MAVLink Protocol:** https://mavlink.io/en/
- **Common Messages:** https://mavlink.io/en/messages/common.html
- **pymavlink:** https://mavlink.io/en/mavgen_python/

### Tools
- **Mission Planner:** https://ardupilot.org/planner/
- **QGroundControl:** https://docs.qgroundcontrol.com/
- **mavlink-router:** https://github.com/mavlink-router/mavlink-router

---

## Getting Help

### Internal Resources
1. Review onboarding documentation first
2. Check [TROUBLESHOOTING.md](ArduPilot_Build_Instructions/TROUBLESHOOTING.md)
3. Ask team members

### External Resources
1. Search [ArduPilot Discourse](https://discuss.ardupilot.org/)
2. Check [GitHub Issues](https://github.com/ArduPilot/ardupilot/issues)
3. Review [Developer Documentation](https://ardupilot.org/dev/)

### Reporting Issues
- Internal documentation issues: Update this repository
- ArduPilot bugs: Report on GitHub
- Questions: Post on Discourse

---

## Contributing

### Improving This Repository

Found something missing? Have suggestions? Please:

1. **Update documentation** - Fix errors, add clarity, expand examples
2. **Add examples** - Share useful scripts, missions, configurations
3. **Share lessons learned** - Document troubleshooting steps
4. **Improve presentation materials** - Enhance slides and notes

### Contributing to ArduPilot

After completing onboarding, consider contributing to ArduPilot:

1. **Report bugs** - Help improve stability
2. **Improve documentation** - Help future users
3. **Submit pull requests** - Contribute code improvements
4. **Help on forum** - Answer questions from other users

---

## Version Information

**Target ArduPilot Version:** Plane 4.5.7
**Git Tag:** Plane-4.5.7
**Commit:** 0358a9c210bc6c965006f5d6029239b7033616df
**Binaries:** https://firmware.ardupilot.org/Plane/stable-4.5.7/

**Last Updated:** 2026-02-04
**Documentation Version:** 1.0

---

## Acknowledgments

This onboarding environment was created to help new engineers quickly become productive with ArduPilot Plane 4.5.7. It combines official ArduPilot documentation with practical examples and hands-on exercises.

**Resources used:**
- ArduPilot official documentation
- Community contributions
- Team experience and lessons learned

---

## License

This onboarding documentation follows the same license as ArduPilot (GPLv3). Example code and scripts are provided as-is for educational purposes.

ArduPilot is open-source software released under GPLv3: https://www.gnu.org/licenses/gpl-3.0.html

---

**Ready to start? Begin with [ArduPilot Onboarding Guide](Onboarding_Documentation/ArduPilot_Onboarding_Guide.md)!**
