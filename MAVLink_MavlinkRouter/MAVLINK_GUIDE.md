# MAVLink Protocol Guide

## What is MAVLink?

MAVLink (Micro Air Vehicle Link) is a lightweight messaging protocol for communicating with drones and unmanned vehicles. It's the communication standard between:

- **Autopilot ↔ Ground Control Station (GCS)**
- **Autopilot ↔ Companion Computer**
- **Autopilot ↔ Telemetry Radio**
- **Multiple GCS applications simultaneously**

**Key Features:**
- Lightweight and efficient (binary protocol)
- Language-agnostic (libraries for C, Python, Java, etc.)
- Extensible message set
- Version 1 and Version 2 (v2 adds signing, extensions)

---

## MAVLink Message Structure

### Message Components

Every MAVLink message contains:

| Field | Size | Description |
|-------|------|-------------|
| Start Marker | 1 byte | 0xFE (v1) or 0xFD (v2) |
| Payload Length | 1 byte | Size of payload |
| Sequence | 1 byte | Packet sequence number |
| System ID | 1 byte | ID of sender (1-255) |
| Component ID | 1 byte | ID of sender component |
| Message ID | 1-3 bytes | Type of message |
| Payload | Variable | Actual data |
| Checksum | 2 bytes | CRC for error detection |
| Signature | 13 bytes | Optional (v2 only) |

### System ID and Component ID

**System ID:**
- Unique identifier for each vehicle/system
- Default autopilot: 1
- Ground station: typically 255
- Range: 1-255

**Component ID:**
- Identifies component within a system
- Autopilot: 1 (MAV_COMP_ID_AUTOPILOT1)
- Camera: 100 (MAV_COMP_ID_CAMERA)
- Gimbal: 154 (MAV_COMP_ID_GIMBAL)

---

## Essential MAVLink Messages

### Heartbeat (Message ID: 0)

**Purpose:** Periodic "I'm alive" message

**Fields:**
- `type`: Vehicle type (fixed-wing, copter, etc.)
- `autopilot`: Autopilot type (ArduPilot = 3)
- `base_mode`: System mode flags
- `custom_mode`: Vehicle-specific mode
- `system_status`: System status (standby, active, etc.)

**Frequency:** ~1 Hz

**Python Example:**
```python
from pymavlink import mavutil

# Connect to autopilot
master = mavutil.mavlink_connection('udp:127.0.0.1:14550')

# Wait for heartbeat
master.wait_heartbeat()
print(f"Heartbeat from system {master.target_system}")
```

---

### Attitude (Message ID: 30)

**Purpose:** Current attitude (orientation) of vehicle

**Fields:**
- `time_boot_ms`: Timestamp
- `roll`: Roll angle (radians)
- `pitch`: Pitch angle (radians)
- `yaw`: Yaw angle (radians)
- `rollspeed`: Roll angular speed (rad/s)
- `pitchspeed`: Pitch angular speed (rad/s)
- `yawspeed`: Yaw angular speed (rad/s)

**Frequency:** 10-50 Hz (depends on SR* parameters)

---

### Global Position Int (Message ID: 33)

**Purpose:** Filtered global position (GPS + EKF)

**Fields:**
- `time_boot_ms`: Timestamp
- `lat`: Latitude (degrees × 10^7)
- `lon`: Longitude (degrees × 10^7)
- `alt`: Altitude MSL (mm)
- `relative_alt`: Altitude AGL (mm)
- `vx`: X velocity (cm/s)
- `vy`: Y velocity (cm/s)
- `vz`: Z velocity (cm/s)
- `hdg`: Heading (degrees × 100)

**Frequency:** 1-10 Hz

---

### VFR HUD (Message ID: 74)

**Purpose:** Metrics displayed on Vehicle Flight Rules HUD

**Fields:**
- `airspeed`: Current airspeed (m/s)
- `groundspeed`: Current groundspeed (m/s)
- `heading`: Current heading (degrees)
- `throttle`: Current throttle (%)
- `alt`: Current altitude MSL (m)
- `climb`: Current climb rate (m/s)

**Frequency:** 1-10 Hz

---

### Sys Status (Message ID: 1)

**Purpose:** System status and health

**Fields:**
- `onboard_control_sensors_present`: Sensor bitmask (present)
- `onboard_control_sensors_enabled`: Sensor bitmask (enabled)
- `onboard_control_sensors_health`: Sensor bitmask (healthy)
- `load`: CPU load (%)
- `voltage_battery`: Battery voltage (mV)
- `current_battery`: Battery current (cA)
- `battery_remaining`: Battery remaining (%)

**Frequency:** 1 Hz

---

### GPS Raw Int (Message ID: 24)

**Purpose:** Raw GPS data

**Fields:**
- `time_usec`: Timestamp (µs)
- `fix_type`: GPS fix type (0=no fix, 3=3D fix)
- `lat`: Latitude (degrees × 10^7)
- `lon`: Longitude (degrees × 10^7)
- `alt`: Altitude MSL (mm)
- `eph`: GPS horizontal dilution of position
- `epv`: GPS vertical dilution of position
- `vel`: GPS ground speed (cm/s)
- `cog`: Course over ground (degrees × 100)
- `satellites_visible`: Number of satellites

**Frequency:** 1-5 Hz

---

### Mission Commands

#### Mission Count (Message ID: 44)

Sent by GCS to declare number of mission items to upload.

#### Mission Item Int (Message ID: 73)

Individual mission waypoint/command.

**Key Fields:**
- `seq`: Sequence number
- `frame`: Coordinate frame
- `command`: MAV_CMD (NAV_WAYPOINT, TAKEOFF, etc.)
- `param1-4`: Command-specific parameters
- `x`: Latitude (degrees × 10^7)
- `y`: Longitude (degrees × 10^7)
- `z`: Altitude (m)

---

### Command Messages

#### Command Long (Message ID: 76)

Send command to vehicle (arm, set mode, etc.)

**Common Commands:**
- `MAV_CMD_COMPONENT_ARM_DISARM` (400): Arm/disarm vehicle
- `MAV_CMD_DO_SET_MODE` (176): Set flight mode
- `MAV_CMD_NAV_TAKEOFF` (22): Takeoff command
- `MAV_CMD_NAV_RETURN_TO_LAUNCH` (20): Return to launch

**Python Example:**
```python
# Arm the vehicle
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,  # Confirmation
    1,  # Param1: 1 = arm
    0, 0, 0, 0, 0, 0  # Unused params
)
```

---

## Message Streaming Rates

ArduPilot controls message streaming rates with `SR*` parameters:

| Parameter Group | Controls |
|----------------|----------|
| SR0_* | Serial 0 (USB) rates |
| SR1_* | Serial 1 (Telem1) rates |
| SR2_* | Serial 2 (Telem2) rates |

### Rate Parameters

| Parameter | Messages Affected |
|-----------|-------------------|
| SR*_EXTRA1 | ATTITUDE, SIMSTATE |
| SR*_EXTRA2 | VFR_HUD |
| SR*_EXTRA3 | AHRS, SYSTEM_TIME |
| SR*_POSITION | GLOBAL_POSITION_INT |
| SR*_RAW_SENS | RAW_IMU, SCALED_PRESSURE |
| SR*_RC_CHAN | SERVO_OUTPUT_RAW, RC_CHANNELS |

**Value:** Hz (messages per second)
- 0 = disabled
- 1 = 1 Hz
- 10 = 10 Hz

**Example:**
```bash
# Set position updates to 5 Hz on Telem1
param set SR1_POSITION 5
```

---

## Python MAVLink Examples

### Connect and Monitor

```python
from pymavlink import mavutil
import time

# Connect to SITL
master = mavutil.mavlink_connection('udp:127.0.0.1:14550')

# Wait for heartbeat
print("Waiting for heartbeat...")
master.wait_heartbeat()
print(f"Connected to system {master.target_system}")

# Read messages
while True:
    msg = master.recv_match(blocking=True, timeout=1)
    if msg:
        print(msg)
```

### Get Specific Message

```python
# Get VFR_HUD message
msg = master.recv_match(type='VFR_HUD', blocking=True, timeout=5)
if msg:
    print(f"Airspeed: {msg.airspeed} m/s")
    print(f"Altitude: {msg.alt} m")
    print(f"Heading: {msg.heading} degrees")
```

### Arm Vehicle

```python
# Arm
master.arducopter_arm()
# or
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0, 1, 0, 0, 0, 0, 0, 0
)

# Wait for ack
ack = master.recv_match(type='COMMAND_ACK', blocking=True, timeout=5)
print(f"Arm result: {ack.result}")
```

### Set Flight Mode

```python
# Set mode to GUIDED
mode_id = master.mode_mapping()['GUIDED']
master.set_mode(mode_id)

# Or use command_long
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_DO_SET_MODE,
    0,
    mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    mode_id,
    0, 0, 0, 0, 0
)
```

### Request Data Stream

```python
# Request all streams at 10 Hz
master.mav.request_data_stream_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_ALL,
    10,  # Hz
    1    # Enable
)
```

---

## MAVLink over Different Transports

### Serial

```python
# Direct serial connection
master = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)
```

### UDP

```python
# Listen for MAVLink on UDP port
master = mavutil.mavlink_connection('udp:127.0.0.1:14550')

# Send to specific UDP endpoint
master = mavutil.mavlink_connection('udpout:192.168.1.100:14550')
```

### TCP

```python
# TCP server (listen)
master = mavutil.mavlink_connection('tcp:127.0.0.1:5760')

# TCP client (connect)
master = mavutil.mavlink_connection('tcpout:192.168.1.100:5760')
```

---

## Monitoring MAVLink in SITL

### MAVProxy Built-in

MAVProxy shows message traffic in console window. Enable/disable with:

```bash
# Show all messages
set streamrate -1

# Show specific message
watch VFR_HUD

# Stop watching
unwatch VFR_HUD
```

### Python Monitor Script

```python
#!/usr/bin/env python3
"""
Simple MAVLink monitor
Displays key telemetry from autopilot
"""

from pymavlink import mavutil
import time

def monitor_mavlink(connection_string='udp:127.0.0.1:14550'):
    master = mavutil.mavlink_connection(connection_string)

    print("Waiting for heartbeat...")
    master.wait_heartbeat()
    print(f"Connected to system {master.target_system}\n")

    while True:
        # Get VFR HUD
        msg = master.recv_match(type='VFR_HUD', blocking=False)
        if msg:
            print(f"\r  Airspeed: {msg.airspeed:5.1f} m/s | "
                  f"Alt: {msg.alt:6.1f} m | "
                  f"Heading: {msg.heading:3.0f}° | "
                  f"Throttle: {msg.throttle:3.0f}%", end='')

        time.sleep(0.1)

if __name__ == '__main__':
    monitor_mavlink()
```

---

## MAVLink Message Reference

### Online Resources

- **MAVLink Common Messages:** https://mavlink.io/en/messages/common.html
- **ArduPilot-specific Messages:** https://mavlink.io/en/messages/ardupilotmega.html
- **MAVLink Protocol:** https://mavlink.io/en/guide/
- **pymavlink Documentation:** https://mavlink.io/en/mavgen_python/

### Command IDs (MAV_CMD)

Common commands used in missions and command_long:

| ID | Command | Description |
|----|---------|-------------|
| 16 | NAV_WAYPOINT | Navigate to waypoint |
| 20 | NAV_RETURN_TO_LAUNCH | Return to launch |
| 21 | NAV_LAND | Land at location |
| 22 | NAV_TAKEOFF | Takeoff |
| 84 | NAV_VTOL_TAKEOFF | VTOL takeoff |
| 85 | NAV_VTOL_LAND | VTOL land |
| 176 | DO_SET_MODE | Set flight mode |
| 400 | COMPONENT_ARM_DISARM | Arm or disarm |

---

## Next Steps

1. [ ] Practice with Python pymavlink scripts
2. [ ] Monitor messages in SITL
3. [ ] Learn [mavlink-router](MAVLINK_ROUTER_GUIDE.md) for routing
4. [ ] Explore message structure with examples
5. [ ] Build custom GCS or monitoring tools

---

## Additional Resources

- [MAVLink Developer Guide](https://mavlink.io/en/)
- [pymavlink Examples](https://github.com/ArduPilot/pymavlink/tree/master/examples)
- [ArduPilot MAVLink Docs](https://ardupilot.org/dev/docs/mavlink-basics.html)
- [Main Onboarding Guide](../Onboarding_Documentation/ArduPilot_Onboarding_Guide.md)

---

**Last Updated:** 2026-02-03
**Target Version:** Plane 4.5.7
