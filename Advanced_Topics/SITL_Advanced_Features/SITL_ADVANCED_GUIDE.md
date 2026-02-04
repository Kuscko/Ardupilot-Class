# SITL Advanced Features Guide

## Wind Simulation

**Enable wind:**
```bash
sim_vehicle.py --vehicle ArduPlane --console --map --wind=10,45,2
# 10 m/s wind from 45°, gusts up to 2 m/s
```

**Parameters:**
- Speed (m/s)
- Direction (degrees, 0=North)
- Variation/gusts (m/s)

**Test wind compensation:**
1. Set strong crosswind
2. Fly AUTO mission
3. Observe path correction

## Sensor Failure Injection

**Simulate GPS failure:**
```bash
param set SIM_GPS_DISABLE 1  # Disable GPS
param set SIM_GPS_DELAY 2    # 2 second delay
param set SIM_GPS_GLITCH_X 10  # 10m position glitch
```

**Simulate IMU failure:**
```bash
param set SIM_ACC1_BIAS_X 2.0  # Accelerometer bias
param set SIM_GYR1_BIAS_X 0.1  # Gyro bias
```

**Test failsafes:**
- GPS loss triggers RTL
- Verify EKF handles degraded sensors

## Multiple Vehicles

**Launch 2 aircraft:**
```bash
# Terminal 1
sim_vehicle.py -I0 --out=127.0.0.1:14550

# Terminal 2  
sim_vehicle.py -I1 --out=127.0.0.1:14551
```

**Connect both:**
```bash
mavproxy.py --master=127.0.0.1:14550 --master=127.0.0.1:14551
```

## Custom Start Locations

```bash
# CMAC (default)
sim_vehicle.py -L CMAC

# Custom lat,lon,alt,heading
sim_vehicle.py --custom-location=37.7749,-122.4194,100,180
```

## Replay Functionality

**Record flight:**
```bash
param set LOG_REPLAY 1  # Enable replay logging
# Fly mission
```

**Replay:**
```bash
sim_vehicle.py --replay logfile.BIN
```

**Author:** Patrick Kelly (@Kuscko)
