#!/usr/bin/env python3
"""
Simple MAVLink Monitor
Displays real-time telemetry from autopilot

Usage:
    python3 mavlink_monitor.py [connection_string]

Example:
    python3 mavlink_monitor.py udp:127.0.0.1:14550
    python3 mavlink_monitor.py /dev/ttyUSB0:57600

Author: Patrick Kelly (@Kuscko)
FOR: AEVEX Onboarding
Version: 1.0
"""

import sys
import time
from pymavlink import mavutil


def monitor_mavlink(connection_string='udp:127.0.0.1:14550'):
    """Connect to autopilot and display telemetry"""

    print(f"Connecting to {connection_string}...")
    master = mavutil.mavlink_connection(connection_string)

    print("Waiting for heartbeat...")
    master.wait_heartbeat()
    print(f"Connected to system {master.target_system} component {master.target_component}")
    print(f"Autopilot type: {master.autopilot_type} Vehicle type: {master.vehicle_type}\n")

    print("=" * 80)
    print("Real-time Telemetry (Ctrl+C to exit)")
    print("=" * 80)

    last_hb = time.time()

    while True:
        try:
            # Get VFR_HUD for primary flight data
            msg = master.recv_match(type='VFR_HUD', blocking=False)
            if msg:
                print(f"\rAirspeed: {msg.airspeed:5.1f} m/s | "
                      f"Groundspeed: {msg.groundspeed:5.1f} m/s | "
                      f"Alt: {msg.alt:6.1f} m | "
                      f"Climb: {msg.climb:+5.1f} m/s | "
                      f"Heading: {msg.heading:3.0f}° | "
                      f"Throttle: {msg.throttle:3.0f}%  ", end='', flush=True)

            # Check for heartbeat (every 5 seconds)
            if time.time() - last_hb > 5:
                hb = master.recv_match(type='HEARTBEAT', blocking=False)
                if hb:
                    last_hb = time.time()

            time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
            break


def print_system_info(master):
    """Print detailed system information"""
    print("\n" + "=" * 80)
    print("System Information")
    print("=" * 80)

    # Request system status
    master.mav.request_data_stream_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL, 1, 1)

    # Get system status
    msg = master.recv_match(type='SYS_STATUS', blocking=True, timeout=5)
    if msg:
        print(f"Battery Voltage: {msg.voltage_battery / 1000:.2f} V")
        print(f"Battery Current: {msg.current_battery / 100:.2f} A")
        print(f"Battery Remaining: {msg.battery_remaining} %")
        print(f"CPU Load: {msg.load / 10:.1f} %")

    # Get GPS status
    msg = master.recv_match(type='GPS_RAW_INT', blocking=True, timeout=5)
    if msg:
        fix_type = ['No GPS', 'No Fix', '2D Fix', '3D Fix', 'DGPS', 'RTK Float', 'RTK Fixed'][msg.fix_type]
        print(f"GPS Fix: {fix_type}")
        print(f"Satellites: {msg.satellites_visible}")
        print(f"GPS Lat/Lon: {msg.lat/1e7:.6f}, {msg.lon/1e7:.6f}")
        print(f"GPS Alt: {msg.alt/1000:.1f} m")

    print("=" * 80 + "\n")


if __name__ == '__main__':
    connection_string = sys.argv[1] if len(sys.argv) > 1 else 'udp:127.0.0.1:14550'
    monitor_mavlink(connection_string)
