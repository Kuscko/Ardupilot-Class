# mavlink-router Guide

## What is mavlink-router?

mavlink-router is a tool that routes MAVLink packets between multiple endpoints. It enables multiple ground control stations, companion computers, and other MAVLink applications to communicate with a single autopilot simultaneously.

**Use Cases:**
- Connect Mission Planner + QGroundControl + custom scripts to one autopilot
- Route telemetry between serial, UDP, and TCP connections
- Companion computer routing (autopilot ↔ multiple applications)
- Log all MAVLink traffic
- Filter messages based on source/destination

---

## Why Use mavlink-router?

### Without mavlink-router:

```
Autopilot (Serial) ─── Single GCS only
```

Only one application can connect to the autopilot's serial port at a time.

### With mavlink-router:

```
                    ┌─── Mission Planner (UDP)
                    │
Autopilot (Serial) ─┤─── QGroundControl (UDP)
                    │
                    ├─── Python Script (UDP)
                    │
                    └─── Remote GCS (TCP)
```

Multiple applications receive all telemetry and can send commands.

---

## Installation

### Ubuntu/Debian (WSL2)

```bash
# Install dependencies
sudo apt update
sudo apt install -y git meson ninja-build pkg-config \
    gcc g++ systemd python3-pip

# Clone repository
cd ~
git clone https://github.com/mavlink-router/mavlink-router.git
cd mavlink-router

# Build with meson
meson setup build .
ninja -C build

# Install
sudo ninja -C build install
```

### Verify Installation

```bash
mavlink-routerd --version
```

---

## Basic Usage

### Command Line Mode

Simple routing without configuration file:

```bash
# Route from serial to two UDP endpoints
mavlink-routerd \
    --endpoint udp:127.0.0.1:14550 \
    --endpoint udp:127.0.0.1:14551 \
    /dev/ttyUSB0:57600
```

**Explanation:**
- `/dev/ttyUSB0:57600` - Serial port at 57600 baud (autopilot)
- `udp:127.0.0.1:14550` - Send to Mission Planner
- `udp:127.0.0.1:14551` - Send to QGroundControl

### SITL Example

Route SITL (which uses UDP) to multiple endpoints:

```bash
# SITL outputs MAVLink on UDP port 14550
# Forward to additional endpoints
mavlink-routerd \
    --endpoint udp:127.0.0.1:14551 \
    --endpoint tcp:0.0.0.0:5760 \
    udp:127.0.0.1:14550
```

---

## Configuration File

For complex setups, use a configuration file.

### Configuration File Location

- Default: `/etc/mavlink-router/main.conf`
- Custom: `mavlink-routerd -c /path/to/config.conf`

### Basic Configuration

**File:** `basic_config.conf`

```ini
[General]
# TCP port for configuration/status
TcpServerPort = 5790

# Log all MAVLink traffic
Log = /var/log/mavlink-router
# MaxLogFiles = 10

[UartEndpoint autopilot]
Device = /dev/ttyUSB0
Baud = 57600

[UdpEndpoint missionplanner]
Mode = Normal
Address = 127.0.0.1
Port = 14550

[UdpEndpoint qgroundcontrol]
Mode = Normal
Address = 127.0.0.1
Port = 14551
```

**Run with config:**
```bash
mavlink-routerd -c basic_config.conf
```

---

## Configuration Examples

### Example 1: SITL with Multiple GCS

**Scenario:** Route SITL to Mission Planner and QGroundControl

**File:** `sitl_multi_gcs.conf`

```ini
[General]
TcpServerPort = 5790

# SITL source (UDP input)
[UdpEndpoint sitl]
Mode = Normal
Address = 127.0.0.1
Port = 14550

# Mission Planner
[UdpEndpoint missionplanner]
Mode = Normal
Address = 127.0.0.1
Port = 14560

# QGroundControl
[UdpEndpoint qgc]
Mode = Normal
Address = 127.0.0.1
Port = 14570

# Python scripts
[UdpEndpoint scripts]
Mode = Normal
Address = 127.0.0.1
Port = 14580
```

**Usage:**
```bash
# Start SITL
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane -L CMAC --console --map

# In another terminal, start router
mavlink-routerd -c sitl_multi_gcs.conf

# Connect Mission Planner to 127.0.0.1:14560
# Connect QGC to UDP port 14570
# Python scripts connect to 127.0.0.1:14580
```

---

### Example 2: Companion Computer (Raspberry Pi)

**Scenario:** Raspberry Pi with autopilot on serial, routing to onboard scripts and remote GCS

**File:** `companion_router.conf`

```ini
[General]
TcpServerPort = 5790
Log = /home/pi/mavlink-logs
MaxLogFiles = 20

# Autopilot on serial
[UartEndpoint autopilot]
Device = /dev/ttyAMA0
Baud = 921600

# Onboard scripts (localhost)
[UdpEndpoint local_scripts]
Mode = Normal
Address = 127.0.0.1
Port = 14550

# Remote GCS over WiFi
[UdpEndpoint remote_gcs]
Mode = Normal
Address = 192.168.1.100
Port = 14550

# TCP server for dynamic connections
[TcpEndpoint tcp_server]
Mode = Server
Port = 5760
```

**Setup on Raspberry Pi:**
```bash
sudo systemctl enable mavlink-router@companion_router
sudo systemctl start mavlink-router@companion_router
```

---

### Example 3: Telemetry Radio Setup

**Scenario:** Telemetry radio on USB, multiple local applications

**File:** `telemetry_radio.conf`

```ini
[General]
TcpServerPort = 5790

# Telemetry radio
[UartEndpoint telemetry]
Device = /dev/ttyUSB0
Baud = 57600

# Mission Planner
[UdpEndpoint mp]
Mode = Normal
Address = 127.0.0.1
Port = 14550

# Custom monitoring script
[UdpEndpoint monitor]
Mode = Normal
Address = 127.0.0.1
Port = 14555

# Log traffic
Log = /home/user/flight_logs
```

---

### Example 4: Multi-Vehicle Setup

**Scenario:** Two vehicles, separate routing

**File:** `multi_vehicle.conf`

```ini
[General]
TcpServerPort = 5790

# Vehicle 1 (System ID 1)
[UartEndpoint vehicle1]
Device = /dev/ttyUSB0
Baud = 57600
Filter = 1  # Only system ID 1

# Vehicle 2 (System ID 2)
[UartEndpoint vehicle2]
Device = /dev/ttyUSB1
Baud = 57600
Filter = 2  # Only system ID 2

# GCS for both vehicles
[UdpEndpoint gcs]
Mode = Normal
Address = 127.0.0.1
Port = 14550
```

---

## Endpoint Types

### UartEndpoint (Serial)

```ini
[UartEndpoint name]
Device = /dev/ttyUSB0
Baud = 57600
# FlowControl = false
```

**Baud rates:** 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600

---

### UdpEndpoint

```ini
[UdpEndpoint name]
Mode = Normal
Address = 127.0.0.1
Port = 14550
# BindPort = 0  # Port to bind locally
```

**Modes:**
- `Normal`: Send and receive
- `Eavesdropping`: Receive only (don't send back to source)

---

### TcpEndpoint

```ini
[TcpEndpoint name]
Mode = Server
Port = 5760
# Address = 192.168.1.100  # For client mode
```

**Modes:**
- `Server`: Listen for connections
- `Client`: Connect to remote server

---

## Advanced Features

### Message Filtering

Filter by system ID:

```ini
[UartEndpoint autopilot]
Device = /dev/ttyUSB0
Baud = 57600
Filter = 1  # Only system ID 1
```

### Logging

```ini
[General]
Log = /var/log/mavlink
MaxLogFiles = 50
DebugLogLevel = info  # error, warning, info, debug
```

Logs are in MAVLink `.bin` format, viewable with Mission Planner or MAVExplorer.

### System ID Assignment

mavlink-router passes through system IDs unchanged. To change system ID, modify autopilot parameter:

```bash
param set SYSID_THISMAV 1
```

---

## Running as a Service

### Create systemd service

**File:** `/etc/systemd/system/mavlink-router.service`

```ini
[Unit]
Description=MAVLink Router
After=network.target

[Service]
ExecStart=/usr/local/bin/mavlink-routerd -c /etc/mavlink-router/main.conf
Restart=on-failure
User=root

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable mavlink-router
sudo systemctl start mavlink-router
sudo systemctl status mavlink-router
```

---

## Troubleshooting

### Router not starting

**Check logs:**
```bash
journalctl -u mavlink-router -f
```

**Common issues:**
- Serial port permissions: Add user to `dialout` group
  ```bash
  sudo usermod -a -G dialout $USER
  # Logout and login
  ```
- Port already in use: Check for other MAVLink connections
- Invalid configuration: Verify config file syntax

### No data on endpoints

**Check:**
1. Is autopilot sending MAVLink? Connect directly to verify.
2. Are endpoints configured correctly?
3. Check firewall: `sudo ufw allow 14550/udp`
4. Use `tcpdump` to verify packets:
   ```bash
   sudo tcpdump -i lo -n port 14550
   ```

### Multiple routers conflict

Only one process can listen on a UDP port. If SITL and router both try to use 14550:

**Solution:** Configure SITL to use different port:
```bash
Tools/autotest/sim_vehicle.py -v ArduPlane --out=127.0.0.1:14540
```

Then configure router to listen on 14540.

---

## Testing mavlink-router

### Simple Test

Terminal 1 - Start router:
```bash
mavlink-routerd --endpoint udp:127.0.0.1:14560 udp:127.0.0.1:14550
```

Terminal 2 - Run SITL:
```bash
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane -L CMAC --console --map
```

Terminal 3 - Connect with pymavlink:
```python
from pymavlink import mavutil
master = mavutil.mavlink_connection('udp:127.0.0.1:14560')
master.wait_heartbeat()
print("Connected via router!")
```

---

## Use Cases with ArduPilot

### 1. Development Setup

```
SITL ─→ mavlink-router ─┬─→ MAVProxy (debugging)
                         ├─→ Mission Planner (mission planning)
                         ├─→ Python scripts (automation)
                         └─→ Log file
```

### 2. Flight Test Setup

```
Telemetry Radio ─→ mavlink-router ─┬─→ Mission Planner (pilot)
                                    ├─→ QGC (observer)
                                    └─→ Data logger
```

### 3. Companion Computer

```
Autopilot ─→ mavlink-router ─┬─→ Vision system
                              ├─→ AI/ML application
                              ├─→ Remote GCS (WiFi)
                              └─→ Backup telemetry (LTE)
```

---

## Configuration File Reference

### Complete Example

```ini
[General]
# TCP port for status queries
TcpServerPort = 5790

# Enable logging
Log = /var/log/mavlink
MaxLogFiles = 20
DebugLogLevel = info

# Report statistics interval (seconds)
ReportStats = 60

# Autopilot serial connection
[UartEndpoint autopilot]
Device = /dev/ttyUSB0
Baud = 921600
FlowControl = false

# Local GCS applications
[UdpEndpoint gcs_local]
Mode = Normal
Address = 127.0.0.1
Port = 14550

# Remote GCS over network
[UdpEndpoint gcs_remote]
Mode = Normal
Address = 192.168.1.100
Port = 14550

# TCP server for dynamic connections
[TcpEndpoint tcp_clients]
Mode = Server
Port = 5760

# Companion computer internal routing
[UdpEndpoint internal]
Mode = Normal
Address = 127.0.0.1
Port = 14540
```

---

## Performance Considerations

### Message Load

mavlink-router is lightweight and can handle:
- 100+ messages/second per endpoint
- 10+ endpoints simultaneously
- Minimal CPU impact (<1% on modern systems)

### Bandwidth

Calculate bandwidth for planning:
- Typical MAVLink message: ~50-100 bytes
- At 50 Hz (50 messages/sec): ~5 KB/s per endpoint
- 5 endpoints: ~25 KB/s total

---

## Additional Resources

- [mavlink-router GitHub](https://github.com/mavlink-router/mavlink-router)
- [MAVLink Protocol](https://mavlink.io/en/)
- [ArduPilot MAVLink](https://ardupilot.org/dev/docs/mavlink-basics.html)
- [Main Onboarding Guide](../../../Documents/ArduPilot_Onboarding_Guide.md)

---

**Last Updated:** 2026-02-03
