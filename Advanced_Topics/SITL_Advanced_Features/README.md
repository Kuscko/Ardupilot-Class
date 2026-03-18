# SITL Advanced Features

Advanced SITL capabilities for comprehensive testing: wind simulation, sensor failure injection, multi-vehicle coordination, log replay, and simulation speed control.

## Key SITL Command-Line Options

| Option      | Purpose                      | Example                            |
| ----------- | ---------------------------- | ---------------------------------- |
| --wind      | Set wind speed/direction     | --wind=10,270,2                    |
| --speedup   | Simulation speed multiplier  | --speedup=5                        |
| --home      | Custom start location        | --home=-35.363,149.165,584,270     |
| --model     | Vehicle model                | --model=quad                       |
| --console   | Enable MAVProxy console      | --console                          |
| --map       | Enable map display           | --map                              |

## Exercises

### Exercise 1: Simulate Wind Conditions

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --map --wind=15,270,2
# speed(m/s), direction(deg), turbulence(m/s)

# Calm
sim_vehicle.py --wind=0,0,0

# Strong gusty
sim_vehicle.py --wind=20,180,5

# Adjust at runtime
param set SIM_WIND_SPD 10
param set SIM_WIND_DIR 180
param set SIM_WIND_TURB 3
```

### Exercise 2: Inject Sensor Failures

```bash
cd ~/ardupilot/ArduCopter
sim_vehicle.py --console --map

param set SIM_GPS_DISABLE 1
param set SIM_GPS_GLITCH_X 100
param set SIM_GPS_GLITCH_Y 50
param set SIM_GPS_GLITCH_Z 20
param set SIM_MAG_ERROR 50
param set SIM_BARO_DRIFT 0.02
param set SIM_ACC1_FAIL 1
param set SIM_GYR1_FAIL 1
param set SIM_ARSPD_FAIL 1
```

```python
# gps_failure_test.py
from pymavlink import mavutil
import time

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()

master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
    0, 0, 0, 0, 0, 0, 0, 50)

time.sleep(30)

master.mav.param_set_send(
    master.target_system,
    master.target_component,
    b'SIM_GPS_DISABLE',
    1, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)

print("GPS disabled - observing failsafe behavior")
time.sleep(60)

master.mav.param_set_send(
    master.target_system,
    master.target_component,
    b'SIM_GPS_DISABLE',
    0, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)

print("GPS re-enabled")
```

### Exercise 3: Multi-Vehicle Simulation

```bash
# Terminal 1 (copter)
cd ~/ardupilot/ArduCopter
sim_vehicle.py -I0 --out=udp:127.0.0.1:14550 --console --map

# Terminal 2 (copter)
sim_vehicle.py -I1 --out=udp:127.0.0.1:14551 --console

# Terminal 3 (plane)
cd ~/ardupilot/ArduPlane
sim_vehicle.py -I2 --out=udp:127.0.0.1:14552 --console
```

```python
# multi_vehicle_control.py
from pymavlink import mavutil
import time

vehicles = [
    mavutil.mavlink_connection('udp:127.0.0.1:14550'),
    mavutil.mavlink_connection('udp:127.0.0.1:14551'),
    mavutil.mavlink_connection('udp:127.0.0.1:14552'),
]

for v in vehicles:
    v.wait_heartbeat()
    print(f"Connected to vehicle {v.target_system}")

for v in vehicles:
    v.mav.command_long_send(
        v.target_system, v.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, 1, 0, 0, 0, 0, 0, 0)
    time.sleep(1)

for i, v in enumerate(vehicles):
    v.mav.command_long_send(
        v.target_system, v.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0, 0, 0, 0, 0, 0, 0, 50 + (i * 10))  # Staggered altitudes
```

### Exercise 4: Custom Start Locations

```bash
# San Francisco
sim_vehicle.py --home=37.7749,-122.4194,10,0 --console --map

# Tokyo
sim_vehicle.py --home=35.6762,139.6503,40,90 --console --map

# High altitude
sim_vehicle.py --home=27.9881,86.9250,5364,0 --console --map

# Enable terrain following
param set TERRAIN_ENABLE 1
param set TERRAIN_FOLLOW 1
```

### Exercise 5: Log Replay for Debugging

```bash
param set LOG_BITMASK 2293759
param set LOG_REPLAY 1
param write

# After flight, replay
sim_vehicle.py --console --map --replay=logs/latest.BIN

# In MAVProxy during replay, test parameter changes
param set ATC_RAT_RLL_P 0.15
```

### Exercise 6: Control Simulation Speed

```bash
sim_vehicle.py --speedup=5 --console   # 5x real-time
sim_vehicle.py --speedup=0.5 --console # Slow motion

# Dynamic control in MAVProxy
set speedup 10
set speedup 1
set speedup 0.25
```

```python
# endurance_test.py
from pymavlink import mavutil
import time

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()

master.mav.param_set_send(
    master.target_system, master.target_component,
    b'SIM_SPEEDUP', 10, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)

print("Starting 2-hour endurance test at 10x speed")
```

### Exercise 7: Advanced Scenario Testing

```bash
# Engine failure with wind
sim_vehicle.py --wind=15,270,5 --console --map

mode LOITER
arm throttle
# Climb to altitude
param set SIM_ENGINE_FAIL 1
# Observe emergency landing behavior
```

```python
# battery_failure_test.py
from pymavlink import mavutil
import time

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()

master.mav.param_set_send(
    master.target_system, master.target_component,
    b'SIM_BATT_VOLTAGE',
    10.0, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)

print("Battery failsafe should trigger")
time.sleep(30)
```

## Common Issues

### SITL Won't Start

```bash
ps aux | grep sim_vehicle
pkill -f sim_vehicle

cd ~/ardupilot
./waf clean
./waf configure --board sitl
./waf plane

pip3 install pymavlink mavproxy
```

### Simulation Too Slow

```bash
set speedup 1
param set SIM_RATE_HZ 400
sim_vehicle.py --model=quad  # Lighter model
```

### Wind Simulation Not Working

```bash
param show SIM_WIND_SPD
param set SIM_WIND_SPD 15
param set SIM_WIND_DIR 180
param set SIM_WIND_TURB 3
```

### Multi-Vehicle Conflicts

```bash
sim_vehicle.py -I0 --log-dir=/tmp/vehicle0
sim_vehicle.py -I1 --log-dir=/tmp/vehicle1
param show SYSID_THISMAV  # Should be unique per vehicle
```

### Replay Issues

```bash
# Use correct vehicle type for the log
cd ~/ardupilot/ArduCopter
sim_vehicle.py --replay=logs/latest.BIN

param show LOG_REPLAY  # Must have been 1 when recording
```

## Automated Test Suite

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

        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0, 1, 0, 0, 0, 0, 0, 0)
        time.sleep(2)

        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0, 0, 0, 0, 0, 0, 0, 50)
        time.sleep(30)

        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_LAND,
            0, 0, 0, 0, 0, 0, 0, 0)
        time.sleep(30)

        print("Test: PASSED")

    def test_gps_failsafe(self):
        """Test GPS loss handling"""
        print("Test: GPS Failsafe")

        self.master.mav.param_set_send(
            self.master.target_system, self.master.target_component,
            b'SIM_GPS_DISABLE',
            1, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
        time.sleep(30)

        print("Test: PASSED")

tester = SITLTester('udp:127.0.0.1:14550')
tester.test_takeoff_land()
tester.test_gps_failsafe()
```

## Physics-Based Testing

```bash
param set SIM_WEIGHT_KG 25
param set SIM_CG_OFFSET_X 0.1
param set SIM_ENGINE_FAIL 1
param set SIM_ENGINE_MUL 0.5
param set SIM_SERVO_FAIL 1
```

---

- [SITL Advanced Guide](SITL_ADVANCED_GUIDE.md)
- [SITL Documentation](https://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html)
- [SITL Advanced Testing](https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html)
- [Gazebo SITL](https://ardupilot.org/dev/docs/sitl-with-gazebo.html)
