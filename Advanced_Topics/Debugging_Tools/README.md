# Debugging Tools and Techniques

Essential debugging tools for ArduPilot: GDB, memory analysis, printf debugging, and hardware debugging.

## Key Concepts

### Debugging Levels

1. **Printf Debugging** - Quick, no tools required, good for initial investigation
2. **GDB Debugging** - Interactive, powerful, breakpoints and variable inspection
3. **Memory Analysis** - Valgrind, ASAN for buffer overflows and memory leaks
4. **Hardware Debugging** - Real-time debugging on actual flight controller hardware

## Exercises

### Exercise 1: Basic GDB Debugging in SITL

```bash
cd ~/ardupilot/ArduPlane
../Tools/autotest/sim_vehicle.py -v ArduPlane --debug --gdb
```

```text
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
sim_vehicle.py -v ArduPlane --debug --gdb
```

```gdb
(gdb) break Plane::update_navigation
(gdb) run
(gdb) print location
(gdb) print target_altitude_cm
(gdb) print control_mode
(gdb) backtrace
(gdb) continue
```

### Exercise 3: Conditional Breakpoints

```gdb
(gdb) break AP_GPS::update if num_sats < 6
(gdb) run
```

### Exercise 4: Analyze Segmentation Fault

```bash
sim_vehicle.py -v ArduPlane --debug --gdb
```

```gdb
(gdb) run
(gdb) backtrace
(gdb) frame 0
(gdb) info locals
(gdb) print this
```

### Exercise 5: Printf Debugging

```cpp
// In ArduPlane/Plane.cpp
void Plane::update() {
    hal.console->printf("Mode: %d, Alt: %d\n",
                        (int)control_mode,
                        (int)current_loc.alt);

    gcs().send_text(MAV_SEVERITY_INFO, "Debug: value=%d", some_value);
}
```

```bash
./waf plane
sim_vehicle.py --console
```

### Exercise 6: Enable Address Sanitizer (ASAN)

```bash
cd ~/ardupilot
./waf configure --board sitl --debug --enable-sanitize
./waf plane
cd ArduPlane
sim_vehicle.py
```

ASAN output example if issue found:

```text
==12345==ERROR: AddressSanitizer: heap-buffer-overflow
READ of size 4 at 0x603000000010 thread T0
    #0 0x7ffff in AP_GPS::update()
```

### Exercise 7: Valgrind Memory Analysis

```bash
cd ~/ardupilot
./waf configure --board sitl
./waf plane

cd ArduPlane
valgrind --leak-check=full --show-leak-kinds=all ./arduplane --model quad
```

### Hardware Debugging Setup

```bash
# Build with debugging
./waf configure --board Pixhawk1 --debug
./waf plane

# On companion computer
arm-none-eabi-gdbserver :3333 /dev/ttyACM0

# On development machine
arm-none-eabi-gdb build/Pixhawk1/bin/arduplane
(gdb) target remote <IP>:3333
(gdb) break main
(gdb) continue
```

## Common Debugging Scenarios

### Debug Pre-Arm Check Failure

```bash
sim_vehicle.py -v ArduPlane --debug --gdb
```

```gdb
(gdb) break AP_Arming::pre_arm_checks
(gdb) run
(gdb) print why_not_arming
(gdb) backtrace
```

### Debug EKF Issues

```gdb
(gdb) break AP_NavEKF3::checkLaneSwitch
(gdb) run
(gdb) print _health_status
(gdb) print _ekf_core[0]->_fault_status
```

### Debug Mode Changes

```gdb
(gdb) break Plane::set_mode
(gdb) run
(gdb) print control_mode
(gdb) print new_mode
```

## Common Issues

### GDB Doesn't Start

```bash
which gdb
sudo apt-get install gdb
sim_vehicle.py -v ArduPlane --debug --gdb
```

### No Debug Symbols

```bash
./waf configure --board sitl --debug
./waf clean
./waf plane
```

### ASAN False Positives

```bash
export ASAN_OPTIONS=suppressions=asan_suppressions.txt
export ASAN_OPTIONS=detect_leaks=0
```

---

- [ArduPilot Debugging Guide](https://ardupilot.org/dev/docs/debugging.html)
- [GDB Command Reference](GDB_COMMAND_REFERENCE.md)
- [Valgrind Manual](https://valgrind.org/docs/manual/index.html)
