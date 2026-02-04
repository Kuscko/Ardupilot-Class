# Testing and CI/CD

## Overview

Master ArduPilot's testing framework and continuous integration workflows for reliable code contributions and automated quality assurance. Comprehensive testing ensures flight software stability, prevents regressions, and maintains the high reliability standards required for autonomous systems [1].

This module covers the autotest framework, unit testing, simulation tests, GitHub CI/CD workflows, pre-commit hooks, and test coverage analysis.

## Prerequisites

Before starting this module, you should have:

- Completed ArduPilot build system setup
- Git and GitHub account for contributions
- Python programming knowledge
- Understanding of SITL simulation
- Familiarity with ArduPilot codebase structure

## What You'll Learn

By completing this module, you will:

- Run and create autotest simulation tests
- Write unit tests for ArduPilot libraries
- Set up pre-commit hooks for code quality
- Understand GitHub CI/CD workflows
- Analyze test coverage and identify gaps
- Debug failing tests efficiently
- Contribute tests with code changes

## Key Concepts

### ArduPilot Testing Layers

Multi-level testing strategy [1]:

**Unit Tests:**
- Test individual functions and classes
- Fast execution (milliseconds)
- No hardware or simulation required
- Located in libraries/*/tests/

**Integration Tests:**
- Test component interactions
- Use SITL simulation
- Validate MAVLink communication
- Autotest framework

**System Tests:**
- Full vehicle simulation tests
- Complete mission scenarios
- Hardware-in-the-loop (HITL)
- Real hardware validation

### Autotest Framework

Python-based test automation [2]:

**Test Categories:**
- Takeoff and land sequences
- Flight mode transitions
- Failsafe behaviors
- Mission execution
- Parameter changes
- Sensor failures

**Test Vehicles:**
- Copter (multicopter)
- Plane (fixed-wing)
- Rover (ground vehicle)
- Sub (submarine)
- Helicopter
- QuadPlane

### CI/CD Pipeline

Automated testing on GitHub [3]:

| Stage | Purpose | Duration |
| ----- | ------- | -------- |
| Build | Compile all vehicle types | 10-15 min |
| Unit Tests | Run library unit tests | 2-5 min |
| Autotest | SITL simulation tests | 60-90 min |
| Style Check | Code formatting validation | 1-2 min |
| Warnings | Check for compiler warnings | 5-10 min |

## Hands-On Practice

### Exercise 1: Run Existing Autotests

Execute complete autotest suite:

```bash
# Run all copter tests
cd ~/ardupilot
./Tools/autotest/autotest.py --vehicle=Copter

# Run specific test
./Tools/autotest/autotest.py --vehicle=Copter --test=Fly

# Run with debugging
./Tools/autotest/autotest.py --vehicle=Copter --debug

# Run faster (no delays)
./Tools/autotest/autotest.py --vehicle=Copter --speedup=10

# Run subset of tests
./Tools/autotest/autotest.py --vehicle=Copter --test=Takeoff,Land

# Run plane tests
./Tools/autotest/autotest.py --vehicle=Plane

# Run all vehicles (takes hours!)
./Tools/autotest/autotest.py
```

**Expected output:**

```
AP: Copter V4.5.0
Autotest starting
Test: Takeoff ... OK (15.2s)
Test: Land ... OK (8.4s)
Test: RTL ... OK (22.1s)
Test: Mission ... OK (45.3s)
...
ALL TESTS PASSED
```

### Exercise 2: Write a Custom Autotest

Create new test for specific behavior:

```python
# Tools/autotest/copter.py
# Add new test method to TestCopter class

def CustomFlightTest(self):
    """Test custom flight behavior"""

    # Takeoff to 10m
    self.takeoff(10)

    # Change to LOITER mode
    self.change_mode('LOITER')

    # Wait for position hold
    self.wait_location(
        self.mav.location(),
        accuracy=2,
        timeout=30
    )

    # Verify altitude maintained
    self.wait_altitude(
        9, 11,  # Between 9 and 11 meters
        timeout=10,
        relative=True
    )

    # Test mode change
    self.change_mode('RTL')

    # Wait for landing
    self.wait_disarmed(timeout=90)

    self.progress("Custom flight test PASSED")
```

**Run custom test:**

```bash
# Add test to test list in copter.py
# Then run:
./Tools/autotest/autotest.py --vehicle=Copter --test=CustomFlightTest
```

### Exercise 3: Write Unit Tests

Create unit tests for library functions:

```cpp
// libraries/AP_Example/tests/test_example.cpp

#include <AP_gtest.h>
#include <AP_Example/AP_Example.h>

// Test fixture
class AP_Example_Test : public ::testing::Test {
protected:
    AP_Example example;
};

// Test basic functionality
TEST_F(AP_Example_Test, Initialization) {
    EXPECT_TRUE(example.init());
    EXPECT_EQ(example.get_value(), 0);
}

// Test calculations
TEST_F(AP_Example_Test, Calculations) {
    example.set_value(10);
    EXPECT_EQ(example.get_value(), 10);

    example.add(5);
    EXPECT_EQ(example.get_value(), 15);

    example.multiply(2);
    EXPECT_EQ(example.get_value(), 30);
}

// Test edge cases
TEST_F(AP_Example_Test, EdgeCases) {
    example.set_value(INT_MAX);
    example.add(1);
    // Should handle overflow gracefully
    EXPECT_LT(example.get_value(), INT_MAX);
}

// Test error conditions
TEST_F(AP_Example_Test, ErrorHandling) {
    EXPECT_FALSE(example.invalid_operation());
}
```

**Run unit tests:**

```bash
# Build and run all unit tests
cd ~/ardupilot
./waf configure --board=linux
./waf tests

# Run specific test
./build/linux/tests/test_example

# With verbose output
./build/linux/tests/test_example --gtest_verbose
```

### Exercise 4: Set Up Pre-Commit Hooks

Install code quality checks:

```bash
# Install pre-commit framework
pip3 install pre-commit

# Create .pre-commit-config.yaml
cd ~/ardupilot
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: local
    hooks:
      - id: check-style
        name: Check code style
        entry: ./Tools/scripts/run_checkstyle.sh
        language: system
        types: [c++, c]

      - id: check-python
        name: Check Python style
        entry: python3 -m flake8
        language: system
        types: [python]

      - id: check-trailing-whitespace
        name: Check trailing whitespace
        entry: trailing-whitespace-fixer
        language: system

      - id: check-yaml
        name: Check YAML
        entry: check-yaml
        language: system
        types: [yaml]
EOF

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Hooks now run automatically on git commit
```

**Expected behavior:**

```bash
# On git commit, hooks run:
Check code style...............................................Passed
Check Python style.............................................Passed
Check trailing whitespace......................................Passed
Check YAML.....................................................Passed
```

### Exercise 5: GitHub CI/CD Workflow

Understand and use GitHub Actions:

```yaml
# .github/workflows/test_custom.yml
# Custom workflow for specific tests

name: Custom Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-20.04

    steps:
      - name: Checkout code
        uses: actions/checkout@v2
        with:
          submodules: recursive

      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            build-essential \
            python3-dev \
            python3-pip

      - name: Build ArduPilot
        run: |
          ./waf configure --board=sitl
          ./waf copter

      - name: Run unit tests
        run: |
          ./waf tests

      - name: Run autotest
        run: |
          ./Tools/autotest/autotest.py \
            --vehicle=Copter \
            --test=Takeoff,Land \
            --speedup=10

      - name: Upload logs
        if: failure()
        uses: actions/upload-artifact@v2
        with:
          name: test-logs
          path: /tmp/autotest_logs/
```

**Trigger workflow:**

```bash
# Push to trigger CI
git add .
git commit -m "Add custom tests"
git push origin feature-branch

# Watch workflow in GitHub
# Actions tab shows test progress
# Green check = all tests passed
# Red X = tests failed, review logs
```

### Exercise 6: Test Coverage Analysis

Measure test coverage:

```bash
# Build with coverage enabled
cd ~/ardupilot
./waf configure --board=sitl --coverage
./waf copter

# Run tests
./Tools/autotest/autotest.py --vehicle=Copter

# Generate coverage report
gcov build/sitl/arducopter/*.gcno
lcov --capture --directory . --output-file coverage.info
genhtml coverage.info --output-directory coverage_html

# View report
firefox coverage_html/index.html
```

**Analyze results:**

```
Coverage Summary:
- Libraries: 75% line coverage
- Vehicle code: 82% line coverage
- Untested areas:
  - Error handling paths
  - Failsafe edge cases
  - Rare sensor configurations

Action: Write tests for untested code paths
```

### Exercise 7: Debug Failing Tests

Troubleshoot test failures:

```bash
# Run test with debug output
./Tools/autotest/autotest.py \
  --vehicle=Copter \
  --test=Mission \
  --debug \
  --no-clean

# Test fails, examine logs
cd /tmp/autotest_logs/
ls -lt

# View detailed log
less Copter-test.Mission/APM.log

# Run with GDB for crashes
./Tools/autotest/autotest.py \
  --vehicle=Copter \
  --test=Mission \
  --gdb

# Breakpoint at failure point
# (gdb) break mission_start
# (gdb) continue
```

**Common failure patterns:**

```python
# Timeout failures - increase timeout
self.wait_altitude(9, 11, timeout=30)  # Increase from 10

# Intermittent failures - add retries
for i in range(3):
    try:
        self.test_operation()
        break
    except Exception as e:
        if i == 2:
            raise
        time.sleep(1)

# Race conditions - add synchronization
self.wait_ready_to_arm()  # Wait before arming
self.arm_vehicle()
```

## Common Issues

### Issue 1: Autotest Hangs

**Symptoms:**
- Test doesn't complete
- Process stuck
- No output for minutes

**Solutions:**

```bash
# Kill hanging process
pkill -f sim_vehicle

# Clean up temp files
rm -rf /tmp/autotest_*

# Run with timeout
timeout 600 ./Tools/autotest/autotest.py --vehicle=Copter

# Check for port conflicts
netstat -an | grep 14550
# Kill processes using test ports

# Reduce speedup (may cause timing issues)
./Tools/autotest/autotest.py --vehicle=Copter --speedup=1
```

### Issue 2: Unit Test Compilation Fails

**Symptoms:**
- Build errors in test code
- Linking failures
- Missing dependencies

**Solutions:**

```bash
# Clean build
cd ~/ardupilot
./waf clean
./waf configure --board=linux
./waf tests

# Check for missing includes
# Add to test file:
#include <AP_HAL/AP_HAL.h>
#include <AP_Math/AP_Math.h>

# Verify test framework installed
sudo apt-get install libgtest-dev
cd /usr/src/gtest
sudo cmake .
sudo make
sudo cp *.a /usr/lib

# Link required libraries in wscript
# def build(bld):
#     bld.ap_program(
#         libraries=['AP_Example', 'AP_Math']
#     )
```

### Issue 3: CI Fails Locally Passes

**Symptoms:**
- Tests pass on local machine
- GitHub CI shows failures
- Environment differences

**Solutions:**

```bash
# Use Docker to match CI environment
docker run -it --rm -v $(pwd):/ardupilot \
  ubuntu:20.04 /bin/bash

# Inside container:
cd /ardupilot
apt-get update
apt-get install -y build-essential python3-dev
./waf configure --board=sitl
./waf copter
./Tools/autotest/autotest.py --vehicle=Copter

# Check for:
# - Different Python versions
# - Missing system dependencies
# - Timing assumptions (CI slower)
# - Hard-coded paths
```

### Issue 4: Test Flakiness

**Symptoms:**
- Test passes sometimes, fails others
- Intermittent failures
- No clear cause

**Solutions:**

```bash
# Run test multiple times
for i in {1..10}; do
  ./Tools/autotest/autotest.py --vehicle=Copter --test=Mission
  if [ $? -ne 0 ]; then
    echo "Failed on run $i"
    break
  fi
done

# Identify flaky tests
# Common causes:
# - Timing dependencies
# - Insufficient wait periods
# - Race conditions
# - Resource cleanup issues

# Fix: Add proper synchronization
self.wait_ready_to_arm()
self.wait_heartbeat()
self.wait_mode('LOITER')

# Increase tolerances
self.wait_location(..., accuracy=5)  # Increase from 2
```

### Issue 5: Coverage Report Empty

**Symptoms:**
- No coverage data generated
- Empty report
- Missing .gcno files

**Solutions:**

```bash
# Rebuild with coverage
./waf clean
./waf configure --board=sitl --coverage
./waf copter

# Verify coverage files created
find build/sitl -name "*.gcno"
# Should list many files

# Run tests (generates .gcda files)
./Tools/autotest/autotest.py --vehicle=Copter

# Check .gcda files created
find build/sitl -name "*.gcda"

# Generate report
lcov --directory build/sitl \
     --capture \
     --output-file coverage.info

# If still empty, check compiler flags
./waf configure --board=sitl --coverage --check-c-compiler=gcc
```

## Best Practices

### Test Design Principles

```python
# 1. Test one thing per test
def TestTakeoff(self):
    """Only test takeoff, not entire mission"""
    self.takeoff(10)
    self.wait_altitude(9, 11, relative=True, timeout=30)

# 2. Independent tests (no dependencies)
def TestMission(self):
    """Complete test, doesn't rely on previous tests"""
    self.takeoff(10)
    self.load_mission("test_mission.txt")
    self.run_mission()
    self.wait_disarmed()

# 3. Descriptive names
def TestGeofenceBreachTriggersRTL(self):
    """Clear what behavior is tested"""
    pass

# 4. Fast tests (< 30 seconds ideal)
def TestQuickArmDisarm(self):
    """Fast smoke test"""
    self.arm_vehicle()
    self.disarm_vehicle()
```

### Contributing Tests

```bash
# When submitting PR with code changes:

# 1. Add test for new feature
# Example: New flight mode
def TestNewFlightMode(self):
    self.takeoff(10)
    self.change_mode('NEW_MODE')
    self.verify_new_mode_behavior()
    self.land()

# 2. Add test for bug fix
# Reproduce bug, verify fix prevents it

# 3. Update existing tests if needed
# If behavior changed, update test expectations

# 4. Run full test suite before submitting
./Tools/autotest/autotest.py --vehicle=Copter

# 5. Check coverage increased
# New code should have tests
```

### Continuous Testing Workflow

```bash
# Local development workflow:

# 1. Make code changes
vim libraries/AP_Example/AP_Example.cpp

# 2. Build
./waf copter

# 3. Run relevant unit tests
./build/linux/tests/test_example

# 4. Run relevant autotests
./Tools/autotest/autotest.py --vehicle=Copter --test=Feature

# 5. Run pre-commit checks
pre-commit run

# 6. Commit if all pass
git add .
git commit -m "Add new feature with tests"

# 7. Push and watch CI
git push origin feature-branch
# Monitor GitHub Actions

# 8. Address any CI failures
# Fix, commit, push again
```

## Additional Resources

- [Autotest Documentation](https://ardupilot.org/dev/docs/testing-with-autotest.html) [1] - Complete autotest guide
- [Unit Testing](https://ardupilot.org/dev/docs/unit-tests.html) [2] - Unit test framework
- [GitHub Actions](https://docs.github.com/en/actions) [3] - CI/CD documentation
- [Contributing Guide](https://ardupilot.org/dev/docs/contributing.html) - How to contribute

### Testing Tools

- [Valgrind](https://valgrind.org/) - Memory leak detection
- [GDB](https://www.gnu.org/software/gdb/) - Debugging tool
- [Coverage.py](https://coverage.readthedocs.io/) - Python coverage
- [gcov/lcov](http://ltp.sourceforge.net/coverage/lcov.php) - C++ coverage

## Next Steps

After mastering testing and CI/CD:

1. **Advanced Test Scenarios** - Complex multi-vehicle tests
2. **Performance Testing** - Benchmark and profiling
3. **Fuzz Testing** - Automated bug finding
4. **Hardware Testing** - Real hardware validation

---

**Sources:**

[1] https://ardupilot.org/dev/docs/testing-with-autotest.html
[2] https://ardupilot.org/dev/docs/unit-tests.html
[3] https://docs.github.com/en/actions
