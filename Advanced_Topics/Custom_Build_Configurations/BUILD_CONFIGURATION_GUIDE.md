# Custom Build Configurations Guide

ArduPilot's build system allows customizing features, board definitions, and build options for specific hardware or applications.

---

## Board Definitions (hwdef.dat)

### Location

```text
libraries/AP_HAL_ChibiOS/hwdef/BOARDNAME/
├── hwdef.dat          # Main hardware definition
├── hwdef-bl.dat       # Bootloader definition (optional)
└── README.md          # Board documentation
```

### hwdef.dat Structure

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

| Directive        | Purpose               | Example                          |
| ---------------- | --------------------- | -------------------------------- |
| `MCU`            | Microcontroller type  | `MCU STM32F7xx`                  |
| `SERIAL_ORDER`   | Serial port priority  | `SERIAL_ORDER OTG1 USART2`       |
| `SPIDEV`         | Define SPI device     | `SPIDEV mpu9250 SPI1 DEVID1`     |
| `IMU`            | Define IMU            | `IMU Invensense SPI:mpu9250`     |
| `BARO`           | Define barometer      | `BARO MS56XX I2C:0:0x76`         |
| `define`         | C preprocessor define | `define HAL_STORAGE_SIZE 16384`  |

---

## Feature Enable/Disable

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

**Navigation:** `HAL_RALLY_ENABLED`, `MODE_AUTO_ENABLED`, `MODE_RTL_ENABLED`, `MODE_LOITER_ENABLED`

**Peripherals:** `HAL_PARACHUTE_ENABLED`, `HAL_MOUNT_ENABLED`, `HAL_SPRAYER_ENABLED`, `HAL_GRIPPER_ENABLED`

**Sensors:** `HAL_COMPASS_ENABLED`, `HAL_AIRSPEED_ENABLED`, `HAL_RANGEFINDER_ENABLED`

**Logging:** `HAL_LOGGING_ENABLED`, `HAL_LOGGING_DATAFLASH_ENABLED`

---

## Build Optimization

### Optimize for Size

```python
env OPTIMIZE -Os
define HAL_DEBUG_BUILD 0
define HAL_LOGGING_ENABLED 0
```

```bash
./waf configure --board=YourBoard
./waf plane --optimize=size
```

### Optimize for Speed

```python
env OPTIMIZE -O3
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

# Modify pin assignments, enable/disable features
```

### Step 3: Build

```bash
cd ~/ardupilot/ArduPlane
./waf configure --board=MyCustomBoard
./waf plane
```

### Step 4: Flash

```bash
./waf plane --upload
```

---

## Flash Size Management

### Check Flash Usage

```bash
./waf plane
# Output shows:
# text    data     bss     dec     hex filename
# 985234  12456  123456  1121146  111cfa build/.../arduplane
```

- `text` = Code size
- `data` = Initialized data
- Total = text + data (must fit in FLASH_SIZE_KB)

### Reducing Flash Usage

```python
# Priority 1: Disable unused features
define HAL_PARACHUTE_ENABLED 0
define HAL_SPRAYER_ENABLED 0

# Priority 2: Disable sensors not on board
define HAL_COMPASS_AK8963_ENABLED 0
define HAL_COMPASS_HMC5843_ENABLED 0

# Priority 3: Disable unused modes
define MODE_QSTABILIZE_ENABLED 0
define MODE_QHOVER_ENABLED 0

# Priority 4: Reduce logging (last resort)
define HAL_LOGGING_ENABLED 0
```

---

## Custom Bootloader

### hwdef-bl.dat Example

```python
MCU STM32F7xx STM32F767xx
FLASH_SIZE_KB 2048
OSCILLATOR_HZ 24000000

FLASH_BOOTLOADER_LOAD_KB 16

PA0 LED_BOOTLOADER OUTPUT

PA11 OTG_FS_DM OTG1
PA12 OTG_FS_DP OTG1
```

### Build and Flash Bootloader

```bash
./waf configure --board=MyCustomBoard --bootloader
./waf bootloader

# Via STLink or DFU
dfu-util -a 0 -D build/MyCustomBoard/bin/AP_Bootloader.bin
```

---

## Custom Defaults

Create `defaults.parm` in board directory:

```text
# Custom default parameters for MyCustomBoard
SERIAL1_PROTOCOL,2
SERIAL1_BAUD,921
LOG_BACKEND_TYPE,1
LOG_FILE_DSRMROT,1
ARSPD_TYPE,1
GPS_TYPE,1
```

Parameters are set on first boot.

---

## Build Variants

```text
MyBoard/
├── hwdef.dat              # Standard config
├── hwdef-racing.dat       # Racing variant
├── hwdef-longrange.dat    # Long range variant
```

```bash
./waf configure --board=MyBoard --variant=racing
./waf plane
```

---

## Example: Minimal Build

```python
# Start from base hwdef.dat
include hwdef.dat

define HAL_PARACHUTE_ENABLED 0
define HAL_SPRAYER_ENABLED 0
define HAL_GRIPPER_ENABLED 0
define HAL_MOUNT_ENABLED 0
define HAL_RALLY_ENABLED 0
define HAL_BEACON_ENABLED 0
define HAL_ADSB_ENABLED 0
define HAL_PROXIMITY_ENABLED 0
define HAL_RPM_ENABLED 0
define MODE_LOITER_ENABLED 0
define MODE_CIRCLE_ENABLED 0
define MODE_GUIDED_ENABLED 0
define HAL_LOGGING_ENABLED 0
define AP_SCRIPTING_ENABLED 0
env OPTIMIZE -Os
```

```bash
./waf configure --board=MyBoard --variant=minimal
./waf plane
```

---

## Example: Custom Plane with LIDAR

```python
define HAL_RANGEFINDER_ENABLED 1

SERIAL4 USART4
PA0 USART4_TX USART4
PA1 USART4_RX USART4

SERIAL4_PROTOCOL 9    # Rangefinder
SERIAL4_BAUD 115      # 115200
RNGFND1_TYPE 8        # LightwareSerial
```

---

## Troubleshooting

### Feature Not Defined

**Error:** `AP_Parachute.h: No such file` — Feature disabled but code references it. Guard with `#if HAL_PARACHUTE_ENABLED`.

### Flash Overflow

**Error:** `region 'flash' overflowed` — Disable features (see Flash Size Management above).

### Bootloader Not Working

- Check LED_BOOTLOADER pin is correct
- Verify USB pins are correct
- Check FLASH_BOOTLOADER_LOAD_KB matches

---

## Best Practices

1. Always start from an existing board — don't create from scratch
2. Use a unique board ID — never reuse another board's ID
3. Test incrementally — make small changes, test often
4. Track hwdef.dat changes in git

---

- [Custom Firmware Guide](https://ardupilot.org/dev/docs/building-the-code.html)
- [Hardware Definition Files](https://ardupilot.org/dev/docs/hwdef.html)
- Example boards: `hwdef/CubeOrange/`, `hwdef/Pixhawk4/`, `hwdef/MatekH743/`

**Author:** Patrick Kelly (@Kuscko)
