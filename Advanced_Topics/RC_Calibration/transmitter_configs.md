# Transmitter Configuration Examples

Common transmitter configurations for ArduPilot — channel assignments, mixing, and switch setup.

---

## FrSky Taranis X9D/X9D+

### Channel Assignment

| Channel | Function         | Stick/Switch           |
| ------- | ---------------- | ---------------------- |
| CH1     | Roll (Aileron)   | Right Stick Left/Right |
| CH2     | Pitch (Elevator) | Right Stick Up/Down    |
| CH3     | Throttle         | Left Stick Up/Down     |
| CH4     | Yaw (Rudder)     | Left Stick Left/Right  |
| CH5     | Flight Mode      | Switch SF (3-position) |
| CH6     | Tuning/Aux       | Knob S1 or S2          |
| CH7     | Camera Trigger   | Switch SH (2-position) |
| CH8     | Arm/Disarm       | Switch SC (3-position) |

### Model Setup - MIXER Page

```text
CH1  100% Ail  Weight: 100%
CH2  100% Ele  Weight: 100%
CH3  100% Thr  Weight: 100%  Offset: -100%
CH4  100% Rud  Weight: 100%
CH5  100% SF   Weight: 100%
CH6  100% S1   Weight: 100%
CH7  100% SH   Weight: 100%
CH8  100% SC   Weight: 100%
```

**Note:** CH3 (Throttle) has Offset: -100% to ensure 1000µs at low stick.

### INPUTS Page

```text
I1   Ail   Weight: 100%
I2   Ele   Weight: 100%  (Optional: -100% to reverse)
I3   Thr   Weight: 100%
I4   Rud   Weight: 100%
```

### Flight Mode Setup (3-Position Switch)

```text
CH5  Switch: SF
     Curve: Custom 3-point
     Point 1: -100% (SF↑) → 1000µs (FLTMODE1)
     Point 2:    0% (SF-) → 1500µs (FLTMODE3)
     Point 3: +100% (SF↓) → 2000µs (FLTMODE5)
```

### Failsafe Setup

**Model Setup → FAILSAFE:**

```text
CH1: Hold
CH2: Hold
CH3: -100 (Throttle low)
CH4: Hold
CH5: 0 (RTL mode)
CH6-8: Hold
```

---

## Radiomaster TX16S

### Channel Assignment

| Channel | Function    | Control        |
| ------- | ----------- | -------------- |
| CH1     | Roll        | Right Stick LR |
| CH2     | Pitch       | Right Stick UD |
| CH3     | Throttle    | Left Stick UD  |
| CH4     | Yaw         | Left Stick LR  |
| CH5     | Flight Mode | SA (3-pos)     |
| CH6     | Auto-Tune   | SE (2-pos)     |
| CH7     | Camera      | SG (2-pos)     |
| CH8     | Arm         | SF (2-pos)     |

### EdgeTX Configuration

```text
1: 100% Ail  Weight:100 Offset:0   Curve:---
2: 100% Ele  Weight:100 Offset:0   Curve:---
3: 100% Thr  Weight:100 Offset:-100 Curve:---
4: 100% Rud  Weight:100 Offset:0   Curve:---
5: 100% SA   Weight:100
6: 100% SE   Weight:100
7: 100% SG   Weight:100
8: 100% SF   Weight:100
```

### Flight Modes (6-position using SA + SB)

**Logical Switches:**

```text
L01: SA↑ AND SB↑ → Mode 1 (MANUAL)
L02: SA- AND SB↑ → Mode 2 (CIRCLE)
L03: SA↓ AND SB↑ → Mode 3 (STABILIZE)
L04: SA↑ AND SB↓ → Mode 4 (FBWA)
L05: SA- AND SB↓ → Mode 5 (FBWB)
L06: SA↓ AND SB↓ → Mode 6 (AUTO)
```

**CH5 Mixer:**

```text
CH5  Weight:100 Source:L01 Offset:-100
CH5  Weight:100 Source:L02 Offset:-60
CH5  Weight:100 Source:L03 Offset:-20
CH5  Weight:100 Source:L04 Offset:+20
CH5  Weight:100 Source:L05 Offset:+60
CH5  Weight:100 Source:L06 Offset:+100
```

---

## Spektrum DX6/DX8

### Channel Assignment (Mode 2)

| Channel | Function    | Control               |
| ------- | ----------- | --------------------- |
| THRO    | Throttle    | Left Stick UD         |
| AILE    | Roll        | Right Stick LR        |
| ELEV    | Pitch       | Right Stick UD        |
| RUDD    | Yaw         | Left Stick LR         |
| GEAR    | Flight Mode | Gear Switch (2-pos)   |
| AUX1    | Tuning      | Flap Switch or Knob   |
| AUX2    | Camera      | Aux Switch            |

### Servo Setup

```text
THRO: Travel 100%/100%  Reverse: Normal
AILE: Travel 100%/100%  Reverse: Normal
ELEV: Travel 100%/100%  Reverse: Normal (or Reverse if needed)
RUDD: Travel 100%/100%  Reverse: Normal
GEAR: Travel 100%/100%  Reverse: Normal
AUX1: Travel 100%/100%  Reverse: Normal
```

### Flight Mode on GEAR Switch

2-position GEAR switch directly gives 2 modes. For 4 modes, combine GEAR + FLAP:

1. GEAR Up + FLAP Up = 1000µs → MANUAL
2. GEAR Up + FLAP Down = 1333µs → FBWA
3. GEAR Down + FLAP Up = 1666µs → AUTO
4. GEAR Down + FLAP Down = 2000µs → RTL

### Spektrum Failsafe

```text
THRO: -100 (Low throttle)
AILE: 0 (Center)
ELEV: 0 (Center)
RUDD: 0 (Center)
GEAR: 0 (Mid — RTL if configured)
AUX1-2: Hold
```

---

## Futaba T14SG

### Channel Assignment

| Channel | Function    | Control        |
| ------- | ----------- | -------------- |
| CH1     | Throttle    | Left Stick UD  |
| CH2     | Aileron     | Right Stick LR |
| CH3     | Elevator    | Right Stick UD |
| CH4     | Rudder      | Left Stick LR  |
| CH5     | Flight Mode | SA (3-pos)     |
| CH6     | Tuning      | VR Knob        |
| CH7     | Camera      | SB (2-pos)     |
| CH8     | Arm         | SD (2-pos)     |

### Linkage Menu

Set all channels to Travel: 100%/100%, Reverse: Normal (adjust per channel).

### Flight Mode via Condition

```text
Condition 1: SA Up   → CH5 = -100% (1000µs) → FLTMODE1
Condition 2: SA Mid  → CH5 = 0%    (1500µs) → FLTMODE3
Condition 3: SA Down → CH5 = +100% (2000µs) → FLTMODE5
```

### Futaba Failsafe

```text
CH1 (Throttle): F/S = -100%
CH2-4: Hold
CH5: F/S = 0% (RTL mode)
CH6-8: Hold
```

---

## FlySky FS-i6X

### Channel Assignment

| Channel | Function    | Control        |
| ------- | ----------- | -------------- |
| CH1     | Roll        | Right Stick LR |
| CH2     | Pitch       | Right Stick UD |
| CH3     | Throttle    | Left Stick UD  |
| CH4     | Yaw         | Left Stick LR  |
| CH5     | Flight Mode | SwC (3-pos)    |
| CH6     | Aux         | VrA (Knob)     |

### System Setup

**Functions Setup → AUX CHANNELS:**

```text
CH5: SwC
CH6: VrA
```

Reverse channels if needed: Functions Setup → Reverse.

### Flight Mode (3-position)

- SwC Up: 1000µs → FLTMODE1 (MANUAL)
- SwC Mid: 1500µs → FLTMODE3 (FBWA)
- SwC Down: 2000µs → FLTMODE5 (AUTO)

### Failsafe (RX Settings)

1. Bind receiver to transmitter
2. Set failsafe positions: Throttle low, others center
3. Press F/S button on receiver for 2 seconds

**Note:** FS-i6X has limited failsafe options — use ArduPilot RC failsafe as primary.

---

## General Calibration Steps

1. Center all trim tabs on transmitter before calibrating
2. Ensure stick endpoints produce: min ~1000µs, center ~1500µs, max ~2000µs
3. Test failsafe: power on TX+RX, turn off TX, verify throttle goes low and flight mode goes to RTL
4. In Mission Planner: Initial Setup → Mandatory Hardware → Radio Calibration — move all sticks through full range

---

## ArduPilot Parameter Configuration

```bash
RC_PROTOCOLS,1        # or 2048 for SBUS
FLTMODE_CH,5
RC7_OPTION,9          # Camera trigger
RC8_OPTION,153        # Arm/Disarm
THR_FS_VALUE,975
FS_SHORT_ACTN,0       # Continue on short failsafe
FS_LONG_ACTN,1        # RTL on long failsafe (>1.5s)
```

---

## Troubleshooting

- **Channel Reversed:** Use transmitter reverse, not ArduPilot RCMAP
- **Stick not centered at 1500µs:** Adjust subtrim on transmitter
- **Mode switch not working:** Verify FLTMODE_CH matches, re-calibrate CH5, check mode PWM thresholds
- **Failsafe not triggering:** Verify THR_FS_VALUE is set, configure receiver failsafe output < 975µs

---

- [ArduPilot RC Setup](https://ardupilot.org/plane/docs/common-rc-transmitter-flight-mode-configuration.html)

**Author:** Patrick Kelly (@Kuscko)
