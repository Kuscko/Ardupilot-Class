# Safety Systems and Geofencing Guide

## Geofence Types

### 1. Circular Fence

**Setup:**
```bash
param set FENCE_ENABLE 1        # Enable fence
param set FENCE_TYPE 2          # Circular fence
param set FENCE_RADIUS 500      # 500m radius
param set FENCE_ALT_MAX 200     # 200m max altitude
param set FENCE_ALT_MIN 50      # 50m min altitude (RTL floor)
param set FENCE_ACTION 1        # RTL on breach
```

### 2. Polygon Fence

**Upload via Mission Planner:**
1. Flight Plan → Fence
2. Draw polygon on map
3. Upload to autopilot

### 3. Altitude Fence

```bash
param set FENCE_TYPE 1          # Altitude only
param set FENCE_ALT_MAX 400     # Max 400m AGL
```

## Fence Actions

```bash
param set FENCE_ACTION 0        # Report only
param set FENCE_ACTION 1        # RTL
param set FENCE_ACTION 2        # Land
param set FENCE_ACTION 3        # SmartRTL
```

## Rally Points

**Purpose:** Alternative safe landing points

**Setup:**
1. Mission Planner → Flight Plan → Rally Points
2. Click map to add rally points
3. Upload to autopilot

**Parameters:**
```bash
param set RALLY_TOTAL 3         # Number of rally points
param set RALLY_LIMIT_KM 2      # Max 2km from rally point
```

## Battery Failsafe

```bash
param set BATT_LOW_VOLT 10.5    # Low battery warning
param set BATT_CRT_VOLT 10.0    # Critical - RTL
param set BATT_FS_LOW_ACT 2     # Land on low battery
param set BATT_FS_CRT_ACT 2     # Land on critical
```

## Pre-Arm Safety Checks

**Common pre-arm checks:**
- GPS lock (10+ satellites)
- EKF variance low
- Compass calibrated
- RC calibrated
- Battery voltage OK
- Geofence valid

**Disable checks (use carefully!):**
```bash
param set ARMING_CHECK 0        # Disable all (dangerous!)
param set ARMING_CHECK 1        # Enable all (safe)
# Bitmask for selective disable
```

**Author:** Patrick Kelly (@Kuscko)
