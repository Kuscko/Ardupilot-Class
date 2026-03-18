# RC Calibration and Setup

Proper RC configuration is essential for safe operation, mode switching, and failsafe behavior.

## Channel Mapping

| Channel | Function    | Typical Range |
| ------- | ----------- | ------------- |
| 1       | Roll        | 1000-2000 μs  |
| 2       | Pitch       | 1000-2000 μs  |
| 3       | Throttle    | 1000-2000 μs  |
| 4       | Yaw         | 1000-2000 μs  |
| 5       | Flight Mode | 1000-2000 μs  |
| 6       | Auxiliary 1 | 1000-2000 μs  |
| 7       | Auxiliary 2 | 1000-2000 μs  |
| 8       | Auxiliary 3 | 1000-2000 μs  |

## Common Flight Modes

| Mode Number | Name      | Use Case                         |
| ----------- | --------- | -------------------------------- |
| 0           | STABILIZE | Manual flight with stabilization |
| 2           | ALTHOLD   | Maintain altitude                |
| 3           | AUTO      | Autonomous mission               |
| 4           | GUIDED    | GCS control                      |
| 5           | LOITER    | GPS hold position                |
| 6           | RTL       | Return to launch                 |
| 9           | LAND      | Auto land                        |

## Exercises

### Exercise 1: Identify RC Receiver Type

```bash
param show SERIAL1_PROTOCOL
param show RC_PROTOCOLS

param set SERIAL1_PROTOCOL 23
param set SERIAL1_BAUD 100000
param set SERIAL1_OPTIONS 0
param write
reboot
```

### Exercise 2: RC Calibration Procedure

**Using Mission Planner:**

1. INITIAL SETUP → Mandatory Hardware → Radio Calibration
2. Click "Calibrate Radio"
3. Move all sticks and switches to extremes, then center
4. Click "Click when Done"
5. Verify channels show 1000-2000 μs, center ~1500 μs

**Manual parameter configuration:**

```bash
param set RC1_MIN 1000
param set RC1_MAX 2000
param set RC1_TRIM 1500
param set RC1_DZ 10
param set RC1_REVERSED 0

param set RC2_MIN 1000
param set RC2_MAX 2000
param set RC2_TRIM 1500

param set RC3_MIN 1000
param set RC3_MAX 2000
param set RC3_TRIM 1500

param set RC4_MIN 1000
param set RC4_MAX 2000
param set RC4_TRIM 1500
param write
```

### Exercise 3: Channel Mapping Configuration

```bash
param set RCMAP_ROLL 1
param set RCMAP_PITCH 2
param set RCMAP_THROTTLE 3
param set RCMAP_YAW 4
param write
reboot
```

**Transmitter modes:** Mode 2 (most common) has Throttle/Yaw on left, Roll/Pitch on right.

### Exercise 4: Flight Mode Switch Configuration

```bash
param set FLTMODE_CH 5

param set FLTMODE1 0        # Low PWM (<1230) = STABILIZE
param set FLTMODE2 2        # (1230-1360) = ALTHOLD
param set FLTMODE3 3        # (1360-1490) = AUTO
param set FLTMODE4 5        # (1490-1620) = LOITER
param set FLTMODE5 9        # (1620-1749) = LAND
param set FLTMODE6 6        # High PWM (>1749) = RTL
param write
```

### Exercise 5: Auxiliary Function Mapping

```bash
param set RC7_OPTION 153    # Arm/Disarm
param set RC8_OPTION 9      # Camera trigger
param set RC6_OPTION 11     # Fence enable
param set RC9_OPTION 31     # Motor emergency stop
param write
reboot
```

### Exercise 6: RC Failsafe Configuration

```bash
param set FS_THR_ENABLE 1
param set FS_THR_VALUE 975
param set FS_THR_ACTION 1   # 0=Continue, 1=RTL, 2=Land
param set FS_TIMEOUT 1.5
param set FS_GCS_ENABLE 1
param set FS_GCS_TIMEOUT 5
param write
```

Test: arm in safe area, turn off transmitter, verify failsafe action, restore transmitter.

### Exercise 7: RC Range Testing

```bash
param set RSSI_TYPE 1
param set RSSI_PIN 103
param set RSSI_CHAN 8
param set RSSI_CHAN_LOW 0
param set RSSI_CHAN_HIGH 255
param write
```

Expected range: 2.4GHz 500m-1km, 900MHz 2-10km, ELRS 10-40km+. RSSI should be > 50% at operational range.

## Common Issues

### No RC Input Detected

```bash
param show SERIAL1_PROTOCOL
param set SERIAL1_PROTOCOL 23
param show BRD_PWM_COUNT
param set BRD_PWM_COUNT 8
param show RC_PROTOCOLS
param set RC_PROTOCOLS 1
param write
reboot
```

### Reversed Controls

```bash
param set RC1_REVERSED 1  # Or fix in transmitter (preferred)
```

### Noisy or Jittery RC Input

```bash
param set RC1_DZ 20
param set RC2_DZ 20
param set RC3_DZ 20
param set RC4_DZ 20
param set RC_FILT 50
```

### Mode Switch Not Working

```bash
param show FLTMODE_CH
param set FLTMODE_CH 5
param show RC5_MIN
param show RC5_MAX

rc 5 1100  # Should trigger FLTMODE1
rc 5 1300  # Should trigger FLTMODE2
rc 5 1500  # Should trigger FLTMODE3
```

### Failsafe Not Triggering

```bash
param show FS_THR_ENABLE
param set FS_THR_ENABLE 1
param show FS_THR_VALUE
param set FS_THR_VALUE 975
param set FS_THR_ACTION 1
```

## Advanced RC Configuration

### Elevon Mixing (Flying Wing)

```bash
param set MIXING_GAIN 0.5
param set SERVO1_FUNCTION 77   # Left elevon
param set SERVO2_FUNCTION 78   # Right elevon
```

### V-Tail Mixing

```bash
param set SERVO1_FUNCTION 73   # Left V-tail
param set SERVO2_FUNCTION 74   # Right V-tail
```

### Channel Scaling

```bash
# If receiver outputs 800-2200 instead of 1000-2000
param set RC1_MIN 800
param set RC1_MAX 2200
param set RC1_TRIM 1500
```

---

- [RC Setup Guide](RC_SETUP_GUIDE.md)
- [Transmitter Configs](transmitter_configs.md)
- [Radio Control Setup](https://ardupilot.org/copter/docs/common-radio-control-calibration.html)
- [RC Input Protocols](https://ardupilot.org/copter/docs/common-rc-systems.html)
- [Failsafe Configuration](https://ardupilot.org/copter/docs/radio-failsafe.html)
- [Auxiliary Functions](https://ardupilot.org/copter/docs/common-auxiliary-functions.html)
