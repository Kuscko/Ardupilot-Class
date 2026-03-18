# Example SITL Mission Plans

Start SITL before loading any missions:

```bash
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
```

Wait for `GPS: 3D Fix`. All missions use the **CMAC** default SITL location (lat: -35.363264, lon: 149.165239, ~584m MSL). Use default location or `-L CMAC` for best results.

---

## Mission File Format

ArduPilot missions use the QGroundControl Waypoint Protocol (QGC WPL 110):

```
<INDEX>  <CURRENT>  <COORD_FRAME>  <COMMAND>  <PARAM1>  <PARAM2>  <PARAM3>  <PARAM4>  <LAT>  <LON>  <ALT>  <AUTOCONTINUE>
```

| Field | What it means | Common values |
|-------|---------------|---------------|
| INDEX | Waypoint number (starts at 0) | 0 = home, 1+ = mission steps |
| CURRENT | Is this the active waypoint? | 1 = home position, 0 = everything else |
| COORD_FRAME | How altitude is interpreted | 0 = absolute (MSL), 3 = relative to home |
| COMMAND | What to do at this waypoint | See command table below |
| PARAM1-4 | Command-specific values | Varies by command |
| LAT / LON | GPS coordinates (decimal degrees) | e.g., -35.363264 / 149.165239 |
| ALT | Altitude in meters | Relative to home when frame = 3 |
| AUTOCONTINUE | Move to next waypoint automatically? | 1 = yes (almost always) |

**Common MAVLink commands:**

| Command ID | Name | What it does | Key parameters |
|------------|------|-------------|----------------|
| 16 | NAV_WAYPOINT | Fly to a GPS coordinate | -- |
| 17 | NAV_LOITER_TURNS | Circle a point N times | param1 = turns, param2 = radius (m), param4 = exit direction (1=CW) |
| 19 | NAV_LOITER_TIME | Circle a point for N seconds | param1 = time in seconds |
| 21 | NAV_LAND | Land at a GPS coordinate | -- |
| 22 | NAV_TAKEOFF | Climb to altitude | param1 = pitch angle in degrees |
| 178 | DO_CHANGE_SPEED | Change airspeed mid-flight | param1 = speed type (0=airspeed), param2 = speed (m/s), param3 = throttle (-1=no change) |

---

## Mission 1: Simple Flight

**File:** `simple_flight.waypoints` | **Difficulty:** Beginner | **Duration:** ~5 min

Takeoff, fly to two waypoints, return and land.

```
QGC WPL 110
0	1	0	16	0.00	0.00	0.00	0.00	-35.36326400	149.16523900	584.090000	1
1	0	3	22	15.00	0.00	0.00	0.00	-35.36326400	149.16523900	100.000000	1
2	0	3	16	0.00	0.00	0.00	0.00	-35.37000000	149.17000000	100.000000	1
3	0	3	16	0.00	0.00	0.00	0.00	-35.36500000	149.17500000	100.000000	1
4	0	3	21	0.00	0.00	0.00	0.00	-35.36326400	149.16523900	0.000000	1
```

| WP | Command | Altitude | What happens |
|----|---------|----------|-------------|
| 0 | NAV_WAYPOINT (16) | 584m MSL | Home position |
| 1 | NAV_TAKEOFF (22) | 100m AGL | Climb at 15° pitch |
| 2 | NAV_WAYPOINT (16) | 100m AGL | First waypoint (~750m southeast) |
| 3 | NAV_WAYPOINT (16) | 100m AGL | Second waypoint (~500m east) |
| 4 | NAV_LAND (21) | 0m | Land at home |

```bash
wp load simple_flight.waypoints
wp list
mode AUTO
arm throttle
```

Tips: `wp set 3` skips to WP 3, `mode LOITER` pauses, `mode RTL` aborts.

---

## Mission 2: Square Pattern

**File:** `square_pattern.waypoints` | **Difficulty:** Beginner | **Duration:** ~8 min

Takeoff to 80m, fly a ~500m × 500m square, land.

```
QGC WPL 110
0	1	0	16	0.00	0.00	0.00	0.00	-35.36326400	149.16523900	584.090000	1
1	0	3	22	15.00	0.00	0.00	0.00	-35.36326400	149.16523900	80.000000	1
2	0	3	16	0.00	0.00	0.00	0.00	-35.36826400	149.16523900	80.000000	1
3	0	3	16	0.00	0.00	0.00	0.00	-35.36826400	149.17023900	80.000000	1
4	0	3	16	0.00	0.00	0.00	0.00	-35.36326400	149.17023900	80.000000	1
5	0	3	16	0.00	0.00	0.00	0.00	-35.36326400	149.16523900	80.000000	1
6	0	3	21	0.00	0.00	0.00	0.00	-35.36326400	149.16523900	0.000000	1
```

```bash
wp load square_pattern.waypoints
wp list
mode AUTO
arm throttle
```

**What to watch:** Turn sharpness (`NAVL1_PERIOD`), altitude hold through turns (`TECS_SPDWEIGHT`), wind drift (`param set SIM_WIND_SPD 10`).

| Parameter | What it controls | Try this |
|-----------|-----------------|----------|
| NAVL1_PERIOD | Turn sharpness (seconds) | 15 for tight, 20 for gentle |
| WP_RADIUS | Distance to count WP as "reached" (m) | 50-100 |
| LIM_ROLL_CD | Max bank angle (centidegrees) | 4500 = 45° |

---

## Mission 3: Altitude Test

**File:** `altitude_test.waypoints` | **Difficulty:** Intermediate | **Duration:** ~10 min

Staircase climb (50→100→150→200m) then descend — primary mission for TECS tuning.

```
QGC WPL 110
0	1	0	16	0.00	0.00	0.00	0.00	-35.36326400	149.16523900	584.090000	1
1	0	3	22	15.00	0.00	0.00	0.00	-35.36326400	149.16523900	50.000000	1
2	0	3	16	0.00	0.00	0.00	0.00	-35.36826400	149.16523900	100.000000	1
3	0	3	16	0.00	0.00	0.00	0.00	-35.37326400	149.16523900	150.000000	1
4	0	3	16	0.00	0.00	0.00	0.00	-35.37826400	149.16523900	200.000000	1
5	0	3	16	0.00	0.00	0.00	0.00	-35.37826400	149.17023900	200.000000	1
6	0	3	16	0.00	0.00	0.00	0.00	-35.37326400	149.17023900	150.000000	1
7	0	3	16	0.00	0.00	0.00	0.00	-35.36826400	149.17023900	100.000000	1
8	0	3	16	0.00	0.00	0.00	0.00	-35.36326400	149.17023900	50.000000	1
9	0	3	21	0.00	0.00	0.00	0.00	-35.36326400	149.16523900	0.000000	1
```

```bash
wp load altitude_test.waypoints
wp list
mode AUTO
arm throttle
```

| Parameter | What it controls | Conservative | Aggressive |
|-----------|-----------------|-------------|------------|
| TECS_CLMB_MAX | Max climb rate (m/s) | 3.0 | 8.0 |
| TECS_SINK_MAX | Max descent rate (m/s) | 2.0 | 6.0 |
| TECS_TIME_CONST | Response speed (seconds) | 7.0 | 3.0 |
| TECS_SPDWEIGHT | Speed vs altitude priority | 1.0 (balanced) | 2.0 (speed priority) |

**Tuning workflow:**

```bash
param load params_tecs_tuning.param
wp load altitude_test.waypoints
mode AUTO
arm throttle
# Adjust ONE parameter, e.g.:
param set TECS_CLMB_MAX 3.0
# Fly again and compare
```

---

## Mission 4: Loiter Test

**File:** `loiter_test.waypoints` | **Difficulty:** Intermediate | **Duration:** ~8 min

Takeoff to 100m, circle a point 3 times (50m radius), loiter at a second point for 30 seconds, land.

```
QGC WPL 110
0	1	0	16	0.00	0.00	0.00	0.00	-35.36326400	149.16523900	584.090000	1
1	0	3	22	15.00	0.00	0.00	0.00	-35.36326400	149.16523900	100.000000	1
2	0	3	16	0.00	0.00	0.00	0.00	-35.37000000	149.17000000	100.000000	1
3	0	3	17	3.00	50.00	0.00	1.00	-35.37000000	149.17000000	100.000000	1
4	0	3	16	0.00	0.00	0.00	0.00	-35.36500000	149.16500000	120.000000	1
5	0	3	19	30.00	0.00	0.00	0.00	-35.36500000	149.16500000	120.000000	1
6	0	3	21	0.00	0.00	0.00	0.00	-35.36326400	149.16523900	0.000000	1
```

| WP | Command | What happens |
|----|---------|-------------|
| 3 | NAV_LOITER_TURNS (17) | Circle 3 times, 50m radius, clockwise exit |
| 5 | NAV_LOITER_TIME (19) | Circle for 30 seconds |

```bash
wp load loiter_test.waypoints
wp list
mode AUTO
arm throttle
```

| Parameter | What it controls | Try this |
|-----------|-----------------|----------|
| WP_LOITER_RAD | Default loiter radius (m) | 50-100 |
| LIM_ROLL_CD | Max bank angle (centidegrees) | 3000 = 30°, 6000 = 60° |
| NAVL1_PERIOD | L1 controller responsiveness (s) | 12-18 |

---

## Mission 5: Speed Test

**File:** `speed_test.waypoints` | **Difficulty:** Intermediate | **Duration:** ~7 min

Takeoff to 100m, fly a rectangular course changing speed at each leg: 12 m/s → 18 m/s → 15 m/s.

```
QGC WPL 110
0	1	0	16	0.00	0.00	0.00	0.00	-35.36326400	149.16523900	584.090000	1
1	0	3	22	15.00	0.00	0.00	0.00	-35.36326400	149.16523900	100.000000	1
2	0	3	178	0.00	12.00	-1.00	0.00	0.00000000	0.00000000	0.000000	1
3	0	3	16	0.00	0.00	0.00	0.00	-35.37000000	149.16523900	100.000000	1
4	0	3	178	0.00	18.00	-1.00	0.00	0.00000000	0.00000000	0.000000	1
5	0	3	16	0.00	0.00	0.00	0.00	-35.37000000	149.17523900	100.000000	1
6	0	3	178	0.00	15.00	-1.00	0.00	0.00000000	0.00000000	0.000000	1
7	0	3	16	0.00	0.00	0.00	0.00	-35.36326400	149.17523900	100.000000	1
8	0	3	21	0.00	0.00	0.00	0.00	-35.36326400	149.16523900	0.000000	1
```

`DO_CHANGE_SPEED` (178) executes immediately with no lat/lon. `param1=0` = airspeed, `param2` = target speed (m/s), `param3=-1` = don't change throttle limits.

```bash
wp load speed_test.waypoints
wp list
mode AUTO
arm throttle
```

| Parameter | What it controls | Try this |
|-----------|-----------------|----------|
| ARSPD_FBW_MIN | Minimum allowed airspeed (m/s) | 10-12 |
| ARSPD_FBW_MAX | Maximum allowed airspeed (m/s) | 22-28 |
| TRIM_ARSPD_CM | Default cruise airspeed (cm/s) | 1500 = 15 m/s |
| TECS_SPDWEIGHT | Speed vs altitude priority | <1.0 = altitude, >1.0 = speed |

---

## Mission Template

**File:** `mission_template.waypoints`

```
QGC WPL 110
0	1	0	16	0.00	0.00	0.00	0.00	-35.36326400	149.16523900	584.090000	1
1	0	3	22	15.00	0.00	0.00	0.00	-35.36326400	149.16523900	100.000000	1
2	0	3	16	0.00	0.00	0.00	0.00	-35.37000000	149.17000000	100.000000	1
3	0	3	16	0.00	0.00	0.00	0.00	-35.38000000	149.17000000	100.000000	1
4	0	3	21	0.00	0.00	0.00	0.00	-35.36326400	149.16523900	0.000000	1
```

Every mission needs: header `QGC WPL 110`, home WP (index 0, current=1), takeoff (cmd 22), one or more waypoints (cmd 16), and land/RTL (cmd 21/20).

```bash
cp mission_template.waypoints my_custom_mission.waypoints
# Edit lat/lon/alt for waypoints 2+
wp load my_custom_mission.waypoints
wp list
mode AUTO
arm throttle
```

---

## Parameter Files

### params_conservative.param

| Category | Key settings |
|----------|-------------|
| TECS | Climb 3 m/s, sink 2 m/s, time constant 6s |
| Airspeed | 12-20 m/s, cruise 15 m/s |
| Throttle | Max 70% |
| Navigation | 30° bank, 18s L1 period, 80m loiter radius |
| Failsafes | All enabled (short=RTL, long=land) |
| Fence | 500m radius, 200m ceiling |

```bash
param load params_conservative.param
```

Use for: first flights, testing new code, windy conditions.

### params_performance.param

| Category | Key settings |
|----------|-------------|
| TECS | Climb 8 m/s, sink 6 m/s, time constant 3s |
| Airspeed | 10-28 m/s, cruise 20 m/s |
| Throttle | Max 100% |
| Navigation | 60° bank, 12s L1 period, 50m loiter radius |
| Fence | 1000m radius, 400m ceiling |

```bash
param load params_performance.param
```

> **Warning:** Only use after successful conservative testing.

### params_tecs_tuning.param

| Parameter | Baseline | Tuning range | Effect of increasing |
| --- | --- | --- | --- |
| TECS_CLMB_MAX | 5.0 m/s | 2-10 | Faster climbs |
| TECS_SINK_MAX | 5.0 m/s | 2-10 | Faster descents |
| TECS_TIME_CONST | 5.0 sec | 3-10 | Slower, smoother response |
| TECS_SPDWEIGHT | 1.0 | 0.5-2.0 | Prioritizes speed over altitude |
| TECS_SINK_MIN | 2.0 m/s | 0-5 | Steeper minimum glide slope |
| TECS_THR_DAMP | 0.5 | 0-1 | More throttle damping |
| TECS_INTEG_GAIN | 0.1 | 0-0.5 | Stronger long-term error correction |

```bash
param load params_tecs_tuning.param
wp load altitude_test.waypoints
mode AUTO
arm throttle
param set TECS_TIME_CONST 3.0   # Try more aggressive
param set TECS_TIME_CONST 8.0   # Try more conservative
```

---

## Creating Missions in MAVProxy

### Method 1: Map (Interactive)

1. Start SITL with `--map`
2. Right-click to add waypoints
3. Double-click to edit altitude/command
4. `wp save my_mission.waypoints`

### Method 2: Text File

1. Copy `mission_template.waypoints`
2. Edit coordinates in a text editor
3. `wp load my_mission.waypoints`

### Method 3: MAVProxy Commands

```bash
wp clear
wp add -35.370000 149.170000 100 16
wp add -35.375000 149.170000 100 16
wp list
wp save my_mission.waypoints
```

---

## Mission Execution Quick Reference

```bash
wp load <filename>    # Load mission
wp list               # Verify waypoints
mode AUTO             # Switch to autonomous mode
arm throttle          # Arm (mission begins)

mode LOITER           # Pause
mode AUTO             # Resume
wp set 5              # Jump to waypoint 5
mode RTL              # Abort
```

---

## Mission Planning Best Practices

1. Always include a home waypoint (WP 0) with `current=1` and correct ground elevation.
2. Always include a takeoff waypoint (WP 1) with command 22.
3. End with LAND (21) or RTL (20).
4. Keep waypoints at least 50m apart.
5. Use frame 3 (relative to home) for mission altitudes.
6. Test in SITL before real flights.
7. Start with conservative parameters.
8. Change one parameter at a time when tuning.

---

## Troubleshooting

| Problem | Cause / Fix |
| --- | --- |
| Aircraft doesn't follow mission | Check `mode AUTO`, `arm throttle`, `wp list` |
| Aircraft skips waypoints | `WP_RADIUS` too large, waypoints too close (<50m), or aggressive TECS settings |
| Aircraft overshoots turns | Increase `NAVL1_PERIOD`, lower airspeed, increase `WP_RADIUS` |
| Mission doesn't load | Run `wp clear` then reload; verify file starts with `QGC WPL 110` and uses tab-separated values |
| Aircraft flies wrong direction | Check WP 0 coordinates, verify lat/lon sign, verify `coord_frame=3` |

---

## Additional Resources

- [MAVLink Command Reference](https://mavlink.io/en/messages/common.html#mav_commands)
- [ArduPilot Mission Commands](https://ardupilot.org/plane/docs/common-mavlink-mission-command-messages-mav_cmd.html)
- [TECS Tuning Guide](https://ardupilot.org/plane/docs/tecs-total-energy-control-system-for-speed-height-tuning-guide.html)
- [PARAMETER_GUIDE.md](PARAMETER_GUIDE.md)
- [SITL_QUICK_START.md](SITL_QUICK_START.md)
- [USING_EXAMPLES.md](USING_EXAMPLES.md)

---

**Author:** Patrick Kelly (@Kuscko)
**Last Updated:** 2026-02-10
