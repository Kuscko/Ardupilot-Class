# ArduPilot Debugging Guide

## GDB in SITL

**Build with debug symbols:**
```bash
cd ~/ardupilot/ArduPlane
./waf configure --board sitl --debug
./waf plane
```

**Run with GDB:**
```bash
gdb build/sitl/bin/arduplane
(gdb) run --model quad
```

**Useful GDB commands:**
```
break AP_AHRS::update  # Set breakpoint
run                    # Start program
continue               # Continue execution
print variable         # Print variable value
backtrace              # Show call stack
```

## Printf Debugging

**Add debug output:**
```cpp
#include <GCS_MAVLink/GCS.h>
gcs().send_text(MAV_SEVERITY_INFO, "Debug: value=%f", my_value);
```

## MAVLink Console

**View console messages:**
```bash
# In MAVProxy
messages
```

**Author:** Patrick Kelly (@Kuscko)
