# ArduPilot Technical Onboarding Guide

**Target Firmware:** Plane 4.5.7  
**Git Pin:** `tag Plane-4.5.7 @ commit 0358a9c210bc6c965006f5d6029239b7033616df`

---

## Scope and Version Pinning

This document targets ArduPilot Plane 4.5.7. Parameter availability, enums, and defaults can vary by vehicle type and firmware version. Always consult the parameter reference for your exact version when setting values.

| Field | Value |
|-------|-------|
| Firmware Version | Plane 4.5.7 |
| Git Tag | Plane-4.5.7 |
| Commit Hash | 0358a9c210bc6c965006f5d6029239b7033616df |
| Binaries | https://firmware.ardupilot.org/Plane/stable-4.5.7/ |
| Tags List | https://github.com/ArduPilot/ardupilot/tags |

**Recommended pinning approach:**
- Use a released tag/branch for your vehicle (e.g., Plane-4.5.7) and record the exact commit hash
- Verify the firmware build exists on the ArduPilot firmware server
- Use the version selector on parameter documentation pages to match your firmware

---

## Introduction: What is ArduPilot?

ArduPilot is open-source autopilot firmware that runs on supported flight-controller hardware. It reads sensors, estimates vehicle state, and outputs actuator commands to achieve the selected mode behavior.

When you hear 'ArduPilot,' it refers to the **software/firmware**. When you hear 'Pixhawk,' 'CubeOrange,' or 'Kakute,' those are examples of **flight controller hardware** that runs ArduPilot. The same ArduPilot code can run on many different hardware boards — this flexibility is one of its greatest strengths.

> **Reference:** ArduPilot repository: https://github.com/ArduPilot/ardupilot

### ArduPilot Variants

ArduPilot has separate firmware variants for different vehicle types that share a large common codebase (libraries) with vehicle-specific behavior in each stack:

| Variant | Vehicle Type | Key Characteristics |
|---------|--------------|---------------------|
| ArduPlane | Fixed-wing aircraft | Airspeed management, stall prevention, coordinated turns. This guide's focus. |
| ArduCopter | Multirotors | Hover capability, omnidirectional movement, different control algorithms. |
| ArduRover | Ground vehicles & boats | Surface navigation, obstacle avoidance. |
| ArduSub | Underwater vehicles | Depth control, underwater navigation. |

All variants share about 80% of their code (the 'libraries'), but each has vehicle-specific code for its unique characteristics.

> **Reference:** ArduPilot repository overview: https://github.com/ArduPilot/ardupilot

### Aircraft Components

A typical ArduPilot-based aircraft has these components:

#### Flight Controller

A circuit board containing a processor, built-in sensors (accelerometers, gyroscopes, barometer), and connection ports. ArduPilot runs on this board. Common examples: CubeOrange, Pixhawk 6X, Matek H743.

#### Sensors

| Sensor | Function | Location |
|--------|----------|----------|
| GPS | Provides latitude, longitude, altitude | External — mounted on top of aircraft |
| Compass (Magnetometer) | Determines heading direction | Often built into GPS module |
| Airspeed Sensor | Measures airflow speed over wings | External — critical for stall prevention |
| IMU | Accelerometers + gyroscopes for motion sensing | Built into flight controller |
| Barometer | Measures air pressure for altitude | Built into flight controller |

#### Outputs

| Output | Function |
|--------|----------|
| Servos | Small motors that move control surfaces (ailerons, elevator, rudder) |
| ESCs | Electronic Speed Controllers — control the main propulsion motor(s) |

#### Communication

| Component | Function |
|-----------|----------|
| RC Receiver | Receives commands from pilot's handheld transmitter for manual control |
| Telemetry Radio | Two-way link between aircraft and ground station. Sends status down; receives commands up. |

### Key Terminology

| Term | Definition |
|------|------------|
| Parameters | Configuration settings stored in the flight controller. Over 1,000 parameters control everything from turn aggressiveness to failsafe thresholds. Names like TECS_CLMB_MAX or ARSPD_FBW_MIN. |
| Flight Modes | Different autopilot control methods. MANUAL = direct pilot control. AUTO = follows mission. RTL = return to launch. FBWA = stabilized with pilot direction. |
| Mission | Sequence of commands executed in AUTO mode. Example: take off, fly to waypoint A, circle, land. |
| GCS | Ground Control Station — software (Mission Planner, QGroundControl) for mission planning, monitoring, and configuration. |
| MAVLink | Communication protocol between autopilot and GCS. Telemetry data streams as MAVLink messages. |
| SITL | Software-In-The-Loop simulation. Runs actual ArduPilot code with simulated sensors for safe testing. |
| EKF | Extended Kalman Filter — combines multiple sensor data to estimate position and orientation accurately. |
| Arming | Enabling motors. Armed = can fly. Disarmed = won't respond to throttle. Safety feature. |
| Failsafe | Automatic response to problems (lost signal → RTL, low battery → land). |

> **Reference:** Plane parameter reference (use version selector for 4.5.7): https://ardupilot.org/plane/docs/parameters.html

> **Reference:** Mission Planner: https://ardupilot.org/planner/ | QGroundControl: https://docs.qgroundcontrol.com/

---

## Week 1: Foundation and Environment Setup

### Days 1-2: Development Environment and SITL

**Goal:** Set up a working development environment where you can simulate flights, test parameters, and eventually modify code.

#### Why WSL2?

ArduPilot development is typically done in a Linux environment. On Windows, WSL2 (Windows Subsystem for Linux 2) provides a lightweight Linux environment that integrates smoothly with Windows.

**Why WSL2 over WSL1?** WSL2 has a full Linux kernel, which improves compatibility for building ArduPilot. With hundreds of thousands of lines of code, fast compilation saves hours of your time.

> ⚠️ **WARNING:** Always store and build your source code inside the WSL filesystem (your ~ home directory), NOT under /mnt/c. Building from the Windows-mounted filesystem is significantly slower due to cross-filesystem overhead.

> **Reference:** WSL file storage performance: https://askubuntu.com/questions/1485228/

#### Installation Steps

1. Open Control Panel → Programs → Turn Windows features on or off → Check 'Windows Subsystem for Linux' → OK → Restart
2. Open Microsoft Store, search 'Ubuntu 22.04 LTS', install it
3. Launch Ubuntu, create username and password when prompted
4. Run the update command shown below

#### Complete Setup Commands

Copy and paste these commands in your WSL terminal:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-pip
cd ~
git clone --recursive https://github.com/ArduPilot/ardupilot.git
cd ardupilot
git fetch --tags
git checkout Plane-4.5.7
git submodule update --init --recursive
./Tools/environment_install/install-prereqs-ubuntu.sh -y
. ~/.profile
python3 -m pip install --user --upgrade pymavlink mavproxy
```

> **Reference:** Downloading the Code: https://ardupilot.org/dev/docs/where-to-get-the-code.html

> **Reference:** Release procedures: https://ardupilot.org/dev/docs/release-procedures.html

#### Understanding SITL

**What is SITL?** SITL (Software-In-The-Loop) lets you run ArduPilot on your development machine and test modes, missions, and scripting without flight hardware. SITL can simulate environment conditions (wind) and failure modes.

**Why this matters:** When you test in SITL, you're testing the same code that runs on your aircraft. However, SITL is not identical to real flight — real sensors, aerodynamics, RF links, and actuator limits can change outcomes.

**SITL is essential for:**
- Testing missions before flying on real aircraft
- Learning how parameters affect behavior without crash risk
- Developing and debugging Lua scripts
- Testing failsafe behaviors safely
- Training new team members

> **Reference:** Using SITL: https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html

> **Reference:** SITL simulation parameters: https://ardupilot.org/dev/docs/SITL_simulation_parameters.html

#### Starting SITL

```bash
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
```

On first run, SITL builds the required binaries. Three windows appear:

| Window | Purpose |
|--------|---------|
| MAVProxy Command Prompt | Where you type commands. Shows current mode like 'MANUAL>'. |
| Console | Real-time status: mode, GPS, battery, autopilot messages. |
| Map | Satellite view with aircraft position. Right-click to add waypoints. |

> **Reference:** Plane SITL/MAVProxy tutorial: https://ardupilot.org/dev/docs/plane-sitlmavproxy-tutorial.html

#### Essential MAVProxy Commands

| Command | Example | What It Does |
|---------|---------|--------------|
| mode | `mode FBWA` | Changes flight mode |
| arm | `arm throttle` | Enables motors (aircraft can fly) |
| param show | `param show ARSPD*` | Lists parameters matching pattern |
| param set | `param set THR_MAX 80` | Changes parameter value |
| rc | `rc 3 1700` | Sets RC channel (3=throttle, 1700=70%) |
| wp list | `wp list` | Shows current mission waypoints |
| disarm | `disarm` | Disables motors |

#### Your First Simulated Flight

1. Start SITL: `Tools/autotest/sim_vehicle.py -v ArduPlane -L CMAC --console --map`
2. Wait for 'GPS: 3D Fix' in console
3. Set flight mode: `mode FBWA`
4. Arm the aircraft: `arm throttle`
5. Set throttle: `rc 3 1700` (70% throttle)
6. Watch aircraft take off on map
7. Try RTL mode: `mode RTL`
8. Disarm: `disarm`

> ✅ **CHECKPOINT:** Take a screenshot showing SITL with map, console, and command prompt visible.

---

### Days 3-4: TECS and Parameter Deep Dive

**Goal:** Learn how ArduPilot's parameter system works, with deep focus on TECS (flight control), PID tuning, and serial configuration.

#### How Parameters Work

ArduPilot behavior is configured through parameters stored on the vehicle in non-volatile memory (survives power cycles). Parameter availability, enums, and defaults can vary by vehicle type and firmware version.

**Parameter Naming Convention:** Parameters follow PREFIX_NAME pattern. The prefix indicates the system:

| Prefix | System |
|--------|--------|
| TECS_ | Total Energy Control System (altitude and airspeed) |
| ARSPD_ | Airspeed sensor settings |
| SERIAL_ | Serial port configuration |
| BATT_ | Battery monitoring |
| FS_ | Failsafe settings |
| EK3_ | EKF3 state estimation |

> **Reference:** Plane parameter reference (select version 4.5.7): https://ardupilot.org/plane/docs/parameters.html

#### Parameter Commands

```bash
param show TECS_*           # List parameters matching prefix
param show ARSPD_*          # List airspeed parameters
param show TECS_SPDWEIGHT   # Read a specific parameter
param set TECS_SPDWEIGHT 1.0  # Set a parameter
```

> ⚠️ **WARNING:** Some parameters require reboot to take effect. Check the parameter description in docs or Mission Planner. When in doubt, reboot after changing critical parameters.

#### TECS: Total Energy Control System

**What is TECS?** TECS is the algorithm controlling how your plane climbs, descends, and maintains airspeed. Poor TECS tuning leads to aircraft that oscillate, overshoot altitudes, or struggle to maintain speed.

**The Physics:** An aircraft has two types of mechanical energy:

| Energy Type | Description | Control |
|-------------|-------------|---------|
| Kinetic Energy | Energy of motion (airspeed). Faster = more kinetic energy. | Pitch trades kinetic ↔ potential |
| Potential Energy | Energy of height (altitude). Higher = more potential energy. | Throttle adds total energy |

These convert into each other. Pitch down: lose altitude but gain airspeed. Pitch up without throttle: climb but slow down. TECS manages both together.

#### Critical TECS Parameters

| Parameter | Function | Tuning Guidance |
|-----------|----------|-----------------|
| TECS_TIME_CONST | Response speed | Higher = slower, smoother. Try 7-10 if altitude oscillates. Default 5.0 |
| TECS_CLMB_MAX | Max climb rate (m/s) | Measure at full throttle, max pitch. Set to 80-90% of measured. |
| TECS_SINK_MAX | Max descent rate (m/s) | Set to rate achievable without exceeding max airspeed. |
| TECS_THR_DAMP | Throttle damping | Increase if speed/altitude oscillates. Requires airspeed sensor. |
| TECS_SPDWEIGHT | Energy distribution | 0 = pitch controls altitude. 2 = pitch controls speed. 1 = balanced. |

#### Serial Port Configuration

**What are serial ports?** Communication channels (UARTs) on the flight controller. GPS, telemetry radios, and companion computers connect through these.

| Parameter | Function | Common Values |
|-----------|----------|---------------|
| SERIALn_PROTOCOL | What's connected | 1/2 = MAVLink, 5 = GPS, 9 = Rangefinder, 28 = Scripting |
| SERIALn_BAUD | Speed | 57 = 57600, 115 = 115200, 921 = 921600 |
| SERIALn_OPTIONS | Special settings | Usually leave at 0 |

> **Reference:** Telemetry/Serial Setup: https://ardupilot.org/plane/docs/common-telemetry-port-setup.html

> **Reference:** Serial Port Options: https://ardupilot.org/plane/docs/common-serial-options.html

**Example — telemetry radio on Serial 1:**

```bash
param set SERIAL1_PROTOCOL 2   # MAVLink2
param set SERIAL1_BAUD 57      # 57600 baud
```

---

### Day 5: Failsafe Configuration

**Goal:** Understand and configure safety systems protecting your aircraft when things go wrong.

#### Why Failsafes Matter

Plane failsafes handle loss of RC input, loss of GCS link, low battery, and other fault conditions. Without them, a lost aircraft could fly away until battery dies, enter uncontrolled flight, continue into restricted airspace, or crash after battery voltage drops too low.

> **Reference:** Plane failsafe documentation: https://ardupilot.org/plane/docs/apms-failsafe-function.html

#### RC Failsafe

**Triggers when:** Pilot's transmitter signal lost (out of range, transmitter battery dies, interference).

| Stage | Parameter | Timeout | Purpose |
|-------|-----------|---------|---------|
| Short Failsafe | FS_SHORT_ACTN | 1.5s default | Might be momentary glitch. Options: 0=nothing, 1=RTL, 2=FBWA |
| Long Failsafe | FS_LONG_ACTN | 5s default | Definitely lost contact. Options: 0=nothing, 1=RTL, 2=Land |

| Parameter | Function |
|-----------|----------|
| THR_FAILSAFE | RC throttle failsafe enable/disable (see parameter reference for enum values) |
| THR_FS_VALUE | RC throttle failsafe threshold (confirm correct value for your RC receiver) |

#### Battery Failsafe

**Triggers when:** Voltage or remaining capacity drops below threshold.

| Level | Voltage Parameter | Capacity Parameter | Typical Action |
|-------|-------------------|-------------------|----------------|
| Low Battery | BATT_LOW_VOLT | BATT_LOW_MAH | Warning — typically triggers RTL |
| Critical Battery | BATT_CRT_VOLT | BATT_CRT_MAH | Emergency — forces immediate landing |

For 4S LiPo (nominal 14.8V): Low ~14.0V, Critical ~13.2V

#### Geofence

**What is it?** Virtual boundary aircraft cannot cross. If breached, failsafe triggers. Do not rely on generic enum lists; confirm values for your firmware version.

| Type | Parameter | Description |
|------|-----------|-------------|
| Circular | FENCE_RADIUS | Maximum distance from home |
| Altitude Ceiling | FENCE_ALT_MAX | Maximum altitude |
| Altitude Floor | FENCE_ALT_MIN | Minimum altitude |
| Breach Action | FENCE_ACTION | Response to breach (see docs for enum values) |

> **Reference:** Geo-Fencing in Plane: https://ardupilot.org/plane/docs/geofencing.html

> **Reference:** AC_Fence.cpp source: https://github.com/ArduPilot/ardupilot/blob/master/libraries/AC_Fence/AC_Fence.cpp

---

## Week 2: Advanced Topics

### Days 6-7: Building ArduPilot and Code Structure

#### Building with WAF

**What is WAF?** A build system that compiles source code into firmware. Handles complexity of building for many hardware targets.

```bash
./waf configure --board sitl            # Configure for simulation
./waf plane                             # Build ArduPlane
./waf configure --board CubeOrangePlus  # For real hardware
```

| Build Type | Output Location |
|------------|-----------------|
| SITL | build/sitl/bin/arduplane |
| Hardware | build/BOARDNAME/bin/arduplane.apj |

#### Codebase Structure

~700,000 lines of C++. Key directories:

| Directory | Contents | Size |
|-----------|----------|------|
| ArduPlane/, ArduCopter/, etc. | Vehicle-specific code | Relatively small |
| libraries/ | Shared code across all vehicles | ~80% of codebase |

#### Key Libraries

| Library | Function |
|---------|----------|
| AP_AHRS | Attitude/Heading Reference System — orientation estimate |
| AP_NavEKF3 | Extended Kalman Filter — fuses sensor data |
| AP_GPS, AP_Baro, AP_Compass | Sensor drivers |
| AP_Param | Parameter system |
| GCS_MAVLink | MAVLink communication |

#### Sensor Driver Architecture

**Front-end/Back-end Pattern:**

| Layer | Function | Benefit |
|-------|----------|---------|
| Front-end | Public interface for vehicle code | Doesn't need to know which hardware is connected |
| Back-end | Hardware-specific code for each sensor model | Adding new hardware only requires new back-end |

#### EKF Basics

**What problem does EKF solve?** Multiple sensors with different characteristics need to be combined optimally:

| Sensor | Strength | Weakness |
|--------|----------|----------|
| GPS | Absolute position | Slow (5-20 Hz), ~2m error |
| Accelerometer | Very fast (400+ Hz) | Drifts over time |
| Barometer | Good for relative altitude | Affected by weather |
| Compass | Heading reference | Affected by magnetic interference |

EKF combines all sensors, weighting each by expected accuracy. Result is better than any single sensor.

---

### Days 8-9: MAVLink Communication

#### What is MAVLink?

MAVLink (Micro Air Vehicle Link) is the messaging protocol used between the autopilot, ground station, and companion computers. Message IDs and fields are defined in MAVLink XML message sets (e.g., common.xml). Any MAVLink-compatible GCS works with any MAVLink-compatible autopilot.

#### Message Structure

| Field | Range | Purpose |
|-------|-------|---------|
| System ID | 1-255 | Identifies sender. Each aircraft has unique ID. |
| Component ID | 1-255 | Which component. Autopilot=1, Camera=100. |
| Message ID | Varies | Message type. HEARTBEAT=0, ATTITUDE=30. |
| Payload | Variable | The actual data. |

> **Reference:** MAVLink common messages: https://mavlink.io/en/messages/common.html

> **Reference:** ArduPilot MAVLink basics: https://ardupilot.org/dev/docs/mavlink-basics.html

#### Essential Messages

| Message | ID | Contents |
|---------|-----|----------|
| HEARTBEAT | 0 | Periodic heartbeat. Contains mode, armed state. |
| ATTITUDE | 30 | Roll, pitch, yaw angles and rates. |
| GLOBAL_POSITION_INT | 33 | EKF-filtered position and velocity. |
| VFR_HUD | 74 | Airspeed, groundspeed, heading, throttle, altitude. |
| SYS_STATUS | 1 | Battery voltage/current, sensor health. |

#### mavlink-router

**What is it?** mavlink-router routes MAVLink packets between endpoints (serial, UDP, TCP), enabling multiple consumers of telemetry.

Example: Aircraft with Raspberry Pi companion. Autopilot connects to Pi via serial. You want Mission Planner on laptop, QGroundControl on tablet, and Python script on Pi — all receiving telemetry. mavlink-router handles this.

> **Reference:** mavlink-router: https://github.com/mavlink-router/mavlink-router

**Config example (/etc/mavlink-router/main.conf):**

```ini
[UartEndpoint autopilot]
Device = /dev/ttyUSB0
Baud = 921600

[UdpEndpoint gcs]
Mode = Normal
Address = 192.168.1.100
Port = 14550
```

---

### Day 10: Lua Scripting

#### What is Lua Scripting?

Lua is a lightweight programming language. ArduPilot includes a Lua interpreter running scripts alongside main flight code. Add custom behaviors without modifying C++ source.

#### Lua Script Capabilities

| Capability | Examples |
|------------|----------|
| Read sensor data | GPS position, attitude, battery voltage |
| Read/modify parameters | Get and set any parameter |
| Control outputs | Servos and motors |
| Change modes | Switch flight modes programmatically |
| Send messages | Display info on GCS |

**Example uses:** Payload release at coordinates, custom battery alerts, aerobatic maneuvers, automated pre-flight checks.

#### Script Structure

Every script follows this pattern:

```lua
-- my_script.lua
function update()
    -- Your code here
    gcs:send_text(6, 'Hello!')
    return update, 1000  -- Call again in 1000ms
end
return update, 1000  -- Start the script
```

Key points: Script returns function and interval (milliseconds). Function called repeatedly. gcs:send_text() sends messages (6 = info level).

#### Running Scripts in SITL

1. Enable scripting: `param set SCR_ENABLE 1`
2. Restart SITL (creates scripts/ directory)
3. Place .lua files in scripts/ directory
4. Restart SITL again to load scripts
5. Watch console for script output

#### Common API Functions

| Function | Purpose |
|----------|---------|
| gcs:send_text(level, msg) | Send message to GCS |
| ahrs:get_location() | Get current position |
| battery:voltage(0) | Get battery voltage |
| param:get('NAME') | Read parameter value |
| param:set('NAME', value) | Set parameter value |
| vehicle:set_mode(num) | Change flight mode |

> ✅ **EXERCISE:** Create a Lua script monitoring altitude. When above SCR_USER1 parameter value, send warning to GCS. Test in SITL.

---

## Appendix A: Essential Parameters

Always verify parameter availability and defaults for your specific firmware version.

> **Reference:** Plane parameter reference: https://ardupilot.org/plane/docs/parameters.html

### Airspeed Parameters

| Parameter | Function | Notes |
|-----------|----------|-------|
| ARSPD_TYPE | Sensor type | 0=none, 1=analog, 2=MS4525 |
| ARSPD_FBW_MIN | Minimum airspeed in auto modes | m/s |
| ARSPD_FBW_MAX | Maximum airspeed in auto modes | m/s |
| TRIM_ARSPD_CM | Target cruise airspeed | cm/s |

### Throttle Parameters

| Parameter | Function | Notes |
|-----------|----------|-------|
| THR_MAX | Maximum throttle | Percentage |
| THR_MIN | Minimum throttle | Percentage |
| TRIM_THROTTLE | Cruise throttle | Percentage |
| THR_SLEWRATE | Max throttle change rate | Per second |

### Limit Parameters

| Parameter | Function | Notes |
|-----------|----------|-------|
| LIM_PITCH_MAX | Maximum pitch angle | Centidegrees |
| LIM_PITCH_MIN | Minimum pitch angle | Centidegrees |
| LIM_ROLL_CD | Maximum roll angle | Centidegrees |

### Navigation Parameters

| Parameter | Function | Notes |
|-----------|----------|-------|
| NAVL1_PERIOD | Turn tightness | Lower = tighter turns |
| WP_RADIUS | Waypoint acceptance radius | Meters |
| WP_LOITER_RAD | Default loiter radius | Meters |

---

## Appendix B: Troubleshooting

### SITL Won't Start

| Problem | Solution |
|---------|----------|
| Wrong directory | `cd ~/ardupilot/ArduPlane` |
| Build issues | `./waf distclean` then rebuild |
| Windows display issues | Check X server is running (VcXsrv or similar) |

### Build Failures

| Problem | Solution |
|---------|----------|
| Missing submodules | `git submodule update --init --recursive` |
| Missing dependencies | Re-run `install-prereqs-ubuntu.sh` |
| Slow builds | Build in WSL filesystem (~), NOT /mnt/c/ |

> ⚠️ **WARNING:** Always build in WSL filesystem (~), NOT /mnt/c/ — cross-filesystem builds are significantly slower.

### Can't Arm

| Problem | Solution |
|---------|----------|
| PreArm failures | Check console for 'PreArm' messages explaining why |
| GPS not locked | Wait for '3D Fix' message |
| Compass not calibrated | Run compass calibration in GCS |
| Accelerometer not calibrated | Run accelerometer calibration in GCS |

### Lua Scripts Not Loading

| Problem | Solution |
|---------|----------|
| Scripting disabled | `param set SCR_ENABLE 1`, then restart |
| Wrong directory | Place scripts in scripts/ directory |
| Memory errors | Increase SCR_HEAP_SIZE |

---

## Appendix C: Complete Reference Links

### Version-Pinned References (Plane 4.5.7)

| Resource | URL |
|----------|-----|
| Git Tag | Plane-4.5.7 @ commit 0358a9c210bc6c965006f5d6029239b7033616df |
| ArduPilot Tags | https://github.com/ArduPilot/ardupilot/tags |
| Plane 4.5.7 Binaries | https://firmware.ardupilot.org/Plane/stable-4.5.7/ |
| Parameter Reference | https://ardupilot.org/plane/docs/parameters.html |

### Development & SITL

| Resource | URL |
|----------|-----|
| ArduPilot Repository | https://github.com/ArduPilot/ardupilot |
| Getting the Code | https://ardupilot.org/dev/docs/where-to-get-the-code.html |
| Release Procedures | https://ardupilot.org/dev/docs/release-procedures.html |
| Using SITL | https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html |
| SITL Parameters | https://ardupilot.org/dev/docs/SITL_simulation_parameters.html |
| SITL/MAVProxy Tutorial | https://ardupilot.org/dev/docs/plane-sitlmavproxy-tutorial.html |
| WSL Performance | https://askubuntu.com/questions/1485228/ |

### Configuration

| Resource | URL |
|----------|-----|
| Serial Port Setup | https://ardupilot.org/plane/docs/common-telemetry-port-setup.html |
| Serial Options | https://ardupilot.org/plane/docs/common-serial-options.html |
| Failsafe Function | https://ardupilot.org/plane/docs/apms-failsafe-function.html |
| Geofencing | https://ardupilot.org/plane/docs/geofencing.html |
| AC_Fence Source | https://github.com/ArduPilot/ardupilot/blob/master/libraries/AC_Fence/AC_Fence.cpp |

### MAVLink & Communication

| Resource | URL |
|----------|-----|
| MAVLink Messages | https://mavlink.io/en/messages/common.html |
| MAVLink Basics | https://ardupilot.org/dev/docs/mavlink-basics.html |
| mavlink-router | https://github.com/mavlink-router/mavlink-router |

### Official Documentation

| Resource | URL |
|----------|-----|
| ArduPilot Plane | https://ardupilot.org/plane/ |
| Developer Docs | https://ardupilot.org/dev/ |
| MAVLink Protocol | https://mavlink.io/en/ |

### Ground Control Stations

| Resource | URL |
|----------|-----|
| Mission Planner | https://ardupilot.org/planner/ |
| QGroundControl | http://qgroundcontrol.com/ |
| QGC Parameters Guide | https://docs.qgroundcontrol.com/master/en/qgc-user-guide/setup_view/parameters.html |

### Community

| Resource | URL |
|----------|-----|
| ArduPilot Forum | https://discuss.ardupilot.org/ |
| ArduPilot Discord | https://ardupilot.org/discord |

---

*End of Guide*
