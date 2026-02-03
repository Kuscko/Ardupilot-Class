#!/usr/bin/env python3
"""
EKF Health Monitor
Monitors EKF status and displays variance levels in real-time

Usage:
    python3 ekf_test.py [connection_string]

Example:
    python3 ekf_test.py udp:127.0.0.1:14550

Author: Patrick Kelly (@Kuscko)
Version: 1.0
"""

import sys
import time
from pymavlink import mavutil


def monitor_ekf_status(master):
    """Monitor and display EKF status"""
    print("\nEKF Health Monitor")
    print("=" * 60)
    print("Monitoring EKF status... (Ctrl+C to exit)\n")

    last_print = 0

    try:
        while True:
            msg = master.recv_match(blocking=False)

            if msg is None:
                time.sleep(0.01)
                continue

            # EKF Status Report
            if msg.get_type() == 'EKF_STATUS_REPORT':
                current_time = time.time()

                # Print every 2 seconds
                if current_time - last_print > 2.0:
                    print(f"\n[{time.strftime('%H:%M:%S')}] EKF Status:")
                    print(f"  Flags: 0x{msg.flags:04x}")
                    print(f"  Velocity Variance: {msg.velocity_variance:.4f}")
                    print(f"  Position Variance (H): {msg.pos_horiz_variance:.4f}")
                    print(f"  Position Variance (V): {msg.pos_vert_variance:.4f}")
                    print(f"  Compass Variance: {msg.compass_variance:.4f}")
                    print(f"  Terrain Alt Variance: {msg.terrain_alt_variance:.4f}")

                    # Health assessment
                    print("\n  Health Assessment:")
                    if msg.velocity_variance < 0.25:
                        print("    [GOOD] Velocity variance within limits")
                    else:
                        print("    [WARN] Velocity variance HIGH!")

                    if msg.pos_horiz_variance < 0.25:
                        print("    [GOOD] Horizontal position variance OK")
                    else:
                        print("    [WARN] Horizontal position variance HIGH!")

                    if msg.pos_vert_variance < 0.25:
                        print("    [GOOD] Vertical position variance OK")
                    else:
                        print("    [WARN] Vertical position variance HIGH!")

                    print("-" * 60)
                    last_print = current_time

            # Vibration levels
            elif msg.get_type() == 'VIBRATION':
                # Only print if vibration is concerning
                if msg.vibration_x > 30 or msg.vibration_y > 30 or msg.vibration_z > 30:
                    print(f"\n[WARN] High Vibration: X={msg.vibration_x:.1f} "
                          f"Y={msg.vibration_y:.1f} Z={msg.vibration_z:.1f}")

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")


def main():
    # Connection string
    if len(sys.argv) > 1:
        connection_string = sys.argv[1]
    else:
        connection_string = 'udp:127.0.0.1:14550'

    print(f"Connecting to {connection_string}...")

    try:
        master = mavutil.mavlink_connection(connection_string)
        master.wait_heartbeat()

        print(f"Connected to system {master.target_system}")

        # Request EKF status at 2 Hz
        master.mav.command_long_send(
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
            0,
            230,  # EKF_STATUS_REPORT
            500000,  # Interval in microseconds (2 Hz)
            0, 0, 0, 0, 0
        )

        monitor_ekf_status(master)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
