# Log Retrieval Guide

How to download and access ArduPilot logs from SITL and hardware.

---

## Retrieving Logs from SITL

### Method 1: Direct File Access

```bash
cd ~/ardupilot/ArduPlane/logs/
ls -lh

cp ~/ardupilot/ArduPlane/logs/*.BIN ~/my_logs/
```

### Method 2: MAVProxy

```bash
log list
log download 1
log download latest
log erase
```

---

## Retrieving Logs from Hardware

### Method 1: MAVProxy (Recommended)

```bash
mavproxy.py --master=/dev/ttyUSB0 --baudrate=57600
mavproxy.py --master=udp:127.0.0.1:14550
```

```bash
log list
log download 5          # Saves as log_5.bin
log downloadall
log download latest
log erase 5
log erase all
```

### Method 2: Mission Planner

1. Connect → Click "Connect"
2. DATA tab → DataFlash Logs
3. "Download All Logs" or select specific logs
4. Logs saved to `C:\Users\<username>\Documents\Mission Planner\logs\`

### Method 3: QGroundControl

1. Connect to vehicle
2. Analyze icon → Log Download
3. Select and click "Download"
4. Default: `~/Documents/QGroundControl/Logs/`

### Method 4: Direct SD Card Access

1. Power off autopilot
2. Remove SD card, insert into computer
3. Navigate to `APM/LOGS/`
4. Copy `.BIN` files
5. Safely eject, re-insert

Fastest method, works even if autopilot won't boot. Requires physical access.

---

## Download Performance

| Log Size | Method         | Speed      | Time      |
| -------- | -------------- | ---------- | --------- |
| 10MB     | USB 921600     | ~90 KB/s   | ~2 min    |
| 10MB     | USB 115200     | ~10 KB/s   | ~17 min   |
| 10MB     | Radio 57600    | ~5 KB/s    | ~33 min   |
| 10MB     | SD Card        | USB 3.0    | ~10 sec   |

Speed up: use `mavproxy.py --baudrate=921600` or direct SD card access.

---

## Log File Organization

```text
my_logs/
├── 2026-02-03_flight_01/
│   ├── 00000001.BIN
│   ├── params_before.param
│   └── notes.txt
└── archived/
    └── 2026-02-02/
```

Rename logs descriptively:

```text
2026-02-03_SITL_square_pattern_test_01.BIN
2026-02-03_hardware_maiden_flight.BIN
```

---

## Verifying Log Integrity

```bash
ls -lh *.BIN
# Short SITL flight: 500KB - 2MB
# 5-min hardware flight: 5MB - 20MB

mavlogdump.py --types MSG 00000001.BIN | head
```

---

## Troubleshooting

### Can't Connect to Autopilot

```bash
# Linux
ls /dev/ttyUSB* /dev/ttyACM*

param show SERIAL0_BAUD
```

Try different USB cable, port, or baud rate (115200, 57600).

### Download Fails

- Retry (may be RF interference)
- Use USB instead of radio
- Check SD card health

### No Logs Available

```bash
param show LOG_BACKEND_TYPE
# Should be 1, not 0
```

Check vehicle was armed, SD card is inserted and formatted FAT32.

### Log File Corrupted

```bash
mavlogdump.py --robust logfile.BIN > output.txt
```

Re-download or use SD card direct access.

---

## Scripting Log Retrieval

```bash
#!/bin/bash
# download_latest_log.sh
PORT="/dev/ttyUSB0"
BAUD="115200"
OUTPUT_DIR="$HOME/ardupilot_logs"

mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

mavproxy.py --master="$PORT" --baudrate="$BAUD" --cmd="log download latest; exit"
ls -lh *.bin
```

```python
#!/usr/bin/env python3
from pymavlink import mavutil
import sys

def download_logs(connection_string):
    master = mavutil.mavlink_connection(connection_string)
    master.wait_heartbeat()
    print(f"Connected to system {master.target_system}")

    master.mav.log_request_list_send(
        master.target_system,
        master.target_component,
        0, 0xffff
    )
    print("Log list requested. Use MAVProxy for full download.")

if __name__ == "__main__":
    conn = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB0"
    download_logs(conn)
```

---

After retrieval: [LOG_ANALYSIS_GUIDE.md](LOG_ANALYSIS_GUIDE.md)

**Author:** Patrick Kelly (@Kuscko)
