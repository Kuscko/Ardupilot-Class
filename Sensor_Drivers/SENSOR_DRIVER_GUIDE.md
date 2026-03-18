# ArduPilot Sensor Driver Architecture

**Target Version:** Plane 4.5.7

---

## Front-End / Back-End Pattern

ArduPilot uses a two-layer driver architecture so vehicle code works with any sensor hardware without modification.

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

**Front-End:** Public API, sensor instance management, common calculations, data validation, health monitoring.

**Back-End:** Hardware-specific communication (I2C, SPI, UART), data parsing, configuration commands, sensor quirks.

| Benefit | Description |
|---------|-------------|
| **Modularity** | Add new sensors without modifying vehicle code |
| **Multiple instances** | Support multiple GPS, compasses, etc. |
| **Code reuse** | Common logic stays in front-end |
| **Easier testing** | Mock back-ends for SITL |

---

## Key Sensor Driver Libraries

All in `~/ardupilot/libraries/`

### GPS (`AP_GPS`)

**Location:** `libraries/AP_GPS/`

Supported: uBlox, Trimble, Emlid Reach, NMEA, MAVLink GPS, SITL

| File | Purpose |
|------|---------|
| `AP_GPS.h` | Front-end API |
| `AP_GPS.cpp` | Front-end implementation |
| `AP_GPS_UBLOX.cpp` | uBlox backend |
| `GPS_Backend.h` | Base class for backends |

```cpp
const Location& current_location = gps.location();
uint8_t num_sats = gps.num_sats();
float hdop = gps.get_hdop();
```

Parameters: `GPS_TYPE`, `GPS_AUTO_CONFIG`, `GPS_GNSS_MODE`

---

### IMU (`AP_InertialSensor`)

**Location:** `libraries/AP_InertialSensor/`

Supported: Invensense MPU6000/9000, ICM-20602/20689/42688, ST LSM6DS33, SITL

| File | Purpose |
|------|---------|
| `AP_InertialSensor.h` | Front-end API |
| `AP_InertialSensor.cpp` | Front-end, sensor fusion |
| `AP_InertialSensor_Invensense.cpp` | Invensense backend |
| `AP_InertialSensor_Backend.h` | Backend base class |

Provides: Accelerometer (m/s²), gyroscope (rad/s), temperature, multi-IMU averaging/failover.

Parameters: `INS_GYRO_FILTER`, `INS_ACCEL_FILTER`, `INS_USE`

---

### Barometer (`AP_Baro`)

**Location:** `libraries/AP_Baro/`

Supported: MS5611, BMP280/388, LPS25H, SITL

| File | Purpose |
|------|---------|
| `AP_Baro.h` | Front-end API |
| `AP_Baro_MS56XX.cpp` | MS5611/MS5607 backend |
| `AP_Baro_BMP280.cpp` | BMP280 backend |

Provides: Pressure (Pa), altitude (m), temperature.

Parameters: `BARO_PROBE_EXT`, `BARO_ALT_OFFSET`

---

### Compass (`AP_Compass`)

**Location:** `libraries/AP_Compass/`

Supported: HMC5843/5883, AK8963/AK09916, LSM303D, IST8310, built-in GPS modules, SITL

| File | Purpose |
|------|---------|
| `AP_Compass.h` | Front-end API |
| `AP_Compass_HMC5843.cpp` | HMC5843 backend |
| `AP_Compass_AK8963.cpp` | AK8963 backend |

Provides: Magnetic field vector (mGauss), heading (degrees), calibration interface.

Parameters: `COMPASS_ENABLE`, `COMPASS_AUTODEC`, `COMPASS_OFS_X/Y/Z`

---

### Airspeed (`AP_Airspeed`)

**Location:** `libraries/AP_Airspeed/`

Supported: MS4525DO, SDP3X, Analog, SITL

| File | Purpose |
|------|---------|
| `AP_Airspeed.h` | Front-end API |
| `AP_Airspeed_MS4525.cpp` | MS4525 backend |

Provides: Differential pressure (Pa), airspeed (m/s).

Parameters: `ARSPD_TYPE`, `ARSPD_USE`, `ARSPD_RATIO`

---

### Rangefinder (`AP_RangeFinder`)

**Location:** `libraries/AP_RangeFinder/`

Supported: Lightware, Benewake TFmini, LeddarOne, MaxBotix sonar, PWM-based

| File | Purpose |
|------|---------|
| `AP_RangeFinder.h` | Front-end API |
| `AP_RangeFinder_Backend.h` | Backend base |
| `AP_RangeFinder_Benewake_TFMini.cpp` | TFmini backend |

Provides: Distance to ground (cm), obstacle detection.

Parameters: `RNGFND1_TYPE`, `RNGFND1_MIN_CM`, `RNGFND1_MAX_CM`

---

### Battery Monitor (`AP_BattMonitor`)

**Location:** `libraries/AP_BattMonitor/`

Supported: Analog voltage/current, SMBus, BLHeli ESC telemetry, Generator, SITL

Provides: Voltage (V), current (A), consumed capacity (mAh), remaining (%).

Parameters: `BATT_MONITOR`, `BATT_VOLT_PIN`, `BATT_CURR_PIN`, `BATT_CAPACITY`

---

## Directory Structure

```
~/ardupilot/libraries/
├── AP_GPS/
│   ├── AP_GPS.h
│   ├── AP_GPS.cpp
│   ├── AP_GPS_UBLOX.cpp
│   └── GPS_Backend.h
├── AP_InertialSensor/
│   ├── AP_InertialSensor.h
│   ├── AP_InertialSensor.cpp
│   ├── AP_InertialSensor_Invensense.cpp
│   └── AP_InertialSensor_Backend.h
├── AP_Baro/
│   ├── AP_Baro.h
│   ├── AP_Baro_MS56XX.cpp
│   └── AP_Baro_BMP280.cpp
├── AP_Compass/
│   ├── AP_Compass.h
│   ├── AP_Compass_HMC5843.cpp
│   └── AP_Compass_AK8963.cpp
├── AP_Airspeed/
│   ├── AP_Airspeed.h
│   └── AP_Airspeed_MS4525.cpp
├── AP_RangeFinder/
│   ├── AP_RangeFinder.h
│   └── AP_RangeFinder_Backend.h
├── AP_BattMonitor/
│   ├── AP_BattMonitor.h
│   └── AP_BattMonitor_Analog.cpp
└── AP_OpticalFlow/
    ├── AP_OpticalFlow.h
    └── AP_OpticalFlow_Pixart.cpp
```

---

## Adding a New Sensor

### Example: Adding a New GPS

1. Create backend class (`AP_GPS_MyGPS.cpp`) inheriting from `AP_GPS_Backend`; implement `read()`
2. Register backend in `AP_GPS.cpp` detection list
3. Add `GPS_TYPE` enum value in `AP_GPS.h`
4. Implement communication protocol (parse messages, send config)
5. Test in SITL and hardware

Reference: `AP_GPS_UBLOX.cpp`

---

## Sensor Initialization

At boot: hardware detection → driver initialization → calibration loading → health checks before arming.

```cpp
// In AP_GPS.cpp
void AP_GPS::init() {
    // Detect GPS type
    // Create backend instance
    // Configure GPS
    // Start receiving data
}
```

```bash
# View detected sensors in MAVProxy
param show GPS_TYPE
param show COMPASS_*
param show BARO_PROBE_EXT
```

---

## SITL Sensor Simulation

**Location:** `libraries/SITL/SIM_*.cpp`

| File | Simulates |
|------|-----------|
| `SIM_GPS.cpp` | GPS (configurable accuracy, lag) |
| `SIM_Baro.cpp` | Barometer |
| `SIM_Compass.cpp` | Magnetometer |
| `SIM_Airspeed.cpp` | Airspeed sensor |
| `SIM_RangeFinder.cpp` | Rangefinder |

```bash
# Simulate GPS glitch
param set SIM_GPS_GLITCH_X 10  # 10m glitch in X
```

---

## Sensor Calibration

**Compass:** Rotate vehicle in all axes via Mission Planner or QGroundControl. Offsets stored in `COMPASS_OFS_X/Y/Z` and `COMPASS_DIA/ODI_X/Y/Z`.

**Accelerometer:** Place vehicle in 6 orientations. Offsets stored in `INS_ACCOFFS_X/Y/Z` and `INS_ACCSCAL_X/Y/Z`.

**Airspeed:** Cover pitot tube, use GCS calibration tool. Auto-calibrate in flight with `ARSPD_AUTOCAL=1`.

---

## Troubleshooting

### GPS Not Detected

```bash
param set GPS_TYPE 1
param set SERIAL3_PROTOCOL 5  # Serial3 = GPS
param set SERIAL3_BAUD 115    # 115200 baud
```

### Compass Errors

**Symptoms:** "PreArm: Compass not calibrated" or "Bad compass health"

Calibrate compass, move away from metal/magnets, check `COMPASS_USE` and `COMPASS_ENABLE`.

### IMU Errors

**Symptoms:** "PreArm: Accels not calibrated" or high vibration

Calibrate accelerometers, check mounting/damping, review vibration in logs.

---

## Code Examples

### Reading GPS Data

```cpp
#include <AP_GPS/AP_GPS.h>

AP_GPS gps;

void read_gps() {
    gps.update();

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
    ins.update();

    Vector3f accel = ins.get_accel();  // m/s²
    Vector3f gyro = ins.get_gyro();    // rad/s

    float accel_x = accel.x;
    float accel_y = accel.y;
    float accel_z = accel.z;
}
```

---

## Resources

- [Hardware Setup](https://ardupilot.org/plane/docs/common-autopilots.html)
- [Compass Calibration](https://ardupilot.org/plane/docs/common-compass-calibration-in-mission-planner.html)
- [GPS Setup](https://ardupilot.org/plane/docs/common-gps-how-it-works.html)
- [ArduPilot Sensor Architecture](https://ardupilot.org/dev/docs/learning-ardupilot-the-example-sketches.html)

---

**Last Updated:** 2026-02-03
**Target Version:** Plane 4.5.7
