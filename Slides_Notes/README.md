# ArduPilot Learning Resources & Quick Reference

## Overview

Condensed reference materials, checklists, and a presentation outline for ArduPilot Plane 4.5.7 development.

**Included:**
- Quick reference cards for common tasks
- Learning checklist to track progress
- Presentation outline for team knowledge sharing

## Prerequisites

- Completed initial ArduPilot setup and SITL
- Basic flight controller concepts
- Experience with at least one ArduPilot module

## Quick Reference Card

**[QUICK_REFERENCE_CARD.md](QUICK_REFERENCE_CARD.md)** — one-page summaries of:

### Essential Commands

**SITL:**
```bash
sim_vehicle.py --console --map        # Start SITL with console and map
sim_vehicle.py -w                     # Wipe parameters to defaults
sim_vehicle.py --location CMAC        # Start at specific location
```

**MAVProxy:**
```bash
mode AUTO               # Switch to autonomous mode
arm throttle            # Arm vehicle
wp load mission.txt     # Load mission file
param set PARAM VALUE   # Set parameter
status                  # Check vehicle status
```

**Build:**
```bash
./waf configure --board sitl    # Configure for SITL
./waf plane                     # Build ArduPlane
./waf list_boards               # List available boards
```

### Critical Parameters

**Flight Control:** `ARMING_CHECK`, `TRIM_ARSPD_CM`, `WP_RADIUS`, `RTL_ALTITUDE`

**TECS:** `TECS_PITCH_MAX/MIN`, `TECS_CLMB_MAX`, `TECS_SPDWEIGHT`

**EKF:** `EK3_ENABLE`, `EK3_SRC1_POSXY`, `EK3_GPS_TYPE`

**Failsafes:** `FS_SHORT_ACTN`, `FS_LONG_ACTN`, `BATT_FS_LOW_ACT`

### Common Workflows

**First Flight:** Build → start SITL → check pre-arm → arm → test manual → load mission → test AUTO → verify RTL

**Parameter Tuning:** Load baseline → change one parameter → test in SITL → analyze logs → document → repeat

**Troubleshooting:** `status` → pre-arm checks → sensor health → parameter values → flight logs → forums/Discord

## Learning Checklist

**[ONBOARDING_CHECKLIST.md](ONBOARDING_CHECKLIST.md)**

### Week 1: Environment Setup
- [ ] Install WSL2/Ubuntu
- [ ] Build ArduPilot from source
- [ ] Run first SITL simulation
- [ ] MAVProxy basics and parameters

### Week 2: Core Concepts
- [ ] Flight modes, EKF fundamentals
- [ ] Sensor drivers, codebase structure
- [ ] Read MAVLink messages

### Week 3: Mission Planning
- [ ] Create waypoint mission, test autonomous flight
- [ ] Tune TECS, configure failsafes, analyze logs

### Week 4: Advanced Topics
- [ ] Lua scripting, mavlink-router
- [ ] GPS-denied scenarios, sensor failures

## Presentation Outline

**[ONBOARDING_PRESENTATION_OUTLINE.md](ONBOARDING_PRESENTATION_OUTLINE.md)** — 8-session structure:

| Session | Topic | Duration |
|---------|-------|----------|
| 1 | ArduPilot intro & environment | 45 min |
| 2 | Parameters & flight modes | 45 min |
| 3 | Mission planning & SITL | 30 min |
| 4 | Lua scripting | 30 min |
| 5 | MAVLink & communication | 30 min |
| 6 | EKF & sensor drivers | 30 min |
| 7 | Building & codebase tour | 30 min |
| 8 | Wrap-up & next steps | 15 min |

## Additional Resources

- [ArduPilot Docs](https://ardupilot.org/plane/) - User and developer guides
- [MAVLink Guide](https://mavlink.io/en/) - Protocol specification
- [ArduPilot Discord](https://ardupilot.org/discord) - Real-time help
- [Discourse Forums](https://discuss.ardupilot.org/) - Searchable Q&A
- [GitHub Repository](https://github.com/ArduPilot/ardupilot) - Source code
- [ArduPilot Learning Pathway](https://ardupilot.org/dev/docs/learning-ardupilot-introduction.html)
- [ArduPilot Glossary](https://ardupilot.org/plane/docs/common-glossary.html)
- [Contributing Guide](https://ardupilot.org/dev/docs/contributing.html)
