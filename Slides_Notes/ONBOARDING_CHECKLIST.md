# ArduPilot Onboarding Checklist

Use this checklist to track your progress through the onboarding process.

---

## Week 1: Foundation and Environment Setup

### Days 1-2: Development Environment and SITL

- [ ] Install WSL2 on Windows
- [ ] Install Ubuntu 22.04 LTS in WSL
- [ ] Update system packages (`sudo apt update && sudo apt upgrade`)
- [ ] Install git, python3, python3-pip
- [ ] Clone ArduPilot repository to `~/ardupilot`
- [ ] Checkout Plane 4.5.7 tag
- [ ] Update git submodules
- [ ] Run `install-prereqs-ubuntu.sh`
- [ ] Install pymavlink and mavproxy
- [ ] Build ArduPlane for SITL
- [ ] Start SITL successfully
- [ ] Verify three windows open (command, console, map)
- [ ] Wait for GPS lock in SITL
- [ ] Complete first simulated flight in FBWA
- [ ] Take screenshot of running SITL

**Checkpoint:** Can you start SITL and fly in FBWA mode?

---

### Days 3-4: TECS and Parameter Deep Dive

- [ ] View parameters with `param show TECS_*`
- [ ] Set a parameter with `param set`
- [ ] Save parameters to file
- [ ] Load parameters from file
- [ ] Understand TECS parameters:
  - [ ] TECS_TIME_CONST
  - [ ] TECS_CLMB_MAX
  - [ ] TECS_SINK_MAX
  - [ ] TECS_SPDWEIGHT
- [ ] Modify TECS parameters in SITL
- [ ] Test flight with modified parameters
- [ ] Observe effect on climb/descent
- [ ] Configure serial port parameters
- [ ] Understand parameter naming convention

**Checkpoint:** Can you modify and test TECS parameters?

---

### Day 5: Failsafe Configuration

- [ ] Configure RC failsafe (FS_SHORT_ACTN, FS_LONG_ACTN)
- [ ] Configure battery failsafe (BATT_LOW_VOLT, BATT_CRT_VOLT)
- [ ] Configure geofence (FENCE_ENABLE, FENCE_RADIUS, FENCE_ALT_MAX)
- [ ] Test RTL mode manually
- [ ] Understand failsafe trigger conditions
- [ ] Review failsafe documentation

**Checkpoint:** Do you understand how failsafes protect the aircraft?

---

## Week 2: Advanced Topics

### Days 6-7: Building ArduPilot and Code Structure

- [ ] Build ArduPlane for SITL using waf
- [ ] Build for hardware target (e.g., CubeOrangePlus)
- [ ] List available boards with `./waf list_boards`
- [ ] Clean and rebuild
- [ ] Navigate ArduPilot directory structure
- [ ] Locate key libraries:
  - [ ] AP_AHRS
  - [ ] AP_NavEKF3
  - [ ] AP_GPS
  - [ ] AP_InertialSensor
  - [ ] AP_Baro
  - [ ] AP_Compass
- [ ] Understand front-end/back-end sensor architecture
- [ ] Review ArduPlane vehicle code structure
- [ ] Find where flight modes are implemented

**Checkpoint:** Can you build ArduPilot and navigate the codebase?

---

### Days 8-9: MAVLink Communication

- [ ] Understand MAVLink message structure
- [ ] List essential MAVLink messages:
  - [ ] HEARTBEAT (0)
  - [ ] ATTITUDE (30)
  - [ ] GLOBAL_POSITION_INT (33)
  - [ ] VFR_HUD (74)
  - [ ] SYS_STATUS (1)
- [ ] Connect to SITL with pymavlink
- [ ] Read telemetry messages in Python
- [ ] Send command to autopilot
- [ ] Arm/disarm vehicle via MAVLink
- [ ] Understand system ID and component ID
- [ ] Review MAVLink common messages documentation
- [ ] Install mavlink-router (optional)
- [ ] Configure mavlink-router for multiple endpoints
- [ ] Test routing SITL to multiple GCS applications

**Checkpoint:** Can you read telemetry and send commands via MAVLink?

---

### Day 10: Lua Scripting

- [ ] Enable Lua scripting (`SCR_ENABLE = 1`)
- [ ] Restart SITL to create scripts/ directory
- [ ] Create hello_world.lua script
- [ ] Test hello_world script in SITL
- [ ] Create altitude_monitor.lua script
- [ ] Set SCR_USER1 parameter
- [ ] Test altitude warning in SITL
- [ ] Understand Lua API functions:
  - [ ] gcs:send_text()
  - [ ] ahrs:get_location()
  - [ ] battery:voltage()
  - [ ] param:get/set()
  - [ ] vehicle:set_mode()
- [ ] Review example Lua scripts
- [ ] Troubleshoot Lua script loading issues

**Checkpoint:** Can you create and run custom Lua scripts?

---

## Additional Topics

### SITL Mission Planning

- [ ] Create simple waypoint mission
- [ ] Load mission with `wp load`
- [ ] List waypoints with `wp list`
- [ ] Execute mission in AUTO mode
- [ ] Understand mission file format
- [ ] Use common mission commands:
  - [ ] NAV_WAYPOINT (16)
  - [ ] NAV_TAKEOFF (22)
  - [ ] NAV_LAND (21)
  - [ ] NAV_RTL (20)
- [ ] Create square pattern mission
- [ ] Create altitude test mission
- [ ] Test mission with speed changes
- [ ] Save and reload missions

**Checkpoint:** Can you create and execute custom missions?

---

### EKF Understanding

- [ ] Understand what EKF does (sensor fusion)
- [ ] List sensors used by EKF:
  - [ ] GPS
  - [ ] IMU (accelerometer + gyroscope)
  - [ ] Barometer
  - [ ] Compass
  - [ ] Airspeed (if equipped)
- [ ] Understand EKF predict + update cycle
- [ ] Review key EKF parameters:
  - [ ] EK3_ENABLE
  - [ ] EK3_GPS_HACC_MAX
  - [ ] EK3_ALT_SOURCE
- [ ] Understand EKF pre-arm checks
- [ ] Interpret EKF variance errors
- [ ] Review EKF documentation

**Checkpoint:** Do you understand how EKF fuses sensor data?

---

### Sensor Drivers

- [ ] Understand front-end/back-end architecture
- [ ] Locate sensor driver code in libraries/
- [ ] Review GPS driver (AP_GPS)
- [ ] Review IMU driver (AP_InertialSensor)
- [ ] Review barometer driver (AP_Baro)
- [ ] Review compass driver (AP_Compass)
- [ ] Understand how sensors are initialized
- [ ] Review SITL sensor simulation

**Checkpoint:** Can you find and understand sensor driver code?

---

## Onboarding Completion

### Knowledge Check

- [ ] Explain what ArduPilot is and what it does
- [ ] Describe the difference between ArduPilot and Pixhawk
- [ ] List the main ArduPilot variants
- [ ] Explain what SITL is and why we use it
- [ ] Start SITL and perform a basic flight
- [ ] Explain what parameters are and how to modify them
- [ ] Configure basic failsafes
- [ ] Create and execute a simple mission
- [ ] Write a basic Lua script
- [ ] Connect to autopilot via MAVLink with Python
- [ ] Explain what EKF does
- [ ] Locate sensor driver code in the repository
- [ ] Build ArduPlane from source

**Final Checkpoint:** Can you demonstrate competence in all core areas?

---

### Practical Exercises

Complete at least 3 of these exercises:

- [ ] **Exercise 1:** Create a mission that flies a specific pattern (triangle, figure-8, etc.)
- [ ] **Exercise 2:** Write a Lua script that monitors battery and triggers RTL at custom threshold
- [ ] **Exercise 3:** Build a Python script that logs telemetry to CSV file
- [ ] **Exercise 4:** Modify a parameter default in code, rebuild, and test
- [ ] **Exercise 5:** Configure mavlink-router to route SITL to multiple endpoints
- [ ] **Exercise 6:** Create a parameter tuning test: modify TECS, document behavior changes

---

### Documentation Review

- [ ] Read ArduPilot Onboarding Guide (main document)
- [ ] Review all README.md files in onboarding folders
- [ ] Study example mission files
- [ ] Review example Lua scripts
- [ ] Study MAVLink guide
- [ ] Review EKF fundamentals document
- [ ] Study sensor driver guide
- [ ] Review build instructions
- [ ] Study troubleshooting guide

---

### Resources Familiarity

- [ ] Bookmark ArduPilot Plane documentation
- [ ] Bookmark ArduPilot developer documentation
- [ ] Bookmark MAVLink common messages
- [ ] Join ArduPilot Discourse forum
- [ ] Join ArduPilot Discord (optional)
- [ ] Star ArduPilot GitHub repository
- [ ] Know where to find parameter reference
- [ ] Know where to find mission command reference

---

## Post-Onboarding

### Continuous Learning

- [ ] Subscribe to ArduPilot development updates
- [ ] Review monthly release notes
- [ ] Explore advanced topics:
  - [ ] PID tuning
  - [ ] Auto-tune
  - [ ] Advanced Lua scripting
  - [ ] Custom MAVLink messages
  - [ ] Flight log analysis
- [ ] Contribute to ArduPilot (optional):
  - [ ] Report bugs
  - [ ] Improve documentation
  - [ ] Submit pull requests

### Help Others

- [ ] Answer questions from new team members
- [ ] Improve onboarding documentation
- [ ] Share lessons learned
- [ ] Create additional examples/scripts

---

## Notes & Reflections

**What went well:**
-

**What was challenging:**
-

**Questions for follow-up:**
-

**Suggestions for improving onboarding:**
-

---

**Completed:** _____ / _____ / _____

**Reviewed by:** _____________________

**Last Updated:** 2026-02-03
