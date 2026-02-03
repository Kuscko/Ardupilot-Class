-- Servo Sweep
-- Sweeps servo 9 back and forth between min and max PWM
-- Useful for testing servos or payload deployment mechanisms
--
-- WARNING: Ensure servo 9 is not assigned to critical flight controls!
--
-- Author: Patrick Kelly (@Kuscko)
-- Version: 1.0

-- Configuration
local servo_num = 9        -- Servo channel (9-16 are typically aux channels)
local min_pwm = 1000       -- Minimum PWM value
local max_pwm = 2000       -- Maximum PWM value
local step = 10            -- PWM increment per update
local update_interval = 50 -- Update every 50ms

-- State variables
local current_pwm = min_pwm
local direction = 1  -- 1 = increasing, -1 = decreasing

function update()
    -- Set servo position
    SRV_Channels:set_output_pwm_chan_timeout(servo_num, current_pwm, 100)

    -- Update position
    current_pwm = current_pwm + (step * direction)

    -- Reverse direction at limits
    if current_pwm >= max_pwm then
        direction = -1
        gcs:send_text(6, string.format("Servo %d: reached max (%d)", servo_num, max_pwm))
    elseif current_pwm <= min_pwm then
        direction = 1
        gcs:send_text(6, string.format("Servo %d: reached min (%d)", servo_num, min_pwm))
    end

    return update, update_interval
end

-- Initial message
gcs:send_text(6, string.format("Servo sweep started on channel %d", servo_num))

return update, update_interval
