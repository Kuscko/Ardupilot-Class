# Companion Computer Integration

Companion computers (Raspberry Pi, NVIDIA Jetson, Intel NUC) connect to ArduPilot via MAVLink over serial or network, enabling computer vision, custom navigation, and mission control while the flight controller handles stabilization.

## Key Concepts

### Architecture

```text
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

- **SERIAL2** (TELEM2): Most common port for companion computers
- **Protocol:** MAVLink2 (protocol 2)
- **Baud Rate:** 921600 for high-bandwidth
- **Flow Control:** Optional RTS/CTS

### Communication Frameworks

1. **MAVROS** - ROS/ROS2 interface (robotics applications)
2. **MAVSDK** - Modern C++/Python SDK (clean API)
3. **DroneKit-Python** - Simple Python scripting (mission automation)

## Configuration Parameters

| Parameter         | Value  | Purpose                       |
| ----------------- | ------ | ----------------------------- |
| SERIAL2_PROTOCOL  | 2      | MAVLink2 protocol             |
| SERIAL2_BAUD      | 921600 | High-speed communication      |
| SR2_POSITION      | 10     | Position updates at 10Hz      |
| SR2_EXTRA1        | 10     | Attitude data at 10Hz         |
| SR2_RAW_SENS      | 2      | Raw sensor data at 2Hz        |

## Exercises

### Exercise 1: Configure Serial Port (SITL)

```bash
# Start SITL with additional MAVLink output
cd ~/ardupilot/ArduPlane
sim_vehicle.py --out=udp:127.0.0.1:14550

# Configure SERIAL2 for companion computer
param set SERIAL2_PROTOCOL 2    # MAVLink2
param set SERIAL2_BAUD 921600
param write
reboot
```

### Exercise 2: Test Connection with MAVProxy

```bash
mavproxy.py --master=udp:127.0.0.1:14550
```

### Exercise 3: DroneKit-Python Basic Script

```python
# companion_monitor.py
from dronekit import connect, VehicleMode
import time

vehicle = connect('udp:127.0.0.1:14550', wait_ready=True)

print(f"Connected to: {vehicle.version}")
print(f"Mode: {vehicle.mode.name}")
print(f"Armed: {vehicle.armed}")
print(f"Battery: {vehicle.battery.voltage}V")

for i in range(30):
    print(f"Altitude: {vehicle.location.global_relative_frame.alt:.2f}m")
    time.sleep(1)

vehicle.close()
```

```bash
python3 companion_monitor.py
```

### Exercise 4: MAVSDK Example

```bash
pip3 install mavsdk

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

```python
# offboard_control.py
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time

vehicle = connect('udp:127.0.0.1:14550', wait_ready=True)

vehicle.mode = VehicleMode("GUIDED")
vehicle.armed = True

while not vehicle.armed:
    time.sleep(1)

vehicle.simple_takeoff(10)

while vehicle.location.global_relative_frame.alt < 9.5:
    print(f"Altitude: {vehicle.location.global_relative_frame.alt:.1f}m")
    time.sleep(1)

target = LocationGlobalRelative(
    vehicle.location.global_frame.lat + 0.0001,
    vehicle.location.global_frame.lon + 0.0001,
    10
)
vehicle.simple_goto(target)

time.sleep(20)

vehicle.mode = VehicleMode("RTL")
vehicle.close()
```

## Hardware Setup (Raspberry Pi to Pixhawk)

**Physical Connection:**

1. TX (RPi GPIO 14) → RX (Pixhawk TELEM2)
2. RX (RPi GPIO 15) → TX (Pixhawk TELEM2)
3. GND (RPi) → GND (Pixhawk)
4. Power RPi separately — do NOT power from Pixhawk

**RPi Serial Configuration:**

```bash
sudo raspi-config
# Interface Options → Serial Port
# - Login shell over serial: NO
# - Serial port hardware: YES

sudo nano /boot/config.txt
# Add: enable_uart=1
# Add: dtoverlay=disable-bt

sudo reboot
ls -l /dev/serial0
# Should show: /dev/serial0 -> ttyAMA0
```

## Common Issues

### No MAVLink Connection

```bash
param show SERIAL2_*
# SERIAL2_PROTOCOL should be 2
# SERIAL2_BAUD should match your connection

# Test with MAVProxy first
mavproxy.py --master=/dev/serial0 --baudrate=921600
mavproxy.py --master=udp:127.0.0.1:14550
```

### Slow or Dropped Data

- Increase baud rate: `param set SERIAL2_BAUD 921600`
- Reduce message rates: `param set SR2_POSITION 5`

### Permission Denied on Serial Port

```bash
sudo usermod -a -G dialout $USER
newgrp dialout
```

---

- [ArduPilot Companion Computers](https://ardupilot.org/dev/docs/companion-computers.html)
- [DroneKit-Python Documentation](https://dronekit-python.readthedocs.io/)
- [MAVSDK Documentation](https://mavsdk.mavlink.io/)
- [MAVROS Documentation](http://wiki.ros.org/mavros)
