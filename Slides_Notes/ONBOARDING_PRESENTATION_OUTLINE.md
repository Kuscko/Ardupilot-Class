# ArduPilot Onboarding Presentation Outline

**Duration:** 2-3 hours (can be split across sessions)
**Audience:** New engineers
**Prerequisites:** Basic programming, Linux command line familiarity

---

## Session 1: ArduPilot Introduction & Environment Setup (45 min)

### Slide 1: Welcome & Overview
- Introduction to ArduPilot project
- What we'll cover in onboarding
- Resources and documentation

### Slide 2: What is ArduPilot?
- Open-source autopilot firmware
- Runs on various flight controller hardware
- Supports Plane, Copter, Rover, Sub
- **Key Point:** ArduPilot = software, Pixhawk/Cube = hardware

### Slide 3: ArduPilot Variants
- ArduPlane (our focus - Plane 4.5.7)
- ArduCopter, ArduRover, ArduSub
- Shared codebase (~80% common libraries)

### Slide 4: Aircraft Components
**Diagram:** Flight controller, sensors (GPS, compass, IMU, barometer, airspeed), outputs (servos, ESCs), communication (RC, telemetry)

### Slide 5: Key Terminology
- Parameters, flight modes, missions/waypoints, GCS, MAVLink, SITL, EKF, arming/disarming, failsafes

### Slide 6: Development Environment
- WSL2 for Linux on Windows
- Build from source for development and learning

### Slide 7: SITL
- Software-In-The-Loop simulation
- Testing without hardware
- **Demo:** Starting SITL

### Slide 8: Installation Overview
- System requirements and installation steps
- Using installation scripts

### Slide 9: First SITL Flight (Demo)
1. Start SITL
2. Wait for GPS lock
3. Switch to FBWA, arm, set throttle
4. RTL and land

### Slide 10: Questions & Hands-On
- Participants follow installation guide

---

## Session 2: Parameters & Flight Modes (45 min)

### Slide 11: Parameter System
- Naming conventions (PREFIX_NAME)
- View/set parameters, parameter persistence

### Slide 12: Critical Parameter Categories
- TECS_*, ARSPD_*, THR_*, SERIAL_*, FS_*, EK3_*

### Slide 13: TECS Deep Dive
- Total Energy Control System
- Physics: kinetic + potential energy
- Key parameters: TECS_TIME_CONST, TECS_CLMB_MAX, TECS_SINK_MAX, TECS_SPDWEIGHT

### Slide 14: Flight Modes Overview
- Manual: MANUAL, STABILIZE, ACRO
- Assisted: FBWA, FBWB, CRUISE
- Autonomous: AUTO, RTL, LOITER, GUIDED

### Slide 15: FBWA vs AUTO
- FBWA: Pilot control with stabilization
- AUTO: Follow mission waypoints

### Slide 16: Failsafe Configuration
- RC Failsafe (short/long)
- Battery Failsafe (low/critical)
- Geofence

### Slide 17: Failsafe Example
**Scenario:** RC lost at 500m → short failsafe (1.5s) → long failsafe (5s) → RTL → land

### Slide 18: Parameter Tuning Best Practices
- Backup before changes
- Change one parameter at a time
- Test in SITL first, document changes

### Slide 19: Hands-On Exercise
1. Start SITL
2. View and modify TECS_CLMB_MAX
3. Test flight, observe effect
4. Configure basic failsafe

---

## Session 3: Mission Planning & SITL Advanced (30 min)

### Slide 20: Mission Planning Basics
- Waypoints, mission file format, MAVProxy vs GCS

### Slide 21: Common Mission Commands

| Command | ID |
|---------|----|
| NAV_WAYPOINT | 16 |
| NAV_TAKEOFF | 22 |
| NAV_LAND | 21 |
| NAV_RTL | 20 |
| NAV_LOITER_TURNS | 17 |
| DO_CHANGE_SPEED | 178 |

### Slide 22: Mission Planning Demo
1. Load example square mission
2. Start AUTO mode
3. Observe aircraft, skip to waypoint

### Slide 23: SITL Advanced Features
- Custom start locations, wind simulation, failure injection, multiple vehicles

### Slide 24: Hands-On Exercise
1. Load and execute example mission
2. Add waypoints, test modified mission

---

## Session 4: Lua Scripting (30 min)

### Slide 25: Lua Scripting
- Custom behaviors without C++, rapid prototyping, payload control

### Slide 26: Lua Script Structure
```lua
function update()
    -- Your code
    gcs:send_text(6, "Hello!")
    return update, 1000
end
return update, 1000
```

### Slide 27: Common Lua API Functions
- `gcs:send_text()`, `ahrs:get_location()`, `battery:voltage()`, `param:get/set()`, `vehicle:set_mode()`

### Slide 28: Lua Demo
1. Enable scripting (`SCR_ENABLE = 1`)
2. Place hello_world.lua in scripts/
3. Restart SITL, observe messages

### Slide 29: Hands-On Exercise
1. Enable scripting
2. Load altitude_monitor.lua
3. Set SCR_USER1, fly above threshold, observe warning

---

## Session 5: MAVLink & Communication (30 min)

### Slide 30: MAVLink
- Binary communication protocol for drones
- Used by all GCS applications
- Header (system/component/message ID), payload, checksum

### Slide 31: Essential MAVLink Messages

| Message | ID | Contains |
|---------|----|----------|
| HEARTBEAT | 0 | Mode, armed state |
| ATTITUDE | 30 | Roll, pitch, yaw |
| GLOBAL_POSITION_INT | 33 | Position, velocity |
| VFR_HUD | 74 | Airspeed, alt, heading |
| SYS_STATUS | 1 | Battery, sensors |
| GPS_RAW_INT | 24 | GPS data |

### Slide 32: mavlink-router
**Diagram:** One autopilot → Mission Planner, QGroundControl, Python scripts, remote GCS

```ini
[UartEndpoint autopilot]
Device = /dev/ttyUSB0
Baud = 57600

[UdpEndpoint gcs]
Address = 127.0.0.1
Port = 14550
```

### Slide 33: Hands-On Exercise
1. Connect to SITL with pymavlink
2. Read VFR_HUD, display telemetry
3. Try arm/disarm script

---

## Session 6: EKF & Sensor Drivers (30 min)

### Slide 34: EKF
- Extended Kalman Filter — sensor fusion combining GPS, IMU, baro, compass
- Estimates position, velocity, attitude

### Slide 35: Sensor Limitations

| Sensor | Weakness |
|--------|----------|
| GPS | Slow, ~2m error |
| Accelerometer | Drifts over time |
| Barometer | Weather-sensitive |
| Compass | Magnetic interference |

### Slide 36: EKF Predict + Update
1. Predict (using IMU)
2. Update (using GPS, baro, compass)
3. Optimal estimate

### Slide 37: Key EKF Parameters
- EK3_ENABLE, EK3_GPS_HACC_MAX, EK3_ALT_SOURCE, noise parameters

### Slide 38: EKF Pre-Arm Checks
- "EKF attitude variance", "EKF velocity variance", "EKF position variance" — causes and fixes

### Slide 39: Sensor Driver Architecture
**Front-end/Back-end pattern:** Front-end = unified API; Back-ends = hardware-specific

### Slide 40: Key Sensor Libraries

```
libraries/
├── AP_GPS/
├── AP_InertialSensor/
├── AP_Baro/
├── AP_Compass/
└── AP_Airspeed/
```

---

## Session 7: Building ArduPilot & Codebase Tour (30 min)

### Slide 41: WAF Build System
```bash
./waf configure --board sitl
./waf plane
./waf clean
./waf list_boards
```

### Slide 42: Codebase Structure
```
~/ardupilot/
├── ArduPlane/        # Plane-specific
├── libraries/        # Shared code (80%)
├── Tools/            # Build tools
└── build/            # Build output
```

### Slide 43: Key Libraries
- AP_AHRS, AP_NavEKF3, GCS_MAVLink, AP_Param, AP_Mission

### Slide 44: Vehicle Code Structure
- Plane.cpp (main loop), mode_*.cpp (flight modes), commands.cpp, Parameters.cpp

### Slide 45: Build Demo
1. Modify a parameter default
2. Rebuild and test in SITL

### Slide 46: Troubleshooting Builds
- Submodule errors, building from /mnt/c/ (slow), missing dependencies

### Slide 47: Hands-On Exercise
1. Build ArduPlane for SITL and hardware target
2. Locate sensor driver code, explore vehicle code structure

---

## Session 8: Wrap-Up & Next Steps (15 min)

### Slide 48: Onboarding Recap
- ArduPilot basics, SITL, parameters, missions, Lua, MAVLink, EKF, sensors, building

### Slide 49: Recommended Learning Path

**Week 1:** Environment setup, SITL, parameters
**Week 2:** Mission planning, Lua, MAVLink
**Week 3:** EKF, codebase, building and modifying

### Slide 50: Resources
- ArduPilot docs, Discourse, Discord, GitHub, internal docs

### Slide 51: Practice Projects
1. Custom mission for local area
2. Lua script for payload release
3. Python GCS monitor tool
4. Modify parameter default and rebuild
5. Add logging to existing code

### Slide 52: Final Q&A

---

## Presentation Delivery Tips

### For Presenters
- Always have backup recordings for live demos
- Allow time for hands-on exercises
- 10-minute break every hour
- Adjust depth based on audience experience

### Recommended Tools
- **Slides:** PowerPoint, Google Slides, or reveal.js
- **Code Demos:** Live terminal with large font
- **Screen Recording:** OBS for backup demos

### Hands-On Lab Setup

**Participant prerequisites:** WSL2, Ubuntu 22.04 LTS, internet, text editor (VS Code)

**Have ready:** Installation scripts, example missions, Lua and Python examples

---

## Additional Materials

### Handouts
- Quick reference cards, parameter cheat sheets, MAVLink message reference

### Follow-Up Materials
- Recorded sessions, slide deck PDF, code examples, practice exercises with solutions

---

**Last Updated:** 2026-02-03
**Version:** 1.0
