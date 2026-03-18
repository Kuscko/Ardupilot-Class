# ArduPilot Pre-Flight Safety Checklist

Complete all applicable items before every flight.

---

## Pre-Mission Planning

### Mission Review

- [ ] Mission waypoints reviewed and validated
- [ ] Takeoff and landing locations confirmed safe
- [ ] Altitude limits comply with regulations
- [ ] Airspace restrictions checked (NOTAMs, TFRs)
- [ ] Weather conditions acceptable
- [ ] Backup landing sites identified

### Risk Assessment

- [ ] Emergency procedures reviewed
- [ ] Safety officer designated (if required)
- [ ] Observers positioned (if required)
- [ ] First aid kit available

---

## Hardware Inspection

### Airframe

- [ ] Structure intact (no cracks, damage)
- [ ] Control surfaces move freely
- [ ] Control linkages secure
- [ ] Propeller balanced and undamaged
- [ ] Landing gear secure
- [ ] Payload secured

### Electronics

- [ ] Flight controller mounted securely
- [ ] All connections tight and secure
- [ ] Wiring protected from propeller
- [ ] GPS antenna clear view of sky
- [ ] Compass away from magnetic interference

### Power System

- [ ] Battery fully charged (> 4.0V per cell for LiPo)
- [ ] Battery connector secure
- [ ] ESC connections verified
- [ ] No burnt smell or damaged components

---

## Parameter Configuration

### Critical Parameters

- [ ] Arming checks enabled: `ARMING_CHECK = 1`
- [ ] RC failsafe configured: `THR_FS_VALUE` set
- [ ] GCS failsafe enabled: `FS_GCS_ENABLE = 1`
- [ ] Battery failsafe set: `BATT_FS_LOW_ACT` configured
- [ ] Return altitude set: `RTL_ALTITUDE` appropriate

### Geofence

- [ ] Geofence enabled: `FENCE_ENABLE = 1`
- [ ] Fence action set: `FENCE_ACTION` (1=RTL recommended)
- [ ] Maximum altitude set: `FENCE_ALT_MAX`
- [ ] Fence margin configured: `FENCE_MARGIN` (5-10m)
- [ ] Fence boundaries loaded and verified
- [ ] Rally points loaded (if used)

### Mode Configuration

- [ ] Flight modes configured correctly
- [ ] Mode switch tested on transmitter
- [ ] RTL mode accessible quickly

---

## Pre-Arm Checks

### Power On Sequence

- [ ] Connect battery (beep/flash expected)
- [ ] Wait for GPS lock (LED solid)
- [ ] Wait for EKF convergence (30+ seconds)
- [ ] Check battery voltage in GCS
- [ ] Verify telemetry connection

### Sensor Health

- [ ] GPS: 10+ satellites, HDop < 1.5
- [ ] Compass: Calibrated, interference < 30%
- [ ] Accelerometer: Calibrated, level indicated
- [ ] Barometer: Altitude reasonable
- [ ] Airspeed: Reading correctly (if equipped)

### EKF Status

- [ ] EKF healthy (no pre-arm errors)
- [ ] Position estimate good
- [ ] Velocity estimate good

### RC System

- [ ] RC receiver bound to transmitter
- [ ] All channels responding correctly
- [ ] Failsafe tested (turn off transmitter)
- [ ] Mode switch functioning
- [ ] Throttle at zero before arming

### Flight Controller

- [ ] No pre-arm errors displayed
- [ ] Logging enabled
- [ ] CPU load acceptable (< 80%)

---

## Takeoff Checklist

### Final Checks

- [ ] Area clear of people/obstacles
- [ ] Wind direction noted
- [ ] GCS monitoring ready

### Arm Sequence

- [ ] Verify mode is correct for takeoff
- [ ] Throttle at zero
- [ ] Arm via RC switch or GCS
- [ ] Verify armed status (LED, GCS, sound)
- [ ] No unusual vibrations or sounds

### Launch

- [ ] Verify positive climb rate
- [ ] Monitor attitude control
- [ ] Verify waypoint navigation (if AUTO)

---

## In-Flight Monitoring

### Continuous

- [ ] Attitude stable
- [ ] GPS lock maintained
- [ ] Battery voltage adequate
- [ ] RC and telemetry link quality good
- [ ] No EKF errors

### Periodic (Every 60 seconds)

- [ ] Battery voltage and remaining flight time
- [ ] Wind conditions
- [ ] Proximity to boundaries

---

## Emergency Procedures

| Situation        | Action                                                |
| ---------------- | ----------------------------------------------------- |
| Lost RC link     | Vehicle enters RTL; re-establish link, land promptly  |
| Lost telemetry   | Monitor via RC; GCS failsafe should trigger           |
| Low battery      | RTL or LAND triggers; override if unsafe location     |
| Geofence breach  | Vehicle triggers RTL; investigate cause after flight  |
| Control loss     | Switch to RTL; if fails, try FBWA/Manual              |
| Collision risk   | Take manual control; if unavoidable, disarm           |

---

## Landing Checklist

- [ ] Landing area clear
- [ ] Approach path clear
- [ ] Smooth touchdown
- [ ] Disarm immediately after landing

---

## Post-Flight

### Immediate

- [ ] Disconnect battery
- [ ] Inspect for damage
- [ ] Note any anomalies

### Log Review

- [ ] Download flight logs
- [ ] Check for errors
- [ ] Review EKF, battery, vibration

### Maintenance

- [ ] Recharge batteries
- [ ] Update maintenance log
- [ ] Address any issues found

### Documentation

- [ ] Log flight in logbook
- [ ] Record flight time
- [ ] Document any incidents

---

## Regulatory Compliance

- [ ] Pilot certificate valid (if required)
- [ ] Aircraft registration current
- [ ] Airspace authorization obtained (if required)
- [ ] Local regulations reviewed

### Operational Limits

- [ ] Maximum altitude: ___________ (regulatory limit)
- [ ] Maximum distance: ___________ (VLOS requirement)
- [ ] Minimum visibility: ___________ (3 statute miles US)

---

## Notes

**Flight Date:** __________ **Pilot:** __________ **Location:** __________

**Pre-Flight Notes:**

**Post-Flight Notes:**

---

**Author:** Patrick Kelly (@Kuscko)
