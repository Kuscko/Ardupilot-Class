#!/usr/bin/env python3
"""
DroneKit Telemetry Monitor
Real-time telemetry monitoring and logging using DroneKit
Author: Patrick Kelly (@Kuscko)
Version: 1.0
Last Updated: 2026-02-03

Requirements:
    pip install dronekit

Usage:
    python3 dronekit_telemetry_monitor.py --connect /dev/ttyACM0 --baud 115200
    python3 dronekit_telemetry_monitor.py --connect udp:127.0.0.1:14550
"""

import time
import argparse
from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil


class TelemetryMonitor:
    """Monitor and display vehicle telemetry"""

    def __init__(self, connection_string, baud=115200):
        """Initialize telemetry monitor"""
        self.connection_string = connection_string
        self.baud = baud
        self.vehicle = None

    def connect_vehicle(self):
        """Connect to vehicle"""
        print(f"Connecting to vehicle on {self.connection_string}...")

        try:
            # Connect with baud rate if serial connection
            if self.connection_string.startswith('/dev/') or self.connection_string.startswith('COM'):
                self.vehicle = connect(self.connection_string, baud=self.baud, wait_ready=True)
            else:
                self.vehicle = connect(self.connection_string, wait_ready=True)

            print("Connected successfully!")
            return True

        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def print_vehicle_info(self):
        """Print basic vehicle information"""
        print("\n" + "=" * 60)
        print("VEHICLE INFORMATION")
        print("=" * 60)
        print(f"Autopilot Firmware version: {self.vehicle.version}")
        print(f"Autopilot capabilities: {self.vehicle.capabilities}")
        print(f"Vehicle type: {self.vehicle._vehicle_type}")
        print(f"Armed: {self.vehicle.armed}")
        print(f"Mode: {self.vehicle.mode.name}")
        print(f"Is armable: {self.vehicle.is_armable}")
        print(f"System status: {self.vehicle.system_status.state}")

    def print_battery_status(self):
        """Print battery information"""
        print("\n" + "=" * 60)
        print("BATTERY STATUS")
        print("=" * 60)
        print(f"Voltage: {self.vehicle.battery.voltage}V")
        print(f"Current: {self.vehicle.battery.current}A")
        print(f"Level: {self.vehicle.battery.level}%")

    def print_gps_status(self):
        """Print GPS information"""
        print("\n" + "=" * 60)
        print("GPS STATUS")
        print("=" * 60)
        print(f"GPS Fix: {self.vehicle.gps_0.fix_type}")
        print(f"Satellites visible: {self.vehicle.gps_0.satellites_visible}")
        print(f"EPH: {self.vehicle.gps_0.eph}")
        print(f"EPV: {self.vehicle.gps_0.epv}")

    def print_location(self):
        """Print location information"""
        print("\n" + "=" * 60)
        print("LOCATION")
        print("=" * 60)
        print(f"Global Location: {self.vehicle.location.global_frame}")
        print(f"Global Relative: {self.vehicle.location.global_relative_frame}")
        print(f"Local Location: {self.vehicle.location.local_frame}")
        print(f"Heading: {self.vehicle.heading}°")

    def print_attitude(self):
        """Print attitude information"""
        print("\n" + "=" * 60)
        print("ATTITUDE")
        print("=" * 60)
        print(f"Pitch: {self.vehicle.attitude.pitch * 57.2958:.2f}°")
        print(f"Roll: {self.vehicle.attitude.roll * 57.2958:.2f}°")
        print(f"Yaw: {self.vehicle.attitude.yaw * 57.2958:.2f}°")

    def print_velocity(self):
        """Print velocity information"""
        print("\n" + "=" * 60)
        print("VELOCITY")
        print("=" * 60)
        vx = self.vehicle.velocity[0] if self.vehicle.velocity[0] is not None else 0
        vy = self.vehicle.velocity[1] if self.vehicle.velocity[1] is not None else 0
        vz = self.vehicle.velocity[2] if self.vehicle.velocity[2] is not None else 0

        import math
        ground_speed = math.sqrt(vx**2 + vy**2)

        print(f"Velocity (NED): [{vx:.2f}, {vy:.2f}, {vz:.2f}] m/s")
        print(f"Ground Speed: {ground_speed:.2f} m/s")
        print(f"Airspeed: {self.vehicle.airspeed:.2f} m/s")
        print(f"Groundspeed: {self.vehicle.groundspeed:.2f} m/s")

    def print_ekf_status(self):
        """Print EKF status"""
        print("\n" + "=" * 60)
        print("EKF STATUS")
        print("=" * 60)
        print(f"EKF OK: {self.vehicle.ekf_ok}")

    def monitor_continuous(self, interval=2):
        """Continuously monitor and display telemetry"""
        print("\n" + "=" * 60)
        print("CONTINUOUS TELEMETRY MONITORING")
        print("Press Ctrl+C to stop")
        print("=" * 60)

        try:
            while True:
                # Clear screen (works on Linux/Mac, comment out for Windows)
                # import os
                # os.system('clear')

                print(f"\n{'=' * 60}")
                print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'=' * 60}")

                # Print basic status
                print(f"Mode: {self.vehicle.mode.name:<15} Armed: {self.vehicle.armed}")
                print(f"Alt:  {self.vehicle.location.global_relative_frame.alt:.1f}m")
                print(f"Bat:  {self.vehicle.battery.voltage:.2f}V ({self.vehicle.battery.level}%)")
                print(f"GPS:  {self.vehicle.gps_0.satellites_visible} sats, Fix: {self.vehicle.gps_0.fix_type}")
                print(f"Spd:  {self.vehicle.groundspeed:.1f} m/s")

                # Print attitude
                pitch = self.vehicle.attitude.pitch * 57.2958
                roll = self.vehicle.attitude.roll * 57.2958
                yaw = self.vehicle.attitude.yaw * 57.2958
                print(f"Att:  P:{pitch:6.1f}° R:{roll:6.1f}° Y:{yaw:6.1f}°")

                # Print position
                lat = self.vehicle.location.global_frame.lat
                lon = self.vehicle.location.global_frame.lon
                print(f"Pos:  {lat:.6f}, {lon:.6f}")

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user")

    def get_parameter(self, param_name):
        """Get a parameter value"""
        try:
            value = self.vehicle.parameters[param_name]
            print(f"{param_name} = {value}")
            return value
        except KeyError:
            print(f"Parameter {param_name} not found")
            return None

    def set_parameter(self, param_name, value):
        """Set a parameter value"""
        try:
            self.vehicle.parameters[param_name] = value
            print(f"Set {param_name} = {value}")
            return True
        except Exception as e:
            print(f"Failed to set {param_name}: {e}")
            return False

    def close(self):
        """Close vehicle connection"""
        if self.vehicle:
            print("\nClosing vehicle connection...")
            self.vehicle.close()
            print("Connection closed")


def main():
    """Main function"""

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='DroneKit Telemetry Monitor')
    parser.add_argument('--connect', required=True,
                        help='Vehicle connection string (e.g., /dev/ttyACM0, udp:127.0.0.1:14550)')
    parser.add_argument('--baud', type=int, default=115200,
                        help='Serial baud rate (default: 115200)')
    parser.add_argument('--continuous', action='store_true',
                        help='Enable continuous monitoring')
    parser.add_argument('--interval', type=int, default=2,
                        help='Update interval for continuous mode (seconds, default: 2)')

    args = parser.parse_args()

    # Create telemetry monitor
    monitor = TelemetryMonitor(args.connect, args.baud)

    # Connect to vehicle
    if not monitor.connect_vehicle():
        return 1

    try:
        # Print vehicle information
        monitor.print_vehicle_info()
        monitor.print_battery_status()
        monitor.print_gps_status()
        monitor.print_location()
        monitor.print_attitude()
        monitor.print_velocity()
        monitor.print_ekf_status()

        # Example: Get some parameters
        print("\n" + "=" * 60)
        print("PARAMETER EXAMPLES")
        print("=" * 60)
        monitor.get_parameter('ARMING_CHECK')
        monitor.get_parameter('THR_MAX')
        monitor.get_parameter('FLTMODE1')

        # Continuous monitoring if requested
        if args.continuous:
            monitor.monitor_continuous(args.interval)

    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user")

    finally:
        # Close connection
        monitor.close()

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())


# ============================================
# NOTES
# ============================================

# Connection strings:
# Serial (Linux):   /dev/ttyACM0
# Serial (Windows): COM3
# UDP:              udp:127.0.0.1:14550
# TCP:              tcp:127.0.0.1:5760
# SITL:             udp:127.0.0.1:14550

# Common DroneKit operations:

# Change mode:
#   vehicle.mode = VehicleMode("GUIDED")

# Arm vehicle:
#   vehicle.armed = True

# Wait for arm:
#   while not vehicle.armed:
#       time.sleep(1)

# Simple goto:
#   point = LocationGlobalRelative(-35.363, 149.165, 20)
#   vehicle.simple_goto(point)

# Send MAVLink command:
#   msg = vehicle.message_factory.command_long_encode(
#       0, 0, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
#       0, 1, 0, 0, 0, 0, 0, 0)
#   vehicle.send_mavlink(msg)

# Attribute listeners:
#   @vehicle.on_attribute('location.global_frame')
#   def listener(self, attr_name, value):
#       print(f"Position: {value}")

# Message listeners:
#   @vehicle.on_message('HEARTBEAT')
#   def listener(self, name, message):
#       print(f"Heartbeat: {message}")
