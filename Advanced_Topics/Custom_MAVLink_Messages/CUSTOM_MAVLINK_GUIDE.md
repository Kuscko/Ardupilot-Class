# Custom MAVLink Messages Guide

## Message Definition (.xml)

**Create custom.xml:**
```xml
<?xml version="1.0"?>
<mavlink>
    <messages>
        <message id="12345" name="CUSTOM_DATA">
            <field type="uint32_t" name="timestamp">ms</field>
            <field type="float" name="value1">custom value 1</field>
            <field type="float" name="value2">custom value 2</field>
        </message>
    </messages>
</mavlink>
```

## Generate Code

```bash
# Clone mavlink repo
git clone https://github.com/mavlink/mavlink.git
cd mavlink

# Generate headers
python -m pymavlink.tools.mavgen --lang=C custom.xml -o generated/
```

## Send from Lua

```lua
function send_custom()
    -- Requires ArduPilot 4.3+ with custom MAVLink support
    mavlink:send_chan(0, 12345, timestamp, value1, value2)
    return send_custom, 1000
end
return send_custom()
```

**Author:** Patrick Kelly (@Kuscko)
