# Custom MAVLink Messages

Custom MAVLink messages extend the protocol for application-specific telemetry, commands, or data exchange between flight controller, companion computer, and ground station.

## Key Concepts

### Message Structure

- **Message ID** - Unique identifier (use 12000-12999 for custom messages)
- **Fields** - Data payload (integers, floats, arrays, strings)
- **CRC Extra** - Message integrity check

### Message Definition XML

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

- **0-255** - Standard MAVLink messages (reserved)
- **12000-12999** - Recommended for custom messages

## Exercises

### Exercise 1: Create Custom Message Definition

```bash
cd ~/ardupilot
mkdir -p custom_mavlink

cat > custom_mavlink/custom_messages.xml << 'EOF'
<?xml version="1.0"?>
<mavlink>
  <include>common.xml</include>
  <version>3</version>
  <dialect>0</dialect>

  <messages>
    <message id="12345" name="CUSTOM_SENSOR_DATA">
      <description>Custom sensor telemetry data</description>
      <field type="uint64_t" name="time_usec" units="us">Timestamp</field>
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

```bash
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

### Exercise 3: Send Custom Message from Lua

```lua
-- send_custom_sensor.lua
local MAV_SEVERITY_INFO = 6

function update()
    local temperature = 25.5
    local pressure = 101325.0
    local humidity = 60.0

    gcs:send_text(MAV_SEVERITY_INFO, string.format(
        "Custom Sensor: T=%.1fC P=%.0fPa H=%.0f%%",
        temperature, pressure, humidity
    ))

    return update, 1000  -- Run every 1000ms
end

return update()
```

### Exercise 4: Receive Custom Message in Python

```python
# receive_custom_message.py
from pymavlink import mavutil
import sys

sys.path.insert(0, 'custom_mavlink/generated_python')

connection = mavutil.mavlink_connection('udp:127.0.0.1:14550')
connection.wait_heartbeat()

print("Listening for CUSTOM_SENSOR_DATA messages...")
while True:
    msg = connection.recv_match(type='CUSTOM_SENSOR_DATA', blocking=True, timeout=5)
    if msg:
        print(f"Temperature: {msg.temperature}°C")
        print(f"Pressure: {msg.pressure} Pa")
        print(f"Humidity: {msg.humidity}%")
```

### Exercise 5: Integrate Custom Message in ArduPilot C++

```bash
# Copy generated headers to ArduPilot MAVLink directory
cp custom_mavlink/generated/*.h \
   ardupilot/modules/mavlink/message_definitions/v1.0/
```

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

```bash
./waf configure --board sitl
./waf plane
```

## Common Issues

### Message ID Conflict

Use ID range 12000-12999. Check existing definitions:

```bash
grep -r "message id" modules/mavlink/
```

### Generated Code Not Found

```bash
ls custom_mavlink/generated/
ls custom_mavlink/generated_python/

export PYTHONPATH=$PYTHONPATH:~/ardupilot/custom_mavlink/generated_python
```

### Message Not Appearing in GCS

Copy XML to GCS definition folder. Mission Planner: `C:\Program Files (x86)\Mission Planner\MAVLink\`

## Message Design Best Practices

- Minimize field count and sizes — use `uint8_t` vs `uint32_t` where appropriate
- Always include `time_usec` timestamp field
- High-frequency (10-50Hz): attitude, position | Medium (1-10Hz): sensor data | Low (0.1-1Hz): diagnostics

---

- [MAVLink Developer Guide](https://mavlink.io/en/guide/define_xml_element.html)
- [PyMAVLink Documentation](https://mavlink.io/en/mavgen_python/)
- [ArduPilot MAVLink](https://ardupilot.org/dev/docs/mavlink-basics.html)
