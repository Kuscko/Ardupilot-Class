# OSD Configuration Guide

## Enable OSD

```bash
param set OSD_TYPE 1         # MAX7456
param set OSD_CHAN 1         # Video channel
```

## Screen Items

```bash
param set OSD_ALTITUDE_EN 1  # Show altitude
param set OSD_BAT_VOLT_EN 1  # Show battery voltage
param set OSD_RSSI_EN 1      # Show RSSI
param set OSD_HORIZON_EN 1   # Show artificial horizon
```

## Position Items

```bash
param set OSD_ALTITUDE_X 23  # X position
param set OSD_ALTITUDE_Y 10  # Y position
```

**Screen grid:** 30 columns x 16 rows

**Author:** Patrick Kelly (@Kuscko)
