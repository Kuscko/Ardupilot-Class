# ArduPilot Sensor Driver Architecture

## Overview

ArduPilot supports dozens of different sensors from various manufacturers. To maintain code flexibility and reduce complexity, ArduPilot uses a **front-end/back-end architecture** for sensor drivers.

**Target Version:** Plane 4.5.7

---

## Front-End / Back-End Pattern

### The Problem

Different hardware requires different code, but vehicle code shouldn't need to know which specific sensor is connected.

**Example:** There are 20+ different GPS modules. Should `ArduPlane` have 20 different code paths for each GPS?

**Solution:** Split sensor drivers into two layers.

---

### Architecture

```
┌─────────────────────────────────────┐
│  Vehicle Code (ArduPlane, etc.)     │
│  "Give me current GPS position"     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     Front-End (AP_GPS)              │  ← Unified API
│  - Public interface                 │
│  - Common functionality             │
│  - Manages multiple back-ends       │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┬───────────┐
       ▼               ▼           ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│ uBlox    │   │ Trimble  │   │ NMEA     │  ← Hardware-specific
│ Backend  │   │ Backend  │   │ Backend  │
└──────────┘   └──────────┘   └──────────┘
```

### Front-End Responsibilities

- **Public API** for vehicle code
- **Sensor instance management** (supports multiple sensors)
- **Common calculations** (e.g., converting to standard units)
- **Data validation**
- **Sensor health monitoring**

### Back-End Responsibilities

- **Hardware-specific communication** (I2C, SPI, UART protocols)
- **Parse sensor data format**
- **Send configuration commands**
- **Handle sensor quirks**

### Benefits

| Benefit | Description |
|---------|-------------|
| **Modularity** | Add new sensors without modifying vehicle code |
| **Multiple instances** | Support multiple GPS, compasses, etc. simultaneously |
| **Code reuse** | Common logic stays in front-end |
| **Easier testing** | Mock back-ends for SITL |

---

## Key Sensor Driver Libraries

All sensor libraries are in `~/ardupilot/libraries/`

### GPS Drivers (`AP_GPS`)

**Location:** `libraries/AP_GPS/`

**Supported GPS:**
- uBlox (most common)
- Trimble
- Emlid Reach
- NMEA (generic)
- MAVLink GPS
- SITL (simulated)

**Key Files:**
| File | Purpose |
|------|---------|
| `AP_GPS.h` | Front-end API |
| `AP_GPS.cpp` | Front-end implementation |
| `AP_GPS_UBLOX.cpp` | uBlox backend |
| `GPS_Backend.h` | Base class for backends |

**Interface Example:**
```cpp
// Vehicle code
const Location& current_location = gps.location();  // Front-end call
uint8_t num_sats = gps.num_sats();
float hdop = gps.get_hdop();
```

**Parameters:**
- `GPS_TYPE` - GPS type (1=AUTO, 2=uBlox, etc.)
- `GPS_AUTO_CONFIG` - Auto-configure GPS
- `GPS_GNSS_MODE` - GPS+GLONASS+Galileo etc.

---

### IMU Drivers (`AP_InertialSensor`)

**Location:** `libraries/AP_InertialSensor/`

**Supported IMUs:**
- Invensense MPU6000/9000
- Invensense ICM-20602/20689/42688
- ST LSM6DS33
- SITL (simulated)

**Key Files:**
| File | Purpose |
|------|---------|
| `AP_InertialSensor.h` | Front-end API |
| `AP_InertialSensor.cpp` | Front-end, sensor fusion |
| `AP_InertialSensor_Invensense.cpp` | Invensense backend |
| `AP_InertialSensor_Backend.h` | Backend base class |

**What it provides:**
- Accelerometer data (m/s²)
- Gyroscope data (rad/s)
- Temperature
- Multi-IMU averaging/failover

**Parameters:**
- `INS_GYRO_FILTER` - Gyro low-pass filter frequency
- `INS_ACCEL_FILTER` - Accel low-pass filter frequency
- `INS_USE` - Which IMUs to use (bitmask)

---

### Barometer Drivers (`AP_Baro`)

**Location:** `libraries/AP_Baro/`

**Supported Barometers:**
- MS5611 (common)
- BMP280/388
- LPS25H
- SITL (simulated)

**Key Files:**
| File | Purpose |
|------|---------|
| `AP_Baro.h` | Front-end API |
| `AP_Baro_MS56XX.cpp` | MS5611/MS5607 backend |
| `AP_Baro_BMP280.cpp` | BMP280 backend |

**What it provides:**
- Atmospheric pressure (Pa)
- Altitude estimate (m)
- Temperature

**Parameters:**
- `BARO_PROBE_EXT` - Probe for external barometers
- `BARO_ALT_OFFSET` - Altitude offset

---

### Compass Drivers (`AP_Compass`)

**Location:** `libraries/AP_Compass/`

**Supported Compasses:**
- HMC5843/5883
- AK8963/AK09916
- LSM303D
- IST8310
- Built-in (in GPS modules)
- SITL (simulated)

**Key Files:**
| File | Purpose |
|------|---------|
| `AP_Compass.h` | Front-end API |
| `AP_Compass_HMC5843.cpp` | HMC5843 backend |
| `AP_Compass_AK8963.cpp` | AK8963 backend |

**What it provides:**
- Magnetic field vector (mGauss)
- Heading (degrees)
- Calibration interface

**Parameters:**
- `COMPASS_ENABLE` - Enable compass
- `COMPASS_AUTODEC` - Auto-declination
- `COMPASS_OFS_X/Y/Z` - Compass offsets (calibration)

---

### Airspeed Sensor (`AP_Airspeed`)

**Location:** `libraries/AP_Airspeed/`

**Supported Sensors:**
- MS4525DO (most common)
- SDP3X
- Analog
- SITL (simulated)

**Key Files:**
| File | Purpose |
|------|---------|
| `AP_Airspeed.h` | Front-end API |
| `AP_Airspeed_MS4525.cpp` | MS4525 backend |

**What it provides:**
- Differential pressure (Pa)
- Airspeed (m/s)

**Parameters:**
- `ARSPD_TYPE` - Airspeed sensor type
- `ARSPD_USE` - Enable airspeed sensor
- `ARSPD_RATIO` - Calibration ratio

---

### Rangefinder (`AP_RangeFinder`)

**Location:** `libraries/AP_RangeFinder/`

**Supported Sensors:**
- Lightware (lidar)
- Benewake TFmini
- LeddarOne
- MaxBotix sonar
- PWM-based rangefinders

**Key Files:**
| File | Purpose |
|------|---------|
| `AP_RangeFinder.h` | Front-end API |
| `AP_RangeFinder_Backend.h` | Backend base |
| `AP_RangeFinder_Benewake_TFMini.cpp` | TFmini backend |

**What it provides:**
- Distance to ground (cm)
- Obstacle detection

**Parameters:**
- `RNGFND1_TYPE` - Rangefinder type
- `RNGFND1_MIN_CM` - Minimum reliable distance
- `RNGFND1_MAX_CM` - Maximum distance

---

### Battery Monitor (`AP_BattMonitor`)

**Location:** `libraries/AP_BattMonitor/`

**Supported Monitors:**
- Analog voltage/current
- SMBus (smart battery)
- BLHeli ESC telemetry
- Generator
- SITL

**What it provides:**
- Voltage (V)
- Current (A)
- Consumed capacity (mAh)
- Remaining capacity (%)

**Parameters:**
- `BATT_MONITOR` - Battery monitor type
- `BATT_VOLT_PIN` - Voltage sensor pin
- `BATT_CURR_PIN` - Current sensor pin
- `BATT_CAPACITY` - Battery capacity (mAh)

---

## Sensor Driver Code Locations

### Directory Structure

```
~/ardupilot/libraries/
├── AP_GPS/                    # GPS drivers
│   ├── AP_GPS.h
│   ├── AP_GPS.cpp
│   ├── AP_GPS_UBLOX.cpp
│   └── GPS_Backend.h
├── AP_InertialSensor/         # IMU (accel + gyro)
│   ├── AP_InertialSensor.h
│   ├── AP_InertialSensor.cpp
│   ├── AP_InertialSensor_Invensense.cpp
│   └── AP_InertialSensor_Backend.h
├── AP_Baro/                   # Barometer
│   ├── AP_Baro.h
│   ├── AP_Baro_MS56XX.cpp
│   └── AP_Baro_BMP280.cpp
├── AP_Compass/                # Compass/Magnetometer
│   ├── AP_Compass.h
│   ├── AP_Compass_HMC5843.cpp
│   └── AP_Compass_AK8963.cpp
├── AP_Airspeed/               # Airspeed sensor
│   ├── AP_Airspeed.h
│   └── AP_Airspeed_MS4525.cpp
├── AP_RangeFinder/            # Rangefinder/Lidar
│   ├── AP_RangeFinder.h
│   └── AP_RangeFinder_Backend.h
├── AP_BattMonitor/            # Battery monitor
│   ├── AP_BattMonitor.h
│   └── AP_BattMonitor_Analog.cpp
└── AP_OpticalFlow/            # Optical flow sensors
    ├── AP_OpticalFlow.h
    └── AP_OpticalFlow_Pixart.cpp
```

---

## Adding a New Sensor

### Example: Adding a New GPS

**Steps:**

1. **Create backend class** (e.g., `AP_GPS_MyGPS.cpp`)
   - Inherit from `AP_GPS_Backend`
   - Implement `read()` method

2. **Register backend** in `AP_GPS.cpp`
   - Add to detection list

3. **Add parameter enum** in `AP_GPS.h`
   - Add new GPS_TYPE value

4. **Implement communication protocol**
   - Parse messages from GPS
   - Send configuration commands

5. **Test in SITL and hardware**

**Reference:** Existing backends (e.g., `AP_GPS_UBLOX.cpp`)

---

## How Sensors Are Initialized

### At Boot

1. **Hardware detection:** ArduPilot probes for sensors
2. **Driver initialization:** Matched drivers are loaded
3. **Calibration loading:** Stored calibration applied
4. **Health checks:** Sensors validated before arming

### Example: GPS Initialization

```cpp
// In AP_GPS.cpp
void AP_GPS::init() {
    // Detect GPS type
    // Create backend instance
    // Configure GPS
    // Start receiving data
}
```

### Viewing Detected Sensors

In SITL or with real hardware:

```bash
# In MAVProxy
param show GPS_TYPE
param show COMPASS_*
param show BARO_PROBE_EXT
```

Or check boot messages in console.

---

## SITL Sensor Simulation

SITL includes simulated sensors with realistic noise and behavior.

**Location:** `libraries/SITL/SIM_*.cpp`

| File | Simulates |
|------|-----------|
| `SIM_GPS.cpp` | GPS (with configurable accuracy, lag) |
| `SIM_Baro.cpp` | Barometer |
| `SIM_Compass.cpp` | Magnetometer |
| `SIM_Airspeed.cpp` | Airspeed sensor |
| `SIM_RangeFinder.cpp` | Rangefinder |

**Capabilities:**
- Add realistic sensor noise
- Simulate GPS dropouts
- Add sensor lag
- Test sensor failures

**Example:** Simulating GPS glitch

```bash
# In SITL, parameter to add GPS noise
param set SIM_GPS_GLITCH_X 10  # 10m glitch in X
```

---

## Sensor Calibration

### Compass Calibration

**Why:** Compass affected by nearby magnets, metal in vehicle

**Process:**
1. Use Mission Planner or QGroundControl
2. Rotate vehicle in all axes
3. Software calculates offsets and scale factors
4. Stored in `COMPASS_OFS_X/Y/Z` and `COMPASS_DIA/ODI_X/Y/Z`

### Accelerometer Calibration

**Why:** Manufacturing tolerances, mounting orientation

**Process:**
1. Place vehicle in 6 orientations (level, sides, nose up/down)
2. Software calculates offsets and scaling
3. Stored in `INS_ACCOFFS_X/Y/Z` and `INS_ACCSCAL_X/Y/Z`

### Airspeed Calibration

**Why:** Pressure sensor offset, tube blockage

**Process:**
1. Cover pitot tube
2. Use GCS calibration tool
3. Fly and auto-calibrate with `ARSPD_AUTOCAL=1`

---

## Troubleshooting Sensors

### GPS Not Detected

**Check:**
- Correct serial port and baud rate
- `GPS_TYPE = 1` (Auto-detect)
- GPS connected and powered

**Fix:**
```bash
param set GPS_TYPE 1
param set SERIAL3_PROTOCOL 5  # Serial3 = GPS
param set SERIAL3_BAUD 115    # 115200 baud
```

### Compass Errors

**Symptoms:** "PreArm: Compass not calibrated" or "Bad compass health"

**Solutions:**
- Calibrate compass
- Move away from metal/magnets
- Check `COMPASS_USE` and `COMPASS_ENABLE`

### IMU Errors

**Symptoms:** "PreArm: Accels not calibrated" or high vibration

**Solutions:**
- Calibrate accelerometers
- Check mounting (damping)
- Review vibration in logs

---

## Code Examples

### Reading GPS Data

```cpp
// In vehicle code
#include <AP_GPS/AP_GPS.h>

AP_GPS gps;

void read_gps() {
    // Update GPS (call frequently)
    gps.update();

    // Get data
    const Location& loc = gps.location();
    float lat = loc.lat * 1e-7;  // degrees
    float lon = loc.lng * 1e-7;
    float alt = loc.alt * 0.01;  // meters

    uint8_t num_sats = gps.num_sats();
    uint8_t fix_type = gps.status();
}
```

### Reading IMU Data

```cpp
#include <AP_InertialSensor/AP_InertialSensor.h>

AP_InertialSensor ins;

void read_imu() {
    // Update IMU
    ins.update();

    // Get data
    Vector3f accel = ins.get_accel();  // m/s²
    Vector3f gyro = ins.get_gyro();    // rad/s

    // Accel in body frame
    float accel_x = accel.x;
    float accel_y = accel.y;
    float accel_z = accel.z;
}
```

---

## Resources

### ArduPilot Documentation

- [Hardware Setup](https://ardupilot.org/plane/docs/common-autopilots.html)
- [Compass Calibration](https://ardupilot.org/plane/docs/common-compass-calibration-in-mission-planner.html)
- [GPS Setup](https://ardupilot.org/plane/docs/common-gps-how-it-works.html)

### Code Reference

Explore sensor drivers in:
```bash
cd ~/ardupilot/libraries
ls -d AP_*
```

Key libraries:
- `AP_GPS/`
- `AP_InertialSensor/`
- `AP_Baro/`
- `AP_Compass/`
- `AP_Airspeed/`

### Developer Docs

- [ArduPilot Sensor Architecture](https://ardupilot.org/dev/docs/learning-ardupilot-the-example-sketches.html)
- [Adding a New Sensor](https://ardupilot.org/dev/docs/code-overview-adding-a-new-mavlink-message.html)

---

## Summary

**Key Takeaways:**

1. **Front-end/back-end architecture** keeps code modular
2. **Front-end provides unified API** to vehicle code
3. **Back-ends handle hardware-specific details**
4. **Multiple sensor instances** supported (e.g., 2 GPS, 3 IMUs)
5. **Sensor drivers in `libraries/AP_*/`**
6. **SITL simulates all sensors** for testing
7. **Calibration essential** for compass, accel, airspeed
8. **Parameters control** sensor behavior

**For new engineers:**
- Understand front-end/back-end pattern
- Locate sensor driver code in `libraries/`
- Learn sensor calibration procedures
- Practice reading sensor data in code examples
- Review SITL sensor simulation code

---

**Last Updated:** 2026-02-03
**Target Version:** Plane 4.5.7
