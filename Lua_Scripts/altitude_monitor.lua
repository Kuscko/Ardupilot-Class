-- Altitude Monitor
-- Warns when altitude exceeds SCR_USER1 parameter
--
-- Setup:
--   param set SCR_USER1 120  (warn above 120 meters)
--
-- Author: Patrick Kelly (@Kuscko)
-- Version: 1.0

function update()
    -- Get current location
    local location = ahrs:get_location()

    if not location then
        -- No position fix yet
        return update, 1000
    end

    -- Get altitude in meters (relative to home)
    local altitude = location:alt() * 0.01  -- Convert cm to m

    -- Get warning threshold from SCR_USER1
    local threshold = param:get('SCR_USER1')

    if threshold and threshold > 0 and altitude > threshold then
        gcs:send_text(4, string.format("WARNING: Altitude %.1fm exceeds %.1fm!", altitude, threshold))
    end

    return update, 1000  -- Check every second
end

return update, 1000
