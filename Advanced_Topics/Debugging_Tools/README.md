# Debugging Tools and Techniques

## Overview

Master essential debugging tools and techniques for ArduPilot development, including GDB debugging, memory analysis, printf debugging, and hardware debugging with real flight controllers [1].

Effective debugging is critical for identifying issues, understanding code behavior, and developing robust features. This module covers both software (SITL) and hardware debugging approaches.

## Prerequisites

Before starting this module, you should have:

- ArduPilot built from source for SITL
- Understanding of C++ programming
- Basic Linux command line skills
- Familiarity with ArduPilot architecture
- (Optional) Hardware flight controller for hardware debugging

## What You'll Learn

By completing this module, you will:

- Use GDB to debug ArduPilot in SITL
- Set breakpoints and inspect variables
- Analyze stack traces and core dumps
- Use Valgrind for memory leak detection
- Enable and use Address Sanitizer (ASAN)
- Implement printf-style debugging
- Set up hardware debugging with gdbserver
- Debug common ArduPilot issues

## Key Concepts

### Debugging Levels

**1. Printf Debugging** - Quick, simple, requires no tools
**2. GDB Debugging** - Interactive, powerful, steep learning curve
**3. Memory Analysis** - Valgrind, ASAN for memory issues
**4. Hardware Debugging** - Real-time debugging on actual hardware

### GDB (GNU Debugger)

GDB allows [1]:
- Setting breakpoints to pause execution
- Stepping through code line-by-line
- Inspecting variable values
- Examining call stacks
- Analyzing crashes and segfaults

### Address Sanitizer (ASAN)

ASAN detects [2]:
- Buffer overflows
- Use-after-free errors
- Memory leaks
- Stack/heap corruption

## Hands-On Practice

### Exercise 1: Basic GDB Debugging in SITL

Debug ArduPlane using GDB:

```bash
cd ~/ardupilot/ArduPlane

# Build with debug symbols
../Tools/autotest/sim_vehicle.py -v ArduPlane --debug --gdb

# GDB will start automatically
# At (gdb) prompt, type:
run

# ArduPilot starts running
# Press Ctrl+C to pause execution
```

**Basic GDB commands:**
```
(gdb) break AP_AHRS::update          # Set breakpoint
(gdb) continue                       # Continue execution
(gdb) next                           # Step over
(gdb) step                           # Step into
(gdb) print variable_name            # Print variable
(gdb) backtrace                      # Show call stack
(gdb) quit                           # Exit GDB
```

### Exercise 2: Set Breakpoints and Inspect Variables

```bash
# Start SITL with GDB
sim_vehicle.py -v ArduPlane --debug --gdb

# In GDB:
(gdb) break Plane::update_navigation
(gdb) run

# When breakpoint hit:
(gdb) print location
(gdb) print target_altitude_cm
(gdb) print control_mode
(gdb) backtrace

# Continue execution
(gdb) continue
```

**Expected Result:** Execution pauses at breakpoint, you can inspect variables.

### Exercise 3: Conditional Breakpoints

Set breakpoints that only trigger under specific conditions:

```bash
(gdb) break AP_GPS::update if num_sats < 6
(gdb) run

# Breakpoint only triggers when GPS has fewer than 6 satellites
```

**Use Cases:**
- Debug rare conditions
- Investigate specific parameter values
- Analyze error states

### Exercise 4: Analyze Segmentation Fault

Investigate a crash:

```bash
# Simulate a crash scenario
sim_vehicle.py -v ArduPlane --debug --gdb

(gdb) run
# Wait for crash or trigger it

# When crash occurs:
(gdb) backtrace              # Show where crash happened
(gdb) frame 0                # Go to crash frame
(gdb) info locals            # Show local variables
(gdb) print this             # Examine object state
```

**Expected Output:**
```
Program received signal SIGSEGV, Segmentation fault.
0x00007ffff7a1234 in AP_GPS::update()
(gdb) backtrace
#0  AP_GPS::update() at libraries/AP_GPS/AP_GPS.cpp:234
#1  Plane::update_GPS() at ArduPlane/Plane.cpp:456
```

### Exercise 5: Printf Debugging

Add debug output without GDB:

```cpp
// In ArduPlane/Plane.cpp
void Plane::update() {
    // Add debug output
    hal.console->printf("Mode: %d, Alt: %d\n",
                        (int)control_mode,
                        (int)current_loc.alt);

    // Or use GCS message
    gcs().send_text(MAV_SEVERITY_INFO, "Debug: value=%d", some_value);
}
```

**Rebuild and test:**
```bash
./waf plane
cd ArduPlane
sim_vehicle.py --console
# Watch debug output in console
```

### Exercise 6: Enable Address Sanitizer (ASAN)

Detect memory issues automatically:

```bash
cd ~/ardupilot

# Configure with ASAN enabled
./waf configure --board sitl --debug --enable-sanitize

# Build
./waf plane

# Run SITL
cd ArduPlane
sim_vehicle.py

# ASAN will report any memory issues detected
```

**Expected Output (if issue found):**
```
=================================================================
==12345==ERROR: AddressSanitizer: heap-buffer-overflow
READ of size 4 at 0x603000000010 thread T0
    #0 0x7ffff in AP_GPS::update()
```

### Exercise 7: Valgrind Memory Analysis

Check for memory leaks:

```bash
# Build SITL
cd ~/ardupilot
./waf configure --board sitl
./waf plane

# Run with Valgrind
cd ArduPlane
valgrind --leak-check=full --show-leak-kinds=all ./arduplane --model quad

# Let run for 30 seconds, then Ctrl+C
# Valgrind reports memory leaks and issues
```

**Look for:**
- Memory leaks ("definitely lost")
- Invalid reads/writes
- Use of uninitialized values

## Hardware Debugging

### Setup GDB with Hardware Flight Controller

Debug code running on real hardware:

**1. Build with debugging enabled:**
```bash
./waf configure --board Pixhawk1 --debug
./waf plane
```

**2. Flash firmware to flight controller**

**3. Connect with gdbserver:**
```bash
# On companion computer connected to flight controller
arm-none-eabi-gdbserver :3333 /dev/ttyACM0

# On development machine
arm-none-eabi-gdb build/Pixhawk1/bin/arduplane
(gdb) target remote <IP>:3333
(gdb) break main
(gdb) continue
```

**Note:** Hardware debugging requires JTAG/SWD debugger (ST-Link, J-Link, Black Magic Probe).

## Common Debugging Scenarios

### Debug Pre-Arm Check Failure

```bash
# Start with GDB
sim_vehicle.py -v ArduPlane --debug --gdb

# Set breakpoint in pre-arm checks
(gdb) break AP_Arming::pre_arm_checks
(gdb) run

# Try to arm in MAVProxy
# When breakpoint hit:
(gdb) print why_not_arming
(gdb) backtrace
```

### Debug EKF Issues

```bash
(gdb) break AP_NavEKF3::checkLaneSwitch
(gdb) run

# When EKF switches lanes or reports issue:
(gdb) print _health_status
(gdb) print _ekf_core[0]->_fault_status
```

### Debug Mode Changes

```bash
(gdb) break Plane::set_mode
(gdb) run

# Try changing modes
# Inspect why mode change succeeded/failed
(gdb) print control_mode
(gdb) print new_mode
```

## Common Issues

### Issue: GDB Doesn't Start

**Symptoms:** `sim_vehicle.py --gdb` starts SITL without GDB

**Solution:**
```bash
# Verify GDB installed
which gdb
sudo apt-get install gdb

# Use --debug and --gdb together
sim_vehicle.py -v ArduPlane --debug --gdb
```

### Issue: No Debug Symbols

**Symptoms:** GDB shows "No debugging symbols found"

**Solution:**
```bash
# Build with debug symbols
./waf configure --board sitl --debug
./waf clean
./waf plane
```

### Issue: ASAN False Positives

**Symptoms:** ASAN reports issues in system libraries

**Solution:**
```bash
# Use suppressions file
export ASAN_OPTIONS=suppressions=asan_suppressions.txt

# Or disable ASAN for specific checks
export ASAN_OPTIONS=detect_leaks=0
```

## GDB Command Reference

### Breakpoints

```
break function_name          # Break at function
break file.cpp:123          # Break at line
break Class::method         # Break at method
delete 1                    # Delete breakpoint 1
info breakpoints            # List breakpoints
```

### Execution Control

```
run                         # Start program
continue (c)                # Continue execution
next (n)                    # Step over
step (s)                    # Step into
finish                      # Run until function returns
until                       # Run until line
```

### Inspection

```
print variable              # Print variable
print *pointer              # Dereference pointer
info locals                 # Show local variables
info args                   # Show function arguments
backtrace (bt)              # Show call stack
frame 2                     # Switch to frame 2
list                        # Show source code
```

### Advanced

```
watch variable              # Break when variable changes
catch throw                 # Break on exception
set variable = value        # Modify variable
call function()             # Call function
```

## Debugging Tips

### 1. Start with Printf Debugging

Quick to implement, no tools needed. Good for initial investigation.

### 2. Use Meaningful Debug Messages

```cpp
// Bad
hal.console->printf("Value: %d\n", x);

// Good
hal.console->printf("GPS: lat=%f lon=%f sats=%d\n",
                    lat, lon, num_sats);
```

### 3. Check Logs First

Many issues visible in dataflash logs. Check logs before deep debugging.

### 4. Isolate the Problem

Narrow down to specific function or module before debugging.

### 5. Test in SITL First

Debug in SITL before testing on hardware. Faster iteration, safer.

## Additional Resources

- [ArduPilot Debugging Guide](https://ardupilot.org/dev/docs/debugging.html) [1] - Official debugging docs
- [GDB Tutorial](https://www.gdbtutorial.com/) [2] - GDB basics
- [Valgrind Manual](https://valgrind.org/docs/manual/index.html) [3] - Memory debugging
- [Address Sanitizer](https://github.com/google/sanitizers/wiki/AddressSanitizer) [4] - ASAN documentation

## Next Steps

After mastering debugging tools:

1. **Performance Optimization** - Profile and optimize code
2. **Testing & CI/CD** - Write automated tests
3. **Code Contribution** - Debug and fix open issues
4. **Flight Log Analysis** - Analyze logs to identify issues

---

**Sources:**

[1] https://ardupilot.org/dev/docs/debugging.html
[2] https://sourceware.org/gdb/documentation/
[3] https://valgrind.org/docs/manual/index.html
[4] https://github.com/google/sanitizers/wiki/AddressSanitizer
