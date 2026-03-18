# mavlink-router Guide

## What is mavlink-router?

mavlink-router routes MAVLink packets between multiple endpoints, allowing multiple GCS applications, companion computers, and custom scripts to communicate with a single autopilot simultaneously.

```
                    ┌─── Mission Planner (UDP)
                    │
Autopilot (Serial) ─┤─── QGroundControl (UDP)
                    │
                    ├─── Python Script (UDP)
                    │
                    └─── Remote GCS (TCP)
```

---

## Installation

```bash
sudo apt update
sudo apt install -y git meson ninja-build pkg-config gcc g++ systemd python3-pip

cd ~
git clone https://github.com/mavlink-router/mavlink-router.git
cd mavlink-router

meson setup build .
ninja -C build
sudo ninja -C build install
```

```bash
mavlink-routerd --version
```

---

## Basic Usage

### Command Line Mode

```bash
# Route from serial to two UDP endpoints
mavlink-routerd \
    --endpoint udp:127.0.0.1:14550 \
    --endpoint udp:127.0.0.1:14551 \
    /dev/ttyUSB0:57600
```

### SITL Example

```bash
# Forward SITL UDP output to additional endpoints
mavlink-routerd \
    --endpoint udp:127.0.0.1:14551 \
    --endpoint tcp:0.0.0.0:5760 \
    udp:127.0.0.1:14550
```

---

## Configuration File

Default location: `/etc/mavlink-router/main.conf`

Custom: `mavlink-routerd -c /path/to/config.conf`

### Basic Configuration

**File:** `basic_config.conf`

```ini
[General]
TcpServerPort = 5790
Log = /var/log/mavlink-router

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

```bash
mavlink-routerd -c basic_config.conf
```

---

## Configuration Examples

### Example 1: SITL with Multiple GCS

**File:** `sitl_multi_gcs.conf`

```ini
[General]
TcpServerPort = 5790

[UdpEndpoint sitl]
Mode = Normal
Address = 127.0.0.1
Port = 14550

[UdpEndpoint missionplanner]
Mode = Normal
Address = 127.0.0.1
Port = 14560

[UdpEndpoint qgc]
Mode = Normal
Address = 127.0.0.1
Port = 14570

[UdpEndpoint scripts]
Mode = Normal
Address = 127.0.0.1
Port = 14580
```

```bash
# Terminal 1: Start SITL
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane -L CMAC --console --map

# Terminal 2: Start router
mavlink-routerd -c sitl_multi_gcs.conf

# Connect Mission Planner to 127.0.0.1:14560
# Connect QGC to UDP 14570
# Python scripts connect to 127.0.0.1:14580
```

---

### Example 2: Companion Computer (Raspberry Pi)

**File:** `companion_router.conf`

```ini
[General]
TcpServerPort = 5790
Log = /home/pi/mavlink-logs
MaxLogFiles = 20

[UartEndpoint autopilot]
Device = /dev/ttyAMA0
Baud = 921600

[UdpEndpoint local_scripts]
Mode = Normal
Address = 127.0.0.1
Port = 14550

[UdpEndpoint remote_gcs]
Mode = Normal
Address = 192.168.1.100
Port = 14550

[TcpEndpoint tcp_server]
Mode = Server
Port = 5760
```

```bash
sudo systemctl enable mavlink-router@companion_router
sudo systemctl start mavlink-router@companion_router
```

---

### Example 3: Telemetry Radio Setup

**File:** `telemetry_radio.conf`

```ini
[General]
TcpServerPort = 5790

[UartEndpoint telemetry]
Device = /dev/ttyUSB0
Baud = 57600

[UdpEndpoint mp]
Mode = Normal
Address = 127.0.0.1
Port = 14550

[UdpEndpoint monitor]
Mode = Normal
Address = 127.0.0.1
Port = 14555

Log = /home/user/flight_logs
```

---

### Example 4: Multi-Vehicle Setup

**File:** `multi_vehicle.conf`

```ini
[General]
TcpServerPort = 5790

[UartEndpoint vehicle1]
Device = /dev/ttyUSB0
Baud = 57600
Filter = 1  # Only system ID 1

[UartEndpoint vehicle2]
Device = /dev/ttyUSB1
Baud = 57600
Filter = 2  # Only system ID 2

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
```

Baud rates: 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600

### UdpEndpoint

```ini
[UdpEndpoint name]
Mode = Normal        # Normal = send+receive, Eavesdropping = receive only
Address = 127.0.0.1
Port = 14550
```

### TcpEndpoint

```ini
[TcpEndpoint name]
Mode = Server        # Server = listen, Client = connect to remote
Port = 5760
```

---

## Advanced Features

### Message Filtering

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

Logs in MAVLink `.bin` format, viewable with Mission Planner or MAVExplorer.

### System ID

mavlink-router passes system IDs unchanged. Change in autopilot with: `param set SYSID_THISMAV 1`

---

## Running as a Service

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

```bash
sudo systemctl daemon-reload
sudo systemctl enable mavlink-router
sudo systemctl start mavlink-router
sudo systemctl status mavlink-router
```

---

## Troubleshooting

### Router not starting

```bash
journalctl -u mavlink-router -f
```

- Serial port permissions: `sudo usermod -a -G dialout $USER` (then re-login)
- Port already in use: check for other MAVLink connections
- Invalid config syntax

### No data on endpoints

1. Verify autopilot is sending MAVLink directly
2. Check endpoint configuration
3. `sudo ufw allow 14550/udp`
4. `sudo tcpdump -i lo -n port 14550`

### Multiple routers conflict

Configure SITL to use a different port:
```bash
Tools/autotest/sim_vehicle.py -v ArduPlane --out=127.0.0.1:14540
```
Then configure router to listen on 14540.

---

## Testing mavlink-router

Terminal 1 — Start router:
```bash
mavlink-routerd --endpoint udp:127.0.0.1:14560 udp:127.0.0.1:14550
```

Terminal 2 — Run SITL:
```bash
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane -L CMAC --console --map
```

Terminal 3 — Connect with pymavlink:
```python
from pymavlink import mavutil
master = mavutil.mavlink_connection('udp:127.0.0.1:14560')
master.wait_heartbeat()
print("Connected via router!")
```

---

## Use Cases with ArduPilot

**Development:**
```
SITL → mavlink-router ─┬─ MAVProxy (debugging)
                        ├─ Mission Planner
                        ├─ Python scripts
                        └─ Log file
```

**Flight Test:**
```
Telemetry Radio → mavlink-router ─┬─ Mission Planner (pilot)
                                   ├─ QGC (observer)
                                   └─ Data logger
```

**Companion Computer:**
```
Autopilot → mavlink-router ─┬─ Vision system
                             ├─ AI/ML application
                             ├─ Remote GCS (WiFi)
                             └─ Backup telemetry (LTE)
```

---

## Performance

mavlink-router handles 100+ messages/second per endpoint and 10+ simultaneous endpoints with <1% CPU impact. At 50 Hz with 5 endpoints: ~25 KB/s total bandwidth.

---

## Additional Resources

- [mavlink-router GitHub](https://github.com/mavlink-router/mavlink-router)
- [MAVLink Protocol](https://mavlink.io/en/)
- [ArduPilot MAVLink](https://ardupilot.org/dev/docs/mavlink-basics.html)
- [Main Onboarding Guide](../Onboarding_Documentation/ArduPilot_Onboarding_Guide.md)

---

**Last Updated:** 2026-02-03
