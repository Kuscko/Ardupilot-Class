# GDB Debugging Examples for ArduPilot

Practical debugging sessions showing real-world scenarios and solutions.

**Author:** Patrick Kelly (@Kuscko)

---

## Example 1: Debugging a Segmentation Fault

**Scenario:** ArduPlane crashes immediately after arming.

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py --gdb
```

```gdb
(gdb) run
Program received signal SIGSEGV, Segmentation fault.
0x000055555566abcd in AP_AHRS_NavEKF::update (this=0x555555aabbcc)
    at ../../libraries/AP_AHRS/AP_AHRS_NavEKF.cpp:234
234         ekf.getPosition(position);

(gdb) backtrace
#0  AP_AHRS_NavEKF::update at AP_AHRS_NavEKF.cpp:234
#1  Plane::update_AHRS at system.cpp:156
#2  Plane::update at Plane.cpp:123

(gdb) print ekf._ekf3
$3 = (NavEKF3 *) 0x0
```

**Root Cause:** EKF3 pointer is NULL — EKF not initialized because `_ekf_type` is 0.

**Fix:**

```bash
param set AHRS_EKF_TYPE 3
param save
reboot
```

---

## Example 2: GPS Not Acquiring Fix

**Scenario:** GPS shows 0 satellites, vehicle won't arm.

```gdb
(gdb) break AP_GPS::update
(gdb) run

(gdb) print state[0].status
$2 = AP_GPS::GPS_Status::NO_GPS

(gdb) print _port->available()
$5 = 0

(gdb) print _port->is_initialized()
$7 = false
```

**Root Cause:** GPS UART port not initialized. `find_serial()` returned NULL — GPS serial port not configured.

**Fix:**

```bash
param set SERIAL3_PROTOCOL 5  # GPS on SERIAL3
param set SERIAL3_BAUD 115200
param save
reboot
```

---

## Example 3: EKF Variance Error

**Scenario:** Logs show "EKF3 IMU1 stopped aiding", vehicle won't arm.

```gdb
(gdb) break NavEKF3::healthy

(gdb) print _gps_check_fail_status
$1 = {nsats = true, hdop = true, hacc = true, vacc = true, sacc = true, ...}

(gdb) print gps.status(0)
$3 = AP_GPS::GPS_Status::NO_GPS
```

**Root Cause:** GPS has no fix. For SITL:

```bash
param set SIM_GPS_DISABLE 0
reboot
```

---

## Example 4: Mode Change Failure

**Scenario:** Switching to AUTO mode fails, stays in MANUAL.

```gdb
(gdb) break Plane::set_mode
(gdb) run

(gdb) step  # into new_mode->enter()

(gdb) print mission.num_commands()
$4 = 0
# Returns false: "No mission loaded"
```

**Root Cause:** No mission loaded. AUTO mode requires a valid mission.

**Fix:**

```bash
wp load missions/test_mission.txt
```

---

## Example 5: Sensor Reading Issues

**Scenario:** Barometer reads 0, altitude jumps wildly.

```gdb
(gdb) break AP_Baro::update
(gdb) commands 1
> silent
> printf "Baro[0] Press: %f, Temp: %f\n", _sensor[0].pressure, _sensor[0].temperature
> continue
> end

(gdb) run
Baro[0] Press: 0.000000, Temp: 0.000000

(gdb) print _num_sensors
$1 = 0
```

**Root Cause:** No barometer detected during init. For SITL:

```bash
param set SIM_BARO_DISABLE 0
reboot
```

---

## Example 6: Memory Corruption Detection

**Scenario:** Random crashes, variables changing unexpectedly.

```gdb
(gdb) watch control_mode
(gdb) continue

Hardware watchpoint 2: control_mode
Old value = Plane::Mode::Number::MANUAL
New value = Plane::Mode::Number::12345
0x555555bbccdd in some_buggy_function ()

(gdb) backtrace
#1  buffer_overflow ()

(gdb) list
236         strcpy(buffer, very_long_string);  // BUG: No bounds check!
```

**Fix:**

```cpp
// Before (unsafe)
strcpy(buffer, very_long_string);

// After (safe)
strncpy(buffer, very_long_string, sizeof(buffer) - 1);
buffer[sizeof(buffer) - 1] = '\0';
```

---

## Example 7: Infinite Loop Investigation

**Scenario:** Vehicle hangs during initialization, never completes boot.

```gdb
(gdb) run
# Press Ctrl+C
^C
Program received signal SIGINT, Interrupt.
0x555555889900 in wait_for_sensor() at sensor.cpp:123
123         while (!sensor_ready()) {}

(gdb) print _sensor_handle
$2 = (void *) 0x0
```

**Root Cause:** `_sensor_handle` is NULL — sensor never initialized.

**Fix:**

```cpp
// Before (hangs forever)
void wait_for_sensor() {
    while (!sensor_ready()) {}
}

// After (timeout protection)
bool wait_for_sensor(uint32_t timeout_ms) {
    uint32_t start_ms = AP_HAL::millis();
    while (!sensor_ready()) {
        if (AP_HAL::millis() - start_ms > timeout_ms) {
            gcs().send_text(MAV_SEVERITY_ERROR, "Sensor init timeout");
            return false;
        }
        hal.scheduler->delay(10);
    }
    return true;
}
```

---

## Common GDB Patterns

### Conditional Logging

```gdb
(gdb) break update_function
(gdb) commands
> silent
> if (error_condition)
>   printf "ERROR: variable = %d\n", variable
>   backtrace
> end
> continue
> end
```

### Monitor Variable Changes

```gdb
(gdb) watch important_variable
(gdb) commands
> backtrace 1
> continue
> end
```

### Count Function Calls

```gdb
(gdb) break expensive_function
(gdb) commands
> silent
> set $count = $count + 1
> continue
> end
(gdb) set $count = 0
(gdb) run
# Ctrl+C
(gdb) print $count
```

---

- [GDB Command Reference](GDB_COMMAND_REFERENCE.md)
- [ArduPilot Debugging Documentation](https://ardupilot.org/dev/docs/debugging.html)
