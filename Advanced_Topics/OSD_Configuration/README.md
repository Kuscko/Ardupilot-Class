# OSD Configuration

ArduPilot OSD overlays critical flight data on FPV video feeds. Integrated OSD uses a MAX7456 chip (or similar); external OSD uses hardware like MinimOSD connected via MAVLink.

## Video Standards

| Standard | Resolution | Frame Rate | Regions              |
| -------- | ---------- | ---------- | -------------------- |
| NTSC     | 720x480    | 60Hz       | North America, Japan |
| PAL      | 720x576    | 50Hz       | Europe, Asia, Africa |

## Exercises

### Exercise 1: Enable and Configure OSD

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --osdmsp

param set OSD_TYPE 1              # 1=MAX7456, 2=SITL, 3=MSP
param set OSD_UNITS 1             # 0=metric, 1=imperial
param set OSD_FORMAT 0            # 0=NTSC, 1=PAL
param set OSD_SCREENS 3
param write
reboot
```

### Exercise 2: Design Custom Screen Layout

```bash
# Screen coordinates: X (0-29), Y (0-15 for NTSC/PAL)

# Altitude - top left
param set OSD1_ALTITUDE_X 2
param set OSD1_ALTITUDE_Y 2
param set OSD1_ALTITUDE_EN 1

# Battery voltage - top right
param set OSD1_BAT_VOLT_X 22
param set OSD1_BAT_VOLT_Y 2
param set OSD1_BAT_VOLT_EN 1

# Current - below battery voltage
param set OSD1_CURRENT_X 22
param set OSD1_CURRENT_Y 3
param set OSD1_CURRENT_EN 1

# Artificial horizon - center
param set OSD1_HORIZON_X 14
param set OSD1_HORIZON_Y 8
param set OSD1_HORIZON_EN 1

# GPS satellites - bottom left
param set OSD1_SATS_X 2
param set OSD1_SATS_Y 13
param set OSD1_SATS_EN 1

# Home direction - bottom center
param set OSD1_HOMEDIST_X 12
param set OSD1_HOMEDIST_Y 13
param set OSD1_HOMEDIST_EN 1

# Flight mode - bottom right
param set OSD1_FLTMODE_X 20
param set OSD1_FLTMODE_Y 13
param set OSD1_FLTMODE_EN 1

param write
```

### Exercise 3: Configure Multiple OSD Screens

```bash
# Screen 2: Navigation/Mission screen
param set OSD2_ALTITUDE_EN 1
param set OSD2_ALTITUDE_X 2
param set OSD2_ALTITUDE_Y 2

param set OSD2_WPNUMBER_EN 1
param set OSD2_WPNUMBER_X 14
param set OSD2_WPNUMBER_Y 3

param set OSD2_WPDIST_EN 1
param set OSD2_WPDIST_X 14
param set OSD2_WPDIST_Y 4

param set OSD2_CRSSHAIR_EN 1
param set OSD2_CRSSHAIR_X 14
param set OSD2_CRSSHAIR_Y 8

# Screen 3: Performance tuning screen
param set OSD3_PITCH_EN 1
param set OSD3_PITCH_X 2
param set OSD3_PITCH_Y 2

param set OSD3_ROLL_EN 1
param set OSD3_ROLL_X 2
param set OSD3_ROLL_Y 3

param set OSD3_THROTTLE_EN 1
param set OSD3_THROTTLE_X 2
param set OSD3_THROTTLE_Y 4

# Switch between screens using RC switch (channel 6)
param set OSD_SW_METHOD 1
param set OSD_CHAN 6
param write
```

Screen switching: Low PWM (< 1300) = Screen 1, Mid (1300-1700) = Screen 2, High (> 1700) = Screen 3.

### Exercise 4: Configure Warnings and Alerts

```bash
param set OSD1_BAT_VOLT_EN 1
param set BATT_LOW_VOLT 10.5
param set BATT_CRT_VOLT 10.0

param set OSD1_BATUSED_EN 1
param set OSD1_BATUSED_X 14
param set OSD1_BATUSED_Y 2

param set OSD1_RSSI_EN 1
param set OSD1_RSSI_X 25
param set OSD1_RSSI_Y 2
param set RSSI_TYPE 1

param set OSD1_SATS_EN 1
param set OSD1_FLTMODE_EN 1

param set OSD1_ARMING_EN 1
param set OSD1_ARMING_X 14
param set OSD1_ARMING_Y 10

param write
```

### Exercise 5: Customize OSD Appearance

```bash
param set OSD_W_BRIGHTNESS 3      # White level (0-3)
param set OSD_B_BRIGHTNESS 2      # Black level (0-3)
param set OSD_FONT 0              # Default font
param set OSD_UNITS 0             # 0=metric, 1=imperial, 2=SI
param set OSD_MSG_TIME 10         # Seconds to show messages
param set OSD1_STATS_EN 1         # Show flight stats after landing
param write
```

### Exercise 6: Mission Planner OSD Configuration

1. Connect to flight controller
2. CONFIG → Full Parameter List → OSD
3. Or: Setup → Optional Hardware → OSD → OSD Screen Setup
4. Visual editor shows OSD layout — drag elements to position
5. Enable/disable elements with checkboxes
6. Write parameters to flight controller

### Exercise 7: Test OSD in SITL

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py --console --osdmsp

module load OSD

mode FBWA
arm throttle

rc 6 1000  # Screen 1
rc 6 1500  # Screen 2
rc 6 2000  # Screen 3
```

## Common Issues

### No OSD Display

```bash
param show OSD_TYPE     # Should be 1 (MAX7456) or 2 (SITL)
param show OSD_FORMAT   # 0=NTSC, 1=PAL — must match camera
param show OSD1_*_EN    # Some should be 1
```

### Garbled or Flickering Display

```bash
param set OSD_W_BRIGHTNESS 2
param set OSD_B_BRIGHTNESS 1
param set OSD_FORMAT 0  # Try NTSC or PAL
```

### Elements Not Positioned Correctly

```bash
# NTSC: X=0-29, Y=0-12  |  PAL: X=0-29, Y=0-15
param set OSD1_ALTITUDE_X 2
param set OSD1_ALTITUDE_Y 2
```

### Missing or Incorrect Data

```bash
param set OSD1_SATS_EN 1
param set OSD1_GSPEED_EN 1
param set BATT_MONITOR 4       # Enable battery monitor
param set BATT_VOLT_PIN 2
param set BATT_CURR_PIN 3
param set ARSPD_TYPE 1         # Enable airspeed
param write
```

### OSD Screen Switching Not Working

```bash
param set OSD_SCREENS 3
param set OSD_SW_METHOD 1
param set OSD_CHAN 6
rc 6 1000
rc 6 1500
rc 6 2000
```

## OSD Element Reference

### Essential Flight Elements

| Element        | Parameter        | Purpose              |
| -------------- | ---------------- | -------------------- |
| Altitude       | OSD#_ALTITUDE    | Height above home    |
| Airspeed       | OSD#_ASPEED      | Current airspeed     |
| Ground speed   | OSD#_GSPEED      | Speed over ground    |
| Battery voltage| OSD#_BAT_VOLT    | Cell voltage         |
| Current draw   | OSD#_CURRENT     | Current consumption  |
| GPS satellites | OSD#_SATS        | GPS fix quality      |
| Flight mode    | OSD#_FLTMODE     | Current flight mode  |
| Horizon        | OSD#_HORIZON     | Artificial horizon   |

### Navigation Elements

| Element           | Parameter        | Purpose               |
| ----------------- | ---------------- | --------------------- |
| Home direction    | OSD#_HOMEDIR     | Arrow to home         |
| Home distance     | OSD#_HOMEDIST    | Distance to home      |
| Waypoint number   | OSD#_WPNUMBER    | Current waypoint      |
| Waypoint distance | OSD#_WPDIST      | Distance to WP        |
| Crosshair         | OSD#_CRSSHAIR    | Center reference      |
| Wind              | OSD#_WIND        | Wind speed/direction  |

### Status Elements

| Element        | Parameter      | Purpose           |
| -------------- | -------------- | ----------------- |
| Arming status  | OSD#_ARMING    | Pre-arm checks    |
| Messages       | OSD#_MESSAGE   | System messages   |
| RSSI           | OSD#_RSSI      | Signal strength   |
| Statistics     | OSD#_STATS     | Post-flight stats |

---

- [OSD Setup Guide](OSD_SETUP_GUIDE.md)
- [OSD Configuration](https://ardupilot.org/plane/docs/common-osd-overview.html)
- [OSD Parameter Reference](https://ardupilot.org/plane/docs/parameters.html#osd-parameters)
- [Mission Planner OSD](https://ardupilot.org/planner/docs/common-mission-planner-osd.html)
- [Digital OSD / MSP](https://ardupilot.org/plane/docs/common-msp-osd-overview.html)
