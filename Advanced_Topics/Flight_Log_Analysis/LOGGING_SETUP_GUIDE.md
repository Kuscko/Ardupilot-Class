# ArduPilot Logging Setup Guide

ArduPilot's DataFlash logging system records detailed telemetry for post-flight analysis, debugging, and tuning.

---

## Log Storage

- **SITL:** `~/ardupilot/ArduPlane/logs/` — `.BIN` files created each run
- **Hardware:** SD card, usually `APM/LOGS/YYYY-MM-DD/HH-MM-SS.BIN`

---

## Essential Logging Parameters

### LOG_BACKEND_TYPE

- 0 = Disabled | 1 = Block (recommended) | 2 = MAVLink | 3 = Both

```bash
param set LOG_BACKEND_TYPE 1
```

### LOG_FILE_DSRMROT

Creates a new log file on each arm/disarm cycle.

```bash
param set LOG_FILE_DSRMROT 1
```

### LOG_DISARMED

```bash
param set LOG_DISARMED 0  # Only log while armed (saves space)
param set LOG_DISARMED 1  # Log continuously (pre-arm debugging)
```

### LOG_REPLAY

```bash
param set LOG_REPLAY 0  # Normal operation
param set LOG_REPLAY 1  # Enable replay logging
```

---

## LOG_BITMASK

| Bit | Value  | Message Type   | Description             |
| --- | ------ | -------------- | ----------------------- |
| 0   | 1      | ATTITUDE_FAST  | Fast attitude data      |
| 1   | 2      | ATTITUDE_MED   | Medium rate attitude    |
| 2   | 4      | GPS            | GPS position data       |
| 3   | 8      | PM             | Performance monitoring  |
| 4   | 16     | THR            | Throttle/TECS data      |
| 5   | 32     | NTUN           | Navigation tuning       |
| 6   | 64     | MODE           | Mode changes            |
| 7   | 128    | IMU            | IMU data                |
| 8   | 256    | CMD            | Mission commands        |
| 9   | 512    | CURRENT        | Current sensors         |
| 10  | 1024   | COMPASS        | Magnetometer            |
| 11  | 2048   | TECS           | TECS controller         |
| 12  | 4096   | CAMERA         | Camera triggers         |
| 13  | 8192   | RC             | RC input                |
| 14  | 16384  | ARM_DISARM     | Arm/disarm events       |
| 15  | 32768  | IMU_RAW        | Raw IMU (high rate)     |

```bash
param set LOG_BITMASK 1048575   # All messages
param set LOG_BITMASK 176126    # Balanced (default)
param set LOG_BITMASK 131071    # Minimal
```

---

## Recommended Configurations

### For Tuning (TECS, PID)

```bash
param set LOG_BACKEND_TYPE 1
param set LOG_FILE_DSRMROT 1
param set LOG_DISARMED 0
param set LOG_BITMASK 176126
```

### For Debugging Pre-arm Issues

```bash
param set LOG_DISARMED 1
param set LOG_BITMASK 1048575
```

### For Long Flights (Save Space)

```bash
param set LOG_BITMASK 131071
param set LOG_FILE_DSRMROT 1
```

### For Vibration Analysis

```bash
param set LOG_BITMASK 32896   # IMU (128) + IMU_RAW (32768)
```

---

## Enabling Logging

### In SITL

```bash
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map

param set LOG_BACKEND_TYPE 1
param set LOG_FILE_DSRMROT 1
param set LOG_BITMASK 176126
param save

arm throttle
# ... fly ...
disarm

ls ~/ardupilot/ArduPlane/logs/
```

---

## Verifying Logging

```bash
param show LOG_*
```

Expected:

```text
LOG_BACKEND_TYPE  1.000000
LOG_BITMASK       176126.000000
LOG_DISARMED      0.000000
LOG_FILE_DSRMROT  1.000000
LOG_REPLAY        0.000000
```

```bash
# SITL
ls -lh ~/ardupilot/ArduPlane/logs/

# Hardware (MAVProxy)
log list
```

---

## Converting Logs

```bash
# To CSV
mavlogdump.py --format csv logfile.BIN > logfile.csv

# To MATLAB
mavlogdump.py --format mat logfile.BIN -o logfile.mat

# To KML (Google Earth)
mavlogdump.py --format kml logfile.BIN > flight.kml
```

---

## Troubleshooting

### No Logs Created

```bash
param show LOG_BACKEND_TYPE
param set LOG_BACKEND_TYPE 1
```

- Verify SD card is inserted and formatted FAT32
- Ensure vehicle was armed (or set `LOG_DISARMED 1`)

### Log Files Too Large

- Reduce LOG_BITMASK
- Enable LOG_FILE_DSRMROT
- Download and delete old logs regularly

### Incomplete Logs

- Check SD card health
- Verify sufficient disk space

---

## Sample Parameter Sets

```text
# params_logging_standard.param
LOG_BACKEND_TYPE,1
LOG_FILE_DSRMROT,1
LOG_DISARMED,0
LOG_REPLAY,0
LOG_BITMASK,176126
```

```text
# params_logging_comprehensive.param
LOG_BACKEND_TYPE,1
LOG_FILE_DSRMROT,1
LOG_DISARMED,1
LOG_REPLAY,1
LOG_BITMASK,1048575
```

---

After setup, retrieve logs: [LOG_RETRIEVAL_GUIDE.md](LOG_RETRIEVAL_GUIDE.md) | Analyze logs: [LOG_ANALYSIS_GUIDE.md](LOG_ANALYSIS_GUIDE.md)

**Author:** Patrick Kelly (@Kuscko)
