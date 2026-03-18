# TECS Performance Analysis Tutorial

TECS (Total Energy Control System) manages aircraft altitude and airspeed. Analyzing TECS logs helps tune performance.

## Key TECS Log Messages

| Parameter  | Description            | Target           |
| ---------- | ---------------------- | ---------------- |
| TECS.h     | Target altitude (m)    | Mission altitude |
| TECS.dh    | Altitude error (m)     | Close to 0       |
| TECS.spd   | Target airspeed (m/s)  | Cruise speed     |
| TECS.dspd  | Speed error (m/s)      | Close to 0       |
| TECS.ith   | Integrator throttle    | Stable           |
| TECS.iph   | Integrator pitch       | Stable           |

## Analysis in Mission Planner

**Graph altitude tracking:**

1. Open log in Mission Planner
2. Select TECS messages
3. Graph `TECS.h` and `GPS.Alt`
4. Compare desired vs actual

**Graph speed tracking:**

1. Select TECS messages
2. Graph `TECS.spd` and `GPS.Spd`
3. Check tracking accuracy

## Common Issues

### Issue 1: Altitude Oscillation

**Symptoms:** TECS.h and GPS.Alt diverge/converge repeatedly
**Cause:** TECS_TIME_CONST too low
**Fix:** Increase TECS_TIME_CONST (try 6.0–8.0)

### Issue 2: Slow Response

**Symptoms:** Large lag between TECS.h and GPS.Alt
**Cause:** TECS_TIME_CONST too high
**Fix:** Decrease TECS_TIME_CONST (try 3.0–4.0)

### Issue 3: Speed Swings During Climbs

**Symptoms:** Speed drops significantly when climbing
**Cause:** TECS_SPDWEIGHT too low
**Fix:** Increase TECS_SPDWEIGHT (try 1.5–2.0)

## MAVExplorer Commands

```bash
# Altitude tracking
graph TECS.h GPS.Alt

# Altitude error
graph TECS.dh

# Speed tracking
graph TECS.spd GPS.Spd

# Throttle response
graph TECS.ith RCOU.C3
```

## Tuning Workflow

1. Fly altitude test mission
2. Analyze TECS.dh (altitude error)
3. If oscillating → Increase TIME_CONST
4. If sluggish → Decrease TIME_CONST
5. Check speed during altitude changes
6. Adjust SPDWEIGHT if needed
7. Repeat until satisfied

**Author:** Patrick Kelly (@Kuscko)
