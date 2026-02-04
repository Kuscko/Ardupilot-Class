# MAVLink Protocol & Mavlink-Router

## Overview

MAVLink (Micro Air Vehicle Link) is the lightweight messaging protocol used by ArduPilot for communication between flight controllers, ground control stations, and companion computers [1]. Mavlink-router is a tool that enables routing MAVLink messages to multiple destinations simultaneously, essential for complex system architectures with multiple ground stations or companion computers [2].

**Why MAVLink Matters:**
- Industry-standard protocol for drone communication
- Supports telemetry, commands, mission planning, and parameter management
- Enables integration with companion computers and custom applications
- Required for understanding ArduPilot system communication

## Prerequisites

Before starting this module, you should:

- Have completed SITL setup and understand basic ArduPilot operation
- Be familiar with network concepts (TCP, UDP, serial ports)
- Understand basic ArduPilot parameters and flight modes
- Have Python installed for scripting examples (optional)

## What You'll Learn

By completing this module, you will:

- Understand MAVLink protocol structure and message types
- Identify essential MAVLink messages for ArduPilot operations
- Monitor and interpret MAVLink messages in real-time
- Install and configure mavlink-router for message routing
- Route telemetry between SITL, GCS, and companion computers
- Create Python scripts to send/receive MAVLink messages
- Debug communication issues using MAVLink tools

## Key Concepts

### MAVLink Protocol Basics

MAVLink is a binary protocol optimized for bandwidth-limited links [1]:

**Message Structure:**
- **Header:** Protocol version, system ID, component ID
- **Payload:** Message-specific data
- **Checksum:** Error detection

**Key Features:**
- Compact binary format (minimal overhead)
- Versioned protocol (MAVLink 1 and MAVLink 2)
- System/Component addressing for multi-vehicle networks
- Automatic message serialization/deserialization

### Essential MAVLink Messages

**Heartbeat (ID: 0):**
- Sent periodically by all systems (1 Hz)
- Indicates system is alive and operational
- Contains system type, autopilot type, base mode

**Attitude (ID: 30):**
- Roll, pitch, yaw angles
- Angular velocities
- Update rate: 10-50 Hz

**GPS_RAW_INT (ID: 24):**
- GPS position (latitude, longitude, altitude)
- Satellite count, GPS fix type
- Update rate: 1-10 Hz

**COMMAND_LONG (ID: 76):**
- Send commands to vehicle (arm, mode change, etc.)
- Used for action requests from GCS

**MISSION_ITEM (ID: 39):**
- Waypoint definition for autonomous missions
- Contains position, command, parameters

See [MAVLink Common Messages](https://mavlink.io/en/messages/common.html) [3] for complete message reference.

### MAVLink Communication Patterns

**Telemetry Streaming:**
- Flight controller broadcasts status messages
- GCS receives and displays data
- Typically UDP broadcast or serial

**Command/Response:**
- GCS sends command (COMMAND_LONG)
- Flight controller acknowledges (COMMAND_ACK)
- Request-response pattern

**Mission Upload/Download:**
- Multi-message sequence
- Mission count, items, acknowledgments
- Stateful protocol exchange

### Mavlink-Router Architecture

Mavlink-router acts as a hub for MAVLink traffic [2]:

```
[Flight Controller] <--serial--> [mavlink-router] <--UDP--> [GCS]
                                        |
                                        +--UDP--> [Companion Computer]
                                        |
                                        +--TCP--> [Custom Application]
```

**Benefits:**
- Single connection to flight controller
- Multiple consumers of telemetry
- Flexible routing (serial, UDP, TCP)
- Automatic endpoint discovery

## Hands-On Practice

### Exercise 1: Monitor MAVLink Messages in SITL

Start SITL and observe raw MAVLink traffic:

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --map
```

In MAVProxy console, enable message monitoring:

```bash
# Show all messages (very verbose)
set shownoise 1

# Show specific message type
watch HEARTBEAT
watch GPS_RAW_INT
watch ATTITUDE
```

**Expected Output:** Real-time display of message contents and update rates

### Exercise 2: Inspect Messages with pymavlink

Use Python to decode and display specific messages:

```bash
cd ~/Desktop/Work/AEVEX/MAVLink_MavlinkRouter/example_python_scripts
python3 monitor_messages.py --connect tcp:127.0.0.1:5760
```

This script displays parsed message data in readable format.

### Exercise 3: Install Mavlink-Router

Install mavlink-router on Ubuntu/WSL2:

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y git ninja-build pkg-config gcc g++ systemd

# Clone and build
cd ~/
git clone https://github.com/mavlink-router/mavlink-router.git
cd mavlink-router
git submodule update --init --recursive

# Build using meson
meson setup build .
ninja -C build
sudo ninja -C build install
```

**Verify installation:**
```bash
mavlink-routerd --version
```

### Exercise 4: Configure Mavlink-Router

Create configuration file for routing SITL telemetry:

```bash
cd ~/Desktop/Work/AEVEX/MAVLink_MavlinkRouter/example_configs
cat sitl_example.conf
```

**Example Configuration:**
```ini
[General]
TcpServerPort=5760

[UdpEndpoint to_gcs]
Mode = Normal
Address = 127.0.0.1
Port = 14550

[UdpEndpoint to_companion]
Mode = Normal
Address = 127.0.0.1
Port = 14551
```

### Exercise 5: Run Mavlink-Router with SITL

Start SITL and route telemetry to multiple destinations:

```bash
# Terminal 1: Start SITL (no GCS)
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --map -A "--uartC=tcp:127.0.0.1:5762"

# Terminal 2: Run mavlink-router
mavlink-routerd -e 127.0.0.1:14550 127.0.0.1:5762
```

This routes telemetry from SITL to UDP port 14550 (standard GCS port).

### Exercise 6: Send Commands via MAVLink

Use Python script to send commands to vehicle:

```bash
cd ~/Desktop/Work/AEVEX/MAVLink_MavlinkRouter/example_python_scripts
python3 send_command.py --connect tcp:127.0.0.1:5760 --command ARM
```

**Available commands:** ARM, DISARM, TAKEOFF, RTL, LAND

## Complete Guides

This module includes comprehensive documentation:

- **[MAVLINK_GUIDE.md](MAVLINK_GUIDE.md)** - Complete MAVLink protocol guide with message reference
- **[MAVLINK_ROUTER_GUIDE.md](MAVLINK_ROUTER_GUIDE.md)** - Mavlink-router installation and configuration

## Example Files

**Configuration Files:** [example_configs/](example_configs/)
- `sitl_example.conf` - SITL routing configuration
- `hardware_example.conf` - Hardware flight controller routing
- `multi_gcs.conf` - Multiple ground station setup

**Python Scripts:** [example_python_scripts/](example_python_scripts/)
- `monitor_messages.py` - Display real-time MAVLink messages
- `send_command.py` - Send commands to vehicle
- `request_data_stream.py` - Request specific message rates
- `mission_upload.py` - Upload waypoint mission

## Common Issues

### Issue: No MAVLink messages received

**Symptom:** Connection established but no messages appear

**Solutions:**
1. Verify connection string is correct (TCP vs UDP, correct port)
2. Check firewall isn't blocking ports
3. Confirm SITL/hardware is actually sending messages
4. Test with MAVProxy first to verify connection
5. Use `tcpdump` or `wireshark` to verify network traffic

### Issue: Mavlink-router "address already in use"

**Symptom:** Cannot start mavlink-router, port conflict

**Solutions:**
```bash
# Find process using port
sudo lsof -i :5760

# Kill conflicting process
kill <PID>

# Or use different port in configuration
```

### Issue: Messages received but corrupted

**Symptom:** Parse errors, checksum failures

**Common Causes:**
- MAVLink version mismatch (MAVLink 1 vs 2)
- Serial baud rate mismatch
- Buffer overflow on slow connections

**Solutions:**
1. Verify MAVLink version compatibility
2. Check serial port settings (baud rate, parity)
3. Reduce message rates: `SR0_* parameters`
4. Increase buffer sizes in mavlink-router

### Issue: SITL connection refused

**Symptom:** Cannot connect to SITL TCP port

**Solutions:**
```bash
# Start SITL with explicit TCP port
sim_vehicle.py --console --map -A "--serial0=tcp:127.0.0.1:5760"

# Or use MAVProxy's output add
output add 127.0.0.1:14550
```

### Issue: Permission denied on serial port (hardware)

**Symptom:** Cannot open /dev/ttyUSB0 or similar

**Solutions:**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Logout and login for group change to take effect

# Or temporarily change permissions
sudo chmod 666 /dev/ttyUSB0
```

See complete troubleshooting in **[MAVLINK_ROUTER_GUIDE.md](MAVLINK_ROUTER_GUIDE.md)**.

## Message Rate Configuration

Control how frequently ArduPilot sends specific messages using SR parameters [4]:

**Common Parameters:**
- `SR0_POSITION` - GPS position messages
- `SR0_RAW_SENS` - Raw sensor data (IMU, baro)
- `SR0_RC_CHAN` - RC channel values
- `SR0_EXTRA1` - Attitude (roll/pitch/yaw)
- `SR0_EXTRA2` - VFR_HUD messages
- `SR0_EXTRA3` - Battery, system status

**Example:**
```bash
# Set GPS position to 10 Hz
param set SR0_POSITION 10

# Disable raw sensor data
param set SR0_RAW_SENS 0
```

**Note:** SR0_* controls serial port 0 (USB), SR1_* for telemetry port 1, etc.

## Python MAVLink Examples

### Basic Message Reading

```python
from pymavlink import mavutil

# Connect to vehicle
connection = mavutil.mavlink_connection('tcp:127.0.0.1:5760')

# Wait for heartbeat
connection.wait_heartbeat()
print("Connected to vehicle")

# Read messages
while True:
    msg = connection.recv_match(blocking=True)
    if msg:
        print(msg)
```

### Send Command

```python
# Arm vehicle
connection.mav.command_long_send(
    connection.target_system,
    connection.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0, 1, 0, 0, 0, 0, 0, 0
)
```

See [example_python_scripts/](example_python_scripts/) for complete examples.

## Additional Resources

### Official MAVLink Documentation

- **[MAVLink Developer Guide](https://mavlink.io/en/)** [1] - Complete protocol documentation
- **[MAVLink Common Messages](https://mavlink.io/en/messages/common.html)** [3] - Message reference
- **[MAVLink ArduPilot Dialect](https://mavlink.io/en/messages/ardupilotmega.html)** - ArduPilot-specific messages
- **[pymavlink Documentation](https://mavlink.io/en/mavgen_python/)** - Python library guide

### Mavlink-Router Resources

- **[Mavlink-Router GitHub](https://github.com/mavlink-router/mavlink-router)** [2] - Source and documentation
- **[Configuration Guide](https://github.com/mavlink-router/mavlink-router/blob/master/README.md)** - Setup instructions

### ArduPilot Documentation

- **[ArduPilot MAVLink Guide](https://ardupilot.org/dev/docs/mavlink-basics.html)** [4] - ArduPilot MAVLink overview
- **[Message Streaming Rates](https://ardupilot.org/dev/docs/mavlink-requesting-data.html)** - SR parameter documentation
- **[MAVLink Commands](https://ardupilot.org/dev/docs/copter-commands-in-guided-mode.html)** - Command reference

### Development Tools

- **[MAVExplorer](https://ardupilot.org/dev/docs/using-mavexplorer-for-log-analysis.html)** - Log analysis with MAVLink
- **[QGroundControl](http://qgroundcontrol.com/)** - Popular GCS using MAVLink
- **[Mission Planner](https://ardupilot.org/planner/)** - Windows GCS

### Community Resources

- [ArduPilot Discord: MAVLink Channel](https://ardupilot.org/discord)
- [Discourse: MAVLink Topics](https://discuss.ardupilot.org/tags/mavlink)
- [MAVLink Mailing List](https://groups.google.com/g/mavlink)

## Security Considerations

**MAVLink Security:**
- Protocol has no built-in encryption or authentication
- Anyone on network can send commands
- Consider using VPN for remote connections
- MAVLink 2 supports message signing (optional)

**Best Practices:**
- Use firewalls to restrict access
- Implement application-level authentication
- Monitor for unauthorized commands
- Use secure channels (SSH tunnels) for critical operations

## Next Steps

After completing this MAVLink module:

1. **Companion Computer Integration** - Set up Raspberry Pi or similar ([Companion Computer Guide](../Advanced_Topics/Companion_Computer/))
2. **Custom MAVLink Messages** - Create your own message types ([Custom Messages](../Advanced_Topics/Custom_MAVLink_Messages/))
3. **Telemetry Radio Setup** - Configure long-range telemetry ([Telemetry Radio](../Advanced_Topics/Telemetry_Radio_Setup/))
4. **Advanced Scripting** - Combine MAVLink with Lua scripts ([Lua Scripts](../Lua_Scripts/))
5. **Flight Log Analysis** - Analyze MAVLink logs ([Log Analysis](../Advanced_Topics/Flight_Log_Analysis/))

---

**Sources:**

[1] https://mavlink.io/en/
[2] https://github.com/mavlink-router/mavlink-router
[3] https://mavlink.io/en/messages/common.html
[4] https://ardupilot.org/dev/docs/mavlink-basics.html
