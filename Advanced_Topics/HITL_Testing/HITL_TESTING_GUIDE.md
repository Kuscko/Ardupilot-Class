# Hardware-in-the-Loop (HITL) Testing Guide

## Overview

Hardware-in-the-Loop (HITL) testing connects a real flight controller to a simulator, running actual firmware with real sensors while simulating flight dynamics. This bridges the gap between SITL and real-world flight testing.

---

## HITL vs SITL Comparison

| Feature | SITL | HITL | Real Flight |
|---------|------|------|-------------|
| **Hardware** | None | Flight controller | Full vehicle |
| **Sensors** | Simulated | Real (IMU, baro, compass) | Real |
| **GPS** | Simulated | Simulated | Real |
| **Dynamics** | Simulated | Simulated | Real |
| **Motors** | Simulated | Simulated | Real |
| **Cost** | Free | Low | High |
| **Risk** | None | None | Crash risk |
| **Use Case** | Code testing | Hardware validation | Final testing |

**When to Use HITL:**
- Testing new flight controller hardware
- Validating sensor calibration procedures
- Testing firmware before real flights
- Training with actual hardware interface
- Debugging hardware-specific issues

---

## HITL Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Computer (Simulator)                                        │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Mission Planner / MAVProxy                       │       │
│  │  - Send MAVLink commands                          │       │
│  │  - Monitor telemetry                              │       │
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
│  ┌──────────────────────────────────────────────────┐       │
│  │  ArduPilot Firmware (HITL mode)                   │       │
│  │  - Real IMU, barometer, compass                   │       │
│  │  - Receives simulated GPS, airspeed from sim      │       │
│  │  - Runs real control loops                        │       │
│  │  - Sends servo outputs to simulator               │       │
│  └──────────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

---

## HITL Setup

### Prerequisites

**Hardware:**
- Flight controller (Pixhawk, Cube, etc.)
- USB cable for connection to computer
- Computer with flight simulator

**Software:**
- ArduPilot firmware (HITL-enabled build)
- Flight simulator (X-Plane 10+, RealFlight, or JSBSim)
- Mission Planner or MAVProxy
- MAVLink router (optional, for multiple connections)

---

## Step 1: Prepare Flight Controller

### Flash HITL Firmware

ArduPilot doesn't have separate HITL builds anymore. Use standard firmware and enable HITL via parameters.

**Download firmware:**
1. Go to https://firmware.ardupilot.org/
2. Navigate to `Plane/stable/`
3. Select your board (e.g., `CubeOrange`)
4. Download `arduplane.apj`

**Flash via Mission Planner:**
1. Connect flight controller via USB
2. Open Mission Planner
3. Go to **SETUP → Install Firmware**
4. Select **ArduPlane**
5. Click **Load custom firmware**
6. Select downloaded `.apj` file
7. Wait for flash to complete

**Flash via command line:**
```bash
# Using pymavlink
mavproxy.py --master=/dev/ttyACM0 --load-firmware arduplane.apj
```

### Enable HITL Mode

**Connect to flight controller:**
```bash
# Via Mission Planner or MAVProxy
mavproxy.py --master=/dev/ttyACM0 --baudrate=115200
```

**Set HITL parameters:**
```bash
# Enable HITL simulation
param set SIM_ENABLED 1

# Set GPS type to HITL
param set GPS_TYPE 100

# Set airspeed sensor to HITL
param set ARSPD_TYPE 100

# Disable safety switch (optional, for testing)
param set BRD_SAFETY_DEFLT 0

# Save parameters
param save

# Reboot flight controller
reboot
```

**Verify HITL mode:**
```bash
# Check SIM parameters are set
param show SIM_*
param show GPS_TYPE
param show ARSPD_TYPE
```

---

## Step 2: Simulator Configuration

### Option 1: X-Plane (Recommended)

**Install X-Plane:**
1. Download X-Plane 10 or later
2. Install with default settings
3. Download aircraft models suitable for testing

**Configure ArduPilot plugin:**
```bash
# Download ArduPilot X-Plane plugin
cd ~/Downloads
git clone https://github.com/ArduPilot/XPlane-plugin.git
cd XPlane-plugin

# Copy to X-Plane plugins directory
# Linux/Mac:
cp -r ardupilot /path/to/X-Plane/Resources/plugins/

# Windows:
# Copy ardupilot folder to C:\X-Plane 11\Resources\plugins\
```

**X-Plane settings:**
1. Launch X-Plane
2. Select aircraft (e.g., Cessna 172)
3. Go to **Settings → Data Output**
4. Enable required data outputs:
   - Position (lat/lon/alt)
   - Speeds
   - Attitude
   - Angular velocities

**Start X-Plane:**
- Aircraft will connect to flight controller automatically
- Check for "ArduPilot connected" message

### Option 2: JSBSim (Lightweight)

**Install JSBSim:**
```bash
# Ubuntu/Debian
sudo apt-get install jsbsim

# Or build from source
git clone https://github.com/JSBSim-Team/jsbsim.git
cd jsbsim
mkdir build && cd build
cmake ..
make
sudo make install
```

**Run JSBSim with ArduPilot:**
```bash
# Start JSBSim simulator
cd ~/ardupilot/Tools/autotest
./sim_vehicle.py --vehicle=ArduPlane --aircraft=Rascal --console --map

# Connect to real hardware
# (This actually starts SITL, for pure HITL use X-Plane or RealFlight)
```

### Option 3: RealFlight

**Requirements:**
- RealFlight RF9 or RF9.5
- RealFlight Link utility

**Setup:**
1. Install RealFlight
2. Download RealFlight Link from ArduPilot
3. Configure serial connection between RealFlight and flight controller
4. Start RealFlight with ArduPilot aircraft model

---

## Step 3: Connect Everything

### Connection Diagram

```
┌──────────────┐         USB          ┌─────────────────┐
│   Computer   ├─────────────────────▶│ Flight Controller│
│              │                      │   (HITL mode)   │
│              │◀─────────────────────┤                 │
└──────┬───────┘    MAVLink Telemetry └─────────────────┘
       │
       │ Localhost/Network
       │
┌──────▼───────┐
│  X-Plane or  │
│  Simulator   │
│              │
└──────────────┘
```

### Start HITL Session

**Terminal 1: Start Mission Planner/MAVProxy**
```bash
# Connect to flight controller
mavproxy.py --master=/dev/ttyACM0 --baudrate=115200 --console --map

# Or use Mission Planner (Windows)
# Click "Connect" and select COM port
```

**Terminal 2: Start X-Plane**
```bash
# Launch X-Plane with ArduPilot plugin enabled
# Select aircraft
# Position aircraft on runway
```

**Verify connection:**
```bash
# In MAVProxy, check GPS status
gps status

# Should show:
# GPS_RAW_INT: fix_type=3 (3D fix)
# satellites_visible=10+

# Check attitude
watch ATT

# Should show real-time attitude from flight controller
```

---

## Step 4: Testing Workflow

### Pre-flight Checks

**Check sensors:**
```bash
# IMU (should be real sensor data)
watch IMU

# Barometer (real)
watch BARO

# Compass (real)
watch COMPASS

# GPS (simulated from X-Plane)
watch GPS

# Airspeed (simulated from X-Plane)
watch ARSP
```

**Check control surfaces:**
```bash
# Arm the vehicle
arm throttle

# Check servo outputs in X-Plane
# Move RC sticks and verify control surface movement
```

### Flight Test Procedure

**1. Manual Flight Test**
```bash
# Set mode to MANUAL
mode MANUAL

# Arm
arm throttle

# In X-Plane, advance throttle
# Verify aircraft responds correctly

# Test control surfaces
# Roll: Check aileron response
# Pitch: Check elevator response
# Yaw: Check rudder response

# Disarm
disarm
```

**2. Stabilized Flight Test**
```bash
# Set mode to FBWA (Fly-By-Wire A)
mode FBWA

# Arm and takeoff in X-Plane
arm throttle

# Verify stabilization
# Aircraft should self-level when sticks centered

# Test altitude hold
# Pitch stick controls climb/descend

# Disarm after landing
disarm
```

**3. Auto Mission Test**
```bash
# Load a simple mission
wp load simple_mission.waypoints

# Verify waypoints
wp list

# Set mode to AUTO
mode AUTO

# Arm and takeoff
arm throttle

# Monitor mission execution
# Aircraft should follow waypoints in X-Plane

# RTL when complete
mode RTL
disarm
```

### Data Logging

**Enable logging:**
```bash
param set LOG_BACKEND_TYPE 1
param set LOG_DISARMED 1
param set LOG_BITMASK 1048575  # Log everything for testing
param save
```

**Download logs after test:**
```bash
# List logs
log list

# Download latest
log download latest

# Analyze with Mission Planner or MAVExplorer
```

---

## Troubleshooting

### Issue 1: Flight Controller Not Entering HITL Mode

**Symptoms:**
- GPS_TYPE shows 0 or 1 instead of 100
- SIM_ENABLED shows 0

**Solutions:**
1. Verify parameters are set correctly:
   ```bash
   param show SIM_ENABLED
   param show GPS_TYPE
   param show ARSPD_TYPE
   ```

2. Ensure firmware supports HITL (use recent stable release)

3. Reboot after setting parameters:
   ```bash
   reboot
   ```

4. Check for parameter save errors:
   ```bash
   param save
   # Wait for "Parameters saved" message
   ```

### Issue 2: No GPS Fix in HITL

**Symptoms:**
- GPS shows no fix or 0 satellites
- "PreArm: Need 3D Fix" error

**Solutions:**
1. Verify X-Plane is running and aircraft is positioned

2. Check X-Plane data output settings:
   - Enable GPS data output in X-Plane settings
   - Verify plugin is loaded

3. Check GPS_TYPE parameter:
   ```bash
   param set GPS_TYPE 100  # HITL GPS
   param save
   reboot
   ```

4. Try MAVLink GPS injection (alternative method):
   ```bash
   param set GPS_TYPE 14  # MAVLink
   ```

### Issue 3: Simulator Not Receiving Control Outputs

**Symptoms:**
- Control surfaces don't move in X-Plane
- Motors don't spin

**Solutions:**
1. Check that vehicle is armed:
   ```bash
   arm throttle
   ```

2. Verify servo output channels:
   ```bash
   param show SERVO*_FUNCTION
   # Ensure correct channel assignments
   ```

3. Check X-Plane plugin is receiving MAVLink:
   - Look for servo output messages in plugin log
   - Verify serial connection is active

4. Test servo outputs manually:
   ```bash
   # In MAVProxy
   servo set 1 1500  # Neutral
   servo set 1 1800  # Move servo
   ```

### Issue 4: IMU/Sensor Data Errors

**Symptoms:**
- "PreArm: Accels not healthy"
- "PreArm: Gyros not calibrated"

**Solutions:**
1. Calibrate accelerometers:
   ```bash
   # In Mission Planner: SETUP → Accel Calibration
   # Or via MAVProxy:
   accelcal
   ```

2. Calibrate compass:
   ```bash
   # In Mission Planner: SETUP → Compass
   # Or via MAVProxy:
   compassmot  # If needed
   ```

3. Check for vibration:
   - Ensure flight controller is on vibration dampening mount
   - Check VIBE messages in logs

4. Recalibrate gyros:
   ```bash
   # Flight controller must be still
   # Reboot and wait 30 seconds without moving
   ```

### Issue 5: Communication Timeouts

**Symptoms:**
- "No Heartbeat" messages
- Intermittent connection drops

**Solutions:**
1. Check USB cable and connections:
   - Try different cable
   - Check for loose connections

2. Reduce baud rate:
   ```bash
   param set SERIAL0_BAUD 57  # 57600 instead of 115200
   ```

3. Check for other programs using serial port:
   ```bash
   # Linux
   lsof | grep ttyACM0

   # Kill conflicting processes
   ```

4. Update USB drivers (Windows):
   - Device Manager → Update drivers for COM port

### Issue 6: X-Plane Plugin Not Loading

**Symptoms:**
- No "ArduPilot connected" message in X-Plane
- Plugin not visible in X-Plane plugin menu

**Solutions:**
1. Verify plugin installation path:
   ```
   X-Plane/Resources/plugins/ardupilot/
   ```

2. Check X-Plane log file:
   ```
   X-Plane/Log.txt
   # Look for plugin loading errors
   ```

3. Ensure correct X-Plane version:
   - X-Plane 10.51 or later
   - X-Plane 11.x (recommended)

4. Rebuild plugin for your platform:
   ```bash
   cd XPlane-plugin
   mkdir build && cd build
   cmake ..
   make
   ```

---

## HITL Best Practices

1. **Start Simple:**
   - Begin with basic MANUAL flight
   - Progress to FBWA, then AUTO
   - Don't jump to complex missions immediately

2. **Calibrate Sensors:**
   - Always calibrate accels and compass on real hardware
   - Verify calibration before each HITL session

3. **Log Everything:**
   - Enable comprehensive logging (LOG_BITMASK = 1048575)
   - Review logs after each test
   - Compare HITL logs to SITL for validation

4. **Test Incrementally:**
   - Test one feature at a time
   - Verify basic flight before testing new code
   - Document any anomalies

5. **Monitor Performance:**
   - Watch for CPU load spikes
   - Check for timing issues (IMU sample rates)
   - Verify control loop timing

6. **Validate Against SITL:**
   - Run same tests in SITL and HITL
   - Compare results to identify hardware-specific issues
   - Use HITL to validate sensor behavior

---

## Common HITL Use Cases

### Use Case 1: New Hardware Validation

**Goal:** Test new flight controller hardware before flight

**Procedure:**
1. Flash firmware and configure HITL
2. Run basic flight tests (MANUAL, FBWA)
3. Check sensor health and calibration
4. Run extended AUTO mission
5. Review logs for anomalies
6. Compare to known-good hardware

### Use Case 2: Firmware Pre-release Testing

**Goal:** Validate firmware changes before release

**Procedure:**
1. Set up HITL with production hardware
2. Run regression tests (standard missions)
3. Compare performance to previous firmware
4. Test new features in HITL environment
5. Document any issues found

### Use Case 3: Sensor Fusion Debugging

**Goal:** Debug EKF or sensor issues

**Procedure:**
1. Configure HITL with real sensors
2. Inject simulated GPS errors/dropouts
3. Monitor EKF behavior in logs
4. Test failover mechanisms
5. Validate sensor switching logic

### Use Case 4: Training and Familiarization

**Goal:** Train operators on flight controller interface

**Procedure:**
1. Set up HITL with actual hardware
2. Practice arming/disarming procedures
3. Test mode switches and failsafes
4. Run mission upload/download
5. Practice emergency procedures (RTL, LAND)

---

## Advanced HITL Configurations

### Multi-Vehicle HITL

**Setup multiple flight controllers:**
```bash
# Flight Controller 1
mavproxy.py --master=/dev/ttyACM0 --out=udp:127.0.0.1:14550

# Flight Controller 2
mavproxy.py --master=/dev/ttyACM1 --out=udp:127.0.0.1:14551

# X-Plane configured for multi-vehicle
```

### HITL with Companion Computer

**Test companion computer integration:**
```
┌──────────────┐      Serial       ┌─────────────────┐
│  Companion   ├──────────────────▶│ Flight Controller│
│  Computer    │◀──────────────────┤    (HITL)       │
│ (ROS/MAVSDK) │                   └─────────────────┘
└──────────────┘
       │
       │ Network
       ▼
┌──────────────┐
│  X-Plane     │
│  Simulator   │
└──────────────┘
```

**Configuration:**
1. Connect companion computer to flight controller (serial/USB)
2. Run HITL on flight controller
3. Run companion computer code (ROS node, MAVSDK app)
4. Monitor interactions in X-Plane

---

## HITL Troubleshooting Checklist

### Pre-Flight Checklist

- [ ] Flight controller powered and connected via USB
- [ ] HITL parameters set (SIM_ENABLED, GPS_TYPE, ARSPD_TYPE)
- [ ] Sensors calibrated (accel, compass, gyro)
- [ ] X-Plane running with ArduPilot plugin loaded
- [ ] Aircraft positioned on runway in X-Plane
- [ ] MAVProxy/Mission Planner connected and receiving telemetry
- [ ] GPS showing 3D fix with 10+ satellites
- [ ] IMU data streaming normally
- [ ] No "PreArm" error messages
- [ ] Control surfaces responding to RC input
- [ ] Logging enabled

### During Flight Checklist

- [ ] Heartbeat messages received continuously
- [ ] GPS position updates in real-time
- [ ] Attitude matches X-Plane display
- [ ] Servo outputs controlling X-Plane aircraft
- [ ] Mode changes execute correctly
- [ ] Mission waypoints followed accurately
- [ ] No CPU load warnings
- [ ] No sensor health warnings
- [ ] Failsafes working as expected

### Post-Flight Checklist

- [ ] Log files downloaded and verified
- [ ] No errors in logs (check with Mission Planner)
- [ ] Vibration levels acceptable (VIBE < 30)
- [ ] EKF variance acceptable (< 0.25)
- [ ] GPS performance acceptable (HDop < 2.0)
- [ ] Control performance reviewed (ATT vs DES)
- [ ] Test results documented
- [ ] Issues logged for investigation

---

## HITL vs Real Flight Transition

### What HITL Validates

**Validated by HITL:**
- Flight controller hardware functionality
- Sensor calibration procedures
- Firmware stability on real hardware
- Basic control loop behavior
- Mission logic and waypoint following
- Mode switching and failsafes
- Parameter tuning (partially)

**NOT Validated by HITL:**
- Real-world GPS performance
- Actual flight dynamics and aerodynamics
- Motor/ESC/propeller performance
- Battery current draw and endurance
- Wind and weather response
- Communication range
- Vibration from motors and props

### Transitioning to Real Flight

After successful HITL testing:

1. **Review HITL logs thoroughly**
   - Ensure no anomalies
   - Verify all systems healthy

2. **Perform hardware check**
   - Inspect wiring and connections
   - Test motors and servos
   - Check battery voltage and capacity

3. **Conservative first flight**
   - Use conservative parameters from HITL
   - Start with MANUAL or FBWA mode
   - Keep altitude low initially
   - Have RC failsafe configured

4. **Compare flight logs**
   - Download log after first flight
   - Compare to HITL logs
   - Note any differences in behavior
   - Adjust parameters as needed

---

## Resources

**Official Documentation:**
- [ArduPilot HITL Documentation](https://ardupilot.org/dev/docs/hitl-simulators.html)
- [X-Plane Plugin Setup](https://ardupilot.org/dev/docs/sitl-with-xplane.html)
- [RealFlight Setup](https://ardupilot.org/dev/docs/sitl-with-realflight.html)

**Tools:**
- [X-Plane](https://www.x-plane.com/)
- [RealFlight](https://www.realflight.com/)
- [JSBSim](https://jsbsim.sourceforge.net/)
- [ArduPilot X-Plane Plugin](https://github.com/ArduPilot/XPlane-plugin)

**Community:**
- [ArduPilot Discourse](https://discuss.ardupilot.org/)
- [ArduPilot Discord](https://ardupilot.org/discord)

---

**Author:** Patrick Kelly (@Kuscko)
**Version:** 1.0
**Last Updated:** 2026-02-03
