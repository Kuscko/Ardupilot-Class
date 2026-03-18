# L1 Controller and Navigation Guide

## L1 Controller Overview

The L1 controller guides the aircraft to follow desired paths (waypoints, loiter circles).

## Key Parameters

```bash
NAVL1_PERIOD,18        # L1 control period (sec)
NAVL1_DAMPING,0.75     # Damping ratio
WP_LOITER_RAD,80       # Loiter radius (m)
WP_RADIUS,30           # Waypoint acceptance radius
```

## NAVL1_PERIOD

**Effect:** Controls how aggressively aircraft turns toward path

- Lower (12-15): Aggressive turns, tight tracking
- Medium (16-20): Balanced
- Higher (20-25): Gentle turns, loose tracking

**Tune:** Adjust based on aircraft speed and responsiveness

## Path Tracking Analysis

**In logs:**

```bash
graph NTUN.WpDist  # Distance to waypoint
graph NTUN.NavRoll # Navigation roll command
graph NTUN.Xtrack  # Cross-track error
```

**Author:** Patrick Kelly (@Kuscko)
