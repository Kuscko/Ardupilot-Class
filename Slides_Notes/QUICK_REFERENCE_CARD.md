# ArduPilot Quick Reference Card

## Essential SITL Commands

### Starting SITL

```bash
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane -L CMAC --console --map
```

### Basic Flight

```bash
mode FBWA              # Stabilized flight
arm throttle           # Enable motors
rc 3 1700              # Set throttle to 70%
mode RTL               # Return to launch
disarm                 # Disable motors
```

---

## Essential MAVProxy Commands

| Command | Example | Description |
|---------|---------|-------------|
| `mode` | `mode FBWA` | Change flight mode |
| `arm` | `arm throttle` | Arm vehicle |
| `disarm` | `disarm` | Disarm vehicle |
| `rc` | `rc 3 1700` | Set RC channel |
| `param show` | `param show TECS_*` | Show parameters |
| `param set` | `param set THR_MAX 80` | Set parameter |
| `wp list` | `wp list` | List waypoints |
| `wp load` | `wp load mission.txt` | Load mission |

---

## Flight Modes Reference

| Mode | Type | Description |
|------|------|-------------|
| **MANUAL** | Manual | Direct control, no stabilization |
| **FBWA** | Assisted | Stabilized + altitude hold |
| **FBWB** | Assisted | Stabilized + altitude + airspeed |
| **AUTO** | Autonomous | Follow mission waypoints |
| **RTL** | Autonomous | Return to launch point |
| **LOITER** | Autonomous | Circle at current location |
| **GUIDED** | Autonomous | GCS-commanded navigation |

---

## Critical Parameters

### TECS (Altitude/Speed Control)

```bash
TECS_TIME_CONST    # Response speed (default 5.0)
TECS_CLMB_MAX      # Max climb rate m/s (default 5.0)
TECS_SINK_MAX      # Max descent rate m/s (default 5.0)
TECS_SPDWEIGHT     # Speed vs alt priority (default 1.0)
```

### Airspeed

```bash
ARSPD_FBW_MIN      # Min airspeed m/s (default 12)
ARSPD_FBW_MAX      # Max airspeed m/s (default 22)
TRIM_ARSPD_CM      # Cruise airspeed cm/s (default 1500)
```

### Throttle

```bash
THR_MIN            # Min throttle % (default 0)
THR_MAX            # Max throttle % (default 75)
TRIM_THROTTLE      # Cruise throttle % (default 45)
```

### Failsafes

```bash
FS_SHORT_ACTN      # Short failsafe action (0=none, 1=RTL)
FS_LONG_ACTN       # Long failsafe action (0=none, 2=Land)
BATT_LOW_VOLT      # Low battery voltage
BATT_CRT_VOLT      # Critical battery voltage
```

---

## Lua Scripting Quick Start

### Enable Scripting

```bash
param set SCR_ENABLE 1
# Restart SITL
```

### Basic Script Template

```lua
function update()
    gcs:send_text(6, "Hello!")
    return update, 1000  -- Run every 1 second
end
return update, 1000
```

### Common API Functions

```lua
ahrs:get_location()        -- Get position
battery:voltage(0)         -- Get battery voltage
param:get('NAME')          -- Get parameter
param:set('NAME', value)   -- Set parameter
vehicle:set_mode(num)      -- Change mode
gcs:send_text(level, msg)  -- Send message
```

---

## MAVLink Python Quick Start

### Connect to Autopilot

```python
from pymavlink import mavutil

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()
print(f"Connected to system {master.target_system}")
```

### Read Messages

```python
msg = master.recv_match(type='VFR_HUD', blocking=True, timeout=5)
if msg:
    print(f"Airspeed: {msg.airspeed} m/s")
    print(f"Altitude: {msg.alt} m")
```

### Arm Vehicle

```python
master.arducopter_arm()
# or
master.mav.command_long_send(
    master.target_system, master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0, 1, 0, 0, 0, 0, 0, 0
)
```

---

## Build Commands

```bash
# Configure for SITL
./waf configure --board sitl

# Build ArduPlane
./waf plane

# Configure for hardware
./waf configure --board CubeOrangePlus

# Clean build
./waf clean

# Complete clean
./waf distclean

# List available boards
./waf list_boards
```

---

## Troubleshooting Quick Fixes

### GPS Not Locking (SITL)

```bash
# Wait 10-30 seconds
# Check console for "GPS: 3D Fix"
```

### Can't Arm

```bash
# Check PreArm messages in console
mode FBWA                # Switch to FBWA
arm throttle force       # Force arm (SITL only)
```

### SITL Won't Start

```bash
cd ~/ardupilot/ArduPlane
../waf plane            # Rebuild
# Check you're in ArduPlane directory
```

### Slow Build

```bash
# Verify building in WSL filesystem
pwd  # Should show /home/username/...
# NOT /mnt/c/...
```

---

## File Locations

```bash
~/ardupilot/                              # ArduPilot installation
~/ardupilot/build/sitl/bin/arduplane      # SITL binary
~/ardupilot/ArduPlane/scripts/            # Lua scripts (SITL)
~/ardupilot/ArduPlane/                    # Vehicle code
~/ardupilot/libraries/AP_GPS/             # Sensor drivers
~/ardupilot/libraries/AP_InertialSensor/
~/ardupilot/libraries/AP_Baro/
```

---

## Useful Links

| Resource | URL |
|----------|-----|
| **Plane Docs** | <https://ardupilot.org/plane/> |
| **Dev Docs** | <https://ardupilot.org/dev/> |
| **Parameters** | <https://ardupilot.org/plane/docs/parameters.html> |
| **MAVLink** | <https://mavlink.io/en/messages/common.html> |
| **Forum** | <https://discuss.ardupilot.org/> |
| **GitHub** | <https://github.com/ArduPilot/ardupilot> |

---

## Common MAVLink Messages

| Message | ID | Contains |
| ------- | -- | -------- |
| HEARTBEAT | 0 | Mode, armed state |
| ATTITUDE | 30 | Roll, pitch, yaw |
| GLOBAL_POSITION_INT | 33 | Position, velocity |
| VFR_HUD | 74 | Airspeed, alt, heading |
| SYS_STATUS | 1 | Battery, sensors |
| GPS_RAW_INT | 24 | GPS data |

---

## RC Channel Reference

| Channel | Function | Range |
|---------|----------|-------|
| 1 | Roll (Ailerons) | 1000-2000 (1500=neutral) |
| 2 | Pitch (Elevator) | 1000-2000 (1500=neutral) |
| 3 | Throttle | 1000-2000 (1000=idle) |
| 4 | Yaw (Rudder) | 1000-2000 (1500=neutral) |

---

## Flight Mode Numbers (for Lua/Python)

| Number | Mode |
|--------|------|
| 0 | MANUAL |
| 2 | STABILIZE |
| 5 | FBWA |
| 6 | FBWB |
| 10 | AUTO |
| 11 | RTL |
| 12 | LOITER |
| 15 | GUIDED |

---

**Last Updated:** 2026-02-03
**Version:** 1.0
