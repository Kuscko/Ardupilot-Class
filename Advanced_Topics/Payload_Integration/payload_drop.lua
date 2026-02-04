-- Payload Drop Control Script
-- Controls servo-based payload release mechanism
-- Author: Patrick Kelly (@Kuscko)
-- Version: 1.0
-- Last Updated: 2026-02-03

-- Configuration
local SERVO_CHANNEL = 9           -- Servo channel for payload release
local RELEASE_PWM = 1900          -- PWM value to release payload
local HOLD_PWM = 1100             -- PWM value to hold payload
local RELEASE_DURATION_MS = 2000  -- How long to hold release position (ms)
local RC_TRIGGER_CHANNEL = 7      -- RC channel to trigger release (RC7)
local RC_TRIGGER_THRESHOLD = 1700 -- PWM threshold to trigger

-- State tracking
local payload_released = false
local release_start_time = 0

-- Initialize
function init()
    -- Set servo to hold position
    SRV_Channels:set_output_pwm_chan_timeout(SERVO_CHANNEL, HOLD_PWM, 0)
    gcs:send_text(6, "Payload: Ready")
    return update, 100  -- Call update() every 100ms
end

-- Main update function
function update()
    -- Check if already released
    if payload_released then
        -- Check if release duration has elapsed
        local now = millis()
        if now - release_start_time > RELEASE_DURATION_MS then
            -- Return servo to hold position
            SRV_Channels:set_output_pwm_chan_timeout(SERVO_CHANNEL, HOLD_PWM, 0)
            gcs:send_text(6, "Payload: Servo reset")
            -- Stop script (payload already dropped)
            return
        end
        return update, 100
    end

    -- Check RC trigger
    local rc_in = rc:get_pwm(RC_TRIGGER_CHANNEL)
    if rc_in and rc_in > RC_TRIGGER_THRESHOLD then
        -- Trigger release
        release_payload()
    end

    return update, 100
end

-- Release payload function
function release_payload()
    -- Set servo to release position
    SRV_Channels:set_output_pwm_chan_timeout(SERVO_CHANNEL, RELEASE_PWM, 0)

    -- Mark as released
    payload_released = true
    release_start_time = millis()

    -- Log event
    gcs:send_text(6, "Payload: RELEASED!")

    -- Get current position for logging
    local pos = ahrs:get_position()
    if pos then
        local lat = pos:lat()
        local lon = pos:lng()
        local alt = pos:alt() * 0.01  -- Convert cm to meters
        gcs:send_text(6, string.format("Drop location: %.6f, %.6f, %.1fm", lat, lon, alt))
    end
end

-- Start script
return init()

-- ============================================
-- USAGE INSTRUCTIONS
-- ============================================
--
-- 1. Copy this script to SD card: APM/scripts/payload_drop.lua
--
-- 2. Enable scripting:
--    param set SCR_ENABLE 1
--    param set SCR_HEAP_SIZE 65536
--    param save
--    reboot
--
-- 3. Configure servo:
--    param set SERVO9_FUNCTION 0  -- Manual control
--
-- 4. Configure RC trigger:
--    - Use RC7 switch (or other channel)
--    - High position (>1700 PWM) triggers release
--
-- 5. Testing:
--    - Ground test servo movement first
--    - Verify HOLD_PWM holds payload
--    - Verify RELEASE_PWM releases payload
--    - Adjust PWM values if needed
--
-- 6. Safety:
--    - Test on ground extensively
--    - Use safety pin until ready to drop
--    - Confirm drop zone is clear
--    - Check regulations for payload drops
--
-- ============================================
-- CUSTOMIZATION
-- ============================================
--
-- Adjust these values for your mechanism:
-- SERVO_CHANNEL: Which servo controls release
-- RELEASE_PWM: PWM to release (1900 = full extension)
-- HOLD_PWM: PWM to hold (1100 = full retraction)
-- RELEASE_DURATION_MS: How long servo stays in release position
-- RC_TRIGGER_CHANNEL: Which RC channel triggers drop
-- RC_TRIGGER_THRESHOLD: PWM value to trigger (>1700 = high position)
--
-- Alternative triggers:
-- - GCS command
-- - Waypoint-based (mission command)
-- - Altitude-based
-- - Time-based
--
-- ============================================
-- TROUBLESHOOTING
-- ============================================
--
-- Payload won't release:
-- - Check SERVO_CHANNEL is correct
-- - Verify RELEASE_PWM value (may need 2000)
-- - Check servo is powered
-- - Verify scripting is enabled
--
-- Accidental release:
-- - Check RC_TRIGGER_THRESHOLD (may be too low)
-- - Verify RC switch position
-- - Add safety switch requirement
--
-- Script not running:
-- - Check SCR_ENABLE = 1
-- - Verify script on SD card
-- - Check GCS messages for errors
-- - Increase SCR_HEAP_SIZE if out of memory
