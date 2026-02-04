# ArduPilot Code Style Checklist

Use this checklist before submitting a pull request to ensure your code follows ArduPilot style guidelines.

---

## General Formatting

- [ ] No trailing whitespace on any line
- [ ] Files end with single newline
- [ ] No mixed line endings (use LF, not CRLF)
- [ ] Maximum line length: 120 characters (prefer 80-100)
- [ ] Use UTF-8 encoding

## Indentation

- [ ] Use 4 spaces for indentation (no tabs)
- [ ] Continuation lines indented by 4 spaces
- [ ] Switch case statements indented

**Example:**
```cpp
void function()
{
    if (condition) {
        do_something();
    }
}
```

## Braces

- [ ] Opening brace on same line as statement
- [ ] Closing brace on own line
- [ ] Always use braces, even for single-line blocks
- [ ] Consistent brace style throughout

**Correct:**
```cpp
if (condition) {
    statement;
}

if (condition) {
    statement;
} else {
    other_statement;
}
```

**Incorrect:**
```cpp
if (condition)
    statement;  // Missing braces

if (condition)
{  // Opening brace on wrong line
    statement;
}
```

## Naming Conventions

### Classes

- [ ] Use PascalCase for class names
- [ ] Prefix library classes with `AP_`

**Examples:**
```cpp
class AP_AHRS { };
class NavEKF3 { };
class Plane { };
```

### Functions

- [ ] Use snake_case for function names
- [ ] Use descriptive names
- [ ] Boolean functions start with verb (is_, has_, can_)

**Examples:**
```cpp
void update_position();
float get_altitude();
bool is_armed();
bool has_gps_lock();
```

### Variables

- [ ] Member variables prefixed with underscore: `_variable_name`
- [ ] Local variables use snake_case (no underscore)
- [ ] Global variables avoided (use singletons)

**Examples:**
```cpp
class MyClass {
private:
    float _altitude;          // Member variable
    uint32_t _last_update_ms; // Member variable
};

void function() {
    float local_value = 0;    // Local variable
}
```

### Constants

- [ ] Use ALL_CAPS for constants
- [ ] Use `constexpr` or `const` appropriately

**Examples:**
```cpp
static constexpr float MAX_SPEED = 25.0f;
static constexpr uint32_t TIMEOUT_MS = 5000;
const float GRAVITY = 9.81f;
```

### Enums

- [ ] Enum names in PascalCase
- [ ] Enum values in ALL_CAPS

**Example:**
```cpp
enum class FlightMode {
    MANUAL = 0,
    CIRCLE = 1,
    STABILIZE = 2,
    AUTO = 10,
};
```

## Comments

- [ ] Use `//` for single-line comments
- [ ] Use `/* */` for multi-line comments
- [ ] Document complex algorithms
- [ ] Explain "why", not "what"
- [ ] Update comments when code changes
- [ ] No commented-out code in PR

**Good:**
```cpp
// Limit acceleration to prevent motor saturation
float limited_accel = constrain_float(desired_accel, -MAX_ACCEL, MAX_ACCEL);
```

**Bad:**
```cpp
// Set x to 5
float x = 5.0f;  // What, not why
```

## Header Files

### Include Order

- [ ] System headers first (`#include <stdio.h>`)
- [ ] Library headers second (`#include <AP_Math/AP_Math.h>`)
- [ ] Local headers last (`#include "Plane.h"`)
- [ ] Group related includes together
- [ ] Alphabetize within groups

**Example:**
```cpp
#include <stdio.h>
#include <stdint.h>

#include <AP_AHRS/AP_AHRS.h>
#include <AP_GPS/AP_GPS.h>
#include <AP_Math/AP_Math.h>

#include "Plane.h"
#include "navigation.h"
```

### Header Guards

- [ ] Use `#pragma once` (preferred)
- [ ] Or use include guards: `#ifndef FILENAME_H` / `#define FILENAME_H`

**Example:**
```cpp
#pragma once

// Header contents here
```

## Class Structure

- [ ] `public` section first
- [ ] `protected` section second
- [ ] `private` section last
- [ ] Group related members together

**Example:**
```cpp
class AP_MyFeature {
public:
    // Constructors
    AP_MyFeature();

    // Public methods
    void init();
    void update();

protected:
    // Protected methods
    void internal_calc();

private:
    // Private member variables
    float _value;
    uint32_t _timestamp;

    // Private methods
    void calculate();
};
```

## Pointers and References

- [ ] Pointer/reference symbol attached to type: `int* ptr`, not `int *ptr`
- [ ] Use `nullptr` instead of `NULL` or `0`
- [ ] Check pointers before dereferencing

**Example:**
```cpp
void process_data(const DataStruct* data)
{
    if (data == nullptr) {
        return;
    }
    // Use data
}
```

## Type Casting

- [ ] Use C++ style casts (`static_cast`, `const_cast`, `reinterpret_cast`)
- [ ] Avoid C-style casts

**Correct:**
```cpp
float value = static_cast<float>(integer_value);
```

**Incorrect:**
```cpp
float value = (float)integer_value;  // C-style cast
```

## Floating Point

- [ ] Use `f` suffix for float literals: `1.0f`, not `1.0`
- [ ] Use `double` only when necessary (usually prefer `float`)
- [ ] Use `isnan()`, `isinf()` for validation

**Example:**
```cpp
float value = 3.14f;       // Correct
double precise = 3.14159;  // Only if double precision needed
```

## Boolean

- [ ] Use `true`/`false`, not `1`/`0` for booleans
- [ ] Explicitly test booleans: `if (is_armed)`, not `if (is_armed == true)`

**Correct:**
```cpp
bool armed = true;
if (armed) {
    // Do something
}
```

**Incorrect:**
```cpp
bool armed = 1;            // Use true/false
if (armed == true) {       // Redundant comparison
    // Do something
}
```

## Conditionals

- [ ] Use comparison operators explicitly: `if (value != 0)`, not `if (value)`
- [ ] Put constant on left side of comparison to prevent assignment: `if (5 == x)`
- [ ] Use braces even for single-line conditionals

## Loops

- [ ] Prefer range-based for loops when possible
- [ ] Cache loop limit if expensive to calculate
- [ ] Use `size_t` or `uint32_t` for array indices

**Example:**
```cpp
// Range-based for
for (auto& item : container) {
    process(item);
}

// Traditional loop with cached limit
const uint32_t count = get_count();
for (uint32_t i = 0; i < count; i++) {
    process(array[i]);
}
```

## Memory Management

- [ ] Avoid `new`/`delete` in flight code
- [ ] Use static allocation or object pools
- [ ] Check return values of allocation functions

## Error Handling

- [ ] Check return values
- [ ] Validate input parameters
- [ ] Use `INTERNAL_ERROR()` for should-never-happen cases
- [ ] Log errors appropriately

**Example:**
```cpp
bool init_sensor()
{
    if (!sensor.probe()) {
        gcs().send_text(MAV_SEVERITY_ERROR, "Sensor init failed");
        return false;
    }
    return true;
}
```

## Parameters

- [ ] Parameter names start with subsystem prefix
- [ ] Use appropriate parameter type (`PARAM_INT`, `PARAM_FLOAT`)
- [ ] Document parameter range and units
- [ ] Group related parameters

**Example:**
```cpp
// @Param: MYLIB_GAIN
// @DisplayName: My Library Gain
// @Description: Gain value for control loop
// @Range: 0.1 2.0
// @User: Advanced
AP_GROUPINFO("MYLIB_GAIN", 1, AP_MyLib, _gain, 1.0f),
```

## HAL Usage

- [ ] Use HAL functions for time: `AP_HAL::millis()`, `AP_HAL::micros()`
- [ ] Use HAL for I/O operations
- [ ] Don't use platform-specific code outside HAL

## Debugging Code

- [ ] Remove debug print statements before PR
- [ ] Remove commented-out code
- [ ] Remove unused variables
- [ ] No `#if 0` blocks in final code

## Testing Additions

- [ ] Test new features in SITL
- [ ] Add unit tests for new algorithms
- [ ] Document test procedure in PR

---

## Pre-Submission Commands

Run these commands before submitting PR:

```bash
# Code style check
./Tools/scripts/check_code_style.sh <your_file.cpp>

# Build test
./waf configure --board=sitl
./waf plane

# Unit tests
./waf tests

# Specific platform tests
./waf configure --board=MatekH743
./waf plane
```

---

## Common Violations

### Trailing Whitespace
```bash
# Find trailing whitespace
grep -n '[[:space:]]$' your_file.cpp

# Remove trailing whitespace (Linux/Mac)
sed -i 's/[[:space:]]*$//' your_file.cpp
```

### Tabs Instead of Spaces
```bash
# Find tabs
grep -n $'\t' your_file.cpp

# Convert tabs to spaces (4 spaces)
expand -t 4 your_file.cpp > temp && mv temp your_file.cpp
```

### Line Endings
```bash
# Convert CRLF to LF
dos2unix your_file.cpp
# Or
sed -i 's/\r$//' your_file.cpp
```

---

## Quick Reference

| Element | Style | Example |
|---------|-------|---------|
| Class | PascalCase | `AP_AHRS`, `NavEKF3` |
| Function | snake_case | `get_position()`, `update_nav()` |
| Member Variable | _snake_case | `_altitude`, `_timestamp` |
| Local Variable | snake_case | `local_value`, `temp` |
| Constant | ALL_CAPS | `MAX_SPEED`, `TIMEOUT_MS` |
| Enum | PascalCase | `FlightMode` |
| Enum Value | ALL_CAPS | `MANUAL`, `AUTO` |

---

## Resources

- [Official ArduPilot Coding Style](https://ardupilot.org/dev/docs/code-style.html)
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/)
- [Code Review Checklist](https://ardupilot.org/dev/docs/code-review.html)

---

**Author:** Patrick Kelly (@Kuscko)
**Version:** 1.0
**Last Updated:** 2026-02-03
