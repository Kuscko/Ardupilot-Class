# Vibration Analysis Tutorial

## Overview

Excessive vibration degrades flight performance and can cause crashes. Log analysis identifies vibration issues.

## Vibration Log Messages

| Message | Parameters | Good Range |
|---------|------------|------------|
| VIBE | VibeX, VibeY, VibeZ | < 30 m/s² |
| IMU | AccX, AccY, AccZ | No clipping (±16g) |
| IMU | GyrX, GyrY, GyrZ | No clipping (±2000°/s) |

## Quick Check in Mission Planner

1. Open log
2. Select **VIBE** messages
3. Graph all three axes: `VIBE.VibeX`, `VIBE.VibeY`, `VIBE.VibeZ`
4. Check values stay below 30 m/s²

## Vibration Severity Levels

| Level | Value (m/s²) | Action Required |
|-------|--------------|-----------------|
| Good | 0-15 | None - optimal |
| Acceptable | 15-30 | Monitor, consider improvement |
| Warning | 30-60 | Reduce vibration soon |
| Critical | 60+ | Do not fly - fix immediately |

## Clipping Detection

**Check for IMU clipping:**
1. Graph `IMU.AccX`, `IMU.AccY`, `IMU.AccZ`
2. Look for flat-top peaks at ±16
3. Check `IMU.GyrX/Y/Z` for ±2000 limits

**Clipping indicates:**
- Severe vibration
- Physical impact
- IMU saturation (sensor overload)

## Common Vibration Sources

1. **Unbalanced propellers**
   - Check: Regular vibration pattern
   - Fix: Balance or replace props

2. **Loose motor mounts**
   - Check: High Z-axis vibration
   - Fix: Tighten mounting screws

3. **ESC noise**
   - Check: EMI interference
   - Fix: Add filtering, reroute wires

4. **Frame resonance**
   - Check: Specific frequency spikes
   - Fix: Stiffen frame, add dampening

## MAVExplorer Analysis

```bash
# View vibration
graph VIBE.VibeX VIBE.VibeY VIBE.VibeZ

# Check clipping
graph IMU.AccX IMU.AccY IMU.AccZ

# Correlate with throttle
graph VIBE.VibeZ RCOU.C3
```

## Solutions by Symptom

**High X/Y vibration:**
- Check propeller balance
- Inspect motor bearings
- Verify motor alignment

**High Z vibration:**
- Check motor mount tightness
- Add vibration damping pads
- Inspect frame rigidity

**Vibration increases with throttle:**
- Unbalanced props/motors
- Resonant frequency issue
- ESC calibration needed

**Clipping:**
- Severe vibration problem
- Must fix before flying
- Check all mechanical connections

## Fixing Vibration

1. Balance propellers (prop balancer tool)
2. Tighten all screws and connections
3. Add vibration damping (gel pads, rubber mounts)
4. Replace worn propellers
5. Check motor timing (BLHeli settings)
6. Isolate FC from frame vibration

**Author:** Patrick Kelly (@Kuscko)
**Version:** 1.0
