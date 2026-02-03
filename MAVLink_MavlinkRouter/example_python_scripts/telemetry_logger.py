#!/usr/bin/env python3
"""
Telemetry Logger
Logs telemetry data to CSV file for analysis

Usage:
    python3 telemetry_logger.py [connection_string] [output_file]

Example:
    python3 telemetry_logger.py udp:127.0.0.1:14550 flight_log.csv

Author: Patrick Kelly (@Kuscko)
Version: 1.0
"""

import sys
import time
import csv
from pymavlink import mavutil


class TelemetryLogger:
    def __init__(self, master, output_file):
        self.master = master
        self.output_file = output_file
        self.data = {}
        self.csv_writer = None
        self.csv_file = None

    def start_logging(self):
        """Start logging telemetry"""
        print(f"\nLogging telemetry to {self.output_file}")
        print("Press Ctrl+C to stop\n")

        # Open CSV file
        self.csv_file = open(self.output_file, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)

        # Write header
        header = [
            'timestamp',
            'lat', 'lon', 'alt',
            'vx', 'vy', 'vz',
            'roll', 'pitch', 'yaw',
            'airspeed', 'groundspeed',
            'throttle', 'climb_rate',
            'mode', 'armed',
            'gps_sats', 'gps_fix'
        ]
        self.csv_writer.writerow(header)

        log_interval = 0.2  # 5 Hz
        last_log = 0

        try:
            while True:
                msg = self.master.recv_match(blocking=False)

                if msg is None:
                    time.sleep(0.01)
                    continue

                # Collect data from different messages
                msg_type = msg.get_type()

                if msg_type == 'GLOBAL_POSITION_INT':
                    self.data['lat'] = msg.lat / 1e7
                    self.data['lon'] = msg.lon / 1e7
                    self.data['alt'] = msg.alt / 1000.0
                    self.data['vx'] = msg.vx / 100.0
                    self.data['vy'] = msg.vy / 100.0
                    self.data['vz'] = msg.vz / 100.0

                elif msg_type == 'ATTITUDE':
                    import math
                    self.data['roll'] = math.degrees(msg.roll)
                    self.data['pitch'] = math.degrees(msg.pitch)
                    self.data['yaw'] = math.degrees(msg.yaw)

                elif msg_type == 'VFR_HUD':
                    self.data['airspeed'] = msg.airspeed
                    self.data['groundspeed'] = msg.groundspeed
                    self.data['throttle'] = msg.throttle
                    self.data['climb_rate'] = msg.climb

                elif msg_type == 'HEARTBEAT':
                    self.data['mode'] = msg.custom_mode
                    self.data['armed'] = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0

                elif msg_type == 'GPS_RAW_INT':
                    self.data['gps_sats'] = msg.satellites_visible
                    self.data['gps_fix'] = msg.fix_type

                # Write to CSV every log_interval seconds
                current_time = time.time()
                if current_time - last_log >= log_interval:
                    self.write_row()
                    last_log = current_time

        except KeyboardInterrupt:
            print("\n\nStopping logger...")
            self.csv_file.close()
            print(f"Log saved to {self.output_file}")

    def write_row(self):
        """Write current data to CSV"""
        row = [
            time.time(),
            self.data.get('lat', 0),
            self.data.get('lon', 0),
            self.data.get('alt', 0),
            self.data.get('vx', 0),
            self.data.get('vy', 0),
            self.data.get('vz', 0),
            self.data.get('roll', 0),
            self.data.get('pitch', 0),
            self.data.get('yaw', 0),
            self.data.get('airspeed', 0),
            self.data.get('groundspeed', 0),
            self.data.get('throttle', 0),
            self.data.get('climb_rate', 0),
            self.data.get('mode', 0),
            self.data.get('armed', False),
            self.data.get('gps_sats', 0),
            self.data.get('gps_fix', 0),
        ]
        self.csv_writer.writerow(row)

        # Print status
        if int(time.time()) % 5 == 0:  # Every 5 seconds
            print(f"Logging... Alt: {self.data.get('alt', 0):.1f}m, "
                  f"Speed: {self.data.get('airspeed', 0):.1f}m/s, "
                  f"Armed: {self.data.get('armed', False)}")


def main():
    # Connection string
    if len(sys.argv) > 1:
        connection_string = sys.argv[1]
    else:
        connection_string = 'udp:127.0.0.1:14550'

    # Output file
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = f'telemetry_log_{int(time.time())}.csv'

    print(f"Connecting to {connection_string}...")

    try:
        master = mavutil.mavlink_connection(connection_string)
        master.wait_heartbeat()

        print(f"Connected to system {master.target_system}")

        logger = TelemetryLogger(master, output_file)
        logger.start_logging()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
