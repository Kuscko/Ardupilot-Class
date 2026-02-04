# Custom Build Configurations Guide

## Overview

ArduPilot's build system allows customizing features, board definitions, and build options for specific hardware or applications.

---

## Board Definitions (hwdef.dat)

### Location

Board hardware definitions are in:
```
libraries/AP_HAL_ChibiOS/hwdef/BOARDNAME/
├── hwdef.dat          # Main hardware definition
├── hwdef-bl.dat       # Bootloader definition (optional)
└── README.md          # Board documentation
```

### hwdef.dat Structure

**Example hwdef.dat:**
```python
# MCU and crystal
MCU STM32F7xx STM32F767xx
FLASH_SIZE_KB 2048
OSCILLATOR_HZ 24000000

# Board ID
APJ_BOARD_ID 9

# Bootloader
FLASH_RESERVE_START_KB 16

# Serial ports
SERIAL_ORDER OTG1 USART2 USART3

# UART definitions
PA9 USART1_TX USART1
PA10 USART1_RX USART1

# SPI buses
PA5 SPI1_SCK SPI1
PA6 SPI1_MISO SPI1
PA7 SPI1_MOSI SPI1

# I2C
PB8 I2C1_SCL I2C1
PB9 I2C1_SDA I2C1

# IMU
PC13 MPU9250_CS CS
PC14 MPU9250_DRDY INPUT

# Define IMU
SPIDEV mpu9250 SPI1 DEVID1 MPU9250_CS MODE3 4*MHZ 8*MHZ
IMU Invensense SPI:mpu9250 ROTATION_YAW_180

# Barometer
BARO MS56XX I2C:0:0x76

# Compass
COMPASS AK8963:probe_mpu9250 0 ROTATION_YAW_270

# Storage
define HAL_STORAGE_SIZE 16384
```

### Common hwdef.dat Directives

| Directive | Purpose | Example |
|-----------|---------|---------|
| `MCU` | Microcontroller type | `MCU STM32F7xx` |
| `SERIAL_ORDER` | Serial port priority | `SERIAL_ORDER OTG1 USART2` |
| `SPIDEV` | Define SPI device | `SPIDEV mpu9250 SPI1 DEVID1` |
| `IMU` | Define IMU | `IMU Invensense SPI:mpu9250` |
| `BARO` | Define barometer | `BARO MS56XX I2C:0:0x76` |
| `define` | C preprocessor define | `define HAL_STORAGE_SIZE 16384` |

---

## Feature Enable/Disable

### Build-Time Features

ArduPilot uses C preprocessor defines to enable/disable features at compile time.

### Common Feature Defines

**In hwdef.dat:**
```python
# Disable features to save flash space
define HAL_PARACHUTE_ENABLED 0
define HAL_SPRAYER_ENABLED 0
define HAL_GRIPPER_ENABLED 0
define HAL_LOGGING_ENABLED 1
define HAL_RALLY_ENABLED 1

# Disable specific sensors
define HAL_COMPASS_AK8963_ENABLED 0
define HAL_BARO_MS5611_ENABLED 0

# Disable protocols
define HAL_SUPPORT_RCOUT_SERIAL 0
define COMPASS_CAL_ENABLED 0
```

### Feature Categories

**Navigation:**
- `HAL_RALLY_ENABLED` - Rally points
- `MODE_AUTO_ENABLED` - AUTO mode
- `MODE_RTL_ENABLED` - RTL mode
- `MODE_LOITER_ENABLED` - LOITER mode

**Peripherals:**
- `HAL_PARACHUTE_ENABLED` - Parachute support
- `HAL_MOUNT_ENABLED` - Gimbal/mount
- `HAL_SPRAYER_ENABLED` - Crop sprayer
- `HAL_GRIPPER_ENABLED` - Gripper/release

**Sensors:**
- `HAL_COMPASS_ENABLED` - Compass
- `HAL_AIRSPEED_ENABLED` - Airspeed sensor
- `HAL_RANGEFINDER_ENABLED` - Rangefinder

**Logging:**
- `HAL_LOGGING_ENABLED` - DataFlash logging
- `HAL_LOGGING_DATAFLASH_ENABLED` - Flash logging backend

---

## Build Optimization

### Optimize for Size

**In hwdef.dat:**
```python
# Use -Os optimization (optimize for size)
env OPTIMIZE -Os

# Disable debug symbols
define HAL_DEBUG_BUILD 0

# Minimal logging
define HAL_LOGGING_ENABLED 0
```

**Build:**
```bash
./waf configure --board=YourBoard
./waf plane --optimize=size
```

### Optimize for Speed

**In hwdef.dat:**
```python
# Use -O3 optimization (optimize for speed)
env OPTIMIZE -O3

# Enable fast sampling
define HAL_FAST_SAMPLE 1
```

---

## Creating a Custom Board

### Step 1: Copy Existing Board

```bash
cd ~/ardupilot/libraries/AP_HAL_ChibiOS/hwdef
cp -r CubeOrange MyCustomBoard
cd MyCustomBoard
```

### Step 2: Modify hwdef.dat

```python
# Change board ID (must be unique!)
APJ_BOARD_ID 999

# Modify as needed
# Change pin assignments
# Enable/disable features
# Adjust peripherals
```

### Step 3: Build

```bash
cd ~/ardupilot/ArduPlane
./waf configure --board=MyCustomBoard
./waf plane
```

### Step 4: Flash

```bash
# Upload to board
./waf plane --upload
```

---

## Flash Size Management

### Check Flash Usage

```bash
# After building
./waf plane

# Output shows:
# text    data     bss     dec     hex filename
# 985234  12456  123456  1121146  111cfa build/.../arduplane
```

**Flash usage:**
- `text` = Code size
- `data` = Initialized data
- Total = text + data (must fit in FLASH_SIZE_KB)

### Reducing Flash Usage

**Priority 1: Disable unused features**
```python
define HAL_PARACHUTE_ENABLED 0
define HAL_SPRAYER_ENABLED 0
```

**Priority 2: Disable sensors not on board**
```python
define HAL_COMPASS_AK8963_ENABLED 0
define HAL_COMPASS_HMC5843_ENABLED 0
```

**Priority 3: Disable unused modes**
```python
define MODE_QSTABILIZE_ENABLED 0  # QuadPlane modes
define MODE_QHOVER_ENABLED 0
```

**Priority 4: Reduce logging**
```python
define HAL_LOGGING_ENABLED 0  # Last resort!
```

---

## Custom Bootloader

### bootloader hwdef-bl.dat

**Example:**
```python
# Minimal bootloader config
MCU STM32F7xx STM32F767xx
FLASH_SIZE_KB 2048
OSCILLATOR_HZ 24000000

# Bootloader flash reservation
FLASH_BOOTLOADER_LOAD_KB 16

# LED for bootloader status
PA0 LED_BOOTLOADER OUTPUT

# USB for firmware upload
PA11 OTG_FS_DM OTG1
PA12 OTG_FS_DP OTG1
```

### Build Bootloader

```bash
./waf configure --board=MyCustomBoard --bootloader
./waf bootloader
```

### Flash Bootloader

```bash
# Via STLink or DFU
dfu-util -a 0 -D build/MyCustomBoard/bin/AP_Bootloader.bin
```

---

## Custom Defaults

### defaults.parm File

Create `defaults.parm` in board directory:

```
# Custom default parameters for MyCustomBoard
SERIAL1_PROTOCOL,2
SERIAL1_BAUD,921
LOG_BACKEND_TYPE,1
LOG_FILE_DSRMROT,1
ARSPD_TYPE,1
GPS_TYPE,1
```

**These parameters are set on first boot.**

---

## Build Variants

### Create Multiple Configurations

**In hwdef directory:**
```
MyBoard/
├── hwdef.dat              # Standard config
├── hwdef-racing.dat       # Racing variant
├── hwdef-longrange.dat    # Long range variant
```

**Build specific variant:**
```bash
./waf configure --board=MyBoard --variant=racing
./waf plane
```

---

## Example: Minimal Build

**Goal:** Smallest possible build for basic flight

**hwdef-minimal.dat:**
```python
# Start from base hwdef.dat
include hwdef.dat

# Disable everything non-essential
define HAL_PARACHUTE_ENABLED 0
define HAL_SPRAYER_ENABLED 0
define HAL_GRIPPER_ENABLED 0
define HAL_MOUNT_ENABLED 0
define HAL_RALLY_ENABLED 0
define HAL_BEACON_ENABLED 0
define HAL_ADSB_ENABLED 0
define HAL_PROXIMITY_ENABLED 0
define HAL_RPM_ENABLED 0

# Disable advanced modes
define MODE_LOITER_ENABLED 0
define MODE_CIRCLE_ENABLED 0
define MODE_GUIDED_ENABLED 0

# Minimal logging
define HAL_LOGGING_ENABLED 0

# Disable Lua scripting
define AP_SCRIPTING_ENABLED 0

# Size optimization
env OPTIMIZE -Os
```

**Build:**
```bash
./waf configure --board=MyBoard --variant=minimal
./waf plane
```

---

## Example: Custom Plane with LIDAR

**Add rangefinder support:**

**In hwdef.dat:**
```python
# Enable rangefinder
define HAL_RANGEFINDER_ENABLED 1

# Lightware LiDAR on SERIAL4
SERIAL4 USART4
PA0 USART4_TX USART4
PA1 USART4_RX USART4

# Default parameters
SERIAL4_PROTOCOL 9    # Rangefinder
SERIAL4_BAUD 115      # 115200
RNGFND1_TYPE 8        # LightwareSerial
```

---

## Troubleshooting

### Build Fails: Feature Not Defined

**Error:** `AP_Parachute.h: No such file`

**Cause:** Feature disabled but code references it

**Fix:** Properly guard with `#if HAL_PARACHUTE_ENABLED`

### Flash Overflow

**Error:** `region 'flash' overflowed`

**Cause:** Firmware too large for flash

**Fix:** Disable features (see Flash Size Management)

### Bootloader Not Working

**Symptom:** Board won't enter bootloader

**Fix:**
- Check LED_BOOTLOADER pin correct
- Verify USB pins correct
- Check FLASH_BOOTLOADER_LOAD_KB matches

---

## Best Practices

1. **Always start from existing board** - Don't create from scratch
2. **Unique board ID** - Never reuse another board's ID
3. **Test incrementally** - Make small changes, test often
4. **Document changes** - Update README.md
5. **Version control** - Track hwdef.dat changes in git
6. **Backup working config** - Before major changes

---

## Resources

**Official Documentation:**
- [Custom Firmware Guide](https://ardupilot.org/dev/docs/building-the-code.html)
- [Board Configuration](https://ardupilot.org/dev/docs/porting.html)
- [ChibiOS HAL](https://ardupilot.org/dev/docs/apmcopter-programming-libraries.html)

**Example Boards:**
- `libraries/AP_HAL_ChibiOS/hwdef/CubeOrange/`
- `libraries/AP_HAL_ChibiOS/hwdef/Pixhawk4/`
- `libraries/AP_HAL_ChibiOS/hwdef/MatekH743/`

---

**Author:** Patrick Kelly (@Kuscko)
**Version:** 1.0
**Last Updated:** 2026-02-03
