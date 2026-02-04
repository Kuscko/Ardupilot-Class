# OSD Configuration

## Overview

Master On-Screen Display (OSD) configuration in ArduPilot to overlay critical flight data directly onto FPV video feeds. OSD provides real-time flight information visible through goggles or monitors, essential for safe and effective FPV operations [1].

This module covers OSD hardware setup, screen layout design, parameter configuration, and customization for different mission profiles and vehicle types.

## Prerequisites

Before starting this module, you should have:

- Flight controller with OSD support (most modern flight controllers include OSD chips)
- FPV camera and video transmitter setup
- Basic understanding of ArduPilot parameters
- Mission Planner or QGroundControl for OSD configuration
- Optional: MinimOSD or other external OSD hardware

## What You'll Learn

By completing this module, you will:

- Configure OSD parameters for different video standards (NTSC/PAL)
- Design custom screen layouts for different flight modes
- Enable and position OSD elements (altitude, speed, battery, etc.)
- Customize OSD fonts and styles
- Configure warnings and alerts on OSD
- Switch between multiple OSD screens
- Troubleshoot common OSD issues

## Key Concepts

### OSD Architecture

ArduPilot OSD can be implemented in two ways [1]:

- **Integrated OSD:** Built into flight controller (MAX7456 chip or similar)
- **External OSD:** Separate hardware like MinimOSD connected via MAVLink
- **Digital OSD:** For DJI, HDZero, and other digital FPV systems

### OSD Elements

Common OSD elements [2]:

- **Attitude:** Artificial horizon, roll/pitch indicators
- **Navigation:** GPS coordinates, home direction, waypoint info
- **Telemetry:** Altitude, speed, distance, heading
- **Battery:** Voltage, current, remaining capacity
- **Status:** Flight mode, armed state, GPS satellites
- **Warnings:** Low battery, geofence, failsafe alerts

### Video Standards

OSD supports different video formats:

| Standard | Resolution | Frame Rate | Regions |
| -------- | ---------- | ---------- | ------- |
| NTSC | 720x480 | 60Hz | North America, Japan |
| PAL | 720x576 | 50Hz | Europe, Asia, Africa |

## Hands-On Practice

### Exercise 1: Enable and Configure OSD

Basic OSD setup:

```bash
# Start SITL with OSD simulation
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --osdmsp

# Enable OSD
param set OSD_TYPE 1              # 1=MAX7456, 2=SITL, 3=MSP
param set OSD_UNITS 1             # 0=metric, 1=imperial

# Set video format
param set OSD_FORMAT 0            # 0=NTSC, 1=PAL

# Enable OSD on multiple screens
param set OSD_SCREENS 3           # Screens available

param write
reboot
```

**Expected result:**
- OSD overlay appears on video feed
- Default elements visible (altitude, speed, battery)

### Exercise 2: Design Custom Screen Layout

Position OSD elements on screen:

```bash
# Screen coordinates: X (0-29), Y (0-15 for NTSC, 0-15 for PAL)
# Each element has position parameters: OSD#_<ELEMENT>_X and OSD#_<ELEMENT>_Y

# Configure Screen 1 (default flight screen)
# Altitude - top left
param set OSD1_ALTITUDE_X 2
param set OSD1_ALTITUDE_Y 2
param set OSD1_ALTITUDE_EN 1      # Enable element

# Battery voltage - top right
param set OSD1_BAT_VOLT_X 22
param set OSD1_BAT_VOLT_Y 2
param set OSD1_BAT_VOLT_EN 1

# Current - below battery voltage
param set OSD1_CURRENT_X 22
param set OSD1_CURRENT_Y 3
param set OSD1_CURRENT_EN 1

# Artificial horizon - center
param set OSD1_HORIZON_X 14
param set OSD1_HORIZON_Y 8
param set OSD1_HORIZON_EN 1

# GPS satellites - bottom left
param set OSD1_SATS_X 2
param set OSD1_SATS_Y 13
param set OSD1_SATS_EN 1

# Home direction - bottom center
param set OSD1_HOMEDIST_X 12
param set OSD1_HOMEDIST_Y 13
param set OSD1_HOMEDIST_EN 1

# Flight mode - bottom right
param set OSD1_FLTMODE_X 20
param set OSD1_FLTMODE_Y 13
param set OSD1_FLTMODE_EN 1

param write
```

**Layout tips:**
- Keep critical info in center field of view
- Place less critical data at edges
- Avoid cluttering center (obstructs view)
- Group related information together

### Exercise 3: Configure Multiple OSD Screens

Create different screens for different flight phases:

```bash
# Screen 1: Normal flight (already configured)

# Screen 2: Navigation/Mission screen
param set OSD2_ALTITUDE_EN 1
param set OSD2_ALTITUDE_X 2
param set OSD2_ALTITUDE_Y 2

# Waypoint info
param set OSD2_WPNUMBER_EN 1
param set OSD2_WPNUMBER_X 14
param set OSD2_WPNUMBER_Y 3

param set OSD2_WPDIST_EN 1
param set OSD2_WPDIST_X 14
param set OSD2_WPDIST_Y 4

# Crosstrack error
param set OSD2_CRSSHAIR_EN 1
param set OSD2_CRSSHAIR_X 14
param set OSD2_CRSSHAIR_Y 8

# Screen 3: Performance tuning screen
param set OSD3_PITCH_EN 1
param set OSD3_PITCH_X 2
param set OSD3_PITCH_Y 2

param set OSD3_ROLL_EN 1
param set OSD3_ROLL_X 2
param set OSD3_ROLL_Y 3

param set OSD3_THROTTLE_EN 1
param set OSD3_THROTTLE_X 2
param set OSD3_THROTTLE_Y 4

# Switch between screens using RC switch (channel 6)
param set OSD_SW_METHOD 1         # Use RC channel
param set OSD_CHAN 6              # RC channel for switching
param write
```

**Screen switching:**
- Low PWM (< 1300): Screen 1
- Mid PWM (1300-1700): Screen 2
- High PWM (> 1700): Screen 3

### Exercise 4: Configure Warnings and Alerts

Set up critical alerts on OSD:

```bash
# Battery warnings
param set OSD1_BAT_VOLT_EN 1
param set BATT_LOW_VOLT 10.5      # Warning voltage
param set BATT_CRT_VOLT 10.0      # Critical voltage

# Enable battery warning display
param set OSD1_BATUSED_EN 1       # Show mAh used
param set OSD1_BATUSED_X 14
param set OSD1_BATUSED_Y 2

# RSSI warning
param set OSD1_RSSI_EN 1
param set OSD1_RSSI_X 25
param set OSD1_RSSI_Y 2
param set RSSI_TYPE 1             # Enable RSSI

# GPS warning (flashing when <6 satellites)
param set OSD1_SATS_EN 1

# Altitude warning
param set OSD1_ALTITUDE_EN 1

# Flight mode changes (always visible)
param set OSD1_FLTMODE_EN 1

# Arming status
param set OSD1_ARMING_EN 1
param set OSD1_ARMING_X 14
param set OSD1_ARMING_Y 10

param write
```

**Expected behavior:**
- Battery voltage flashes when below threshold
- RSSI icon changes when signal weak
- GPS count flashes when insufficient satellites
- Arming status clearly visible before takeoff

### Exercise 5: Customize OSD Appearance

Fine-tune OSD display settings:

```bash
# Adjust overall brightness
param set OSD_W_BRIGHTNESS 3      # White level (0-3)
param set OSD_B_BRIGHTNESS 2      # Black level (0-3)

# Font style (requires custom font upload)
param set OSD_FONT 0              # Default font

# Units
param set OSD_UNITS 0             # 0=metric, 1=imperial, 2=SI

# Message display time
param set OSD_MSG_TIME 10         # Seconds to show messages

# Enable statistics on disarm
param set OSD1_STATS_EN 1         # Show flight stats after landing

param write
```

**Statistics shown on disarm:**
- Flight time
- Max altitude
- Max distance
- Max speed
- Total current used

### Exercise 6: Mission Planner OSD Configuration

Use Mission Planner's visual OSD designer:

**Steps:**
1. Connect to flight controller
2. CONFIG → Full Parameter List → OSD
3. Or use: Setup → Optional Hardware → OSD → OSD Screen Setup
4. Visual editor shows OSD layout
5. Drag elements to desired positions
6. Enable/disable elements with checkboxes
7. Write parameters to flight controller

**Advantages:**
- Visual real-time preview
- Easier than manual parameter entry
- Can test different layouts quickly
- Shows all available elements

### Exercise 7: Test OSD in SITL

Verify OSD configuration in simulation:

```bash
# Start SITL with OSD output
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --osdmsp

# In MAVProxy, view OSD
module load OSD

# Fly a mission and observe OSD updates
mode FBWA
arm throttle
# Fly around
# Watch OSD elements update in real-time

# Test screen switching (if configured)
rc 6 1000  # Screen 1
rc 6 1500  # Screen 2
rc 6 2000  # Screen 3
```

**Verify:**
- All enabled elements visible
- Positions correct
- Values update in real-time
- Warnings trigger appropriately
- Screen switching works

## Common Issues

### Issue 1: No OSD Display

**Symptoms:**
- Video feed shows but no OSD overlay
- Blank screen or static

**Solutions:**
```bash
# Check OSD enabled
param show OSD_TYPE
# Should be 1 (MAX7456) or 2 (SITL)

# Verify video standard matches camera
param show OSD_FORMAT
# 0=NTSC, 1=PAL - must match camera

# Check at least one element enabled
param show OSD1_*_EN
# Some should be 1

# Verify OSD chip power
# Check wiring for external OSD
# Ensure camera provides clean video signal
```

### Issue 2: Garbled or Flickering Display

**Symptoms:**
- OSD text corrupted or unreadable
- Flickering characters
- Partial display

**Solutions:**
```bash
# Adjust brightness levels
param set OSD_W_BRIGHTNESS 2
param set OSD_B_BRIGHTNESS 1

# Check video standard
param set OSD_FORMAT 0  # Try NTSC
# or
param set OSD_FORMAT 1  # Try PAL

# Update OSD firmware (external OSD)
# Check video signal quality
# Add ground plane isolation
# Use shielded video cables
```

### Issue 3: Elements Not Positioned Correctly

**Symptoms:**
- OSD elements cut off at screen edges
- Elements overlap
- Wrong positions

**Solutions:**
```bash
# NTSC: X=0-29, Y=0-12
# PAL: X=0-29, Y=0-15

# Reposition elements within bounds
param set OSD1_ALTITUDE_X 2   # X must be 0-29
param set OSD1_ALTITUDE_Y 2   # Y depends on video standard

# Use Mission Planner visual editor
# Verify video standard matches display

# For SITL, ensure --osdmsp flag used
```

### Issue 4: Missing or Incorrect Data

**Symptoms:**
- GPS shows 0 satellites
- Battery shows wrong voltage
- Speed or altitude stuck at 0

**Solutions:**
```bash
# GPS not enabled
param set OSD1_SATS_EN 1
param set OSD1_GSPEED_EN 1

# Battery monitoring not configured
param set BATT_MONITOR 4       # Enable battery monitor
param set BATT_VOLT_PIN 2
param set BATT_CURR_PIN 3

# Airspeed sensor required for some elements
param set ARSPD_TYPE 1         # Enable airspeed

# Verify sensors working in Mission Planner
# Check raw sensor data

param write
```

### Issue 5: OSD Screen Switching Not Working

**Symptoms:**
- Can't change OSD screens
- Stuck on one screen
- RC switch has no effect

**Solutions:**
```bash
# Verify multiple screens enabled
param set OSD_SCREENS 3        # Enable 3 screens

# Configure switching method
param set OSD_SW_METHOD 1      # RC switch
param set OSD_CHAN 6           # Use channel 6

# Test RC channel
rc 6 1000
rc 6 1500
rc 6 2000

# Alternative: use MAVLink commands
# Or disable switching if not needed
param set OSD_SW_METHOD 0
```

## OSD Element Reference

### Essential Flight Elements

| Element | Parameter | Purpose |
| ------- | --------- | ------- |
| Altitude | OSD#_ALTITUDE | Height above home |
| Airspeed | OSD#_ASPEED | Current airspeed |
| Ground speed | OSD#_GSPEED | Speed over ground |
| Battery voltage | OSD#_BAT_VOLT | Cell voltage |
| Current draw | OSD#_CURRENT | Current consumption |
| GPS satellites | OSD#_SATS | GPS fix quality |
| Flight mode | OSD#_FLTMODE | Current flight mode |
| Horizon | OSD#_HORIZON | Artificial horizon |

### Navigation Elements

| Element | Parameter | Purpose |
| ------- | --------- | ------- |
| Home direction | OSD#_HOMEDIR | Arrow to home |
| Home distance | OSD#_HOMEDIST | Distance to home |
| Waypoint number | OSD#_WPNUMBER | Current waypoint |
| Waypoint distance | OSD#_WPDIST | Distance to WP |
| Crosshair | OSD#_CRSSHAIR | Center reference |
| Wind | OSD#_WIND | Wind speed/direction |

### Status Elements

| Element | Parameter | Purpose |
| ------- | --------- | ------- |
| Arming status | OSD#_ARMING | Pre-arm checks |
| Messages | OSD#_MESSAGE | System messages |
| RSSI | OSD#_RSSI | Signal strength |
| Statistics | OSD#_STATS | Post-flight stats |

## Additional Resources

- [OSD Configuration Guide](https://ardupilot.org/plane/docs/common-osd-overview.html) [1] - Official OSD setup
- [OSD Parameter Reference](https://ardupilot.org/plane/docs/parameters.html#osd-parameters) [2] - Complete OSD parameters
- [Mission Planner OSD](https://ardupilot.org/planner/docs/common-mission-planner-osd.html) [3] - Visual OSD configuration
- [MinimOSD Setup](https://ardupilot.org/copter/docs/common-minim-osd-quick-installation-guide.html) - External OSD hardware

### OSD Customization

- [Custom Fonts](https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_OSD/fonts) - OSD font files
- [Digital OSD Integration](https://ardupilot.org/plane/docs/common-msp-osd-overview.html) - DJI/HDZero setup

## Next Steps

After mastering OSD configuration:

1. **FPV Racing Setup** - Optimize OSD for high-speed flight
2. **Long Range Configuration** - Design OSD for endurance missions
3. **Payload Integration** - Add payload status to OSD
4. **Telemetry Radio Setup** - Combine OSD with ground station telemetry

---

**Sources:**

[1] https://ardupilot.org/plane/docs/common-osd-overview.html
[2] https://ardupilot.org/plane/docs/parameters.html#osd-parameters
[3] https://ardupilot.org/planner/docs/common-mission-planner-osd.html
