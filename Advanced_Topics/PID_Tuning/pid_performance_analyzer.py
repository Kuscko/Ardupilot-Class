#!/usr/bin/env python3
"""
PID Performance Analyzer
Analyzes and graphs PID tuning performance from ArduPilot logs
Author: Patrick Kelly (@Kuscko)
Version: 1.0
Last Updated: 2026-02-03

Requirements:
    pip install matplotlib pymavlink numpy

Usage:
    python3 pid_performance_analyzer.py logfile.BIN
    python3 pid_performance_analyzer.py logfile.BIN --output graphs/
"""

import sys
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from pymavlink import mavutil


class PIDAnalyzer:
    """Analyze PID performance from ArduPilot logs"""

    def __init__(self, logfile):
        """Initialize analyzer with log file"""
        self.logfile = logfile
        self.roll_data = {'time': [], 'actual': [], 'desired': []}
        self.pitch_data = {'time': [], 'actual': [], 'desired': []}
        self.yaw_data = {'time': [], 'actual': [], 'desired': []}
        self.rate_roll_data = {'time': [], 'actual': [], 'desired': []}
        self.rate_pitch_data = {'time': [], 'actual': [], 'desired': []}
        self.rate_yaw_data = {'time': [], 'actual': [], 'desired': []}

    def parse_log(self):
        """Parse log file and extract PID data"""
        print(f"Parsing {self.logfile}...")

        try:
            mlog = mavutil.mavlink_connection(self.logfile)
        except Exception as e:
            print(f"Error opening log file: {e}")
            return False

        # Track start time for relative timestamps
        start_time = None

        # Parse messages
        msg_count = 0
        while True:
            msg = mlog.recv_match(type=['ATT', 'RATE'], blocking=False)
            if msg is None:
                break

            msg_count += 1
            if msg_count % 1000 == 0:
                print(f"  Processed {msg_count} messages...", end='\r')

            msg_type = msg.get_type()

            # Get timestamp
            if hasattr(msg, 'TimeUS'):
                timestamp_us = msg.TimeUS
            else:
                continue

            if start_time is None:
                start_time = timestamp_us

            # Convert to seconds from start
            time_s = (timestamp_us - start_time) / 1.0e6

            # Parse ATT messages (attitude)
            if msg_type == 'ATT':
                # Roll
                if hasattr(msg, 'Roll') and hasattr(msg, 'DesRoll'):
                    self.roll_data['time'].append(time_s)
                    self.roll_data['actual'].append(np.rad2deg(msg.Roll))
                    self.roll_data['desired'].append(np.rad2deg(msg.DesRoll))

                # Pitch
                if hasattr(msg, 'Pitch') and hasattr(msg, 'DesPitch'):
                    self.pitch_data['time'].append(time_s)
                    self.pitch_data['actual'].append(np.rad2deg(msg.Pitch))
                    self.pitch_data['desired'].append(np.rad2deg(msg.DesPitch))

                # Yaw
                if hasattr(msg, 'Yaw') and hasattr(msg, 'DesYaw'):
                    self.yaw_data['time'].append(time_s)
                    self.yaw_data['actual'].append(np.rad2deg(msg.Yaw))
                    self.yaw_data['desired'].append(np.rad2deg(msg.DesYaw))

            # Parse RATE messages (rate controller)
            elif msg_type == 'RATE':
                # Roll rate
                if hasattr(msg, 'R') and hasattr(msg, 'RDes'):
                    self.rate_roll_data['time'].append(time_s)
                    self.rate_roll_data['actual'].append(np.rad2deg(msg.R))
                    self.rate_roll_data['desired'].append(np.rad2deg(msg.RDes))

                # Pitch rate
                if hasattr(msg, 'P') and hasattr(msg, 'PDes'):
                    self.rate_pitch_data['time'].append(time_s)
                    self.rate_pitch_data['actual'].append(np.rad2deg(msg.P))
                    self.rate_pitch_data['desired'].append(np.rad2deg(msg.PDes))

                # Yaw rate
                if hasattr(msg, 'Y') and hasattr(msg, 'YDes'):
                    self.rate_yaw_data['time'].append(time_s)
                    self.rate_yaw_data['actual'].append(np.rad2deg(msg.Y))
                    self.rate_yaw_data['desired'].append(np.rad2deg(msg.YDes))

        print(f"\n  Parsed {msg_count} messages")
        print(f"  Roll samples: {len(self.roll_data['time'])}")
        print(f"  Pitch samples: {len(self.pitch_data['time'])}")
        print(f"  Yaw samples: {len(self.yaw_data['time'])}")

        return True

    def analyze_performance(self):
        """Analyze PID performance and detect issues"""
        print("\nAnalyzing PID performance...")

        issues = []

        # Analyze roll
        if len(self.roll_data['time']) > 0:
            roll_error = np.array(self.roll_data['actual']) - np.array(self.roll_data['desired'])
            roll_rms = np.sqrt(np.mean(roll_error**2))
            print(f"  Roll RMS error: {roll_rms:.2f}°")

            if roll_rms > 5.0:
                issues.append(f"High roll error (RMS: {roll_rms:.2f}°) - tune RLL_RATE_P/I/D")

            # Check for oscillation (high frequency variation)
            if len(roll_error) > 10:
                roll_variation = np.std(np.diff(roll_error))
                if roll_variation > 2.0:
                    issues.append(f"Roll oscillation detected (variation: {roll_variation:.2f}) - reduce RLL_RATE_P or increase RLL_RATE_D")

        # Analyze pitch
        if len(self.pitch_data['time']) > 0:
            pitch_error = np.array(self.pitch_data['actual']) - np.array(self.pitch_data['desired'])
            pitch_rms = np.sqrt(np.mean(pitch_error**2))
            print(f"  Pitch RMS error: {pitch_rms:.2f}°")

            if pitch_rms > 5.0:
                issues.append(f"High pitch error (RMS: {pitch_rms:.2f}°) - tune PTCH_RATE_P/I/D")

            # Check for oscillation
            if len(pitch_error) > 10:
                pitch_variation = np.std(np.diff(pitch_error))
                if pitch_variation > 2.0:
                    issues.append(f"Pitch oscillation detected (variation: {pitch_variation:.2f}) - reduce PTCH_RATE_P or increase PTCH_RATE_D")

        # Print issues
        if issues:
            print("\n  Issues detected:")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print("\n  No major tuning issues detected")

        return issues

    def plot_attitude(self, output_dir=None):
        """Plot attitude (roll, pitch, yaw)"""
        print("\nGenerating attitude plots...")

        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        fig.suptitle('Attitude Control Performance', fontsize=16)

        # Roll
        if len(self.roll_data['time']) > 0:
            axes[0].plot(self.roll_data['time'], self.roll_data['desired'],
                        'g--', label='Desired', linewidth=2)
            axes[0].plot(self.roll_data['time'], self.roll_data['actual'],
                        'b-', label='Actual', linewidth=1, alpha=0.7)
            axes[0].set_ylabel('Roll (degrees)')
            axes[0].legend(loc='upper right')
            axes[0].grid(True, alpha=0.3)

        # Pitch
        if len(self.pitch_data['time']) > 0:
            axes[1].plot(self.pitch_data['time'], self.pitch_data['desired'],
                        'g--', label='Desired', linewidth=2)
            axes[1].plot(self.pitch_data['time'], self.pitch_data['actual'],
                        'b-', label='Actual', linewidth=1, alpha=0.7)
            axes[1].set_ylabel('Pitch (degrees)')
            axes[1].legend(loc='upper right')
            axes[1].grid(True, alpha=0.3)

        # Yaw
        if len(self.yaw_data['time']) > 0:
            axes[2].plot(self.yaw_data['time'], self.yaw_data['desired'],
                        'g--', label='Desired', linewidth=2)
            axes[2].plot(self.yaw_data['time'], self.yaw_data['actual'],
                        'b-', label='Actual', linewidth=1, alpha=0.7)
            axes[2].set_ylabel('Yaw (degrees)')
            axes[2].set_xlabel('Time (seconds)')
            axes[2].legend(loc='upper right')
            axes[2].grid(True, alpha=0.3)

        plt.tight_layout()

        if output_dir:
            output_path = Path(output_dir) / 'attitude_performance.png'
            plt.savefig(output_path, dpi=150)
            print(f"  Saved: {output_path}")
        else:
            plt.show()

        plt.close()

    def plot_errors(self, output_dir=None):
        """Plot tracking errors"""
        print("\nGenerating error plots...")

        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        fig.suptitle('Attitude Tracking Errors', fontsize=16)

        # Roll error
        if len(self.roll_data['time']) > 0:
            roll_error = np.array(self.roll_data['actual']) - np.array(self.roll_data['desired'])
            axes[0].plot(self.roll_data['time'], roll_error, 'r-', linewidth=1)
            axes[0].axhline(y=0, color='k', linestyle='--', alpha=0.3)
            axes[0].set_ylabel('Roll Error (degrees)')
            axes[0].grid(True, alpha=0.3)

        # Pitch error
        if len(self.pitch_data['time']) > 0:
            pitch_error = np.array(self.pitch_data['actual']) - np.array(self.pitch_data['desired'])
            axes[1].plot(self.pitch_data['time'], pitch_error, 'r-', linewidth=1)
            axes[1].axhline(y=0, color='k', linestyle='--', alpha=0.3)
            axes[1].set_ylabel('Pitch Error (degrees)')
            axes[1].grid(True, alpha=0.3)

        # Yaw error
        if len(self.yaw_data['time']) > 0:
            yaw_error = np.array(self.yaw_data['actual']) - np.array(self.yaw_data['desired'])
            axes[2].plot(self.yaw_data['time'], yaw_error, 'r-', linewidth=1)
            axes[2].axhline(y=0, color='k', linestyle='--', alpha=0.3)
            axes[2].set_ylabel('Yaw Error (degrees)')
            axes[2].set_xlabel('Time (seconds)')
            axes[2].grid(True, alpha=0.3)

        plt.tight_layout()

        if output_dir:
            output_path = Path(output_dir) / 'tracking_errors.png'
            plt.savefig(output_path, dpi=150)
            print(f"  Saved: {output_path}")
        else:
            plt.show()

        plt.close()

    def plot_rate_controllers(self, output_dir=None):
        """Plot rate controller performance"""
        print("\nGenerating rate controller plots...")

        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        fig.suptitle('Rate Controller Performance', fontsize=16)

        # Roll rate
        if len(self.rate_roll_data['time']) > 0:
            axes[0].plot(self.rate_roll_data['time'], self.rate_roll_data['desired'],
                        'g--', label='Desired', linewidth=2)
            axes[0].plot(self.rate_roll_data['time'], self.rate_roll_data['actual'],
                        'b-', label='Actual', linewidth=1, alpha=0.7)
            axes[0].set_ylabel('Roll Rate (deg/s)')
            axes[0].legend(loc='upper right')
            axes[0].grid(True, alpha=0.3)

        # Pitch rate
        if len(self.rate_pitch_data['time']) > 0:
            axes[1].plot(self.rate_pitch_data['time'], self.rate_pitch_data['desired'],
                        'g--', label='Desired', linewidth=2)
            axes[1].plot(self.rate_pitch_data['time'], self.rate_pitch_data['actual'],
                        'b-', label='Actual', linewidth=1, alpha=0.7)
            axes[1].set_ylabel('Pitch Rate (deg/s)')
            axes[1].legend(loc='upper right')
            axes[1].grid(True, alpha=0.3)

        # Yaw rate
        if len(self.rate_yaw_data['time']) > 0:
            axes[2].plot(self.rate_yaw_data['time'], self.rate_yaw_data['desired'],
                        'g--', label='Desired', linewidth=2)
            axes[2].plot(self.rate_yaw_data['time'], self.rate_yaw_data['actual'],
                        'b-', label='Actual', linewidth=1, alpha=0.7)
            axes[2].set_ylabel('Yaw Rate (deg/s)')
            axes[2].set_xlabel('Time (seconds)')
            axes[2].legend(loc='upper right')
            axes[2].grid(True, alpha=0.3)

        plt.tight_layout()

        if output_dir:
            output_path = Path(output_dir) / 'rate_performance.png'
            plt.savefig(output_path, dpi=150)
            print(f"  Saved: {output_path}")
        else:
            plt.show()

        plt.close()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Analyze PID performance from ArduPilot logs')
    parser.add_argument('logfile', help='ArduPilot .BIN log file')
    parser.add_argument('--output', '-o', help='Output directory for graphs (if not specified, displays interactively)')
    parser.add_argument('--no-rate', action='store_true', help='Skip rate controller plots')

    args = parser.parse_args()

    # Check if log file exists
    if not Path(args.logfile).exists():
        print(f"Error: Log file not found: {args.logfile}")
        return 1

    # Create output directory if specified
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Output directory: {output_dir}")
    else:
        output_dir = None

    # Create analyzer
    analyzer = PIDAnalyzer(args.logfile)

    # Parse log
    if not analyzer.parse_log():
        return 1

    # Analyze performance
    analyzer.analyze_performance()

    # Generate plots
    analyzer.plot_attitude(output_dir)
    analyzer.plot_errors(output_dir)

    if not args.no_rate:
        analyzer.plot_rate_controllers(output_dir)

    print("\nAnalysis complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())


# ============================================
# USAGE EXAMPLES
# ============================================

# Basic usage (display plots):
#   python3 pid_performance_analyzer.py flight.BIN

# Save plots to directory:
#   python3 pid_performance_analyzer.py flight.BIN --output graphs/

# Skip rate controller plots:
#   python3 pid_performance_analyzer.py flight.BIN --no-rate

# ============================================
# INTERPRETING RESULTS
# ============================================

# Good PID tuning:
# - Actual closely follows desired (green dashed line)
# - Minimal oscillation
# - RMS error < 5 degrees
# - Smooth response to changes

# Over-tuned (P too high):
# - Oscillation visible
# - Actual overshoots desired
# - High frequency variations
# - Solution: Reduce RLL_RATE_P / PTCH_RATE_P

# Under-tuned (P too low):
# - Sluggish response
# - Large tracking errors
# - Actual lags behind desired
# - Solution: Increase RLL_RATE_P / PTCH_RATE_P

# I term issues:
# - Steady-state error (offset)
# - Solution: Increase RLL_RATE_I / PTCH_RATE_I

# D term issues:
# - Overshoot on quick changes
# - Solution: Increase RLL_RATE_D / PTCH_RATE_D
