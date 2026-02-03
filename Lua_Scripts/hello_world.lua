-- Hello World Script
-- Sends a message to GCS every 5 seconds
-- This is the simplest possible Lua script for ArduPilot
--
-- Author: Patrick Kelly (@Kuscko)
-- FOR: AEVEX Onboarding
-- Version: 1.0

function update()
    gcs:send_text(6, "Hello from Lua!")
    return update, 5000  -- Run every 5 seconds
end

return update, 5000
