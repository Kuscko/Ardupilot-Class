#!/bin/bash
# Wind Scenario Testing Script
# Automated testing of ArduPlane in various wind conditions using SITL
# Author: Patrick Kelly (@Kuscko)
# Version: 1.0
# Last Updated: 2026-02-03

set -e  # Exit on error

# ============================================
# CONFIGURATION
# ============================================

# ArduPilot directory
ARDUPILOT_DIR="$HOME/ardupilot"

# Test mission file
MISSION_FILE="$HOME/ardupilot/Tools/autotest/Generic_Missions/CMAC-circuit.txt"

# Log output directory
LOG_DIR="$HOME/sitl_wind_tests"
mkdir -p "$LOG_DIR"

# Test duration (seconds)
TEST_DURATION=300

# ============================================
# WIND SCENARIOS
# ============================================

# Array of wind test scenarios
# Format: "speed,direction,turbulence,description"
declare -a WIND_SCENARIOS=(
    "0,0,0,Calm - No Wind"
    "5,0,0,Light Breeze - 5 m/s from North"
    "10,45,0,Moderate Wind - 10 m/s from NE"
    "15,90,2,Strong Wind - 15 m/s from East with light turbulence"
    "20,180,5,Very Strong Wind - 20 m/s from South with moderate turbulence"
    "10,270,10,Crosswind - 10 m/s from West with heavy turbulence"
    "5,0,20,Severe Turbulence - 5 m/s with extreme gusts"
)

# ============================================
# FUNCTIONS
# ============================================

run_wind_test() {
    local wind_speed=$1
    local wind_direction=$2
    local wind_turbulence=$3
    local description=$4

    echo ""
    echo "=================================================="
    echo "TEST: $description"
    echo "  Speed: ${wind_speed} m/s"
    echo "  Direction: ${wind_direction}°"
    echo "  Turbulence: ${wind_turbulence}"
    echo "=================================================="

    # Create log directory for this test
    local test_name="${wind_speed}ms_${wind_direction}deg_turb${wind_turbulence}"
    local test_dir="$LOG_DIR/$test_name"
    mkdir -p "$test_dir"

    # Start SITL with wind parameters
    cd "$ARDUPILOT_DIR/ArduPlane"

    echo "Starting SITL with wind conditions..."

    # Run SITL in background
    Tools/autotest/sim_vehicle.py \
        --vehicle=ArduPlane \
        --console \
        --map \
        --wind="${wind_speed},${wind_direction},${wind_turbulence}" \
        --out=127.0.0.1:14550 \
        > "$test_dir/sitl_output.log" 2>&1 &

    SITL_PID=$!

    # Wait for SITL to start
    echo "Waiting for SITL to initialize..."
    sleep 30

    # Check if SITL is running
    if ! kill -0 $SITL_PID 2>/dev/null; then
        echo "ERROR: SITL failed to start"
        cat "$test_dir/sitl_output.log"
        return 1
    fi

    # Connect with MAVProxy and run test
    echo "Running automated test..."

    # Create MAVProxy command file
    cat > "$test_dir/mavproxy_commands.txt" <<EOF
# Load mission
wp load $MISSION_FILE
wp list

# Arm and takeoff
mode FBWA
arm throttle
rc 3 1700

# Wait for altitude
sleep 10

# Start mission
mode AUTO

# Wait for test duration
sleep $TEST_DURATION

# Return to launch
mode RTL

# Wait for landing
sleep 60

# Disarm
disarm

# Exit
exit
EOF

    # Run MAVProxy with command file
    timeout $((TEST_DURATION + 120)) mavproxy.py \
        --master=udp:127.0.0.1:14550 \
        --cmd="script $test_dir/mavproxy_commands.txt" \
        > "$test_dir/mavproxy_output.log" 2>&1 || true

    # Stop SITL
    echo "Stopping SITL..."
    kill $SITL_PID 2>/dev/null || true
    sleep 5

    # Copy log files
    echo "Copying log files..."
    cp "$ARDUPILOT_DIR/ArduPlane/logs/"*.BIN "$test_dir/" 2>/dev/null || echo "No logs found"

    # Generate quick analysis
    echo "Generating analysis..."
    if [ -f "$test_dir/"*.BIN ]; then
        local logfile=$(ls -t "$test_dir/"*.BIN | head -1)

        # Extract key metrics
        mavlogdump.py --types GPS,ATT,TECS "$logfile" > "$test_dir/analysis.txt" 2>/dev/null || true

        echo "Log file: $logfile" > "$test_dir/summary.txt"
        echo "Test: $description" >> "$test_dir/summary.txt"
        echo "Wind: ${wind_speed} m/s @ ${wind_direction}° (turbulence: ${wind_turbulence})" >> "$test_dir/summary.txt"
    fi

    echo "Test complete: $description"
    echo "Results saved to: $test_dir"
}

# ============================================
# MAIN EXECUTION
# ============================================

main() {
    echo "=================================================="
    echo "ArduPlane Wind Scenario Testing"
    echo "=================================================="
    echo ""
    echo "Test configuration:"
    echo "  ArduPilot directory: $ARDUPILOT_DIR"
    echo "  Mission file: $MISSION_FILE"
    echo "  Log directory: $LOG_DIR"
    echo "  Test duration: ${TEST_DURATION}s per scenario"
    echo "  Number of scenarios: ${#WIND_SCENARIOS[@]}"
    echo ""
    echo "Press Ctrl+C to abort"
    echo ""

    sleep 5

    # Run each wind scenario
    local test_num=1
    for scenario in "${WIND_SCENARIOS[@]}"; do
        echo ""
        echo "Running test $test_num of ${#WIND_SCENARIOS[@]}"

        # Parse scenario
        IFS=',' read -r speed direction turbulence description <<< "$scenario"

        # Run test
        run_wind_test "$speed" "$direction" "$turbulence" "$description"

        ((test_num++))

        # Pause between tests
        echo "Pausing 10s before next test..."
        sleep 10
    done

    # Generate summary report
    echo ""
    echo "=================================================="
    echo "All tests complete!"
    echo "=================================================="
    echo ""
    echo "Results saved to: $LOG_DIR"
    echo ""
    echo "Summary of tests:"
    for scenario in "${WIND_SCENARIOS[@]}"; do
        IFS=',' read -r speed direction turbulence description <<< "$scenario"
        local test_name="${speed}ms_${direction}deg_turb${turbulence}"
        echo "  $description -> $LOG_DIR/$test_name"
    done
    echo ""
    echo "To analyze results:"
    echo "  cd $LOG_DIR"
    echo "  ls -la */summary.txt"
    echo "  mavexplorer.py [test_dir]/*.BIN"
}

# ============================================
# RUN
# ============================================

# Check if running in ArduPilot directory
if [ ! -d "$ARDUPILOT_DIR" ]; then
    echo "ERROR: ArduPilot directory not found: $ARDUPILOT_DIR"
    echo "Please set ARDUPILOT_DIR variable correctly"
    exit 1
fi

# Check if mission file exists
if [ ! -f "$MISSION_FILE" ]; then
    echo "WARNING: Mission file not found: $MISSION_FILE"
    echo "Will attempt to continue anyway"
fi

# Run main function
main

echo ""
echo "Testing complete!"

# ============================================
# NOTES
# ============================================

# Wind parameter format: speed,direction,turbulence
#   speed:       Wind speed in m/s
#   direction:   Wind direction in degrees (0=North, 90=East, 180=South, 270=West)
#   turbulence:  Turbulence level 0-20 (0=none, 20=extreme)
#
# To run this script:
#   chmod +x test_wind_scenarios.sh
#   ./test_wind_scenarios.sh
#
# To analyze results:
#   cd ~/sitl_wind_tests/[test_name]
#   mavexplorer.py *.BIN
#
# To compare tests:
#   mavlogdump.py --types=TECS test1/*.BIN > test1_tecs.txt
#   mavlogdump.py --types=TECS test2/*.BIN > test2_tecs.txt
#   diff test1_tecs.txt test2_tecs.txt
