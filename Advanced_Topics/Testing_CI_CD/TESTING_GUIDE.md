# ArduPilot Testing Guide

## autotest Framework

**Run SITL tests:**
```bash
cd ~/ardupilot
Tools/autotest/autotest.py build.Plane test.Plane
```

**Run specific test:**
```bash
./Tools/autotest/autotest.py test.Plane.FlyEachFrame
```

## Writing Tests

**Example test (Python):**
```python
def MyTest(self):
    """Test description"""
    self.change_mode('FBWA')
    self.arm_vehicle()
    self.set_rc(3, 1700)  # Throttle
    self.wait_altitude(50, 60, relative=True)
    self.disarm_vehicle()
```

**Author:** Patrick Kelly (@Kuscko)
