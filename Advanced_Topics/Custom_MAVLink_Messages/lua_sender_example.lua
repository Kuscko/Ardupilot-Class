-- Custom MAVLink Message Sender (Lua)
-- Sends custom MAVLink messages from ArduPilot using Lua scripting
-- Author: Patrick Kelly (@Kuscko)
-- Version: 1.0
-- Last Updated: 2026-02-03

-- Configuration
local MSG_ID_CUSTOM_SENSOR = 12000
local MSG_ID_CUSTOM_STATUS = 12001
local SEND_RATE_MS = 1000  -- Send every 1000ms (1 Hz)

-- Simulated sensor values (replace with real sensor reads)
local sensor1_value = 0.0
local sensor2_value = 0.0
local sensor3_value = 0.0

-- Initialize
function init()
    gcs:send_text(6, "Custom MAVLink: Started")
    return send_custom_messages, SEND_RATE_MS
end

-- Main function to send custom messages
function send_custom_messages()
    -- Update simulated sensor values
    update_sensors()

    -- Send CUSTOM_SENSOR_DATA message (ID 12000)
    send_sensor_data()

    -- Send CUSTOM_STATUS message (ID 12001)
    send_status()

    return send_custom_messages, SEND_RATE_MS
end

-- Update sensor values (simulated)
function update_sensors()
    -- Simulate sensor readings (replace with actual sensor API calls)
    sensor1_value = ahrs:get_temperature()  -- Get IMU temperature
    sensor2_value = baro:get_pressure()     -- Get barometric pressure
    sensor3_value = ahrs:get_gyro():length() -- Get gyro magnitude

    -- Or use custom I2C/SPI sensors via Lua
end

-- Send CUSTOM_SENSOR_DATA message
function send_sensor_data()
    -- Message fields: timestamp, sensor1, sensor2, sensor3, status
    local timestamp = millis()
    local sensor_status = 0  -- 0 = OK

    -- Check sensor health
    if not ahrs:healthy() then
        sensor_status = 1  -- Error
    end

    -- Pack and send message
    -- Note: ArduPilot Lua MAVLink API may vary by version
    -- This is conceptual - check your version's API

    -- Method 1: Using mavlink:send_chan (if available)
    -- mavlink:send_chan(
    --     0,                    -- Channel (0 = all channels)
    --     MSG_ID_CUSTOM_SENSOR, -- Message ID
    --     timestamp,            -- Field 1: timestamp_ms
    --     sensor1_value,        -- Field 2: sensor1_value
    --     sensor2_value,        -- Field 3: sensor2_value
    --     sensor3_value,        -- Field 4: sensor3_value
    --     sensor_status         -- Field 5: sensor_status
    -- )

    -- Method 2: Using named message sending (ArduPilot 4.4+)
    -- Create message table
    local msg = {}
    msg.timestamp_ms = timestamp
    msg.sensor1_value = sensor1_value
    msg.sensor2_value = sensor2_value
    msg.sensor3_value = sensor3_value
    msg.sensor_status = sensor_status

    -- Send via GCS (this is a simplified example)
    -- Actual implementation depends on ArduPilot Lua bindings version
    -- gcs:send_named_float("SENSOR1", sensor1_value)
    -- gcs:send_named_float("SENSOR2", sensor2_value)
    -- gcs:send_named_float("SENSOR3", sensor3_value)

    -- For debugging, send as text
    local debug_msg = string.format("Sensors: %.2f, %.2f, %.2f",
                                    sensor1_value, sensor2_value, sensor3_value)
    gcs:send_text(7, debug_msg)  -- Severity 7 = DEBUG
end

-- Send CUSTOM_STATUS message
function send_status()
    local timestamp = millis()

    -- Get flight mode
    local mode = vehicle:get_mode()

    -- Get battery percentage
    local battery = battery:healthy(0) and battery:capacity_remaining_pct(0) or 0

    -- Calculate mission progress
    local mission_progress = 0
    if mission:state() == mission.MISSION_RUNNING then
        local current_wp = mission:get_current_nav_index()
        local total_wp = mission:num_commands()
        if total_wp > 0 then
            mission_progress = (current_wp / total_wp) * 100
        end
    end

    -- Health flags
    local health_flags = 0
    if ahrs:healthy() then
        health_flags = health_flags | (1 << 0)  -- Bit 0: AHRS healthy
    end
    if gps:status(0) >= gps.GPS_OK_FIX_3D then
        health_flags = health_flags | (1 << 1)  -- Bit 1: GPS healthy
    end
    if battery:healthy(0) then
        health_flags = health_flags | (1 << 2)  -- Bit 2: Battery healthy
    end

    -- Send status message
    -- (Actual MAVLink send code here - see send_sensor_data comments)

    -- Debug output
    local status_msg = string.format("Status: Mode=%d Battery=%.0f%% Mission=%.0f%%",
                                     mode, battery, mission_progress)
    gcs:send_text(7, status_msg)
end

-- Start script
return init()

-- ============================================
-- USAGE INSTRUCTIONS
-- ============================================
--
-- 1. Copy to SD card: APM/scripts/lua_sender_example.lua
--
-- 2. Enable scripting:
--    param set SCR_ENABLE 1
--    param set SCR_HEAP_SIZE 65536
--    param save
--    reboot
--
-- 3. Monitor GCS messages to see debug output
--
-- 4. Receive messages using python_receiver_example.py
--
-- 5. Verify messages in Mission Planner:
--    - CTRL+F → MAVLink Inspector
--    - Look for message ID 12000, 12001
--
-- ============================================
-- IMPORTANT NOTES
-- ============================================
--
-- ArduPilot Lua MAVLink Support:
-- - MAVLink message sending from Lua requires ArduPilot 4.3+
-- - Not all message types fully supported in all versions
-- - Check ArduPilot Lua docs for your version:
--   https://ardupilot.org/plane/docs/common-lua-scripts.html
--
-- Alternative Approaches:
-- 1. Use named value floats (limited to float values):
--    gcs:send_named_float("MYSENSOR", value)
--
-- 2. Use STATUS_TEXT messages (for debugging):
--    gcs:send_text(severity, "message")
--
-- 3. Modify ArduPilot C++ code for full custom messages:
--    - Add message to libraries/GCS_MAVLink/
--    - Implement send function
--    - Recompile firmware
--
-- ============================================
-- TROUBLESHOOTING
-- ============================================
--
-- Script not running:
-- - Check SCR_ENABLE = 1
-- - Verify script on SD card
-- - Check SCR_HEAP_SIZE adequate
-- - Look for errors in GCS messages
--
-- Messages not received:
-- - Verify message ID doesn't conflict
-- - Check MAVLink protocol version
-- - Ensure ground station configured for custom messages
-- - Use MAVLink Inspector to debug
--
-- High CPU load:
-- - Reduce SEND_RATE_MS (send less frequently)
-- - Optimize sensor read functions
-- - Reduce number of messages sent
--
-- ============================================
-- CUSTOMIZATION
-- ============================================
--
-- To send your own sensor data:
-- 1. Replace update_sensors() with your sensor reads
-- 2. Adjust message fields in send_sensor_data()
-- 3. Change MSG_ID to match your XML definition
-- 4. Modify SEND_RATE_MS for desired update rate
--
-- To add more messages:
-- 1. Define new MSG_ID constant
-- 2. Create new send_xxx() function
-- 3. Call from send_custom_messages()
--
-- ============================================
-- RESOURCES
-- ============================================
--
-- ArduPilot Lua Scripting:
-- https://ardupilot.org/plane/docs/common-lua-scripts.html
--
-- Lua Scripting API Reference:
-- https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_Scripting/docs/docs.lua
--
-- MAVLink Documentation:
-- https://mavlink.io/en/
