# Sensor Drivers in ArduPilot

## Overview

ArduPilot's sensor driver architecture provides a modular, extensible framework for integrating GPS, barometers, compasses, IMUs, and other sensors with the flight controller [1]. Understanding this architecture is essential for debugging sensor issues, adding new sensor support, or optimizing sensor performance.

**Why Learn Sensor Drivers:**
- Troubleshoot sensor failures and configuration issues
- Add support for new sensor hardware
- Optimize sensor performance for specific applications
- Understand how ArduPilot processes sensor data
- Contribute sensor-related code improvements

## Prerequisites

Before starting this module, you should:

- Have completed ArduPilot build setup and understand C++ basics
- Be familiar with ArduPilot architecture and libraries
- Understand sensor types (GPS, IMU, barometer, compass)
- Know how to navigate the ArduPilot codebase
- Have experience running SITL for testing

## What You'll Learn

By completing this module, you will:

- Understand ArduPilot's sensor driver architecture
- Locate sensor driver code in the codebase
- Identify the front-end/back-end driver pattern
- Configure sensor parameters for different hardware
- Debug sensor initialization and runtime issues
- Test sensor drivers in SITL with simulated sensors
- Add support for new sensor types

## Key Concepts

### Sensor Driver Architecture

ArduPilot uses a consistent architecture across all sensor types [2]:

**Front-End (AP_Sensor):**
- Provides unified API for vehicle code
- Manages multiple sensor instances
- Handles sensor selection and failover
- Performs sensor fusion and filtering

**Back-End (AP_Sensor_Backend):**
- Implements hardware-specific communication
- Reads raw sensor data
- Converts to standard units
- Reports sensor health

**Example: GPS Architecture**
```
AP_GPS (front-end)
  ├── AP_GPS_UBLOX (u-blox back-end)
  ├── AP_GPS_NMEA (generic NMEA back-end)
  ├── AP_GPS_SBP (Swift Navigation back-end)
  └── AP_GPS_SIRF (SiRF back-end)
```

### Sensor Driver Locations

**Key Sensor Libraries** in `libraries/`:

| Sensor Type | Library | Description |
|-------------|---------|-------------|
| GPS | `AP_GPS/` | GPS receivers (u-blox, NMEA, etc.) |
| IMU | `AP_InertialSensor/` | Accelerometers and gyroscopes |
| Barometer | `AP_Baro/` | Pressure/altitude sensors |
| Compass | `AP_Compass/` | Magnetometers |
| Rangefinder | `AP_RangeFinder/` | Distance sensors (lidar, sonar) |
| Airspeed | `AP_Airspeed/` | Pitot tubes and airspeed sensors |
| Optical Flow | `AP_OpticalFlow/` | Optical flow sensors |
| Battery | `AP_BattMonitor/` | Battery monitors |

### Driver Initialization Flow

1. **Detection:** Front-end probes for available sensors
2. **Instantiation:** Creates back-end for detected hardware
3. **Configuration:** Applies parameters (orientation, offsets, etc.)
4. **Calibration:** Runs calibration if needed (compass, accel)
5. **Runtime:** Continuous data reading and health monitoring

### Sensor Parameters

Each sensor type has associated parameters [3]:

**GPS Parameters (GPS_*):**
- `GPS_TYPE` - GPS receiver type
- `GPS_AUTO_SWITCH` - Automatic GPS switching
- `GPS_BLEND_MASK` - GPS blending configuration

**Compass Parameters (COMPASS_*):**
- `COMPASS_TYPEMASK` - Enabled compass types
- `COMPASS_ORIENT` - Compass orientation
- `COMPASS_OFS_X/Y/Z` - Calibration offsets

**Barometer Parameters (BARO_*):**
- `BARO_PROBE_EXT` - External barometer detection
- `BARO_ALT_OFFSET` - Altitude offset

See **[SENSOR_DRIVER_GUIDE.md](SENSOR_DRIVER_GUIDE.md)** for complete parameter reference.

## Hands-On Practice

### Exercise 1: Explore GPS Driver Code

Navigate the GPS driver implementation:

```bash
cd ~/ardupilot/libraries/AP_GPS

# List GPS back-ends
ls -1 AP_GPS_*.cpp

# View front-end interface
less AP_GPS.h

# Examine u-blox back-end
less AP_GPS_UBLOX.cpp
```

**Key Methods to Find:**
- `detect()` - Hardware detection
- `read()` - Data reading from hardware
- `send_blob()` - Configuration commands
- `_parse_gps()` - Message parsing

### Exercise 2: Monitor Sensor Data in SITL

Start SITL and monitor sensor outputs:

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py
```

In MAVProxy console:

```bash
# GPS status
gps 0

# IMU status
ftp list @SYS/imu*.csv

# Barometer status
watch SCALED_PRESSURE

# Compass status
watch RAW_IMU
```

### Exercise 3: Configure Multiple GPS Instances

Simulate multiple GPS receivers:

```bash
# Enable dual GPS
param set GPS_TYPE 1     # Primary GPS
param set GPS_TYPE2 1    # Secondary GPS
param set GPS_AUTO_SWITCH 1  # Enable auto-switching

# Check GPS status
status gps
```

**Expected:** SITL reports two GPS instances, automatically selects best

### Exercise 4: Test Sensor Parameters

Experiment with sensor configuration:

```bash
# Load example sensor parameters
cd ~/Desktop/Work/AEVEX/Sensor_Drivers
param load sensor_params_example.param

# Check compass orientation
param show COMPASS_ORIENT

# Test barometer altitude offset
param set BARO_ALT_OFFSET 10.0  # 10m offset
```

### Exercise 5: Monitor Sensor Health

Use Python script to monitor sensor health:

```bash
cd ~/Desktop/Work/AEVEX/Sensor_Drivers
python3 sensor_test.py --connect tcp:127.0.0.1:5760
```

This script displays:
- GPS satellite count and fix type
- IMU health and vibration levels
- Barometer altitude and variance
- Compass health and interference levels

### Exercise 6: Trace Sensor Driver Execution

Add debug output to understand driver flow:

```bash
# Edit GPS driver to add debug prints
cd ~/ardupilot/libraries/AP_GPS
# Add: hal.console->printf("GPS: detected u-blox\n"); to detect()

# Rebuild
cd ~/ardupilot
./waf plane

# Run and observe debug output
cd ArduPlane
./arduplane --help
```

## Complete Guide

See **[SENSOR_DRIVER_GUIDE.md](SENSOR_DRIVER_GUIDE.md)** for comprehensive documentation including:

- Detailed driver architecture explanation
- Complete code walkthrough for each sensor type
- Adding new sensor support
- Sensor calibration procedures
- Hardware integration guidelines
- Debugging techniques

## Configuration Files

- **[sensor_params_example.param](sensor_params_example.param)** - Example sensor configuration
- **[sensor_test.py](sensor_test.py)** - Python sensor monitoring script

## Common Issues

### Issue: "No GPS detected"

**Symptom:** ArduPilot reports "No GPS" or GPS not initializing

**Solutions:**
1. Check `GPS_TYPE` parameter matches hardware
2. Verify serial port configuration (SERIAL3_PROTOCOL for GPS)
3. Check baud rate: `SERIAL3_BAUD` should match GPS (typically 38400 or 115200)
4. Verify physical connection (RX/TX not swapped)
5. Check GPS has power and antenna

**Debug in SITL:**
```bash
param set GPS_TYPE 1  # Auto-detect
param show SERIAL*    # Check serial config
```

### Issue: Compass inconsistent or unhealthy

**Symptom:** Pre-arm check fails: "Compass inconsistent"

**Solutions:**
1. Perform compass calibration in multiple orientations
2. Check for magnetic interference (move away from metal, power wires)
3. Verify compass orientation: `COMPASS_ORIENT`
4. Disable unhealthy compass instances
5. Consider external compass away from interference

**Calibration:**
```bash
# In MAVProxy
compassmot start
# Follow on-screen instructions
compassmot accept
```

### Issue: IMU errors or high vibration

**Symptom:** "IMU errors" or "High vibration" warnings

**Solutions:**
1. Check IMU health in logs (ClipCount < 1000 per minute)
2. Verify proper mounting (soft-mount flight controller)
3. Balance propellers and secure components
4. Check accelerometer calibration: `accelcal`
5. Review vibration levels in logs (< 30 m/s² acceptable)

### Issue: Barometer altitude drifting

**Symptom:** Altitude estimate drifts over time

**Solutions:**
1. Ensure barometer has temperature compensation
2. Protect barometer from direct airflow
3. Shield from light (some sensors light-sensitive)
4. Use altitude offset if needed: `BARO_ALT_OFFSET`
5. Check EKF fusion of GPS + barometer

### Issue: New sensor not detected

**Symptom:** Custom or new sensor hardware not recognized

**Solutions:**
1. Verify sensor type parameter configured
2. Check I2C/SPI bus configuration
3. Confirm sensor address (I2C) or CS pin (SPI)
4. Review driver probe/detect logic
5. Add debug output to driver initialization
6. Check hardware compatibility (voltage levels, timing)

See **[SENSOR_DRIVER_GUIDE.md](SENSOR_DRIVER_GUIDE.md)** for detailed troubleshooting.

## Sensor Testing Best Practices

**In SITL:**
- Test sensor failover (disable GPS, check behavior)
- Simulate sensor noise and interference
- Verify parameter changes take effect
- Test multiple sensor instances

**On Hardware:**
- Always calibrate sensors after installation
- Verify sensor orientation matches configuration
- Test in representative environment
- Monitor sensor health during test flights
- Review logs after flights for sensor issues

## Adding New Sensor Support

**Steps to add new sensor driver:**

1. **Create back-end class:**
   ```cpp
   class AP_GPS_NewType : public AP_GPS_Backend {
       // Implement detection, reading, parsing
   };
   ```

2. **Register in front-end:**
   - Add to `AP_GPS::detect()`
   - Add parameter for sensor type

3. **Implement required methods:**
   - `detect()` - Hardware detection
   - `read()` - Data reading
   - `handle_message()` - Message parsing

4. **Test thoroughly:**
   - SITL simulation
   - Hardware integration
   - Failover scenarios

See **[SENSOR_DRIVER_GUIDE.md](SENSOR_DRIVER_GUIDE.md)** for detailed implementation guide.

## Additional Resources

### Official ArduPilot Documentation

- **[Sensor Configuration](https://ardupilot.org/plane/docs/common-sensor-setup.html)** [1] - Sensor setup guide
- **[Developer: Sensor Drivers](https://ardupilot.org/dev/docs/learning-ardupilot-the-example-sketches.html)** [2] - Driver development
- **[GPS Configuration](https://ardupilot.org/plane/docs/common-gps-how-it-works.html)** [3] - GPS setup
- **[Compass Calibration](https://ardupilot.org/plane/docs/common-compass-calibration-in-mission-planner.html)** - Compass setup
- **[IMU Calibration](https://ardupilot.org/plane/docs/common-accelerometer-calibration.html)** - Accelerometer setup

### Code Navigation

- **[AP_GPS Library](https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_GPS)** - GPS driver code
- **[AP_InertialSensor Library](https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_InertialSensor)** - IMU drivers
- **[AP_Compass Library](https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_Compass)** - Compass drivers
- **[AP_Baro Library](https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_Baro)** - Barometer drivers

### Hardware Documentation

- **[Supported GPS Receivers](https://ardupilot.org/plane/docs/common-gps-selection.html)** - Compatible GPS hardware
- **[Supported IMUs](https://ardupilot.org/plane/docs/common-autopilots.html)** - Flight controller IMUs
- **[External Sensors](https://ardupilot.org/plane/docs/common-optional-hardware.html)** - Additional sensor options

### Community Resources

- [ArduPilot Discord: Hardware Channel](https://ardupilot.org/discord)
- [Discourse: Sensor Topics](https://discuss.ardupilot.org/c/hardware-discussion/15)
- [GitHub: Sensor Issues](https://github.com/ArduPilot/ardupilot/labels/Component-Sensors)

## Next Steps

After completing this sensor driver module:

1. **Analyze Flight Logs** - Learn to interpret sensor data in logs ([Flight Log Analysis](../Advanced_Topics/Flight_Log_Analysis/))
2. **EKF Deep Dive** - Understand how sensors feed EKF ([EKF Notes](../EKF_Notes/))
3. **Custom Hardware** - Integrate custom sensors ([Payload Integration](../Advanced_Topics/Payload_Integration/))
4. **Contribute Code** - Add support for new sensors ([Code Contribution](../Advanced_Topics/Code_Contribution_Workflow/))
5. **Performance Optimization** - Optimize sensor processing ([Performance Optimization](../Advanced_Topics/Performance_Optimization/))

---

**Sources:**

[1] https://ardupilot.org/plane/docs/common-sensor-setup.html
[2] https://ardupilot.org/dev/docs/learning-ardupilot-the-example-sketches.html
[3] https://ardupilot.org/plane/docs/common-gps-how-it-works.html
