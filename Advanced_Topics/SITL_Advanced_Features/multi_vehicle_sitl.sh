#!/bin/bash
# Multi-Vehicle SITL Launch Script
# Launch multiple ArduPlane instances for swarm/formation testing
# Author: Patrick Kelly (@Kuscko)
# Version: 1.0
# Last Updated: 2026-02-03

set -e  # Exit on error

# ============================================
# CONFIGURATION
# ============================================

# Number of vehicles to launch
NUM_VEHICLES=3

# ArduPilot directory
ARDUPILOT_DIR="$HOME/ardupilot"

# Starting location (CMAC field)
START_LAT=-35.363261
START_LON=149.165230
START_ALT=584

# Vehicle separation (meters)
SEPARATION=10

# Base instance number
BASE_INSTANCE=0

# MAVLink base ports
BASE_MAVLINK_PORT=14550
BASE_SITL_PORT=5760

# ============================================
# FUNCTIONS
# ============================================

launch_vehicle() {
    local vehicle_num=$1
    local instance=$((BASE_INSTANCE + vehicle_num))

    # Calculate position offset (spread vehicles in a line)
    local lat_offset=$(echo "$vehicle_num * 0.00009" | bc -l)  # ~10m per vehicle
    local lat=$(echo "$START_LAT + $lat_offset" | bc -l)

    # Calculate ports
    local mavlink_port=$((BASE_MAVLINK_PORT + vehicle_num * 10))
    local sitl_port=$((BASE_SITL_PORT + vehicle_num))

    echo ""
    echo "=================================================="
    echo "Launching Vehicle #$vehicle_num"
    echo "  Instance: $instance"
    echo "  Position: $lat, $START_LON, ${START_ALT}m"
    echo "  MAVLink port: $mavlink_port"
    echo "  SITL port: $sitl_port"
    echo "=================================================="

    # Create vehicle directory
    local vehicle_dir="$HOME/sitl_vehicle_${vehicle_num}"
    mkdir -p "$vehicle_dir"

    cd "$ARDUPILOT_DIR/ArduPlane"

    # Launch SITL instance
    Tools/autotest/sim_vehicle.py \
        --vehicle=ArduPlane \
        --instance=$instance \
        --custom-location="$lat,$START_LON,$START_ALT,0" \
        --out=127.0.0.1:$mavlink_port \
        --no-mavproxy \
        --model=plane \
        --speedup=1 \
        --sysid=$((instance + 1)) \
        > "$vehicle_dir/sitl_output.log" 2>&1 &

    local pid=$!

    echo "  SITL PID: $pid"
    echo "  Logs: $vehicle_dir/sitl_output.log"

    # Save PID to file
    echo $pid > "$vehicle_dir/sitl.pid"

    # Wait a bit before launching next vehicle
    sleep 5
}

stop_all_vehicles() {
    echo ""
    echo "Stopping all vehicles..."

    for ((i=0; i<NUM_VEHICLES; i++)); do
        local vehicle_dir="$HOME/sitl_vehicle_${i}"
        if [ -f "$vehicle_dir/sitl.pid" ]; then
            local pid=$(cat "$vehicle_dir/sitl.pid")
            echo "  Stopping vehicle #$i (PID: $pid)"
            kill $pid 2>/dev/null || true
            rm "$vehicle_dir/sitl.pid"
        fi
    done

    echo "All vehicles stopped"
}

print_connection_info() {
    echo ""
    echo "=================================================="
    echo "Vehicle Connection Information"
    echo "=================================================="

    for ((i=0; i<NUM_VEHICLES; i++)); do
        local mavlink_port=$((BASE_MAVLINK_PORT + i * 10))
        local sysid=$((BASE_INSTANCE + i + 1))

        echo ""
        echo "Vehicle #$i (System ID: $sysid)"
        echo "  MAVProxy:         mavproxy.py --master=udp:127.0.0.1:$mavlink_port"
        echo "  Mission Planner:  UDP port $mavlink_port"
        echo "  MAVSDK:           udp://:$mavlink_port"
        echo "  DroneKit:         udp:127.0.0.1:$mavlink_port"
    done

    echo ""
}

# ============================================
# SIGNAL HANDLERS
# ============================================

# Trap Ctrl+C and cleanup
trap 'echo ""; echo "Caught interrupt signal"; stop_all_vehicles; exit 0' INT TERM

# ============================================
# MAIN EXECUTION
# ============================================

main() {
    echo "=================================================="
    echo "Multi-Vehicle SITL Launcher"
    echo "=================================================="
    echo ""
    echo "Configuration:"
    echo "  Number of vehicles: $NUM_VEHICLES"
    echo "  Starting location: $START_LAT, $START_LON"
    echo "  Vehicle separation: ${SEPARATION}m"
    echo "  Base MAVLink port: $BASE_MAVLINK_PORT"
    echo ""
    echo "Press Ctrl+C to stop all vehicles"
    echo ""

    sleep 3

    # Launch all vehicles
    for ((i=0; i<NUM_VEHICLES; i++)); do
        launch_vehicle $i
    done

    echo ""
    echo "=================================================="
    echo "All vehicles launched!"
    echo "=================================================="

    # Print connection information
    print_connection_info

    echo "=================================================="
    echo "Example MAVProxy connections:"
    echo "=================================================="
    echo ""
    echo "Connect to vehicle 0:"
    echo "  mavproxy.py --master=udp:127.0.0.1:14550"
    echo ""
    echo "Connect to all vehicles:"
    for ((i=0; i<NUM_VEHICLES; i++)); do
        local port=$((BASE_MAVLINK_PORT + i * 10))
        echo "  # Terminal $((i+1))"
        echo "  mavproxy.py --master=udp:127.0.0.1:$port"
    done
    echo ""

    # Wait for user to stop
    echo "Press Ctrl+C to stop all vehicles"
    echo ""

    # Wait indefinitely
    while true; do
        sleep 1
    done
}

# ============================================
# CHECK PREREQUISITES
# ============================================

if [ ! -d "$ARDUPILOT_DIR" ]; then
    echo "ERROR: ArduPilot directory not found: $ARDUPILOT_DIR"
    echo "Please set ARDUPILOT_DIR correctly"
    exit 1
fi

if ! command -v bc &> /dev/null; then
    echo "ERROR: 'bc' calculator not found"
    echo "Install with: sudo apt-get install bc"
    exit 1
fi

# ============================================
# RUN
# ============================================

main

# ============================================
# NOTES
# ============================================

# Multi-vehicle SITL allows testing:
# - Formation flying
# - Swarm coordination
# - Multi-vehicle missions
# - Collision avoidance
# - Communication between vehicles
#
# Each vehicle has:
# - Unique System ID (SYSID)
# - Unique MAVLink port
# - Separate parameters and logs
# - Independent position and state
#
# To connect to individual vehicles:
#   Vehicle 0: udp:127.0.0.1:14550
#   Vehicle 1: udp:127.0.0.1:14560
#   Vehicle 2: udp:127.0.0.1:14570
#
# To control vehicles programmatically:
#   Use MAVSDK, DroneKit, or pymavlink with specific ports
#
# Example MAVSDK Python:
#   from mavsdk import System
#   drone0 = System()
#   await drone0.connect(system_address="udp://:14550")
#   drone1 = System()
#   await drone1.connect(system_address="udp://:14560")
#
# To run this script:
#   chmod +x multi_vehicle_sitl.sh
#   ./multi_vehicle_sitl.sh
#
# To stop:
#   Press Ctrl+C
