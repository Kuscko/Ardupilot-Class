# Custom Build Configurations

Custom ArduPilot builds let you enable/disable features, optimize for flash size or performance, and support custom hardware using hardware definition files (hwdef.dat).

## Key Concepts

### Hardware Definition Files (hwdef.dat)

Each flight controller board has a `hwdef.dat` file at `libraries/AP_HAL_ChibiOS/hwdef/<BOARD>/hwdef.dat` defining:

- MCU specifications (processor, flash, RAM)
- Pin assignments (UART, I2C, SPI)
- Default parameters
- Enabled/disabled features

### Feature Flags

```cpp
define HAL_PARACHUTE_ENABLED 1        // Enable parachute support
define HAL_SPRAYER_ENABLED 0          // Disable sprayer support
define AP_TERRAIN_AVAILABLE 1         // Enable terrain following
define HAL_WITH_DSP 0                 // Disable DSP features
```

### Flash Memory Constraints

| Board size   | Flash   |
| ------------ | ------- |
| Small        | 1MB     |
| Medium       | 2MB     |
| Large        | 8MB+    |

### Feature Flag Flash Impact

| Feature Flag              | Purpose                  | Flash Impact |
| ------------------------- | ------------------------ | ------------ |
| HAL_PARACHUTE_ENABLED     | Parachute deployment     | ~5KB         |
| HAL_SPRAYER_ENABLED       | Agricultural sprayer     | ~3KB         |
| HAL_MOUNT_ENABLED         | Gimbal mount control     | ~15KB        |
| AP_TERRAIN_AVAILABLE      | Terrain following        | ~20KB        |
| HAL_OSD_ENABLED           | On-screen display        | ~30KB        |
| HAL_LOGGING_ENABLED       | Dataflash logging        | ~40KB        |
| AP_CAMERA_ENABLED         | Camera trigger control   | ~10KB        |
| HAL_QUADPLANE_ENABLED     | QuadPlane VTOL support   | ~50KB        |

## Exercises

### Exercise 1: List Available Boards

```bash
cd ~/ardupilot
./waf list_boards
```

### Exercise 2: Examine Board Configuration

```bash
cd libraries/AP_HAL_ChibiOS/hwdef
cat Pixhawk1/hwdef.dat
```

Example hwdef.dat excerpt:

```text
MCU STM32F4xx STM32F427xx
FLASH_SIZE_KB 2048
RAM_SIZE_KB 256

UART1 TX PB6
UART1 RX PB7

define HAL_PARACHUTE_ENABLED 1
define AP_TERRAIN_AVAILABLE 1
```

### Exercise 3: Create Custom Board Variant

```bash
cd ~/ardupilot/libraries/AP_HAL_ChibiOS/hwdef
mkdir CustomPixhawk
cp Pixhawk1/hwdef.dat CustomPixhawk/hwdef.dat
nano CustomPixhawk/hwdef.dat
```

Add to disable features:

```text
define HAL_PARACHUTE_ENABLED 0
define HAL_SPRAYER_ENABLED 0
define HAL_GRIPPER_ENABLED 0
define AP_TERRAIN_AVAILABLE 0
define HAL_OSD_ENABLED 0
```

```bash
cd ~/ardupilot
./waf configure --board=CustomPixhawk
./waf plane
ls -lh build/CustomPixhawk/bin/arduplane.apj
```

### Exercise 4: Enable Optional Feature

```bash
nano libraries/AP_HAL_ChibiOS/hwdef/CustomPixhawk/hwdef.dat
```

```text
define HAL_QUADPLANE_ENABLED 1
define HAL_MOUNT_ENABLED 1
define AP_CAMERA_ENABLED 1
```

```bash
./waf clean
./waf configure --board=CustomPixhawk
./waf plane
```

### Exercise 5: Check Flash Usage

```bash
./waf configure --board=Pixhawk1
./waf plane
ls -lh build/Pixhawk1/bin/arduplane.apj

./waf configure --board=CustomPixhawk
./waf plane
ls -lh build/CustomPixhawk/bin/arduplane.apj
```

### Common Configuration: Reduce Flash

```text
define HAL_PARACHUTE_ENABLED 0
define HAL_SPRAYER_ENABLED 0
define HAL_GRIPPER_ENABLED 0
define HAL_BEACON_ENABLED 0
define HAL_PROXIMITY_ENABLED 0
define AP_TERRAIN_AVAILABLE 0
define HAL_ADSB_ENABLED 0
define HAL_OSD_ENABLED 0
```

### Common Configuration: Custom Parameter Defaults

```text
env DEFAULT_PARAMETERS libraries/AP_HAL_ChibiOS/hwdef/CustomPixhawk/defaults.parm
```

```text
# defaults.parm
SERIAL2_PROTOCOL 2
SERIAL2_BAUD 921600
ARMING_CHECK 1
BRD_SAFETYENABLE 1
```

## Common Issues

### Undefined Symbols

```text
undefined reference to `AP_Parachute::update()'
```

Feature disabled but code references it — either enable the feature or disable dependent features.

### Firmware Too Large

```text
region `flash' overflowed by 45678 bytes
```

```text
define HAL_LOGGING_DATAFLASH_ENABLED 0
define AP_TERRAIN_AVAILABLE 0
define HAL_OSD_ENABLED 0
```

### hwdef.dat Changes Not Taking Effect

```bash
./waf clean
./waf configure --board=CustomPixhawk
./waf plane
```

### Board Not Found

```bash
ls libraries/AP_HAL_ChibiOS/hwdef/CustomBoard/
# Must contain hwdef.dat

./waf distclean
./waf configure --board=CustomBoard
```

---

- [ArduPilot Build Options](https://ardupilot.org/dev/docs/build-options.html)
- [Hardware Definition Files](https://ardupilot.org/dev/docs/hwdef.html)
- Study: `hwdef/Pixhawk1/`, `hwdef/MatekH743/`, `hwdef/CUAV-X7/`
