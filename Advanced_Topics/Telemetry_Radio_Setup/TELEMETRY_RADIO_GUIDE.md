# Telemetry Radio Setup Guide (SiK Radios)

## Hardware Setup

**Air Radio:** Connect to autopilot TELEM1/2 port
**Ground Radio:** Connect to laptop USB

## Firmware Update

**Using Mission Planner:**
1. Initial Setup → Optional Hardware → SiK Radio
2. Connect ground radio to USB
3. Click "Upload Firmware (Local)"
4. Wait for completion
5. Repeat for air radio

## Configuration

### Basic Settings

```
SERIAL_SPEED: 57 (57600 baud)
AIR_SPEED: 64 (64 kbps)
NETID: 25 (network ID, must match pair)
TXPOWER: 20 (20 dBm, max for most regions)
ECC: 1 (enable error correction)
MAVLINK: 1 (enable MAVLink framing)
```

### Advanced Settings

```
MIN_FREQ: 915000 (US), 433000 (EU)
MAX_FREQ: 928000 (US), 435000 (EU)
NUM_CHANNELS: 50
DUTY_CYCLE: 100 (percentage)
LBT_RSSI: 0 (listen before talk threshold)
```

### Apply Settings

**In Mission Planner:**
1. Load settings from radio
2. Modify as needed
3. Click "Save Settings"
4. Repeat for paired radio

## Range Testing

**Mission Planner:**
1. Connect to vehicle
2. Walk away with laptop
3. Monitor RSSI (signal strength)
4. Note max range before dropouts

**Expected range:**
- 100mW (20dBm): 300-500m
- 500mW (27dBm): 1-2km  
- 1W (30dBm): 2-5km

**Factors:**
- Antenna type/quality
- Terrain/obstacles
- Interference (2.4GHz WiFi, etc.)
- Power level

## Troubleshooting

**No connection:**
- Check baud rates match (autopilot & radio)
- Verify NETID matches on both radios
- Check frequencies are legal for region

**Short range:**
- Increase TXPOWER (check local regulations)
- Use better antennas
- Check antenna orientation
- Reduce AIR_SPEED (improves range)

**Lost packets:**
- Reduce AIR_SPEED
- Enable ECC
- Check for interference
- Move ground station

**Author:** Patrick Kelly (@Kuscko)
