-- Waypoint Logger
-- Logs when waypoints are reached during AUTO mission
-- Displays waypoint number and coordinates
--
-- Author: Patrick Kelly (@Kuscko)
-- Version: 1.0

local last_waypoint = -1

function update()
    -- Only log in AUTO mode
    local mode = vehicle:get_mode()
    local AUTO_MODE = 10  -- AUTO mode for Plane

    if mode ~= AUTO_MODE then
        -- Not in AUTO mode, just check less frequently
        return update, 2000
    end

    -- Get current waypoint number in AUTO mode
    local current_wp = mission:get_current_nav_index()

    if current_wp and current_wp ~= last_waypoint then
        local location = ahrs:get_location()

        if location then
            local lat = location:lat() * 1e-7  -- Convert to degrees
            local lon = location:lng() * 1e-7  -- Convert to degrees
            local alt = location:alt() * 0.01  -- Convert to meters

            gcs:send_text(6, string.format("Waypoint %d reached: %.6f, %.6f, alt %.1fm",
                current_wp, lat, lon, alt))
        end

        last_waypoint = current_wp
    end

    return update, 500  -- Check twice per second during AUTO
end

return update, 500
