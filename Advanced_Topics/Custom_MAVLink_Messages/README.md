# Custom MAVLink Messages

## Overview

Learn to define, implement, and use custom MAVLink messages in ArduPilot for specialized telemetry, commands, or data exchange between flight controller, companion computer, and ground station [1].

MAVLink is the lightweight messaging protocol used by ArduPilot for communication. Custom messages allow you to extend the protocol for application-specific needs without modifying core MAVLink definitions.

## Prerequisites

Before starting this module, you should have:

- Understanding of MAVLink protocol basics
- ArduPilot build environment configured
- Experience with C++ and Python programming
- Familiarity with XML syntax
- Companion computer or GCS application to test messages

## What You'll Learn

By completing this module, you will:

- Understand MAVLink message structure and XML definitions
- Create custom message definitions
- Generate MAVLink libraries from XML
- Send custom messages from ArduPilot (C++ or Lua)
- Receive and parse custom messages in Python/DroneKit
- Integrate custom messages into ArduPilot codebase
- Test custom messages in SITL

## Key Concepts

### MAVLink Message Structure

MAVLink messages consist of [1]:

- **Message ID** - Unique identifier (0-255 for MAVLink 1, 0-16777215 for MAVLink 2)
- **Fields** - Data payload (integers, floats, arrays, strings)
- **CRC Extra** - Message integrity check
- **Target System/Component** - Addressing (optional)

### Message Definition XML

Messages are defined in XML format:

```xml
<message id="12345" name="CUSTOM_SENSOR_DATA">
  <description>Custom sensor telemetry</description>
  <field type="uint64_t" name="time_usec" units="us">Timestamp</field>
  <field type="float" name="temperature" units="degC">Temperature</field>
  <field type="float" name="pressure" units="Pa">Pressure</field>
  <field type="uint8_t" name="sensor_id">Sensor ID</field>
</message>
```

### Message ID Ranges

Use appropriate ID ranges [2]:

- **0-255** - Standard MAVLink messages (reserved)
- **256-65535** - Development/testing messages
- **12000-12999** - Recommended for custom messages
- **Over 16777215** - MAVLink 2 only

## Hands-On Practice

### Exercise 1: Create Custom Message Definition

Create XML definition for custom telemetry:

```bash
cd ~/ardupilot
mkdir -p custom_mavlink

# Create message definition file
cat > custom_mavlink/custom_messages.xml << 'EOF'
<?xml version="1.0"?>
<mavlink>
  <include>common.xml</include>
  <version>3</version>
  <dialect>0</dialect>

  <messages>
    <message id="12345" name="CUSTOM_SENSOR_DATA">
      <description>Custom sensor telemetry data</description>
      <field type="uint64_t" name="time_usec" units="us">Timestamp (UNIX Epoch time or time since system boot)</field>
      <field type="float" name="temperature" units="degC">Temperature reading</field>
      <field type="float" name="pressure" units="Pa">Pressure reading</field>
      <field type="float" name="humidity" units="%">Relative humidity</field>
      <field type="uint8_t" name="sensor_id">Sensor identifier</field>
      <field type="uint8_t" name="sensor_status">Sensor status flags</field>
    </message>

    <message id="12346" name="CUSTOM_COMMAND">
      <description>Custom command to device</description>
      <field type="uint8_t" name="target_system">System ID</field>
      <field type="uint8_t" name="target_component">Component ID</field>
      <field type="uint8_t" name="command">Command ID</field>
      <field type="float" name="param1">Parameter 1</field>
      <field type="float" name="param2">Parameter 2</field>
    </message>
  </messages>
</mavlink>
EOF
```

### Exercise 2: Generate MAVLink Libraries

Generate C and Python libraries from XML:

```bash
# Install MAVLink generator
pip3 install pymavlink

# Generate C headers for ArduPilot
python3 -m pymavlink.tools.mavgen \
    --lang=C \
    --wire-protocol=2.0 \
    --output=custom_mavlink/generated \
    custom_mavlink/custom_messages.xml

# Generate Python library
python3 -m pymavlink.tools.mavgen \
    --lang=Python \
    --wire-protocol=2.0 \
    --output=custom_mavlink/generated_python \
    custom_mavlink/custom_messages.xml
```

**Expected Output:**
- `custom_mavlink/generated/` - C header files
- `custom_mavlink/generated_python/` - Python module

### Exercise 3: Send Custom Message from Lua Script

Create Lua script to send custom message:

```lua
-- send_custom_sensor.lua
local MAV_SEVERITY_INFO = 6
local CUSTOM_SENSOR_DATA_MSGID = 12345

function update()
    -- Get current time
    local time_usec = micros():tofloat()

    -- Simulate sensor readings
    local temperature = 25.5
    local pressure = 101325.0
    local humidity = 60.0
    local sensor_id = 1
    local sensor_status = 0

    -- Send custom message
    -- Note: This requires custom MAVLink integration
    gcs:send_text(MAV_SEVERITY_INFO, string.format(
        "Custom Sensor: T=%.1fC P=%.0fPa H=%.0f%%",
        temperature, pressure, humidity
    ))

    return update, 1000  -- Run every 1000ms
end

return update()
```

**Note:** Full custom message sending requires C++ integration. Lua can use `gcs:send_text()` for simple telemetry.

### Exercise 4: Receive Custom Message in Python

Create Python script to receive custom messages:

```python
# receive_custom_message.py
from pymavlink import mavutil
import sys

# Add generated MAVLink library to path
sys.path.insert(0, 'custom_mavlink/generated_python')
from pymavlink.dialects.v20 import custom_messages as mavlink

# Connect to vehicle
connection = mavutil.mavlink_connection('udp:127.0.0.1:14550')
print("Waiting for heartbeat...")
connection.wait_heartbeat()
print(f"Connected to system {connection.target_system}, component {connection.target_component}")

# Listen for custom messages
print("Listening for CUSTOM_SENSOR_DATA messages...")
while True:
    msg = connection.recv_match(type='CUSTOM_SENSOR_DATA', blocking=True, timeout=5)
    if msg:
        print(f"Received custom sensor data:")
        print(f"  Timestamp: {msg.time_usec}")
        print(f"  Temperature: {msg.temperature}°C")
        print(f"  Pressure: {msg.pressure} Pa")
        print(f"  Humidity: {msg.humidity}%")
        print(f"  Sensor ID: {msg.sensor_id}")
        print(f"  Status: {msg.sensor_status}")
        print()
```

### Exercise 5: Integrate Custom Message in ArduPilot

For full integration, modify ArduPilot source:

**1. Copy generated headers:**
```bash
# Copy to ArduPilot MAVLink directory
cp custom_mavlink/generated/*.h \
   ardupilot/modules/mavlink/message_definitions/v1.0/
```

**2. Create custom library:**
```cpp
// libraries/AP_CustomSensor/AP_CustomSensor.cpp
#include "AP_CustomSensor.h"
#include <GCS_MAVLink/GCS.h>

void AP_CustomSensor::send_mavlink_data() {
    mavlink_msg_custom_sensor_data_send(
        chan,
        AP_HAL::micros64(),
        get_temperature(),
        get_pressure(),
        get_humidity(),
        sensor_id,
        get_status()
    );
}
```

**3. Rebuild ArduPilot:**
```bash
./waf configure --board sitl
./waf plane
```

## Testing Custom Messages

### Test in SITL

```bash
# Terminal 1: Start SITL
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --map

# Terminal 2: Run receiver script
cd ~/ardupilot
python3 receive_custom_message.py

# Terminal 3: Trigger message sending (via MAVProxy)
mavproxy.py --master=udp:127.0.0.1:14550
# Use commands to trigger custom message sending
```

### Verify Message Receipt

Check that:
- Messages appear in GCS (Mission Planner, QGroundControl)
- Python receiver correctly parses data
- Message rate is appropriate (not flooding)
- Data values are valid

## Common Issues

### Issue: Message ID Conflict

**Symptoms:** Messages not received or incorrect parsing

**Cause:** ID conflicts with existing messages

**Solution:**
- Use ID range 12000-12999 for custom messages
- Check existing definitions: `grep -r "message id" modules/mavlink/`
- Verify MAVLink version compatibility

### Issue: Generated Code Not Found

**Symptoms:** `ImportError` or compile errors

**Cause:** Generated files not in correct location

**Solution:**
```bash
# Verify generated files exist
ls custom_mavlink/generated/
ls custom_mavlink/generated_python/

# Add to Python path
export PYTHONPATH=$PYTHONPATH:~/ardupilot/custom_mavlink/generated_python

# Or install as package
cd custom_mavlink/generated_python
pip3 install -e .
```

### Issue: Message Not Appearing in GCS

**Symptoms:** Python receives message but GCS doesn't show it

**Cause:** GCS doesn't have custom message definition

**Solution:**
- Copy XML to GCS definition folder
- Mission Planner: `C:\Program Files (x86)\Mission Planner\MAVLink\`
- QGroundControl: Requires custom build with definitions
- Use MAVLink Inspector in GCS to view raw messages

## Message Design Best Practices

### Keep Messages Small

- Minimize field count and sizes
- Use appropriate data types (uint8_t vs uint32_t)
- Consider bandwidth constraints

### Use Appropriate Update Rates

- **High-frequency (10-50Hz):** Attitude, position
- **Medium-frequency (1-10Hz):** Sensor data, status
- **Low-frequency (0.1-1Hz):** Configuration, diagnostics

### Include Timestamps

Always include `time_usec` field for data correlation and analysis.

### Version Your Messages

Add version field for future compatibility:
```xml
<field type="uint8_t" name="msg_version">Message version</field>
```

## Additional Resources

- [MAVLink Developer Guide](https://mavlink.io/en/guide/define_xml_element.html) [1] - Message XML format
- [MAVLink Message IDs](https://mavlink.io/en/messages/common.html) [2] - Reserved ID ranges
- [PyMAVLink Documentation](https://mavlink.io/en/mavgen_python/) [3] - Python generation
- [ArduPilot MAVLink](https://ardupilot.org/dev/docs/mavlink-basics.html) [4] - ArduPilot implementation
- [Custom Dialect](https://mavlink.io/en/guide/define_xml_element.html#dialect-file-structure) [5] - Creating dialects

## Next Steps

After mastering custom MAVLink messages:

1. **Companion Computer Integration** - Use custom messages with companion computers
2. **Payload Integration** - Control custom payloads via MAVLink
3. **Telemetry Optimization** - Optimize message rates and bandwidth
4. **GCS Development** - Build custom ground station features

---

**Sources:**

[1] https://mavlink.io/en/guide/define_xml_element.html
[2] https://mavlink.io/en/messages/common.html
[3] https://mavlink.io/en/mavgen_python/
[4] https://ardupilot.org/dev/docs/mavlink-basics.html
[5] https://mavlink.io/en/guide/xml_schema.html
