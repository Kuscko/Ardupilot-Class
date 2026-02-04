# Custom Build Configurations

## Overview

Learn to create custom ArduPilot builds tailored to specific hardware, feature requirements, or flash memory constraints. Custom configurations allow you to enable/disable features, optimize for performance or size, and support custom hardware designs [1].

This module covers hardware definition files (hwdef.dat), feature flags, build optimization, and managing flash memory constraints.

## Prerequisites

Before starting this module, you should have:

- Successfully built ArduPilot from source for SITL
- Understanding of WAF build system basics
- Familiarity with ArduPilot architecture and libraries
- Basic knowledge of hardware specifications (flash size, peripherals)
- Text editor for modifying configuration files

## What You'll Learn

By completing this module, you will:

- Understand ArduPilot's build configuration system
- Modify hardware definition files (hwdef.dat)
- Enable and disable features using AP_* defines
- Optimize builds for flash size or performance
- Create custom board variants
- Troubleshoot build configuration issues
- Understand bootloader requirements

## Key Concepts

### Hardware Definition Files (hwdef.dat)

Each flight controller board has a `hwdef.dat` file defining [2]:

- **MCU specifications** - Processor, flash size, RAM
- **Pin assignments** - Which GPIO pins connect to which peripherals
- **Default parameters** - Board-specific parameter defaults
- **Features** - Enabled/disabled features for this board

**Location:** `libraries/AP_HAL_ChibiOS/hwdef/<BOARD>/hwdef.dat`

### Feature Flags

ArduPilot uses preprocessor defines to enable/disable features [3]:

```cpp
// In hwdef.dat or AP_HAL_ChibiOS_Class.h
define HAL_PARACHUTE_ENABLED 1        // Enable parachute support
define HAL_SPRAYER_ENABLED 0          // Disable sprayer support
define AP_TERRAIN_AVAILABLE 1         // Enable terrain following
define HAL_WITH_DSP 0                 // Disable DSP features
```

**Why Customize?** Reduces flash usage, removes unneeded code, optimizes for specific use cases.

### Flash Memory Constraints

Flight controllers have limited flash memory:

- **Small boards:** 1MB flash (tight constraints)
- **Medium boards:** 2MB flash (moderate constraints)
- **Large boards:** 8MB+ flash (minimal constraints)

Custom builds help fit required features within available flash.

### Build Optimization Levels

WAF supports optimization flags:

- **-O2** - Default, balanced optimization
- **-Os** - Optimize for size (smaller binary)
- **-O3** - Optimize for speed (faster execution, larger binary)

## Hands-On Practice

### Exercise 1: List Available Boards

```bash
cd ~/ardupilot

# List all supported boards
./waf list_boards

# Output shows boards like:
# - Pixhawk1
# - MatekH743
# - CubeOrange
# - SITL
# ... many others
```

### Exercise 2: Examine Board Configuration

```bash
# View a board's hardware definition
cd libraries/AP_HAL_ChibiOS/hwdef

# Example: Look at Pixhawk1 configuration
cat Pixhawk1/hwdef.dat

# Key sections to notice:
# - MCU model and flash size
# - Pin definitions (UART, I2C, SPI)
# - Default parameters
# - Feature defines
```

**Example hwdef.dat excerpt:**
```
# MCU class and specific type
MCU STM32F4xx STM32F427xx

# Flash and RAM
FLASH_SIZE_KB 2048
RAM_SIZE_KB 256

# UART pins
UART1 TX PB6
UART1 RX PB7

# Features
define HAL_PARACHUTE_ENABLED 1
define AP_TERRAIN_AVAILABLE 1
```

### Exercise 3: Create Custom Board Variant

Create a minimal custom build:

```bash
cd ~/ardupilot/libraries/AP_HAL_ChibiOS/hwdef

# Create custom board based on existing board
mkdir CustomPixhawk
cp Pixhawk1/hwdef.dat CustomPixhawk/hwdef.dat

# Edit CustomPixhawk/hwdef.dat
nano CustomPixhawk/hwdef.dat
```

**Modify to disable features:**
```
# Add these lines to disable features and reduce flash usage
define HAL_PARACHUTE_ENABLED 0
define HAL_SPRAYER_ENABLED 0
define HAL_GRIPPER_ENABLED 0
define AP_TERRAIN_AVAILABLE 0
define HAL_LOGGING_ENABLED 0         # Disable logging (not recommended!)
define HAL_OSD_ENABLED 0              # Disable OSD
```

**Build custom configuration:**
```bash
cd ~/ardupilot
./waf configure --board=CustomPixhawk
./waf plane

# Check resulting binary size
ls -lh build/CustomPixhawk/bin/arduplane.apj
```

**Expected Result:** Smaller firmware size compared to standard build.

### Exercise 4: Enable Optional Feature

Add a feature that's disabled by default:

```bash
# Edit your custom hwdef.dat
nano libraries/AP_HAL_ChibiOS/hwdef/CustomPixhawk/hwdef.dat

# Enable advanced features
define HAL_QUADPLANE_ENABLED 1        # Enable QuadPlane support
define HAL_MOUNT_ENABLED 1            # Enable gimbal mount support
define AP_CAMERA_ENABLED 1            # Enable camera control
```

**Rebuild:**
```bash
./waf clean
./waf configure --board=CustomPixhawk
./waf plane
```

### Exercise 5: Check Flash Usage

Monitor how configuration changes affect flash size:

```bash
# Build default Pixhawk1
./waf configure --board=Pixhawk1
./waf plane
ls -lh build/Pixhawk1/bin/arduplane.apj

# Build custom configuration
./waf configure --board=CustomPixhawk
./waf plane
ls -lh build/CustomPixhawk/bin/arduplane.apj

# Compare sizes
du -h build/Pixhawk1/bin/arduplane.apj
du -h build/CustomPixhawk/bin/arduplane.apj
```

**Analysis:** Note the difference in firmware size based on enabled features.

## Common Configuration Changes

### Reduce Flash Usage

When flash is constrained, disable features:

```
# Minimal configuration for small boards
define HAL_PARACHUTE_ENABLED 0
define HAL_SPRAYER_ENABLED 0
define HAL_GRIPPER_ENABLED 0
define HAL_BEACON_ENABLED 0
define HAL_PROXIMITY_ENABLED 0
define AP_TERRAIN_AVAILABLE 0
define HAL_ADSB_ENABLED 0
define HAL_OSD_ENABLED 0              # Only if OSD not needed
```

### Enable Advanced Features

For capable boards with ample flash:

```
# Advanced features
define HAL_QUADPLANE_ENABLED 1
define HAL_SOARING_ENABLED 1
define AP_TERRAIN_AVAILABLE 1
define HAL_MOUNT_ENABLED 1
define HAL_CAMERA_ENABLED 1
define AP_CAMERA_SCRIPTING_ENABLED 1
define HAL_VISUALODOM_ENABLED 1
```

### Custom Parameter Defaults

Set board-specific parameter defaults:

```
# In hwdef.dat
env DEFAULT_PARAMETERS libraries/AP_HAL_ChibiOS/hwdef/CustomPixhawk/defaults.parm
```

**Create defaults.parm:**
```
# CustomPixhawk default parameters
SERIAL2_PROTOCOL 2           # MAVLink2 on TELEM2
SERIAL2_BAUD 921600          # High baud rate
ARMING_CHECK 1               # Enable all arming checks
BRD_SAFETYENABLE 1           # Require safety switch
```

## Common Issues

### Issue: Build Fails with Undefined Symbols

**Symptoms:**
```
undefined reference to `AP_Parachute::update()'
```

**Cause:** Feature disabled in hwdef.dat but code still references it

**Solution:**

1. Check if feature is required by other enabled features
2. Either enable the feature or disable dependent features
3. Review build output for dependency chains

### Issue: Firmware Too Large for Flash

**Symptoms:**
```
region `flash' overflowed by 45678 bytes
```

**Cause:** Too many features enabled for available flash

**Solutions:**

```
# Disable optional features in hwdef.dat
define HAL_LOGGING_DATAFLASH_ENABLED 0
define AP_TERRAIN_AVAILABLE 0
define HAL_OSD_ENABLED 0
define HAL_PARACHUTE_ENABLED 0

# Or use smaller optimization
CFLAGS = -Os  # Optimize for size
```

### Issue: Modified hwdef.dat Not Taking Effect

**Symptoms:** Changes to hwdef.dat don't appear in build

**Solution:**

```bash
# Clean build entirely
./waf clean

# Reconfigure with your board
./waf configure --board=CustomPixhawk

# Rebuild
./waf plane
```

### Issue: Board Not Found

**Symptoms:** `./waf configure --board=CustomBoard` reports "Invalid board"

**Cause:** New board directory not detected

**Solution:**

```bash
# Verify directory structure
ls libraries/AP_HAL_ChibiOS/hwdef/CustomBoard/

# Should contain:
# - hwdef.dat (required)

# Clean and reconfigure
./waf distclean
./waf configure --board=CustomBoard
```

## Feature Reference

Common feature flags and their purposes [3]:

| Feature Flag | Purpose | Flash Impact |
|--------------|---------|--------------|
| HAL_PARACHUTE_ENABLED | Parachute deployment | ~5KB |
| HAL_SPRAYER_ENABLED | Agricultural sprayer | ~3KB |
| HAL_MOUNT_ENABLED | Gimbal mount control | ~15KB |
| AP_TERRAIN_AVAILABLE | Terrain following | ~20KB |
| HAL_OSD_ENABLED | On-screen display | ~30KB |
| HAL_LOGGING_ENABLED | Dataflash logging | ~40KB |
| AP_CAMERA_ENABLED | Camera trigger control | ~10KB |
| HAL_QUADPLANE_ENABLED | QuadPlane VTOL support | ~50KB |

**Note:** Flash impact is approximate and varies by vehicle type.

## Additional Resources

- [ArduPilot Build Options](https://ardupilot.org/dev/docs/build-options.html) [1] - Feature flags reference
- [Hardware Definition Files](https://ardupilot.org/dev/docs/hwdef.html) [2] - hwdef.dat documentation
- [Adding New Board](https://ardupilot.org/dev/docs/building-setup-linux.html#adding-a-new-board) [3] - Custom board guide
- [Flash Optimization](https://ardupilot.org/dev/docs/code-overview-size-reduction.html) [4] - Size reduction techniques

### Board Examples

Study existing board configurations:

- `hwdef/Pixhawk1/` - Classic Pixhawk configuration
- `hwdef/MatekH743/` - Modern H7 board
- `hwdef/CUAV-X7/` - Feature-rich configuration
- `hwdef/JHEMCU-GSF405A/` - Minimal racing quad board

## Next Steps

After mastering custom builds:

1. **Debugging Tools** - Debug custom hardware configurations
2. **Sensor Drivers** - Add support for custom sensors
3. **Performance Optimization** - Profile and optimize code
4. **Code Contribution** - Contribute new board support upstream

---

**Sources:**

[1] https://ardupilot.org/dev/docs/build-options.html
[2] https://ardupilot.org/dev/docs/hwdef.html
[3] https://ardupilot.org/dev/docs/building-setup-linux.html
[4] https://ardupilot.org/dev/docs/code-overview-size-reduction.html
