#!/usr/bin/env python

"""
Example ArduPilot Autotest - Custom Flight Tests
Demonstrates how to write custom autotests for ArduPilot using the autotest framework

Author: Patrick Kelly (@Kuscko)
Version: 1.0
Last Updated: 2026-02-03

This file shows examples of:
1. Basic waypoint navigation tests
2. Sensor failure simulation tests
3. Geofence violation tests
4. Custom parameter validation tests
5. Scripting (Lua) integration tests

To run this test:
    cd ~/ardupilot/Tools/autotest
    ./autotest.py --vehicle=Plane --test=CustomTests
"""

from __future__ import print_function
import math
import time

from pymavlink import mavutil

# Import autotest framework
from common import AutoTest
from pysim import util


class CustomTests(AutoTest):
    """Custom test suite for ArduPilot Plane"""

    def __init__(self, *args, **kwargs):
        super(CustomTests, self).__init__(*args, **kwargs)
        self.set_current_test_name("CustomTests")

    # =========================================================================
    # EXAMPLE 1: Basic Waypoint Navigation Test
    # =========================================================================

    def test_simple_waypoint_mission(self):
        """Test basic waypoint navigation with AUTO mode"""
        self.context_push()

        # Create a simple mission
        self.progress("Creating waypoint mission")
        items = []

        # Home waypoint (required)
        items.append(self.mav.mav.mission_item_int_encode(
            self.sysid_thismav(),
            1,  # component ID
            0,  # sequence
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            1,  # current (1 for home)
            0,  # autocontinue
            0, 0, 0, 0,  # params 1-4
            int(self.home_latitude * 1e7),  # lat
            int(self.home_longitude * 1e7),  # lon
            100,  # altitude (meters)
        ))

        # Takeoff
        items.append(self.mav.mav.mission_item_int_encode(
            self.sysid_thismav(),
            1,
            1,  # sequence
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0,  # current
            1,  # autocontinue
            0, 0, 0, 0,  # params
            0, 0,  # lat/lon (use current position)
            100,  # takeoff altitude
        ))

        # Waypoint 1 - 100m North
        items.append(self.mav.mav.mission_item_int_encode(
            self.sysid_thismav(),
            1,
            2,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            0, 1,
            0, 0, 0, 0,
            int((self.home_latitude + 0.0009) * 1e7),  # ~100m north
            int(self.home_longitude * 1e7),
            100,
        ))

        # RTL
        items.append(self.mav.mav.mission_item_int_encode(
            self.sysid_thismav(),
            1,
            3,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
            0, 1,
            0, 0, 0, 0,
            0, 0, 0,
        ))

        # Upload mission
        self.upload_using_mission_protocol(mavutil.mavlink.MAV_MISSION_TYPE_MISSION, items)
        self.progress("Mission uploaded successfully")

        # Arm and takeoff
        self.change_mode('AUTO')
        self.wait_ready_to_arm()
        self.arm_vehicle()

        # Wait for takeoff
        self.wait_altitude(90, 110, relative=True, timeout=60)
        self.progress("Takeoff complete")

        # Wait for mission completion
        self.wait_mode('RTL', timeout=180)
        self.progress("Mission complete, RTL active")

        # Wait for landing
        self.wait_disarmed(timeout=120)
        self.progress("Test complete - vehicle disarmed")

        self.context_pop()

    # =========================================================================
    # EXAMPLE 2: GPS Failure Simulation Test
    # =========================================================================

    def test_gps_failure_handling(self):
        """Test vehicle behavior when GPS fails"""
        self.context_push()

        # Takeoff first
        self.takeoff(alt=100)

        # Switch to FBWA (requires GPS for nav but can fly without)
        self.change_mode('FBWA')

        # Get initial position
        m = self.mav.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=5)
        self.progress("Initial position: lat=%f lon=%f alt=%f" %
                      (m.lat / 1e7, m.lon / 1e7, m.relative_alt / 1000.0))

        # Simulate GPS failure
        self.progress("Simulating GPS failure...")
        self.set_parameter('SIM_GPS_DISABLE', 1)

        # Wait for GPS status to show no fix
        self.wait_gps_fix_type_value(0, timeout=30)  # 0 = NO_GPS
        self.progress("GPS failure detected")

        # Vehicle should continue flying (FBWA doesn't require GPS)
        # But EKF should start warning
        self.wait_statustext("EKF3 IMU. stopped aiding", timeout=30, check_context=True)
        self.progress("EKF detected GPS failure")

        # Re-enable GPS
        self.progress("Re-enabling GPS...")
        self.set_parameter('SIM_GPS_DISABLE', 0)

        # Wait for GPS fix to return
        self.wait_gps_fix_type_value(3, timeout=60)  # 3 = 3D_FIX
        self.progress("GPS fix restored")

        # Wait for EKF to recover
        time.sleep(10)

        # Switch to RTL and land
        self.change_mode('RTL')
        self.wait_disarmed()
        self.progress("Test complete")

        self.context_pop()

    # =========================================================================
    # EXAMPLE 3: Geofence Violation Test
    # =========================================================================

    def test_geofence_breach(self):
        """Test geofence violation and return behavior"""
        self.context_push()

        # Configure geofence
        self.progress("Configuring circular geofence")
        self.set_parameter('FENCE_ENABLE', 1)      # Enable fence
        self.set_parameter('FENCE_TYPE', 2)        # Circle only
        self.set_parameter('FENCE_RADIUS', 150)    # 150m radius
        self.set_parameter('FENCE_ACTION', 1)      # RTL on breach

        # Takeoff
        self.takeoff(alt=100)
        self.change_mode('FBWA')

        # Fly toward fence boundary
        self.progress("Flying toward geofence boundary...")
        self.set_rc(1, 2000)  # Roll right
        self.set_rc(2, 1500)  # Neutral pitch
        self.set_rc(3, 1700)  # Throttle up

        # Wait for fence breach
        self.wait_statustext("Geofence.*Boundary", timeout=60, check_context=True, regex=True)
        self.progress("Geofence breach detected")

        # Should automatically switch to RTL
        self.wait_mode('RTL', timeout=10)
        self.progress("Vehicle entered RTL due to geofence breach")

        # Reset RC
        self.set_rc_default()

        # Wait for return and landing
        self.wait_disarmed(timeout=120)
        self.progress("Test complete")

        # Disable fence for other tests
        self.set_parameter('FENCE_ENABLE', 0)

        self.context_pop()

    # =========================================================================
    # EXAMPLE 4: Parameter Validation Test
    # =========================================================================

    def test_parameter_bounds(self):
        """Test that critical parameters enforce valid ranges"""
        self.context_push()

        # Test 1: Altitude limits
        self.progress("Testing altitude limit parameters")

        # ALT_HOLD_RTL should be positive
        try:
            self.set_parameter('ALT_HOLD_RTL', -100)
            raise NotAchievedException("ALT_HOLD_RTL accepted negative value!")
        except ValueError:
            self.progress("ALT_HOLD_RTL correctly rejects negative value")

        # Test 2: Roll limit
        self.progress("Testing roll limit parameters")

        # RLL_LIM_MAX should be 0-90 degrees
        self.set_parameter('RLL_LIM_MAX', 45)  # Valid
        self.progress("RLL_LIM_MAX accepts valid value (45)")

        try:
            self.set_parameter('RLL_LIM_MAX', 100)  # Invalid (>90)
            # Should either reject or clamp to 90
            value = self.get_parameter('RLL_LIM_MAX')
            if value > 90:
                raise NotAchievedException("RLL_LIM_MAX accepted invalid value >90!")
            self.progress("RLL_LIM_MAX clamped to %f" % value)
        except ValueError:
            self.progress("RLL_LIM_MAX correctly rejects value >90")

        # Test 3: Baud rate validation
        self.progress("Testing serial baud rate parameter")

        valid_bauds = [1, 2, 4, 9, 19, 38, 57, 111, 115, 230, 256, 460, 500, 921, 1500, 2000]
        self.set_parameter('SERIAL1_BAUD', 57)  # Valid (57600)
        self.progress("SERIAL1_BAUD accepts valid value")

        self.context_pop()

    # =========================================================================
    # EXAMPLE 5: Lua Scripting Test
    # =========================================================================

    def test_lua_script_execution(self):
        """Test that Lua scripting is working"""
        self.context_push()

        # Enable scripting
        self.progress("Enabling Lua scripting")
        self.set_parameter('SCR_ENABLE', 1)
        self.reboot_sitl()

        # Wait for boot
        self.wait_ready_to_arm()

        # Check for scripting heap allocation
        heap = self.get_parameter('SCR_HEAP_SIZE', timeout=5)
        if heap == 0:
            raise NotAchievedException("Scripting enabled but no heap allocated")
        self.progress("Scripting heap: %d bytes" % (heap * 1024))

        # Look for script loaded message
        # Note: This requires a test script to be present in scripts/ directory
        # For this example, we just verify scripting is enabled
        self.progress("Scripting enabled and initialized")

        # Disable scripting to clean up
        self.set_parameter('SCR_ENABLE', 0)

        self.context_pop()

    # =========================================================================
    # EXAMPLE 6: Failsafe Testing
    # =========================================================================

    def test_throttle_failsafe(self):
        """Test throttle failsafe triggers RTL"""
        self.context_push()

        # Configure throttle failsafe
        self.progress("Configuring throttle failsafe")
        self.set_parameter('THR_FS_VALUE', 950)    # Failsafe threshold
        self.set_parameter('FS_SHORT_ACTN', 0)     # Short failsafe: Continue
        self.set_parameter('FS_LONG_ACTN', 1)      # Long failsafe: RTL
        self.set_parameter('FS_LONG_TIMEOUT', 5)   # 5 seconds

        # Takeoff and fly
        self.takeoff(alt=100)
        self.change_mode('FBWA')

        # Simulate throttle failsafe by setting RC3 below threshold
        self.progress("Triggering throttle failsafe...")
        self.set_rc(3, 900)  # Below THR_FS_VALUE

        # Wait for failsafe message
        self.wait_statustext("Throttle failsafe", timeout=10, check_context=True)
        self.progress("Throttle failsafe detected")

        # Wait for long failsafe timeout
        time.sleep(6)

        # Should switch to RTL
        self.wait_mode('RTL', timeout=10)
        self.progress("Long failsafe triggered RTL")

        # Restore throttle
        self.set_rc(3, 1500)

        # Wait for landing
        self.wait_disarmed(timeout=120)
        self.progress("Test complete")

        self.context_pop()

    # =========================================================================
    # EXAMPLE 7: DO_JUMP Command Test
    # =========================================================================

    def test_mission_do_jump(self):
        """Test DO_JUMP command in mission"""
        self.context_push()

        # Create mission with DO_JUMP
        items = []

        # Home
        items.append(self.mav.mav.mission_item_int_encode(
            self.sysid_thismav(), 1, 0,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            1, 0, 0, 0, 0, 0,
            int(self.home_latitude * 1e7),
            int(self.home_longitude * 1e7),
            100,
        ))

        # Takeoff
        items.append(self.mav.mav.mission_item_int_encode(
            self.sysid_thismav(), 1, 1,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0, 1, 0, 0, 0, 0, 0, 0, 100,
        ))

        # Waypoint (target of jump)
        items.append(self.mav.mav.mission_item_int_encode(
            self.sysid_thismav(), 1, 2,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            0, 1, 0, 0, 0, 0,
            int((self.home_latitude + 0.0005) * 1e7),
            int(self.home_longitude * 1e7),
            100,
        ))

        # DO_JUMP - jump to waypoint 2, repeat 2 times
        items.append(self.mav.mav.mission_item_int_encode(
            self.sysid_thismav(), 1, 3,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_DO_JUMP,
            0, 1,
            2,  # target waypoint
            2,  # repeat count
            0, 0, 0, 0, 0,
        ))

        # RTL
        items.append(self.mav.mav.mission_item_int_encode(
            self.sysid_thismav(), 1, 4,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
            0, 1, 0, 0, 0, 0, 0, 0, 0,
        ))

        # Upload and run mission
        self.upload_using_mission_protocol(mavutil.mavlink.MAV_MISSION_TYPE_MISSION, items)

        self.change_mode('AUTO')
        self.wait_ready_to_arm()
        self.arm_vehicle()

        # Monitor mission item changes - should see waypoint 2 repeated
        seen_wp2 = 0
        start_time = time.time()
        timeout = 120

        while time.time() - start_time < timeout:
            m = self.mav.recv_match(type='MISSION_CURRENT', blocking=True, timeout=1)
            if m and m.seq == 2:
                seen_wp2 += 1
                self.progress("At waypoint 2, count: %d" % seen_wp2)

            # Should see WP2 three times (initial + 2 jumps)
            if seen_wp2 >= 3:
                self.progress("DO_JUMP executed correctly")
                break

            # Check if RTL started
            if self.mode_is('RTL'):
                break

        if seen_wp2 < 3:
            raise NotAchievedException("DO_JUMP did not repeat correctly (seen %d times)" % seen_wp2)

        # Wait for landing
        self.wait_mode('RTL', timeout=60)
        self.wait_disarmed(timeout=120)

        self.context_pop()

    # =========================================================================
    # Test Suite Definition
    # =========================================================================

    def tests(self):
        """Return list of all tests"""
        return [
            self.test_simple_waypoint_mission,
            self.test_gps_failure_handling,
            self.test_geofence_breach,
            self.test_parameter_bounds,
            self.test_lua_script_execution,
            self.test_throttle_failsafe,
            self.test_mission_do_jump,
        ]


# ============================================================================
# USAGE INSTRUCTIONS
# ============================================================================

# To run these tests:
#
# 1. Copy this file to ArduPilot autotest directory:
#    cp example_autotest_custom.py ~/ardupilot/Tools/autotest/
#
# 2. Run all tests:
#    cd ~/ardupilot/Tools/autotest
#    ./autotest.py --vehicle=Plane --test=CustomTests
#
# 3. Run specific test:
#    ./autotest.py --vehicle=Plane --test=CustomTests.test_simple_waypoint_mission
#
# 4. Run in debug mode:
#    ./autotest.py --vehicle=Plane --test=CustomTests --debug
#
# 5. Keep SITL running after test:
#    ./autotest.py --vehicle=Plane --test=CustomTests --no-rebuild --no-clean

# ============================================================================
# WRITING YOUR OWN TESTS
# ============================================================================

# Test Structure:
# - All test methods must start with "test_"
# - Use self.progress() for logging
# - Use self.context_push/pop() for setup/teardown
# - Raise NotAchievedException() on failure
# - Use existing helper methods from AutoTest class

# Common Helper Methods:
# - self.takeoff(alt)                    - Automated takeoff
# - self.change_mode(mode)               - Change flight mode
# - self.wait_altitude(min, max)         - Wait for altitude
# - self.wait_mode(mode)                 - Wait for mode change
# - self.wait_disarmed()                 - Wait for disarm
# - self.arm_vehicle()                   - Arm the vehicle
# - self.set_rc(channel, pwm)            - Set RC channel
# - self.set_parameter(name, value)      - Set parameter
# - self.get_parameter(name)             - Get parameter
# - self.wait_statustext(text)           - Wait for status message
# - self.reboot_sitl()                   - Reboot SITL

# Example Test Template:
"""
def test_my_feature(self):
    '''Test description here'''
    self.context_push()

    # Setup
    self.set_parameter('PARAM1', 10)

    # Execute
    self.takeoff(alt=100)
    # ... test code ...

    # Verify
    if not some_condition:
        raise NotAchievedException("Test failed because...")

    # Cleanup
    self.wait_disarmed()
    self.context_pop()
"""
