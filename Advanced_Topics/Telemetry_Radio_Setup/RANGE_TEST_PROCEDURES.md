# Telemetry Radio Range Test Procedures

**Author:** Patrick Kelly (@Kuscko)

---

## Overview

Range testing validates maximum usable range, link quality at distance, interference robustness, and antenna performance.

**Test types:** Ground Range, Flight Range, Interference, Obstacle (NLOS).

**Safety:** Maintain visual line of sight, configure failsafe before flight, test in open area.

---

## Pre-Test Preparation

### Equipment Checklist

- [ ] Telemetry radio pair (ground + air)
- [ ] Flight controller with telemetry configured
- [ ] Laptop with Mission Planner/QGC
- [ ] Fully charged batteries
- [ ] GPS with clear sky view
- [ ] Notepad for recording results

### Radio Configuration

```bash
python3 sik_radio_config.py --port /dev/ttyUSB0 --baud 57600 --air-speed 64 --netid 25 --txpower 20 --ecc --mavlink
python3 sik_radio_config.py --port /dev/ttyUSB0  # Verify settings
```

**Recommended:** Serial baud 57600, Air speed 64 kbps, TX Power maximum (check regulations), ECC and MAVLink enabled.

### ArduPilot Configuration

```bash
SERIAL2_PROTOCOL,2        # MAVLink2
SERIAL2_BAUD,57           # 57600 baud
FS_LONG_ACTN,1            # RTL on long failsafe
FS_LONG_TIMEOUT,20
SR2_EXTRA1,2
SR2_EXTRA2,2
SR2_EXTRA3,1
SR2_POSITION,2
SR2_RAW_SENS,1
SR2_RC_CHAN,1
```

**Pre-Flight Verification:**

- Green LED solid on both radios (linked)
- Record RSSI baseline at 1m (should be > 200)
- GPS 3D fix, HDOP < 2.0, 8+ satellites
- Test failsafe: turn off ground radio, verify failsafe, restore

---

## Ground Range Test

### Step-by-Step Procedure

1. **Baseline (0-10m):** Record RSSI at 1m, 5m, 10m.
2. **Near range (10-100m):** Move vehicle to 25m, 50m, 100m. Record RSSI, send test command, verify ACK.
3. **Medium range (100-500m):** Continue at 150m, 200m, 300m, 400m, 500m. Note if RSSI drops below 100.
4. **Maximum range (500m+):** Continue until link lost. Walk back; record recovery distance.

### Data Logging Script

```python
#!/usr/bin/env python3
"""Log RSSI values during range test"""
import time
from pymavlink import mavutil

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()

print("Logging RSSI... Press Ctrl+C to stop")
print("Time,LocalRSSI,RemoteRSSI,Noise,RxErrors,Fixed")

try:
    while True:
        master.mav.request_data_stream_send(
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_EXTRA3,
            1, 1)

        msg = master.recv_match(type='RADIO_STATUS', blocking=True, timeout=2)
        if msg:
            print(f"{time.time()},{msg.rssi},{msg.remrssi},{msg.noise},{msg.rxerrors},{msg.fixed}")

        time.sleep(1)

except KeyboardInterrupt:
    print("\nLogging stopped")
```

### Link Quality Thresholds

| Quality  | RSSI    | Packet Loss | Notes                    |
| -------- | ------- | ----------- | ------------------------ |
| Good     | > 150   | 0%          | Smooth telemetry         |
| Marginal | 100-150 | < 5%        | Delayed ACKs possible    |
| Poor     | < 100   | > 10%       | Unreliable, do not fly   |

---

## Flight Range Test

### Mission Profile

1. Takeoff to 100m AGL
2. Fly straight away from home
3. Monitor RSSI continuously
4. Turn at planned distance, RSSI < 150, or link lost 5+ seconds
5. Return and land

### Auto Mission Example

```text
QGC WPL 110
0    1    0    16    0    0    0    0    -35.363261    149.165237    584.0    1
1    0    3    22    0    0    0    0    -35.363261    149.165237    100.0    1
2    0    3    16    0    0    0    0    -35.363261    149.170237    100.0    1
3    0    3    16    0    0    0    0    -35.363261    149.175237    100.0    1
4    0    3    16    0    0    0    0    -35.363261    149.165237    100.0    1
5    0    3    20    0    0    0    0    0              0              0        1
```

### Pre-Flight Setup

```bash
FS_LONG_ACTN,1
FS_LONG_TIMEOUT,10
LOG_BITMASK,65535
```

### In-Flight Actions

- If RSSI drops below 150: note distance, switch to LOITER/RTL.
- If link lost: vehicle triggers failsafe RTL; wait for return; link re-establishes.

---

## Interference Testing

1. Test in urban/RF-noisy environment (near WiFi, cell towers, other RC pilots)
2. Compare ground range results vs open-field baseline
3. Use spectrum analyzer to identify interference; adjust `MIN_FREQ`/`MAX_FREQ` to avoid busy bands
4. Verify different `NETID` values prevent interference between radio pairs

---

## Data Analysis

### RSSI vs. Distance Plot

```python
import matplotlib.pyplot as plt

distances = [10, 25, 50, 100, 150, 200, 300, 400, 500]
rssi = [250, 245, 238, 225, 210, 195, 175, 155, 130]

plt.plot(distances, rssi, 'b-o')
plt.xlabel('Distance (m)')
plt.ylabel('RSSI')
plt.title('Telemetry Radio Range Test')
plt.grid(True)
plt.axhline(y=150, color='r', linestyle='--', label='Warning threshold')
plt.axhline(y=100, color='orange', linestyle='--', label='Critical threshold')
plt.legend()
plt.savefig('rssi_range_test.png')
plt.show()
```

### Link Budget

```text
Path Loss (dB) = 20*log10(distance_m) + 20*log10(freq_MHz) + 32.45

For 915MHz at 1km:
  Path Loss = 60 + 59.2 + 32.45 = 151.65 dB

Link Margin = TX(20dBm) + TX_Gain(2dBi) + RX_Gain(2dBi) - Path_Loss - RX_Sensitivity(-117dBm)
            = 20 + 2 + 2 - 151.65 + 117 = -10.65 dB  → link will fail at 1km
```

Reduce air speed or increase TX power to improve margin.

**Target:** 200% range margin (if mission is 500m, reliable range should be 1000m).

---

## Troubleshooting

### Poor Range (< 500m with standard settings)

- Check antenna connections and orientation; try higher-gain antenna
- Increase TXPOWER to maximum legal level
- Reduce AIR_SPEED from 64 to 32 or 16 kbps
- Change NETID; test in different location; use spectrum analyzer

### Intermittent Link

- Secure radio and antenna; add vibration damping
- Route cables away from ESCs/motors; add ferrite beads
- Update SiK firmware (both radios must match)
- Check for overheating at high power

### Asymmetric Link

- Verify TX power settings match on both radios
- Ensure both antennas are same type and orientation
- Swap radios to isolate hardware failure

---

## Best Practices

- Mount radio away from motors/ESCs; keep antenna clear of carbon fiber
- Use vertical orientation for omnidirectional coverage
- Lower air speed = longer range (less throughput)
- Enable ECC and MAVLink framing
- Plan missions for 50% of tested range
- Re-test after any hardware changes

---

## Test Report Template

```text
TELEMETRY RADIO RANGE TEST REPORT
Date: __________  Tester: __________  Location: __________

EQUIPMENT:
Radio Model: __________  Firmware: __________  Antenna: __________

CONFIGURATION:
Serial Baud: __________  Air Speed: __ kbps  TX Power: __ dBm
Network ID: __________  ECC: Y/N  MAVLink: Y/N

GROUND TEST:
Max reliable range: ____m  RSSI at max: ____  Link lost at: ____m

FLIGHT TEST:
Max range: ____m  RSSI at max: ____  Failsafe triggered: Y/N

ENVIRONMENT: Weather: __________  RF Environment: Clean/Moderate/Noisy

CONCLUSION: Pass/Fail  Recommended mission range: ____m
```

---

- [SiK Radio Configuration](https://ardupilot.org/copter/docs/common-sik-telemetry-radio.html)
- [ArduPilot Telemetry](https://ardupilot.org/copter/docs/common-telemetry-landingpage.html)
