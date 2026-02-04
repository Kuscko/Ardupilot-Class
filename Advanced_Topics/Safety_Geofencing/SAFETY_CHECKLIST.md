# ArduPilot Pre-Flight Safety Checklist

Comprehensive safety checklist for ArduPilot operations. Complete all applicable items before every flight.

---

## Pre-Mission Planning

### Mission Review
- [ ] Mission waypoints reviewed and validated
- [ ] Takeoff and landing locations confirmed safe
- [ ] Altitude limits comply with regulations
- [ ] Airspace restrictions checked (NOTAMs, TFRs)
- [ ] Weather conditions acceptable for flight
- [ ] Backup landing sites identified

### Risk Assessment
- [ ] Flight risk assessment completed
- [ ] Emergency procedures reviewed
- [ ] Safety officer designated (if required)
- [ ] Observers positioned (if required)
- [ ] First aid kit available
- [ ] Fire extinguisher accessible

---

## Hardware Inspection

### Airframe
- [ ] Airframe structure intact (no cracks, damage)
- [ ] Control surfaces move freely
- [ ] Control linkages secure
- [ ] Propeller balanced and undamaged
- [ ] Landing gear secure
- [ ] Payload secured properly

### Electronics
- [ ] Flight controller mounted securely
- [ ] All connections tight and secure
- [ ] Wiring protected from propeller
- [ ] GPS antenna clear view of sky
- [ ] Compass away from magnetic interference
- [ ] Telemetry radio antenna secure

### Power System
- [ ] Battery fully charged
- [ ] Battery voltage checked (> 4.0V per cell for LiPo)
- [ ] Battery connector secure
- [ ] ESC connections verified
- [ ] Power distribution clean and secure
- [ ] No burnt smell or damaged components

---

## Parameter Configuration

### Critical Parameters
- [ ] Arming checks enabled: `ARMING_CHECK = 1`
- [ ] RC failsafe configured: `THR_FS_VALUE` set
- [ ] GCS failsafe enabled: `FS_GCS_ENABLE = 1`
- [ ] Battery failsafe set: `BATT_FS_LOW_ACT` configured
- [ ] Return altitude set: `RTL_ALTITUDE` appropriate

### Geofence Configuration
- [ ] Geofence enabled: `FENCE_ENABLE = 1`
- [ ] Fence action set: `FENCE_ACTION` (1=RTL recommended)
- [ ] Maximum altitude set: `FENCE_ALT_MAX` (regulatory limit)
- [ ] Minimum altitude set: `FENCE_ALT_MIN` (if applicable)
- [ ] Fence margin configured: `FENCE_MARGIN` (5-10m recommended)
- [ ] Fence boundaries loaded and verified
- [ ] Rally points loaded (if used)

### Mode Configuration
- [ ] Flight modes configured correctly
- [ ] Mode switch tested on transmitter
- [ ] RTL mode accessible quickly
- [ ] Manual mode as backup option

---

## Pre-Arm Checks

### Power On Sequence
- [ ] Connect battery (vehicle should beep/flash)
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
- [ ] Rangefinder: Functioning (if equipped)

### EKF Status
- [ ] EKF healthy (no pre-arm errors)
- [ ] Position estimate good
- [ ] Velocity estimate good
- [ ] Innovations within limits
- [ ] EKF variance low

### RC System
- [ ] RC receiver bound to transmitter
- [ ] All channels responding correctly
- [ ] Failsafe tested (turn off transmitter)
- [ ] Mode switch functioning
- [ ] Throttle at zero before arming

### Flight Controller
- [ ] No pre-arm errors displayed
- [ ] Firmware version correct
- [ ] Log files available (not full)
- [ ] Logging enabled
- [ ] CPU load acceptable (< 80%)

---

## Range Checks

### RC Range Test
- [ ] Performed range check before flight
- [ ] Full range tested (walk away with TX)
- [ ] Control surfaces respond at range
- [ ] Failsafe triggers when out of range
- [ ] Minimum 100m range verified

### Telemetry Range Test
- [ ] Telemetry link tested at distance
- [ ] Signal strength adequate
- [ ] Reconnection tested
- [ ] GCS failsafe functioning

---

## Takeoff Checklist

### Final Checks
- [ ] Area clear of people/obstacles
- [ ] Wind direction noted
- [ ] Takeoff path clear
- [ ] Camera/recording started (if required)
- [ ] GCS monitoring ready
- [ ] Observer ready (if required)

### Arm Sequence
- [ ] Verify mode is correct for takeoff
- [ ] Throttle at zero
- [ ] Arm via RC switch or GCS
- [ ] Verify armed status (LED, GCS, sound)
- [ ] Propeller spinning (QuadPlane/Copter)
- [ ] No unusual vibrations or sounds

### Launch
- [ ] Launch smoothly (hand launch/runway)
- [ ] Verify positive climb rate
- [ ] Monitor attitude control
- [ ] Transition to desired mode
- [ ] Verify waypoint navigation (if AUTO)

---

## In-Flight Monitoring

### Continuous Monitoring
- [ ] Attitude stable
- [ ] Altitude maintaining
- [ ] GPS lock maintained
- [ ] Battery voltage adequate
- [ ] RC link quality good
- [ ] Telemetry link quality good
- [ ] Airspeed in acceptable range
- [ ] No EKF errors
- [ ] Mission progress normal

### Periodic Checks (Every 60 seconds)
- [ ] Battery voltage check
- [ ] Remaining flight time estimate
- [ ] Wind conditions assessment
- [ ] Proximity to boundaries
- [ ] Backup plan review

---

## Emergency Procedures

### Lost Link (RC or Telemetry)
- [ ] Vehicle enters RTL automatically
- [ ] Monitor return via remaining link
- [ ] Re-establish link if possible
- [ ] Be ready for manual intervention
- [ ] Land as soon as link restored

### Low Battery
- [ ] Vehicle initiates RTL or LAND
- [ ] Override if unsafe landing location
- [ ] Select safe landing area
- [ ] Land immediately

### Geofence Breach
- [ ] Vehicle triggers fence action (RTL)
- [ ] Monitor vehicle behavior
- [ ] Do not override unless necessary
- [ ] Investigate cause after flight

### Control Loss
- [ ] Switch to RTL mode
- [ ] If RTL fails, switch to FBWA/Manual
- [ ] Attempt controlled landing
- [ ] Crash landing if necessary (away from people)

### Collision Risk
- [ ] Take immediate manual control
- [ ] Avoid collision
- [ ] If impact unavoidable, disarm to minimize damage

---

## Landing Checklist

### Approach
- [ ] Landing area clear
- [ ] Wind direction favorable
- [ ] Approach path clear
- [ ] Airspeed appropriate
- [ ] Altitude decreasing normally

### Touchdown
- [ ] Smooth touchdown
- [ ] No damage observed
- [ ] Throttle to zero
- [ ] Disarm immediately
- [ ] Propeller stopped

---

## Post-Flight

### Immediate Actions
- [ ] Disconnect battery
- [ ] Inspect for damage
- [ ] Check for loose connections
- [ ] Note any anomalies

### Log Review
- [ ] Download flight logs
- [ ] Check for errors in log
- [ ] Review EKF performance
- [ ] Check battery usage
- [ ] Note vibration levels
- [ ] Review mission execution

### Maintenance
- [ ] Clean airframe if needed
- [ ] Check for wear on components
- [ ] Recharge batteries
- [ ] Update maintenance log
- [ ] Address any issues found

### Documentation
- [ ] Log flight in logbook
- [ ] Record flight time
- [ ] Document any incidents
- [ ] Update checklist if needed
- [ ] Brief team on flight

---

## Regulatory Compliance

### Before Each Flight
- [ ] Part 107 certificate valid (if commercial, US)
- [ ] Aircraft registration current
- [ ] Insurance valid
- [ ] Airspace authorization obtained (if required)
- [ ] NOTAM filed (if required)
- [ ] Local regulations reviewed

### Operational Limits
- [ ] Maximum altitude: ___________ (regulatory limit)
- [ ] Maximum distance: ___________ (VLOS requirement)
- [ ] Maximum speed: ___________ (regulatory limit)
- [ ] Minimum visibility: ___________ (3 statute miles US)
- [ ] Maximum wind: ___________ (aircraft limit)

---

## Emergency Contacts

**In Case of Emergency:**

- Emergency Services: 911 (US) / 112 (EU)
- FAA: 1-866-TELL-FAA (US)
- Local Police: ___________
- Airfield Manager: ___________
- Safety Officer: ___________
- Insurance: ___________

---

## Notes Section

**Flight Date:** __________
**Pilot:** __________
**Observer:** __________
**Location:** __________
**Special Conditions:** __________

**Pre-Flight Notes:**


**Post-Flight Notes:**


---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-02-03 | Initial version | Patrick Kelly |

---

**Author:** Patrick Kelly (@Kuscko)
**Version:** 1.0
**Last Updated:** 2026-02-03

**Note:** This checklist should be customized for your specific aircraft, mission, and regulatory environment. Print and bring to every flight!
