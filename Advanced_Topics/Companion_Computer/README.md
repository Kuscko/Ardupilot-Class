# Companion Computer Integration

## Overview

Learn to integrate companion computers (Raspberry Pi, NVIDIA Jetson, Intel NUC) with ArduPilot flight controllers to enable advanced capabilities like computer vision, autonomous navigation, mission planning, and custom control algorithms [1].

Companion computers communicate with the flight controller via MAVLink over serial or network connections, allowing high-level processing while the flight controller handles low-level stabilization and control.

## Prerequisites

Before starting this module, you should have:

- ArduPilot flight controller (SITL or hardware)
- Basic understanding of MAVLink protocol
- Linux command line experience
- Python or C++ programming knowledge
- Familiarity with serial communication concepts
- (Optional) Raspberry Pi 4 or similar single-board computer

## What You'll Learn

By completing this module, you will:

- Configure serial connections between companion computer and flight controller
- Set up MAVLink communication over UART, USB, or network
- Use MAVROS to integrate with ROS/ROS2
- Develop applications using MAVSDK and DroneKit-Python
- Implement offboard control modes
- Troubleshoot common connection issues
- Understand data rates and bandwidth considerations

## Key Concepts

### Companion Computer Architecture

```
┌─────────────────────────┐
│  Companion Computer     │
│  (High-level Processing)│
│  - Computer Vision      │
│  - Path Planning        │
│  - Mission Control      │
└───────────┬─────────────┘
            │ MAVLink
            │ (Serial/Network)
┌───────────▼─────────────┐
│  Flight Controller      │
│  (Low-level Control)    │
│  - Stabilization        │
│  - Motor Control        │
│  - Sensor Fusion        │
└─────────────────────────┘
```

### MAVLink Serial Connection

ArduPilot uses SERIAL ports for companion computer communication [2]:

- **SERIAL2** (TELEM2): Most common for companion computers
- **Protocol:** Set to MAVLink2 (protocol 2)
- **Baud Rate:** Typically 921600 for high-bandwidth
- **Flow Control:** Optional RTS/CTS for reliable communication

### Communication Frameworks

Three main options for companion computer development [3]:

1. **MAVROS** - ROS/ROS2 interface (robotics applications)
2. **MAVSDK** - Modern C++/Python SDK (clean API)
3. **DroneKit-Python** - Simple Python scripting (mission automation)

## Hands-On Practice

### Exercise 1: Configure Serial Port (SITL)

Configure ArduPilot to communicate with companion computer:

```bash
# Start SITL with additional MAVLink output
cd ~/ardupilot/ArduPlane
sim_vehicle.py --out=udp:127.0.0.1:14550

# In MAVProxy console, configure SERIAL2 for companion computer
param set SERIAL2_PROTOCOL 2    # MAVLink2
param set SERIAL2_BAUD 921600   # Baud rate
param write
reboot
```

**Expected Result:** SERIAL2 configured for MAVLink communication at 921600 baud.

### Exercise 2: Test Connection with MAVProxy

Verify MAVLink communication:

```bash
# Connect MAVProxy to the companion port
mavproxy.py --master=udp:127.0.0.1:14550

# You should see:
# - Heartbeat messages
# - System status
# - GPS data
# - Attitude information
```

### Exercise 3: DroneKit-Python Basic Script

Create a simple monitoring script:

```python
# companion_monitor.py
from dronekit import connect, VehicleMode
import time

# Connect to vehicle
vehicle = connect('udp:127.0.0.1:14550', wait_ready=True)

print(f"Connected to: {vehicle.version}")
print(f"Mode: {vehicle.mode.name}")
print(f"Armed: {vehicle.armed}")
print(f"GPS: {vehicle.gps_0}")
print(f"Battery: {vehicle.battery.voltage}V")

# Monitor altitude for 30 seconds
for i in range(30):
    print(f"Altitude: {vehicle.location.global_relative_frame.alt:.2f}m")
    time.sleep(1)

vehicle.close()
```

**Run Script:**
```bash
python3 companion_monitor.py
```

**Expected Output:** Real-time vehicle telemetry data.

### Exercise 4: MAVSDK Example

Install and test MAVSDK:

```bash
# Install MAVSDK-Python
pip3 install mavsdk

# Create test script
cat > mavsdk_test.py << 'EOF'
import asyncio
from mavsdk import System

async def run():
    drone = System()
    await drone.connect(system_address="udp://:14550")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone connected!")
            break

    # Get telemetry
    async for position in drone.telemetry.position():
        print(f"Altitude: {position.relative_altitude_m:.2f}m")
        break

    async for battery in drone.telemetry.battery():
        print(f"Battery: {battery.voltage_v:.2f}V")
        break

asyncio.run(run())
EOF

python3 mavsdk_test.py
```

### Exercise 5: Offboard Control Mode

Send position setpoints from companion computer:

```python
# offboard_control.py
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time

vehicle = connect('udp:127.0.0.1:14550', wait_ready=True)

# Arm and takeoff
print("Arming...")
vehicle.mode = VehicleMode("GUIDED")
vehicle.armed = True

while not vehicle.armed:
    time.sleep(1)

print("Taking off to 10m...")
vehicle.simple_takeoff(10)

# Wait to reach target altitude
while vehicle.location.global_relative_frame.alt < 9.5:
    print(f"Altitude: {vehicle.location.global_relative_frame.alt:.1f}m")
    time.sleep(1)

print("Reached target altitude")

# Send position command
target = LocationGlobalRelative(
    vehicle.location.global_frame.lat + 0.0001,
    vehicle.location.global_frame.lon + 0.0001,
    10
)
vehicle.simple_goto(target)

time.sleep(20)

# Return to launch
vehicle.mode = VehicleMode("RTL")
vehicle.close()
```

**Safety Note:** Test in SITL first. Always include failsafes in real flights.

## Hardware Setup

### Raspberry Pi to Pixhawk Connection

**Physical Connection:**

1. **TX (RPi GPIO 14)** → **RX (Pixhawk TELEM2)**
2. **RX (RPi GPIO 15)** → **TX (Pixhawk TELEM2)**
3. **GND (RPi)** → **GND (Pixhawk)**
4. **5V** - Use separate power supplies (do NOT power RPi from Pixhawk)

**RPi Serial Configuration:**

```bash
# Disable serial console, enable UART
sudo raspi-config
# Interface Options → Serial Port
# - Login shell over serial: NO
# - Serial port hardware: YES

# Edit /boot/config.txt
sudo nano /boot/config.txt
# Add: enable_uart=1
# Add: dtoverlay=disable-bt  # If using UART0

sudo reboot

# Test serial port
ls -l /dev/serial0
# Should show: /dev/serial0 -> ttyAMA0
```

**Connect DroneKit:**
```python
vehicle = connect('/dev/serial0', baud=921600, wait_ready=True)
```

## Common Issues

### Issue: No MAVLink Connection

**Symptoms:** DroneKit/MAVSDK cannot connect, timeout errors

**Solutions:**

1. **Verify SERIAL parameters:**
   ```bash
   param show SERIAL2_*
   # SERIAL2_PROTOCOL should be 2 (MAVLink2)
   # SERIAL2_BAUD should match your connection
   ```

2. **Check physical connection:**
   - TX→RX and RX→TX (crossed)
   - Common ground
   - Correct voltage levels (3.3V logic)

3. **Test with MAVProxy first:**
   ```bash
   # Hardware
   mavproxy.py --master=/dev/serial0 --baudrate=921600

   # SITL
   mavproxy.py --master=udp:127.0.0.1:14550
   ```

### Issue: Slow or Dropped Data

**Symptoms:** Telemetry updates slowly, gaps in data

**Solutions:**

- Increase baud rate: `param set SERIAL2_BAUD 921600`
- Reduce message rates: `param set SR2_POSITION 5` (reduce to 5Hz)
- Enable flow control if available
- Check for serial buffer overruns in logs

### Issue: Permission Denied on Serial Port

**Symptoms:** `Permission denied: '/dev/ttyUSB0'`

**Solution:**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Log out and back in, or:
newgrp dialout

# Verify
groups
```

## Configuration Parameters

Key parameters for companion computer setup [2]:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| SERIAL2_PROTOCOL | 2 | MAVLink2 protocol |
| SERIAL2_BAUD | 921600 | High-speed communication |
| SR2_POSITION | 10 | Position updates at 10Hz |
| SR2_EXTRA1 | 10 | Attitude data at 10Hz |
| SR2_RAW_SENS | 2 | Raw sensor data at 2Hz |

## Additional Resources

- [ArduPilot Companion Computers](https://ardupilot.org/dev/docs/companion-computers.html) [1] - Official guide
- [MAVLink Common Messages](https://mavlink.io/en/messages/common.html) [2] - Protocol reference
- [DroneKit-Python Documentation](https://dronekit-python.readthedocs.io/) [3] - DroneKit API
- [MAVSDK Documentation](https://mavsdk.mavlink.io/) [4] - MAVSDK guides
- [MAVROS Documentation](http://wiki.ros.org/mavros) [5] - ROS integration

### Example Projects

- [Precision Landing](https://ardupilot.org/dev/docs/precision-landing-with-irlock.html) - Vision-based landing
- [Object Avoidance](https://ardupilot.org/copter/docs/common-object-avoidance-landing-page.html) - Obstacle detection
- [Indoor Navigation](https://ardupilot.org/copter/docs/common-vio-tracking-camera.html) - VIO systems

## Next Steps

After mastering companion computer integration:

1. **Custom MAVLink Messages** - Create custom telemetry for your application
2. **Computer Vision** - Integrate OpenCV for visual processing
3. **Payload Integration** - Control cameras and sensors from companion
4. **Advanced Navigation** - Implement custom path planning algorithms

---

**Sources:**

[1] https://ardupilot.org/dev/docs/companion-computers.html
[2] https://ardupilot.org/copter/docs/parameters.html#serial-parameters
[3] https://dronekit-python.readthedocs.io/
[4] https://mavsdk.mavlink.io/
[5] http://wiki.ros.org/mavros
