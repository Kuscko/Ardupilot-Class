# MAVLink Protocol & Mavlink-Router

## Overview

MAVLink (Micro Air Vehicle Link) is the lightweight binary messaging protocol used by ArduPilot for communication between flight controllers, ground control stations, and companion computers. Mavlink-router enables routing MAVLink messages to multiple destinations simultaneously.

## Prerequisites

- SITL setup complete and comfortable with basic ArduPilot operation
- Familiar with network concepts (TCP, UDP, serial ports)
- Python installed for scripting examples (optional)

## Key Concepts

### MAVLink Protocol

MAVLink messages contain: header (protocol version, system ID, component ID), payload, and checksum.

**Key features:** Compact binary format, versioned (MAVLink 1 and 2), system/component addressing for multi-vehicle networks.

### Essential Messages

| Message | ID | Rate | Purpose |
|---------|-----|------|---------|
| Heartbeat | 0 | 1 Hz | System alive, mode/type info |
| Attitude | 30 | 10-50 Hz | Roll, pitch, yaw + angular rates |
| GPS_RAW_INT | 24 | 1-10 Hz | GPS position, satellites, fix type |
| COMMAND_LONG | 76 | On-demand | Send commands (arm, mode change) |
| MISSION_ITEM | 39 | Upload | Waypoint definitions |

See [MAVLink Common Messages](https://mavlink.io/en/messages/common.html).

### Communication Patterns

- **Telemetry Streaming:** Flight controller broadcasts; GCS receives and displays
- **Command/Response:** GCS sends COMMAND_LONG; FC acknowledges with COMMAND_ACK
- **Mission Upload/Download:** Multi-message stateful exchange

### Mavlink-Router Architecture

```
[Flight Controller] <--serial--> [mavlink-router] <--UDP--> [GCS]
                                       |
                                       +--UDP--> [Companion Computer]
                                       |
                                       +--TCP--> [Custom Application]
```

## Hands-On Practice

### Exercise 1: Monitor MAVLink Messages in SITL

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --map
```

In MAVProxy console:
```bash
set shownoise 1       # Show all messages
watch HEARTBEAT
watch GPS_RAW_INT
watch ATTITUDE
```

### Exercise 2: Inspect Messages with pymavlink

```bash
cd ~/Desktop/Work/AEVEX/MAVLink_MavlinkRouter/example_python_scripts
python3 monitor_messages.py --connect tcp:127.0.0.1:5760
```

### Exercise 3: Install Mavlink-Router

```bash
sudo apt-get update
sudo apt-get install -y git ninja-build pkg-config gcc g++ systemd

cd ~/
git clone https://github.com/mavlink-router/mavlink-router.git
cd mavlink-router
git submodule update --init --recursive

meson setup build .
ninja -C build
sudo ninja -C build install
```

```bash
mavlink-routerd --version
```

### Exercise 4: Configure Mavlink-Router

```bash
cd ~/Desktop/Work/AEVEX/MAVLink_MavlinkRouter/example_configs
cat sitl_example.conf
```

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

```bash
# Terminal 1: Start SITL
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --map -A "--uartC=tcp:127.0.0.1:5762"

# Terminal 2: Run mavlink-router
mavlink-routerd -e 127.0.0.1:14550 127.0.0.1:5762
```

### Exercise 6: Send Commands via MAVLink

```bash
cd ~/Desktop/Work/AEVEX/MAVLink_MavlinkRouter/example_python_scripts
python3 send_command.py --connect tcp:127.0.0.1:5760 --command ARM
```

## Complete Guides

- **[MAVLINK_GUIDE.md](MAVLINK_GUIDE.md)** - MAVLink protocol reference with message details and Python examples
- **[MAVLINK_ROUTER_GUIDE.md](MAVLINK_ROUTER_GUIDE.md)** - Mavlink-router installation and configuration

## Example Files

**Configuration Files:** [example_configs/](example_configs/)
- `sitl_example.conf`, `hardware_example.conf`, `multi_gcs.conf`

**Python Scripts:** [example_python_scripts/](example_python_scripts/)
- `monitor_messages.py`, `send_command.py`, `request_data_stream.py`, `mission_upload.py`

## Message Rate Configuration

```bash
param set SR0_POSITION 10   # GPS position at 10 Hz
param set SR0_RAW_SENS 0    # Disable raw sensor data
```

SR0_* = serial port 0 (USB), SR1_* = telemetry port 1, etc.

## Python MAVLink Examples

```python
from pymavlink import mavutil

connection = mavutil.mavlink_connection('tcp:127.0.0.1:5760')
connection.wait_heartbeat()
print("Connected to vehicle")

while True:
    msg = connection.recv_match(blocking=True)
    if msg:
        print(msg)
```

```python
# Arm vehicle
connection.mav.command_long_send(
    connection.target_system,
    connection.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0, 1, 0, 0, 0, 0, 0, 0
)
```

## Common Issues

### No MAVLink messages received
1. Verify connection string (TCP vs UDP, correct port)
2. Check firewall isn't blocking ports
3. Test with MAVProxy first
4. Use `tcpdump` to verify network traffic

### Mavlink-router "address already in use"
```bash
sudo lsof -i :5760
kill <PID>
# Or use different port in configuration
```

### Messages corrupted
- Verify MAVLink version compatibility (v1 vs v2)
- Check serial baud rate match
- Reduce message rates with `SR0_*` parameters

### Permission denied on serial port
```bash
sudo usermod -a -G dialout $USER
# Logout and login for group change to take effect
```

## Security Considerations

MAVLink has no built-in encryption or authentication. Anyone on the network can send commands.

- Use firewalls to restrict access to MAVLink ports
- Use VPN or SSH tunnels for remote connections
- MAVLink 2 supports optional message signing

## Additional Resources

- **[MAVLink Developer Guide](https://mavlink.io/en/)**
- **[MAVLink Common Messages](https://mavlink.io/en/messages/common.html)**
- **[Mavlink-Router GitHub](https://github.com/mavlink-router/mavlink-router)**
- **[ArduPilot MAVLink Guide](https://ardupilot.org/dev/docs/mavlink-basics.html)**
- **[pymavlink Documentation](https://mavlink.io/en/mavgen_python/)**
- [ArduPilot Discord](https://ardupilot.org/discord)

## Next Steps

1. **Companion Computer Integration** ([Companion Computer Guide](../Advanced_Topics/Companion_Computer/))
2. **Telemetry Radio Setup** ([Telemetry Radio](../Advanced_Topics/Telemetry_Radio_Setup/))
3. **Advanced Scripting** - Combine MAVLink with Lua ([Lua Scripts](../Lua_Scripts/))
4. **Flight Log Analysis** ([Log Analysis](../Advanced_Topics/Flight_Log_Analysis/))
