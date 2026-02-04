#!/usr/bin/env python3
"""
ArduPilot Log Parser
Automated analysis of ArduPilot binary logs

Usage:
    python3 log_parser.py logfile.BIN
    python3 log_parser.py logfile.BIN --report report.txt

Author: Patrick Kelly (@Kuscko)
Version: 1.0
"""

import sys
import subprocess
import statistics
from pathlib import Path


class LogParser:
    def __init__(self, logfile):
        self.logfile = logfile
        self.data = {}
        self.issues = []
        self.warnings = []

    def parse_log(self):
        """Parse log file and extract key metrics"""
        print(f"Parsing {self.logfile}...")

        try:
            # Use mavlogdump.py to extract data
            result = subprocess.run(
                ['mavlogdump.py', '--types', 'VIBE,GPS,EKF,BATT,MODE', self.logfile],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                return False

            self._process_output(result.stdout)
            return True

        except FileNotFoundError:
            print("Error: mavlogdump.py not found. Install MAVProxy:")
            print("  pip install --user MAVProxy")
            return False
        except subprocess.TimeoutExpired:
            print("Error: Parsing timed out")
            return False

    def _process_output(self, output):
        """Process mavlogdump output"""
        vibration_x = []
        vibration_y = []
        vibration_z = []
        gps_sats = []
        gps_hdop = []
        ekf_vn = []
        battery_volts = []
        mode_changes = []

        for line in output.split('\n'):
            # Parse VIBE messages
            if 'VIBE' in line and 'VibeX' in line:
                try:
                    parts = line.split()
                    for part in parts:
                        if 'VibeX' in part:
                            val = float(part.split(':')[1])
                            vibration_x.append(val)
                        elif 'VibeY' in part:
                            val = float(part.split(':')[1])
                            vibration_y.append(val)
                        elif 'VibeZ' in part:
                            val = float(part.split(':')[1])
                            vibration_z.append(val)
                except (ValueError, IndexError):
                    pass

            # Parse GPS messages
            elif 'GPS' in line and 'NSats' in line:
                try:
                    parts = line.split()
                    for part in parts:
                        if 'NSats' in part:
                            val = int(part.split(':')[1])
                            gps_sats.append(val)
                        elif 'HDop' in part:
                            val = float(part.split(':')[1])
                            gps_hdop.append(val)
                except (ValueError, IndexError):
                    pass

            # Parse EKF messages
            elif 'EKF' in line and 'VN' in line:
                try:
                    parts = line.split()
                    for part in parts:
                        if part.startswith('VN:'):
                            val = float(part.split(':')[1])
                            ekf_vn.append(val)
                except (ValueError, IndexError):
                    pass

            # Parse BATT messages
            elif 'BATT' in line and 'Volt' in line:
                try:
                    parts = line.split()
                    for part in parts:
                        if 'Volt' in part and not 'CellVolt' in part:
                            val = float(part.split(':')[1])
                            battery_volts.append(val)
                except (ValueError, IndexError):
                    pass

            # Parse MODE messages
            elif 'MODE' in line and 'Mode' in line:
                mode_changes.append(line)

        # Store data
        self.data['vibration_x'] = vibration_x
        self.data['vibration_y'] = vibration_y
        self.data['vibration_z'] = vibration_z
        self.data['gps_sats'] = gps_sats
        self.data['gps_hdop'] = gps_hdop
        self.data['ekf_vn'] = ekf_vn
        self.data['battery_volts'] = battery_volts
        self.data['mode_changes'] = mode_changes

    def analyze(self):
        """Analyze parsed data and identify issues"""
        print("\nAnalyzing log data...\n")

        # Vibration analysis
        if self.data.get('vibration_x'):
            vibe_x_max = max(self.data['vibration_x'])
            vibe_y_max = max(self.data['vibration_y'])
            vibe_z_max = max(self.data['vibration_z'])
            vibe_max = max(vibe_x_max, vibe_y_max, vibe_z_max)

            if vibe_max > 60:
                self.issues.append(f"CRITICAL: High vibration detected ({vibe_max:.1f} m/s²)")
            elif vibe_max > 30:
                self.warnings.append(f"WARNING: Elevated vibration ({vibe_max:.1f} m/s²)")

        # GPS analysis
        if self.data.get('gps_sats'):
            sats_min = min(self.data['gps_sats'])
            sats_avg = statistics.mean(self.data['gps_sats'])

            if sats_min < 6:
                self.issues.append(f"CRITICAL: Low GPS satellites (min: {sats_min})")
            elif sats_min < 10:
                self.warnings.append(f"WARNING: Marginal GPS satellites (min: {sats_min})")

        if self.data.get('gps_hdop'):
            hdop_max = max(self.data['gps_hdop'])

            if hdop_max > 2.5:
                self.issues.append(f"CRITICAL: Poor GPS accuracy (HDop: {hdop_max:.2f})")
            elif hdop_max > 1.5:
                self.warnings.append(f"WARNING: Marginal GPS accuracy (HDop: {hdop_max:.2f})")

        # EKF analysis
        if self.data.get('ekf_vn'):
            ekf_max = max(self.data['ekf_vn'])

            if ekf_max > 0.5:
                self.issues.append(f"CRITICAL: EKF variance high ({ekf_max:.3f})")
            elif ekf_max > 0.25:
                self.warnings.append(f"WARNING: EKF variance elevated ({ekf_max:.3f})")

        # Battery analysis
        if self.data.get('battery_volts'):
            volt_min = min(self.data['battery_volts'])

            if volt_min < 10.0:
                self.issues.append(f"CRITICAL: Battery voltage low ({volt_min:.2f}V)")
            elif volt_min < 10.5:
                self.warnings.append(f"WARNING: Battery voltage marginal ({volt_min:.2f}V)")

    def generate_report(self):
        """Generate analysis report"""
        report = []
        report.append("=" * 60)
        report.append("ArduPilot Log Analysis Report")
        report.append("=" * 60)
        report.append(f"Log file: {self.logfile}")
        report.append("")

        # Statistics
        report.append("Statistics:")
        report.append("-" * 60)

        if self.data.get('vibration_x'):
            vibe_x_avg = statistics.mean(self.data['vibration_x'])
            vibe_y_avg = statistics.mean(self.data['vibration_y'])
            vibe_z_avg = statistics.mean(self.data['vibration_z'])
            report.append(f"Vibration (avg):  X={vibe_x_avg:.1f}  Y={vibe_y_avg:.1f}  Z={vibe_z_avg:.1f} m/s²")

        if self.data.get('gps_sats'):
            sats_avg = statistics.mean(self.data['gps_sats'])
            report.append(f"GPS Satellites (avg): {sats_avg:.1f}")

        if self.data.get('gps_hdop'):
            hdop_avg = statistics.mean(self.data['gps_hdop'])
            report.append(f"GPS HDop (avg): {hdop_avg:.2f}")

        if self.data.get('ekf_vn'):
            ekf_avg = statistics.mean(self.data['ekf_vn'])
            report.append(f"EKF Variance (avg): {ekf_avg:.3f}")

        if self.data.get('battery_volts'):
            volt_avg = statistics.mean(self.data['battery_volts'])
            volt_min = min(self.data['battery_volts'])
            report.append(f"Battery Voltage:  Avg={volt_avg:.2f}V  Min={volt_min:.2f}V")

        report.append("")

        # Mode changes
        if self.data.get('mode_changes'):
            report.append(f"Mode Changes: {len(self.data['mode_changes'])}")
            for mode in self.data['mode_changes'][:5]:  # First 5
                report.append(f"  {mode.strip()}")
            if len(self.data['mode_changes']) > 5:
                report.append(f"  ... and {len(self.data['mode_changes'])-5} more")
            report.append("")

        # Issues
        if self.issues:
            report.append("CRITICAL ISSUES:")
            report.append("-" * 60)
            for issue in self.issues:
                report.append(f"  {issue}")
            report.append("")

        # Warnings
        if self.warnings:
            report.append("WARNINGS:")
            report.append("-" * 60)
            for warning in self.warnings:
                report.append(f"  {warning}")
            report.append("")

        # Summary
        report.append("=" * 60)
        if not self.issues and not self.warnings:
            report.append("STATUS: All checks passed")
        elif self.issues:
            report.append("STATUS: ISSUES FOUND - Review critical items above")
        else:
            report.append("STATUS: Minor warnings - Review recommended")
        report.append("=" * 60)

        return "\n".join(report)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 log_parser.py logfile.BIN [--report output.txt]")
        sys.exit(1)

    logfile = sys.argv[1]

    if not Path(logfile).exists():
        print(f"Error: File not found: {logfile}")
        sys.exit(1)

    # Parse and analyze
    parser = LogParser(logfile)

    if not parser.parse_log():
        sys.exit(1)

    parser.analyze()

    # Generate report
    report = parser.generate_report()
    print(report)

    # Save to file if requested
    if '--report' in sys.argv:
        idx = sys.argv.index('--report')
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"\nReport saved to: {output_file}")


if __name__ == "__main__":
    main()
