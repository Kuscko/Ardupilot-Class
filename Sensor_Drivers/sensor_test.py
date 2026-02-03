#!/usr/bin/env python3
"""
Sensor Data Monitor
Displays real-time sensor readings from all major sensors

Usage:
    python3 sensor_test.py [connection_string]

Example:
    python3 sensor_test.py udp:127.0.0.1:14550

Author: Patrick Kelly (@Kuscko)
Version: 1.0
"""

import sys
import time
from pymavlink import mavutil


class SensorMonitor:
    def __init__(self, master):
        self.master = master
        self.last_update = {}

    def monitor_sensors(self):
        """Monitor all sensor data"""
        print("\nSensor Data Monitor")
        print("=" * 80)
        print("Monitoring sensors... (Ctrl+C to exit)\n")

        try:
            while True:
                msg = master.recv_match(blocking=False)

                if msg is None:
                    time.sleep(0.01)
                    continue

                msg_type = msg.get_type()

                # GPS Data
                if msg_type == 'GPS_RAW_INT':
                    self.print_gps(msg)

                # IMU Data
                elif msg_type == 'RAW_IMU':
                    self.print_imu(msg)

                # Barometer (via VFR_HUD for altitude)
                elif msg_type == 'VFR_HUD':
                    self.print_baro(msg)

                # Compass
                elif msg_type == 'ATTITUDE':
                    self.print_compass(msg)

                # Airspeed
                elif msg_type == 'VFR_HUD':
                    self.print_airspeed(msg)

        except KeyboardInterrupt:
            print("\n\nMonitoring stopped")

    def print_gps(self, msg):
        """Print GPS data"""
        if self.should_print('GPS', 2.0):
            print(f"\n[GPS] Sats: {msg.satellites_visible}, "
                  f"Fix: {msg.fix_type}, "
                  f"HDOP: {msg.eph/100.0:.2f}, "
                  f"Lat: {msg.lat/1e7:.6f}, "
                  f"Lon: {msg.lon/1e7:.6f}, "
                  f"Alt: {msg.alt/1000.0:.1f}m")

    def print_imu(self, msg):
        """Print IMU data"""
        if self.should_print('IMU', 5.0):
            # Convert to m/s² and rad/s
            acc_x = msg.xacc / 1000.0 * 9.81
            acc_y = msg.yacc / 1000.0 * 9.81
            acc_z = msg.zacc / 1000.0 * 9.81
            gyro_x = msg.xgyro / 1000.0
            gyro_y = msg.ygyro / 1000.0
            gyro_z = msg.zgyro / 1000.0

            print(f"\n[IMU] Accel: [{acc_x:6.2f}, {acc_y:6.2f}, {acc_z:6.2f}] m/s²")
            print(f"      Gyro:  [{gyro_x:6.3f}, {gyro_y:6.3f}, {gyro_z:6.3f}] rad/s")

    def print_baro(self, msg):
        """Print barometer/altitude data"""
        if self.should_print('BARO', 3.0):
            print(f"\n[BARO] Altitude: {msg.alt:.1f}m, "
                  f"Climb: {msg.climb:.2f}m/s")

    def print_compass(self, msg):
        """Print compass/attitude data"""
        if self.should_print('COMPASS', 3.0):
            import math
            # Convert to degrees
            roll = math.degrees(msg.roll)
            pitch = math.degrees(msg.pitch)
            yaw = math.degrees(msg.yaw)

            print(f"\n[COMPASS] Roll: {roll:6.1f}°, "
                  f"Pitch: {pitch:6.1f}°, "
                  f"Yaw: {yaw:6.1f}°")

    def print_airspeed(self, msg):
        """Print airspeed data"""
        if self.should_print('AIRSPEED', 3.0):
            print(f"\n[AIRSPEED] {msg.airspeed:.1f} m/s "
                  f"({msg.airspeed * 3.6:.1f} km/h)")

    def should_print(self, sensor, interval):
        """Rate limit printing"""
        current_time = time.time()
        last = self.last_update.get(sensor, 0)

        if current_time - last > interval:
            self.last_update[sensor] = current_time
            return True
        return False


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

        monitor = SensorMonitor(master)
        monitor.monitor_sensors()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
