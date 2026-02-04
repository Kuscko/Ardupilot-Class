# Telemetry Radio Setup

## Overview

Master telemetry radio configuration and troubleshooting for reliable long-range communication between ground control station and ArduPilot vehicles. Telemetry radios provide real-time monitoring, parameter adjustment, and command capability essential for safe autonomous operations [1].

This module covers SiK radio firmware, range testing, power optimization, frequency selection, and link quality troubleshooting.

## Prerequisites

Before starting this module, you should have:

- Telemetry radio pair (e.g., SiK radios, RFD900, Holybro)
- Flight controller with telemetry port
- Ground control station (laptop with Mission Planner)
- Understanding of serial protocols
- Basic RF (radio frequency) knowledge

## What You'll Learn

By completing this module, you will:

- Configure and update SiK radio firmware
- Optimize radio parameters for range and throughput
- Perform systematic range testing
- Select appropriate frequencies and avoid interference
- Troubleshoot link quality and connection issues
- Configure MAVLink streaming rates
- Set up redundant telemetry links

## Key Concepts

### Telemetry Radio Types

Common telemetry systems [1]:

**SiK Radios (Si1000 chipset):**
- 915MHz (Americas) or 433MHz (Europe/Asia)
- Open-source firmware
- 1-40km range typical
- Frequency hopping for reliability

**RFD900 Series:**
- High-power long-range
- 10-60km range
- Configurable output power
- Advanced error correction

**Holybro/Radiolink:**
- Integrated solutions
- Various frequencies
- Pre-configured for ArduPilot

**LTE/4G Telemetry:**
- Cellular network based
- Unlimited range (with coverage)
- Higher latency
- Requires data plan

### Link Budget

RF link considerations [2]:

| Factor | Impact | Notes |
| ------ | ------ | ----- |
| TX Power | Higher = longer range | Regulatory limits apply |
| Antenna Gain | Higher = longer range | Directional trade-off |
| Frequency | Lower = better penetration | 433MHz vs 915MHz |
| Baud Rate | Lower = longer range | Speed vs range trade-off |
| Interference | Reduces range | Avoid WiFi, Bluetooth |

### MAVLink Streaming

Telemetry data rates [3]:

- **SR0_EXTRA1:** Attitude data (roll, pitch, yaw)
- **SR0_EXTRA2:** VFR_HUD (airspeed, groundspeed, heading)
- **SR0_EXTRA3:** AHRS, HWSTATUS, SYSTEM_TIME
- **SR0_POSITION:** Global position, GPS data
- **SR0_RC_CHAN:** RC channel values

## Hands-On Practice

### Exercise 1: Firmware Update and Configuration

Update SiK radio firmware for latest features:

**Using Mission Planner:**

1. Connect air radio to flight controller
2. Connect ground radio to PC via USB
3. Mission Planner → INITIAL SETUP → Optional Hardware → SiK Radio
4. Click "Upload Firmware (Local)"
5. Select latest firmware file
6. Wait for upload to complete

**Configure radio parameters:**

```bash
# In Mission Planner SiK Radio config screen

# Basic settings
SERIAL_SPEED: 57      # 57600 baud (match SERIAL2_BAUD)
AIR_SPEED: 64         # Air data rate (64 = optimal)
NETID: 25             # Network ID (unique per radio pair)

# Range optimization
TXPOWER: 20           # TX power (20 = 100mW, max depends on model)
ECC: 1                # Error correction (1 = enabled)
MAVLINK: 1            # MAVLink framing (1 = enabled)

# Advanced
NUM_CHANNELS: 50      # Frequency hopping channels
DUTY_CYCLE: 100       # % time transmitting (100 = full duplex)
MAX_WINDOW: 131       # Max packet window size

# Click "Save Settings" for both radios
```

### Exercise 2: Serial Port Configuration

Configure ArduPilot serial ports for telemetry:

```bash
# Connect to flight controller
# In Mission Planner or MAVProxy

# Configure SERIAL2 for telemetry (most common)
param set SERIAL2_PROTOCOL 2      # 2 = MAVLink2
param set SERIAL2_BAUD 57         # 57600 baud (match radio)

# Alternative: SERIAL1 for telemetry
param set SERIAL1_PROTOCOL 2
param set SERIAL1_BAUD 57

# Enable MAVLink2 protocol (recommended)
param set SERIAL2_OPTIONS 0       # 0 = default

param write
reboot
```

**Verify telemetry connection:**

```bash
# Check link status in Mission Planner
# Flight Data screen shows:
# - Link quality (should be > 80%)
# - Packets received
# - RSSI (signal strength)

# In MAVProxy:
link
# Shows active MAVLink connections
```

### Exercise 3: Optimize MAVLink Streaming Rates

Balance data rate and bandwidth:

```bash
# Default rates (good for most applications)
param set SR0_EXTRA1 4        # Attitude at 4Hz
param set SR0_EXTRA2 4        # VFR_HUD at 4Hz
param set SR0_EXTRA3 2        # AHRS at 2Hz
param set SR0_POSITION 2      # Position at 2Hz
param set SR0_RC_CHAN 2       # RC channels at 2Hz
param set SR0_RAW_SENS 2      # Raw sensors at 2Hz
param set SR0_RAW_CTRL 2      # Control at 2Hz

# Long-range (reduced bandwidth)
param set SR0_EXTRA1 2        # Reduce all rates
param set SR0_EXTRA2 2
param set SR0_EXTRA3 1
param set SR0_POSITION 1
param set SR0_RC_CHAN 1

# High-bandwidth (local testing)
param set SR0_EXTRA1 10       # Increase for smoother display
param set SR0_EXTRA2 10
param set SR0_EXTRA3 4
param set SR0_POSITION 4

param write
```

**Monitor bandwidth usage:**

```bash
# In Mission Planner
# Flight Data → Status → Messages/sec
# Should be < radio air speed (e.g., < 64kbps)

# Reduce rates if:
# - Link quality drops
# - Packet loss increases
# - Radio buffer overruns occur
```

### Exercise 4: Range Testing Procedure

Systematically test radio range:

**Preparation:**

```bash
# Set radio to max legal power
# In Mission Planner SiK Radio config:
TXPOWER: 30    # Check local regulations (100mW typical max)

# Enable RSSI on OSD or telemetry
param set RSSI_TYPE 3          # 3 = Receiver RSSI
param set RSSI_PIN -1          # -1 = use MAVLink RSSI

# Configure low RSSI warning
param set RSSI_CHAN_LOW 50     # Warning at 50% signal
```

**Range test protocol:**

1. **Static test (baseline):**
   - Place ground radio at test location
   - Walk with air radio (or vehicle)
   - Monitor RSSI and link quality
   - Note distance when quality drops below 70%

2. **Line-of-sight test:**
   - Open field, no obstacles
   - Gradually increase distance
   - Record RSSI at 100m intervals
   - Note maximum range

3. **Obstacle test:**
   - Test through buildings, trees
   - Note range reduction
   - Identify dead zones

4. **Flight test:**
   - Fly actual mission profile
   - Monitor link throughout
   - Verify adequate margin

**Expected ranges (typical):**

```
100mW SiK radios (915MHz):
- Line of sight: 1-3km
- Light obstacles: 500m-1km
- Urban environment: 200-500m

1W RFD900 radios:
- Line of sight: 10-40km
- Light obstacles: 5-10km
- Urban environment: 2-5km
```

### Exercise 5: Frequency Selection and Interference

Avoid RF interference:

```bash
# Check frequency settings
# In Mission Planner SiK Radio config

MIN_FREQ: 915000      # Minimum frequency (kHz)
MAX_FREQ: 928000      # Maximum frequency (kHz)
NUM_CHANNELS: 50      # Hopping channels

# For 433MHz radios:
MIN_FREQ: 433050
MAX_FREQ: 434790
NUM_CHANNELS: 50

# Avoid interference sources:
# - WiFi (2.4GHz) - use 433MHz or 915MHz
# - Bluetooth (2.4GHz)
# - RC transmitters (2.4GHz or 900MHz)
# - Video transmitters (5.8GHz, 1.2GHz)
# - LTE bands (check your region)
```

**Spectrum analysis:**

```bash
# Use spectrum analyzer app or hardware
# Identify clean frequency bands
# Configure radio to use clear channels

# Adjust MIN_FREQ and MAX_FREQ to avoid busy bands
# Example: Avoid 915-920MHz if interference present
MIN_FREQ: 920000
MAX_FREQ: 928000
```

### Exercise 6: Multi-Radio Redundancy

Set up backup telemetry links:

```bash
# Primary telemetry: SiK radio on SERIAL2
param set SERIAL2_PROTOCOL 2
param set SERIAL2_BAUD 57

# Secondary telemetry: WiFi or LTE on SERIAL4
param set SERIAL4_PROTOCOL 2
param set SERIAL4_BAUD 921      # 921600 baud for WiFi

# Third telemetry: USB connection
# Automatically configured

param write
reboot
```

**Mission Planner multi-link setup:**

1. Connect to primary radio (USB)
2. Ctrl+L to add link
3. Connect to secondary radio (TCP/IP)
4. Both links active simultaneously
5. Mission Planner uses best available link

**Expected behavior:**
- Seamless failover between links
- Continue operation if one link fails
- Higher reliability for critical missions

### Exercise 7: Troubleshooting Link Issues

Diagnose and fix common problems:

**Poor link quality test:**

```python
# link_quality_monitor.py
from pymavlink import mavutil
import time

master = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)
master.wait_heartbeat()

print("Monitoring link quality...")
print("Press Ctrl+C to stop\n")

try:
    while True:
        # Request radio status
        master.mav.request_data_stream_send(
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_ALL,
            10, 1)

        # Receive radio status
        msg = master.recv_match(type='RADIO_STATUS', blocking=True, timeout=2)

        if msg:
            rssi_local = msg.rssi
            rssi_remote = msg.remrssi
            noise_local = msg.noise
            noise_remote = msg.remnoise
            rxerrors = msg.rxerrors

            snr_local = rssi_local - noise_local
            snr_remote = rssi_remote - noise_remote

            print(f"Local RSSI: {rssi_local} dBm, SNR: {snr_local} dB")
            print(f"Remote RSSI: {rssi_remote} dBm, SNR: {snr_remote} dB")
            print(f"RX Errors: {rxerrors}")
            print(f"Link Quality: {(255 - rxerrors) / 255 * 100:.1f}%\n")

        time.sleep(1)

except KeyboardInterrupt:
    print("\nMonitoring stopped")
```

## Common Issues

### Issue 1: No Telemetry Connection

**Symptoms:**
- Mission Planner won't connect
- No data received
- Radio LEDs not synchronized

**Solutions:**

```bash
# Check physical connections
# - Radio powered (LED on)
# - Serial cable connected correctly
# - TX/RX not swapped

# Verify baud rates match
# Radio config: SERIAL_SPEED = 57 (57600)
# ArduPilot: SERIAL2_BAUD = 57

# Check COM port (Windows)
# Device Manager → Ports
# Note COM port number (e.g., COM3)

# Try different USB port
# Some USB ports have driver issues

# Reset radio to defaults
# Hold button while powering on
# Reconfigure from scratch
```

### Issue 2: Poor Link Quality

**Symptoms:**
- Frequent disconnections
- High packet loss
- Low RSSI (<50)

**Solutions:**

```bash
# Increase TX power
TXPOWER: 30    # Maximum legal power

# Reduce data rates
param set SR0_EXTRA1 2
param set SR0_EXTRA2 2
param set SR0_POSITION 1

# Lower air speed (better range)
AIR_SPEED: 32   # Reduce from 64

# Enable error correction
ECC: 1

# Check antenna connections
# - Antennas secured
# - No damage to cables
# - Ground plane for monopole antennas

# Avoid interference
# - Turn off WiFi
# - Distance from power lines
# - Clear line of sight
```

### Issue 3: Intermittent Connection

**Symptoms:**
- Connection drops randomly
- Works sometimes, fails other times
- Inconsistent behavior

**Solutions:**

```bash
# Check for interference
# Use spectrum analyzer
# Change frequency band if needed

# Verify power supply
# Radio needs stable voltage
# Check for voltage drops during TX

# Update firmware
# Latest SiK firmware fixes bugs
# Both radios must match versions

# Check for overheating
# Radios can overheat at high power
# Add cooling/ventilation

# Inspect antenna
# Poor antenna can cause intermittent issues
# Try different antenna
```

### Issue 4: Short Range

**Symptoms:**
- Range much less than expected
- Connection lost at short distance
- RSSI drops quickly

**Solutions:**

```bash
# Verify TX power setting
TXPOWER: 30    # Should be max

# Check antenna type and orientation
# Omnidirectional vs directional
# Vertical polarization typical

# Test with different antennas
# Higher gain antenna extends range
# 3-5 dBi antennas common

# Reduce baud rate
AIR_SPEED: 32   # Slower = longer range

# Enable all range optimizations
ECC: 1
MAVLINK: 1
DUTY_CYCLE: 100

# Check frequency
# 433MHz has longer range than 915MHz
# But may have more interference
```

### Issue 5: Radio Configuration Lost

**Symptoms:**
- Settings revert to defaults
- Radio not saving configuration
- Needs reconfiguration every boot

**Solutions:**

```bash
# Ensure "Save Settings" clicked in Mission Planner
# Both air and ground radios

# Check firmware version
# Old firmware may have save bugs
# Update to latest version

# Power cycle after save
# Disconnect power for 10 seconds
# Reconnect and verify settings retained

# Replace radio if persistent
# Flash memory may be faulty
# Hardware issue
```

## Advanced Telemetry Configuration

### Directional Antenna Setup

```bash
# For long-range operations
# Use directional antenna on ground
# Omnidirectional on vehicle

# Antenna options:
# - Yagi (10-15 dBi gain, narrow beam)
# - Patch (6-9 dBi gain, medium beam)
# - Helical (12-16 dBi gain, circular polarization)

# Antenna tracker for auto-pointing
param set SERIAL3_PROTOCOL 1      # GPS on SERIAL3
# Connect antenna tracker to mission planner
# Tracker follows vehicle automatically
```

### Encryption and Security

```bash
# Enable AES encryption (if supported)
# In SiK radio configuration:

# Not available on all radios
# Check firmware capabilities

# Alternative: VPN tunnel for network telemetry
# Secure MAVLink over LTE/WiFi
```

### Telemetry Relay

```bash
# Vehicle-to-vehicle relay
# Vehicle 1 has long-range radio
# Vehicle 2 uses Vehicle 1 as relay

# Configure SERIAL port for relay
param set SERIAL4_PROTOCOL 2    # MAVLink
# Connect vehicles via short-range link
# Mission Planner connects to Vehicle 1
# Can control both vehicles
```

## Telemetry Performance Optimization

```bash
# Optimal configuration for 915MHz SiK radios

# Radio settings (Mission Planner):
SERIAL_SPEED: 57      # 57600 baud
AIR_SPEED: 64         # 64kbps air rate
NETID: 25             # Unique network ID
TXPOWER: 20           # 100mW (or max legal)
ECC: 1                # Error correction on
MAVLINK: 1            # MAVLink framing on
NUM_CHANNELS: 50      # Full hopping spread
DUTY_CYCLE: 100       # Full duplex
MAX_WINDOW: 131       # Max window size

# ArduPilot settings:
param set SERIAL2_PROTOCOL 2
param set SERIAL2_BAUD 57

# Streaming rates (balanced):
param set SR0_EXTRA1 4
param set SR0_EXTRA2 4
param set SR0_EXTRA3 2
param set SR0_POSITION 2
param set SR0_RC_CHAN 2
param set SR0_RAW_SENS 1
param set SR0_RAW_CTRL 1

# Expected performance:
# - Range: 1-3km line of sight
# - Link quality: >90% at normal range
# - Latency: <100ms
# - Packet loss: <5%
```

## Additional Resources

- [Telemetry Radio Overview](https://ardupilot.org/copter/docs/common-telemetry-landingpage.html) [1] - Complete telemetry guide
- [SiK Radio Configuration](https://ardupilot.org/copter/docs/common-sik-telemetry-radio.html) [2] - SiK radio setup
- [RFD900 Setup](https://ardupilot.org/copter/docs/common-rfd900.html) - RFD900 configuration
- [MAVLink Streaming](https://ardupilot.org/dev/docs/mavlink-basics.html) [3] - MAVLink protocol details

### Regulatory Information

- [FCC Regulations (USA)](https://www.fcc.gov/) - 915MHz band rules
- [CE Regulations (Europe)](https://ec.europa.eu/) - 433MHz and 868MHz
- [Radio Regulations by Country](https://ardupilot.org/copter/docs/common-telemetry-radio-regional-regulations.html) - Frequency restrictions

## Next Steps

After mastering telemetry radio setup:

1. **LTE/4G Telemetry** - Cellular-based unlimited range
2. **Satellite Telemetry** - Iridium for truly global coverage
3. **Antenna Tracking** - Auto-pointing antennas for long range
4. **Mesh Networks** - Multi-vehicle communication networks

---

**Sources:**

[1] https://ardupilot.org/copter/docs/common-telemetry-landingpage.html
[2] https://ardupilot.org/copter/docs/common-sik-telemetry-radio.html
[3] https://ardupilot.org/dev/docs/mavlink-basics.html
