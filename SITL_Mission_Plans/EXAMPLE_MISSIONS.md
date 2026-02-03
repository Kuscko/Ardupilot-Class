# Example SITL Mission Plans

This document contains example mission plans you can test in SITL to learn mission planning, waypoint navigation, and AUTO mode behavior.

---

## Mission File Format

ArduPilot missions use the MAVLink Waypoint Protocol. Each line represents a waypoint with this format:

```
<INDEX> <CURRENT> <COORD_FRAME> <COMMAND> <PARAM1> <PARAM2> <PARAM3> <PARAM4> <LAT> <LON> <ALT> <AUTOCONTINUE>
```

**Key fields:**
- **INDEX**: Waypoint number (0, 1, 2, ...)
- **CURRENT**: 1 for home position, 0 for others
- **COORD_FRAME**: Usually 3 (absolute altitude) or 0 (home relative)
- **COMMAND**: MAV_CMD type (e.g., 16=WAYPOINT, 22=TAKEOFF, 21=LAND)
- **LAT/LON**: Coordinates in decimal degrees × 10^7
- **ALT**: Altitude in meters
- **AUTOCONTINUE**: 1 to automatically continue to next waypoint

---

## Mission 1: Simple Square Pattern

**Description:** Takeoff, fly in a square pattern, return to launch

**File:** `mission_square.txt`

```
QGC WPL 110
0	1	0	16	0	0	0	0	35.328400	-119.003100	584.000000	1
1	0	3	22	15.00000000	0.00000000	0.00000000	0.00000000	35.328400	-119.003100	100.000000	1
2	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.329400	-119.003100	100.000000	1
3	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.329400	-119.002100	100.000000	1
4	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.328400	-119.002100	100.000000	1
5	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.328400	-119.003100	100.000000	1
6	0	3	20	0.00000000	0.00000000	0.00000000	0.00000000	35.328400	-119.003100	0.000000	1
```

**Waypoint breakdown:**
- WP 0: Home position (required)
- WP 1: Takeoff to 100m
- WP 2-5: Square pattern corners
- WP 6: RTL (Return to Launch)

**To test:**
```bash
# Start SITL
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane -L CMAC --console --map

# Load mission
wp load mission_square.txt

# Verify waypoints
wp list

# Start mission
mode AUTO
arm throttle
```

---

## Mission 2: Altitude Test

**Description:** Takeoff, climb to different altitudes, observe TECS behavior

**File:** `mission_altitude_test.txt`

```
QGC WPL 110
0	1	0	16	0	0	0	0	35.328400	-119.003100	584.000000	1
1	0	3	22	15.00000000	0.00000000	0.00000000	0.00000000	35.328400	-119.003100	100.000000	1
2	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.330000	-119.003100	150.000000	1
3	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.330000	-119.001500	200.000000	1
4	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.328400	-119.001500	150.000000	1
5	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.328400	-119.003100	100.000000	1
6	0	3	20	0.00000000	0.00000000	0.00000000	0.00000000	35.328400	-119.003100	0.000000	1
```

**Purpose:** Test TECS climb/descent performance at different altitudes

**Parameters to observe:**
- TECS_CLMB_MAX (max climb rate)
- TECS_SINK_MAX (max descent rate)
- TECS_SPDWEIGHT (speed vs altitude priority)

---

## Mission 3: Loiter and Survey

**Description:** Takeoff, fly to location, loiter (circle), continue survey pattern

**File:** `mission_loiter_survey.txt`

```
QGC WPL 110
0	1	0	16	0	0	0	0	35.328400	-119.003100	584.000000	1
1	0	3	22	15.00000000	0.00000000	0.00000000	0.00000000	35.328400	-119.003100	100.000000	1
2	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.330000	-119.003100	120.000000	1
3	0	3	17	3.00000000	0.00000000	0.00000000	0.00000000	35.330000	-119.003100	120.000000	1
4	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.330500	-119.002500	120.000000	1
5	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.330500	-119.003500	120.000000	1
6	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.329500	-119.003500	120.000000	1
7	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.329500	-119.002500	120.000000	1
8	0	3	20	0.00000000	0.00000000	0.00000000	0.00000000	35.328400	-119.003100	0.000000	1
```

**Waypoint breakdown:**
- WP 0: Home
- WP 1: Takeoff
- WP 2: Navigate to loiter point
- WP 3: Loiter for 3 turns (command 17)
- WP 4-7: Survey grid pattern
- WP 8: RTL

**MAVLink Commands:**
- 16 = NAV_WAYPOINT
- 17 = NAV_LOITER_TURNS (PARAM1 = number of turns)
- 22 = NAV_TAKEOFF
- 20 = NAV_RETURN_TO_LAUNCH

---

## Mission 4: Speed Test

**Description:** Test different airspeeds

**File:** `mission_speed_test.txt`

```
QGC WPL 110
0	1	0	16	0	0	0	0	35.328400	-119.003100	584.000000	1
1	0	3	22	15.00000000	0.00000000	0.00000000	0.00000000	35.328400	-119.003100	100.000000	1
2	0	3	178	15.00000000	-1.00000000	0.00000000	0.00000000	0.000000	0.000000	0.000000	1
3	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.330000	-119.003100	100.000000	1
4	0	3	178	20.00000000	-1.00000000	0.00000000	0.00000000	0.000000	0.000000	0.000000	1
5	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.330000	-119.001500	100.000000	1
6	0	3	178	25.00000000	-1.00000000	0.00000000	0.00000000	0.000000	0.000000	0.000000	1
7	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.328400	-119.001500	100.000000	1
8	0	3	20	0.00000000	0.00000000	0.00000000	0.00000000	35.328400	-119.003100	0.000000	1
```

**MAVLink Command 178:** DO_CHANGE_SPEED
- PARAM1: Speed type (0=airspeed, 1=groundspeed)
- PARAM2: Speed in m/s (-1 = use default)

**Waypoint breakdown:**
- WP 2: Set airspeed to 15 m/s
- WP 4: Set airspeed to 20 m/s
- WP 6: Set airspeed to 25 m/s

---

## Mission 5: Camera Trigger Simulation

**Description:** Survey pattern with simulated camera triggers

**File:** `mission_camera_trigger.txt`

```
QGC WPL 110
0	1	0	16	0	0	0	0	35.328400	-119.003100	584.000000	1
1	0	3	22	15.00000000	0.00000000	0.00000000	0.00000000	35.328400	-119.003100	100.000000	1
2	0	3	206	10.00000000	0.00000000	1.00000000	0.00000000	0.000000	0.000000	0.000000	1
3	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.330000	-119.003100	120.000000	1
4	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.330000	-119.002500	120.000000	1
5	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.329500	-119.002500	120.000000	1
6	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.329500	-119.003100	120.000000	1
7	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.329000	-119.003100	120.000000	1
8	0	3	16	0.00000000	0.00000000	0.00000000	0.00000000	35.329000	-119.002500	120.000000	1
9	0	3	207	0.00000000	0.00000000	0.00000000	0.00000000	0.000000	0.000000	0.000000	1
10	0	3	20	0.00000000	0.00000000	0.00000000	0.00000000	35.328400	-119.003100	0.000000	1
```

**MAVLink Commands:**
- 206 = DO_SET_CAM_TRIGG_DIST (PARAM1 = distance in meters between triggers)
- 207 = DO_SET_CAM_TRIGG_DIST with 0 distance = stop triggering

**Waypoint breakdown:**
- WP 2: Start camera triggering every 10m
- WP 3-8: Survey grid (camera triggers automatically)
- WP 9: Stop camera triggering

---

## Creating Missions in MAVProxy

### Method 1: Right-click on Map

1. Start SITL with map: `--map`
2. Right-click on map → Add waypoint
3. Double-click waypoint to edit altitude
4. Save: `wp save my_mission.txt`

### Method 2: Manual Entry

```bash
wp clear
wp add <lat> <lon> <alt> <command>

# Example:
wp add 35.330000 -119.003100 100 16  # Regular waypoint
wp add 35.330000 -119.002000 100 16
wp list
wp save my_mission.txt
```

---

## Mission Planning Best Practices

### 1. Altitude Selection
- Minimum safe altitude: 50m+ AGL (Above Ground Level)
- SITL default terrain: ~584m MSL (Mean Sea Level)
- Use absolute altitudes (frame type 3) for consistency

### 2. Waypoint Spacing
- Minimum: ~50m between waypoints
- Longer legs = smoother flight
- Tight patterns may cause overshoots

### 3. Speed Considerations
- Default cruise speed: TRIM_ARSPD_CM parameter
- Min airspeed: ARSPD_FBW_MIN
- Max airspeed: ARSPD_FBW_MAX
- Fixed-wing cannot hover or fly very slowly

### 4. Turn Radius
- Determined by NAVL1_PERIOD parameter
- Tighter turns = potential altitude loss
- Allow space for turning at waypoints

### 5. Mission Testing Checklist
- [ ] Home position set correctly (WP 0)
- [ ] Takeoff waypoint included (command 22)
- [ ] All altitudes safe and consistent
- [ ] RTL or LAND at end
- [ ] Geofence configured if needed
- [ ] Parameters tuned appropriately

---

## Mission Execution Tips

### Starting a Mission

```bash
# Load mission
wp load my_mission.txt

# Verify loaded correctly
wp list

# Arm and start AUTO mode
arm throttle
mode AUTO

# Monitor progress in console
```

### Pausing/Resuming

```bash
# Pause mission (switch to loiter)
mode LOITER

# Resume mission
mode AUTO
```

### Skipping Waypoints

```bash
# Jump to waypoint 5
wp set 5
```

### Aborting Mission

```bash
# Return to launch immediately
mode RTL

# Or land immediately
mode LAND
```

---

## Advanced Mission Commands

### Conditional Commands

- **Delay:** `NAV_DELAY` (command 93)
- **Condition Distance:** Execute next command after traveling X meters
- **Condition Yaw:** Point aircraft in specific direction

### DO Commands (Immediate Actions)

- **DO_SET_SERVO:** Control servo position
- **DO_SET_RELAY:** Toggle relay
- **DO_DIGICAM_CONTROL:** Trigger camera
- **DO_CHANGE_SPEED:** Modify airspeed/groundspeed
- **DO_SET_ROI:** Point camera at Region of Interest

### Example: Servo Control

```
<INDEX>	0	3	183	<SERVO_NUM>	<PWM_VALUE>	0	0	0	0	0	1
```

---

## Troubleshooting Missions

### Aircraft doesn't follow mission

**Check:**
- Is mode set to AUTO? `mode AUTO`
- Is aircraft armed? `arm throttle`
- Are waypoints loaded? `wp list`

### Aircraft skips waypoints

**Causes:**
- Waypoint acceptance radius too large (WP_RADIUS)
- Waypoints too close together
- Altitude changes too aggressive

### Mission doesn't upload

**Fix:**
```bash
# Clear existing mission
wp clear

# Reload
wp load mission.txt
```

### Aircraft flies in wrong direction

**Causes:**
- Home position incorrect
- Waypoint coordinates wrong (check lat/lon)
- Coordinate frame incorrect

---

## Next Steps

1. [ ] Test each example mission in SITL
2. [ ] Modify missions to experiment
3. [ ] Create your own custom mission
4. [ ] Learn [Parameter Tuning](PARAMETER_GUIDE.md)
5. [ ] Combine missions with Lua scripts

---

## Additional Resources

- [MAVLink Mission Protocol](https://mavlink.io/en/services/mission.html)
- [MAVLink Command List](https://mavlink.io/en/messages/common.html#mav_commands)
- [ArduPilot Mission Commands](https://ardupilot.org/plane/docs/common-mavlink-mission-command-messages-mav_cmd.html)

---

**Last Updated:** 2026-02-03
