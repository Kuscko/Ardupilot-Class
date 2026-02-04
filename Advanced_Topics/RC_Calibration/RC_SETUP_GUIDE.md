# RC Calibration and Setup Guide

## RC Receiver Types

| Type | Protocol | Channels | Notes |
|------|----------|----------|-------|
| PPM | PPM Sum | 8+ | Single wire, common |
| SBUS | SBUS | 16+ | Inverted signal |
| DSM | Spektrum | 8-12 | Satellite receivers |
| SRXL | Multiplex | 16 | Less common |

## Connection Setup

**Serial port configuration:**
```bash
param set SERIAL3_PROTOCOL 23  # RCIN on SERIAL3
param set SERIAL3_BAUD 100     # SBUS = 100000 baud
```

## Calibration Procedure

### Step 1: Radio Calibration

**In Mission Planner:**
1. Connect to autopilot
2. Initial Setup → Mandatory Hardware → Radio Calibration
3. Move all sticks to extremes
4. Click "Calibrate Radio"
5. Move sticks through full range
6. Click "Click when Done"

**Verify:**
- All channels show 1000-2000 PWM
- Center = ~1500
- No reversed channels (unless intentional)

### Step 2: Mode Setup

**Common mode switch setup (Channel 5):**
```bash
param set MODE_CH 5          # Use channel 5 for modes
param set MODE1 1            # Position 1 = MANUAL (1)
param set MODE2 5            # Position 2 = FBWA (5)
param set MODE3 10           # Position 3 = AUTO (10)
param set MODE4 11           # Position 4 = RTL (11)
param set MODE5 12           # Position 5 = LOITER (12)
param set MODE6 15           # Position 6 = GUIDED (15)
```

### Step 3: Failsafe Setup

```bash
param set FS_SHORT_ACTN 1    # RTL on short failsafe
param set FS_LONG_ACTN 2     # Land on long failsafe
param set THR_FS_VALUE 950   # Failsafe PWM threshold
```

## Channel Mapping

```bash
param set RCMAP_ROLL 1       # Channel 1 = Roll
param set RCMAP_PITCH 2      # Channel 2 = Pitch
param set RCMAP_THROTTLE 3   # Channel 3 = Throttle
param set RCMAP_YAW 4        # Channel 4 = Yaw
```

## Reversing Channels

```bash
param set RC1_REVERSED 1     # Reverse roll
param set RC2_REVERSED 1     # Reverse pitch
```

## Testing

1. Move sticks, verify correct surfaces move
2. Test mode switch, verify mode changes
3. Test failsafe by turning off TX
4. Confirm RTL/Land activates

**Author:** Patrick Kelly (@Kuscko)
