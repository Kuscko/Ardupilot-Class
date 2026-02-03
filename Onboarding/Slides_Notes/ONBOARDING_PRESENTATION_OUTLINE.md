# ArduPilot Onboarding Presentation Outline

## Presentation Structure

**Duration:** 2-3 hours (can be split across multiple sessions)

**Target Audience:** New engineers joining the team

**Prerequisites:** Basic programming knowledge, familiarity with Linux command line

---

## Session 1: ArduPilot Introduction & Environment Setup (45 min)

### Slide 1: Welcome & Overview
- Introduction to ArduPilot project
- What we'll cover in onboarding
- Resources and documentation

### Slide 2: What is ArduPilot?
- Open-source autopilot firmware
- Runs on various flight controller hardware
- Supports multiple vehicle types (Plane, Copter, Rover, Sub)
- **Key Point:** ArduPilot = software, Pixhawk/Cube = hardware

### Slide 3: ArduPilot Variants
- ArduPlane (our focus - Plane 4.5.7)
- ArduCopter
- ArduRover
- ArduSub
- Shared codebase (~80% common libraries)

### Slide 4: Aircraft Components
**Diagram showing:**
- Flight controller (brain)
- Sensors (GPS, compass, IMU, barometer, airspeed)
- Outputs (servos, ESCs)
- Communication (RC receiver, telemetry)

### Slide 5: Key Terminology
- Parameters
- Flight modes
- Missions/Waypoints
- GCS (Ground Control Station)
- MAVLink
- SITL
- EKF
- Arming/Disarming
- Failsafes

### Slide 6: Development Environment
- **Why WSL2?** Linux environment on Windows
- **Why build from source?** Development, customization, learning
- **Git workflow** for version control

### Slide 7: SITL (Software-In-The-Loop)
- What is SITL?
- Why use SITL?
- Testing without hardware
- **Demo:** Starting SITL

### Slide 8: Installation Overview
- System requirements
- Installation steps (high-level)
- Using installation scripts
- Expected installation time

### Slide 9: First SITL Flight (Demo)
**Live Demo:**
1. Start SITL
2. Wait for GPS lock
3. Switch to FBWA
4. Arm
5. Set throttle
6. Fly and observe
7. RTL and land

### Slide 10: Questions & Hands-On
- Q&A
- Participants follow installation guide
- Instructor helps with issues

---

## Session 2: Parameters & Flight Modes (45 min)

### Slide 11: Parameter System
- What are parameters?
- Naming conventions (PREFIX_NAME)
- How to view/set parameters
- Parameter persistence

### Slide 12: Critical Parameter Categories
**Table format:**
- TECS_* (altitude/speed control)
- ARSPD_* (airspeed)
- THR_* (throttle)
- SERIAL_* (communications)
- FS_* (failsafes)
- EK3_* (EKF)

### Slide 13: TECS Deep Dive
- Total Energy Control System explained
- Physics: kinetic + potential energy
- Key parameters:
  - TECS_TIME_CONST
  - TECS_CLMB_MAX
  - TECS_SINK_MAX
  - TECS_SPDWEIGHT

### Slide 14: Flight Modes Overview
**Table:**
- Manual modes (MANUAL, STABILIZE, ACRO)
- Assisted modes (FBWA, FBWB, CRUISE)
- Autonomous modes (AUTO, RTL, LOITER, GUIDED)

### Slide 15: FBWA vs AUTO
- FBWA: Pilot control with stabilization
- AUTO: Follow mission waypoints
- When to use each

### Slide 16: Failsafe Configuration
- RC Failsafe (short/long)
- Battery Failsafe (low/critical)
- Geofence
- **Importance:** Safety nets for real flights

### Slide 17: Failsafe Example
**Scenario walkthrough:**
- RC signal lost at 500m distance
- Short failsafe triggers (1.5s) → continues
- Long failsafe triggers (5s) → RTL
- Aircraft returns and lands

### Slide 18: Parameter Tuning Best Practices
- Always backup parameters before changes
- Change one parameter at a time
- Test in SITL first
- Document changes
- Some parameters require reboot

### Slide 19: Hands-On Exercise
**Participants:**
1. Start SITL
2. View TECS parameters
3. Modify TECS_CLMB_MAX
4. Test flight and observe
5. Configure basic failsafe

### Slide 20: Questions

---

## Session 3: Mission Planning & SITL Advanced (30 min)

### Slide 21: Mission Planning Basics
- Waypoints and commands
- Mission file format (MAVLink waypoint protocol)
- Creating missions in MAVProxy vs GCS

### Slide 22: Common Mission Commands
**Table:**
- NAV_WAYPOINT (16)
- NAV_TAKEOFF (22)
- NAV_LAND (21)
- NAV_RTL (20)
- NAV_LOITER_TURNS (17)
- DO_CHANGE_SPEED (178)

### Slide 23: Example Mission Walkthrough
**Show mission file:**
- Home position
- Takeoff
- Waypoint navigation
- Loiter
- RTL

### Slide 24: Mission Planning Demo
**Live demo:**
1. Load example square mission
2. Review waypoints
3. Start AUTO mode
4. Observe aircraft follow mission
5. Skip to waypoint

### Slide 25: SITL Advanced Features
- Custom start locations
- Wind simulation
- Failure injection
- Multiple vehicles

### Slide 26: Hands-On Exercise
**Participants:**
1. Load example mission
2. Execute in AUTO mode
3. Modify mission (add waypoints)
4. Test modified mission

---

## Session 4: Lua Scripting (30 min)

### Slide 27: Why Lua Scripting?
- Add custom behaviors without C++
- Rapid prototyping
- Payload control
- Custom logic

### Slide 28: Lua Capabilities
- Read sensor data
- Read/modify parameters
- Control servos
- Change modes
- Send GCS messages

### Slide 29: Lua Script Structure
**Code example:**
```lua
function update()
    -- Your code
    gcs:send_text(6, "Hello!")
    return update, 1000
end
return update, 1000
```

### Slide 30: Common Lua API Functions
- `gcs:send_text()` - Send message
- `ahrs:get_location()` - Get position
- `battery:voltage()` - Battery status
- `param:get/set()` - Parameters
- `vehicle:set_mode()` - Change mode

### Slide 31: Example Scripts
1. Hello World
2. Altitude monitor
3. Battery monitor
4. Auto mode switch
5. Waypoint logger

### Slide 32: Lua Demo
**Live demo:**
1. Enable scripting
2. Place hello_world.lua in scripts/
3. Restart SITL
4. Observe messages

### Slide 33: Hands-On Exercise
**Participants:**
1. Enable Lua scripting
2. Load altitude_monitor.lua
3. Set SCR_USER1 parameter
4. Fly above threshold
5. Observe warning

---

## Session 5: MAVLink & Communication (30 min)

### Slide 34: What is MAVLink?
- Micro Air Vehicle Link protocol
- Communication standard for drones
- Binary protocol (efficient)
- Used by all GCS applications

### Slide 35: MAVLink Message Structure
**Diagram:**
- Header (system ID, component ID, message ID)
- Payload (message data)
- Checksum
- Signature (v2 only)

### Slide 36: Essential MAVLink Messages
**Table:**
- HEARTBEAT (0)
- ATTITUDE (30)
- GLOBAL_POSITION_INT (33)
- VFR_HUD (74)
- SYS_STATUS (1)
- GPS_RAW_INT (24)

### Slide 37: mavlink-router Purpose
**Diagram:** One autopilot → many endpoints
- Mission Planner
- QGroundControl
- Python scripts
- Remote GCS

### Slide 38: mavlink-router Configuration
**Show example config:**
```ini
[UartEndpoint autopilot]
Device = /dev/ttyUSB0
Baud = 57600

[UdpEndpoint gcs]
Address = 127.0.0.1
Port = 14550
```

### Slide 39: Python MAVLink Examples
**Code snippets:**
- Connect to autopilot
- Read telemetry
- Send commands
- Arm/disarm

### Slide 40: Hands-On Exercise
**Participants:**
1. Connect to SITL with pymavlink
2. Read VFR_HUD messages
3. Display telemetry
4. Try arm/disarm script

---

## Session 6: EKF & Sensor Drivers (30 min)

### Slide 41: What is the EKF?
- Extended Kalman Filter
- Sensor fusion algorithm
- Combines all sensors for best estimate
- Estimates position, velocity, attitude

### Slide 42: Why Sensor Fusion?
**Table showing sensor limitations:**
- GPS: slow, ~2m error
- Accelerometer: fast, but drifts
- Barometer: affected by weather
- Compass: magnetic interference

### Slide 43: EKF Predict + Update Cycle
**Diagram:**
1. Prediction (using IMU)
2. Update (using GPS, baro, compass)
3. Optimal estimate

### Slide 44: EKF Parameters
- EK3_ENABLE
- EK3_GPS_HACC_MAX
- EK3_ALT_SOURCE
- Noise parameters (trust levels)

### Slide 45: EKF Pre-Arm Checks
**Common errors:**
- "EKF attitude variance"
- "EKF velocity variance"
- "EKF position variance"
- How to resolve

### Slide 46: Sensor Driver Architecture
**Diagram: Front-end/Back-end pattern**
- Front-end: unified API
- Back-ends: hardware-specific

### Slide 47: Key Sensor Libraries
- AP_GPS (GPS drivers)
- AP_InertialSensor (IMU)
- AP_Baro (barometer)
- AP_Compass (magnetometer)
- AP_Airspeed (airspeed sensor)

### Slide 48: Sensor Code Locations
**Directory tree:**
```
libraries/
├── AP_GPS/
├── AP_InertialSensor/
├── AP_Baro/
├── AP_Compass/
└── AP_Airspeed/
```

### Slide 49: Questions

---

## Session 7: Building ArduPilot & Codebase Tour (30 min)

### Slide 50: Why Build from Source?
- Custom modifications
- Bug fixes
- Learning
- Contributing to project

### Slide 51: WAF Build System
- Configuration: `./waf configure --board sitl`
- Build: `./waf plane`
- Clean: `./waf clean`
- List boards: `./waf list_boards`

### Slide 52: Codebase Structure
**Directory tree:**
```
~/ardupilot/
├── ArduPlane/        # Plane-specific
├── libraries/        # Shared code (80%)
├── Tools/            # Build tools
└── build/            # Build output
```

### Slide 53: Key Libraries Tour
- AP_AHRS (attitude reference)
- AP_NavEKF3 (Kalman filter)
- GCS_MAVLink (communication)
- AP_Param (parameter system)
- AP_Mission (waypoint handling)

### Slide 54: Vehicle Code Structure
**ArduPlane example:**
- Plane.cpp (main loop)
- mode_*.cpp (flight modes)
- commands.cpp (mission commands)
- Parameters.cpp (parameter definitions)

### Slide 55: Build Demo
**Live demo:**
1. Modify simple parameter default
2. Rebuild
3. Test in SITL
4. Verify change

### Slide 56: Contributing to ArduPilot
- GitHub workflow
- Pull requests
- Code style
- Testing requirements

### Slide 57: Troubleshooting Builds
**Common issues:**
- Submodule errors
- Python package conflicts
- Building from /mnt/c/ (slow)
- Missing dependencies

### Slide 58: Hands-On Exercise
**Participants:**
1. Build ArduPlane for SITL
2. Build for hardware target (e.g., CubeOrange)
3. Locate sensor driver code
4. Explore vehicle code structure

---

## Session 8: Wrap-Up & Next Steps (15 min)

### Slide 59: Onboarding Recap
**What we covered:**
- ArduPilot basics
- SITL and testing
- Parameters and flight modes
- Mission planning
- Lua scripting
- MAVLink communication
- EKF and sensor drivers
- Building from source

### Slide 60: Onboarding Repository Tour
**Show folder structure:**
- Build instructions
- Installation scripts
- SITL mission plans
- Lua script examples
- MAVLink guides
- EKF notes
- Sensor driver docs

### Slide 61: Recommended Learning Path
**Week 1:**
- Environment setup
- SITL familiarization
- Parameter exploration

**Week 2:**
- Mission planning
- Lua scripting
- MAVLink basics

**Week 3:**
- EKF understanding
- Codebase exploration
- Building and modifying

### Slide 62: Resources
- ArduPilot documentation
- Discourse forum
- Discord
- GitHub
- Internal documentation

### Slide 63: Getting Help
- Check onboarding docs first
- Ask team members
- ArduPilot Discourse forum
- GitHub issues

### Slide 64: Practice Projects
**Suggested projects:**
1. Create custom mission for local area
2. Write Lua script for payload release
3. Build custom GCS monitor tool
4. Modify parameter default and rebuild
5. Add logging to existing code

### Slide 65: Final Q&A
- Open discussion
- Address concerns
- Schedule follow-up sessions

### Slide 66: Thank You & Contact
- Presenter contact info
- Team resources
- Next steps

---

## Presentation Delivery Tips

### For Presenters

1. **Live Demos:** Always have backup recordings in case of technical issues
2. **Pace:** Allow time for hands-on exercises
3. **Questions:** Encourage questions throughout
4. **Breaks:** 10-minute break every hour
5. **Flexibility:** Adjust depth based on audience experience

### Recommended Tools

- **Slides:** PowerPoint, Google Slides, or reveal.js
- **Code Demos:** Live terminal with large font
- **Screen Recording:** OBS for backup demos
- **Remote Sessions:** Zoom/Teams screen sharing

### Hands-On Lab Setup

**Prerequisites for participants:**
- WSL2 installed
- Ubuntu 22.04 LTS ready
- Internet access
- Text editor (VS Code recommended)

**Have ready:**
- Installation scripts
- Example mission files
- Lua script examples
- Python script examples

---

## Additional Materials

### Handouts
- Quick reference cards
- Parameter cheat sheets
- MAVLink message reference
- Troubleshooting flowcharts

### Follow-Up Materials
- Recorded sessions
- Slide deck PDF
- Code examples repository
- Practice exercises with solutions

---

**Last Updated:** 2026-02-03
**Version:** 1.0
