# RC Calibration and Setup

## Overview

Master RC (Radio Control) calibration and setup for reliable manual and autonomous flight control in ArduPilot. Proper RC configuration is essential for safe operation, mode switching, and failsafe behavior [1].

This module covers RC receiver types, channel mapping, calibration procedures, failsafe configuration, and mode switch setup for real hardware deployments.

## Prerequisites

Before starting this module, you should have:

- RC transmitter and compatible receiver
- Flight controller with RC input capability
- Understanding of ArduPilot parameters
- Mission Planner or QGroundControl installed
- Basic knowledge of RC protocols (PWM, PPM, SBUS)

## What You'll Learn

By completing this module, you will:

- Understand RC receiver types and protocols
- Configure channel mapping (RCMAP_* parameters)
- Perform complete RC calibration procedure
- Set up RC failsafe behavior
- Configure flight mode switches
- Map auxiliary functions to channels
- Troubleshoot common RC issues

## Key Concepts

### RC Receiver Types

ArduPilot supports multiple receiver protocols [1]:

**PWM (Pulse Width Modulation):**
- Traditional single-wire-per-channel
- 50Hz update rate
- Requires one input pin per channel
- Simple, reliable, legacy

**PPM (Pulse Position Modulation):**
- Multiple channels on single wire
- 50Hz update rate
- Common on older systems

**SBUS (Serial Bus):**
- Digital protocol from FrSky
- 100Hz update rate
- 16 channels on single wire
- Inverted serial signal

**CRSF (Crossfire):**
- TBS Crossfire protocol
- High update rate (150Hz+)
- Long range capable
- Full telemetry support

**Other Protocols:**
- DSM/Spektrum
- IBUS (FlySky)
- SRXL
- GHST (ImmersionRC Ghost)

### Channel Mapping

Standard RC channel assignments [2]:

| Channel | Function | Typical Range |
| ------- | -------- | ------------- |
| 1 | Roll | 1000-2000 μs |
| 2 | Pitch | 1000-2000 μs |
| 3 | Throttle | 1000-2000 μs |
| 4 | Yaw | 1000-2000 μs |
| 5 | Flight Mode | 1000-2000 μs |
| 6 | Auxiliary 1 | 1000-2000 μs |
| 7 | Auxiliary 2 | 1000-2000 μs |
| 8 | Auxiliary 3 | 1000-2000 μs |

### Failsafe Behavior

RC failsafe triggers when signal lost [3]:

- **Return to Launch (RTL):** Navigate home and land
- **Land:** Descend and land at current location
- **Continue:** Maintain current mission
- **SmartRTL:** Return via safest path

## Hands-On Practice

### Exercise 1: Identify RC Receiver Type

Determine your receiver protocol:

```bash
# Connect to flight controller
# In Mission Planner or MAVProxy

# Check current RC protocol
param show SERIAL1_PROTOCOL
param show RC_PROTOCOLS

# Common values:
# SERIAL1_PROTOCOL = 23 for SBUS
# SERIAL1_PROTOCOL = 0 for PWM/PPM on dedicated pins

# Check which serial port receives RC
param show SERIAL1_BAUD
param show SERIAL2_BAUD

# For SBUS on SERIAL1
param set SERIAL1_PROTOCOL 23
param set SERIAL1_BAUD 100000  # SBUS baud rate
param set SERIAL1_OPTIONS 0    # Non-inverted

param write
reboot
```

**Physical connection check:**
- PWM: Multiple wires to individual RC pins
- PPM: Single wire to PPM input
- SBUS: Single wire to SERIAL port (usually marked RX)
- Check flight controller documentation for pinout

### Exercise 2: RC Calibration Procedure

Perform complete RC calibration:

**Using Mission Planner:**

1. **Initial Radio Calibration:**
   - Go to INITIAL SETUP → Mandatory Hardware → Radio Calibration
   - Click "Calibrate Radio"
   - Move all sticks and switches to extremes
   - Center all sticks
   - Click "Click when Done"

2. **Verify calibration:**
   - Check all channels show 1000-2000 μs range
   - Center should be ~1500 μs
   - Min should be ~1000 μs
   - Max should be ~2000 μs

**Manual parameter configuration:**

```bash
# Set RC input min/max/trim for each channel
# Example for Channel 1 (Roll)

param set RC1_MIN 1000      # Minimum PWM value
param set RC1_MAX 2000      # Maximum PWM value
param set RC1_TRIM 1500     # Center/neutral value
param set RC1_DZ 10         # Deadzone (μs)
param set RC1_REVERSED 0    # 0=normal, 1=reversed

# Repeat for all channels 1-8+
param set RC2_MIN 1000      # Pitch
param set RC2_MAX 2000
param set RC2_TRIM 1500

param set RC3_MIN 1000      # Throttle
param set RC3_MAX 2000
param set RC3_TRIM 1500

param set RC4_MIN 1000      # Yaw
param set RC4_MAX 2000
param set RC4_TRIM 1500

param write
```

**Expected results:**
- All channels respond correctly
- Full range of motion
- No reversed controls
- Center positions stable

### Exercise 3: Channel Mapping Configuration

Map RC channels to flight controller functions:

```bash
# Default mapping (Mode 2 transmitter)
param set RCMAP_ROLL 1      # Channel 1 = Roll
param set RCMAP_PITCH 2     # Channel 2 = Pitch
param set RCMAP_THROTTLE 3  # Channel 3 = Throttle
param set RCMAP_YAW 4       # Channel 4 = Yaw

# If your transmitter uses different layout (Mode 1):
# param set RCMAP_ROLL 1
# param set RCMAP_PITCH 3
# param set RCMAP_THROTTLE 2
# param set RCMAP_YAW 4

param write
reboot

# Verify mapping in Mission Planner
# Flight Data → Quick → Actions → Arm/Disarm
# Move sticks and verify correct response
```

**Common transmitter modes:**
- **Mode 1:** Throttle/Yaw on right, Roll/Pitch on left
- **Mode 2:** Throttle/Yaw on left, Roll/Pitch on right (most common)
- **Mode 3:** Throttle/Roll on right, Pitch/Yaw on left
- **Mode 4:** Throttle/Roll on left, Pitch/Yaw on right

### Exercise 4: Flight Mode Switch Configuration

Set up 3-6 flight modes on a switch:

```bash
# Configure mode channel (usually channel 5)
param set FLTMODE_CH 5

# Define flight modes for 6-position switch
# PWM ranges for each position

# Mode 1: Low PWM (<1230)
param set FLTMODE1 0        # 0 = STABILIZE

# Mode 2: (1230-1360)
param set FLTMODE2 2        # 2 = ALTHOLD

# Mode 3: (1360-1490)
param set FLTMODE3 3        # 3 = AUTO

# Mode 4: (1490-1620)
param set FLTMODE4 5        # 5 = LOITER

# Mode 5: (1620-1749)
param set FLTMODE5 9        # 9 = LAND

# Mode 6: High PWM (>1749)
param set FLTMODE6 6        # 6 = RTL

param write

# Test mode switching
# Move mode switch through all positions
# Verify correct mode displayed
```

**Common flight modes:**
| Mode Number | Name | Use Case |
| ----------- | ---- | -------- |
| 0 | STABILIZE | Manual flight with stabilization |
| 2 | ALTHOLD | Maintain altitude |
| 3 | AUTO | Autonomous mission |
| 4 | GUIDED | GCS control |
| 5 | LOITER | GPS hold position |
| 6 | RTL | Return to launch |
| 9 | LAND | Auto land |

### Exercise 5: Auxiliary Function Mapping

Map switches to auxiliary functions:

```bash
# Example: Arm/Disarm on channel 7
param set RC7_OPTION 153    # 153 = Arm/Disarm

# Common RC options:
# 153 = Arm/Disarm
# 9 = Camera Trigger
# 31 = Motor Emergency Stop
# 24 = Parachute Release
# 27 = Retract Mount

# Example: Camera trigger on channel 8
param set RC8_OPTION 9      # Camera trigger

# Example: Enable/disable fence on channel 6
param set RC6_OPTION 11     # Fence enable

# Emergency stop on channel 9
param set RC9_OPTION 31     # Motor emergency stop

param write
reboot
```

**Verify auxiliary functions:**
- Toggle switch
- Check corresponding action occurs
- Verify in Mission Planner status messages

### Exercise 6: RC Failsafe Configuration

Configure failsafe behavior for signal loss:

```bash
# Enable RC failsafe
param set FS_THR_ENABLE 1   # Enable throttle failsafe
param set FS_THR_VALUE 975  # PWM value indicating failsafe

# Failsafe action
param set FS_THR_ACTION 1   # 0=Continue, 1=RTL, 2=Land

# Timeout before failsafe triggers
param set FS_TIMEOUT 1.5    # Seconds (1.5s typical)

# GCS failsafe (telemetry loss)
param set FS_GCS_ENABLE 1   # Enable GCS failsafe
param set FS_GCS_TIMEOUT 5  # Seconds before trigger

param write

# Test failsafe (SAFELY!)
# 1. Arm vehicle in safe area
# 2. Turn off transmitter
# 3. Verify failsafe action triggers
# 4. Turn transmitter back on
# 5. Verify control restored
```

**Failsafe testing checklist:**
- Test on ground first
- Use kill switch nearby
- Verify correct failsafe action
- Test telemetry failsafe separately
- Document failsafe behavior

### Exercise 7: RC Range Testing

Verify RC range and link quality:

```bash
# Enable RSSI (Receiver Signal Strength Indicator)
param set RSSI_TYPE 1       # 1=Analog pin, 3=SBUS RSSI
param set RSSI_PIN 103      # Analog pin for RSSI
param set RSSI_CHAN 8       # Or channel with RSSI data

# Configure RSSI scaling
param set RSSI_CHAN_LOW 0   # PWM/voltage at min signal
param set RSSI_CHAN_HIGH 255 # PWM/voltage at max signal

param write

# Range test procedure:
# 1. Walk away from vehicle with transmitter
# 2. Monitor RSSI in telemetry
# 3. Note distance when RSSI drops below safe threshold
# 4. Test in all directions (obstructions)
# 5. Verify failsafe triggers at appropriate range
```

**Expected range:**
- 2.4GHz: 500m-1km (line of sight)
- 900MHz: 2-10km (long range systems)
- ELRS: 10-40km+ (extreme long range)
- RSSI should be > 50% at operational range

## Common Issues

### Issue 1: No RC Input Detected

**Symptoms:**
- Flight controller shows no RC channels
- "No RC receiver" message
- Cannot calibrate

**Solutions:**

```bash
# Check physical connections
# Verify receiver powered and bound to transmitter

# Check protocol configuration
param show SERIAL1_PROTOCOL
param set SERIAL1_PROTOCOL 23  # For SBUS

# For PWM/PPM receivers
param show BRD_PWM_COUNT
param set BRD_PWM_COUNT 8      # Enable PWM inputs

# Check RC protocol enabled
param show RC_PROTOCOLS
param set RC_PROTOCOLS 1       # Enable all protocols

# Reboot after protocol changes
param write
reboot

# Verify receiver LED indicates binding
# Check receiver manual for binding procedure
```

### Issue 2: Reversed Controls

**Symptoms:**
- Controls work opposite direction
- Roll left causes right roll
- Forward pitch causes backward pitch

**Solutions:**

```bash
# Reverse individual channel
param show RC1_REVERSED
param set RC1_REVERSED 1       # 1 = reversed

# Or fix in transmitter settings (preferred)
# Transmitter: Reverse servo output for channel

# Verify all channels:
# - Roll right stick = vehicle rolls right
# - Pitch forward stick = vehicle pitches forward
# - Yaw right stick = vehicle yaws right
# - Throttle up stick = throttle increases
```

### Issue 3: Noisy or Jittery RC Input

**Symptoms:**
- RC values jump around
- Erratic servo movements
- Difficult to control

**Solutions:**

```bash
# Increase RC deadzone
param set RC1_DZ 20            # Increase from 10 to 20
param set RC2_DZ 20
param set RC3_DZ 20
param set RC4_DZ 20

# Add RC filtering
param set RC_FILT 50           # Enable RC filter (Hz)

# Check for:
# - EMI from motors/ESCs
# - Poor receiver antenna placement
# - Low receiver voltage
# - Interference from 2.4GHz WiFi

# Use ferrite beads on receiver wires
# Keep receiver away from ESCs and motors
```

### Issue 4: Mode Switch Not Working

**Symptoms:**
- Flight mode doesn't change
- Stuck in one mode
- Random mode changes

**Solutions:**

```bash
# Verify mode channel
param show FLTMODE_CH
param set FLTMODE_CH 5         # Use channel 5

# Check channel 5 calibration
param show RC5_MIN
param show RC5_MAX
# Should span full range 1000-2000

# Re-calibrate channel 5
# Move mode switch through all positions

# Adjust mode PWM boundaries if needed
# Ensure switch positions correspond to mode ranges

# Test each position:
rc 5 1100  # Should trigger FLTMODE1
rc 5 1300  # Should trigger FLTMODE2
rc 5 1500  # Should trigger FLTMODE3
# etc.
```

### Issue 5: Failsafe Not Triggering

**Symptoms:**
- Transmitter off, vehicle continues flying
- No failsafe action when expected
- Failsafe triggers too early/late

**Solutions:**

```bash
# Check failsafe enabled
param show FS_THR_ENABLE
param set FS_THR_ENABLE 1

# Verify failsafe PWM value
param show FS_THR_VALUE
# Should be below normal throttle range
param set FS_THR_VALUE 975     # Below 1000

# Check receiver failsafe configuration
# Most receivers can be programmed for failsafe output
# Set receiver to output <975 μs on signal loss

# Test failsafe value
# In Mission Planner, watch RC3 (throttle) value
# Turn off transmitter
# RC3 should drop to FS_THR_VALUE or below

# Adjust failsafe action if needed
param set FS_THR_ACTION 1      # RTL
```

## Advanced RC Configuration

### Transmitter Mixing

Configure transmitter for advanced control:

**Elevon Mixing (Flying Wing):**
```bash
# In ArduPilot (preferred method)
param set MIXING_GAIN 0.5      # Elevon mixing
param set SERVO1_FUNCTION 77   # Left elevon
param set SERVO2_FUNCTION 78   # Right elevon

# Or configure in transmitter
# Mix: Aileron + Elevator → Servo 1
# Mix: Aileron - Elevator → Servo 2
```

**V-Tail Mixing:**
```bash
# In ArduPilot
param set SERVO1_FUNCTION 73   # Left V-tail
param set SERVO2_FUNCTION 74   # Right V-tail

# Mixing handled automatically by ArduPilot
```

### Expo and Dual Rates

Adjust control sensitivity:

```bash
# ArduPilot expo on RC inputs
param set RC1_DZ 30            # Larger deadzone = more expo feel

# Better: Configure in transmitter
# Expo: 30-50% for smooth flight
# Dual rates:
#   - Rate 1: 100% (acro/sport)
#   - Rate 2: 60-70% (precision/video)
```

### Channel Scaling

Custom scaling for non-standard ranges:

```bash
# If receiver outputs 800-2200 instead of 1000-2000
param set RC1_MIN 800
param set RC1_MAX 2200
param set RC1_TRIM 1500

# ArduPilot will scale appropriately
```

## RC Troubleshooting Workflow

```bash
# 1. Check physical connections
#    - Receiver power LED on
#    - Receiver bound to transmitter
#    - Correct pins connected

# 2. Verify protocol
param show SERIAL1_PROTOCOL
param show RC_PROTOCOLS

# 3. Calibrate RC
#    - Mission Planner → Radio Calibration
#    - Move all sticks to extremes

# 4. Test in Mission Planner
#    - Flight Data → Quick
#    - Verify all channels respond

# 5. Configure modes and aux functions
param show FLTMODE_CH
param show RC7_OPTION

# 6. Test failsafe
#    - Safe environment
#    - Turn off transmitter
#    - Verify correct action

# 7. Range test
#    - Walk away with transmitter
#    - Monitor RSSI
#    - Note failsafe distance
```

## Additional Resources

- [Radio Control Setup](https://ardupilot.org/copter/docs/common-radio-control-calibration.html) [1] - Official RC calibration guide
- [RC Input Protocols](https://ardupilot.org/copter/docs/common-rc-systems.html) [2] - Supported RC protocols
- [Failsafe Configuration](https://ardupilot.org/copter/docs/radio-failsafe.html) [3] - Failsafe setup guide
- [Auxiliary Functions](https://ardupilot.org/copter/docs/common-auxiliary-functions.html) - RC_OPTIONS reference

### Transmitter Setup Guides

- [OpenTX Setup](https://ardupilot.org/copter/docs/common-opentx.html) - FrSky transmitter configuration
- [Spektrum Setup](https://ardupilot.org/copter/docs/common-spektrum-rc.html) - Spektrum binding and setup

## Next Steps

After mastering RC calibration:

1. **Flight Mode Tuning** - Optimize flight characteristics per mode
2. **Advanced Failsafe** - SmartRTL and custom failsafe logic
3. **Telemetry Integration** - Display flight data on transmitter
4. **Redundant RC Systems** - Backup RC links for reliability

---

**Sources:**

[1] https://ardupilot.org/copter/docs/common-radio-control-calibration.html
[2] https://ardupilot.org/copter/docs/common-rc-systems.html
[3] https://ardupilot.org/copter/docs/radio-failsafe.html
