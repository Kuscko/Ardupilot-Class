#!/usr/bin/env python3
"""
Custom MAVLink Message Receiver (Python)
Receives and decodes custom MAVLink messages from ArduPilot
Author: Patrick Kelly (@Kuscko)
Version: 1.0
Last Updated: 2026-02-03

Requirements:
    pip install pymavlink

Usage:
    python3 python_receiver_example.py
    python3 python_receiver_example.py --connect udp:127.0.0.1:14550
"""

import sys
import time
import argparse
from pymavlink import mavutil


class CustomMAVLinkReceiver:
    """Receive and process custom MAVLink messages"""

    def __init__(self, connection_string):
        """Initialize receiver with connection string"""
        self.connection_string = connection_string
        self.master = None

        # Message IDs for custom messages
        self.MSG_ID_CUSTOM_SENSOR = 12000
        self.MSG_ID_CUSTOM_STATUS = 12001
        self.MSG_ID_CUSTOM_COMMAND = 12002
        self.MSG_ID_CUSTOM_PAYLOAD = 12003

    def connect(self):
        """Connect to vehicle"""
        print(f"Connecting to vehicle on {self.connection_string}...")

        try:
            self.master = mavutil.mavlink_connection(
                self.connection_string,
                dialect="ardupilotmega"  # Use ardupilotmega dialect
            )

            # Wait for heartbeat
            print("Waiting for heartbeat...")
            self.master.wait_heartbeat()
            print(f"Connected to system {self.master.target_system}, component {self.master.target_component}")

            return True

        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def receive_messages(self):
        """Main loop to receive and process messages"""
        print("\nListening for custom MAVLink messages...")
        print("Press Ctrl+C to stop\n")

        msg_count = {
            'CUSTOM_SENSOR_DATA': 0,
            'CUSTOM_STATUS': 0,
            'CUSTOM_COMMAND': 0,
            'CUSTOM_PAYLOAD_DATA': 0,
            'other': 0
        }

        try:
            while True:
                # Receive message (blocking with timeout)
                msg = self.master.recv_match(blocking=True, timeout=1.0)

                if msg is None:
                    continue

                # Get message type
                msg_type = msg.get_type()

                # Process custom messages by ID
                msg_id = msg.get_msgId() if hasattr(msg, 'get_msgId') else None

                if msg_id == self.MSG_ID_CUSTOM_SENSOR:
                    self.handle_custom_sensor(msg)
                    msg_count['CUSTOM_SENSOR_DATA'] += 1

                elif msg_id == self.MSG_ID_CUSTOM_STATUS:
                    self.handle_custom_status(msg)
                    msg_count['CUSTOM_STATUS'] += 1

                elif msg_id == self.MSG_ID_CUSTOM_COMMAND:
                    self.handle_custom_command(msg)
                    msg_count['CUSTOM_COMMAND'] += 1

                elif msg_id == self.MSG_ID_CUSTOM_PAYLOAD:
                    self.handle_custom_payload(msg)
                    msg_count['CUSTOM_PAYLOAD_DATA'] += 1

                else:
                    # Other standard MAVLink messages
                    msg_count['other'] += 1

                    # Optionally process standard messages
                    if msg_type in ['HEARTBEAT', 'STATUSTEXT']:
                        self.handle_standard_message(msg)

                # Print statistics every 10 seconds
                if time.time() % 10 < 0.1:
                    print(f"\nMessage counts: {msg_count}")

        except KeyboardInterrupt:
            print("\n\nStopped by user")
            print(f"Final message counts: {msg_count}")

    def handle_custom_sensor(self, msg):
        """Process CUSTOM_SENSOR_DATA message (ID 12000)"""
        try:
            timestamp = msg.timestamp_ms
            sensor1 = msg.sensor1_value
            sensor2 = msg.sensor2_value
            sensor3 = msg.sensor3_value
            status = msg.sensor_status

            print(f"[SENSOR] Time:{timestamp}ms S1:{sensor1:.2f} S2:{sensor2:.2f} S3:{sensor3:.2f} Status:{status}")

            # Process sensor data
            if status != 0:
                print(f"  WARNING: Sensor status error: {status}")

        except AttributeError as e:
            print(f"Error parsing CUSTOM_SENSOR_DATA: {e}")

    def handle_custom_status(self, msg):
        """Process CUSTOM_STATUS message (ID 12001)"""
        try:
            timestamp = msg.timestamp_ms
            flight_mode = msg.flight_mode
            health_flags = msg.health_flags
            battery_pct = msg.battery_remaining_pct
            mission_pct = msg.mission_progress_pct

            print(f"[STATUS] Mode:{flight_mode} Battery:{battery_pct:.0f}% Mission:{mission_pct:.0f}% Health:0x{health_flags:02X}")

            # Decode health flags
            ahrs_ok = (health_flags & 0x01) != 0
            gps_ok = (health_flags & 0x02) != 0
            battery_ok = (health_flags & 0x04) != 0

            if not ahrs_ok or not gps_ok or not battery_ok:
                print(f"  Health: AHRS:{ahrs_ok} GPS:{gps_ok} Battery:{battery_ok}")

        except AttributeError as e:
            print(f"Error parsing CUSTOM_STATUS: {e}")

    def handle_custom_command(self, msg):
        """Process CUSTOM_COMMAND message (ID 12002)"""
        try:
            target_system = msg.target_system
            target_component = msg.target_component
            command_id = msg.command_id
            param1 = msg.param1
            param2 = msg.param2
            param3 = msg.param3

            print(f"[COMMAND] ID:{command_id} Params:{param1:.2f},{param2:.2f},{param3:.2f}")

        except AttributeError as e:
            print(f"Error parsing CUSTOM_COMMAND: {e}")

    def handle_custom_payload(self, msg):
        """Process CUSTOM_PAYLOAD_DATA message (ID 12003)"""
        try:
            timestamp = msg.timestamp_ms
            temperature = msg.payload_temperature
            voltage = msg.payload_voltage
            state = msg.payload_state
            data = msg.payload_data  # Byte array

            print(f"[PAYLOAD] Temp:{temperature:.1f}C Voltage:{voltage:.2f}V State:{state}")

        except AttributeError as e:
            print(f"Error parsing CUSTOM_PAYLOAD_DATA: {e}")

    def handle_standard_message(self, msg):
        """Process standard MAVLink messages"""
        msg_type = msg.get_type()

        if msg_type == 'HEARTBEAT':
            # Optionally print heartbeat
            pass

        elif msg_type == 'STATUSTEXT':
            # Print status text messages
            severity = msg.severity
            text = msg.text
            print(f"[STATUSTEXT] Severity:{severity} {text}")

    def send_custom_command(self, command_id, param1=0, param2=0, param3=0):
        """Send CUSTOM_COMMAND to vehicle"""
        try:
            # Create CUSTOM_COMMAND message
            self.master.mav.send(
                self.master.mav.custom_command_encode(
                    self.master.target_system,      # target_system
                    self.master.target_component,   # target_component
                    command_id,                      # command_id
                    param1,                          # param1
                    param2,                          # param2
                    param3                           # param3
                )
            )

            print(f"Sent CUSTOM_COMMAND: ID={command_id} Params={param1},{param2},{param3}")

        except Exception as e:
            print(f"Error sending command: {e}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Receive custom MAVLink messages')
    parser.add_argument('--connect', default='udp:127.0.0.1:14550',
                        help='MAVLink connection string (default: udp:127.0.0.1:14550)')

    args = parser.parse_args()

    # Create receiver
    receiver = CustomMAVLinkReceiver(args.connect)

    # Connect to vehicle
    if not receiver.connect():
        sys.exit(1)

    # Receive messages
    receiver.receive_messages()


if __name__ == "__main__":
    main()


# ============================================
# USAGE EXAMPLES
# ============================================

# Basic usage (UDP):
#   python3 python_receiver_example.py

# Serial connection:
#   python3 python_receiver_example.py --connect /dev/ttyACM0:115200

# TCP connection:
#   python3 python_receiver_example.py --connect tcp:127.0.0.1:5760

# SITL connection:
#   python3 python_receiver_example.py --connect udp:127.0.0.1:14550

# ============================================
# IMPORTANT NOTES
# ============================================

# Custom Message Definition:
# - Requires custom MAVLink XML file (see custom_telemetry.xml)
# - Generate Python bindings with pymavlink
# - Copy generated files to Python path

# Generating Custom Bindings:
#   python -m pymavlink.tools.mavgen \
#       --lang=Python \
#       --wire-protocol=2.0 \
#       --output=generated/ \
#       custom_telemetry.xml

# Installing Generated Module:
#   cp -r generated/custom /path/to/python/site-packages/

# Using Custom Dialect:
#   from pymavlink.dialects.v20 import custom as mavlink
#   master = mavutil.mavlink_connection(connection_string, dialect="custom")

# ============================================
# TROUBLESHOOTING
# ============================================

# No messages received:
# - Check connection string is correct
# - Verify vehicle is sending custom messages
# - Use MAVLink Inspector to verify message IDs
# - Check firewall settings (UDP)
# - Verify custom dialect installed

# AttributeError on message fields:
# - Regenerate Python bindings from XML
# - Verify field names match XML definition
# - Check message ID matches

# Connection timeout:
# - Verify IP address and port
# - Check vehicle is running
# - Test with standard MAVLink messages first
# - Try different connection type (serial vs UDP)

# ============================================
# EXTENDING THIS SCRIPT
# ============================================

# To add more message handlers:
# 1. Define new MSG_ID constant
# 2. Add elif clause in receive_messages()
# 3. Create handler function (handle_xxx)
# 4. Process message fields

# To send commands to vehicle:
# 1. Use send_custom_command() method
# 2. Or create custom send function
# 3. Encode message with mav.xxx_encode()
# 4. Send with master.mav.send()

# To log messages to file:
# 1. Open CSV file
# 2. Write message fields to CSV
# 3. Close file on exit

# To forward messages:
# 1. Create second MAVLink connection
# 2. Receive on one, send on other
# 3. Optionally filter or transform
