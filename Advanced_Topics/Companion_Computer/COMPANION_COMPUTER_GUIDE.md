# Companion Computer Integration Guide

## Serial Connection Setup

### Hardware Connection

**Pixhawk/Cube → Raspberry Pi:**
- TELEM2 port → Raspberry Pi UART
- TX → RX, RX → TX
- GND → GND
- 5V (optional, can power separately)

### ArduPilot Parameters

```bash
param set SERIAL2_PROTOCOL 2    # MAVLink 2
param set SERIAL2_BAUD 921      # 921600 baud
param set SR2_EXTRA1 10         # Stream rate (Hz)
param set SR2_EXTRA2 10
param set SR2_EXTRA3 2
param set SR2_POSITION 10
param set SR2_RAW_SENS 2
```

### Raspberry Pi Setup

**Enable UART:**
```bash
# Edit /boot/config.txt
sudo nano /boot/config.txt

# Add:
enable_uart=1
dtoverlay=disable-bt

# Reboot
sudo reboot
```

**Test connection:**
```bash
# Install MAVProxy
pip3 install pymavlink mavproxy

# Connect
mavproxy.py --master=/dev/serial0 --baudrate=921600
```

## ROS/MAVROS Integration

### Install MAVROS

```bash
# ROS Noetic (Ubuntu 20.04)
sudo apt install ros-noetic-mavros ros-noetic-mavros-extras

# Install GeographicLib
sudo /opt/ros/noetic/lib/mavros/install_geographiclib_datasets.sh
```

### Launch MAVROS

```bash
# Create launch file: mavros_apm.launch
roslaunch mavros apm.launch fcu_url:=/dev/serial0:921600
```

### Subscribe to Topics

**Python example:**
```python
#!/usr/bin/env python3
import rospy
from mavros_msgs.msg import State
from sensor_msgs.msg import NavSatFix

def state_callback(msg):
    print(f"Mode: {msg.mode}, Armed: {msg.armed}")

def gps_callback(msg):
    print(f"GPS: {msg.latitude}, {msg.longitude}")

rospy.init_node('mavros_listener')
rospy.Subscriber("/mavros/state", State, state_callback)
rospy.Subscriber("/mavros/global_position/global", NavSatFix, gps_callback)
rospy.spin()
```

## MAVSDK

### Install

```bash
pip3 install mavsdk
```

### Basic Example

```python
#!/usr/bin/env python3
import asyncio
from mavsdk import System

async def run():
    drone = System()
    await drone.connect(system_address="serial:///dev/serial0:921600")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone connected!")
            break

    # Get telemetry
    async for position in drone.telemetry.position():
        print(f"Altitude: {position.relative_altitude_m}m")
        break

asyncio.run(run())
```

## DroneKit-Python

### Install

```bash
pip3 install dronekit
```

### Example

```python
from dronekit import connect, VehicleMode

# Connect
vehicle = connect('/dev/serial0', baud=921600, wait_ready=True)

# Get parameters
print(f"Mode: {vehicle.mode.name}")
print(f"Armed: {vehicle.armed}")
print(f"GPS: {vehicle.location.global_frame}")

# Change mode
vehicle.mode = VehicleMode("GUIDED")
vehicle.armed = True

vehicle.close()
```

**Author:** Patrick Kelly (@Kuscko)
