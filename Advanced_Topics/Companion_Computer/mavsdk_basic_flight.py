#!/usr/bin/env python3
"""
MAVSDK Basic Flight Example
Simple autonomous flight using MAVSDK Python
Author: Patrick Kelly (@Kuscko)
Version: 1.0
Last Updated: 2026-02-03

Requirements:
    pip install mavsdk

Usage:
    python3 mavsdk_basic_flight.py
"""

import asyncio
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan


async def run():
    """Main async function to run the flight"""

    # Create drone instance
    drone = System()

    # ============================================
    # CONNECT TO VEHICLE
    # ============================================

    print("Connecting to vehicle...")

    # Connect via serial (adjust port as needed)
    # await drone.connect(system_address="serial:///dev/ttyACM0:115200")

    # Connect via UDP (for SITL or mavlink-router)
    await drone.connect(system_address="udp://:14540")

    # Wait for connection
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Connected to drone!")
            break

    # ============================================
    # GET VEHICLE INFO
    # ============================================

    print("Getting vehicle info...")
    info = await drone.info.get_identification()
    print(f"Hardware UID: {info.hardware_uid}")

    version = await drone.info.get_version()
    print(f"Firmware version: {version.flight_sw_major}.{version.flight_sw_minor}.{version.flight_sw_patch}")

    # ============================================
    # WAIT FOR GPS
    # ============================================

    print("Waiting for GPS lock...")
    async for gps_info in drone.telemetry.gps_info():
        if gps_info.fix_type >= 3 and gps_info.num_satellites >= 10:
            print(f"GPS lock acquired: {gps_info.num_satellites} satellites, fix type {gps_info.fix_type}")
            break

    # Get home position
    async for position in drone.telemetry.position():
        home_lat = position.latitude_deg
        home_lon = position.longitude_deg
        home_alt = position.absolute_altitude_m
        print(f"Home position: {home_lat:.6f}, {home_lon:.6f}, {home_alt:.1f}m")
        break

    # ============================================
    # CREATE MISSION
    # ============================================

    print("Creating mission...")

    mission_items = []

    # Takeoff to 50m
    mission_items.append(MissionItem(
        home_lat,
        home_lon,
        50,
        10,  # Speed 10 m/s
        True,  # Is fly-through
        float('nan'),  # Gimbal pitch
        float('nan'),  # Gimbal yaw
        MissionItem.CameraAction.NONE,
        float('nan'),  # Loiter time
        float('nan'),  # Camera photo interval
        float('nan'),  # Acceptance radius
        float('nan'),  # Yaw
        float('nan')   # Camera photo distance
    ))

    # Waypoint 1: North 100m
    mission_items.append(MissionItem(
        home_lat + 0.0009,  # ~100m north
        home_lon,
        50,
        10,
        True,
        float('nan'),
        float('nan'),
        MissionItem.CameraAction.NONE,
        float('nan'),
        float('nan'),
        float('nan'),
        float('nan'),
        float('nan')
    ))

    # Waypoint 2: East 100m
    mission_items.append(MissionItem(
        home_lat + 0.0009,
        home_lon + 0.0009,  # ~100m east
        50,
        10,
        True,
        float('nan'),
        float('nan'),
        MissionItem.CameraAction.NONE,
        float('nan'),
        float('nan'),
        float('nan'),
        float('nan'),
        float('nan')
    ))

    # Waypoint 3: Back to origin
    mission_items.append(MissionItem(
        home_lat,
        home_lon,
        50,
        10,
        True,
        float('nan'),
        float('nan'),
        MissionItem.CameraAction.NONE,
        float('nan'),
        float('nan'),
        float('nan'),
        float('nan'),
        float('nan')
    ))

    # Create mission plan
    mission_plan = MissionPlan(mission_items)

    # Upload mission
    print("Uploading mission...")
    await drone.mission.upload_mission(mission_plan)
    print("Mission uploaded!")

    # ============================================
    # ARM AND START MISSION
    # ============================================

    # Check if vehicle is armable
    print("Waiting for vehicle to be ready to arm...")
    async for health in drone.telemetry.health():
        if health.is_armable:
            print("Vehicle is armable")
            break

    # Arm vehicle
    print("Arming...")
    await drone.action.arm()
    print("Armed!")

    # Set mode to AUTO (mission)
    print("Starting mission...")
    await drone.mission.start_mission()
    print("Mission started!")

    # ============================================
    # MONITOR MISSION PROGRESS
    # ============================================

    print("Monitoring mission progress...")

    # Print mission progress
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: {mission_progress.current}/{mission_progress.total}")
        if mission_progress.current == mission_progress.total:
            print("Mission complete!")
            break

    # ============================================
    # RETURN AND LAND
    # ============================================

    print("Returning to launch...")
    await drone.action.return_to_launch()

    # Wait until landed
    print("Waiting for landing...")
    async for in_air in drone.telemetry.in_air():
        if not in_air:
            print("Landed!")
            break

    # Disarm
    print("Disarming...")
    await drone.action.disarm()
    print("Disarmed!")

    print("Flight complete!")


if __name__ == "__main__":
    """Entry point"""

    print("=" * 50)
    print("MAVSDK Basic Flight Example")
    print("=" * 50)
    print()

    # Run async function
    asyncio.run(run())

    print()
    print("=" * 50)
    print("Done!")
    print("=" * 50)


# ============================================
# NOTES
# ============================================

# Connection strings:
# - Serial:     serial:///dev/ttyACM0:115200
# - UDP:        udp://:14540
# - TCP:        tcp://127.0.0.1:5760
# - SITL:       udp://:14540

# Common MAVSDK operations:

# Get telemetry:
#   async for position in drone.telemetry.position():
#       print(f"Lat: {position.latitude_deg}, Lon: {position.longitude_deg}")

# Set mode:
#   await drone.action.set_mode("GUIDED")

# Takeoff:
#   await drone.action.takeoff()

# Land:
#   await drone.action.land()

# Go to location:
#   await drone.action.goto_location(lat, lon, alt_m, yaw_deg)

# Set parameters:
#   await drone.param.set_param_int("PARAM_NAME", value)
#   await drone.param.set_param_float("PARAM_NAME", value)

# Get parameters:
#   value = await drone.param.get_param_int("PARAM_NAME")
#   value = await drone.param.get_param_float("PARAM_NAME")

# Error handling:
# try:
#     await drone.action.arm()
# except Exception as e:
#     print(f"Arming failed: {e}")
