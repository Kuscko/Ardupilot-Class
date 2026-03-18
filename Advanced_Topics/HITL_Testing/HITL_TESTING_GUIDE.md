# Hardware-in-the-Loop (HITL) Testing Guide

HITL connects a real flight controller to a simulator, running actual firmware with real sensors while simulating flight dynamics.

---

## HITL vs SITL Comparison

| Feature   | SITL         | HITL                        | Real Flight   |
| --------- | ------------ | --------------------------- | ------------- |
| Hardware  | None         | Flight controller           | Full vehicle  |
| Sensors   | Simulated    | Real (IMU, baro, compass)   | Real          |
| GPS       | Simulated    | Simulated                   | Real          |
| Dynamics  | Simulated    | Simulated                   | Real          |
| Cost      | Free         | Low                         | High          |
| Risk      | None         | None                        | Crash risk    |
| Use Case  | Code testing | Hardware validation         | Final testing |

---

## HITL Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│  Computer (Simulator)                                        │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Mission Planner / MAVProxy                       │       │
│  └────────────────┬──────────────────────────────────┘       │
│                   │ MAVLink (USB/Serial)                     │
│  ┌────────────────▼──────────────────────────────────┐       │
│  │  Flight Simulator (X-Plane, RealFlight, JSBSim)   │       │
│  │  - Physics simulation                              │       │
│  │  - Send sensor data (GPS, airspeed, etc.)         │       │
│  └────────────────┬──────────────────────────────────┘       │
└───────────────────┼──────────────────────────────────────────┘
                    │ MAVLink (Serial/USB)
┌───────────────────▼──────────────────────────────────────────┐
│  Flight Controller (Real Hardware)                           │
│  - Real IMU, barometer, compass                             │
│  - Receives simulated GPS, airspeed from sim                │
│  - Runs real control loops                                  │
│  - Sends servo outputs to simulator                         │
└──────────────────────────────────────────────────────────────┘
```

---

## Step 1: Prepare Flight Controller

### Enable HITL Mode

```bash
mavproxy.py --master=/dev/ttyACM0 --baudrate=115200
```

```bash
param set SIM_ENABLED 1
param set GPS_TYPE 100
param set ARSPD_TYPE 100
param set BRD_SAFETY_DEFLT 0
param save
reboot
```

Verify:

```bash
param show SIM_*
param show GPS_TYPE
param show ARSPD_TYPE
```

---

## Step 2: Simulator Configuration

### Option 1: X-Plane (Recommended)

```bash
git clone https://github.com/ArduPilot/XPlane-plugin.git
cd XPlane-plugin
cp -r ardupilot /path/to/X-Plane/Resources/plugins/
```

In X-Plane Settings → Data Output, enable: Position, Speeds, Attitude, Angular velocities.

### Option 2: JSBSim (Lightweight)

```bash
sudo apt-get install jsbsim
```

### Option 3: RealFlight

Requires RealFlight RF9 or RF9.5 and the RealFlight Link utility.

---

## Step 3: Start HITL Session

```bash
# Connect to flight controller
mavproxy.py --master=/dev/ttyACM0 --baudrate=115200 --console --map
```

Verify connection:

```bash
gps status   # Should show: fix_type=3, satellites_visible=10+
watch ATT    # Should show real-time attitude
```

---

## Step 4: Testing Workflow

### Manual Flight Test

```bash
mode MANUAL
arm throttle
# Advance throttle in X-Plane, verify control surface responses
disarm
```

### Stabilized Flight Test

```bash
mode FBWA
arm throttle
# Aircraft should self-level when sticks centered
disarm
```

### Auto Mission Test

```bash
wp load simple_mission.waypoints
wp list
mode AUTO
arm throttle
# Monitor mission execution in X-Plane
mode RTL
disarm
```

### Data Logging

```bash
param set LOG_BACKEND_TYPE 1
param set LOG_DISARMED 1
param set LOG_BITMASK 1048575
param save

log list
log download latest
```

---

## Troubleshooting

### Flight Controller Not Entering HITL Mode

```bash
param show SIM_ENABLED
param show GPS_TYPE
param show ARSPD_TYPE
reboot
```

Ensure firmware supports HITL (use recent stable release).

### No GPS Fix

```bash
param set GPS_TYPE 100
param save
reboot
```

Verify X-Plane is running with plugin loaded and data output enabled.

### Simulator Not Receiving Control Outputs

```bash
arm throttle
param show SERVO*_FUNCTION

# Test servo outputs manually
servo set 1 1500  # Neutral
servo set 1 1800  # Move servo
```

### IMU/Sensor Data Errors

```bash
accelcal     # Calibrate accelerometers
compassmot   # Compass calibration if needed
```

### Communication Timeouts

```bash
param set SERIAL0_BAUD 57  # Reduce from 115200 to 57600
```

Check for other programs using the serial port:

```bash
lsof | grep ttyACM0
```

### X-Plane Plugin Not Loading

Verify plugin path: `X-Plane/Resources/plugins/ardupilot/`

Check `X-Plane/Log.txt` for errors. Requires X-Plane 10.51+.

---

## HITL Best Practices

1. Start with basic MANUAL flight, progress to FBWA then AUTO
2. Always calibrate accels and compass on real hardware
3. Enable comprehensive logging (`LOG_BITMASK = 1048575`)
4. Test one feature at a time
5. Run same tests in SITL and HITL to identify hardware-specific issues

---

## Pre-Flight Checklist

- [ ] Flight controller powered and connected via USB
- [ ] HITL parameters set (SIM_ENABLED, GPS_TYPE, ARSPD_TYPE)
- [ ] Sensors calibrated (accel, compass, gyro)
- [ ] X-Plane running with ArduPilot plugin loaded
- [ ] GPS showing 3D fix with 10+ satellites
- [ ] No "PreArm" error messages
- [ ] Control surfaces responding to RC input
- [ ] Logging enabled

---

## What HITL Validates vs Does Not

**Validated:** Flight controller hardware, sensor calibration, firmware stability, mission logic, mode switching, failsafes

**Not validated:** Real-world GPS, actual aerodynamics, motor/ESC/prop performance, battery endurance, wind response, communication range, vibration from motors

---

- [ArduPilot HITL Documentation](https://ardupilot.org/dev/docs/hitl-simulators.html)
- [X-Plane Plugin Setup](https://ardupilot.org/dev/docs/sitl-with-xplane.html)
- [JSBSim](https://jsbsim.sourceforge.net/)

**Author:** Patrick Kelly (@Kuscko)
