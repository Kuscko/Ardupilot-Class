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

```text
SERIAL_SPEED: 57 (57600 baud)
AIR_SPEED: 64 (64 kbps)
NETID: 25 (network ID, must match pair)
TXPOWER: 20 (20 dBm, max for most regions)
ECC: 1 (enable error correction)
MAVLINK: 1 (enable MAVLink framing)
```

### Advanced Settings

```text
MIN_FREQ: 915000 (US), 433000 (EU)
MAX_FREQ: 928000 (US), 435000 (EU)
NUM_CHANNELS: 50
DUTY_CYCLE: 100 (percentage)
LBT_RSSI: 0 (listen before talk threshold)
```

### Apply Settings

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

**Factors:** Antenna type, terrain/obstacles, interference (WiFi), power level.

## Troubleshooting

**No connection:** Check baud rates match (autopilot & radio), verify NETID matches on both radios, check frequencies are legal for region.

**Short range:** Increase TXPOWER (check local regulations), use better antennas, check antenna orientation, reduce AIR_SPEED.

**Lost packets:** Reduce AIR_SPEED, enable ECC, check for interference, move ground station.

**Author:** Patrick Kelly (@Kuscko)
