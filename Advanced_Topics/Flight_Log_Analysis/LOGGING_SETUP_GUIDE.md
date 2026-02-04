# ArduPilot Logging Setup Guide

## Overview

ArduPilot's DataFlash logging system records detailed telemetry data during flight for post-flight analysis. Logs are essential for debugging, tuning, and performance analysis.

---

## Log Storage

### SITL
- Logs stored in: `~/ardupilot/ArduPlane/logs/`
- Format: `.BIN` files (binary)
- Automatically created each time SITL runs

### Hardware
- Logs stored on SD card or internal flash
- Location depends on board (usually microSD card)
- Log files: `YYYY-MM-DD/HH-MM-SS.BIN`

---

## Essential Logging Parameters

### LOG_BACKEND_TYPE
**Default:** 1 (Block logging)
**Options:**
- 0 = Disabled
- 1 = Block (recommended for most uses)
- 2 = Mavlink (streaming over telemetry)
- 3 = Block and Mavlink (both)

```bash
param set LOG_BACKEND_TYPE 1
```

### LOG_FILE_DSRMROT
**Purpose:** Disarm rotation - creates new log file on each arm/disarm cycle
**Default:** 0
**Recommended:** 1

```bash
param set LOG_FILE_DSRMROT 1
```

### LOG_DISARMED
**Purpose:** Log while disarmed
**Default:** 0 (off)
**Use:** Set to 1 for troubleshooting pre-arm issues

```bash
param set LOG_DISARMED 0  # Only log while armed (saves space)
param set LOG_DISARMED 1  # Log continuously (for pre-arm debugging)
```

### LOG_REPLAY
**Purpose:** Log extra data for SITL replay
**Default:** 0
**Use:** Set to 1 only when needed for replay debugging

```bash
param set LOG_REPLAY 0  # Normal operation
param set LOG_REPLAY 1  # Enable replay logging
```

---

## Message Type Selection

ArduPilot logs different message types. Control what gets logged with `LOG_BITMASK`:

### LOG_BITMASK
**Default:** 176126 (or board-specific)
**Type:** Bitmask of message types to log

Common useful values:
```bash
# Comprehensive logging (large log files)
param set LOG_BITMASK 1048575  # All messages (2^20-1)

# Balanced logging (recommended)
param set LOG_BITMASK 176126  # Default on most boards

# Minimal logging (save space)
param set LOG_BITMASK 131071  # Basic flight data only
```

### Message Type Bits

| Bit | Value | Message Type | Description |
|-----|-------|--------------|-------------|
| 0 | 1 | ATTITUDE_FAST | Fast attitude data |
| 1 | 2 | ATTITUDE_MED | Medium rate attitude |
| 2 | 4 | GPS | GPS position data |
| 3 | 8 | PM | Performance monitoring |
| 4 | 16 | THR | Throttle/TECS data |
| 5 | 32 | NTUN | Navigation tuning |
| 6 | 64 | MODE | Mode changes |
| 7 | 128 | IMU | IMU data |
| 8 | 256 | CMD | Mission commands |
| 9 | 512 | CURRENT | Current sensors |
| 10 | 1024 | COMPASS | Magnetometer |
| 11 | 2048 | TECS | TECS controller |
| 12 | 4096 | CAMERA | Camera triggers |
| 13 | 8192 | RC | RC input |
| 14 | 16384 | ARM_DISARM | Arm/disarm events |
| 15 | 32768 | IMU_RAW | Raw IMU (high rate) |

**Example:** To log GPS (4) + IMU (128) + ATTITUDE (1) + TECS (2048):
```bash
# 4 + 128 + 1 + 2048 = 2181
param set LOG_BITMASK 2181
```

---

## Recommended Configurations

### For Tuning (TECS, PID)
```bash
param set LOG_BACKEND_TYPE 1
param set LOG_FILE_DSRMROT 1
param set LOG_DISARMED 0
param set LOG_BITMASK 176126  # Includes TECS, NTUN, ATT, IMU
```

### For Debugging Pre-arm Issues
```bash
param set LOG_DISARMED 1  # Log before arming
param set LOG_BITMASK 1048575  # Log everything
```

### For Long Flights (Save Space)
```bash
param set LOG_BITMASK 131071  # Essentials only
param set LOG_FILE_DSRMROT 1
```

### For Vibration Analysis
```bash
param set LOG_BITMASK 176126
# Ensure bits 7 (IMU) and 15 (IMU_RAW) are set
# 128 + 32768 = 32896
param set LOG_BITMASK 32896  # Or combine with other bits
```

---

## Enabling Logging Step-by-Step

### In SITL
```bash
# Start SITL
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map

# In MAVProxy, configure logging
param set LOG_BACKEND_TYPE 1
param set LOG_FILE_DSRMROT 1
param set LOG_BITMASK 176126

# Save parameters
param save

# Arm and fly - logs will be created
arm throttle
# ... fly ...
disarm

# Find logs
ls ~/ardupilot/ArduPlane/logs/
```

### On Hardware
```bash
# Connect via MAVProxy or Mission Planner
# Set parameters:
param set LOG_BACKEND_TYPE 1
param set LOG_FILE_DSRMROT 1
param set LOG_BITMASK 176126

# Write to SD card
param save

# Fly and land
# Download logs via MAVProxy or Mission Planner
```

---

## Verifying Logging is Working

### Check Parameters
```bash
param show LOG_*
```

Expected output:
```
LOG_BACKEND_TYPE  1.000000
LOG_BITMASK       176126.000000
LOG_DISARMED      0.000000
LOG_FILE_DSRMROT  1.000000
LOG_REPLAY        0.000000
```

### Check Log Files

**SITL:**
```bash
ls -lh ~/ardupilot/ArduPlane/logs/
# Should see .BIN files after arming
```

**Hardware:**
```bash
# In MAVProxy
log list
# Should show available logs on SD card
```

---

## Troubleshooting

### No Logs Created

**Problem:** No .BIN files after flight

**Solutions:**
1. Check LOG_BACKEND_TYPE is not 0
   ```bash
   param show LOG_BACKEND_TYPE
   param set LOG_BACKEND_TYPE 1
   ```

2. Verify SD card is inserted and formatted (FAT32)

3. Check disk space:
   ```bash
   # In MAVProxy
   status
   # Look for "Log: " line
   ```

4. Ensure you armed the vehicle:
   ```bash
   # Logging usually only happens while armed
   # Unless LOG_DISARMED = 1
   ```

### Log Files Too Large

**Problem:** SD card fills up quickly

**Solutions:**
1. Reduce LOG_BITMASK (log fewer message types)
2. Enable LOG_FILE_DSRMROT (separate files per flight)
3. Download and delete old logs regularly

### Incomplete Logs

**Problem:** Log stops mid-flight

**Solutions:**
1. Check SD card health
2. Verify sufficient disk space
3. Check for high CPU load (use SCHED messages in log)

---

## Log File Format

ArduPilot logs use a binary format (.BIN) that must be converted for analysis.

### File Structure
- **Header:** Flight controller type, firmware version
- **Messages:** Time-stamped data packets
- **Types:** FMT (format definitions), ATT (attitude), GPS, IMU, etc.

### Converting Logs

**To CSV:**
```bash
# Using MAVExplorer
mavlogdump.py --format csv logfile.BIN > logfile.csv
```

**To MATLAB:**
```bash
mavlogdump.py --format mat logfile.BIN -o logfile.mat
```

**To KML (Google Earth):**
```bash
mavlogdump.py --format kml logfile.BIN > flight.kml
```

---

## Sample Parameter Sets

### params_logging_standard.param
```
# Standard logging configuration
LOG_BACKEND_TYPE,1
LOG_FILE_DSRMROT,1
LOG_DISARMED,0
LOG_REPLAY,0
LOG_BITMASK,176126
```

### params_logging_comprehensive.param
```
# Comprehensive logging (large files)
LOG_BACKEND_TYPE,1
LOG_FILE_DSRMROT,1
LOG_DISARMED,1
LOG_REPLAY,1
LOG_BITMASK,1048575
```

### params_logging_minimal.param
```
# Minimal logging (save space)
LOG_BACKEND_TYPE,1
LOG_FILE_DSRMROT,1
LOG_DISARMED,0
LOG_REPLAY,0
LOG_BITMASK,131071
```

---

## Best Practices

1. **Always Enable Logging:** Logs are essential for debugging crashes
2. **Use LOG_FILE_DSRMROT:** Separate files make analysis easier
3. **Save Pre-flight Parameters:** `param save backup.param` before every flight
4. **Download Logs Regularly:** Don't let SD card fill up
5. **Keep Logs Organized:** Name logs by date and flight purpose
6. **Archive Important Logs:** Keep logs from incidents/good flights

---

## Next Steps

After setting up logging:
1. Fly a test flight and collect logs
2. Download logs using [LOG_RETRIEVAL_GUIDE.md](LOG_RETRIEVAL_GUIDE.md)
3. Analyze logs using [LOG_ANALYSIS_GUIDE.md](LOG_ANALYSIS_GUIDE.md)

---

**Author:** Patrick Kelly (@Kuscko)
**Version:** 1.0
**Last Updated:** 2026-02-03

**References:**
- [ArduPilot Logging Documentation](https://ardupilot.org/copter/docs/common-downloading-and-analyzing-data-logs-in-mission-planner.html)
- [DataFlash Log Messages](https://ardupilot.org/copter/docs/logmessages.html)
