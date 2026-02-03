#!/usr/bin/env python3
"""
Arm/Disarm Example
Demonstrates arming and disarming the vehicle via MAVLink

WARNING: Use in SITL only for learning. Real aircraft require proper safety procedures.

Usage:
    python3 arm_disarm.py [connection_string]

Author: Patrick Kelly (@Kuscko)
Version: 1.0
"""

import sys
import time
from pymavlink import mavutil


def wait_for_command_ack(master, command_id, timeout=5):
    """Wait for command acknowledgement"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        msg = master.recv_match(type='COMMAND_ACK', blocking=True, timeout=1)
        if msg and msg.command == command_id:
            result_text = {
                mavutil.mavlink.MAV_RESULT_ACCEPTED: "ACCEPTED",
                mavutil.mavlink.MAV_RESULT_TEMPORARILY_REJECTED: "TEMPORARILY_REJECTED",
                mavutil.mavlink.MAV_RESULT_DENIED: "DENIED",
                mavutil.mavlink.MAV_RESULT_UNSUPPORTED: "UNSUPPORTED",
                mavutil.mavlink.MAV_RESULT_FAILED: "FAILED",
            }.get(msg.result, f"UNKNOWN({msg.result})")

            return msg.result, result_text
    return None, "TIMEOUT"


def arm_vehicle(master, force=False):
    """Arm the vehicle"""
    print("Attempting to arm vehicle...")

    # Send arm command
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        1,  # 1 = arm, 0 = disarm
        21196 if force else 0,  # Force arm (bypasses some pre-arm checks)
        0, 0, 0, 0, 0
    )

    # Wait for acknowledgement
    result, result_text = wait_for_command_ack(master, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM)

    if result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        print("✓ Vehicle ARMED")
        return True
    else:
        print(f"✗ Arm failed: {result_text}")
        print("  Check console for PreArm error messages")
        return False


def disarm_vehicle(master, force=False):
    """Disarm the vehicle"""
    print("Attempting to disarm vehicle...")

    # Send disarm command
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        0,  # 0 = disarm
        21196 if force else 0,  # Force disarm
        0, 0, 0, 0, 0
    )

    # Wait for acknowledgement
    result, result_text = wait_for_command_ack(master, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM)

    if result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        print("✓ Vehicle DISARMED")
        return True
    else:
        print(f"✗ Disarm failed: {result_text}")
        return False


def check_arm_status(master):
    """Check if vehicle is currently armed"""
    msg = master.recv_match(type='HEARTBEAT', blocking=True, timeout=5)
    if msg:
        armed = msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
        return bool(armed)
    return None


def main(connection_string='udp:127.0.0.1:14550'):
    """Main function"""
    print(f"Connecting to {connection_string}...")
    master = mavutil.mavlink_connection(connection_string)

    print("Waiting for heartbeat...")
    master.wait_heartbeat()
    print(f"Connected to system {master.target_system}\n")

    # Check current status
    is_armed = check_arm_status(master)
    if is_armed is not None:
        status = "ARMED" if is_armed else "DISARMED"
        print(f"Current status: {status}\n")

    # Arm vehicle
    if arm_vehicle(master):
        print("Waiting 5 seconds...\n")
        time.sleep(5)

        # Disarm vehicle
        disarm_vehicle(master)

    print("\nDone.")


if __name__ == '__main__':
    connection_string = sys.argv[1] if len(sys.argv) > 1 else 'udp:127.0.0.1:14550'
    main(connection_string)
