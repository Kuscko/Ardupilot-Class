-- Automatic Mode Switch
-- Switches to RTL if battery below threshold and not already in RTL
--
-- Setup:
--   Modify voltage_threshold below to match your battery type
--
-- WARNING: Test thoroughly in SITL before using on real aircraft
--
-- Author: Patrick Kelly (@Kuscko)
-- Version: 1.0

-- Configuration
local voltage_threshold = 13.5  -- Volts (adjust for your battery)
local RTL_MODE = 11  -- RTL mode number for Plane

local rtl_triggered = false

function update()
    local voltage = battery:voltage(0)

    if not voltage then
        return update, 1000
    end

    -- Get current mode
    local current_mode = vehicle:get_mode()

    -- If voltage critical and not in RTL, switch to RTL
    if voltage < voltage_threshold and current_mode ~= RTL_MODE and not rtl_triggered then
        gcs:send_text(1, string.format("Auto RTL triggered: Battery %.2fV < %.2fV", voltage, voltage_threshold))
        vehicle:set_mode(RTL_MODE)
        rtl_triggered = true
    end

    -- Reset if battery recovers (for testing)
    if voltage >= voltage_threshold + 0.5 then
        rtl_triggered = false
    end

    return update, 2000  -- Check every 2 seconds
end

return update, 2000
