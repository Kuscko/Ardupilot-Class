# Performance Optimization

## Overview

Master ArduPilot performance monitoring and optimization to ensure reliable, efficient operation on resource-constrained hardware. Performance optimization is critical for maintaining stable flight control loops, preventing scheduler overruns, and maximizing flight controller capabilities [1].

This module covers CPU profiling, memory management, scheduler analysis, and optimization techniques for custom code and configurations.

## Prerequisites

Before starting this module, you should have:

- Completed ArduPilot build system setup
- Understanding of ArduPilot architecture
- Familiarity with C++ programming
- Development environment configured
- Basic understanding of real-time systems

## What You'll Learn

By completing this module, you will:

- Monitor CPU usage and identify bottlenecks
- Analyze scheduler performance and loop timing
- Use profiling tools to measure code execution time
- Optimize memory usage and reduce RAM consumption
- Apply performance best practices to custom code
- Configure logging for minimal performance impact
- Troubleshoot scheduler overruns and timing issues

## Key Concepts

### ArduPilot Scheduler

ArduPilot uses a cooperative multitasking scheduler [1]:

- **Main loop:** Runs at 400Hz (default for most flight controllers)
- **Fast tasks:** Critical control loops (attitude control, sensor reading)
- **Slow tasks:** Navigation, logging, telemetry
- **Scheduler timing:** Each task has priority and execution frequency

### Performance Metrics

Key performance indicators [2]:

- **CPU load:** Percentage of time spent executing tasks
- **Loop time:** Time to complete one main loop iteration
- **Scheduler overruns:** Tasks that exceed allocated time
- **Memory usage:** RAM and flash consumption
- **I/O performance:** Sensor read rates, logging throughput

### Performance Constraints

Hardware limitations to consider:

| Board Type | CPU Speed | RAM | Flash |
| ---------- | --------- | --- | ----- |
| Pixhawk 1 | 168MHz | 192KB | 1MB |
| Pixhawk 4 | 216MHz | 512KB | 2MB |
| CubeOrange | 480MHz | 1MB | 2MB |
| Pixhawk 6X | 480MHz | 2MB | 2MB |

## Hands-On Practice

### Exercise 1: Monitor CPU and Memory Usage

Check current performance metrics:

```bash
# Start SITL
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console

# Monitor scheduler performance
module load graph
graph SCHED.RunTime SCHED.Load

# Check CPU load
status

# View detailed scheduler info
sched

# Monitor memory usage
param show MEM_*
```

**Key metrics to monitor:**

```
SCHED messages in logs:
- MainLoop: Main loop timing
- Load: CPU load percentage (should be < 90%)
- RunTime: Time spent in tasks (microseconds)
- Overruns: Number of tasks exceeding time budget
```

### Exercise 2: Analyze Scheduler Performance

Profile scheduler task execution:

```bash
# Enable detailed scheduler logging
param set LOG_BITMASK 2293759  # Log everything
param set SCHED_DEBUG 4        # Enable scheduler debugging
param write
reboot

# Fly test flight
mode FBWA
arm throttle
# Fly around
disarm

# Analyze logs
cd logs
# Download latest log
```

**Python script to analyze scheduler:**

```python
# analyze_scheduler.py
from pymavlink import mavutil
import statistics

def analyze_scheduler_performance(logfile):
    """Analyze scheduler performance from flight log"""
    mlog = mavutil.mavlink_connection(logfile)

    loads = []
    overruns = []
    loop_times = []

    while True:
        msg = mlog.recv_match(type='SCHED', blocking=False)
        if msg is None:
            break

        loads.append(msg.Load)
        if hasattr(msg, 'Overruns'):
            overruns.append(msg.Overruns)
        if hasattr(msg, 'MainLoop'):
            loop_times.append(msg.MainLoop)

    if loads:
        print(f"CPU Load Statistics:")
        print(f"  Mean: {statistics.mean(loads):.1f}%")
        print(f"  Max: {max(loads):.1f}%")
        print(f"  StdDev: {statistics.stdev(loads):.1f}%")

    if loop_times:
        print(f"\nMain Loop Timing (microseconds):")
        print(f"  Mean: {statistics.mean(loop_times):.0f}μs")
        print(f"  Max: {max(loop_times):.0f}μs")
        print(f"  Target: 2500μs (400Hz)")

    if overruns:
        total_overruns = sum(overruns)
        print(f"\nScheduler Overruns: {total_overruns}")
        if total_overruns > 100:
            print("  WARNING: High overrun count!")

# Usage
analyze_scheduler_performance("flight.BIN")
```

**Expected results:**
- CPU load < 80% during normal flight
- Loop times consistently < 2500μs
- Minimal scheduler overruns

### Exercise 3: Profile Custom Code

Measure execution time of functions:

```cpp
// Custom code with profiling
#include <AP_Profiler/AP_Profiler.h>

void MyClass::expensive_function() {
    // Start profiling
    PROFILE_MARK("MyExpensiveFunction");

    // Your code here
    for (int i = 0; i < 1000; i++) {
        // Do work
    }

    // Profile automatically stops when PROFILE_MARK goes out of scope
}

// Check results in scheduler debug output
```

**Alternative manual timing:**

```cpp
void MyClass::timed_function() {
    uint32_t start_us = AP_HAL::micros();

    // Your code here
    do_work();

    uint32_t elapsed_us = AP_HAL::micros() - start_us;

    gcs().send_text(MAV_SEVERITY_INFO, "Function took %lu μs",
                    (unsigned long)elapsed_us);
}
```

### Exercise 4: Optimize Logging for Performance

Configure logging to minimize CPU impact:

```bash
# Reduce logging rate
param set LOG_BITMASK 176126   # Default logging (not everything)
param set LOG_DISARMED 0       # Don't log when disarmed

# Disable high-rate logs if not needed
param set LOG_FILE_DSRMROT 1   # Rotate logs when disarmed

# For performance testing, disable non-essential logs
param set INS_LOG_BAT_MASK 0   # Disable IMU batch logging
param set LOG_REPLAY 0         # Disable replay

param write
reboot
```

**Logging performance impact:**

| Logging Level | CPU Impact | Use Case |
| ------------- | ---------- | -------- |
| Minimal (176126) | ~5% | Normal operations |
| Default (2293759) | ~15% | Debugging |
| Full + IMU Batch | ~25% | Detailed analysis |

### Exercise 5: Memory Usage Analysis

Monitor and optimize RAM usage:

```cpp
// Check available memory
#include <AP_HAL/AP_HAL.h>

void check_memory() {
    uint32_t free_memory = hal.util->available_memory();

    gcs().send_text(MAV_SEVERITY_INFO,
                    "Free memory: %lu bytes",
                    (unsigned long)free_memory);
}

// Optimize memory usage
// Use PROGMEM for constant strings
const char msg[] PROGMEM = "This is stored in flash, not RAM";

// Use stack allocation instead of heap when possible
void good_function() {
    float buffer[10];  // Stack - fast, no fragmentation
}

void avoid_this() {
    float *buffer = new float[10];  // Heap - slower, fragments memory
    delete[] buffer;
}
```

**Memory profiling in SITL:**

```bash
# Show memory statistics
param show MEM

# In code, track allocations
# Look for memory leaks
```

### Exercise 6: Optimize Sensor Reading

Efficient sensor data access:

```cpp
// Bad: Reading sensors multiple times
void inefficient_code() {
    float roll = ahrs.roll;
    float pitch = ahrs.pitch;
    // ... later ...
    float roll2 = ahrs.roll;  // Reads sensor again!
}

// Good: Read once, cache locally
void efficient_code() {
    // Get attitude once
    float roll, pitch, yaw;
    ahrs.get_attitude(roll, pitch, yaw);

    // Use cached values
    process_roll(roll);
    process_pitch(pitch);
}

// Use faster approximations when appropriate
void fast_math_example() {
    // Avoid expensive operations in hot loops
    // Use fast_atan2 instead of atan2
    float angle = fast_atan2f(y, x);

    // Use integer math when possible
    int32_t angle_cdeg = degrees(angle) * 100;  // Centidegrees
}
```

### Exercise 7: Scheduler Task Optimization

Optimize custom scheduler tasks:

```cpp
// Create efficient scheduler task
void MyClass::update_task(void) {
    // Check if we need to run
    uint32_t now = AP_HAL::millis();
    if (now - last_update_ms < UPDATE_INTERVAL_MS) {
        return;  // Skip this iteration
    }
    last_update_ms = now;

    // Do minimal work
    // Break long operations into chunks
    switch (state) {
        case STATE_INIT:
            do_fast_init();
            state = STATE_PROCESS;
            break;

        case STATE_PROCESS:
            // Process one item per call
            if (process_next_item()) {
                state = STATE_COMPLETE;
            }
            break;

        case STATE_COMPLETE:
            finalize();
            state = STATE_INIT;
            break;
    }
}

// Register task with appropriate rate
const AP_Scheduler::Task MyClass::scheduler_tasks[] = {
    SCHED_TASK(update_task, 50, 100),  // 50Hz, 100μs budget
};
```

## Common Issues

### Issue 1: High CPU Load

**Symptoms:**
- CPU load consistently > 90%
- Sluggish control response
- Scheduler overruns

**Solutions:**

```bash
# Disable non-essential features
param set COMPASS_CAL_FIT 0    # Disable compass auto-cal
param set FENCE_ENABLE 0       # Disable fence (if not needed)
param set OSD_TYPE 0           # Disable OSD

# Reduce logging
param set LOG_BITMASK 176126

# Lower telemetry rates
param set SR0_EXTRA1 2         # Reduce attitude rate
param set SR0_EXTRA2 2         # Reduce VFR_HUD rate

# Reduce EKF rate (advanced)
param set EK3_IMU_MASK 1       # Use single IMU

# Disable scripts if running
param set SCR_ENABLE 0

param write
reboot
```

### Issue 2: Scheduler Overruns

**Symptoms:**
- SCHED.Overruns increasing
- Jittery control
- Missed sensor reads

**Solutions:**

```cpp
// Identify slow tasks
// Check SCHED messages in log

// Optimize slow code paths
// Break up long operations
void fix_overruns() {
    // Instead of:
    // for (int i = 0; i < 1000; i++) { process(i); }

    // Do:
    static int current_index = 0;
    process(current_index);
    current_index = (current_index + 1) % 1000;
    // Spreads work across multiple calls
}
```

```bash
# Increase task time budget if legitimate
# Edit scheduler table in code

# Reduce task frequency
# Lower priority tasks can run slower
```

### Issue 3: Memory Fragmentation

**Symptoms:**
- Available memory decreases over time
- Random crashes after extended operation
- Out of memory errors

**Solutions:**

```cpp
// Avoid dynamic allocation in flight code
// Pre-allocate buffers at initialization

class MyClass {
    // Good: Fixed-size buffer
    float buffer[100];

    // Avoid: Dynamic allocation
    // float *buffer = new float[size];

public:
    void init() {
        // Pre-allocate everything needed
        // One-time allocation
    }
};

// Use object pools for repeated allocations
// Reuse objects instead of new/delete
```

### Issue 4: Slow I/O Operations

**Symptoms:**
- SD card logging delays
- Telemetry lag
- Sensor timeouts

**Solutions:**

```bash
# Use DMA for I/O operations
# Configure in board definitions

# Reduce logging rate
param set LOG_BITMASK 176126

# Use faster SD cards (Class 10 or better)

# Enable I/O buffering
# Batch writes instead of single-byte writes
```

### Issue 5: Performance Regression

**Symptoms:**
- Performance worse after code changes
- New features cause overruns
- Increased memory usage

**Solutions:**

```bash
# Benchmark before and after changes
# Compare scheduler logs

# Use profiling to identify bottlenecks

# Consider trade-offs:
# - Accuracy vs speed
# - Features vs performance
# - Memory vs CPU

# Optimize hot paths
# Profile and optimize functions called frequently
```

## Performance Best Practices

### Code Optimization

1. **Minimize allocations**
   - Pre-allocate at initialization
   - Use stack over heap
   - Reuse buffers

2. **Efficient algorithms**
   - O(1) or O(log n) preferred
   - Avoid O(n²) in loops
   - Cache computed values

3. **Fast math**
   - Use integer math when possible
   - Approximate functions (fast_atan2)
   - Look-up tables for expensive operations

4. **Compiler optimization**

```cpp
// Use const for read-only data
const float CONSTANT_VALUE = 1.234f;

// Use inline for small, frequently-called functions
inline float square(float x) { return x * x; }

// Use compiler attributes
__attribute__((always_inline)) void critical_function();
```

### Configuration Optimization

```bash
# Minimal configuration for maximum performance
param set LOG_BITMASK 176126   # Reduce logging
param set SR0_EXTRA1 2         # Lower telemetry rates
param set SR0_EXTRA2 2
param set SR0_POSITION 2
param set COMPASS_CAL_FIT 0    # Disable auto-cal
param set TERRAIN_ENABLE 0     # Disable terrain (if not needed)
param set AVOID_ENABLE 0       # Disable avoidance
param set OSD_TYPE 0           # Disable OSD (if not needed)
```

## Performance Testing

### Benchmark Script

```python
# benchmark_performance.py
from pymavlink import mavutil
import time

def benchmark_mission(connection_string):
    """Run performance benchmark mission"""
    master = mavutil.mavlink_connection(connection_string)
    master.wait_heartbeat()

    # Record start time
    start_time = time.time()

    # Monitor performance
    max_load = 0
    samples = 0

    while time.time() - start_time < 60:  # 1 minute test
        msg = master.recv_match(type='SYSTEM_TIME', blocking=True, timeout=1)

        # Request scheduler info
        master.mav.command_long_send(
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN,
            0, 0, 0, 0, 0, 0, 0, 0)

        # Collect CPU load
        sys_status = master.recv_match(type='SYS_STATUS', blocking=True, timeout=1)
        if sys_status:
            load = sys_status.load / 10.0  # Convert to percentage
            max_load = max(max_load, load)
            samples += 1

    print(f"Performance Benchmark Results:")
    print(f"  Max CPU Load: {max_load:.1f}%")
    print(f"  Samples: {samples}")
    print(f"  Status: {'PASS' if max_load < 80 else 'FAIL'}")

# Usage
benchmark_performance('udp:127.0.0.1:14550')
```

## Additional Resources

- [Scheduler Overview](https://ardupilot.org/dev/docs/learning-ardupilot-threading.html) [1] - ArduPilot threading model
- [Profiling ArduPilot](https://ardupilot.org/dev/docs/profiling.html) [2] - Profiling guide
- [Code Optimization](https://ardupilot.org/dev/docs/code-overview-object-avoidance.html) - Performance patterns
- [Memory Management](https://ardupilot.org/dev/docs/learning-ardupilot-storage.html) - Storage and memory

### Development Tools

- [GDB Debugging](https://ardupilot.org/dev/docs/debugging-with-gdb.html) - Debug performance issues
- [MAVLink Inspector](https://ardupilot.org/dev/docs/mavlink-inspector.html) - Monitor message rates

## Next Steps

After mastering performance optimization:

1. **Custom Feature Development** - Build efficient custom features
2. **Advanced Logging** - Implement high-performance logging
3. **Real-Time Systems** - Deep dive into RTOS concepts
4. **Hardware Integration** - Optimize for specific hardware platforms

---

**Sources:**

[1] https://ardupilot.org/dev/docs/learning-ardupilot-threading.html
[2] https://ardupilot.org/dev/docs/profiling.html
