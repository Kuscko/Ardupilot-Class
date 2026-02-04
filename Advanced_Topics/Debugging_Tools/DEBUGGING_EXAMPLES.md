# GDB Debugging Examples for ArduPilot

Practical debugging sessions showing real-world scenarios and solutions.

**Author:** Patrick Kelly (@Kuscko)
**Version:** 1.0
**Last Updated:** 2026-02-03

---

## Table of Contents

1. [Example 1: Debugging a Segmentation Fault](#example-1-debugging-a-segmentation-fault)
2. [Example 2: GPS Not Acquiring Fix](#example-2-gps-not-acquiring-fix)
3. [Example 3: EKF Variance Error](#example-3-ekf-variance-error)
4. [Example 4: Mode Change Failure](#example-4-mode-change-failure)
5. [Example 5: Sensor Reading Issues](#example-5-sensor-reading-issues)
6. [Example 6: Memory Corruption Detection](#example-6-memory-corruption-detection)
7. [Example 7: Infinite Loop Investigation](#example-7-infinite-loop-investigation)

---

## Example 1: Debugging a Segmentation Fault

### Scenario
ArduPlane crashes immediately after arming with a segmentation fault.

### Debug Session

```bash
# Start SITL with GDB
$ cd ~/ardupilot/ArduPlane
$ sim_vehicle.py --gdb

# GDB starts automatically
GNU gdb (Ubuntu 12.1-0ubuntu1) 12.1
(gdb)
```

#### Step 1: Run until crash

```gdb
(gdb) run
Starting program: /home/user/ardupilot/build/sitl/bin/arduplane --model quadplane

[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
[New Thread 0x7ffff6800000 (LWP 12345)]

Program received signal SIGSEGV, Segmentation fault.
0x000055555566abcd in AP_AHRS_NavEKF::update (this=0x555555aabbcc) at ../../libraries/AP_AHRS/AP_AHRS_NavEKF.cpp:234
234         ekf.getPosition(position);
```

#### Step 2: Examine the backtrace

```gdb
(gdb) backtrace
#0  0x000055555566abcd in AP_AHRS_NavEKF::update (this=0x555555aabbcc)
    at ../../libraries/AP_AHRS/AP_AHRS_NavEKF.cpp:234
#1  0x000055555567def0 in Plane::update_AHRS (this=0x555555998877)
    at ../../ArduPlane/system.cpp:156
#2  0x000055555568fedc in Plane::update (this=0x555555998877)
    at ../../ArduPlane/Plane.cpp:123
#3  0x00005555556789ab in Plane::loop (this=0x555555998877)
    at ../../ArduPlane/ArduPlane.cpp:89
#4  0x000055555569cdef in AP_HAL::Scheduler::loop (this=0x555555776655)
    at ../../libraries/AP_HAL/Scheduler.cpp:45
#5  0x00005555555abcde in main (argc=3, argv=0x7fffffffe0a8)
    at ../../ArduPlane/main.cpp:12
```

**Analysis:** Crash occurs in `AP_AHRS_NavEKF::update()` when calling `ekf.getPosition()`.

#### Step 3: Examine the crash location

```gdb
(gdb) frame 0
#0  0x000055555566abcd in AP_AHRS_NavEKF::update (this=0x555555aabbcc)
    at ../../libraries/AP_AHRS/AP_AHRS_NavEKF.cpp:234
234         ekf.getPosition(position);

(gdb) list
229     void AP_AHRS_NavEKF::update(void)
230     {
231         // Update EKF
232         ekf.UpdateFilter();
233
234         ekf.getPosition(position);
235
236         // Update DCM
237         update_DCM();
238     }
```

#### Step 4: Inspect variables

```gdb
(gdb) print this
$1 = (AP_AHRS_NavEKF * const) 0x555555aabbcc

(gdb) print ekf
$2 = {_ekf_type = 3, _ekf3 = 0x0, core = {0x0, 0x0, 0x0}}

(gdb) print ekf._ekf3
$3 = (NavEKF3 *) 0x0
```

**Root Cause:** The EKF3 object pointer is NULL! The EKF hasn't been initialized.

#### Step 5: Find initialization issue

```gdb
(gdb) break AP_AHRS_NavEKF::init
Breakpoint 1 at 0x555555667788: file ../../libraries/AP_AHRS/AP_AHRS_NavEKF.cpp, line 45.

(gdb) run
Breakpoint 1, AP_AHRS_NavEKF::init (this=0x555555aabbcc)
    at ../../libraries/AP_AHRS/AP_AHRS_NavEKF.cpp:45
45      void AP_AHRS_NavEKF::init(void)

(gdb) next
46      {
(gdb) next
47          if (_ekf_type == 3) {
(gdb) print _ekf_type
$4 = 0

(gdb) next
51          }
```

**Solution:** `_ekf_type` is 0, so EKF3 initialization is skipped. Check `AHRS_EKF_TYPE` parameter is set correctly (should be 3 for EKF3).

### Fix

```bash
# Set parameter in SITL
param set AHRS_EKF_TYPE 3
param save
reboot
```

---

## Example 2: GPS Not Acquiring Fix

### Scenario
GPS shows 0 satellites in SITL, vehicle won't arm.

### Debug Session

```gdb
# Start SITL with GDB
$ sim_vehicle.py --gdb

(gdb) break AP_GPS::update
Breakpoint 1 at 0x555555678abc

(gdb) run
[...vehicle boots...]

Breakpoint 1, AP_GPS::update (this=0x555555ddeeff)
    at ../../libraries/AP_GPS/AP_GPS.cpp:456

(gdb) print num_instances
$1 = 1

(gdb) print state[0].status
$2 = AP_GPS::GPS_Status::NO_GPS

(gdb) print _drivers[0]
$3 = (AP_GPS_Backend *) 0x555555ffeedd

(gdb) print *_drivers[0]
$4 = {<AP_GPS_Backend> = {_frontend = 0x555555ddeeff, _state = @0x555555ddeeff,
    _instance = 0, ...}}

# Step through update to see what happens
(gdb) step
AP_GPS_UBLOX::read (this=0x555555ffeedd)
    at ../../libraries/AP_GPS/AP_GPS_UBLOX.cpp:234

(gdb) next
235         uint8_t data;
(gdb) next
236         while (_port->available()) {

(gdb) print _port->available()
$5 = 0
```

**Analysis:** GPS port has no data available. Serial connection issue.

```gdb
(gdb) print _port
$6 = (AP_HAL::UARTDriver *) 0x555555aabbcc

(gdb) print _port->is_initialized()
$7 = false
```

**Root Cause:** GPS UART port not initialized.

```gdb
# Check serial manager configuration
(gdb) break AP_SerialManager::find_serial
Breakpoint 2 at 0x555555889900

(gdb) continue
Breakpoint 2, AP_SerialManager::find_serial (this=0x555555776655, protocol=5, instance=0)

(gdb) print protocol
$8 = AP_SerialManager::SerialProtocol::GPS

(gdb) finish
Run till exit from #0  AP_SerialManager::find_serial (...)
0x555555667788 in AP_GPS::init()

(gdb) print $rax
$9 = 0x0
```

**Solution:** `find_serial()` returned NULL. GPS serial port not configured in `SERIAL*_PROTOCOL` parameters.

### Fix

```bash
# Check serial parameters
param show SERIAL*_PROTOCOL
param set SERIAL3_PROTOCOL 5  # GPS on SERIAL3
param set SERIAL3_BAUD 115200
param save
reboot
```

---

## Example 3: EKF Variance Error

### Scenario
Vehicle logs show "EKF3 IMU1 stopped aiding" and won't arm.

### Debug Session

```gdb
(gdb) break NavEKF3::UpdateFilter
Breakpoint 1 at 0x555555990011

(gdb) commands 1
> silent
> printf "EKF3 Update - GPS Status: %d, Sats: %d\n", gps.status(), gps.num_sats()
> continue
> end

(gdb) run
[...messages scroll by...]
EKF3 Update - GPS Status: 0, Sats: 0
EKF3 Update - GPS Status: 0, Sats: 0
[...continues...]
```

**Analysis:** GPS status is 0 (NO_GPS), no satellites.

```gdb
# Set breakpoint on EKF health check
(gdb) delete 1
(gdb) break NavEKF3::healthy
Breakpoint 2 at 0x555555991122

(gdb) continue
Breakpoint 2, NavEKF3::healthy (this=0x555555ccddee)

(gdb) print _gps_check_fail_status
$1 = {nsats = true, hdop = true, hacc = true, vacc = true, sacc = true,
      yaw = false, pos_drift = false, pos_horiz_abs = false, ...}

(gdb) print gps.num_sensors()
$2 = 1

(gdb) print gps.status(0)
$3 = AP_GPS::GPS_Status::NO_GPS
```

**Root Cause:** GPS has no fix, failing EKF pre-arm checks.

```gdb
# Check GPS configuration
(gdb) break AP_GPS_UBLOX::_parse_gps
Breakpoint 3 at 0x555555887766

(gdb) continue
[...no breakpoint hit...]
```

**Analysis:** GPS parsing never called - no data from GPS module.

### Solution

This is the same issue as Example 2 - GPS serial port not configured. Additionally:

```gdb
# Check if simulated GPS is enabled in SITL
(gdb) print _sitl
$4 = (SITL::SIM *) 0x0
```

For SITL, ensure GPS simulation is enabled:

```bash
# SITL startup
sim_vehicle.py --console --map --aircraft test1
# Enable simulated GPS
param set SIM_GPS_DISABLE 0
reboot
```

---

## Example 4: Mode Change Failure

### Scenario
Switching to AUTO mode fails, stays in MANUAL.

### Debug Session

```gdb
(gdb) break Plane::set_mode
Breakpoint 1 at 0x555555778899

(gdb) run
[...wait for mode change attempt...]

Breakpoint 1, Plane::set_mode (this=0x555555aabbcc, mode=Mode::Number::AUTO,
    reason=ModeReason::RC_COMMAND) at ../../ArduPlane/mode.cpp:123

(gdb) next
124     {
(gdb) next
125         if (mode == control_mode) {
(gdb) print mode
$1 = Plane::Mode::Number::AUTO

(gdb) print control_mode
$2 = Plane::Mode::Number::MANUAL

(gdb) next
129         Mode *new_mode = plane.mode_from_mode_num(mode);
(gdb) next
130         if (new_mode == nullptr) {
(gdb) print new_mode
$3 = (Plane::Mode *) 0x555555ddeeff

(gdb) next
135         if (!new_mode->enter()) {
(gdb) step
Plane::ModeAuto::enter (this=0x555555ddeeff)
    at ../../ArduPlane/mode_auto.cpp:45

(gdb) next
46      {
(gdb) next
47          if (mission.num_commands() < 2) {
(gdb) print mission.num_commands()
$4 = 0

(gdb) next
48              gcs().send_text(MAV_SEVERITY_WARNING, "No mission loaded");
(gdb) next
49              return false;
```

**Root Cause:** No mission loaded, AUTO mode requires valid mission.

### Solution

```bash
# Load a mission before switching to AUTO
wp load missions/test_mission.txt
# Or create a simple mission
wp clear
wp add 0 0 16 0 0 0 0 -35.363261 149.165237 584 1
wp add 1 0 16 0 0 0 0 -35.363261 149.166237 100 1
wp add 2 0 20 0 0 0 0 0 0 0 1
```

---

## Example 5: Sensor Reading Issues

### Scenario
Barometer readings are stuck at 0, altitude jumps wildly.

### Debug Session

```gdb
(gdb) break AP_Baro::update
Breakpoint 1 at 0x555555665544

(gdb) commands 1
> silent
> printf "Baro[0] Press: %f, Temp: %f\n", _sensor[0].pressure, _sensor[0].temperature
> continue
> end

(gdb) run
[...output scrolls...]
Baro[0] Press: 0.000000, Temp: 0.000000
Baro[0] Press: 0.000000, Temp: 0.000000
Baro[0] Press: 0.000000, Temp: 0.000000
```

**Analysis:** Barometer reads zero constantly.

```gdb
(gdb) delete 1
(gdb) break AP_Baro_Backend::_copy_to_frontend
Breakpoint 2 at 0x555555666777

(gdb) continue
[...breakpoint never hit...]
```

**Analysis:** Backend never copies data to frontend - sensor not updating.

```gdb
(gdb) break AP_Baro::init
Breakpoint 3 at 0x555555667788

(gdb) run
Breakpoint 3, AP_Baro::init (this=0x555555998877)

(gdb) next
[...step through init...]

(gdb) print _num_sensors
$1 = 0
```

**Root Cause:** No barometer sensors detected during init.

```gdb
# Check what sensors are being probed
(gdb) break AP_Baro::_probe_i2c_barometers
Breakpoint 4 at 0x555555668899

(gdb) continue
Breakpoint 4, AP_Baro::_probe_i2c_barometers (this=0x555555998877)

(gdb) step
[...shows I2C probe sequence...]

(gdb) print hal.i2c_mgr->get_device(0, 0x76)
$2 = (AP_HAL::OwnPtr<AP_HAL::I2CDevice>) nullptr
```

**Solution:** I2C barometer not found. For SITL:

```bash
# Enable simulated barometer
param set SIM_BARO_DISABLE 0
reboot
```

For hardware: Check I2C connections, try different I2C addresses.

---

## Example 6: Memory Corruption Detection

### Scenario
Random crashes, variables changing unexpectedly.

### Debug Session

```gdb
# Use watchpoints to detect memory writes
(gdb) break Plane::setup
Breakpoint 1 at 0x555555778899

(gdb) run
Breakpoint 1, Plane::setup()

# Set watchpoint on critical variable
(gdb) watch control_mode
Hardware watchpoint 2: control_mode

(gdb) continue
Hardware watchpoint 2: control_mode

Old value = Plane::Mode::Number::INITIALISING
New value = Plane::Mode::Number::MANUAL
Plane::set_mode (this=0x555555aabbcc, mode=Mode::Number::MANUAL,
    reason=ModeReason::INITIALISED)
```

This is expected. Continue monitoring.

```gdb
(gdb) continue
Hardware watchpoint 2: control_mode

Old value = Plane::Mode::Number::MANUAL
New value = Plane::Mode::Number::12345
0x555555bbccdd in some_buggy_function ()

(gdb) backtrace
#0  0x555555bbccdd in some_buggy_function ()
#1  0x555555ccddee in buffer_overflow ()
```

**Root Cause:** Invalid mode value (12345) indicates memory corruption. Check for buffer overflows in the call stack.

```gdb
(gdb) frame 1
#1  0x555555ccddee in buffer_overflow ()

(gdb) list
234     void buffer_overflow() {
235         char buffer[10];
236         strcpy(buffer, very_long_string);  // BUG: No bounds check!
237     }
```

### Solution

Fix buffer overflow by using safe string functions:

```cpp
// Before (unsafe)
strcpy(buffer, very_long_string);

// After (safe)
strncpy(buffer, very_long_string, sizeof(buffer) - 1);
buffer[sizeof(buffer) - 1] = '\0';
```

---

## Example 7: Infinite Loop Investigation

### Scenario
Vehicle hangs during initialization, never completes boot.

### Debug Session

```gdb
(gdb) run
[...program hangs...]

# Press Ctrl+C to interrupt
^C
Program received signal SIGINT, Interrupt.
0x555555889900 in wait_for_sensor() at sensor.cpp:123
123         while (!sensor_ready()) {}
```

**Analysis:** Stuck in infinite loop waiting for sensor.

```gdb
(gdb) backtrace
#0  0x555555889900 in wait_for_sensor() at sensor.cpp:123
#1  0x555555778899 in init_sensors() at init.cpp:45
#2  0x555555667788 in Plane::setup() at ArduPlane.cpp:89

(gdb) print sensor_ready()
$1 = false

# Set conditional breakpoint to see if it ever becomes true
(gdb) break sensor.cpp:123 if sensor_ready() == true
Breakpoint 1 at 0x555555889900

(gdb) continue
[...never hits breakpoint - sensor_ready() never returns true...]

# Investigate why sensor isn't ready
(gdb) break sensor_ready
Breakpoint 2 at 0x555555990011

(gdb) continue
Breakpoint 2, sensor_ready() at sensor.cpp:234

(gdb) step
235     {
(gdb) next
236         return (_sensor_handle != nullptr && _sensor_initialized);
(gdb) print _sensor_handle
$2 = (void *) 0x0

(gdb) print _sensor_initialized
$3 = false
```

**Root Cause:** `_sensor_handle` is NULL, sensor was never initialized. Infinite loop because code assumes sensor will eventually initialize.

### Solution

Add timeout to prevent infinite loop:

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

### Pattern 1: Conditional Logging

```gdb
# Log only when specific condition occurs
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

### Pattern 2: Monitor Variable Changes

```gdb
# Track all changes to a variable
(gdb) watch important_variable
(gdb) commands
> backtrace 1
> continue
> end
```

### Pattern 3: Performance Profiling

```gdb
# Count how many times a function is called
(gdb) break expensive_function
(gdb) commands
> silent
> set $count = $count + 1
> continue
> end
(gdb) set $count = 0
(gdb) run
# After some time: Ctrl+C
(gdb) print $count
$1 = 1234567  # Called over 1 million times!
```

---

## Tips for Effective Debugging

1. **Start with backtrace**: Always run `bt` immediately after a crash to see the call stack
2. **Examine variables**: Use `print` to inspect variables at crash location
3. **Use watchpoints**: For mysterious variable changes, set watchpoints to catch writes
4. **Add strategic breakpoints**: Break at function entry points to trace execution flow
5. **Use conditional breaks**: Only stop when specific conditions are met to reduce noise
6. **Save sessions**: Use `save breakpoints` to save your breakpoint setup for future sessions
7. **Log to file**: Use `set logging on` to capture all GDB output for later analysis
8. **Step carefully**: Use `next` to step over functions, `step` to step into them
9. **Check initialization**: Many bugs are due to uninitialized objects - check in constructors
10. **Verify assumptions**: Don't assume pointers are valid - always check for NULL

---

## Additional Resources

- [GDB Command Reference](GDB_COMMAND_REFERENCE.md)
- [ArduPilot Debugging Documentation](https://ardupilot.org/dev/docs/debugging.html)
- [GDB Official Manual](https://sourceware.org/gdb/current/onlinedocs/gdb/)

---

**Remember:** When debugging:
1. Reproduce the issue consistently
2. Form a hypothesis about the cause
3. Use GDB to test your hypothesis
4. Fix the root cause, not just symptoms
5. Test the fix thoroughly
6. Add checks to prevent similar bugs

Happy debugging!
