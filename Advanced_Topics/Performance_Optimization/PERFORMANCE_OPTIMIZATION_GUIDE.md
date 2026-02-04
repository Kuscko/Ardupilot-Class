# ArduPilot Performance Optimization Guide

## Overview

ArduPilot runs on resource-constrained embedded systems. Performance optimization ensures reliable real-time control by minimizing CPU load, memory usage, and maintaining consistent loop timing. This guide covers monitoring, profiling, and optimization techniques.

---

## Performance Fundamentals

### Real-Time Requirements

ArduPilot is a real-time system with strict timing constraints:

| Task | Target Rate | Max Latency | Criticality |
|------|-------------|-------------|-------------|
| **IMU Sampling** | 1000 Hz | 1 ms | Critical |
| **Main Loop** | 400 Hz | 2.5 ms | Critical |
| **Fast Loop** | 400 Hz | 2.5 ms | Critical |
| **EKF Update** | 50-400 Hz | Variable | High |
| **RC Input** | 50 Hz | 20 ms | High |
| **GPS Update** | 5-10 Hz | 100-200 ms | Medium |
| **Logging** | Variable | 100 ms | Low |
| **Telemetry** | 4-50 Hz | 250 ms | Low |

**Key Principle:** Fast loops must complete within their time budget to maintain control stability.

---

## Performance Monitoring

### Monitor CPU Load

**Via MAVProxy/Mission Planner:**
```bash
# In MAVProxy
status

# Output includes:
# Load: 45%  # CPU load percentage
```

**Via Parameters:**
```bash
# Check scheduler performance
param show SCHED_*

# Enable scheduler debugging
param set SCHED_DEBUG 1
param set LOG_BITMASK 1048575  # Log everything including SCHED messages
```

**In Logs (SCHED Messages):**
```bash
# Download log and analyze with MAVExplorer
mavlogdump.py --types SCHED logfile.BIN

# Look for:
# SCHED.Load - CPU load (target < 80%)
# SCHED.IntCount - Interrupt count
# SCHED.LoopTime - Loop execution time (µs)
```

### Monitor Memory Usage

**Check available memory:**
```bash
# In MAVProxy
status

# Shows:
# Mem: 123456/262144 bytes  # Used/Total
```

**Via MEMINFO messages:**
```bash
# Enable memory logging
param set LOG_BITMASK 1048575

# In logs, check MEMINFO messages
mavlogdump.py --types MEMINFO logfile.BIN

# MEMINFO.freemem - Free memory (bytes)
# MEMINFO.brkval - Heap usage
```

### Analyze Loop Timing

**Monitor main loop timing:**
```bash
# In logs, check PM (Performance Monitoring) messages
mavlogdump.py --types PM logfile.BIN

# PM.MaxT - Maximum loop time (µs)
# PM.NLon - Number of long loops (> 5% over budget)
# PM.NLoop - Total loops executed
```

**Expected values:**
- Main loop: ~2500 µs (400 Hz)
- MaxT: < 3000 µs (< 20% overrun acceptable)
- NLon: < 1% of NLoop

**Critical thresholds:**
- MaxT > 4000 µs: Performance problem
- MaxT > 5000 µs: Critical, likely stability issues
- NLon > 5% of NLoop: Investigate immediately

---

## Profiling Tools

### Built-in Profiling

**Enable scheduler profiling:**
```bash
# Set scheduler debug level
param set SCHED_DEBUG 4  # Maximum detail

# Enable comprehensive logging
param set LOG_BITMASK 1048575
param set LOG_DISARMED 1

# Fly or run test
# Download and analyze logs
```

**Analyze scheduler logs:**
```bash
# Extract SCHED messages
mavlogdump.py --types SCHED logfile.BIN > sched_analysis.txt

# Look for tasks taking excessive time
# Example SCHED message:
# SCHED: Task=EKF_Update Time=450us MaxTime=800us
```

### SITL Profiling with Valgrind

**Profile memory usage:**
```bash
# Build SITL with debug symbols
cd ~/ardupilot/ArduPlane
./waf configure --board=sitl --debug
./waf plane

# Run with Valgrind massif (heap profiler)
valgrind --tool=massif \
         --massif-out-file=massif.out \
         build/sitl/bin/arduplane \
         --model quadplane --console

# Analyze results
ms_print massif.out > massif_analysis.txt
less massif_analysis.txt
```

**Profile CPU usage:**
```bash
# Run with Callgrind (call graph profiler)
valgrind --tool=callgrind \
         --callgrind-out-file=callgrind.out \
         build/sitl/bin/arduplane \
         --model quadplane --console

# Visualize with KCachegrind
kcachegrind callgrind.out
```

### GDB Profiling

**Attach GDB to SITL:**
```bash
# Start SITL
cd ~/ardupilot/ArduPlane
sim_vehicle.py --gdb

# In GDB prompt, set breakpoints
(gdb) break AP_AHRS::update
(gdb) continue

# When breakpoint hit, inspect
(gdb) backtrace
(gdb) info locals

# Profile specific function
(gdb) set print pretty on
(gdb) call AP::scheduler().print_task_info()
```

### Perf (Linux Performance Analyzer)

**Record performance data:**
```bash
# Build SITL
./waf configure --board=sitl --debug
./waf plane

# Start SITL in background
./build/sitl/bin/arduplane --model quadplane &
SITL_PID=$!

# Record with perf
sudo perf record -F 99 -p $SITL_PID -g -- sleep 30

# Analyze results
sudo perf report

# Generate flamegraph
sudo perf script | ~/FlameGraph/stackcollapse-perf.pl | ~/FlameGraph/flamegraph.pl > flame.svg
```

---

## Common Performance Issues

### Issue 1: High CPU Load

**Symptoms:**
- SCHED.Load > 80%
- PM.MaxT > 4000 µs
- PM.NLon increasing

**Causes:**
1. **Too many enabled features**
   - Lua scripting running heavy calculations
   - Excessive logging (LOG_BITMASK too high)
   - Too many sensors enabled

2. **Inefficient code**
   - Polling instead of interrupts
   - Unnecessary calculations in fast loop
   - String operations in critical paths

**Solutions:**

**Reduce enabled features:**
```bash
# Disable Lua scripting if not needed
param set SCR_ENABLE 0

# Reduce logging
param set LOG_BITMASK 176126  # Standard instead of comprehensive

# Disable unused sensors
param set RNGFND1_TYPE 0  # Disable rangefinder if not used
param set FLOW_TYPE 0     # Disable optical flow if not used
```

**Optimize Lua scripts:**
```lua
-- BAD: String operations in fast loop
function update()
    local msg = "Altitude: " .. tostring(ahrs:get_position():alt())
    gcs:send_text(6, msg)
    return update, 20  -- 50 Hz - too fast!
end

-- GOOD: Pre-compute, run slowly
local MSG_PREFIX = "Altitude: "
function update()
    local alt = ahrs:get_position():alt() * 0.01  -- cm to m
    if alt then  -- Check nil
        gcs:send_text(6, string.format("%s%.1f", MSG_PREFIX, alt))
    end
    return update, 1000  -- 1 Hz - appropriate for GCS messages
end
```

**Disable unused modes:**
```bash
# In hwdef.dat or build configuration
define MODE_QSTABILIZE_ENABLED 0  # Disable QuadPlane modes if not used
define MODE_QHOVER_ENABLED 0
define MODE_QLOITER_ENABLED 0
```

### Issue 2: Memory Exhaustion

**Symptoms:**
- MEMINFO.freemem < 10% of total
- Random crashes or reboots
- "Out of memory" errors

**Causes:**
1. **Memory leaks** - Allocated memory not freed
2. **Large buffers** - Logging, Lua, terrain data
3. **Too many features** - Each feature uses RAM

**Solutions:**

**Reduce buffer sizes:**
```bash
# Reduce log buffer
define HAL_LOGGING_BACKENDS_DEFAULT 1  # Smaller logging backend

# Reduce terrain buffer (if used)
param set TERRAIN_SPACING 100  # Larger spacing = less memory

# Reduce Lua heap
param set SCR_HEAP_SIZE 32768  # Reduce from default 64KB
```

**Disable large features:**
```bash
# Disable terrain following
define AP_TERRAIN_AVAILABLE 0

# Disable advanced failsafe
define ADVANCED_FAILSAFE DISABLED

# Disable ADSB
define HAL_ADSB_ENABLED 0
```

**Find memory leaks (SITL):**
```bash
# Run with Valgrind memcheck
valgrind --leak-check=full \
         --show-leak-kinds=all \
         --track-origins=yes \
         --log-file=valgrind.log \
         build/sitl/bin/arduplane --model quadplane

# Check valgrind.log for leaks
grep "definitely lost" valgrind.log
```

### Issue 3: Loop Time Overruns

**Symptoms:**
- PM.MaxT > 3000 µs regularly
- PM.NLon > 5% of PM.NLoop
- Control instability

**Causes:**
1. **Slow I2C/SPI devices** - Sensors taking too long
2. **EKF updates** - Complex calculations
3. **Expensive math** - Trigonometry, square roots in fast loop

**Solutions:**

**Optimize sensor rates:**
```bash
# Reduce EKF update rate (if appropriate)
param set EK3_IMU_MASK 1  # Use only first IMU

# Reduce barometer sampling
param set BARO_EXT_BUS -1  # Use internal baro (faster I2C bus)
```

**Move calculations to slow loop:**
```cpp
// BAD: Heavy calculation in fast loop (400 Hz)
void Plane::update_fast_loop() {
    // This runs every 2.5ms!
    float distance = calculate_distance_to_home();  // Expensive!
    log_distance(distance);
}

// GOOD: Move to slow loop (10 Hz)
void Plane::update_slow_loop() {
    // This runs every 100ms
    if (should_log_distance()) {
        float distance = calculate_distance_to_home();
        log_distance(distance);
    }
}
```

**Cache expensive calculations:**
```cpp
// BAD: Recalculate every time
float get_ground_speed() {
    return sqrt(gps.velocity_north * gps.velocity_north +
                gps.velocity_east * gps.velocity_east);
}

// GOOD: Cache and update periodically
class GPSCache {
    float cached_ground_speed;
    uint32_t last_update_ms;

    float get_ground_speed() {
        uint32_t now = AP_HAL::millis();
        if (now - last_update_ms > 100) {  // Update at 10 Hz
            cached_ground_speed = sqrt(gps.velocity_north * gps.velocity_north +
                                      gps.velocity_east * gps.velocity_east);
            last_update_ms = now;
        }
        return cached_ground_speed;
    }
};
```

### Issue 4: I2C/SPI Bus Contention

**Symptoms:**
- Occasional sensor read failures
- "I2C timeout" errors
- Inconsistent sensor data

**Causes:**
1. **Too many devices on one bus**
2. **Slow I2C clock speed**
3. **Long I2C cables**

**Solutions:**

**Spread devices across buses:**
```
# In hwdef.dat
# BAD: All sensors on I2C1
BARO MS56XX I2C:0:0x76
COMPASS AK8963 I2C:0:0x0c
RANGEFINDER LIDAR I2C:0:0x62

# GOOD: Distribute across buses
BARO MS56XX I2C:0:0x76      # Internal I2C
COMPASS AK8963 SPI:mpu9250   # Use SPI instead
RANGEFINDER LIDAR I2C:1:0x62 # External I2C bus
```

**Increase I2C clock speed (if hardware supports):**
```cpp
// In hwdef.dat
define HAL_I2C_INTERNAL_CLOCK 400000  # 400 kHz (default 100 kHz)
```

**Use SPI instead of I2C where possible:**
- SPI is faster and more reliable
- SPI doesn't suffer from bus contention
- Prefer SPI sensors for critical devices (IMU, baro)

---

## Optimization Techniques

### Code Optimization

**1. Avoid Float Division**
```cpp
// BAD: Division is slow
float result = value / 1000.0f;

// GOOD: Multiply by reciprocal
const float INV_1000 = 0.001f;
float result = value * INV_1000;
```

**2. Use Integer Math Where Possible**
```cpp
// BAD: Float math for percentages
float percent = (float)value / (float)max * 100.0f;

// GOOD: Integer math
uint8_t percent = (value * 100) / max;
```

**3. Minimize Function Calls in Loops**
```cpp
// BAD: Function call every iteration
for (int i = 0; i < get_array_size(); i++) {
    process(array[i]);
}

// GOOD: Cache result
int size = get_array_size();
for (int i = 0; i < size; i++) {
    process(array[i]);
}
```

**4. Use Lookup Tables for Trigonometry**
```cpp
// BAD: Calculate sin/cos every time
float angle_rad = degrees * DEG_TO_RAD;
float x = cos(angle_rad);
float y = sin(angle_rad);

// GOOD: Use lookup table (if angle is discrete)
// ArduPilot has optimized trig functions
float x = cosf_approx(angle_rad);  // Fast approximation
float y = sinf_approx(angle_rad);
```

**5. Compiler Optimization Flags**
```bash
# In wscript or hwdef.dat
env OPTIMIZE -O2     # Standard optimization (default)
env OPTIMIZE -O3     # Aggressive optimization (larger binary)
env OPTIMIZE -Os     # Optimize for size
env OPTIMIZE -Ofast  # Fastest (may break IEEE float compliance)
```

### Parameter Tuning for Performance

**Reduce EKF load:**
```bash
# Use single IMU (if redundancy not needed)
param set EK3_IMU_MASK 1

# Reduce EKF update rate
param set EK3_VELNE_M_NSE 0.5   # Reduce GPS velocity noise (less corrections)

# Disable unused sources
param set EK3_SRC_OPTIONS 0     # Disable all optional sources
```

**Reduce logging overhead:**
```bash
# Log only essential messages
param set LOG_BITMASK 131071    # Basic messages only

# Reduce log rate
param set LOG_FILE_RATEMAX 50   # Max 50 messages/sec
```

**Optimize RC input:**
```bash
# Reduce RC input rate if not needed
param set RC_SPEED 50           # 50 Hz instead of default (less CPU)
```

### Build-Time Optimization

**Disable unused features in hwdef.dat:**
```python
# Disable features to reduce binary size and CPU load
define HAL_PARACHUTE_ENABLED 0
define HAL_SPRAYER_ENABLED 0
define HAL_GRIPPER_ENABLED 0
define HAL_MOUNT_ENABLED 0
define HAL_RALLY_ENABLED 0
define HAL_ADSB_ENABLED 0
define AP_SCRIPTING_ENABLED 0   # Disable Lua
define AP_TERRAIN_AVAILABLE 0   # Disable terrain
define MODE_GUIDED_ENABLED 0    # Disable GUIDED if not used
```

**Compile with optimizations:**
```bash
# Configure for optimized build
./waf configure --board=MatekH743 --optimize=O3

# Build
./waf plane
```

---

## Performance Testing Workflow

### Step 1: Baseline Measurement

**Collect baseline metrics:**
```bash
# Enable comprehensive logging
param set LOG_BACKEND_TYPE 1
param set LOG_BITMASK 1048575
param set SCHED_DEBUG 4
param set LOG_DISARMED 1

# Fly standard test mission
wp load baseline_mission.waypoints
mode AUTO
arm throttle
# ... fly mission ...
disarm

# Download log
log download latest
```

**Analyze baseline:**
```bash
# Extract performance metrics
mavlogdump.py --types PM,SCHED,MEMINFO baseline.BIN > baseline_perf.txt

# Calculate statistics
grep "PM.MaxT" baseline_perf.txt | awk '{sum+=$NF; count++} END {print "Avg MaxT:", sum/count}'
grep "PM.NLon" baseline_perf.txt | tail -1
grep "SCHED.Load" baseline_perf.txt | awk '{sum+=$NF; count++} END {print "Avg Load:", sum/count}'
```

### Step 2: Apply Optimization

**Example: Disable Lua scripting**
```bash
param set SCR_ENABLE 0
param save
reboot
```

### Step 3: Re-test and Compare

**Run same test:**
```bash
wp load baseline_mission.waypoints
mode AUTO
arm throttle
# ... fly mission ...
disarm

log download latest
```

**Compare results:**
```bash
mavlogdump.py --types PM,SCHED optimized.BIN > optimized_perf.txt

# Compare MaxT
echo "Baseline:"
grep "PM.MaxT" baseline_perf.txt | awk '{sum+=$NF; count++} END {print "Avg MaxT:", sum/count, "us"}'
echo "Optimized:"
grep "PM.MaxT" optimized_perf.txt | awk '{sum+=$NF; count++} END {print "Avg MaxT:", sum/count, "us"}'

# Compare CPU load
echo "Baseline:"
grep "SCHED.Load" baseline_perf.txt | awk '{sum+=$NF; count++} END {print "Avg Load:", sum/count, "%"}'
echo "Optimized:"
grep "SCHED.Load" optimized_perf.txt | awk '{sum+=$NF; count++} END {print "Avg Load:", sum/count, "%"}'
```

### Step 4: Document and Iterate

**Document findings:**
```
Optimization: Disabled Lua scripting
Baseline CPU Load: 68%
Optimized CPU Load: 52%
Improvement: 16 percentage points
MaxT Improvement: 350 µs reduction
Trade-off: Lost custom Lua functionality
Recommendation: Enable only when needed
```

---

## Profiling Example: Finding CPU Bottleneck

### Example Scenario

**Problem:** CPU load is 85%, causing occasional control lag

**Step 1: Identify Top Tasks**
```bash
# Enable scheduler debugging
param set SCHED_DEBUG 4
param set LOG_BITMASK 1048575

# Fly and download log
# ... fly test ...
log download latest

# Analyze SCHED messages
mavlogdump.py --types SCHED logfile.BIN | grep "Task=" > tasks.txt

# Find slowest tasks
sort -t= -k3 -n tasks.txt | tail -20
```

**Example output:**
```
SCHED: Task=EKF_Update Time=780us
SCHED: Task=AP_Scripting Time=1200us
SCHED: Task=Logger Time=450us
SCHED: Task=AHRS_Update Time=320us
```

**Step 2: Analyze Top Offender**
```
AP_Scripting: 1200 µs per update
Runs at 50 Hz (every 20ms)
Total CPU time: 1200µs * 50Hz = 60,000µs/sec = 6% of CPU
```

**Step 3: Optimize**
```bash
# Reduce Lua script update rate
# Edit Lua script to run at 10 Hz instead of 50 Hz

function update()
    -- ... script logic ...
    return update, 100  -- Changed from 20ms to 100ms
end

# Or disable if not critical
param set SCR_ENABLE 0
```

**Step 4: Verify**
```bash
# Re-test
# ... fly test ...
log download latest

# Check improvement
mavlogdump.py --types SCHED logfile.BIN | grep "AP_Scripting"
# Should show reduced frequency or no entries
```

---

## Performance Optimization Checklist

### Before Flight

- [ ] Review CPU load target (< 80% for safety margin)
- [ ] Verify memory usage (> 20% free)
- [ ] Check PM.MaxT in recent logs (< 3000 µs)
- [ ] Disable unused features via parameters
- [ ] Optimize Lua scripts for efficiency
- [ ] Set appropriate logging level (not comprehensive for production)

### During Development

- [ ] Profile code with Valgrind/perf in SITL
- [ ] Measure impact of new features on CPU load
- [ ] Test with comprehensive logging enabled (worst case)
- [ ] Verify real-time performance on target hardware
- [ ] Compare performance across firmware versions
- [ ] Document performance regression tests

### Post-Flight Analysis

- [ ] Download and review performance logs
- [ ] Check for loop time overruns (PM.NLon)
- [ ] Verify CPU load stayed within budget
- [ ] Identify performance anomalies or spikes
- [ ] Correlate performance issues with flight events
- [ ] Update optimization plan based on findings

---

## Example: Build Performance Comparison Script

**Script: compare_performance.sh**
```bash
#!/bin/bash
# Compare performance between two log files

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <baseline.BIN> <optimized.BIN>"
    exit 1
fi

BASELINE=$1
OPTIMIZED=$2

echo "Performance Comparison Report"
echo "=============================="
echo ""

# Extract PM messages
mavlogdump.py --types PM "$BASELINE" > /tmp/baseline_pm.txt
mavlogdump.py --types PM "$OPTIMIZED" > /tmp/optimized_pm.txt

# Calculate average MaxT
baseline_maxt=$(grep "PM.MaxT" /tmp/baseline_pm.txt | awk '{sum+=$NF; count++} END {print sum/count}')
optimized_maxt=$(grep "PM.MaxT" /tmp/optimized_pm.txt | awk '{sum+=$NF; count++} END {print sum/count}')

echo "Average MaxT (Loop Time):"
echo "  Baseline:  ${baseline_maxt} µs"
echo "  Optimized: ${optimized_maxt} µs"
echo "  Improvement: $(echo "$baseline_maxt - $optimized_maxt" | bc) µs"
echo ""

# Extract SCHED messages
mavlogdump.py --types SCHED "$BASELINE" > /tmp/baseline_sched.txt
mavlogdump.py --types SCHED "$OPTIMIZED" > /tmp/optimized_sched.txt

# Calculate average CPU load
baseline_load=$(grep "SCHED.Load" /tmp/baseline_sched.txt | awk '{sum+=$NF; count++} END {print sum/count}')
optimized_load=$(grep "SCHED.Load" /tmp/optimized_sched.txt | awk '{sum+=$NF; count++} END {print sum/count}')

echo "Average CPU Load:"
echo "  Baseline:  ${baseline_load}%"
echo "  Optimized: ${optimized_load}%"
echo "  Improvement: $(echo "$baseline_load - $optimized_load" | bc)%"
echo ""

# Extract MEMINFO
mavlogdump.py --types MEMINFO "$BASELINE" > /tmp/baseline_mem.txt 2>/dev/null
mavlogdump.py --types MEMINFO "$OPTIMIZED" > /tmp/optimized_mem.txt 2>/dev/null

if [ -s /tmp/baseline_mem.txt ]; then
    baseline_mem=$(grep "MEMINFO.freemem" /tmp/baseline_mem.txt | awk '{sum+=$NF; count++} END {print sum/count}')
    optimized_mem=$(grep "MEMINFO.freemem" /tmp/optimized_mem.txt | awk '{sum+=$NF; count++} END {print sum/count}')

    echo "Average Free Memory:"
    echo "  Baseline:  ${baseline_mem} bytes"
    echo "  Optimized: ${optimized_mem} bytes"
    echo "  Improvement: $(echo "$optimized_mem - $baseline_mem" | bc) bytes"
fi

# Cleanup
rm /tmp/baseline_*.txt /tmp/optimized_*.txt 2>/dev/null

echo ""
echo "Analysis complete."
```

**Usage:**
```bash
chmod +x compare_performance.sh
./compare_performance.sh baseline_flight.BIN optimized_flight.BIN
```

---

## Resources

**Official Documentation:**
- [ArduPilot Performance](https://ardupilot.org/dev/docs/performance.html)
- [Scheduler Documentation](https://ardupilot.org/dev/docs/apmcopter-programming-scheduler.html)
- [Code Style Guide](https://ardupilot.org/dev/docs/code-style-guide.html)

**Profiling Tools:**
- [Valgrind](https://valgrind.org/)
- [perf](https://perf.wiki.kernel.org/)
- [FlameGraph](https://github.com/brendangregg/FlameGraph)
- [GDB](https://www.gnu.org/software/gdb/)

**Community Resources:**
- [ArduPilot Discourse - Performance Category](https://discuss.ardupilot.org/c/development/performance)
- [ArduPilot Developer Chat](https://ardupilot.org/discord)

---

**Author:** Patrick Kelly (@Kuscko)
**Version:** 1.0
**Last Updated:** 2026-02-03
