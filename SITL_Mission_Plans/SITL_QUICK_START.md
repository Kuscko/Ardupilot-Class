# SITL Quick Start Guide

## What is SITL?

SITL (Software-In-The-Loop) is a simulator that runs the actual ArduPilot firmware on your computer. It's identical to the code running on real aircraft, making it perfect for:
- Testing missions before real flights
- Learning parameters safely
- Developing Lua scripts
- Training new pilots/engineers
- Testing failsafe scenarios

---

## Starting SITL

### Basic Startup

```bash
cd ~/ardupilot
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
```

**Three windows will open:**
1. **MAVProxy Command Prompt** - Type commands here (shows mode like `MANUAL>`)
2. **Console** - Real-time status and messages
3. **Map** - Satellite view with aircraft position

### Startup with Custom Location

```bash
# Start at CMAC
Tools/autotest/sim_vehicle.py -v ArduPlane -L CMAC --console --map

# Start at specific coordinates (lat, lon, alt, heading)
Tools/autotest/sim_vehicle.py -v ArduPlane -L 35.0,-120.0,100,0 --console --map
```

### Startup with Wind Simulation

```bash
# Wind from north at 10 m/s
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map -w 10,0,0
```

---

## Essential MAVProxy Commands

### Flight Control

| Command | Example | Description |
|---------|---------|-------------|
| `mode` | `mode FBWA` | Change flight mode |
| `arm` | `arm throttle` | Enable motors |
| `disarm` | `disarm` | Disable motors |
| `rc` | `rc 3 1700` | Set RC channel (3=throttle, 1=roll, 2=pitch, 4=yaw) |

### Information

| Command | Example | Description |
|---------|---------|-------------|
| `status` | `status` | Show aircraft status |
| `mode` | `mode` | Show current mode |
| `fence` | `fence list` | Show geofence status |

### Parameters

| Command | Example | Description |
|---------|---------|-------------|
| `param show` | `param show ARSPD*` | List parameters matching pattern |
| `param set` | `param set THR_MAX 80` | Set parameter value |
| `param fetch` | `param fetch` | Reload all parameters |
| `param save` | `param save /tmp/params.parm` | Save parameters to file |
| `param load` | `param load /tmp/params.parm` | Load parameters from file |

### Mission (Waypoint) Commands

| Command | Example | Description |
|---------|---------|-------------|
| `wp list` | `wp list` | Show all waypoints |
| `wp load` | `wp load mission.txt` | Load mission from file |
| `wp clear` | `wp clear` | Clear all waypoints |

### Scripting Commands

| Command | Example | Description |
|---------|---------|-------------|
| `script` | `script list` | List loaded scripts |

---

## Your First Flight in SITL

### Step 1: Start SITL
```bash
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane -L CMAC --console --map
```

### Step 2: Wait for GPS Lock
Watch the console until you see:
```
GPS: 3D Fix
```

### Step 3: Switch to FBWA Mode
```bash
mode FBWA
```
FBWA (Fly-By-Wire A) provides stabilization assistance.

### Step 4: Arm the Aircraft
```bash
arm throttle
```
You should see: `ARMED`

### Step 5: Set Throttle
```bash
rc 3 1700
```
This sets throttle to 70%. The aircraft will start moving.

### Step 6: Control the Aircraft
```bash
# Adjust throttle (1000-2000, where 1500 is neutral)
rc 3 1800  # More throttle
rc 3 1500  # Less throttle

# Control roll (ailerons)
rc 1 1700  # Roll right
rc 1 1300  # Roll left
rc 1 1500  # Neutral

# Control pitch (elevator)
rc 2 1700  # Pitch up
rc 2 1300  # Pitch down
rc 2 1500  # Neutral
```

### Step 7: Return to Launch
```bash
mode RTL
```
Aircraft will automatically fly back to launch point.

### Step 8: Disarm
```bash
disarm
```

---

## Flight Modes Reference

### Manual Modes
| Mode | Description | Use Case |
|------|-------------|----------|
| MANUAL | Direct pilot control, no stabilization | Advanced pilots only |
| STABILIZE | Stabilizes aircraft but doesn't hold altitude | Similar to MANUAL with training wheels |
| ACRO | Acrobatic mode for aerobatics | Stunts and advanced maneuvers |

### Assisted Modes
| Mode | Description | Use Case |
|------|-------------|----------|
| FBWA | Fly-By-Wire A: stabilization + altitude hold | Most common manual flying mode |
| FBWB | Fly-By-Wire B: stabilization + altitude + airspeed | Easier flying, holds altitude and speed |
| CRUISE | Like FBWB but can navigate to waypoints | Long distance cruising |

### Autonomous Modes
| Mode | Description | Use Case |
|------|-------------|----------|
| AUTO | Follows loaded mission waypoints | Autonomous missions |
| RTL | Return to Launch: flies back to takeoff location | Emergency return or end of mission |
| LOITER | Circle at current location | Holding pattern or waiting |
| GUIDED | Controlled by GCS commands | Dynamic mission updates |

### Special Modes
| Mode | Description | Use Case |
|------|-------------|----------|
| CIRCLE | Continuously circles a point | Observation or waiting |
| TAKEOFF | Automated takeoff | Mission start |
| LAND | Automated landing | Mission end |
| QHOVER | QuadPlane hover mode | VTOL aircraft only |

---

## RC Channel Reference

| Channel | Function | Values |
|---------|----------|--------|
| 1 | Roll (Ailerons) | 1000-2000 (1500=neutral) |
| 2 | Pitch (Elevator) | 1000-2000 (1500=neutral) |
| 3 | Throttle | 1000-2000 (1000=idle, 2000=full) |
| 4 | Yaw (Rudder) | 1000-2000 (1500=neutral) |
| 5 | Flight Mode | Depends on MODE_CH setting |

---

## Common SITL Scenarios

### Scenario 1: Basic Takeoff and Landing

```bash
# Start SITL
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane -L CMAC --console --map

# Wait for GPS lock
# ...

# Arm and takeoff
mode FBWA
arm throttle
rc 3 1700

# Fly around
# (Use rc commands to control)

# Return and land
mode RTL
# Wait for aircraft to return and land automatically
```

### Scenario 2: Parameter Exploration

```bash
# Start SITL
# ...

# Check current TECS parameters
param show TECS_*

# Modify climb rate
param set TECS_CLMB_MAX 15

# Test and observe changes
mode FBWA
arm throttle
rc 3 1800
# Watch how climb rate changes
```

### Scenario 3: Testing Failsafes

```bash
# Start SITL
# ...

# Configure battery failsafe
param set BATT_LOW_VOLT 14.0
param set BATT_FS_LOW_ACT 1  # RTL on low battery

# Configure RC failsafe
param set FS_SHORT_ACTN 1  # RTL on short failsafe
param set FS_LONG_ACTN 2   # Land on long failsafe

# Test by simulating RC loss (in SITL, this is harder to simulate directly,
# but you can manually trigger RTL to observe behavior)
```

---

## Troubleshooting SITL

### SITL won't start

**Check:**
```bash
# Are you in the right directory?
pwd
# Should show: /home/username/ardupilot/ArduPlane

# Is ArduPlane built?
ls ../build/sitl/bin/arduplane
```

**Fix:**
```bash
cd ~/ardupilot/ArduPlane
../waf plane
```

### No GPS lock

**Normal:** Wait 10-30 seconds for simulated GPS

**If it takes longer:**
- Check console for errors
- Restart SITL
- Try different location: `-L CMAC`

### Cannot arm

**Check console for PreArm errors:**
- `PreArm: Need 3D Fix` → Wait for GPS
- `PreArm: Compass not calibrated` → Use `arm throttle force` (SITL only)
- `PreArm: RC not calibrated` → Switch to FBWA mode first

### Map window doesn't appear

**Cause:** X server not configured

**Fix:** See [X Server Setup Guide](../Installation_Scripts/setup_x_server.md)

**Workaround:** Start without map:
```bash
Tools/autotest/sim_vehicle.py -v ArduPlane --console
```

### Aircraft crashes immediately

**Common causes:**
1. Not in stabilized mode (use FBWA instead of MANUAL)
2. Not enough throttle
3. Incorrect parameter configuration

**Solution:**
```bash
# Use FBWA mode for easier flying
mode FBWA
arm throttle
rc 3 1700  # 70% throttle
```

---

## Saving Your Session

### Save Parameters
```bash
param save ~/my_params.parm
```

### Load Parameters
```bash
param load ~/my_params.parm
```

### Save Mission
```bash
wp save ~/my_mission.txt
```

### Load Mission
```bash
wp load ~/my_mission.txt
```

---

## Next Steps

1. [ ] Practice basic flight in FBWA mode
2. [ ] Experiment with different flight modes
3. [ ] Try [Example Mission Plans](EXAMPLE_MISSIONS.md)
4. [ ] Explore [Parameter Tuning Guide](PARAMETER_GUIDE.md)
5. [ ] Test failsafe scenarios
6. [ ] Create and test custom missions

---

## Additional Resources

- [ArduPilot SITL Docs](https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html)
- [MAVProxy Documentation](https://ardupilot.org/mavproxy/)
- [Flight Modes](https://ardupilot.org/plane/docs/flight-modes.html)
- [Main Onboarding Guide](../Onboarding_Documentation/ArduPilot_Onboarding_Guide.md)

---

**Last Updated:** 2026-02-03
