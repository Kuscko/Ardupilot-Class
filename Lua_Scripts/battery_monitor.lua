-- Battery Monitor
-- Sends warnings at different voltage levels
-- Designed for 4S LiPo batteries (14.8V nominal)
--
-- Voltage levels:
--   Critical: < 13.2V (3.3V per cell)
--   Low: < 14.0V (3.5V per cell)
--
-- Author: Patrick Kelly (@Kuscko)
-- Version: 1.0

local warned_low = false
local warned_critical = false

function update()
    -- Get battery voltage from battery 0
    local voltage = battery:voltage(0)

    if not voltage then
        return update, 1000
    end

    -- Critical battery: < 13.2V for 4S LiPo
    if voltage < 13.2 and not warned_critical then
        gcs:send_text(1, string.format("CRITICAL BATTERY: %.2fV - LAND IMMEDIATELY", voltage))
        warned_critical = true
    end

    -- Low battery: < 14.0V for 4S LiPo
    if voltage < 14.0 and not warned_low then
        gcs:send_text(4, string.format("Low battery warning: %.2fV", voltage))
        warned_low = true
    end

    -- Reset warnings if voltage recovers (useful for SITL testing)
    if voltage >= 14.2 then
        warned_low = false
        warned_critical = false
    end

    return update, 2000  -- Check every 2 seconds
end

return update, 2000
