# ArduPilot Performance Optimization Guide

## Real-Time Requirements

| Task            | Target Rate  | Max Latency | Criticality |
| --------------- | ------------ | ----------- | ----------- |
| IMU Sampling    | 1000 Hz      | 1 ms        | Critical    |
| Main Loop       | 400 Hz       | 2.5 ms      | Critical    |
| Fast Loop       | 400 Hz       | 2.5 ms      | Critical    |
| EKF Update      | 50-400 Hz    | Variable    | High        |
| RC Input        | 50 Hz        | 20 ms       | High        |
| GPS Update      | 5-10 Hz      | 100-200 ms  | Medium      |
| Logging         | Variable     | 100 ms      | Low         |
| Telemetry       | 4-50 Hz      | 250 ms      | Low         |

---

## Performance Monitoring

### Monitor CPU Load

```bash
# In MAVProxy
status

param show SCHED_*
param set SCHED_DEBUG 1
param set LOG_BITMASK 1048575
```

```bash
mavlogdump.py --types SCHED logfile.BIN
# SCHED.Load - CPU load (target < 80%)
# SCHED.IntCount - Interrupt count
# SCHED.LoopTime - Loop execution time (µs)
```

### Monitor Memory Usage

```bash
status
# Shows: Mem: 123456/262144 bytes

param set LOG_BITMASK 1048575
mavlogdump.py --types MEMINFO logfile.BIN
# MEMINFO.freemem - Free memory (bytes)
# MEMINFO.brkval - Heap usage
```

### Analyze Loop Timing

```bash
mavlogdump.py --types PM logfile.BIN
# PM.MaxT - Maximum loop time (µs)
# PM.NLon - Number of long loops (> 5% over budget)
# PM.NLoop - Total loops executed
```

**Expected values:** Main loop ~2500 µs, MaxT < 3000 µs, NLon < 1% of NLoop.

**Critical:** MaxT > 4000 µs = problem; MaxT > 5000 µs = stability risk; NLon > 5% = investigate.

---

## Profiling Tools

### Built-in Profiling

```bash
param set SCHED_DEBUG 4
param set LOG_BITMASK 1048575
param set LOG_DISARMED 1

mavlogdump.py --types SCHED logfile.BIN > sched_analysis.txt
# Look for: SCHED: Task=EKF_Update Time=450us MaxTime=800us
```

### SITL Profiling with Valgrind

```bash
cd ~/ardupilot/ArduPlane
./waf configure --board=sitl --debug
./waf plane

valgrind --tool=massif \
         --massif-out-file=massif.out \
         build/sitl/bin/arduplane \
         --model quadplane --console

ms_print massif.out > massif_analysis.txt
```

```bash
valgrind --tool=callgrind \
         --callgrind-out-file=callgrind.out \
         build/sitl/bin/arduplane \
         --model quadplane --console

kcachegrind callgrind.out
```

### GDB Profiling

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py --gdb

(gdb) break AP_AHRS::update
(gdb) continue
(gdb) backtrace
(gdb) info locals
(gdb) call AP::scheduler().print_task_info()
```

### Perf (Linux Performance Analyzer)

```bash
./waf configure --board=sitl --debug
./waf plane

./build/sitl/bin/arduplane --model quadplane &
SITL_PID=$!

sudo perf record -F 99 -p $SITL_PID -g -- sleep 30
sudo perf report

sudo perf script | ~/FlameGraph/stackcollapse-perf.pl | ~/FlameGraph/flamegraph.pl > flame.svg
```

---

## Common Performance Issues

### High CPU Load

**Symptoms:** SCHED.Load > 80%, PM.MaxT > 4000 µs, PM.NLon increasing.

```bash
param set SCR_ENABLE 0
param set LOG_BITMASK 176126
param set RNGFND1_TYPE 0
param set FLOW_TYPE 0
```

```lua
-- BAD: String operations in fast loop at 50Hz
-- GOOD: Pre-compute, run slowly
local MSG_PREFIX = "Altitude: "
function update()
    local alt = ahrs:get_position():alt() * 0.01
    if alt then
        gcs:send_text(6, string.format("%s%.1f", MSG_PREFIX, alt))
    end
    return update, 1000  -- 1 Hz
end
```

```bash
# Disable unused modes in hwdef.dat
define MODE_QSTABILIZE_ENABLED 0
define MODE_QHOVER_ENABLED 0
```

### Memory Exhaustion

**Symptoms:** MEMINFO.freemem < 10%, random crashes, "Out of memory" errors.

```bash
# Reduce terrain buffer
param set TERRAIN_SPACING 100

# Reduce Lua heap
param set SCR_HEAP_SIZE 32768
```

```bash
# Disable large features in hwdef.dat
define AP_TERRAIN_AVAILABLE 0
define ADVANCED_FAILSAFE DISABLED
define HAL_ADSB_ENABLED 0
```

```bash
valgrind --leak-check=full \
         --show-leak-kinds=all \
         --track-origins=yes \
         --log-file=valgrind.log \
         build/sitl/bin/arduplane --model quadplane

grep "definitely lost" valgrind.log
```

### Loop Time Overruns

**Symptoms:** PM.MaxT > 3000 µs regularly, PM.NLon > 5%, control instability.

```bash
param set EK3_IMU_MASK 1
param set BARO_EXT_BUS -1
```

```cpp
// BAD: Heavy calculation in fast loop (400 Hz)
// GOOD: Move to slow loop (10 Hz)
void Plane::update_slow_loop() {
    if (should_log_distance()) {
        float distance = calculate_distance_to_home();
        log_distance(distance);
    }
}
```

```cpp
// Cache expensive calculations
class GPSCache {
    float cached_ground_speed;
    uint32_t last_update_ms;

    float get_ground_speed() {
        uint32_t now = AP_HAL::millis();
        if (now - last_update_ms > 100) {
            cached_ground_speed = sqrt(gps.velocity_north * gps.velocity_north +
                                      gps.velocity_east * gps.velocity_east);
            last_update_ms = now;
        }
        return cached_ground_speed;
    }
};
```

### I2C/SPI Bus Contention

**Symptoms:** Occasional sensor read failures, "I2C timeout" errors, inconsistent sensor data.

```text
# In hwdef.dat — distribute across buses
BARO MS56XX I2C:0:0x76
COMPASS AK8963 SPI:mpu9250
RANGEFINDER LIDAR I2C:1:0x62
```

```cpp
// In hwdef.dat
define HAL_I2C_INTERNAL_CLOCK 400000  // 400 kHz (default 100 kHz)
```

---

## Optimization Techniques

### Code Optimization

```cpp
// Multiply instead of divide
const float INV_1000 = 0.001f;
float result = value * INV_1000;

// Integer percentages
uint8_t percent = (value * 100) / max;

// Cache loop bounds
int size = get_array_size();
for (int i = 0; i < size; i++) { process(array[i]); }

// Fast trig approximations
float x = cosf_approx(angle_rad);
float y = sinf_approx(angle_rad);
```

### Parameter Tuning for Performance

```bash
param set EK3_IMU_MASK 1
param set EK3_SRC_OPTIONS 0
param set LOG_BITMASK 131071
param set LOG_FILE_RATEMAX 50
param set RC_SPEED 50
```

### Build-Time Optimization

```python
# hwdef.dat — disable unused features
define HAL_PARACHUTE_ENABLED 0
define HAL_SPRAYER_ENABLED 0
define HAL_GRIPPER_ENABLED 0
define HAL_MOUNT_ENABLED 0
define HAL_ADSB_ENABLED 0
define AP_SCRIPTING_ENABLED 0
define AP_TERRAIN_AVAILABLE 0
```

```bash
./waf configure --board=MatekH743 --optimize=O3
./waf plane
```

---

## Performance Testing Workflow

### Baseline Measurement

```bash
param set LOG_BACKEND_TYPE 1
param set LOG_BITMASK 1048575
param set SCHED_DEBUG 4
param set LOG_DISARMED 1

wp load baseline_mission.waypoints
mode AUTO
arm throttle
disarm

log download latest

mavlogdump.py --types PM,SCHED,MEMINFO baseline.BIN > baseline_perf.txt
grep "PM.MaxT" baseline_perf.txt | awk '{sum+=$NF; count++} END {print "Avg MaxT:", sum/count}'
grep "SCHED.Load" baseline_perf.txt | awk '{sum+=$NF; count++} END {print "Avg Load:", sum/count}'
```

### Apply and Compare

```bash
param set SCR_ENABLE 0
param save
reboot

# Re-run same mission, then compare:
mavlogdump.py --types PM,SCHED optimized.BIN > optimized_perf.txt
grep "PM.MaxT" optimized_perf.txt | awk '{sum+=$NF; count++} END {print "Avg MaxT:", sum/count, "us"}'
grep "SCHED.Load" optimized_perf.txt | awk '{sum+=$NF; count++} END {print "Avg Load:", sum/count, "%"}'
```

---

## Example: Finding CPU Bottleneck

```bash
param set SCHED_DEBUG 4
param set LOG_BITMASK 1048575

mavlogdump.py --types SCHED logfile.BIN | grep "Task=" > tasks.txt
sort -t= -k3 -n tasks.txt | tail -20
```

**Example output:**

```text
SCHED: Task=EKF_Update Time=780us
SCHED: Task=AP_Scripting Time=1200us
SCHED: Task=Logger Time=450us
SCHED: Task=AHRS_Update Time=320us
```

```lua
-- Reduce Lua script update rate
function update()
    -- ... script logic ...
    return update, 100  -- 100ms instead of 20ms
end
```

---

## Performance Optimization Checklist

### Before Flight

- [ ] CPU load target < 80%
- [ ] Memory usage > 20% free
- [ ] PM.MaxT in recent logs < 3000 µs
- [ ] Unused features disabled
- [ ] Lua scripts optimized
- [ ] Logging set to production level (not comprehensive)

### During Development

- [ ] Profile with Valgrind/perf in SITL
- [ ] Measure CPU impact of new features
- [ ] Test with comprehensive logging (worst case)
- [ ] Verify real-time performance on target hardware

### Post-Flight Analysis

- [ ] Check PM.NLon (loop overruns)
- [ ] Verify CPU load stayed within budget
- [ ] Correlate performance spikes with flight events

---

## Build Performance Comparison Script

```bash
#!/bin/bash
# compare_performance.sh

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <baseline.BIN> <optimized.BIN>"
    exit 1
fi

BASELINE=$1
OPTIMIZED=$2

echo "Performance Comparison Report"
echo "=============================="

mavlogdump.py --types PM "$BASELINE" > /tmp/baseline_pm.txt
mavlogdump.py --types PM "$OPTIMIZED" > /tmp/optimized_pm.txt

baseline_maxt=$(grep "PM.MaxT" /tmp/baseline_pm.txt | awk '{sum+=$NF; count++} END {print sum/count}')
optimized_maxt=$(grep "PM.MaxT" /tmp/optimized_pm.txt | awk '{sum+=$NF; count++} END {print sum/count}')

echo "Average MaxT (Loop Time):"
echo "  Baseline:  ${baseline_maxt} µs"
echo "  Optimized: ${optimized_maxt} µs"
echo "  Improvement: $(echo "$baseline_maxt - $optimized_maxt" | bc) µs"

mavlogdump.py --types SCHED "$BASELINE" > /tmp/baseline_sched.txt
mavlogdump.py --types SCHED "$OPTIMIZED" > /tmp/optimized_sched.txt

baseline_load=$(grep "SCHED.Load" /tmp/baseline_sched.txt | awk '{sum+=$NF; count++} END {print sum/count}')
optimized_load=$(grep "SCHED.Load" /tmp/optimized_sched.txt | awk '{sum+=$NF; count++} END {print sum/count}')

echo "Average CPU Load:"
echo "  Baseline:  ${baseline_load}%"
echo "  Optimized: ${optimized_load}%"
echo "  Improvement: $(echo "$baseline_load - $optimized_load" | bc)%"

rm /tmp/baseline_*.txt /tmp/optimized_*.txt 2>/dev/null
echo ""
echo "Analysis complete."
```

```bash
chmod +x compare_performance.sh
./compare_performance.sh baseline_flight.BIN optimized_flight.BIN
```

---

- [ArduPilot Performance](https://ardupilot.org/dev/docs/performance.html)
- [Scheduler Documentation](https://ardupilot.org/dev/docs/apmcopter-programming-scheduler.html)
- [Valgrind](https://valgrind.org/)
- [FlameGraph](https://github.com/brendangregg/FlameGraph)

**Author:** Patrick Kelly (@Kuscko)
