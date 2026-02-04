#!/bin/bash
# Performance Comparison Script
# Compare performance metrics between two ArduPilot log files
# Author: Patrick Kelly (@Kuscko)
# Version: 1.0
# Last Updated: 2026-02-03

# Usage: ./compare_performance.sh <baseline.BIN> <optimized.BIN>

set -e  # Exit on error

# Check arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <baseline.BIN> <optimized.BIN>"
    echo ""
    echo "Example:"
    echo "  $0 flight_before_optimization.BIN flight_after_optimization.BIN"
    exit 1
fi

BASELINE=$1
OPTIMIZED=$2

# Check if files exist
if [ ! -f "$BASELINE" ]; then
    echo "Error: Baseline file not found: $BASELINE"
    exit 1
fi

if [ ! -f "$OPTIMIZED" ]; then
    echo "Error: Optimized file not found: $OPTIMIZED"
    exit 1
fi

# Check for mavlogdump.py
if ! command -v mavlogdump.py &> /dev/null; then
    echo "Error: mavlogdump.py not found. Install MAVProxy:"
    echo "  pip install --user MAVProxy"
    exit 1
fi

# Create temporary directory
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

echo "========================================"
echo "  ArduPilot Performance Comparison"
echo "========================================"
echo ""
echo "Baseline:  $BASELINE"
echo "Optimized: $OPTIMIZED"
echo ""
echo "Extracting data..."

# Extract performance messages
mavlogdump.py --types PM "$BASELINE" > "$TMPDIR/baseline_pm.txt" 2>/dev/null
mavlogdump.py --types PM "$OPTIMIZED" > "$TMPDIR/optimized_pm.txt" 2>/dev/null

mavlogdump.py --types SCHED "$BASELINE" > "$TMPDIR/baseline_sched.txt" 2>/dev/null
mavlogdump.py --types SCHED "$OPTIMIZED" > "$TMPDIR/optimized_sched.txt" 2>/dev/null

mavlogdump.py --types MEMINFO "$BASELINE" > "$TMPDIR/baseline_mem.txt" 2>/dev/null
mavlogdump.py --types MEMINFO "$OPTIMIZED" > "$TMPDIR/optimized_mem.txt" 2>/dev/null

echo "Analyzing..."
echo ""

# ============================================
# LOOP TIME ANALYSIS (PM.MaxT)
# ============================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Loop Time Analysis"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -s "$TMPDIR/baseline_pm.txt" ]; then
    # Extract MaxT values
    baseline_maxt_avg=$(grep "MaxT" "$TMPDIR/baseline_pm.txt" | \
        awk -F'[: ,]+' '{for(i=1;i<=NF;i++) if($i=="MaxT") print $(i+1)}' | \
        awk '{sum+=$1; count++} END {if(count>0) print sum/count; else print "N/A"}')

    optimized_maxt_avg=$(grep "MaxT" "$TMPDIR/optimized_pm.txt" | \
        awk -F'[: ,]+' '{for(i=1;i<=NF;i++) if($i=="MaxT") print $(i+1)}' | \
        awk '{sum+=$1; count++} END {if(count>0) print sum/count; else print "N/A"}')

    baseline_maxt_max=$(grep "MaxT" "$TMPDIR/baseline_pm.txt" | \
        awk -F'[: ,]+' '{for(i=1;i<=NF;i++) if($i=="MaxT") print $(i+1)}' | \
        awk 'BEGIN{max=0} {if($1>max) max=$1} END {print max}')

    optimized_maxt_max=$(grep "MaxT" "$TMPDIR/optimized_pm.txt" | \
        awk -F'[: ,]+' '{for(i=1;i<=NF;i++) if($i=="MaxT") print $(i+1)}' | \
        awk 'BEGIN{max=0} {if($1>max) max=$1} END {print max}')

    echo "Average Loop Time (MaxT):"
    echo "  Baseline:  ${baseline_maxt_avg} µs"
    echo "  Optimized: ${optimized_maxt_avg} µs"

    if [ "$baseline_maxt_avg" != "N/A" ] && [ "$optimized_maxt_avg" != "N/A" ]; then
        improvement=$(echo "$baseline_maxt_avg - $optimized_maxt_avg" | bc -l)
        percent=$(echo "scale=2; ($improvement / $baseline_maxt_avg) * 100" | bc -l)
        echo "  Improvement: ${improvement} µs (${percent}%)"
    fi

    echo ""
    echo "Maximum Loop Time (MaxT):"
    echo "  Baseline:  ${baseline_maxt_max} µs"
    echo "  Optimized: ${optimized_maxt_max} µs"

    if [ "$baseline_maxt_max" != "N/A" ] && [ "$optimized_maxt_max" != "N/A" ]; then
        max_improvement=$(echo "$baseline_maxt_max - $optimized_maxt_max" | bc -l)
        echo "  Improvement: ${max_improvement} µs"
    fi

    echo ""

    # Analysis
    if (( $(echo "$optimized_maxt_avg > 3000" | bc -l) )); then
        echo "  ⚠ WARNING: Average loop time still > 3000 µs"
        echo "           Further optimization may be needed"
    elif (( $(echo "$optimized_maxt_avg < 2500" | bc -l) )); then
        echo "  ✓ GOOD: Loop time well within budget"
    fi
else
    echo "  No PM.MaxT data found in logs"
fi

# ============================================
# LONG LOOPS ANALYSIS (PM.NLon)
# ============================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Long Loops Analysis"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -s "$TMPDIR/baseline_pm.txt" ]; then
    baseline_nlon=$(grep "NLon" "$TMPDIR/baseline_pm.txt" | tail -1 | \
        awk -F'[: ,]+' '{for(i=1;i<=NF;i++) if($i=="NLon") print $(i+1)}')
    baseline_nloop=$(grep "NLoop" "$TMPDIR/baseline_pm.txt" | tail -1 | \
        awk -F'[: ,]+' '{for(i=1;i<=NF;i++) if($i=="NLoop") print $(i+1)}')

    optimized_nlon=$(grep "NLon" "$TMPDIR/optimized_pm.txt" | tail -1 | \
        awk -F'[: ,]+' '{for(i=1;i<=NF;i++) if($i=="NLon") print $(i+1)}')
    optimized_nloop=$(grep "NLoop" "$TMPDIR/optimized_pm.txt" | tail -1 | \
        awk -F'[: ,]+' '{for(i=1;i<=NF;i++) if($i=="NLoop") print $(i+1)}')

    echo "Long Loops (loops exceeding time budget):"
    echo "  Baseline:  ${baseline_nlon} / ${baseline_nloop} loops"

    if [ -n "$baseline_nlon" ] && [ -n "$baseline_nloop" ] && [ "$baseline_nloop" -gt 0 ]; then
        baseline_percent=$(echo "scale=2; ($baseline_nlon / $baseline_nloop) * 100" | bc -l)
        echo "             (${baseline_percent}%)"
    fi

    echo "  Optimized: ${optimized_nlon} / ${optimized_nloop} loops"

    if [ -n "$optimized_nlon" ] && [ -n "$optimized_nloop" ] && [ "$optimized_nloop" -gt 0 ]; then
        optimized_percent=$(echo "scale=2; ($optimized_nlon / $optimized_nloop) * 100" | bc -l)
        echo "             (${optimized_percent}%)"
    fi

    echo ""

    # Analysis
    if [ -n "$optimized_percent" ]; then
        if (( $(echo "$optimized_percent > 5" | bc -l) )); then
            echo "  ⚠ WARNING: >5% long loops detected"
            echo "           Performance issues likely"
        elif (( $(echo "$optimized_percent < 1" | bc -l) )); then
            echo "  ✓ EXCELLENT: <1% long loops"
        else
            echo "  ✓ GOOD: Long loops within acceptable range"
        fi
    fi
else
    echo "  No PM.NLon data found in logs"
fi

# ============================================
# CPU LOAD ANALYSIS (SCHED.Load)
# ============================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  CPU Load Analysis"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -s "$TMPDIR/baseline_sched.txt" ]; then
    baseline_load_avg=$(grep "Load" "$TMPDIR/baseline_sched.txt" | \
        awk -F'[: ,]+' '{for(i=1;i<=NF;i++) if($i=="Load") print $(i+1)}' | \
        awk '{sum+=$1; count++} END {if(count>0) print sum/count; else print "N/A"}')

    optimized_load_avg=$(grep "Load" "$TMPDIR/optimized_sched.txt" | \
        awk -F'[: ,]+' '{for(i=1;i<=NF;i++) if($i=="Load") print $(i+1)}' | \
        awk '{sum+=$1; count++} END {if(count>0) print sum/count; else print "N/A"}')

    baseline_load_max=$(grep "Load" "$TMPDIR/baseline_sched.txt" | \
        awk -F'[: ,]+' '{for(i=1;i<=NF;i++) if($i=="Load") print $(i+1)}' | \
        awk 'BEGIN{max=0} {if($1>max) max=$1} END {print max}')

    optimized_load_max=$(grep "Load" "$TMPDIR/optimized_sched.txt" | \
        awk -F'[: ,]+' '{for(i=1;i<=NF;i++) if($i=="Load") print $(i+1)}' | \
        awk 'BEGIN{max=0} {if($1>max) max=$1} END {print max}')

    echo "Average CPU Load:"
    echo "  Baseline:  ${baseline_load_avg}%"
    echo "  Optimized: ${optimized_load_avg}%"

    if [ "$baseline_load_avg" != "N/A" ] && [ "$optimized_load_avg" != "N/A" ]; then
        load_improvement=$(echo "$baseline_load_avg - $optimized_load_avg" | bc -l)
        echo "  Improvement: ${load_improvement} percentage points"
    fi

    echo ""
    echo "Peak CPU Load:"
    echo "  Baseline:  ${baseline_load_max}%"
    echo "  Optimized: ${optimized_load_max}%"

    echo ""

    # Analysis
    if [ "$optimized_load_avg" != "N/A" ]; then
        if (( $(echo "$optimized_load_avg > 80" | bc -l) )); then
            echo "  ⚠ WARNING: CPU load >80%"
            echo "           Risk of performance issues"
        elif (( $(echo "$optimized_load_avg < 50" | bc -l) )); then
            echo "  ✓ EXCELLENT: CPU load <50%"
        else
            echo "  ✓ GOOD: CPU load within acceptable range"
        fi
    fi
else
    echo "  No SCHED.Load data found in logs"
fi

# ============================================
# MEMORY USAGE ANALYSIS
# ============================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Memory Usage Analysis"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -s "$TMPDIR/baseline_mem.txt" ]; then
    baseline_mem=$(grep "freemem" "$TMPDIR/baseline_mem.txt" | \
        awk -F'[: ,]+' '{for(i=1;i<=NF;i++) if($i=="freemem") print $(i+1)}' | \
        awk '{sum+=$1; count++} END {if(count>0) print sum/count; else print "N/A"}')

    optimized_mem=$(grep "freemem" "$TMPDIR/optimized_mem.txt" | \
        awk -F'[: ,]+' '{for(i=1;i<=NF;i++) if($i=="freemem") print $(i+1)}' | \
        awk '{sum+=$1; count++} END {if(count>0) print sum/count; else print "N/A"}')

    echo "Average Free Memory:"
    echo "  Baseline:  ${baseline_mem} bytes"
    echo "  Optimized: ${optimized_mem} bytes"

    if [ "$baseline_mem" != "N/A" ] && [ "$optimized_mem" != "N/A" ]; then
        mem_improvement=$(echo "$optimized_mem - $baseline_mem" | bc -l)
        echo "  Improvement: ${mem_improvement} bytes"
    fi
else
    echo "  No MEMINFO data found in logs"
    echo "  (Enable with: param set LOG_BITMASK 1048575)"
fi

# ============================================
# SUMMARY
# ============================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Overall assessment
ISSUES=0

if [ "$optimized_maxt_avg" != "N/A" ]; then
    if (( $(echo "$optimized_maxt_avg > 3000" | bc -l) )); then
        ((ISSUES++))
    fi
fi

if [ "$optimized_percent" != "" ]; then
    if (( $(echo "$optimized_percent > 5" | bc -l) )); then
        ((ISSUES++))
    fi
fi

if [ "$optimized_load_avg" != "N/A" ]; then
    if (( $(echo "$optimized_load_avg > 80" | bc -l) )); then
        ((ISSUES++))
    fi
fi

if [ $ISSUES -eq 0 ]; then
    echo "  ✓ Performance looks good!"
    echo "  All metrics within acceptable ranges."
elif [ $ISSUES -eq 1 ]; then
    echo "  ⚠ Minor performance concerns"
    echo "  Review warnings above."
else
    echo "  ⚠ Performance issues detected"
    echo "  Further optimization recommended."
fi

echo ""
echo "Analysis complete."
echo ""

# Cleanup is handled by trap
