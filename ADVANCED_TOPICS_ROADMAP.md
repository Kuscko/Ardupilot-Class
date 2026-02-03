# ArduPilot Advanced Topics Roadmap

This document outlines additional topics that could enhance the onboarding program beyond the current scope.

## Current Coverage

The existing onboarding covers:
- [x] Development environment setup (WSL2, Ubuntu)
- [x] Building ArduPilot from source
- [x] SITL basics and mission planning
- [x] Parameters (TECS, airspeed, throttle, failsafes)
- [x] Flight modes
- [x] Lua scripting
- [x] MAVLink protocol and communication
- [x] mavlink-router for telemetry routing
- [x] EKF fundamentals and sensor fusion
- [x] Sensor driver architecture
- [x] Basic troubleshooting

---

## Recommended Additional Topics

### 1. Flight Log Analysis ⭐⭐⭐
**Priority:** HIGH - Essential for debugging and tuning

**Topics to cover:**
- Enabling and configuring logging (LOG_* parameters)
- Downloading logs from autopilot
- Using Mission Planner log review
- Using MAVExplorer for advanced analysis
- Using UAV Log Viewer
- Common log patterns and anomalies
- Performance analysis (vibration, EKF health, sensor health)

**Deliverables:**
- Guide on enabling logging
- Sample log files with known issues
- Tutorial on analyzing TECS performance from logs
- Tutorial on identifying vibration issues
- Python script to parse logs

---

### 2. PID Tuning ⭐⭐⭐
**Priority:** HIGH - Critical for flight performance

**Topics to cover:**
- Rate controller PIDs (roll, pitch, yaw)
- Auto-tune procedure and parameters
- Manual tuning process
- Reading tuning graphs
- Common tuning issues (oscillation, sluggish response)
- SITL tuning vs real-world tuning

**Deliverables:**
- PID tuning guide
- Auto-tune procedure checklist
- Example parameter sets (conservative, aggressive, racing)
- Python script to graph PID performance from logs

---

### 3. SITL Advanced Features ⭐⭐
**Priority:** MEDIUM - Useful for advanced testing

**Topics to cover:**
- Wind simulation (`--wind` parameters)
- Sensor failure injection
- Multiple vehicle simulation
- Custom start locations and scenarios
- Replay functionality
- Frame rate and speed control

**Deliverables:**
- Advanced SITL guide
- Scripts for common test scenarios
- Wind testing mission examples
- Multi-vehicle test setup

---

### 4. Companion Computer Integration ⭐⭐⭐
**Priority:** HIGH - Common in real-world applications

**Topics to cover:**
- Serial connection setup (SERIAL parameters)
- ROS/ROS2 integration with MAVROS
- MAVSDK usage
- DroneKit-Python
- Offboard control modes
- Computer vision integration
- Obstacle avoidance

**Deliverables:**
- Companion computer setup guide
- ROS MAVROS examples
- MAVSDK example applications
- DroneKit mission scripts

---

### 5. Hardware-in-the-Loop (HITL) Testing ⭐⭐
**Priority:** MEDIUM - Bridge between SITL and real flights

**Topics to cover:**
- HITL setup with flight controller
- Connecting HITL to simulator
- Testing real sensors with simulated dynamics
- Common HITL issues

**Deliverables:**
- HITL setup guide
- Connection diagrams
- Troubleshooting checklist

---

### 6. RC Calibration and Setup ⭐⭐
**Priority:** MEDIUM - Essential for real hardware

**Topics to cover:**
- RC receiver types and protocols
- Channel mapping (RCMAP_* parameters)
- RC calibration procedure
- Failsafe RC setup
- Mode switches and auxiliary functions
- Transmitter mixing

**Deliverables:**
- RC setup guide
- Calibration checklist
- Common RC parameter sets
- Transmitter configuration examples

---

### 7. Custom MAVLink Messages ⭐
**Priority:** LOW - Advanced feature

**Topics to cover:**
- MAVLink message definition (.xml files)
- Generating code from definitions
- Sending custom messages from Lua
- Receiving custom messages in Python
- Adding messages to ArduPilot

**Deliverables:**
- Custom message tutorial
- Example message definition
- Example Lua sender
- Example Python receiver

---

### 8. Safety and Geofencing Deep Dive ⭐⭐
**Priority:** MEDIUM - Important for operations

**Topics to cover:**
- Geofence types (circular, polygon, altitude)
- Geofence actions and recovery
- Rally points
- Terrain following
- Parachute and emergency systems
- Pre-arm safety checks

**Deliverables:**
- Safety systems guide
- Geofence configuration examples
- Rally point mission examples
- Safety checklist

---

### 9. Navigation Deep Dive ⭐⭐
**Priority:** MEDIUM - Advanced flight control

**Topics to cover:**
- L1 controller in detail
- NAVL1_* parameters
- Path planning algorithms
- Waypoint navigation precision
- Speed and altitude transitions
- DO_JUMP and conditional waypoints

**Deliverables:**
- L1 controller guide
- Navigation tuning examples
- Advanced mission examples (complex patterns)

---

### 10. Payload Integration ⭐⭐
**Priority:** MEDIUM - Practical applications

**Topics to cover:**
- Camera triggering (DO_DIGICAM_CONTROL)
- Servo control for payloads
- Relay control
- PWM output configuration
- Gimbal control
- Payload release mechanisms

**Deliverables:**
- Payload integration guide
- Camera trigger mission examples
- Servo control Lua scripts
- Gimbal parameter sets

---

### 11. Testing and CI/CD ⭐
**Priority:** LOW - For contributors

**Topics to cover:**
- autotest framework
- Writing simulation tests
- Unit tests in ArduPilot
- GitHub CI/CD workflows
- Pre-commit hooks
- Test coverage

**Deliverables:**
- Testing guide
- Example autotest
- CI/CD setup guide

---

### 12. Telemetry Radio Setup ⭐⭐
**Priority:** MEDIUM - Hardware setup

**Topics to cover:**
- SiK radio configuration
- Radio firmware updates
- Range testing
- Power settings
- Frequency selection
- Troubleshooting link quality

**Deliverables:**
- Telemetry radio guide
- Configuration utility scripts
- Range test procedures

---

### 13. OSD Configuration ⭐
**Priority:** LOW - Nice-to-have feature

**Topics to cover:**
- OSD parameter setup
- Screen layouts
- Font customization
- Video format (NTSC/PAL)
- Warnings and alerts on OSD

**Deliverables:**
- OSD setup guide
- Example screen layouts

---

### 14. Custom Build Configurations ⭐
**Priority:** LOW - Advanced development

**Topics to cover:**
- Board definitions (hwdef.dat)
- Feature enable/disable (AP_* defines)
- Build optimization
- Custom bootloaders
- Flash size management

**Deliverables:**
- Build configuration guide
- Custom board example

---

### 15. Debugging Tools and Techniques ⭐
**Priority:** LOW - Advanced troubleshooting

**Topics to cover:**
- GDB debugging in SITL
- Using gdbserver with hardware
- Valgrind for memory issues
- Address sanitizer (ASAN)
- Printf debugging
- Serial console debugging

**Deliverables:**
- Debugging guide
- GDB command reference
- Example debugging session

---

### 16. Code Contribution Workflow ⭐
**Priority:** LOW - For contributors

**Topics to cover:**
- Fork and branch workflow
- Code style and conventions
- Writing commit messages
- Creating pull requests
- Code review process
- Documentation requirements

**Deliverables:**
- Contribution guide
- PR template
- Code style checklist

---

### 17. Performance Optimization ⭐
**Priority:** LOW - Advanced topic

**Topics to cover:**
- CPU usage monitoring
- Scheduler analysis
- Memory usage
- Loop timing
- Profiling tools
- Optimization techniques

**Deliverables:**
- Performance guide
- Profiling examples

---

## Implementation Priority

### Phase 1 (Most Critical)
1. Flight Log Analysis
2. PID Tuning
3. Companion Computer Integration

### Phase 2 (Important)
1. RC Calibration and Setup
2. Safety and Geofencing
3. SITL Advanced Features
4. Navigation Deep Dive
5. Payload Integration
6. Telemetry Radio Setup

### Phase 3 (Advanced/Optional)
1. Hardware-in-the-Loop
2. Custom MAVLink Messages
3. OSD Configuration
4. Testing and CI/CD
5. Debugging Tools
6. Code Contribution Workflow
7. Custom Build Configurations
8. Performance Optimization

---

## Quick Reference: What's Missing

### For Operators (Real Flight Operations)
- [ ] Flight log analysis and debugging
- [ ] PID tuning procedures
- [ ] RC calibration
- [ ] Telemetry radio setup
- [ ] Safety systems configuration
- [ ] Payload integration

### For Developers (Code Development)
- [ ] Testing framework
- [ ] Debugging tools
- [ ] Code contribution workflow
- [ ] Custom build configurations

### For Advanced Users
- [ ] Companion computer integration
- [ ] HITL testing
- [ ] Custom MAVLink messages
- [ ] Advanced navigation
- [ ] Performance optimization

---

## How to Expand This Training

### Option 1: Dedicated Modules
Create separate folders for each advanced topic:
```
Advanced_Topics/
├── Flight_Log_Analysis/
├── PID_Tuning/
├── Companion_Computer/
└── ...
```

### Option 2: Advanced Track
Create an "Advanced Onboarding" track that builds on the current foundation.

### Option 3: Specialization Paths
Create different paths:
- **Operations Track**: Logs, PID tuning, RC setup, safety
- **Developer Track**: Testing, debugging, contributions
- **Integration Track**: Companion computer, payloads, custom messages

---

## Suggested Next Steps

1. **Phase 1 Priority**: Add Flight Log Analysis module
   - Most requested topic from new engineers
   - Essential for debugging
   - Builds on existing knowledge

2. **Phase 2**: Add PID Tuning module
   - Critical for performance
   - Natural progression from TECS tuning

3. **Phase 3**: Add Companion Computer module
   - Increasingly common requirement
   - Opens up advanced applications

---

**Author:** Patrick Kelly (@Kuscko)
**Version:** 1.0
**Last Updated:** 2026-02-03
