# Sensor Drivers in ArduPilot

## Overview

ArduPilot uses a front-end/back-end driver architecture for GPS, IMUs, barometers, compasses, and other sensors. Understanding it is essential for debugging sensor issues, adding new hardware, or reading sensor code.

## Prerequisites

- ArduPilot build setup, basic C++ knowledge
- Familiar with ArduPilot libraries and SITL

## Key Concepts

### Sensor Driver Architecture

**Front-End (AP_Sensor):** Unified API for vehicle code, manages multiple instances, handles failover and filtering.

**Back-End (AP_Sensor_Backend):** Hardware-specific communication, raw data reading, unit conversion, health reporting.

**Example: GPS Architecture**
```
AP_GPS (front-end)
  ├── AP_GPS_UBLOX (u-blox back-end)
  ├── AP_GPS_NMEA (generic NMEA back-end)
  ├── AP_GPS_SBP (Swift Navigation back-end)
  └── AP_GPS_SIRF (SiRF back-end)
```

### Sensor Driver Locations

| Sensor Type | Library | Description |
|-------------|---------|-------------|
| GPS | `AP_GPS/` | GPS receivers |
| IMU | `AP_InertialSensor/` | Accelerometers and gyroscopes |
| Barometer | `AP_Baro/` | Pressure/altitude sensors |
| Compass | `AP_Compass/` | Magnetometers |
| Rangefinder | `AP_RangeFinder/` | Lidar, sonar |
| Airspeed | `AP_Airspeed/` | Pitot tubes |
| Optical Flow | `AP_OpticalFlow/` | Optical flow sensors |
| Battery | `AP_BattMonitor/` | Battery monitors |

### Driver Initialization Flow

1. **Detection** — Front-end probes for available sensors
2. **Instantiation** — Creates back-end for detected hardware
3. **Configuration** — Applies parameters (orientation, offsets)
4. **Calibration** — Compass, accelerometer calibration
5. **Runtime** — Continuous data reading and health monitoring

### Sensor Parameters

**GPS:** `GPS_TYPE`, `GPS_AUTO_SWITCH`, `GPS_BLEND_MASK`

**Compass:** `COMPASS_TYPEMASK`, `COMPASS_ORIENT`, `COMPASS_OFS_X/Y/Z`

**Barometer:** `BARO_PROBE_EXT`, `BARO_ALT_OFFSET`

See **[SENSOR_DRIVER_GUIDE.md](SENSOR_DRIVER_GUIDE.md)** for complete parameter reference.

## Hands-On Practice

### Exercise 1: Explore GPS Driver Code

```bash
cd ~/ardupilot/libraries/AP_GPS
ls -1 AP_GPS_*.cpp
less AP_GPS.h
less AP_GPS_UBLOX.cpp
```

Key methods: `detect()`, `read()`, `send_blob()`, `_parse_gps()`

### Exercise 2: Monitor Sensor Data in SITL

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py
```

In MAVProxy:

```bash
gps 0
watch SCALED_PRESSURE
watch RAW_IMU
```

### Exercise 3: Configure Multiple GPS Instances

```bash
param set GPS_TYPE 1
param set GPS_TYPE2 1
param set GPS_AUTO_SWITCH 1
status gps
```

### Exercise 4: Test Sensor Parameters

```bash
cd ~/Desktop/Work/AEVEX/Sensor_Drivers
param load sensor_params_example.param
param show COMPASS_ORIENT
param set BARO_ALT_OFFSET 10.0
```

### Exercise 5: Monitor Sensor Health

```bash
cd ~/Desktop/Work/AEVEX/Sensor_Drivers
python3 sensor_test.py --connect tcp:127.0.0.1:5760
```

Displays GPS satellite count/fix, IMU health/vibration, barometer altitude/variance, compass health.

### Exercise 6: Trace Sensor Driver Execution

```bash
cd ~/ardupilot/libraries/AP_GPS
# Add: hal.console->printf("GPS: detected u-blox\n"); to detect()

cd ~/ardupilot
./waf plane
```

## Complete Guide

See **[SENSOR_DRIVER_GUIDE.md](SENSOR_DRIVER_GUIDE.md)** for full architecture, code walkthroughs, adding new sensors, calibration, and debugging.

## Configuration Files

- **[sensor_params_example.param](sensor_params_example.param)** - Example sensor configuration
- **[sensor_test.py](sensor_test.py)** - Python sensor monitoring script

## Common Issues

### "No GPS detected"

1. Set `GPS_TYPE = 1` (auto-detect)
2. Verify `SERIAL3_PROTOCOL` for GPS port
3. Check baud rate (`SERIAL3_BAUD`)
4. Verify RX/TX not swapped and GPS has power

```bash
param set GPS_TYPE 1
param show SERIAL*
```

### Compass inconsistent

1. Calibrate in multiple orientations
2. Move away from magnetic interference
3. Check `COMPASS_ORIENT`
4. Disable unhealthy instances or use external compass

```bash
compassmot start
compassmot accept
```

### IMU errors or high vibration

1. Check ClipCount in logs (< 1000/min)
2. Soft-mount flight controller
3. Balance propellers, secure components
4. Run `accelcal`, review vibration in logs (< 30 m/s²)

### Barometer altitude drifting

1. Ensure temperature compensation
2. Protect from direct airflow and light
3. Use `BARO_ALT_OFFSET` if needed
4. Check EKF GPS + barometer fusion

### New sensor not detected

1. Verify sensor type parameter
2. Check I2C/SPI bus and address/CS pin
3. Review driver probe/detect logic
4. Add debug output to initialization

## Adding New Sensor Support

```cpp
class AP_GPS_NewType : public AP_GPS_Backend {
    // Implement detection, reading, parsing
};
```

1. Register in `AP_GPS::detect()`
2. Add parameter for sensor type
3. Implement `detect()`, `read()`, `handle_message()`
4. Test in SITL and on hardware

See **[SENSOR_DRIVER_GUIDE.md](SENSOR_DRIVER_GUIDE.md)** for detailed implementation guide.

## Additional Resources

- [Sensor Configuration](https://ardupilot.org/plane/docs/common-sensor-setup.html)
- [Developer: Sensor Drivers](https://ardupilot.org/dev/docs/learning-ardupilot-the-example-sketches.html)
- [GPS Configuration](https://ardupilot.org/plane/docs/common-gps-how-it-works.html)
- [Compass Calibration](https://ardupilot.org/plane/docs/common-compass-calibration-in-mission-planner.html)
- [IMU Calibration](https://ardupilot.org/plane/docs/common-accelerometer-calibration.html)
- [AP_GPS Library](https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_GPS)
- [AP_InertialSensor Library](https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_InertialSensor)

## Next Steps

1. Analyze flight logs — [Flight Log Analysis](../Advanced_Topics/Flight_Log_Analysis/)
2. EKF deep dive — [EKF Notes](../EKF_Notes/)
3. Custom hardware integration — [Payload Integration](../Advanced_Topics/Payload_Integration/)

---

**Sources:**

[1] https://ardupilot.org/plane/docs/common-sensor-setup.html
[2] https://ardupilot.org/dev/docs/learning-ardupilot-the-example-sketches.html
[3] https://ardupilot.org/plane/docs/common-gps-how-it-works.html
