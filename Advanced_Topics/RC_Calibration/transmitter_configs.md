# Transmitter Configuration Examples

Common transmitter configurations for ArduPilot. These examples cover popular transmitter brands and show how to set up channels, mixing, and switches.

---

## Table of Contents

1. [FrSky Taranis X9D/X9D+](#frsky-taranis)
2. [Radiomaster TX16S](#radiomaster-tx16s)
3. [Spektrum DX6/DX8](#spektrum-dx6dx8)
4. [Futaba T14SG](#futaba-t14sg)
5. [FlySky FS-i6X](#flysky-fs-i6x)

---

## FrSky Taranis X9D/X9D+

### Channel Assignment

| Channel | Function | Stick/Switch |
|---------|----------|--------------|
| CH1 | Roll (Aileron) | Right Stick Left/Right |
| CH2 | Pitch (Elevator) | Right Stick Up/Down |
| CH3 | Throttle | Left Stick Up/Down |
| CH4 | Yaw (Rudder) | Left Stick Left/Right |
| CH5 | Flight Mode | Switch SF (3-position) |
| CH6 | Tuning/Aux | Knob S1 or S2 |
| CH7 | Camera Trigger | Switch SH (2-position) |
| CH8 | Arm/Disarm | Switch SC (3-position) |

### Model Setup - MIXER Page

**Delete all mixes and create new:**

```
CH1  100% Ail  Weight: 100%
CH2  100% Ele  Weight: 100%
CH3  100% Thr  Weight: 100%  Offset: -100%
CH4  100% Rud  Weight: 100%
CH5  100% SF   Weight: 100%
CH6  100% S1   Weight: 100%
CH7  100% SH   Weight: 100%
CH8  100% SC   Weight: 100%
```

**Note:** CH3 (Throttle) has Offset: -100% to ensure 1000µs at low stick position.

### Model Setup - INPUTS Page

```
I1   Ail   Weight: 100%
I2   Ele   Weight: 100%  (Optional: Weight: -100% to reverse)
I3   Thr   Weight: 100%
I4   Rud   Weight: 100%
```

### Flight Mode Setup (3-Position Switch)

**Switch SF Configuration:**

- **SF↑ (Up):** MANUAL mode
- **SF- (Mid):** FBWA mode
- **SF↓ (Down):** AUTO mode

**In MIXER page for CH5:**
```
CH5  Switch: SF
     Weight: 100%

     Curve: Custom 3-point
     Point 1: -100% (SF↑) → Output 1000µs (FLTMODE1)
     Point 2: 0%    (SF-) → Output 1500µs (FLTMODE3)
     Point 3: +100% (SF↓) → Output 2000µs (FLTMODE5)
```

### Arm/Disarm Setup

**Switch SC Configuration (3-position):**

- **SC↑:** Armed
- **SC-:** Disarmed
- **SC↓:** Disarmed

**In MIXER page for CH8:**
```
CH8  Switch: SC
     Weight: 100%
```

### Failsafe Setup

**Model Setup → FAILSAFE:**

```
CH1: Hold
CH2: Hold
CH3: -100 (Throttle low)
CH4: Hold
CH5: 0 (Middle position - FBWA or RTL mode)
CH6-8: Hold
```

---

## Radiomaster TX16S

### Channel Assignment

Same as Taranis (Mode 2):

| Channel | Function | Control |
|---------|----------|---------|
| CH1 | Roll | Right Stick LR |
| CH2 | Pitch | Right Stick UD |
| CH3 | Throttle | Left Stick UD |
| CH4 | Yaw | Left Stick LR |
| CH5 | Flight Mode | SA (3-pos) |
| CH6 | Auto-Tune | SE (2-pos) |
| CH7 | Camera | SG (2-pos) |
| CH8 | Arm | SF (2-pos) |

### EdgeTX Configuration

**MIXER page:**

```
1: 100% Ail    Weight:100 Offset:0 Curve:---
2: 100% Ele    Weight:100 Offset:0 Curve:---
3: 100% Thr    Weight:100 Offset:-100 Curve:---
4: 100% Rud    Weight:100 Offset:0 Curve:---
5: 100% SA     Weight:100
6: 100% SE     Weight:100
7: 100% SG     Weight:100
8: 100% SF     Weight:100
```

### Flight Modes (6-position using SA + SB)

For 6 flight modes, combine two 3-position switches:

**Logical Switches:**
```
L01: SA↑ AND SB↑ → Mode 1 (MANUAL)
L02: SA- AND SB↑ → Mode 2 (CIRCLE)
L03: SA↓ AND SB↑ → Mode 3 (STABILIZE)
L04: SA↑ AND SB↓ → Mode 4 (FBWA)
L05: SA- AND SB↓ → Mode 5 (FBWB)
L06: SA↓ AND SB↓ → Mode 6 (AUTO)
```

**CH5 Mixer:**
```
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

| Channel | Function | Control |
|---------|----------|---------|
| THRO | Throttle | Left Stick UD |
| AILE | Roll | Right Stick LR |
| ELEV | Pitch | Right Stick UD |
| RUDD | Yaw | Left Stick LR |
| GEAR | Flight Mode | Gear Switch (2-pos) |
| AUX1 | Tuning | Flap Switch or Knob |
| AUX2 | Camera | Aux Switch |

### System Setup

**Function → SERVO SETUP:**

```
THRO: Travel 100% / 100%  Reverse: Normal
AILE: Travel 100% / 100%  Reverse: Normal
ELEV: Travel 100% / 100%  Reverse: Normal (or Reverse if needed)
RUDD: Travel 100% / 100%  Reverse: Normal
GEAR: Travel 100% / 100%  Reverse: Normal
AUX1: Travel 100% / 100%  Reverse: Normal
```

### Flight Mode on GEAR Switch

Spektrum uses 2-position switches, limiting to 2 direct modes:

- **GEAR Up:** MANUAL
- **GEAR Down:** FBWA

**For more modes, use mixing:**

Create a mix combining GEAR + FLAP to get 4 positions:
1. GEAR Up + FLAP Up = 1000µs → MANUAL
2. GEAR Up + FLAP Down = 1333µs → FBWA
3. GEAR Down + FLAP Up = 1666µs → AUTO
4. GEAR Down + FLAP Down = 2000µs → RTL

### Failsafe Setup

**System Setup → FAILSAFE:**

```
THRO: -100 (Low throttle)
AILE: 0 (Center)
ELEV: 0 (Center)
RUDD: 0 (Center)
GEAR: 0 (Mid position for RTL if configured)
AUX1-2: Hold
```

---

## Futaba T14SG

### Channel Assignment

| Channel | Function | Control |
|---------|----------|---------|
| CH1 | Throttle | Left Stick UD |
| CH2 | Aileron | Right Stick LR |
| CH3 | Elevator | Right Stick UD |
| CH4 | Rudder | Left Stick LR |
| CH5 | Flight Mode | SA (3-pos) |
| CH6 | Tuning | VR Knob |
| CH7 | Camera | SB (2-pos) |
| CH8 | Arm | SD (2-pos) |

### Linkage Menu

**Set all channels to:**
- Travel: 100% / 100%
- Reverse: Normal (reverse if needed per channel)

### Flight Mode via Condition

**COND (Condition) Setup:**

Create condition for flight modes:

```
Condition 1: SA Up    → CH5 = -100% (1000µs) → FLTMODE1
Condition 2: SA Mid   → CH5 = 0%    (1500µs) → FLTMODE3
Condition 3: SA Down  → CH5 = +100% (2000µs) → FLTMODE5
```

### Failsafe

**LINKAGE → FAIL SAFE:**

```
CH1 (Throttle): F/S (Failsafe position) = -100%
CH2-4: Hold
CH5: F/S = 0% (RTL mode)
CH6-8: Hold
```

---

## FlySky FS-i6X

### Channel Assignment

| Channel | Function | Control |
|---------|----------|---------|
| CH1 | Roll | Right Stick LR |
| CH2 | Pitch | Right Stick UD |
| CH3 | Throttle | Left Stick UD |
| CH4 | Yaw | Left Stick LR |
| CH5 | Flight Mode | SwC (3-pos) |
| CH6 | Aux | VrA (Knob) |

### System Setup

**Functions Setup → AUX CHANNELS:**

```
CH5: SwC
CH6: VrA
```

**Reverse channels if needed:**
- Go to Functions Setup → Reverse
- Test each channel and reverse if control is backwards

### Flight Mode (3-position)

**SwC positions:**
- Up: 1000µs → FLTMODE1 (MANUAL)
- Mid: 1500µs → FLTMODE3 (FBWA)
- Down: 2000µs → FLTMODE5 (AUTO)

### Failsafe (RX Settings)

**On the receiver:**

1. Bind receiver to transmitter
2. Set desired failsafe stick positions:
   - Throttle: Low
   - Others: Center
3. Press F/S button on receiver for 2 seconds
4. Failsafe is saved

**Note:** FS-i6X has limited failsafe options. Consider using ArduPilot's RC failsafe as primary.

---

## General Calibration Steps

### 1. Center All Trims

Before calibration, center all trim tabs on transmitter.

### 2. Set Endpoints

Ensure stick endpoints produce:
- Minimum: ~1000µs
- Center: ~1500µs
- Maximum: ~2000µs

### 3. Test Failsafe

1. Power on transmitter and receiver
2. Verify normal control
3. Turn off transmitter
4. Verify throttle goes low
5. Verify flight mode goes to RTL (if configured)

### 4. Verify in ArduPilot

**In Mission Planner:**
1. Connect to flight controller
2. Go to Initial Setup → Mandatory Hardware → Radio Calibration
3. Move all sticks through full range
4. Verify bars reach min/max
5. Click "Calibrate Radio" and follow prompts

---

## ArduPilot Parameter Configuration

After transmitter setup, configure ArduPilot parameters:

```bash
# RC type and protocol (set automatically usually)
RC_PROTOCOLS,1    # or 2048 for SBUS, etc.

# Flight mode channel
FLTMODE_CH,5

# Mode PWM thresholds (for 6-position modes)
# These divide the 1000-2000µs range into 6 bands

# RC Option functions (if using dedicated switches)
RC7_OPTION,9      # Camera trigger
RC8_OPTION,153    # Arm/Disarm

# Failsafe
THR_FS_VALUE,975  # Trigger at < 975µs
FS_SHORT_ACTN,0   # Continue on short failsafe
FS_LONG_ACTN,1    # RTL on long failsafe (>1.5s)
```

---

## Troubleshooting

### Channel Reversed
- **Solution:** Use transmitter's reverse function, NOT ArduPilot's RCMAP

### Stick Not Centered at 1500µs
- **Solution:** Adjust subtrim on transmitter or use trim tabs

### Mode Switch Not Working
- **Solution:**
  1. Verify CH5 (or configured channel) is moving
  2. Check FLTMODE_CH parameter matches
  3. Verify mode PWM thresholds

### Failsafe Not Triggering
- **Solution:**
  1. Verify THR_FS_VALUE is set correctly
  2. Test by turning off transmitter
  3. Check receiver is configured for failsafe
  4. Verify ArduPilot sees RC loss

---

**Author:** Patrick Kelly (@Kuscko)
**Version:** 1.0
**Last Updated:** 2026-02-03

**References:**
- [FrSky Taranis Manual](https://www.frsky-rc.com/taranis-x9d/)
- [Radiomaster TX16S Manual](https://www.radiomasterrc.com/products/tx16s-mark-ii-radio-controller)
- [Spektrum DX8 Manual](https://www.spektrumrc.com/Products/Default.aspx?ProdID=SPM8800)
- [ArduPilot RC Setup](https://ardupilot.org/plane/docs/common-rc-transmitter-flight-mode-configuration.html)
