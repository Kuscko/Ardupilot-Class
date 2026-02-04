# Telemetry Radio Range Test Procedures

Comprehensive procedures for testing and validating telemetry radio range and link quality.

**Author:** Patrick Kelly (@Kuscko)
**Version:** 1.0
**Last Updated:** 2026-02-03

---

## Table of Contents

1. [Overview](#overview)
2. [Pre-Test Preparation](#pre-test-preparation)
3. [Ground Range Test](#ground-range-test)
4. [Flight Range Test](#flight-range-test)
5. [Interference Testing](#interference-testing)
6. [Data Analysis](#data-analysis)
7. [Troubleshooting](#troubleshooting)

---

## Overview

### Purpose

Range testing validates:
- Maximum usable range for telemetry link
- Link quality at various distances
- Robustness to interference
- Antenna performance
- Power setting effectiveness

### Test Types

1. **Ground Range Test**: Quick validation on the ground (line of sight)
2. **Flight Range Test**: Real-world validation during flight
3. **Interference Test**: Validation in RF-noisy environments
4. **Obstacle Test**: Non-line-of-sight performance

### Safety Requirements

- Always maintain visual line of sight during flight tests
- Have safety pilot ready to take manual control
- Test in open area away from people and property
- Follow local regulations for radio transmissions
- Ensure failsafe settings are configured properly

---

## Pre-Test Preparation

### Equipment Checklist

**Required:**
- [ ] Telemetry radio pair (ground + air)
- [ ] Flight controller with telemetry configured
- [ ] Laptop with Mission Planner/QGC
- [ ] Fully charged batteries (vehicle + laptop)
- [ ] GPS with clear sky view
- [ ] Measuring tape or GPS distance app
- [ ] Notepad for recording results

**Optional:**
- [ ] Spectrum analyzer (for interference analysis)
- [ ] RSSI logger script
- [ ] Second person for distance measurement
- [ ] Walkie-talkies for coordination
- [ ] Camera to document test setup

### Radio Configuration

```bash
# Configure both radios identically
python3 sik_radio_config.py --port /dev/ttyUSB0 --baud 57600 --air-speed 64 --netid 25 --txpower 20 --ecc --mavlink

# Verify settings on both radios
python3 sik_radio_config.py --port /dev/ttyUSB0
python3 sik_radio_config.py --port /dev/ttyUSB1  # Air radio (if accessible)
```

**Recommended Settings for Range Testing:**
- Serial baud: 57600
- Air speed: 64 kbps (or lower for longer range)
- Network ID: Unique value (avoid 25 if others nearby)
- TX Power: Maximum (check local regulations)
- ECC: Enabled
- MAVLink: Enabled

### ArduPilot Configuration

```bash
# Configure telemetry port (example: SERIAL2 for TELEM2 port)
SERIAL2_PROTOCOL,2        # MAVLink2
SERIAL2_BAUD,57          # 57600 baud

# Configure failsafe for lost link
FS_LONG_ACTN,1           # RTL on long failsafe
FS_LONG_TIMEOUT,20       # 20 seconds

# Reduce telemetry stream rates to extend range
SR2_EXTRA1,2             # Attitude at 2 Hz
SR2_EXTRA2,2             # VFR_HUD at 2 Hz
SR2_EXTRA3,1             # AHRS at 1 Hz
SR2_POSITION,2           # Global position at 2 Hz
SR2_RAW_SENS,1           # Raw sensors at 1 Hz
SR2_RC_CHAN,1            # RC channels at 1 Hz
```

### Pre-Flight Checks

1. **Radio Connection:**
   - Green LED solid on both radios (linked)
   - Mission Planner shows heartbeat
   - Can receive telemetry data

2. **RSSI Baseline:**
   - Record RSSI at 1 meter distance
   - Should be >200 (max 255)

3. **GPS Lock:**
   - GPS has 3D fix
   - HDOP < 2.0
   - 8+ satellites

4. **Failsafe Test:**
   - Turn off ground radio
   - Verify vehicle enters failsafe mode
   - Turn on ground radio
   - Verify failsafe clears

---

## Ground Range Test

### Procedure Overview

Test telemetry link range with vehicle stationary on the ground.

### Test Setup

```
    [Ground Station]  <--- distance --->  [Vehicle]
         |                                    |
    Ground Radio                          Air Radio
```

**Location Requirements:**
- Flat, open area (field, parking lot)
- Minimal obstacles
- Low RF interference
- At least 1 km clear distance

### Step-by-Step Procedure

#### Step 1: Baseline Test (0-10 meters)

1. Place vehicle 1 meter from ground station
2. Power on vehicle and ground station
3. Verify telemetry link established
4. Record RSSI values:
   ```
   Distance: 1m
   Local RSSI: ___
   Remote RSSI: ___
   Noise: ___
   ```

5. Note in Mission Planner or use AT command:
   ```bash
   # Check RSSI with configuration script
   python3 sik_radio_config.py --port /dev/ttyUSB0 --show-rssi
   ```

#### Step 2: Near Range Test (10-100 meters)

1. Move vehicle to 10m, 25m, 50m, 100m increments
2. At each distance:
   - Verify telemetry link active
   - Record RSSI values
   - Send test command (mode change, waypoint)
   - Verify command acknowledgment
   - Note any packet loss in Mission Planner

3. Data collection table:
   ```
   Distance | Local RSSI | Remote RSSI | Noise | Link Quality | Notes
   ---------|------------|-------------|-------|--------------|------
   10m      |            |             |       |              |
   25m      |            |             |       |              |
   50m      |            |             |       |              |
   100m     |            |             |       |              |
   ```

#### Step 3: Medium Range Test (100-500 meters)

1. Continue moving to 150m, 200m, 300m, 400m, 500m
2. At each distance:
   - Check link status
   - Record RSSI
   - Monitor for dropouts
   - Test command/control responsiveness

3. If link degrades (RSSI < 100):
   - Note distance where degradation starts
   - Attempt to re-establish link
   - Record recovery distance

#### Step 4: Maximum Range Test (500m+)

1. Continue increasing distance until link lost
2. Walk back toward ground station until link restores
3. Record:
   - Maximum distance with reliable link
   - Distance where link was lost
   - Distance where link recovered

### Data Logging Script

Use this Python script to log RSSI during test:

```python
#!/usr/bin/env python3
"""Log RSSI values during range test"""
import time
from pymavlink import mavutil

# Connect to vehicle
master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()

print("Logging RSSI... Press Ctrl+C to stop")
print("Time,LocalRSSI,RemoteRSSI,Noise,RxErrors,Fixed")

try:
    while True:
        # Request radio status
        master.mav.request_data_stream_send(
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_EXTRA3,
            1, 1
        )

        # Wait for RADIO_STATUS message
        msg = master.recv_match(type='RADIO_STATUS', blocking=True, timeout=2)
        if msg:
            print(f"{time.time()},{msg.rssi},{msg.remrssi},{msg.noise},{msg.rxerrors},{msg.fixed}")

        time.sleep(1)

except KeyboardInterrupt:
    print("\nLogging stopped")
```

### Expected Results

**Good Link Quality:**
- RSSI > 150 at all tested distances
- No packet loss
- Commands acknowledged immediately
- Smooth telemetry updates

**Marginal Link:**
- RSSI 100-150
- Occasional packet loss (< 5%)
- Delayed command acknowledgment
- Intermittent telemetry gaps

**Poor Link:**
- RSSI < 100
- Frequent packet loss (> 10%)
- Commands fail
- Telemetry unreliable

---

## Flight Range Test

### Procedure Overview

Validate telemetry range during actual flight operations.

### Test Flight Plan

```
Mission profile:
1. Takeoff to 100m AGL
2. Fly straight away from home
3. Monitor RSSI continuously
4. Turn around at:
   - Planned distance (e.g., 500m), OR
   - RSSI drops below threshold (150), OR
   - Link lost for 5+ seconds
5. Return to home
6. Land
```

### Auto Mission Example

Create waypoint mission:

```
QGC WPL 110
0    1    0    16    0    0    0    0    -35.363261    149.165237    584.0    1
1    0    3    22    0    0    0    0    -35.363261    149.165237    100.0    1
2    0    3    16    0    0    0    0    -35.363261    149.170237    100.0    1
3    0    3    16    0    0    0    0    -35.363261    149.175237    100.0    1
4    0    3    16    0    0    0    0    -35.363261    149.180237    100.0    1
5    0    3    16    0    0    0    0    -35.363261    149.165237    100.0    1
6    0    3    20    0    0    0    0    0              0              0        1
```

Each waypoint ~500m apart (adjust based on expected range).

### Flight Test Procedure

#### Pre-Flight

1. Configure failsafe:
   ```
   FS_LONG_ACTN,1        # RTL on link loss
   FS_LONG_TIMEOUT,10    # 10 second timeout
   ```

2. Set up logging:
   ```
   LOG_BITMASK,65535     # Log everything
   LOG_DISARMED,0
   ```

3. Start RSSI logger script (see above)

4. Verify GPS lock and home position set

#### In-Flight

1. Takeoff manually to 100m AGL
2. Switch to AUTO mode
3. Monitor on ground station:
   - RSSI values (local + remote)
   - Distance from home
   - Telemetry update rate
   - Any error messages

4. If RSSI drops below 150:
   - Note distance
   - Switch to RTL or LOITER
   - Allow link to recover
   - Resume test if desired

5. If link lost:
   - Vehicle should trigger failsafe RTL
   - Wait for vehicle to return to range
   - Link should re-establish
   - Let vehicle complete RTL

#### Post-Flight

1. Download logs from vehicle
2. Analyze RSSI vs. distance
3. Check for errors or warnings
4. Review failsafe activation (if any)

### Data Collection

Record during flight:
- Maximum distance achieved
- RSSI at maximum distance
- Any link dropouts (time, duration, distance)
- Failsafe activations
- Recovery behavior

---

## Interference Testing

### Urban/RF-Noisy Environment Test

1. **Test Location:**
   - Near buildings with WiFi
   - Near other RC pilots
   - Near cell towers
   - Industrial areas

2. **Procedure:**
   - Perform ground range test
   - Compare results to open-field test
   - Note degradation in range

3. **Spectrum Analysis:**
   - Use spectrum analyzer to identify interference
   - Try different frequencies if radio supports it
   - Adjust NetID to avoid conflicts

### Multi-Radio Interference

1. Have multiple radios operating on same frequency
2. Test with different NetIDs:
   - Same NetID: Links interfere
   - Different NetID: Links coexist

---

## Data Analysis

### RSSI vs. Distance Plot

Plot RSSI values against distance:

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

### Link Budget Calculation

Estimate theoretical range:

```
Path Loss (dB) = 20 * log10(distance_m) + 20 * log10(freq_MHz) + 32.45

For 915 MHz at 1 km:
Path Loss = 20 * log10(1000) + 20 * log10(915) + 32.45
         = 60 + 59.2 + 32.45
         = 151.65 dB

Link Budget:
TX Power: 20 dBm
TX Antenna Gain: 2 dBi
RX Antenna Gain: 2 dBi
RX Sensitivity: -117 dBm (for 64 kbps)

Link Margin = TX + TX_Gain + RX_Gain - Path_Loss - RX_Sensitivity
           = 20 + 2 + 2 - 151.65 - (-117)
           = -10.65 dB

Negative margin = link will fail at 1 km
```

Reduce air speed or increase TX power to improve range.

### Performance Metrics

Calculate from test data:

```
Maximum Range = _____ meters

Reliable Range (RSSI > 150) = _____ meters

Critical Range (RSSI > 100) = _____ meters

Range Margin = (Reliable Range / Planned Mission Range) * 100 = _____%
```

**Target: 200% margin** (if mission is 500m, reliable range should be 1000m)

---

## Troubleshooting

### Poor Range Performance

**Symptom:** Range < 500m with standard settings

**Possible Causes:**
1. **Antenna Issues:**
   - Check antenna connections tight
   - Verify antennas not damaged
   - Try different antenna orientations
   - Upgrade to higher-gain antenna

2. **Power Settings:**
   - Increase TX power to maximum safe level
   - Check power supply adequate (voltage stable)

3. **Air Speed Too High:**
   - Reduce from 64 kbps to 32 or 16 kbps
   - Lower data rate = longer range

4. **Interference:**
   - Change network ID
   - Test in different location
   - Use spectrum analyzer to find quiet frequency

5. **Terrain/Obstacles:**
   - Ensure line of sight
   - Test at higher altitude
   - Avoid flying behind hills/buildings

### Intermittent Link

**Symptom:** Link drops randomly

**Possible Causes:**
1. **Vibration:**
   - Secure radio and antenna
   - Check for loose connections
   - Add vibration damping

2. **Multipath Fading:**
   - Change altitude
   - Change antenna polarization
   - Enable diversity (if supported)

3. **Electrical Interference:**
   - Route telemetry cables away from ESCs/motors
   - Add ferrite beads to cables
   - Ensure proper grounding

### Asymmetric Link

**Symptom:** One direction works, other doesn't

**Possible Causes:**
1. **Power Imbalance:**
   - Check TX power settings match
   - Verify power supply adequate on both ends

2. **Antenna Mismatch:**
   - Ensure both antennas same type
   - Check antenna orientation

3. **Hardware Failure:**
   - Swap radios to isolate problem
   - Check for damaged components

---

## Best Practices

### Radio Mounting

- Mount away from motors/ESCs (EMI sources)
- Keep antenna clear of carbon fiber/metal
- Use vertical orientation for omnidirectional coverage
- Secure firmly to prevent vibration

### Antenna Selection

- **Omni antennas:** 360° coverage, shorter range
- **Directional antennas:** Longer range, must point at vehicle
- **Diversity systems:** Best reliability, higher cost

### Range Optimization

1. **Lower air speed** = longer range (but less throughput)
2. **Reduce telemetry rates** = less data to transmit
3. **Maximum TX power** = stronger signal (check regulations)
4. **Enable ECC** = better reliability with weak signal
5. **Better antennas** = higher gain = longer range

### Safety Margins

- Plan for 50% of tested range in missions
- Always have failsafe configured
- Test in conditions similar to mission environment
- Re-test after any hardware changes

---

## Test Report Template

```
TELEMETRY RADIO RANGE TEST REPORT
Date: __________
Tester: __________
Location: __________

EQUIPMENT:
Radio Model: __________
Firmware Version: __________
Antenna Type: __________
Vehicle Type: __________

CONFIGURATION:
Serial Baud: __________
Air Speed: __________ kbps
TX Power: __________ dBm
Network ID: __________
ECC: Enabled/Disabled
MAVLink: Enabled/Disabled

GROUND TEST RESULTS:
Maximum Range: __________ meters
RSSI at Max Range: __________
Link Lost at: __________ meters
Link Recovered at: __________ meters

FLIGHT TEST RESULTS:
Maximum Range: __________ meters
RSSI at Max Range: __________
Failsafe Triggered: Yes/No
Recovery Distance: __________ meters

ENVIRONMENTAL CONDITIONS:
Weather: __________
Temperature: __________
RF Environment: Clean / Moderate / Noisy

CONCLUSION:
Pass/Fail
Recommended Mission Range: __________ meters
Notes: __________
```

---

## References

- [SiK Radio Configuration](sik_radio_config.py)
- [ArduPilot Telemetry Documentation](https://ardupilot.org/copter/docs/common-telemetry-landingpage.html)
- [Mission Planner RSSI Monitoring](https://ardupilot.org/planner/)

---

**Remember:**
- Safety first - always have failsafe configured
- Test in safe environment before critical missions
- Document all results for future reference
- Re-test after any configuration changes
