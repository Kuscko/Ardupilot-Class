# Hardware-in-the-Loop (HITL) Testing

## Overview

Hardware-in-the-Loop (HITL) testing bridges the gap between pure software simulation (SITL) and real-world flight testing by running ArduPilot firmware on actual hardware while using simulated vehicle dynamics and sensors [1].

HITL allows you to test real hardware configurations, sensor drivers, and timing issues without the risks and costs of actual flight testing.

## Prerequisites

Before starting this module, you should have:

- SITL setup and experience
- Flight controller hardware (Pixhawk, Cube, etc.)
- USB connection to flight controller
- Understanding of ArduPilot parameter configuration
- Ground station software (Mission Planner or QGroundControl)

## What You'll Learn

By completing this module, you will:

- Understand HITL architecture and when to use it
- Configure flight controller for HITL mode
- Connect HITL to simulation backends
- Test hardware configurations safely
- Troubleshoot HITL connection issues
- Validate sensor drivers and timing

## Key Concepts

### HITL vs SITL vs Real Flight

| Aspect | SITL | HITL | Real Flight |
|--------|------|------|-------------|
| Hardware | None | Flight controller | Full system |
| Sensors | Simulated | Real hardware sensors or simulated | Real sensors |
| Dynamics | Simulated | Simulated | Real physics |
| Safety | Very safe | Safe | Requires precautions |
| Cost | Free | Low | High (fuel, wear) |
| Iteration | Very fast | Fast | Slow |

### HITL Architecture

```
┌─────────────────────┐
│  Simulator          │
│  (FlightGear/X-Plane│
│   JSBSim)           │
│  - Vehicle dynamics │
│  - Visual display   │
└──────────┬──────────┘
           │ MAVLink
           │ (sensor data, GPS)
┌──────────▼──────────┐
│  Flight Controller  │
│  (Real Hardware)    │
│  - Real ArduPilot   │
│  - Real sensors     │
│  - Real timing      │
└──────────┬──────────┘
           │ PWM outputs
┌──────────▼──────────┐
│  Simulator          │
│  (reads PWM)        │
└─────────────────────┘
```

### When to Use HITL

**Use HITL when:**
- Testing specific hardware configurations
- Validating sensor drivers
- Checking real-time performance
- Testing hardware integration
- Preparing for first flights

**Use SITL when:**
- Rapid algorithm development
- Testing without hardware
- Automated testing/CI
- Learning ArduPilot basics

## Hands-On Practice

### Exercise 1: Configure Flight Controller for HITL

Flash HITL-enabled firmware:

```bash
cd ~/ardupilot

# Build HITL firmware for your board
./waf configure --board Pixhawk1
./waf plane --enable-hitl

# Flash to flight controller
# Connect via USB
./waf plane --upload
```

**Configure HITL parameters:**

```
# Connect with Mission Planner or MAVProxy
# Set HITL mode
SERIAL0_PROTOCOL 2        # MAVLink2 on USB
SIM_ENABLED 1             # Enable HITL mode
param write
reboot
```

### Exercise 2: Start HITL Simulation

**Method 1: Using sim_vehicle.py with hardware**

```bash
cd ~/ardupilot/ArduPlane

# Start HITL with connected hardware
# Replace /dev/ttyUSB0 with your device
sim_vehicle.py --aircraft test --map --console \
    --out=udp:127.0.0.1:14550 \
    --serial0=/dev/ttyUSB0 --serial0-baud=115200
```

**Method 2: Manual setup with JSBSim**

Terminal 1 - Start JSBSim:
```bash
cd ~/ardupilot/Tools/autotest
./jsbsim/jsbsim --nice --suspend --script=jsbsim/fgout.xml
```

Terminal 2 - Connect MAVProxy:
```bash
mavproxy.py --master=/dev/ttyUSB0 --master=tcp:127.0.0.1:5760 \
    --sitl=127.0.0.1:5501 --out=127.0.0.1:14550
```

### Exercise 3: Test Basic Flight

Once HITL is running:

```bash
# In MAVProxy console
mode MANUAL
arm throttle

# Should see:
# - Flight controller armed
# - Simulated vehicle responds
# - Real sensor data from hardware

mode FBWA
# Fly around
# Test stabilization

mode AUTO
# Load mission
# Verify waypoint navigation

disarm
```

**Expected Behavior:**
- Real IMU data from flight controller
- Simulated GPS from simulator
- Real control loop timing
- Simulated aerodynamics

### Exercise 4: Test Sensor Configuration

Verify real sensors work correctly:

```bash
# Check IMU
watch -n 0.1 "mavproxy.py --master=/dev/ttyUSB0 --cmd='status'"

# Monitor specific sensors
# In MAVProxy:
status
# Shows: GPS, IMU, compass, barometer status

# Test compass calibration
mode MANUAL
# Physically rotate flight controller
# Watch compass heading change
```

### Exercise 5: Test Hardware-Specific Features

Test features that require real hardware:

**Test RC input (if connected):**
```bash
# Connect RC receiver to flight controller
# In MAVProxy:
rc 1  # Check channel 1
rc 2  # Check channel 2
# Verify RC input works
```

**Test servo outputs:**
```bash
# Connect servos to flight controller outputs
# In flight:
# Observe actual servo movements
# Verify PWM output timing
```

## Common HITL Configurations

### Configuration 1: Basic HITL (Simulated Sensors)

Use when testing without physical sensors:

```
SIM_ENABLED 1
SERIAL0_PROTOCOL 2
SERIAL0_BAUD 115200
```

**All sensors simulated by SITL backend**

### Configuration 2: Hybrid HITL (Real IMU + Simulated GPS)

Use real IMU, simulated GPS/barometer:

```
SIM_ENABLED 1
AHRS_EKF_TYPE 3          # Use EKF3
EK3_SRC1_POSXY 3         # GPS
EK3_SRC1_VELXY 3         # GPS
EK3_SRC1_POSZ 1          # Baro
```

**IMU from real hardware, GPS/baro simulated**

### Configuration 3: Full Hardware Sensors

Use all real sensors:

```
SIM_ENABLED 1
# Connect real GPS, compass, barometer
# Configure normally
# Only vehicle dynamics simulated
```

## Common Issues

### Issue: Flight Controller Not Detected

**Symptoms:** Cannot connect to /dev/ttyUSB0 or COM port

**Solutions:**

```bash
# Linux: Check device
ls -l /dev/ttyUSB* /dev/ttyACM*

# Add user to dialout group
sudo usermod -a -G dialout $USER
# Log out and back in

# Windows: Check Device Manager
# Verify COM port number
# Install USB drivers if needed
```

### Issue: No Sensor Data in Simulation

**Symptoms:** Simulator shows no GPS, altitude stays zero

**Solution:**

```bash
# Verify SIM_ENABLED
param show SIM_ENABLED
# Should be 1

# Check MAVLink connection
# In MAVProxy:
link
# Should show connections to simulator

# Restart with verbose output
sim_vehicle.py -v --debug
```

### Issue: Timing Issues / Poor Performance

**Symptoms:** Jerky simulation, timeouts, "slow system" messages

**Solutions:**

- **Reduce CPU load:** Close unnecessary programs
- **Lower sim rate:** Add `--speedup=1` to sim_vehicle.py
- **Check USB connection:** Use high-quality USB cable
- **Disable unnecessary features:** Reduce LOG_BITMASK

### Issue: Simulator and Hardware Mismatch

**Symptoms:** Vehicle behaves erratically, flips immediately

**Solutions:**

```bash
# Check frame type matches
param show FRAME_CLASS
param show FRAME_TYPE

# Verify correct vehicle type
# ArduPlane, ArduCopter, ArduRover must match simulator

# Reset parameters to defaults
param reset_nodefaults
param write
reboot
```

## HITL Test Scenarios

### Scenario 1: Pre-Flight Hardware Validation

Test hardware before first real flight:

1. Flash HITL firmware
2. Connect all sensors and peripherals
3. Run full mission in HITL
4. Verify all systems nominal
5. Check parameter values
6. Flash production firmware
7. Conduct real flight

### Scenario 2: Failsafe Testing

Test failsafes safely:

```bash
# In HITL:
# Simulate GPS loss
param set SIM_GPS_DISABLE 1

# Simulate low battery
param set SIM_BATT_VOLTAGE 10.5

# Simulate RC loss
# Unplug RC receiver

# Verify failsafes trigger correctly
```

### Scenario 3: Mission Validation

Test complex missions:

1. Load mission waypoints
2. Run in HITL with hardware
3. Verify waypoint navigation
4. Check altitude changes
5. Test speed transitions
6. Validate geofence behavior

## Additional Resources

- [ArduPilot HITL](https://ardupilot.org/dev/docs/hitl.html) [1] - Official HITL guide
- [SITL vs HITL](https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html) [2] - Comparison
- [JSBSim](https://jsbsim.sourceforge.net/) [3] - JSBSim documentation
- [MAVProxy](https://ardupilot.org/mavproxy/) [4] - MAVProxy guide

## Next Steps

After mastering HITL testing:

1. **Real Hardware Testing** - Progress to actual flight tests
2. **Automated Testing** - Create automated HITL test scripts
3. **Custom Simulators** - Integrate custom simulation environments
4. **Continuous Integration** - Add HITL to CI/CD pipeline

---

**Sources:**

[1] https://ardupilot.org/dev/docs/hitl.html
[2] https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html
[3] https://jsbsim.sourceforge.net/
[4] https://ardupilot.org/mavproxy/
