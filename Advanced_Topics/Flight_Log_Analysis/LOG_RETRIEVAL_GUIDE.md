# Log Retrieval Guide

## Overview

This guide covers how to download and access ArduPilot logs from SITL and hardware for analysis.

---

## Retrieving Logs from SITL

### Method 1: Direct File Access

SITL logs are stored as files in the ArduPlane directory:

```bash
cd ~/ardupilot/ArduPlane/logs/

# List log files
ls -lh

# Example output:
# -rw-r--r-- 1 user user 2.3M Feb 3 10:15 00000001.BIN
# -rw-r--r-- 1 user user 1.8M Feb 3 10:30 00000002.BIN
```

**Copy logs to working directory:**
```bash
cp ~/ardupilot/ArduPlane/logs/*.BIN ~/my_logs/
```

### Method 2: MAVProxy

While SITL is running:
```bash
# In MAVProxy console
log list

# Download specific log
log download 1

# Download latest log
log download latest

# Erase all logs
log erase
```

---

## Retrieving Logs from Hardware

### Method 1: MAVProxy (Recommended)

**Connect to autopilot:**
```bash
mavproxy.py --master=/dev/ttyUSB0 --baudrate=57600
# Or for network connection:
mavproxy.py --master=udp:127.0.0.1:14550
```

**List available logs:**
```bash
log list
```

Example output:
```
Log 1  numLogs 10
Log 2  numLogs 10
Log 3  numLogs 10
...
```

**Download specific log:**
```bash
# Download log number 5
log download 5

# Saves to current directory as: log_5.bin
```

**Download all logs:**
```bash
# Download all logs (can take a while!)
log downloadall
```

**Download latest log:**
```bash
log download latest
```

**Erase logs (use carefully!):**
```bash
# Erase a specific log
log erase 5

# Erase ALL logs
log erase all
```

### Method 2: Mission Planner

1. **Connect to autopilot:**
   - Click "Connect" button
   - Select COM port and baud rate

2. **Navigate to Data Flash Logs:**
   - Click "DATA" tab
   - Click "DataFlash Logs" button

3. **Download logs:**
   - Click "Download All Logs" or select specific logs
   - Choose save location
   - Wait for download (can take several minutes)

4. **Review downloaded logs:**
   - Logs saved to: `C:\Users\<username>\Documents\Mission Planner\logs\`
   - Or custom location if specified

### Method 3: QGroundControl

1. **Connect to vehicle**

2. **Navigate to Analyze Tools:**
   - Click "Analyze" icon (toolbar)
   - Select "Log Download"

3. **Download logs:**
   - Select logs to download
   - Click "Download"

4. **Save location:**
   - Default: `~/Documents/QGroundControl/Logs/`

### Method 4: Direct SD Card Access

**For boards with removable SD cards:**

1. Power off the autopilot
2. Remove SD card
3. Insert into computer
4. Navigate to log directory:
   - Usually: `APM/LOGS/`
   - Files: `YYYY-MM-DD/HH-MM-SS.BIN`
5. Copy .BIN files
6. Safely eject SD card
7. Re-insert into autopilot

**Pros:**
- Fastest method
- No telemetry connection needed
- Can access even if autopilot won't boot

**Cons:**
- Requires physical access
- Risk of corrupting SD card if not safely ejected
- Can't use while flying

---

## Log File Organization

### Recommended Directory Structure

```
my_logs/
├── 2026-02-03_flight_01/
│   ├── 00000001.BIN
│   ├── params_before.param
│   ├── notes.txt
│   └── analysis/
│       ├── graphs/
│       └── reports/
├── 2026-02-03_flight_02/
│   ├── 00000002.BIN
│   ├── params_before.param
│   └── notes.txt
└── archived/
    └── 2026-02-02/
        └── ...
```

### File Naming Best Practices

**Rename logs with descriptive names:**
```bash
# Before
00000001.BIN

# After
2026-02-03_SITL_square_pattern_test_01.BIN
2026-02-03_hardware_maiden_flight.BIN
2026-02-03_tecs_tuning_run_03.BIN
```

**Include in filename:**
- Date (YYYY-MM-DD)
- Platform (SITL/hardware/aircraft name)
- Test purpose
- Run number (if multiple tests)

---

## Verifying Log Integrity

### Check Log File Size

```bash
ls -lh *.BIN

# Typical sizes:
# Short SITL flight: 500KB - 2MB
# 5-minute hardware flight: 5MB - 20MB
# Full logging: Can be 50MB+
```

**Red flags:**
- File size is 0 bytes (corrupted or empty)
- File much smaller than expected (incomplete)
- File won't open in analysis tools

### Quick Log Validation

**Using mavlogdump.py:**
```bash
# Check if log is readable
mavlogdump.py --types MSG 00000001.BIN | head

# Should see firmware version and message types
# If errors appear, log may be corrupted
```

**Using Mission Planner:**
- Try to open log in "Review a Log"
- Should load without errors
- Check that FMT messages are present

---

## Download Performance Tips

### Speed Up Downloads

1. **Use MAVProxy over USB:**
   - USB is faster than radio telemetry
   - Connect directly to autopilot via USB

2. **Increase baud rate:**
   ```bash
   # 921600 baud (fast, but may not work on all systems)
   mavproxy.py --master=/dev/ttyUSB0 --baudrate=921600

   # 115200 baud (standard, reliable)
   mavproxy.py --master=/dev/ttyUSB0 --baudrate=115200
   ```

3. **Download specific logs:**
   - Don't use `log downloadall` if you only need recent logs
   - Use `log download latest` for most recent

4. **Direct SD card access:**
   - Fastest method if you have physical access

### Download Times (Approximate)

| Log Size | Method | Speed | Time |
|----------|--------|-------|------|
| 10MB | USB 921600 | ~90 KB/s | ~2 min |
| 10MB | USB 115200 | ~10 KB/s | ~17 min |
| 10MB | Radio 57600 | ~5 KB/s | ~33 min |
| 10MB | SD Card | USB 3.0 | ~10 sec |

---

## Troubleshooting

### Can't Connect to Autopilot

**Problem:** MAVProxy won't connect

**Solutions:**
1. Check USB cable (try different cable)
2. Verify correct port:
   ```bash
   # Linux
   ls /dev/ttyUSB* /dev/ttyACM*

   # Windows
   # Check Device Manager > Ports (COM & LPT)
   ```
3. Check baud rate matches autopilot:
   ```bash
   param show SERIAL0_BAUD
   ```
4. Try different baudrate (115200, 57600)

### Download Fails/Times Out

**Problem:** Log download starts but fails partway

**Solutions:**
1. Retry download (may be RF interference)
2. Use USB connection instead of radio
3. Move closer to vehicle (if using radio)
4. Reduce baudrate for more reliable transfer
5. Check SD card health (may be failing)

### No Logs Available

**Problem:** `log list` shows no logs

**Solutions:**
1. Verify logging was enabled:
   ```bash
   param show LOG_BACKEND_TYPE
   # Should be 1, not 0
   ```
2. Check if vehicle was armed (logs only created when armed)
3. Check SD card is inserted and formatted
4. Try reformatting SD card (FAT32)

### Log File Corrupted

**Problem:** Downloaded log won't open or has errors

**Solutions:**
1. Re-download the log
2. Try different download method (SD card access)
3. Use `mavlogdump.py` to check file:
   ```bash
   mavlogdump.py --robust logfile.BIN > output.txt
   # --robust flag tries to recover corrupted logs
   ```
4. If still corrupted, log may have been corrupted during flight (power loss, SD card issue)

---

## Scripting Log Retrieval

### Bash Script: Download Latest Log

```bash
#!/bin/bash
# download_latest_log.sh
# Downloads latest log from autopilot

PORT="/dev/ttyUSB0"
BAUD="115200"
OUTPUT_DIR="$HOME/ardupilot_logs"

mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

echo "Connecting to autopilot on $PORT..."
mavproxy.py --master="$PORT" --baudrate="$BAUD" --cmd="log download latest; exit"

echo "Log downloaded to $OUTPUT_DIR"
ls -lh *.bin
```

**Usage:**
```bash
chmod +x download_latest_log.sh
./download_latest_log.sh
```

### Python Script: Batch Download

```python
#!/usr/bin/env python3
"""
Download all logs from autopilot
"""
from pymavlink import mavutil
import sys

def download_logs(connection_string):
    # Connect to autopilot
    master = mavutil.mavlink_connection(connection_string)
    master.wait_heartbeat()
    print(f"Connected to system {master.target_system}")

    # Request log list
    master.mav.log_request_list_send(
        master.target_system,
        master.target_component,
        0, 0xffff
    )

    # Wait for log entries
    # (Full implementation would process LOG_ENTRY messages)
    print("Log list requested. Use MAVProxy for full download.")

if __name__ == "__main__":
    conn = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB0"
    download_logs(conn)
```

---

## Next Steps

After retrieving logs:
1. Organize logs in descriptive folders
2. Verify log integrity
3. Proceed to [LOG_ANALYSIS_GUIDE.md](LOG_ANALYSIS_GUIDE.md) for analysis
4. Use [log_parser.py](log_parser.py) for automated analysis

---

**Author:** Patrick Kelly (@Kuscko)
**Version:** 1.0
**Last Updated:** 2026-02-03

**References:**
- [ArduPilot Log Download](https://ardupilot.org/copter/docs/common-downloading-and-analyzing-data-logs-in-mission-planner.html)
- [MAVProxy Log Commands](http://ardupilot.github.io/MAVProxy/html/index.html)
