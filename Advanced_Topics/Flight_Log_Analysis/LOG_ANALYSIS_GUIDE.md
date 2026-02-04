# Flight Log Analysis Guide

## Overview

This guide covers analyzing ArduPilot logs using Mission Planner, MAVExplorer, and UAV Log Viewer.

---

## Analysis Tools Comparison

| Tool | Platform | Best For | Difficulty |
|------|----------|----------|------------|
| **Mission Planner** | Windows | General review, quick checks | Easy |
| **MAVExplorer** | Cross-platform | Advanced analysis, graphing | Medium |
| **UAV Log Viewer** | Web-based | Quick visualization | Easy |

---

## Mission Planner Log Analysis

### Opening a Log

1. Launch Mission Planner
2. Click **DATA** tab
3. Click **DataFlash Logs** button
4. Click **Review a Log**
5. Select .BIN file
6. Wait for log to load

### Main View

**Left Panel:** Message types (ATT, GPS, TECS, etc.)
**Center:** Graph display
**Bottom:** Time slider

### Quick Health Checks

**Check 1: EKF Health**
- Select **EKF** messages
- Graph: `EKF.VN` (velocity north variance)
- Good: < 0.25
- Warning: 0.25-0.5
- Bad: > 0.5

**Check 2: Vibration**
- Select **VIBE** messages
- Graph: `VIBE.VibeX`, `VIBE.VibeY`, `VIBE.VibeZ`
- Good: < 30 m/s²
- Acceptable: 30-60 m/s²
- Bad: > 60 m/s²

**Check 3: GPS**
- Select **GPS** messages
- Graph: `GPS.NSats`, `GPS.HDop`
- Satellites: > 10 (good), 6-10 (ok), < 6 (poor)
- HDop: < 1.5 (good), 1.5-2.5 (ok), > 2.5 (poor)

**Check 4: Battery**
- Select **BATT** messages
- Graph: `BATT.Volt`, `BATT.Curr`
- Check voltage doesn't drop too low
- Verify current draw is reasonable

### Graphing Multiple Parameters

1. Select message type (e.g., **ATT**)
2. Check parameters to graph:
   - `ATT.Roll` - Actual roll angle
   - `ATT.Des Roll` - Desired roll angle
   - `ATT.Pitch` - Actual pitch
3. Click **Graph this data**
4. Add more by selecting another message type

### Common Issues and Patterns

**Oscillation (PID Tuning Needed)**
- Graph shows rapid back-and-forth
- Actual vs Desired has large gap
- Fix: Reduce P gain or increase D gain

**EKF Variance Spike**
- Sudden jump in EKF variance
- Usually GPS glitch or compass interference
- Check GPS and compass messages at same time

**Vibration Clipping**
- IMU values hitting limits (±16g or ±2000°/s)
- Severe vibration or physical impact
- Fix: Improve vibration damping, check propellers

### Pre-arm Check Failures

Search for message: `PreArm:`
- Lists what prevented arming
- Common: EKF variance, GPS lock, compass calibration

---

## MAVExplorer Analysis

### Installation

```bash
pip install --user MAVProxy
# MAVExplorer included with MAVProxy
```

### Launching MAVExplorer

```bash
# Basic usage
mavexplorer.py logfile.BIN

# Or via MAVProxy
mavproxy.py --load-module log
log load logfile.BIN
graph ATT.Roll ATT.DesRoll
```

### Command Syntax

```bash
# Graph a single parameter
graph GPS.Alt

# Graph multiple parameters
graph GPS.Alt BARO.Alt

# Graph with expressions
graph GPS.Alt-BARO.Alt

# Graph derived value
graph sqrt(GPS.Spd**2+GPS.VZ**2)

# Save graph
graph GPS.Alt --save gps_altitude.png
```

### Useful Expressions

**Altitude Error:**
```bash
graph GPS.Alt-BARO.Alt
```

**Total Speed:**
```bash
graph sqrt(GPS.Spd**2+GPS.VZ**2)
```

**Tracking Error:**
```bash
graph sqrt((GPS.NSats-15)**2)
```

**Roll Rate of Change:**
```bash
graph delta(ATT.Roll,'ATT.TimeUS')*1000000
```

### Message Filtering

```bash
# Only show when armed
graph GPS.Alt --condition="STAT.Armed==1"

# Only show AUTO mode (mode 10)
graph TECS.h --condition="MODE.Mode==10"

# Altitude above 50m
graph TECS.spd --condition="GPS.Alt>50"
```

### Exporting Data

```bash
# Export to CSV
mavlogdump.py --format csv logfile.BIN > output.csv

# Export specific messages
mavlogdump.py --types GPS,ATT --format csv logfile.BIN > gps_att.csv

# Export MAVLink messages
mavlogdump.py --format pymavlink logfile.BIN > output.py
```

---

## UAV Log Viewer

### Online Tool

**URL:** https://plot.ardupilot.org/
(or https://logs.px4.io/ for PX4 logs)

### Usage

1. Navigate to UAV Log Viewer website
2. Click **Upload Log** or drag .BIN file
3. Wait for processing
4. View interactive graphs

### Features

- **Auto-generated graphs:** Common parameters pre-graphed
- **Interactive:** Zoom, pan, select time ranges
- **Message browser:** View raw message data
- **Shareable links:** Share analysis with team

### When to Use

- Quick visualization without software installation
- Sharing logs with remote team members
- Cross-platform (works on any device with browser)

---

## Common Analysis Scenarios

### Scenario 1: Aircraft Won't Arm

**Check:**
1. Look for `PreArm:` messages
2. Check EKF variance (EKF.VN, EKF.VP)
3. Check GPS (GPS.NSats, GPS.HDop)
4. Check compass (COMPASS messages)

**Solution path:**
- EKF variance high → Wait longer, check compass calibration
- GPS issues → Move to open area, wait for more satellites
- Compass → Recalibrate, check for magnetic interference

### Scenario 2: Poor Altitude Hold

**Check:**
1. Graph `TECS.h` (target alt) vs `GPS.Alt` (actual alt)
2. Check `TECS.dh` (altitude error)
3. Look at `TECS.spd` vs `TECS.spddem` (speed tracking)

**Common causes:**
- TECS_TIME_CONST too high/low
- TECS_SPDWEIGHT imbalance
- Airspeed sensor issues (if equipped)

### Scenario 3: Vibration Problems

**Check:**
1. Graph `VIBE.VibeX/Y/Z`
2. Check `IMU.AccX/Y/Z` for clipping
3. Look at `BATT.Volt` for power fluctuations

**Solutions:**
- Add vibration damping
- Balance propellers
- Check motor mounts
- Verify ESC calibration

### Scenario 4: GPS Glitches

**Check:**
1. Graph `GPS.NSats` (should be stable)
2. Check `GPS.HDop` (should be < 2.0)
3. Look for sudden jumps in `GPS.Lat/Lng`

**Causes:**
- EMI interference from ESCs/motors
- Poor GPS antenna placement
- Multipath (reflections from surfaces)

### Scenario 5: Mode Changes/Failsafes

**Check:**
1. Look at `MODE` messages
2. Check `RC` messages for RC failsafe
3. Review `BATT` for battery failsafe
4. Check `GPS` for GPS failsafe

**Find when mode changed:**
```bash
# In MAVExplorer
graph MODE.Mode
# Look for transitions
```

---

## Advanced Analysis Techniques

### Spectral Analysis (FFT)

**In MAVExplorer:**
```bash
# Requires matplotlib and scipy
mavfft_isb.py logfile.BIN

# Analyzes vibration frequencies
# Identifies motor/prop imbalance frequencies
```

### Statistical Summary

```bash
# Generate statistics
mavlogdump.py --types GPS logfile.BIN | python -c "
import sys
import statistics
alts = []
for line in sys.stdin:
    if 'Alt' in line:
        # Parse altitude values
        pass
print('Mean altitude:', statistics.mean(alts))
"
```

### Time Alignment

When comparing parameters from different message types:
```bash
# Use TimeUS for microsecond timestamps
# Or TimeMS for millisecond timestamps
graph GPS.Alt GPS.TimeUS ATT.Roll ATT.TimeUS
```

---

## Best Practices

1. **Check logs after every flight** - Don't let issues accumulate
2. **Compare to baseline** - Know what "good" looks like
3. **Focus on changes** - What's different from last flight?
4. **Check timestamps** - Correlate events in time
5. **Save problem logs** - Build a reference library
6. **Document findings** - Note what you discovered

---

## Quick Reference: Critical Parameters

| Parameter | Message | Good Range | Action if Outside |
|-----------|---------|------------|-------------------|
| Vibration X/Y/Z | VIBE.VibeX/Y/Z | < 30 | Check damping, props |
| EKF Velocity | EKF.VN/VE | < 0.25 | Check GPS, compass |
| EKF Position | EKF.PN/PE | < 0.25 | Wait for GPS lock |
| GPS Satellites | GPS.NSats | > 10 | Move to open area |
| GPS HDop | GPS.HDop | < 1.5 | Improve antenna |
| Battery Voltage | BATT.Volt | > 10.5V | Land soon |
| Clipping | IMU.Acc* | < ±16g | Reduce vibration |

---

## Next Steps

- Practice with sample logs: See [sample_logs/](sample_logs/)
- Deep dive into TECS: [TECS_ANALYSIS_TUTORIAL.md](TECS_ANALYSIS_TUTORIAL.md)
- Learn vibration analysis: [VIBRATION_ANALYSIS_TUTORIAL.md](VIBRATION_ANALYSIS_TUTORIAL.md)
- Automate with Python: [log_parser.py](log_parser.py)

---

**Author:** Patrick Kelly (@Kuscko)
**Version:** 1.0

**References:**
- [ArduPilot Log Analysis](https://ardupilot.org/copter/docs/common-downloading-and-analyzing-data-logs-in-mission-planner.html)
- [MAVExplorer Documentation](https://ardupilot.org/dev/docs/using-mavexplorer-for-log-analysis.html)
