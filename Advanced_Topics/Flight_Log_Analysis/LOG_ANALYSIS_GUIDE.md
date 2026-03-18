# Flight Log Analysis Guide

Analyzing ArduPilot logs using Mission Planner, MAVExplorer, and UAV Log Viewer.

---

## Analysis Tools

| Tool                | Platform       | Best For                          | Difficulty |
| ------------------- | -------------- | --------------------------------- | ---------- |
| **Mission Planner** | Windows        | General review, quick checks      | Easy       |
| **MAVExplorer**     | Cross-platform | Advanced analysis, graphing       | Medium     |
| **UAV Log Viewer**  | Web-based      | Quick visualization               | Easy       |

---

## Mission Planner Log Analysis

**Opening a log:** DATA tab → DataFlash Logs → Review a Log → select .BIN file

### Quick Health Checks

**EKF Health** — select EKF messages, graph `EKF.VN`:

- Good: < 0.25 | Warning: 0.25–0.5 | Bad: > 0.5

**Vibration** — graph `VIBE.VibeX/Y/Z`:

- Good: < 30 m/s² | Acceptable: 30–60 | Bad: > 60

**GPS** — graph `GPS.NSats`, `GPS.HDop`:

- Satellites: > 10 good, 6–10 ok, < 6 poor
- HDop: < 1.5 good, 1.5–2.5 ok, > 2.5 poor

**Battery** — graph `BATT.Volt`, `BATT.Curr` — check voltage doesn't drop too low

### Common Patterns

- **Oscillation:** Rapid back-and-forth in attitude — reduce P gain or increase D gain
- **EKF variance spike:** GPS glitch or compass interference — check GPS and compass at same timestamp
- **Vibration clipping:** IMU values hitting ±16g — improve damping, check propellers

### Pre-arm Check Failures

Search for `PreArm:` messages — lists what prevented arming.

---

## MAVExplorer Analysis

### Installation

```bash
pip install --user MAVProxy
```

### Usage

```bash
mavexplorer.py logfile.BIN
```

### Command Syntax

```bash
graph GPS.Alt
graph GPS.Alt BARO.Alt
graph GPS.Alt-BARO.Alt
graph sqrt(GPS.Spd**2+GPS.VZ**2)
graph GPS.Alt --save gps_altitude.png
```

### Message Filtering

```bash
graph GPS.Alt --condition="STAT.Armed==1"
graph TECS.h --condition="MODE.Mode==10"
graph TECS.spd --condition="GPS.Alt>50"
```

### Exporting Data

```bash
mavlogdump.py --format csv logfile.BIN > output.csv
mavlogdump.py --types GPS,ATT --format csv logfile.BIN > gps_att.csv
```

---

## UAV Log Viewer

**URL:** <https://plot.ardupilot.org/>

Upload .BIN file for interactive graphs. Useful for quick visualization and sharing with remote team members.

---

## Common Analysis Scenarios

### Aircraft Won't Arm

1. Look for `PreArm:` messages
2. Check EKF variance (EKF.VN, EKF.VP)
3. Check GPS (GPS.NSats, GPS.HDop)
4. Check compass (COMPASS messages)

### Poor Altitude Hold

1. Graph `TECS.h` vs `GPS.Alt`
2. Check `TECS.dh` (altitude error)
3. Look at `TECS.spd` vs `TECS.spddem`

### Vibration Problems

1. Graph `VIBE.VibeX/Y/Z`
2. Check `IMU.AccX/Y/Z` for clipping
3. Look at `BATT.Volt` for power fluctuations

### GPS Glitches

1. Graph `GPS.NSats` (should be stable)
2. Check `GPS.HDop` (should be < 2.0)
3. Look for sudden jumps in `GPS.Lat/Lng`

### Mode Changes / Failsafes

```bash
graph MODE.Mode
```

Check RC, BATT, and GPS messages at the same timestamps.

---

## Advanced Analysis

### Spectral Analysis (FFT)

```bash
mavfft_isb.py logfile.BIN
```

Identifies motor/prop imbalance frequencies.

### Python Log Analysis Script

```python
# analyze_log.py
from pymavlink import mavutil

def analyze_log(filename):
    print(f"Analyzing: {filename}")
    mlog = mavutil.mavlink_connection(filename)

    max_altitude = 0
    max_speed = 0
    total_current = 0
    count = 0

    while True:
        msg = mlog.recv_match(blocking=False)
        if msg is None:
            break

        msg_type = msg.get_type()

        if msg_type == "GPS":
            if msg.Spd > max_speed:
                max_speed = msg.Spd

        elif msg_type == "CTUN":
            if msg.Alt > max_altitude:
                max_altitude = msg.Alt

        elif msg_type == "BAT":
            total_current += msg.Curr
            count += 1

    avg_current = total_current / count if count > 0 else 0

    print(f"Max Altitude: {max_altitude:.1f}m")
    print(f"Max Speed: {max_speed:.1f}m/s")
    print(f"Avg Current: {avg_current:.1f}A")

analyze_log("test_flight.BIN")
```

---

## Critical Parameters Quick Reference

| Parameter        | Message          | Good Range | Action if Outside       |
| ---------------- | ---------------- | ---------- | ----------------------- |
| Vibration X/Y/Z  | VIBE.VibeX/Y/Z   | < 30       | Check damping, props    |
| EKF Velocity     | EKF.VN/VE        | < 0.25     | Check GPS, compass      |
| EKF Position     | EKF.PN/PE        | < 0.25     | Wait for GPS lock       |
| GPS Satellites   | GPS.NSats        | > 10       | Move to open area       |
| GPS HDop         | GPS.HDop         | < 1.5      | Improve antenna         |
| Battery Voltage  | BATT.Volt        | > 10.5V    | Land soon               |
| Clipping         | IMU.Acc*         | < ±16g     | Reduce vibration        |

---

- [TECS Analysis Tutorial](TECS_ANALYSIS_TUTORIAL.md)
- [Vibration Analysis Tutorial](VIBRATION_ANALYSIS_TUTORIAL.md)
- [ArduPilot Log Analysis](https://ardupilot.org/copter/docs/common-logs.html)
- [MAVExplorer Documentation](https://ardupilot.org/dev/docs/using-mavexplorer-for-log-analysis.html)

**Author:** Patrick Kelly (@Kuscko)
