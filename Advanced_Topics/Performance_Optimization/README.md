# Performance Optimization

ArduPilot runs on resource-constrained hardware with strict real-time requirements. Optimization ensures reliable control loops and prevents scheduler overruns.

## Hardware Performance Constraints

| Board Type  | CPU Speed | RAM   | Flash |
| ----------- | --------- | ----- | ----- |
| Pixhawk 1   | 168MHz    | 192KB | 1MB   |
| Pixhawk 4   | 216MHz    | 512KB | 2MB   |
| CubeOrange  | 480MHz    | 1MB   | 2MB   |
| Pixhawk 6X  | 480MHz    | 2MB   | 2MB   |

## Exercises

### Exercise 1: Monitor CPU and Memory Usage

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console

module load graph
graph SCHED.RunTime SCHED.Load
status
sched
param show MEM_*
```

Key log metrics: `SCHED.Load` < 90%, `SCHED.Overruns` should be minimal.

### Exercise 2: Analyze Scheduler Performance

```bash
param set LOG_BITMASK 2293759
param set SCHED_DEBUG 4
param write
reboot

mode FBWA
arm throttle
disarm
```

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

analyze_scheduler_performance("flight.BIN")
```

### Exercise 3: Profile Custom Code

```cpp
#include <AP_Profiler/AP_Profiler.h>

void MyClass::expensive_function() {
    PROFILE_MARK("MyExpensiveFunction");
    for (int i = 0; i < 1000; i++) { }
}

// Manual timing alternative
void MyClass::timed_function() {
    uint32_t start_us = AP_HAL::micros();
    do_work();
    uint32_t elapsed_us = AP_HAL::micros() - start_us;
    gcs().send_text(MAV_SEVERITY_INFO, "Function took %lu μs",
                    (unsigned long)elapsed_us);
}
```

### Exercise 4: Optimize Logging for Performance

```bash
param set LOG_BITMASK 176126
param set LOG_DISARMED 0
param set LOG_FILE_DSRMROT 1
param set INS_LOG_BAT_MASK 0
param set LOG_REPLAY 0
param write
reboot
```

| Logging Level     | CPU Impact | Use Case          |
| ----------------- | ---------- | ----------------- |
| Minimal (176126)  | ~5%        | Normal operations |
| Default (2293759) | ~15%       | Debugging         |
| Full + IMU Batch  | ~25%       | Detailed analysis |

### Exercise 5: Memory Usage Analysis

```cpp
#include <AP_HAL/AP_HAL.h>

void check_memory() {
    uint32_t free_memory = hal.util->available_memory();
    gcs().send_text(MAV_SEVERITY_INFO,
                    "Free memory: %lu bytes",
                    (unsigned long)free_memory);
}

// Use stack allocation instead of heap when possible
void good_function() {
    float buffer[10];  // Stack — fast, no fragmentation
}
```

### Exercise 6: Optimize Sensor Reading

```cpp
// Good: Read once, cache locally
void efficient_code() {
    float roll, pitch, yaw;
    ahrs.get_attitude(roll, pitch, yaw);
    process_roll(roll);
    process_pitch(pitch);
}

void fast_math_example() {
    float angle = fast_atan2f(y, x);
    int32_t angle_cdeg = degrees(angle) * 100;
}
```

### Exercise 7: Scheduler Task Optimization

```cpp
void MyClass::update_task(void) {
    uint32_t now = AP_HAL::millis();
    if (now - last_update_ms < UPDATE_INTERVAL_MS) {
        return;
    }
    last_update_ms = now;

    switch (state) {
        case STATE_INIT:
            do_fast_init();
            state = STATE_PROCESS;
            break;
        case STATE_PROCESS:
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

const AP_Scheduler::Task MyClass::scheduler_tasks[] = {
    SCHED_TASK(update_task, 50, 100),  // 50Hz, 100μs budget
};
```

## Common Issues

### High CPU Load

```bash
param set COMPASS_CAL_FIT 0
param set FENCE_ENABLE 0
param set OSD_TYPE 0
param set LOG_BITMASK 176126
param set SR0_EXTRA1 2
param set SR0_EXTRA2 2
param set EK3_IMU_MASK 1
param set SCR_ENABLE 0
param write
reboot
```

### Scheduler Overruns

```cpp
// Spread work across multiple calls
static int current_index = 0;
process(current_index);
current_index = (current_index + 1) % 1000;
```

### Memory Fragmentation

```cpp
class MyClass {
    float buffer[100];  // Fixed-size buffer — avoid dynamic allocation

public:
    void init() {
        // Pre-allocate everything at initialization
    }
};
```

### Slow I/O Operations

```bash
param set LOG_BITMASK 176126
# Use Class 10+ SD cards
# Enable DMA in board definitions
```

## Performance Best Practices

```cpp
// Const for read-only data
const float CONSTANT_VALUE = 1.234f;

// Inline for small, frequently-called functions
inline float square(float x) { return x * x; }

// Compiler attributes
__attribute__((always_inline)) void critical_function();
```

```bash
param set LOG_BITMASK 176126
param set SR0_EXTRA1 2
param set SR0_EXTRA2 2
param set SR0_POSITION 2
param set COMPASS_CAL_FIT 0
param set TERRAIN_ENABLE 0
param set AVOID_ENABLE 0
param set OSD_TYPE 0
```

## Performance Benchmark Script

```python
# benchmark_performance.py
from pymavlink import mavutil
import time

def benchmark_mission(connection_string):
    """Run performance benchmark mission"""
    master = mavutil.mavlink_connection(connection_string)
    master.wait_heartbeat()

    start_time = time.time()
    max_load = 0
    samples = 0

    while time.time() - start_time < 60:
        sys_status = master.recv_match(type='SYS_STATUS', blocking=True, timeout=1)
        if sys_status:
            load = sys_status.load / 10.0
            max_load = max(max_load, load)
            samples += 1

    print(f"Performance Benchmark Results:")
    print(f"  Max CPU Load: {max_load:.1f}%")
    print(f"  Samples: {samples}")
    print(f"  Status: {'PASS' if max_load < 80 else 'FAIL'}")

benchmark_performance('udp:127.0.0.1:14550')
```

---

- [Performance Optimization Guide](PERFORMANCE_OPTIMIZATION_GUIDE.md)
- [ArduPilot Performance](https://ardupilot.org/dev/docs/performance.html)
- [Scheduler Documentation](https://ardupilot.org/dev/docs/apmcopter-programming-scheduler.html)
- [Profiling ArduPilot](https://ardupilot.org/dev/docs/profiling.html)
