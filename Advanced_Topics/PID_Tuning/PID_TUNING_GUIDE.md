# PID Tuning Guide for ArduPilot Plane

## Overview

PID (Proportional-Integral-Derivative) controllers stabilize the aircraft. Proper tuning is critical for stable flight.

## Understanding PID

**P (Proportional):** Response to current error
- Higher P = stronger correction
- Too high = oscillation
- Too low = sluggish response

**I (Integral):** Corrects persistent error
- Eliminates steady-state error
- Too high = overshoot
- Too low = doesn't reach target

**D (Derivative):** Dampens response
- Reduces overshoot
- Too high = twitchy/noisy
- Too low = oscillation

## ArduPilot Rate Controllers

### Roll Rate PID
**Parameters:**
- `PTCH2SRV_RMAX_UP` - Max pitch up rate (deg/s)
- `PTCH2SRV_RMAX_DN` - Max pitch down rate (deg/s)  
- `PTCH2SRV_P` - Pitch P gain
- `PTCH2SRV_I` - Pitch I gain
- `PTCH2SRV_D` - Pitch D gain

### Pitch Rate PID
**Parameters:**
- `RLL2SRV_RMAX` - Max roll rate (deg/s)
- `RLL2SRV_P` - Roll P gain
- `RLL2SRV_I` - Roll I gain  
- `RLL2SRV_D` - Roll D gain

### Yaw Rate PID
**Parameters:**
- `YAW2SRV_RMAX` - Max yaw rate (deg/s)
- `YAW2SRV_P` - Yaw P gain
- `YAW2SRV_I` - Yaw I gain
- `YAW2SRV_D` - Yaw D gain

## Auto-Tune Procedure

**RECOMMENDED:** Use auto-tune first, then manually refine.

### Setup
```bash
param set AUTOTUNE_LEVEL 6  # Aggressiveness (1-10)
param set AUTOTUNE_AXES 7   # All axes (1=roll, 2=pitch, 4=yaw)
```

### Procedure
1. Ensure aircraft flies reasonably well
2. Fly to safe altitude (100m+)
3. Enter FBWA mode
4. Switch to AUTOTUNE mode (set via transmitter)
5. Aircraft will perform maneuvers
6. Keep aircraft level when prompted
7. Auto-tune takes 5-15 minutes
8. Exit AUTOTUNE mode when complete
9. New PIDs saved automatically

### Safety
- Maintain safe altitude
- Be ready to switch to MANUAL
- Good weather (calm winds)
- Open area

## Manual Tuning

### Step 1: Set Defaults

```bash
# Conservative starting point
param set RLL2SRV_P 0.4
param set RLL2SRV_I 0.1
param set RLL2SRV_D 0.04

param set PTCH2SRV_P 0.6
param set PTCH2SRV_I 0.1
param set PTCH2SRV_D 0.04

param set YAW2SRV_P 0.5
param set YAW2SRV_I 0.1
param set YAW2SRV_D 0.0
```

### Step 2: Tune Roll (Most Critical)

1. Fly in FBWA, apply sharp roll input
2. Observe response:
   - **Oscillates:** Reduce P by 25%
   - **Sluggish:** Increase P by 25%
   - **Overshoots:** Increase D by 25%
3. Repeat until crisp, non-oscillating response
4. Fine-tune I if steady-state error exists

### Step 3: Tune Pitch

Same process as roll:
1. Apply sharp pitch input
2. Check oscillation/sluggishness
3. Adjust P, then D, then I

### Step 4: Tune Yaw

Less critical for fixed-wing:
1. Test coordinated turns
2. Adjust if rudder hunting occurs
3. Usually minimal tuning needed

## Analyzing Tune Quality in Logs

### Check Tracking

**In MAVExplorer:**
```bash
graph ATT.Roll ATT.DesRoll
graph ATT.Pitch ATT.DesPitch
```

**Good tune:** Actual closely follows desired
**Poor tune:** Gap or oscillation

### Check Rate Response

```bash
graph RATE.RDes RATE.R  # Roll rate
graph RATE.PDes RATE.P  # Pitch rate
```

### Check PID Outputs

```bash
graph PIDR.P PIDR.I PIDR.D  # Roll PID terms
graph PIDP.P PIDP.I PIDP.D  # Pitch PID terms
```

## Troubleshooting

### Rapid Oscillation
**Symptom:** High frequency shake
**Cause:** P too high or D too low
**Fix:** Reduce P by 50%, increase D

### Slow Wobble
**Symptom:** Slow back-and-forth
**Cause:** I too high
**Fix:** Reduce I by 50%

### Sluggish Response
**Symptom:** Doesn't respond quickly
**Cause:** P too low
**Fix:** Increase P by 25%

### Won't Hold Attitude
**Symptom:** Drifts from target
**Cause:** I too low
**Fix:** Increase I

## Example Parameter Sets

**Conservative (training aircraft):**
```
RLL2SRV_P,0.3
RLL2SRV_I,0.05
RLL2SRV_D,0.03
PTCH2SRV_P,0.5
PTCH2SRV_I,0.05
PTCH2SRV_D,0.03
```

**Aggressive (sport/racing):**
```
RLL2SRV_P,0.8
RLL2SRV_I,0.2
RLL2SRV_D,0.08
PTCH2SRV_P,1.0
PTCH2SRV_I,0.2
PTCH2SRV_D,0.08
```

**Author:** Patrick Kelly (@Kuscko)
**Version:** 1.0
