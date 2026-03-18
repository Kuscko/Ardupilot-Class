# ArduPilot Technical Onboarding Guide

**Target Firmware:** Plane 4.5.7
**Git Pin:** `tag Plane-4.5.7 @ commit 0358a9c210bc6c965006f5d6029239b7033616df`

---

## Scope and Version Pinning

This document targets ArduPilot Plane 4.5.7. Parameter availability, enums, and defaults can vary by vehicle type and firmware version. Always consult the parameter reference for your exact version.

| Field | Value |
|-------|-------|
| Firmware Version | Plane 4.5.7 |
| Git Tag | Plane-4.5.7 |
| Commit Hash | 0358a9c210bc6c965006f5d6029239b7033616df |
| Binaries | <https://firmware.ardupilot.org/Plane/stable-4.5.7/> |
| Tags List | <https://github.com/ArduPilot/ardupilot/tags> |

Use a released tag/branch for your vehicle (e.g., Plane-4.5.7), record the exact commit hash, and use the version selector on parameter documentation pages to match your firmware.

---

## Introduction: What is ArduPilot?

ArduPilot is open-source autopilot firmware that runs on supported flight-controller hardware. It reads sensors, estimates vehicle state, and outputs actuator commands to achieve the selected mode behavior. "ArduPilot" refers to the software/firmware; "Pixhawk," "CubeOrange," and "Kakute" are examples of flight controller hardware that runs it.

> **Reference:** <https://github.com/ArduPilot/ardupilot>

### ArduPilot Variants

| Variant | Vehicle Type | Key Characteristics |
|---------|--------------|---------------------|
| ArduPlane | Fixed-wing aircraft | Airspeed management, stall prevention, coordinated turns. This guide's focus. |
| ArduCopter | Multirotors | Hover capability, omnidirectional movement. |
| ArduRover | Ground vehicles & boats | Surface navigation, obstacle avoidance. |
| ArduSub | Underwater vehicles | Depth control, underwater navigation. |

All variants share ~80% of their code (the libraries), with vehicle-specific code for unique characteristics.

### Aircraft Components

#### Flight Controller

A circuit board containing a processor, built-in sensors (accelerometers, gyroscopes, barometer), and connection ports. Common examples: CubeOrange, Pixhawk 6X, Matek H743.

#### Sensors

| Sensor | Function | Location |
|--------|----------|----------|
| GPS | Latitude, longitude, altitude | External — top of aircraft |
| Compass (Magnetometer) | Heading direction | Often built into GPS module |
| Airspeed Sensor | Airflow speed over wings | External — critical for stall prevention |
| IMU | Accelerometers + gyroscopes | Built into flight controller |
| Barometer | Air pressure for altitude | Built into flight controller |

#### Outputs

| Output | Function                                                    |
|--------|-------------------------------------------------------------|
| Servos | Move control surfaces (ailerons, elevator, rudder)          |
| ESCs   | Electronic Speed Controllers — control propulsion motor(s)  |

#### Communication

| Component | Function |
|-----------|----------|
| RC Receiver | Receives commands from pilot's handheld transmitter |
| Telemetry Radio | Two-way link between aircraft and ground station |

### Key Terminology

| Term | Definition |
|------|------------|
| Parameters | Configuration settings stored in non-volatile memory. Over 1,000 parameters (e.g., TECS_CLMB_MAX, ARSPD_FBW_MIN). |
| Flight Modes | MANUAL = direct pilot control. AUTO = follows mission. RTL = return to launch. FBWA = stabilized with pilot direction. |
| Mission | Sequence of commands in AUTO mode (take off, fly waypoints, land). |
| GCS | Ground Control Station — Mission Planner or QGroundControl. |
| MAVLink | Communication protocol between autopilot and GCS. |
| SITL | Software-In-The-Loop simulation — runs actual ArduPilot code with simulated sensors. |
| EKF | Extended Kalman Filter — combines sensor data to estimate position and orientation. |
| Arming | Enabling motors. Armed = can fly. Disarmed = won't respond to throttle. |
| Failsafe | Automatic response to problems (lost signal → RTL, low battery → land). |

> **Reference:** <https://ardupilot.org/plane/docs/parameters.html> | Mission Planner: <https://ardupilot.org/planner/> | QGroundControl: <https://docs.qgroundcontrol.com/>

---

## Week 1: Foundation and Environment Setup

### Days 1-2: Development Environment and SITL

#### Why WSL2?

ArduPilot development is done in Linux. WSL2 provides a full Linux kernel environment on Windows with better compatibility than WSL1.

> ⚠️ **WARNING:** Always store and build source code inside the WSL filesystem (`~`), NOT under `/mnt/c`. Cross-filesystem builds are significantly slower.

> **Reference:** <https://askubuntu.com/questions/1485228/>

#### Installation Steps

1. Control Panel → Programs → Turn Windows features on or off → Check "Windows Subsystem for Linux" → OK → Restart
2. Open Microsoft Store, search "Ubuntu 22.04 LTS", install
3. Launch Ubuntu, create username and password
4. Run the setup commands below

#### Complete Setup Commands

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

> **Reference:** <https://ardupilot.org/dev/docs/where-to-get-the-code.html>

#### Understanding SITL

SITL (Software-In-The-Loop) runs ArduPilot on your development machine, simulating sensors, flight modes, and missions without hardware. You're testing the same code that runs on the aircraft. SITL is not identical to real flight — real sensors, aerodynamics, and actuator limits can change outcomes.

> **Reference:** <https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html>

#### Starting SITL

```bash
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
```

On first run, SITL builds the required binaries. Three windows appear:

| Window | Purpose |
|--------|---------|
| MAVProxy Command Prompt | Type commands. Shows current mode (e.g., `MANUAL>`). |
| Console | Real-time status: mode, GPS, battery, autopilot messages. |
| Map | Satellite view with aircraft position. Right-click to add waypoints. |

> **Reference:** <https://ardupilot.org/dev/docs/plane-sitlmavproxy-tutorial.html>

#### Essential MAVProxy Commands

| Command | Example | What It Does |
|---------|---------|--------------|
| mode | `mode FBWA` | Changes flight mode |
| arm | `arm throttle` | Enables motors |
| param show | `param show ARSPD*` | Lists parameters matching pattern |
| param set | `param set THR_MAX 80` | Changes parameter value |
| rc | `rc 3 1700` | Sets RC channel (3=throttle, 1700=70%) |
| wp list | `wp list` | Shows current mission waypoints |
| disarm | `disarm` | Disables motors |

#### Your First Simulated Flight

1. Start SITL: `Tools/autotest/sim_vehicle.py -v ArduPlane -L CMAC --console --map`
2. Wait for "GPS: 3D Fix" in console
3. `mode FBWA`
4. `arm throttle`
5. `rc 3 1700` (70% throttle)
6. Watch aircraft take off on map
7. `mode RTL`
8. `disarm`

---

### Days 3-4: TECS and Parameter Deep Dive

#### How Parameters Work

Parameters are stored in non-volatile memory (survives power cycles). They follow a `PREFIX_NAME` convention:

| Prefix | System |
|--------|--------|
| TECS_ | Total Energy Control System |
| ARSPD_ | Airspeed sensor |
| SERIAL_ | Serial port configuration |
| BATT_ | Battery monitoring |
| FS_ | Failsafe settings |
| EK3_ | EKF3 state estimation |

> **Reference:** <https://ardupilot.org/plane/docs/parameters.html>

#### Parameter Commands

```bash
param show TECS_*           # List parameters matching prefix
param show ARSPD_*          # List airspeed parameters
param show TECS_SPDWEIGHT   # Read a specific parameter
param set TECS_SPDWEIGHT 1.0  # Set a parameter
```

> ⚠️ **WARNING:** Some parameters require reboot to take effect. When in doubt, reboot after changing critical parameters.

#### TECS: Total Energy Control System

TECS controls how the plane climbs, descends, and maintains airspeed by managing total mechanical energy:

| Energy Type | Description | Control |
|-------------|-------------|---------|
| Kinetic Energy | Speed (faster = more kinetic) | Pitch trades kinetic ↔ potential |
| Potential Energy | Height (higher = more potential) | Throttle adds total energy |

#### Critical TECS Parameters

| Parameter | Function | Tuning Guidance |
|-----------|----------|-----------------|
| TECS_TIME_CONST | Response speed | Higher = slower, smoother. Try 7-10 if altitude oscillates. Default 5.0 |
| TECS_CLMB_MAX | Max climb rate (m/s) | Set to 80-90% of full-throttle measured rate |
| TECS_SINK_MAX | Max descent rate (m/s) | Set to rate achievable without exceeding max airspeed |
| TECS_THR_DAMP | Throttle damping | Increase if speed/altitude oscillates. Requires airspeed sensor. |
| TECS_SPDWEIGHT | Energy distribution | 0 = pitch controls altitude. 2 = pitch controls speed. 1 = balanced. |

#### Serial Port Configuration

| Parameter | Function | Common Values |
|-----------|----------|---------------|
| SERIALn_PROTOCOL | What's connected | 1/2 = MAVLink, 5 = GPS, 9 = Rangefinder, 28 = Scripting |
| SERIALn_BAUD | Speed | 57 = 57600, 115 = 115200, 921 = 921600 |
| SERIALn_OPTIONS | Special settings | Usually leave at 0 |

> **Reference:** <https://ardupilot.org/plane/docs/common-telemetry-port-setup.html>

**Example — telemetry radio on Serial 1:**

```bash
param set SERIAL1_PROTOCOL 2   # MAVLink2
param set SERIAL1_BAUD 57      # 57600 baud
```

---

### Day 5: Failsafe Configuration

#### RC Failsafe

Triggers when the pilot's transmitter signal is lost.

| Stage | Parameter | Timeout | Purpose |
|-------|-----------|---------|---------|
| Short Failsafe | FS_SHORT_ACTN | 1.5s default | Possible momentary glitch. Options: 0=nothing, 1=RTL, 2=FBWA |
| Long Failsafe | FS_LONG_ACTN | 5s default | Definite signal loss. Options: 0=nothing, 1=RTL, 2=Land |

| Parameter | Function |
|-----------|----------|
| THR_FAILSAFE | RC throttle failsafe enable/disable |
| THR_FS_VALUE | RC throttle failsafe threshold |

> **Reference:** <https://ardupilot.org/plane/docs/apms-failsafe-function.html>

#### Battery Failsafe

| Level | Voltage Parameter | Capacity Parameter | Typical Action |
|-------|-------------------|-------------------|----------------|
| Low Battery | BATT_LOW_VOLT | BATT_LOW_MAH | Warning — typically triggers RTL |
| Critical Battery | BATT_CRT_VOLT | BATT_CRT_MAH | Emergency — forces immediate landing |

For 4S LiPo (nominal 14.8V): Low ~14.0V, Critical ~13.2V

#### Geofence

| Type | Parameter | Description |
|------|-----------|-------------|
| Circular | FENCE_RADIUS | Maximum distance from home |
| Altitude Ceiling | FENCE_ALT_MAX | Maximum altitude |
| Altitude Floor | FENCE_ALT_MIN | Minimum altitude |
| Breach Action | FENCE_ACTION | Response to breach (see docs for enum values) |

> **Reference:** <https://ardupilot.org/plane/docs/geofencing.html>

---

## Week 2: Advanced Topics

### Days 6-7: Building ArduPilot and Code Structure

#### Building with WAF

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

~700,000 lines of C++.

| Directory | Contents |
|-----------|----------|
| ArduPlane/, ArduCopter/, etc. | Vehicle-specific code |
| libraries/ | Shared code (~80% of codebase) |

#### Key Libraries

| Library | Function |
|---------|----------|
| AP_AHRS | Attitude/Heading Reference System — orientation estimate |
| AP_NavEKF3 | Extended Kalman Filter — fuses sensor data |
| AP_GPS, AP_Baro, AP_Compass | Sensor drivers |
| AP_Param | Parameter system |
| GCS_MAVLink | MAVLink communication |

#### Sensor Driver Architecture

| Layer | Function | Benefit |
|-------|----------|---------|
| Front-end | Public interface for vehicle code | Doesn't need to know which hardware is connected |
| Back-end | Hardware-specific code per sensor model | Adding new hardware only requires a new back-end |

#### EKF Basics

| Sensor | Strength | Weakness |
|--------|----------|----------|
| GPS | Absolute position | Slow (5-20 Hz), ~2m error |
| Accelerometer | Very fast (400+ Hz) | Drifts over time |
| Barometer | Good for relative altitude | Affected by weather |
| Compass | Heading reference | Affected by magnetic interference |

EKF combines all sensors, weighting each by expected accuracy for a result better than any single sensor.

---

### Days 8-9: MAVLink Communication

#### What is MAVLink?

MAVLink (Micro Air Vehicle Link) is the messaging protocol between the autopilot, ground station, and companion computers. Message IDs and fields are defined in MAVLink XML message sets (e.g., common.xml).

#### Message Structure

| Field | Range | Purpose |
|-------|-------|---------|
| System ID | 1-255 | Identifies sender. Each aircraft has unique ID. |
| Component ID | 1-255 | Which component. Autopilot=1, Camera=100. |
| Message ID | Varies | Message type. HEARTBEAT=0, ATTITUDE=30. |
| Payload | Variable | The actual data. |

> **Reference:** <https://mavlink.io/en/messages/common.html> | <https://ardupilot.org/dev/docs/mavlink-basics.html>

#### Essential Messages

| Message | ID | Contents |
|---------|-----|----------|
| HEARTBEAT | 0 | Periodic heartbeat. Contains mode, armed state. |
| ATTITUDE | 30 | Roll, pitch, yaw angles and rates. |
| GLOBAL_POSITION_INT | 33 | EKF-filtered position and velocity. |
| VFR_HUD | 74 | Airspeed, groundspeed, heading, throttle, altitude. |
| SYS_STATUS | 1 | Battery voltage/current, sensor health. |

#### mavlink-router

mavlink-router routes MAVLink packets between endpoints (serial, UDP, TCP), enabling multiple consumers of telemetry simultaneously.

> **Reference:** <https://github.com/mavlink-router/mavlink-router>

**Config example (`/etc/mavlink-router/main.conf`):**

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

ArduPilot includes a Lua interpreter that runs scripts alongside main flight code, enabling custom behaviors without modifying C++ source.

#### Lua Script Capabilities

| Capability | Examples |
|------------|----------|
| Read sensor data | GPS position, attitude, battery voltage |
| Read/modify parameters | Get and set any parameter |
| Control outputs | Servos and motors |
| Change modes | Switch flight modes programmatically |
| Send messages | Display info on GCS |

#### Script Structure

```lua
-- my_script.lua
function update()
    -- Your code here
    gcs:send_text(6, 'Hello!')
    return update, 1000  -- Call again in 1000ms
end
return update, 1000  -- Start the script
```

The script returns a function and interval (milliseconds). `gcs:send_text()` level 6 = info.

#### Running Scripts in SITL

1. `param set SCR_ENABLE 1`
2. Restart SITL (creates `scripts/` directory)
3. Place `.lua` files in `scripts/`
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

---

## Appendix A: Essential Parameters

Always verify parameter availability and defaults for your specific firmware version.

> **Reference:** <https://ardupilot.org/plane/docs/parameters.html>

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
| Slow builds | Build in WSL filesystem (`~`), NOT `/mnt/c/` |

### Can't Arm

| Problem | Solution |
|---------|----------|
| PreArm failures | Check console for `PreArm` messages |
| GPS not locked | Wait for "3D Fix" message |
| Compass not calibrated | Run compass calibration in GCS |
| Accelerometer not calibrated | Run accelerometer calibration in GCS |

### Lua Scripts Not Loading

| Problem | Solution |
|---------|----------|
| Scripting disabled | `param set SCR_ENABLE 1`, then restart |
| Wrong directory | Place scripts in `scripts/` directory |
| Memory errors | Increase `SCR_HEAP_SIZE` |

---

## Appendix C: Complete Reference Links

### Version-Pinned References (Plane 4.5.7)

| Resource | URL |
|----------|-----|
| Git Tag | Plane-4.5.7 @ commit 0358a9c210bc6c965006f5d6029239b7033616df |
| ArduPilot Tags | <https://github.com/ArduPilot/ardupilot/tags> |
| Plane 4.5.7 Binaries | <https://firmware.ardupilot.org/Plane/stable-4.5.7/> |
| Parameter Reference | <https://ardupilot.org/plane/docs/parameters.html> |

### Development & SITL

| Resource | URL |
|----------|-----|
| ArduPilot Repository | <https://github.com/ArduPilot/ardupilot> |
| Getting the Code | <https://ardupilot.org/dev/docs/where-to-get-the-code.html> |
| Release Procedures | <https://ardupilot.org/dev/docs/release-procedures.html> |
| Using SITL | <https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html> |
| SITL Parameters | <https://ardupilot.org/dev/docs/SITL_simulation_parameters.html> |
| SITL/MAVProxy Tutorial | <https://ardupilot.org/dev/docs/plane-sitlmavproxy-tutorial.html> |
| WSL Performance | <https://askubuntu.com/questions/1485228/> |

### Configuration

| Resource | URL |
|----------|-----|
| Serial Port Setup | <https://ardupilot.org/plane/docs/common-telemetry-port-setup.html> |
| Serial Options | <https://ardupilot.org/plane/docs/common-serial-options.html> |
| Failsafe Function | <https://ardupilot.org/plane/docs/apms-failsafe-function.html> |
| Geofencing | <https://ardupilot.org/plane/docs/geofencing.html> |
| AC_Fence Source | <https://github.com/ArduPilot/ardupilot/blob/master/libraries/AC_Fence/AC_Fence.cpp> |

### MAVLink & Communication

| Resource | URL |
|----------|-----|
| MAVLink Messages | <https://mavlink.io/en/messages/common.html> |
| MAVLink Basics | <https://ardupilot.org/dev/docs/mavlink-basics.html> |
| mavlink-router | <https://github.com/mavlink-router/mavlink-router> |

### Official Documentation

| Resource | URL |
|----------|-----|
| ArduPilot Plane | <https://ardupilot.org/plane/> |
| Developer Docs | <https://ardupilot.org/dev/> |
| MAVLink Protocol | <https://mavlink.io/en/> |

### Ground Control Stations

| Resource | URL |
|----------|-----|
| Mission Planner | <https://ardupilot.org/planner/> |
| QGroundControl | <http://qgroundcontrol.com/> |
| QGC Parameters Guide | <https://docs.qgroundcontrol.com/master/en/qgc-user-guide/setup_view/parameters.html> |

### Community

| Resource | URL |
|----------|-----|
| ArduPilot Forum | <https://discuss.ardupilot.org/> |
| ArduPilot Discord | <https://ardupilot.org/discord> |

---

*End of Guide*
