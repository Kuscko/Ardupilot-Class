# Example SITL Mission Plans

This document walks through every mission and parameter file included in this folder. Each section explains what the file does, what every waypoint means, and how to run it in SITL. If you're new to ArduPilot or mission planning, start with [Mission 1: Simple Flight](#mission-1-simple-flight) and work your way down.

---

## Before You Start

Make sure SITL is running before you try to load any missions:

```bash
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
```

Wait until the console shows `GPS: 3D Fix` before arming.

All missions in this folder use the **CMAC** (Canberra Model Aircraft Club) default SITL location:
- **Latitude:** -35.363264
- **Longitude:** 149.165239
- **Elevation:** ~584m MSL (Mean Sea Level)

If you start SITL at a different location, these missions will still work, but the waypoints will be relative to CMAC. For best results, use the default location or `-L CMAC`.

---

## Mission File Format

ArduPilot missions use the QGroundControl Waypoint Protocol (QGC WPL 110). Each line after the header represents one waypoint:

```
<INDEX>  <CURRENT>  <COORD_FRAME>  <COMMAND>  <PARAM1>  <PARAM2>  <PARAM3>  <PARAM4>  <LAT>  <LON>  <ALT>  <AUTOCONTINUE>
```

**Field-by-field breakdown:**

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

**Common MAVLink commands used in these missions:**

| Command ID | Name | What it does | Key parameters |
|------------|------|-------------|----------------|
| 16 | NAV_WAYPOINT | Fly to a GPS coordinate | -- |
| 17 | NAV_LOITER_TURNS | Circle a point N times | param1 = number of turns, param2 = radius (m), param4 = exit direction (1=CW) |
| 19 | NAV_LOITER_TIME | Circle a point for N seconds | param1 = time in seconds |
| 21 | NAV_LAND | Land at a GPS coordinate | -- |
| 22 | NAV_TAKEOFF | Climb to altitude | param1 = pitch angle in degrees |
| 178 | DO_CHANGE_SPEED | Change airspeed mid-flight | param1 = speed type (0=airspeed), param2 = speed (m/s), param3 = throttle (-1=no change) |

> **Tip:** Command 20 (NAV_RETURN_TO_LAUNCH) also exists but is not used in these files. These missions use command 21 (NAV_LAND) to land at a specific coordinate instead.

---

## Mission 1: Simple Flight

**File:** `simple_flight.waypoints`
**Difficulty:** Beginner
**Duration:** ~5 minutes
**Purpose:** Verify your SITL setup works. This is the "hello world" of ArduPilot missions.

### What it does

Takeoff, fly to two waypoints, then return and land at the home position. That's it -- nice and simple.

### Waypoint data

```
QGC WPL 110
0	1	0	16	0.00	0.00	0.00	0.00	-35.36326400	149.16523900	584.090000	1
1	0	3	22	15.00	0.00	0.00	0.00	-35.36326400	149.16523900	100.000000	1
2	0	3	16	0.00	0.00	0.00	0.00	-35.37000000	149.17000000	100.000000	1
3	0	3	16	0.00	0.00	0.00	0.00	-35.36500000	149.17500000	100.000000	1
4	0	3	21	0.00	0.00	0.00	0.00	-35.36326400	149.16523900	0.000000	1
```

### Waypoint-by-waypoint explanation

| WP | Command | Altitude | What happens |
|----|---------|----------|-------------|
| 0 | NAV_WAYPOINT (16) | 584m MSL | **Home position.** This is where the aircraft starts and where it will return. Always required as WP 0 with `current=1`. The altitude is the ground elevation at CMAC. |
| 1 | NAV_TAKEOFF (22) | 100m AGL | **Takeoff.** Aircraft climbs to 100m above home. The `param1=15` means pitch up at 15 degrees during the climb. |
| 2 | NAV_WAYPOINT (16) | 100m AGL | **First waypoint.** Fly southeast (~750m from home) while holding 100m altitude. |
| 3 | NAV_WAYPOINT (16) | 100m AGL | **Second waypoint.** Fly further east (~500m from WP 2). |
| 4 | NAV_LAND (21) | 0m | **Land.** Return to home coordinates and land. Altitude 0 means touch down on the ground. |

### How to fly it

```bash
# Load the mission
wp load simple_flight.waypoints

# Verify it loaded (should show 5 waypoints: 0-4)
wp list

# Start the mission
mode AUTO
arm throttle

# Watch it fly on the map window!
```

### Things to try

- **Skip a waypoint:** `wp set 3` (jumps to WP 3)
- **Pause the mission:** `mode LOITER` (circles in place)
- **Resume the mission:** `mode AUTO`
- **Abort and come home:** `mode RTL`

---

## Mission 2: Square Pattern

**File:** `square_pattern.waypoints`
**Difficulty:** Beginner
**Duration:** ~8 minutes
**Purpose:** Test navigation accuracy. The square shape makes it easy to see if the aircraft overshoots turns or drifts in wind.

### What it does

Takeoff to 80m, fly a ~500m x 500m square, return to the start, and land.

### Waypoint data

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

### Waypoint-by-waypoint explanation

| WP | Command | Altitude | What happens |
|----|---------|----------|-------------|
| 0 | NAV_WAYPOINT (16) | 584m MSL | **Home position.** |
| 1 | NAV_TAKEOFF (22) | 80m AGL | **Takeoff** to 80m. |
| 2 | NAV_WAYPOINT (16) | 80m AGL | **South edge.** Fly ~500m south from home. |
| 3 | NAV_WAYPOINT (16) | 80m AGL | **Southeast corner.** Fly ~500m east (first 90-degree turn). |
| 4 | NAV_WAYPOINT (16) | 80m AGL | **Northeast corner.** Fly ~500m north (second 90-degree turn). |
| 5 | NAV_WAYPOINT (16) | 80m AGL | **Back to start.** Fly ~500m west to close the square. |
| 6 | NAV_LAND (21) | 0m | **Land** at home. |

### How to fly it

```bash
wp load square_pattern.waypoints
wp list
mode AUTO
arm throttle
```

### What to watch for

- **Turn sharpness:** Does the aircraft cut corners or overshoot? Tune with `NAVL1_PERIOD` (lower = tighter turns).
- **Altitude hold:** Does it stay at 80m through the turns? If it drops in turns, check `TECS_SPDWEIGHT`.
- **Wind drift:** Enable wind with `param set SIM_WIND_SPD 10` and see how it compensates.

### Relevant parameters

| Parameter | What it controls | Try this |
|-----------|-----------------|----------|
| NAVL1_PERIOD | Turn sharpness (seconds) | 15 for tight, 20 for gentle |
| WP_RADIUS | How close to WP before it counts as "reached" (meters) | 50-100 |
| LIM_ROLL_CD | Max bank angle in turns (centidegrees) | 4500 = 45 degrees |

---

## Mission 3: Altitude Test

**File:** `altitude_test.waypoints`
**Difficulty:** Intermediate
**Duration:** ~10 minutes
**Purpose:** Test how well TECS (Total Energy Control System) handles climbing and descending. This is the go-to mission for tuning climb/sink rates.

### What it does

Takeoff to 50m, then progressively climb through 100m, 150m, and 200m. Cross over at 200m, then descend back through 150m, 100m, 50m, and land. This "staircase" profile stresses the TECS controller at every altitude transition.

### Waypoint data

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

### Waypoint-by-waypoint explanation

| WP | Command | Altitude | What happens |
|----|---------|----------|-------------|
| 0 | NAV_WAYPOINT (16) | 584m MSL | **Home position.** |
| 1 | NAV_TAKEOFF (22) | 50m AGL | **Takeoff** to 50m (low initial altitude). |
| 2 | NAV_WAYPOINT (16) | 100m AGL | **Climb to 100m** while flying south. |
| 3 | NAV_WAYPOINT (16) | 150m AGL | **Climb to 150m.** Continue south. |
| 4 | NAV_WAYPOINT (16) | 200m AGL | **Climb to 200m.** Peak altitude -- watch climb rate here. |
| 5 | NAV_WAYPOINT (16) | 200m AGL | **Level at 200m.** Turn east, holding altitude. |
| 6 | NAV_WAYPOINT (16) | 150m AGL | **Descend to 150m.** Heading north. |
| 7 | NAV_WAYPOINT (16) | 100m AGL | **Descend to 100m.** |
| 8 | NAV_WAYPOINT (16) | 50m AGL | **Descend to 50m.** Final descent step. |
| 9 | NAV_LAND (21) | 0m | **Land** at home. |

### How to fly it

```bash
wp load altitude_test.waypoints
wp list
mode AUTO
arm throttle
```

### What to watch for

- **Climb rate:** Does the aircraft reach each altitude before arriving at the waypoint? If not, increase `TECS_CLMB_MAX`.
- **Overshoot:** Does it blow past the target altitude? Increase `TECS_TIME_CONST` for smoother transitions.
- **Descent behavior:** Does it maintain speed during descent, or does it pitch down too aggressively? Adjust `TECS_SINK_MAX`.

### Key TECS parameters for this mission

| Parameter | What it controls | Conservative | Aggressive |
|-----------|-----------------|-------------|------------|
| TECS_CLMB_MAX | Max climb rate (m/s) | 3.0 | 8.0 |
| TECS_SINK_MAX | Max descent rate (m/s) | 2.0 | 6.0 |
| TECS_TIME_CONST | Response speed (seconds) | 7.0 | 3.0 |
| TECS_SPDWEIGHT | Speed vs altitude priority | 1.0 (balanced) | 2.0 (speed priority) |

### Recommended tuning workflow

```bash
# 1. Load the TECS tuning baseline parameters
param load params_tecs_tuning.param

# 2. Load this mission
wp load altitude_test.waypoints

# 3. Fly and observe
mode AUTO
arm throttle

# 4. Adjust ONE parameter, e.g.:
param set TECS_CLMB_MAX 3.0

# 5. Fly again and compare. Repeat.
```

---

## Mission 4: Loiter Test

**File:** `loiter_test.waypoints`
**Difficulty:** Intermediate
**Duration:** ~8 minutes
**Purpose:** Test two different loiter behaviors -- circling a point for a set number of turns, and circling for a set amount of time.

### What it does

Takeoff to 100m, fly to a waypoint, circle it 3 times with a 50m radius, then fly to a second waypoint at 120m and loiter there for 30 seconds, then return and land.

### Waypoint data

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

### Waypoint-by-waypoint explanation

| WP | Command | Altitude | What happens |
|----|---------|----------|-------------|
| 0 | NAV_WAYPOINT (16) | 584m MSL | **Home position.** |
| 1 | NAV_TAKEOFF (22) | 100m AGL | **Takeoff** to 100m. |
| 2 | NAV_WAYPOINT (16) | 100m AGL | **Fly to loiter point** (~750m southeast of home). |
| 3 | NAV_LOITER_TURNS (17) | 100m AGL | **Circle 3 times.** `param1=3` turns, `param2=50` meter radius, `param4=1` means clockwise exit. The aircraft will orbit this point 3 full circles before continuing. |
| 4 | NAV_WAYPOINT (16) | 120m AGL | **Fly to second point** and climb to 120m (~500m northwest). |
| 5 | NAV_LOITER_TIME (19) | 120m AGL | **Circle for 30 seconds.** `param1=30` seconds. The aircraft will orbit until the timer expires. |
| 6 | NAV_LAND (21) | 0m | **Land** at home. |

### How to fly it

```bash
wp load loiter_test.waypoints
wp list
mode AUTO
arm throttle
```

### What to watch for

- **Circle shape:** Is the orbit round or egg-shaped? Tune `WP_LOITER_RAD` and `NAVL1_PERIOD`.
- **Bank angle in turns:** Steep bank = tight circle but potential altitude loss. Controlled by `LIM_ROLL_CD`.
- **Wind compensation:** Enable wind (`param set SIM_WIND_SPD 10`) and see if the orbit stays centered or drifts.
- **Timing accuracy:** Does the 30-second loiter at WP 5 feel about right?

### Relevant parameters

| Parameter | What it controls | Try this |
|-----------|-----------------|----------|
| WP_LOITER_RAD | Default loiter radius (meters) | 50-100 |
| LIM_ROLL_CD | Max bank angle (centidegrees) | 3000 = 30 deg, 6000 = 60 deg |
| NAVL1_PERIOD | L1 controller responsiveness (seconds) | 12-18 |

---

## Mission 5: Speed Test

**File:** `speed_test.waypoints`
**Difficulty:** Intermediate
**Duration:** ~7 minutes
**Purpose:** Test how the aircraft handles mid-flight airspeed changes. Uses the `DO_CHANGE_SPEED` command (178) to set different target airspeeds between waypoints.

### What it does

Takeoff to 100m, then fly a rectangular course while changing speed at each leg: 12 m/s (slow), 18 m/s (fast), then 15 m/s (cruise). This lets you see how TECS couples speed and altitude.

### Waypoint data

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

### Waypoint-by-waypoint explanation

| WP | Command | What happens |
|----|---------|-------------|
| 0 | NAV_WAYPOINT (16) | **Home position.** |
| 1 | NAV_TAKEOFF (22) | **Takeoff** to 100m AGL. |
| 2 | DO_CHANGE_SPEED (178) | **Set airspeed to 12 m/s** (slow cruise). This is a "DO" command -- it executes immediately and doesn't have a location. `param1=0` means airspeed (not groundspeed), `param2=12` is the target speed, `param3=-1` means don't change throttle limits. |
| 3 | NAV_WAYPOINT (16) | **Fly south** at 12 m/s, holding 100m. |
| 4 | DO_CHANGE_SPEED (178) | **Set airspeed to 18 m/s** (fast). |
| 5 | NAV_WAYPOINT (16) | **Fly east** at 18 m/s, holding 100m. |
| 6 | DO_CHANGE_SPEED (178) | **Set airspeed to 15 m/s** (normal cruise). |
| 7 | NAV_WAYPOINT (16) | **Fly north** at 15 m/s back toward home. |
| 8 | NAV_LAND (21) | **Land** at home. |

### Understanding DO_CHANGE_SPEED (Command 178)

This is a "DO" command, meaning it takes effect immediately and doesn't navigate anywhere. The parameters are:

| Parameter | Field | What it means |
|-----------|-------|--------------|
| param1 | Speed type | 0 = airspeed, 1 = groundspeed |
| param2 | Target speed | In m/s (e.g., 12, 15, 18) |
| param3 | Throttle | -1 = don't change throttle limits |

> **Important:** `DO` commands don't have lat/lon/alt -- those fields are all zero. The command fires instantly and the aircraft continues to the next NAV waypoint.

### How to fly it

```bash
wp load speed_test.waypoints
wp list
mode AUTO
arm throttle
```

### What to watch for

- **Altitude dips during speed-up:** When the aircraft accelerates to 18 m/s, does it lose altitude? That's normal -- TECS is trading altitude energy for speed. Tune with `TECS_SPDWEIGHT`.
- **Altitude gain during slow-down:** The reverse -- going from 18 to 15 m/s may cause a slight climb.
- **Throttle response:** Watch the throttle output in the console. Is it smooth or hunting?

### Relevant parameters

| Parameter | What it controls | Try this |
|-----------|-----------------|----------|
| ARSPD_FBW_MIN | Minimum allowed airspeed (m/s) | 10-12 |
| ARSPD_FBW_MAX | Maximum allowed airspeed (m/s) | 22-28 |
| TRIM_ARSPD_CM | Default cruise airspeed (centimeters/sec) | 1500 = 15 m/s |
| TECS_SPDWEIGHT | Speed vs altitude priority | <1.0 = altitude priority, >1.0 = speed priority |

---

## Mission Template

**File:** `mission_template.waypoints`
**Difficulty:** Reference
**Purpose:** A minimal example showing the required structure of a mission file. Copy this as a starting point for your own missions.

### Waypoint data

```
QGC WPL 110
0	1	0	16	0.00	0.00	0.00	0.00	-35.36326400	149.16523900	584.090000	1
1	0	3	22	15.00	0.00	0.00	0.00	-35.36326400	149.16523900	100.000000	1
2	0	3	16	0.00	0.00	0.00	0.00	-35.37000000	149.17000000	100.000000	1
3	0	3	16	0.00	0.00	0.00	0.00	-35.38000000	149.17000000	100.000000	1
4	0	3	21	0.00	0.00	0.00	0.00	-35.36326400	149.16523900	0.000000	1
```

### Structure

Every mission file needs at minimum:

1. **Header line:** `QGC WPL 110` (always the first line)
2. **Home waypoint (WP 0):** `current=1`, your launch position and ground elevation
3. **Takeoff (WP 1):** Command 22, with a target altitude
4. **One or more waypoints:** Command 16, the actual mission
5. **Land or RTL:** Command 21 (land at coordinates) or 20 (return to launch)

### How to create your own mission

```bash
# 1. Copy the template
cp mission_template.waypoints my_custom_mission.waypoints

# 2. Edit the file -- change lat/lon/alt for waypoints 2+
#    (Keep WP 0 and WP 1 as-is for CMAC location)

# 3. Load and test
wp load my_custom_mission.waypoints
wp list
mode AUTO
arm throttle
```

---

## Parameter Files

These files let you quickly swap between different flight "personalities" without changing parameters one at a time.

### params_conservative.param

**Purpose:** Safe, gentle flight parameters for first flights or unfamiliar setups.

| Category | Key settings | Why |
|----------|-------------|-----|
| TECS | Climb 3 m/s, sink 2 m/s, time constant 6s | Slow, smooth altitude changes |
| Airspeed | 12-20 m/s range, cruise at 15 m/s | Narrow speed range prevents surprises |
| Throttle | Max 70% | Limits power to prevent aggressive maneuvers |
| Navigation | 30-degree bank limit, 18s L1 period, 80m loiter radius | Wide, gentle turns |
| Failsafes | All enabled (short=RTL, long=land) | Maximum safety net |
| Fence | 500m radius, 200m altitude ceiling | Prevents flyaways |

```bash
# Load conservative parameters
param load params_conservative.param
```

**Use when:** First flights, testing new code, learning, windy conditions.

### params_performance.param

**Purpose:** Aggressive parameters for experienced users and performance testing.

| Category | Key settings | Why |
|----------|-------------|-----|
| TECS | Climb 8 m/s, sink 6 m/s, time constant 3s | Fast, responsive altitude changes |
| Airspeed | 10-28 m/s range, cruise at 20 m/s | Wide speed envelope |
| Throttle | Max 100% | Full power available |
| Navigation | 60-degree bank limit, 12s L1 period, 50m loiter radius | Tight, aggressive turns |
| Failsafes | All enabled | Still safe even when aggressive |
| Fence | 1000m radius, 400m altitude ceiling | Larger operating area |

```bash
# Load performance parameters (test conservative first!)
param load params_performance.param
```

**Use when:** Performance testing, racing scenarios, advanced tuning, after successful conservative testing.

> **Warning:** Only use after you've flown successfully with conservative parameters. These settings allow much more aggressive flight that can lead to crashes if something is misconfigured.

### params_tecs_tuning.param

**Purpose:** A neutral TECS baseline for systematic tuning. Change one parameter at a time and fly the altitude_test mission to see the effect.

| Parameter | Baseline value | Tuning range | Effect of increasing |
|-----------|---------------|-------------|---------------------|
| TECS_CLMB_MAX | 5.0 m/s | 2-10 | Faster climbs |
| TECS_SINK_MAX | 5.0 m/s | 2-10 | Faster descents |
| TECS_TIME_CONST | 5.0 sec | 3-10 | Slower, smoother response |
| TECS_SPDWEIGHT | 1.0 | 0.5-2.0 | Prioritizes speed over altitude |
| TECS_SINK_MIN | 2.0 m/s | 0-5 | Steeper minimum glide slope |
| TECS_THR_DAMP | 0.5 | 0-1 | More throttle damping (less hunting) |
| TECS_INTEG_GAIN | 0.1 | 0-0.5 | Stronger long-term error correction |

```bash
# TECS tuning workflow
param load params_tecs_tuning.param
wp load altitude_test.waypoints
mode AUTO
arm throttle

# Observe, then adjust ONE parameter:
param set TECS_TIME_CONST 3.0   # Try more aggressive
# Fly again and compare

param set TECS_TIME_CONST 8.0   # Try more conservative
# Fly again and compare
```

---

## Creating Missions in MAVProxy

### Method 1: Using the Map (Interactive)

1. Start SITL with `--map`
2. Right-click on the map to add waypoints
3. Double-click a waypoint to edit its altitude or command
4. Save your mission: `wp save my_mission.waypoints`

### Method 2: Text File (Manual)

1. Copy `mission_template.waypoints`
2. Edit coordinates and commands in a text editor
3. Load with `wp load my_mission.waypoints`

### Method 3: MAVProxy Commands

```bash
wp clear                                    # Clear existing mission
wp add -35.370000 149.170000 100 16         # Add a NAV_WAYPOINT
wp add -35.375000 149.170000 100 16         # Add another
wp list                                     # Verify
wp save my_mission.waypoints                # Save to file
```

---

## Mission Execution Quick Reference

### Starting a Mission

```bash
wp load <filename>    # Load mission
wp list               # Verify waypoints
mode AUTO             # Switch to autonomous mode
arm throttle          # Arm the aircraft (mission begins)
```

### Pausing / Resuming

```bash
mode LOITER           # Pause: circles at current location
mode AUTO             # Resume: continues from where it left off
```

### Skipping Waypoints

```bash
wp set 5              # Jump ahead to waypoint 5
```

### Aborting

```bash
mode RTL              # Return to launch and loiter/land
```

---

## Mission Planning Best Practices

1. **Always include a home waypoint (WP 0)** with `current=1` and the correct ground elevation.
2. **Always include a takeoff waypoint (WP 1)** with command 22.
3. **End with LAND (21) or RTL (20).** These missions use LAND for a controlled touchdown at known coordinates.
4. **Keep waypoints at least 50m apart.** Closer waypoints can cause the aircraft to skip them or oscillate.
5. **Use frame 3 (relative to home) for mission altitudes.** This makes missions portable -- the same mission works at any launch site.
6. **Test in SITL before real flights.** Always.
7. **Start with conservative parameters** and work toward aggressive as you gain confidence.
8. **Change one thing at a time** when tuning. If you change three parameters and something goes wrong, you won't know which one caused it.

---

## Troubleshooting

### Aircraft doesn't follow mission

- Is the mode set to AUTO? Run `mode AUTO`
- Is the aircraft armed? Run `arm throttle`
- Are waypoints loaded? Run `wp list` (should show your waypoints)

### Aircraft skips waypoints

- `WP_RADIUS` may be too large (aircraft "reaches" the waypoint too early)
- Waypoints may be too close together (< 50m)
- Altitude changes between waypoints may be too aggressive for the current TECS settings

### Aircraft overshoots turns

- Increase `NAVL1_PERIOD` for gentler, wider turns
- Decrease airspeed for tighter turns: `param set TRIM_ARSPD_CM 1200`
- Increase `WP_RADIUS` so it doesn't need to hit the exact point

### Mission doesn't load

```bash
wp clear              # Clear existing mission
wp load <filename>    # Try loading again
wp list               # Verify it loaded
```

Check that the file starts with `QGC WPL 110` and uses tab-separated values.

### Aircraft flies in wrong direction

- Check that WP 0 (home) coordinates match the SITL start location
- Verify lat/lon are correct (negative latitude = southern hemisphere)
- Make sure `coord_frame` is set correctly (3 = relative altitude)

---

## Additional Resources

- [MAVLink Command Reference](https://mavlink.io/en/messages/common.html#mav_commands) -- full list of all command IDs
- [MAVLink Mission Protocol](https://mavlink.io/en/services/mission.html) -- how missions work under the hood
- [ArduPilot Mission Commands](https://ardupilot.org/plane/docs/common-mavlink-mission-command-messages-mav_cmd.html) -- ArduPilot-specific mission docs
- [TECS Tuning Guide](https://ardupilot.org/plane/docs/tecs-total-energy-control-system-for-speed-height-tuning-guide.html) -- official TECS tuning reference
- [PARAMETER_GUIDE.md](PARAMETER_GUIDE.md) -- detailed parameter reference in this repo
- [SITL_QUICK_START.md](SITL_QUICK_START.md) -- getting SITL running from scratch
- [USING_EXAMPLES.md](USING_EXAMPLES.md) -- how to use the example files hands-on

---

**Author:** Patrick Kelly (@Kuscko)
**Last Updated:** 2026-02-10
