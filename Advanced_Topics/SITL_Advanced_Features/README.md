# SITL Advanced Features

## Overview

Master advanced Software-In-The-Loop (SITL) simulation capabilities for comprehensive testing, scenario validation, and edge case exploration in ArduPilot. Advanced SITL features enable realistic environmental simulation, sensor failure injection, multi-vehicle testing, and automated test scenarios [1].

This module covers wind simulation, sensor failures, custom scenarios, replay functionality, multi-vehicle coordination, and advanced debugging techniques.

## Prerequisites

Before starting this module, you should have:

- Completed basic SITL setup and operation
- Understanding of ArduPilot parameters and MAVLink
- Familiarity with command-line tools
- Python programming basics (for scripting)
- Git and ArduPilot source code access

## What You'll Learn

By completing this module, you will:

- Simulate realistic wind conditions and turbulence
- Inject sensor failures and test failsafe responses
- Run multiple simultaneous vehicle simulations
- Create custom test scenarios and locations
- Use log replay for debugging and analysis
- Control simulation speed and frame rate
- Automate testing with Python scripts
- Debug complex flight behaviors

## Key Concepts

### SITL Architecture

ArduPilot SITL simulation components [1]:

**Flight Dynamics Model:**
- JSBSim for planes
- Built-in multicopter physics
- Gazebo integration for complex scenarios
- RealFlight interface for realism

**Sensor Simulation:**
- GPS with configurable accuracy and latency
- IMU with noise and drift
- Barometer with temperature effects
- Magnetometer with declination
- Airspeed sensor with calibration errors

**Environment Simulation:**
- Wind (constant, gusts, turbulence)
- Terrain elevation data
- Atmospheric conditions
- Obstacle detection

### SITL Command-Line Options

Key startup parameters [2]:

| Option | Purpose | Example |
| ------ | ------- | ------- |
| --wind | Set wind speed/direction | --wind=10,270,2 |
| --speedup | Simulation speed multiplier | --speedup=5 |
| --home | Custom start location | --home=-35.363,149.165,584,270 |
| --model | Vehicle model | --model=quad |
| --console | Enable MAVProxy console | --console |
| --map | Enable map display | --map |

## Hands-On Practice

### Exercise 1: Simulate Wind Conditions

Test vehicle performance in various wind scenarios:

```bash
# Start SITL with constant wind
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --map --wind=15,270,2

# Wind parameters: speed(m/s),direction(deg),turbulence(m/s)
# Example: 15 m/s from west (270°), 2 m/s turbulence
```

**Wind simulation options:**

```bash
# Calm conditions
sim_vehicle.py --wind=0,0,0

# Light breeze (5 m/s from north)
sim_vehicle.py --wind=5,0,1

# Strong wind (20 m/s from south)
sim_vehicle.py --wind=20,180,3

# Gusty conditions (15 m/s base, 5 m/s gusts)
sim_vehicle.py --wind=15,90,5

# Variable wind during flight (MAVProxy command)
# In MAVProxy console:
param set SIM_WIND_SPD 10       # Wind speed
param set SIM_WIND_DIR 180      # Wind direction
param set SIM_WIND_TURB 3       # Turbulence
```

**Expected behavior:**
- Vehicle drifts downwind
- Increased control activity
- Navigation compensation
- Test autopilot wind handling

### Exercise 2: Inject Sensor Failures

Test failsafe and redundancy systems:

```bash
# Start SITL
cd ~/ardupilot/ArduCopter
sim_vehicle.py --console --map

# GPS failure simulation
param set SIM_GPS_DISABLE 1     # Disable GPS
# Wait, observe behavior
param set SIM_GPS_DISABLE 0     # Re-enable GPS

# GPS glitch (position jump)
param set SIM_GPS_GLITCH_X 100  # 100m north error
param set SIM_GPS_GLITCH_Y 50   # 50m east error
param set SIM_GPS_GLITCH_Z 20   # 20m altitude error

# Compass interference
param set SIM_MAG_ERROR 50      # 50 degree heading error

# Barometer drift
param set SIM_BARO_DRIFT 0.02   # 2 cm/s drift rate

# IMU failure
param set SIM_ACC1_FAIL 1       # Fail accelerometer 1
param set SIM_GYR1_FAIL 1       # Fail gyroscope 1

# Airspeed sensor failure (planes)
param set SIM_ARSPD_FAIL 1      # Fail airspeed sensor
```

**Test scenarios:**

```python
# gps_failure_test.py
from pymavlink import mavutil
import time

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()

# Takeoff and fly
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0, 0, 0, 0, 0, 0, 0, 50)

time.sleep(30)

# Inject GPS failure
master.mav.param_set_send(
    master.target_system,
    master.target_component,
    b'SIM_GPS_DISABLE',
    1, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)

print("GPS disabled - observing failsafe behavior")
time.sleep(60)

# Re-enable GPS
master.mav.param_set_send(
    master.target_system,
    master.target_component,
    b'SIM_GPS_DISABLE',
    0, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)

print("GPS re-enabled")
```

### Exercise 3: Multi-Vehicle Simulation

Run multiple vehicles simultaneously:

```bash
# Start first vehicle (copter)
cd ~/ardupilot/ArduCopter
sim_vehicle.py -I0 --out=udp:127.0.0.1:14550 --console --map

# In new terminal, start second vehicle (copter)
cd ~/ardupilot/ArduCopter
sim_vehicle.py -I1 --out=udp:127.0.0.1:14551 --console

# In new terminal, start third vehicle (plane)
cd ~/ardupilot/ArduPlane
sim_vehicle.py -I2 --out=udp:127.0.0.1:14552 --console

# Each vehicle has unique:
# - Instance number (-I0, -I1, -I2)
# - MAVLink port (14550, 14551, 14552)
# - System ID (1, 2, 3)
```

**Control multiple vehicles:**

```python
# multi_vehicle_control.py
from pymavlink import mavutil
import time

# Connect to all vehicles
vehicles = [
    mavutil.mavlink_connection('udp:127.0.0.1:14550'),
    mavutil.mavlink_connection('udp:127.0.0.1:14551'),
    mavutil.mavlink_connection('udp:127.0.0.1:14552'),
]

# Wait for heartbeat from each
for v in vehicles:
    v.wait_heartbeat()
    print(f"Connected to vehicle {v.target_system}")

# Arm all vehicles
for v in vehicles:
    v.mav.command_long_send(
        v.target_system,
        v.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, 1, 0, 0, 0, 0, 0, 0)
    print(f"Armed vehicle {v.target_system}")
    time.sleep(1)

# Coordinated takeoff
for i, v in enumerate(vehicles):
    v.mav.command_long_send(
        v.target_system,
        v.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0, 0, 0, 0, 0, 0, 0, 50 + (i * 10))  # Staggered altitudes
    print(f"Vehicle {v.target_system} taking off to {50 + (i * 10)}m")
```

### Exercise 4: Custom Start Locations

Test missions at different geographic locations:

```bash
# Custom home location (lat, lon, alt, heading)
# Example: San Francisco
sim_vehicle.py --home=37.7749,-122.4194,10,0 --console --map

# Example: Tokyo
sim_vehicle.py --home=35.6762,139.6503,40,90 --console --map

# Example: Sydney
sim_vehicle.py --home=-33.8688,151.2093,50,180 --console --map

# High altitude location (affects performance)
sim_vehicle.py --home=27.9881,86.9250,5364,0 --console --map  # Mt. Everest base camp

# Set location during runtime
# In MAVProxy:
# reboot
# Then vehicle will use new home on next start
```

**Test terrain following at custom location:**

```bash
# Enable terrain in SITL
param set TERRAIN_ENABLE 1
param set TERRAIN_FOLLOW 1

# Fly mission over mountainous terrain
# Vehicle follows terrain contours
```

### Exercise 5: Log Replay for Debugging

Replay flight logs to reproduce issues:

```bash
# Record flight with full logging
param set LOG_BITMASK 2293759
param set LOG_REPLAY 1
param write

# Fly mission (or reproduce issue)
# ...

# Find log file
cd logs
ls -lt

# Replay log in SITL
sim_vehicle.py --console --map --replay=logs/latest.BIN

# During replay:
# - Vehicle follows exact log path
# - Can inspect parameters at any time
# - Useful for debugging crashes
# - Test parameter changes without flying
```

**Replay with modified parameters:**

```bash
# Start replay
sim_vehicle.py --replay=logs/crash.BIN

# In MAVProxy, modify parameters
param set ATC_RAT_RLL_P 0.15    # Test new PID value

# Observe if crash still occurs
# Iterate parameter tuning
```

### Exercise 6: Control Simulation Speed

Speed up or slow down simulation:

```bash
# Run at 5x real-time (fast testing)
sim_vehicle.py --speedup=5 --console

# Run at 0.5x real-time (slow motion debugging)
sim_vehicle.py --speedup=0.5 --console

# Dynamic speed control in MAVProxy
set speedup 10      # 10x speed
set speedup 1       # Real-time
set speedup 0.25    # Quarter speed

# Useful for:
# - Fast mission validation (speedup > 1)
# - Slow-motion analysis (speedup < 1)
# - Long-duration testing (speedup > 5)
```

**Automated long-duration test:**

```python
# endurance_test.py
from pymavlink import mavutil
import time

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()

# Set 10x speed
master.mav.param_set_send(
    master.target_system,
    master.target_component,
    b'SIM_SPEEDUP',
    10, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)

# Fly 2-hour mission (simulated in 12 minutes real-time)
print("Starting 2-hour endurance test at 10x speed")
# ... fly mission ...
```

### Exercise 7: Advanced Scenario Testing

Create complex test scenarios:

```bash
# Scenario: Emergency landing with wind
sim_vehicle.py --wind=15,270,5 --console --map

# In MAVProxy:
mode LOITER
arm throttle
# Climb to altitude
# Simulate engine failure
param set SIM_ENGINE_FAIL 1
# Observe emergency landing behavior

# Scenario: Multi-vehicle coordination
# Terminal 1: Leader vehicle
sim_vehicle.py -I0 --out=udp:127.0.0.1:14550

# Terminal 2: Follower vehicle
sim_vehicle.py -I1 --out=udp:127.0.0.1:14551

# Script: Follower maintains formation
```

**Battery failure scenario:**

```python
# battery_failure_test.py
from pymavlink import mavutil
import time

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()

# Start mission
# ...

# Simulate sudden battery voltage drop
master.mav.param_set_send(
    master.target_system,
    master.target_component,
    b'SIM_BATT_VOLTAGE',
    10.0,  # Critical voltage
    mavutil.mavlink.MAV_PARAM_TYPE_REAL32)

print("Battery failsafe should trigger")
time.sleep(30)

# Observe RTL or land behavior
```

## Common Issues

### Issue 1: SITL Won't Start

**Symptoms:**
- SITL fails to launch
- Port already in use
- Module not found errors

**Solutions:**

```bash
# Check for existing SITL instances
ps aux | grep sim_vehicle
# Kill any existing instances
pkill -f sim_vehicle

# Clean build artifacts
cd ~/ardupilot
./waf clean
./waf configure --board sitl
./waf plane

# Install missing Python modules
pip3 install pymavlink mavproxy

# Check Python version (3.6+ required)
python3 --version

# Specify custom port
sim_vehicle.py --master=udp:127.0.0.1:14551
```

### Issue 2: Simulation Too Slow

**Symptoms:**
- Jerky vehicle motion
- Delayed response
- Frame rate drops

**Solutions:**

```bash
# Reduce speedup
set speedup 1

# Disable map and console
sim_vehicle.py  # Minimal UI

# Close other applications
# Reduce CPU load

# Increase frame rate limit
param set SIM_RATE_HZ 400  # Default

# Use lighter vehicle model
sim_vehicle.py --model=quad  # Instead of gazebo
```

### Issue 3: Wind Simulation Not Working

**Symptoms:**
- No wind effect visible
- Vehicle doesn't drift
- Wind parameters ignored

**Solutions:**

```bash
# Verify wind enabled
param show SIM_WIND_SPD
param show SIM_WIND_DIR

# Set wind at runtime
param set SIM_WIND_SPD 15
param set SIM_WIND_DIR 180
param set SIM_WIND_TURB 3

# Check vehicle model supports wind
# Not all models have aerodynamic simulation

# Restart SITL with wind
sim_vehicle.py --wind=15,180,3
```

### Issue 4: Multi-Vehicle Conflicts

**Symptoms:**
- Vehicles interfere with each other
- Port conflicts
- System ID conflicts

**Solutions:**

```bash
# Ensure unique instance numbers
sim_vehicle.py -I0  # Vehicle 1
sim_vehicle.py -I1  # Vehicle 2

# Use different ports
--out=udp:127.0.0.1:14550  # Vehicle 1
--out=udp:127.0.0.1:14551  # Vehicle 2

# Check system IDs
param show SYSID_THISMAV
# Should be different for each vehicle

# Use separate log directories
sim_vehicle.py -I0 --log-dir=/tmp/vehicle0
sim_vehicle.py -I1 --log-dir=/tmp/vehicle1
```

### Issue 5: Replay Issues

**Symptoms:**
- Replay crashes immediately
- Vehicle doesn't follow log path
- Parameter mismatches

**Solutions:**

```bash
# Verify log file valid
ls -lh logs/

# Use correct vehicle type
# If log from copter, replay with copter
cd ~/ardupilot/ArduCopter
sim_vehicle.py --replay=logs/latest.BIN

# Check LOG_REPLAY enabled when recording
param show LOG_REPLAY
# Must be 1 in original flight

# Replay with matching parameters
# Use same parameter file as original flight
param load saved_params.param
```

## Advanced SITL Techniques

### Automated Test Suite

```python
# test_suite.py
from pymavlink import mavutil
import time

class SITLTester:
    def __init__(self, connection_string):
        self.master = mavutil.mavlink_connection(connection_string)
        self.master.wait_heartbeat()

    def test_takeoff_land(self):
        """Test basic takeoff and landing"""
        print("Test: Takeoff and Land")

        # Arm
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0, 1, 0, 0, 0, 0, 0, 0)

        time.sleep(2)

        # Takeoff
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0, 0, 0, 0, 0, 0, 0, 50)

        time.sleep(30)

        # Land
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_LAND,
            0, 0, 0, 0, 0, 0, 0, 0)

        time.sleep(30)

        print("Test: PASSED")

    def test_gps_failsafe(self):
        """Test GPS loss handling"""
        print("Test: GPS Failsafe")

        # Arm and takeoff
        # ...

        # Disable GPS
        self.master.mav.param_set_send(
            self.master.target_system,
            self.master.target_component,
            b'SIM_GPS_DISABLE',
            1, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)

        time.sleep(30)

        # Verify failsafe triggered
        # Check mode changed to LAND or RTL

        print("Test: PASSED")

# Run tests
tester = SITLTester('udp:127.0.0.1:14550')
tester.test_takeoff_land()
tester.test_gps_failsafe()
```

### Physics-Based Testing

```bash
# Test different vehicle configurations
# Heavy payload
param set SIM_WEIGHT_KG 25  # 25kg total weight

# Center of gravity offset
param set SIM_CG_OFFSET_X 0.1  # 10cm forward
param set SIM_CG_OFFSET_Y 0.0
param set SIM_CG_OFFSET_Z 0.0

# Motor failure
param set SIM_ENGINE_FAIL 1    # Engine/motor 1 fails
param set SIM_ENGINE_MUL 0.5   # All motors at 50% power

# Servo failure
param set SIM_SERVO_FAIL 1     # Servo channel 1 fails
```

## Additional Resources

- [SITL Documentation](https://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html) [1] - Complete SITL guide
- [SITL Advanced Features](https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html) [2] - Advanced testing techniques
- [Gazebo SITL](https://ardupilot.org/dev/docs/sitl-with-gazebo.html) - Gazebo integration
- [RealFlight SITL](https://ardupilot.org/dev/docs/sitl-with-realflight.html) - RealFlight simulator

### Testing Tools

- [MAVProxy](https://ardupilot.org/mavproxy/) - Command-line GCS
- [DroneKit](https://dronekit.io/) - Python API for vehicles
- [PyMAVLink](https://github.com/ArduPilot/pymavlink) - MAVLink Python library

## Next Steps

After mastering advanced SITL features:

1. **Automated Testing** - Build comprehensive test automation
2. **Gazebo Integration** - Complex 3D environments
3. **Hardware-in-the-Loop** - Transition to HITL testing
4. **Continuous Integration** - Integrate tests into CI/CD pipeline

---

**Sources:**

[1] https://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html
[2] https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html
