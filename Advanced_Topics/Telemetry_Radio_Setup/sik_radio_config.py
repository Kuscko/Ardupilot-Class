#!/usr/bin/env python3
"""
SiK Telemetry Radio Configuration Utility
Configure and monitor SiK radio modules (3DR Radio, RFD900, etc.)
Author: Patrick Kelly (@Kuscko)
Version: 1.0
Last Updated: 2026-02-03

Requirements:
    pip install pyserial

Usage:
    # Show current settings
    python3 sik_radio_config.py --port /dev/ttyUSB0

    # Configure radio
    python3 sik_radio_config.py --port /dev/ttyUSB0 --baud 57600 --air-speed 64

    # Enter AT command mode for manual configuration
    python3 sik_radio_config.py --port /dev/ttyUSB0 --interactive
"""

import serial
import time
import argparse
import sys


class SiKRadioConfig:
    """Configure SiK telemetry radios"""

    # AT command timeout
    AT_TIMEOUT = 3.0

    # Radio parameters (EEPROM S-registers)
    PARAMS = {
        'S0': 'FORMAT',           # EEPROM format version
        'S1': 'SERIAL_SPEED',     # Serial baud rate (0=1200, 1=2400, etc.)
        'S2': 'AIR_SPEED',        # Air data rate (2-256 kbps)
        'S3': 'NETID',            # Network ID (0-65535)
        'S4': 'TXPOWER',          # Transmit power (1-20 dBm for RFD900)
        'S5': 'ECC',              # Error correction (0=off, 1=on)
        'S6': 'MAVLINK',          # MAVLink framing (0=off, 1=on)
        'S7': 'OPPRESEND',        # Opportunistic resend (0=off, 1=on)
        'S8': 'MIN_FREQ',         # Min frequency (MHz)
        'S9': 'MAX_FREQ',         # Max frequency (MHz)
        'S10': 'NUM_CHANNELS',    # Number of frequency hopping channels
        'S11': 'DUTY_CYCLE',      # Duty cycle (0-100%)
        'S12': 'LBT_RSSI',        # Listen before talk RSSI threshold
        'S13': 'MANCHESTER',      # Manchester encoding (0=off, 1=on)
        'S14': 'RTSCTS',          # RTS/CTS flow control (0=off, 1=on)
        'S15': 'MAX_WINDOW',      # Max transmit window (ms)
    }

    # Serial baud rate encoding
    BAUD_RATES = {
        0: 1200, 1: 2400, 2: 4800, 3: 9600, 4: 19200,
        5: 38400, 6: 57600, 7: 115200, 8: 230400
    }

    def __init__(self, port, baudrate=57600):
        """Initialize radio connection"""
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.in_at_mode = False

    def connect(self):
        """Open serial connection"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1.0,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            print(f"Connected to {self.port} at {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            print(f"Failed to open {self.port}: {e}")
            return False

    def disconnect(self):
        """Close serial connection"""
        if self.ser and self.ser.is_open:
            if self.in_at_mode:
                self.exit_at_mode()
            self.ser.close()
            print("Disconnected")

    def enter_at_mode(self):
        """Enter AT command mode"""
        if self.in_at_mode:
            return True

        print("Entering AT command mode...")

        # Wait for radio to be ready (guard time)
        time.sleep(1.0)

        # Send +++ without newline
        self.ser.write(b'+++')
        self.ser.flush()

        # Wait for OK response
        start_time = time.time()
        response = b''
        while time.time() - start_time < self.AT_TIMEOUT:
            if self.ser.in_waiting:
                response += self.ser.read(self.ser.in_waiting)
                if b'OK' in response:
                    self.in_at_mode = True
                    print("Entered AT command mode")
                    return True
            time.sleep(0.1)

        print(f"Failed to enter AT mode. Response: {response}")
        return False

    def exit_at_mode(self):
        """Exit AT command mode"""
        if not self.in_at_mode:
            return True

        print("Exiting AT command mode...")
        self.send_at_command('ATO')
        self.in_at_mode = False
        print("Exited AT command mode")
        return True

    def send_at_command(self, command):
        """Send AT command and return response"""
        if not self.in_at_mode:
            if not self.enter_at_mode():
                return None

        # Clear input buffer
        self.ser.reset_input_buffer()

        # Send command with newline
        cmd_bytes = (command + '\r\n').encode('ascii')
        self.ser.write(cmd_bytes)
        self.ser.flush()

        # Read response
        start_time = time.time()
        response = b''
        while time.time() - start_time < self.AT_TIMEOUT:
            if self.ser.in_waiting:
                response += self.ser.read(self.ser.in_waiting)
                # Check for command echo + response + OK/ERROR
                if b'OK' in response or b'ERROR' in response:
                    break
            time.sleep(0.05)

        return response.decode('ascii', errors='replace').strip()

    def get_parameter(self, param):
        """Get radio parameter value"""
        response = self.send_at_command(f'AT{param}?')
        if response and '=' in response:
            try:
                value = int(response.split('=')[1].split()[0])
                return value
            except (ValueError, IndexError):
                pass
        return None

    def set_parameter(self, param, value):
        """Set radio parameter value"""
        response = self.send_at_command(f'AT{param}={value}')
        if response and 'OK' in response:
            return True
        return False

    def get_all_parameters(self):
        """Read all radio parameters"""
        print("\nReading radio parameters...")
        params = {}

        for param, name in self.PARAMS.items():
            value = self.get_parameter(param)
            if value is not None:
                params[param] = value
                # Format output
                display_value = value
                if param == 'S1' and value in self.BAUD_RATES:
                    display_value = f"{value} ({self.BAUD_RATES[value]} baud)"
                elif param == 'S2':
                    display_value = f"{value} kbps"
                elif param == 'S4':
                    display_value = f"{value} dBm"
                elif param in ['S8', 'S9']:
                    display_value = f"{value} MHz"

                print(f"  {param} ({name:20s}): {display_value}")
            else:
                print(f"  {param} ({name:20s}): [Read failed]")

        return params

    def get_radio_version(self):
        """Get radio firmware version"""
        response = self.send_at_command('ATI')
        if response:
            print(f"\nRadio firmware version:\n{response}")
            return response
        return None

    def get_rssi(self):
        """Get local and remote RSSI"""
        response = self.send_at_command('ATI5')
        if response:
            print(f"\nRSSI Information:\n{response}")
            return response
        return None

    def get_errors(self):
        """Get error statistics"""
        response = self.send_at_command('ATI7')
        if response:
            print(f"\nError Statistics:\n{response}")
            return response
        return None

    def save_parameters(self):
        """Save parameters to EEPROM"""
        print("\nSaving parameters to EEPROM...")
        response = self.send_at_command('AT&W')
        if response and 'OK' in response:
            print("Parameters saved successfully")
            return True
        else:
            print("Failed to save parameters")
            return False

    def reboot_radio(self):
        """Reboot the radio"""
        print("\nRebooting radio...")
        response = self.send_at_command('ATZ')
        self.in_at_mode = False
        time.sleep(2.0)
        print("Radio rebooted")
        return True

    def factory_reset(self):
        """Reset radio to factory defaults"""
        print("\nResetting to factory defaults...")
        response = self.send_at_command('AT&F')
        if response and 'OK' in response:
            print("Factory reset successful")
            self.save_parameters()
            return True
        else:
            print("Factory reset failed")
            return False

    def configure_basic(self, serial_baud=None, air_speed=None, netid=None,
                       txpower=None, ecc=None, mavlink=None):
        """Configure basic radio parameters"""
        print("\nConfiguring radio parameters...")

        changes_made = False

        if serial_baud is not None:
            # Convert baud rate to code
            baud_code = None
            for code, baud in self.BAUD_RATES.items():
                if baud == serial_baud:
                    baud_code = code
                    break

            if baud_code is not None:
                if self.set_parameter('S1', baud_code):
                    print(f"  Set serial baud rate to {serial_baud}")
                    changes_made = True
            else:
                print(f"  Invalid baud rate: {serial_baud}")

        if air_speed is not None:
            if 2 <= air_speed <= 256:
                if self.set_parameter('S2', air_speed):
                    print(f"  Set air speed to {air_speed} kbps")
                    changes_made = True
            else:
                print(f"  Air speed must be 2-256 kbps")

        if netid is not None:
            if 0 <= netid <= 65535:
                if self.set_parameter('S3', netid):
                    print(f"  Set network ID to {netid}")
                    changes_made = True
            else:
                print(f"  Network ID must be 0-65535")

        if txpower is not None:
            if 1 <= txpower <= 30:
                if self.set_parameter('S4', txpower):
                    print(f"  Set transmit power to {txpower} dBm")
                    changes_made = True
            else:
                print(f"  Transmit power must be 1-30 dBm")

        if ecc is not None:
            if self.set_parameter('S5', 1 if ecc else 0):
                print(f"  Set ECC to {'enabled' if ecc else 'disabled'}")
                changes_made = True

        if mavlink is not None:
            if self.set_parameter('S6', 1 if mavlink else 0):
                print(f"  Set MAVLink framing to {'enabled' if mavlink else 'disabled'}")
                changes_made = True

        if changes_made:
            print("\nSaving configuration...")
            self.save_parameters()
            print("Configuration complete. Please reboot radio for changes to take effect.")
        else:
            print("No changes made")

        return changes_made

    def interactive_mode(self):
        """Interactive AT command mode"""
        print("\n=== Interactive AT Command Mode ===")
        print("Enter AT commands (or 'exit' to quit)")
        print("Example commands: ATI, ATI5, ATS1?, ATS2=64")
        print()

        if not self.enter_at_mode():
            return

        try:
            while True:
                command = input("AT> ").strip()

                if command.lower() in ['exit', 'quit', 'q']:
                    break

                if not command:
                    continue

                # Add AT prefix if not present
                if not command.upper().startswith('AT'):
                    command = 'AT' + command

                response = self.send_at_command(command)
                if response:
                    print(response)

        except KeyboardInterrupt:
            print("\nExiting interactive mode...")

        finally:
            self.exit_at_mode()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='SiK Telemetry Radio Configuration Utility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show current settings
  python3 sik_radio_config.py --port /dev/ttyUSB0

  # Configure for 57600 baud with 64kbps air speed
  python3 sik_radio_config.py --port /dev/ttyUSB0 --baud 57600 --air-speed 64

  # Set network ID and transmit power
  python3 sik_radio_config.py --port /dev/ttyUSB0 --netid 25 --txpower 20

  # Interactive mode
  python3 sik_radio_config.py --port /dev/ttyUSB0 --interactive

  # Factory reset
  python3 sik_radio_config.py --port /dev/ttyUSB0 --factory-reset
        """
    )

    parser.add_argument('--port', required=True,
                        help='Serial port (e.g., /dev/ttyUSB0 or COM3)')
    parser.add_argument('--port-baud', type=int, default=57600,
                        help='Serial port baud rate for connection (default: 57600)')

    # Configuration parameters
    parser.add_argument('--baud', type=int,
                        choices=[1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400],
                        help='Set radio serial baud rate')
    parser.add_argument('--air-speed', type=int,
                        help='Set air data rate (2-256 kbps)')
    parser.add_argument('--netid', type=int,
                        help='Set network ID (0-65535, match both radios)')
    parser.add_argument('--txpower', type=int,
                        help='Set transmit power in dBm (1-30, usually 1-20)')
    parser.add_argument('--ecc', action='store_true',
                        help='Enable error correction')
    parser.add_argument('--no-ecc', action='store_true',
                        help='Disable error correction')
    parser.add_argument('--mavlink', action='store_true',
                        help='Enable MAVLink framing')
    parser.add_argument('--no-mavlink', action='store_true',
                        help='Disable MAVLink framing')

    # Actions
    parser.add_argument('--interactive', action='store_true',
                        help='Enter interactive AT command mode')
    parser.add_argument('--factory-reset', action='store_true',
                        help='Reset radio to factory defaults')
    parser.add_argument('--reboot', action='store_true',
                        help='Reboot the radio')
    parser.add_argument('--show-rssi', action='store_true',
                        help='Show RSSI information')
    parser.add_argument('--show-errors', action='store_true',
                        help='Show error statistics')

    args = parser.parse_args()

    # Create radio config object
    radio = SiKRadioConfig(args.port, args.port_baud)

    # Connect to radio
    if not radio.connect():
        sys.exit(1)

    try:
        # Handle special modes
        if args.interactive:
            radio.interactive_mode()
            return

        if args.factory_reset:
            radio.factory_reset()
            radio.reboot_radio()
            return

        # Show radio information
        radio.get_radio_version()
        radio.get_all_parameters()

        if args.show_rssi:
            radio.get_rssi()

        if args.show_errors:
            radio.get_errors()

        # Configure parameters if requested
        ecc_val = None
        if args.ecc:
            ecc_val = True
        elif args.no_ecc:
            ecc_val = False

        mavlink_val = None
        if args.mavlink:
            mavlink_val = True
        elif args.no_mavlink:
            mavlink_val = False

        if any([args.baud, args.air_speed, args.netid, args.txpower,
                ecc_val is not None, mavlink_val is not None]):
            radio.configure_basic(
                serial_baud=args.baud,
                air_speed=args.air_speed,
                netid=args.netid,
                txpower=args.txpower,
                ecc=ecc_val,
                mavlink=mavlink_val
            )

        if args.reboot:
            radio.reboot_radio()

    finally:
        radio.disconnect()


if __name__ == "__main__":
    main()


# ============================================
# USAGE NOTES
# ============================================

# Common SiK Radio Settings:
# --------------------------
# 3DR Radio (915 MHz):
#   Serial: 57600 baud
#   Air: 64 kbps
#   TxPower: 20 dBm
#   NetID: 25 (default)
#
# RFD900/900+:
#   Serial: 57600 baud
#   Air: 64 kbps
#   TxPower: 20 dBm (up to 30 dBm for 900+)
#   NetID: Match both radios
#
# HolyBro SiK:
#   Serial: 57600 baud
#   Air: 64 kbps
#   TxPower: 20 dBm
#   NetID: 25

# Parameter Recommendations:
# -------------------------
# S1 (SERIAL_SPEED): Match flight controller SERIAL port baud (usually 57600)
# S2 (AIR_SPEED): 64 kbps for most applications, lower for longer range
# S3 (NETID): Use unique ID to avoid interference from other radios
# S4 (TXPOWER): Maximum allowed by regulations (check local laws)
# S5 (ECC): Enable for better error correction (slight performance cost)
# S6 (MAVLINK): Enable for MAVLink optimization
# S7 (OPPRESEND): Enable for better throughput
# S14 (RTSCTS): Disable for most applications

# Troubleshooting:
# ---------------
# 1. Can't enter AT mode:
#    - Ensure correct baud rate (try 57600, 115200, 38400)
#    - Disconnect from flight controller
#    - Try different USB cable
#    - Wait full second before +++
#
# 2. Poor range:
#    - Increase transmit power
#    - Lower air speed (32 or 16 kbps)
#    - Check antenna connections
#    - Verify frequency settings
#    - Enable ECC
#
# 3. Link drops frequently:
#    - Check RSSI with --show-rssi
#    - Verify NetID matches on both radios
#    - Check for interference
#    - Reduce air speed
#    - Enable error correction
#
# 4. No connection:
#    - Verify serial baud rate matches
#    - Check wiring (TX->RX, RX->TX, GND->GND)
#    - Ensure power supply adequate (5V, 500mA+)
#    - Try factory reset
