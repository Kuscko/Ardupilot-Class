# MAVLink Protocol Guide

## What is MAVLink?

MAVLink (Micro Air Vehicle Link) is a lightweight binary messaging protocol for communicating between autopilots, ground control stations, companion computers, and telemetry radios. It supports MAVLink 1 and v2 (adds signing and extensions).

---

## MAVLink Message Structure

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

**System ID:** Autopilot default = 1, GCS = typically 255.

**Component ID:** Autopilot = 1, Camera = 100, Gimbal = 154.

---

## Essential MAVLink Messages

### Heartbeat (ID: 0)

Periodic "I'm alive" message at ~1 Hz. Contains vehicle type, autopilot type, base mode, custom mode, system status.

```python
from pymavlink import mavutil

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()
print(f"Heartbeat from system {master.target_system}")
```

---

### Attitude (ID: 30)

Roll, pitch, yaw angles (radians) and angular speeds (rad/s). **Frequency:** 10-50 Hz.

---

### Global Position Int (ID: 33)

Filtered GPS + EKF position. Lat/lon in degrees × 10^7, altitudes in mm, velocities in cm/s. **Frequency:** 1-10 Hz.

---

### VFR HUD (ID: 74)

Airspeed (m/s), groundspeed (m/s), heading (deg), throttle (%), altitude MSL (m), climb rate (m/s). **Frequency:** 1-10 Hz.

---

### Sys Status (ID: 1)

Sensor bitmasks (present/enabled/healthy), CPU load, battery voltage (mV), current (cA), remaining (%). **Frequency:** 1 Hz.

---

### GPS Raw Int (ID: 24)

Raw GPS data: fix type, lat/lon (deg × 10^7), altitude (mm), DOP values, ground speed (cm/s), satellite count. **Frequency:** 1-5 Hz.

---

### Mission Commands

**Mission Count (ID: 44):** GCS declares number of mission items to upload.

**Mission Item Int (ID: 73):** Individual waypoint/command with seq, frame, command, param1-4, lat (deg × 10^7), lon (deg × 10^7), alt (m).

---

### Command Long (ID: 76)

| Command | ID | Description |
|---------|----|-------------|
| MAV_CMD_COMPONENT_ARM_DISARM | 400 | Arm/disarm vehicle |
| MAV_CMD_DO_SET_MODE | 176 | Set flight mode |
| MAV_CMD_NAV_TAKEOFF | 22 | Takeoff |
| MAV_CMD_NAV_RETURN_TO_LAUNCH | 20 | Return to launch |

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

| Parameter Group | Controls |
|----------------|----------|
| SR0_* | Serial 0 (USB) rates |
| SR1_* | Serial 1 (Telem1) rates |
| SR2_* | Serial 2 (Telem2) rates |

| Parameter | Messages Affected |
|-----------|-------------------|
| SR*_EXTRA1 | ATTITUDE, SIMSTATE |
| SR*_EXTRA2 | VFR_HUD |
| SR*_EXTRA3 | AHRS, SYSTEM_TIME |
| SR*_POSITION | GLOBAL_POSITION_INT |
| SR*_RAW_SENS | RAW_IMU, SCALED_PRESSURE |
| SR*_RC_CHAN | SERVO_OUTPUT_RAW, RC_CHANNELS |

Value = Hz (0=disabled).

```bash
param set SR1_POSITION 5  # 5 Hz position updates on Telem1
```

---

## Python MAVLink Examples

### Connect and Monitor

```python
from pymavlink import mavutil
import time

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')

print("Waiting for heartbeat...")
master.wait_heartbeat()
print(f"Connected to system {master.target_system}")

while True:
    msg = master.recv_match(blocking=True, timeout=1)
    if msg:
        print(msg)
```

### Get Specific Message

```python
msg = master.recv_match(type='VFR_HUD', blocking=True, timeout=5)
if msg:
    print(f"Airspeed: {msg.airspeed} m/s")
    print(f"Altitude: {msg.alt} m")
    print(f"Heading: {msg.heading} degrees")
```

### Arm Vehicle

```python
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0, 1, 0, 0, 0, 0, 0, 0
)

ack = master.recv_match(type='COMMAND_ACK', blocking=True, timeout=5)
print(f"Arm result: {ack.result}")
```

### Set Flight Mode

```python
mode_id = master.mode_mapping()['GUIDED']
master.set_mode(mode_id)
```

### Request Data Stream

```python
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

```python
# Serial
master = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)

# UDP (listen)
master = mavutil.mavlink_connection('udp:127.0.0.1:14550')

# UDP (send to endpoint)
master = mavutil.mavlink_connection('udpout:192.168.1.100:14550')

# TCP (server)
master = mavutil.mavlink_connection('tcp:127.0.0.1:5760')

# TCP (client)
master = mavutil.mavlink_connection('tcpout:192.168.1.100:5760')
```

---

## Monitoring MAVLink in SITL

```bash
set streamrate -1   # Show all messages
watch VFR_HUD       # Show specific message
unwatch VFR_HUD
```

### Python Monitor Script

```python
#!/usr/bin/env python3
"""Simple MAVLink monitor — displays key telemetry"""

from pymavlink import mavutil
import time

def monitor_mavlink(connection_string='udp:127.0.0.1:14550'):
    master = mavutil.mavlink_connection(connection_string)

    print("Waiting for heartbeat...")
    master.wait_heartbeat()
    print(f"Connected to system {master.target_system}\n")

    while True:
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

## MAVLink Command ID Reference

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

## Additional Resources

- [MAVLink Developer Guide](https://mavlink.io/en/)
- [MAVLink Common Messages](https://mavlink.io/en/messages/common.html)
- [ArduPilot-specific Messages](https://mavlink.io/en/messages/ardupilotmega.html)
- [pymavlink Examples](https://github.com/ArduPilot/pymavlink/tree/master/examples)
- [ArduPilot MAVLink Docs](https://ardupilot.org/dev/docs/mavlink-basics.html)
- [Main Onboarding Guide](../Onboarding_Documentation/ArduPilot_Onboarding_Guide.md)

---

**Last Updated:** 2026-02-03
**Target Version:** Plane 4.5.7
