# Hardware-in-the-Loop (HITL) Testing

HITL testing runs ArduPilot firmware on actual hardware while using simulated vehicle dynamics — bridging SITL and real flight.

## Key Concepts

### HITL vs SITL vs Real Flight

| Aspect     | SITL           | HITL                          | Real Flight          |
| ---------- | -------------- | ----------------------------- | -------------------- |
| Hardware   | None           | Flight controller             | Full system          |
| Sensors    | Simulated      | Real hardware or simulated    | Real sensors         |
| Dynamics   | Simulated      | Simulated                     | Real physics         |
| Safety     | Very safe      | Safe                          | Requires precautions |
| Cost       | Free           | Low                           | High                 |
| Iteration  | Very fast      | Fast                          | Slow                 |

### Architecture

```text
┌─────────────────────┐
│  Simulator          │
│  (JSBSim/X-Plane)   │
│  - Vehicle dynamics │
│  - Visual display   │
└──────────┬──────────┘
           │ MAVLink (sensor data, GPS)
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

### When to Use HITL vs SITL

Use **HITL** for: testing specific hardware, validating sensor drivers, checking real-time performance, preparing for first flights.

Use **SITL** for: rapid algorithm development, testing without hardware, automated CI/CD, learning ArduPilot basics.

## Exercises

### Exercise 1: Configure Flight Controller for HITL

```bash
cd ~/ardupilot
./waf configure --board Pixhawk1
./waf plane --enable-hitl
./waf plane --upload
```

```text
SERIAL0_PROTOCOL 2
SIM_ENABLED 1
param write
reboot
```

### Exercise 2: Start HITL Simulation

```bash
cd ~/ardupilot/ArduPlane

sim_vehicle.py --aircraft test --map --console \
    --out=udp:127.0.0.1:14550 \
    --serial0=/dev/ttyUSB0 --serial0-baud=115200
```

Terminal 1 — Start JSBSim:

```bash
cd ~/ardupilot/Tools/autotest
./jsbsim/jsbsim --nice --suspend --script=jsbsim/fgout.xml
```

Terminal 2 — Connect MAVProxy:

```bash
mavproxy.py --master=/dev/ttyUSB0 --master=tcp:127.0.0.1:5760 \
    --sitl=127.0.0.1:5501 --out=127.0.0.1:14550
```

### Exercise 3: Test Basic Flight

```bash
mode MANUAL
arm throttle
mode FBWA
mode AUTO
disarm
```

### Exercise 4: Test Sensor Configuration

```bash
status
# Shows: GPS, IMU, compass, barometer status

# In MANUAL mode, physically rotate flight controller
# Watch compass heading change
```

### Exercise 5: Test Failsafes

```bash
# Simulate GPS loss
param set SIM_GPS_DISABLE 1

# Simulate low battery
param set SIM_BATT_VOLTAGE 10.5

# Verify failsafes trigger correctly
```

## HITL Configurations

### Basic HITL (Simulated Sensors)

```text
SIM_ENABLED 1
SERIAL0_PROTOCOL 2
SERIAL0_BAUD 115200
```

### Hybrid HITL (Real IMU + Simulated GPS)

```text
SIM_ENABLED 1
AHRS_EKF_TYPE 3
EK3_SRC1_POSXY 3
EK3_SRC1_VELXY 3
EK3_SRC1_POSZ 1
```

## Common Issues

### Flight Controller Not Detected

```bash
ls -l /dev/ttyUSB* /dev/ttyACM*
sudo usermod -a -G dialout $USER
```

### No Sensor Data in Simulation

```bash
param show SIM_ENABLED  # Should be 1
sim_vehicle.py -v --debug
```

### Timing Issues

- Close unnecessary programs
- Add `--speedup=1` to sim_vehicle.py
- Use high-quality USB cable
- Reduce `LOG_BITMASK`

### Simulator and Hardware Mismatch

```bash
param show FRAME_CLASS
param show FRAME_TYPE
param reset_nodefaults
param write
reboot
```

---

- [HITL Testing Guide](HITL_TESTING_GUIDE.md)
- [ArduPilot HITL](https://ardupilot.org/dev/docs/hitl.html)
- [JSBSim](https://jsbsim.sourceforge.net/)
