# ArduPilot Code Style Checklist

Use this checklist before submitting a pull request.

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

```cpp
class AP_AHRS { };
class NavEKF3 { };
class Plane { };
```

### Functions

- [ ] Use snake_case for function names
- [ ] Boolean functions start with verb (is_, has_, can_)

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

```cpp
static constexpr float MAX_SPEED = 25.0f;
static constexpr uint32_t TIMEOUT_MS = 5000;
const float GRAVITY = 9.81f;
```

### Enums

- [ ] Enum names in PascalCase
- [ ] Enum values in ALL_CAPS

```cpp
enum class FlightMode {
    MANUAL = 0,
    CIRCLE = 1,
    STABILIZE = 2,
    AUTO = 10,
};
```

## Comments

- [ ] Use `//` for single-line comments, `/* */` for multi-line
- [ ] Explain "why", not "what"
- [ ] Update comments when code changes
- [ ] No commented-out code in PR

**Good:**
```cpp
// Limit acceleration to prevent motor saturation
float limited_accel = constrain_float(desired_accel, -MAX_ACCEL, MAX_ACCEL);
```

## Header Files

### Include Order

- [ ] System headers first (`#include <stdio.h>`)
- [ ] Library headers second (`#include <AP_Math/AP_Math.h>`)
- [ ] Local headers last (`#include "Plane.h"`)
- [ ] Alphabetize within groups

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

```cpp
#pragma once

// Header contents here
```

## Class Structure

- [ ] `public` first, `protected` second, `private` last

```cpp
class AP_MyFeature {
public:
    AP_MyFeature();
    void init();
    void update();

protected:
    void internal_calc();

private:
    float _value;
    uint32_t _timestamp;
    void calculate();
};
```

## Pointers and References

- [ ] Pointer/reference symbol attached to type: `int* ptr`
- [ ] Use `nullptr` instead of `NULL` or `0`
- [ ] Check pointers before dereferencing

```cpp
void process_data(const DataStruct* data)
{
    if (data == nullptr) {
        return;
    }
}
```

## Type Casting

- [ ] Use C++ style casts (`static_cast`, `const_cast`, `reinterpret_cast`)

```cpp
float value = static_cast<float>(integer_value);  // Correct
float value = (float)integer_value;                // Incorrect
```

## Floating Point

- [ ] Use `f` suffix: `1.0f`, not `1.0`
- [ ] Use `isnan()`, `isinf()` for validation

## Boolean

- [ ] Use `true`/`false`, not `1`/`0`
- [ ] Explicitly test: `if (is_armed)`, not `if (is_armed == true)`

## Loops

- [ ] Prefer range-based for loops when possible
- [ ] Use `size_t` or `uint32_t` for array indices

```cpp
for (auto& item : container) {
    process(item);
}

const uint32_t count = get_count();
for (uint32_t i = 0; i < count; i++) {
    process(array[i]);
}
```

## Memory Management

- [ ] Avoid `new`/`delete` in flight code
- [ ] Use static allocation or object pools

## Error Handling

- [ ] Check return values
- [ ] Use `INTERNAL_ERROR()` for should-never-happen cases

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

```cpp
// @Param: MYLIB_GAIN
// @DisplayName: My Library Gain
// @Description: Gain value for control loop
// @Range: 0.1 2.0
// @User: Advanced
AP_GROUPINFO("MYLIB_GAIN", 1, AP_MyLib, _gain, 1.0f),
```

## HAL Usage

- [ ] Use `AP_HAL::millis()`, `AP_HAL::micros()` for time
- [ ] Don't use platform-specific code outside HAL

## Debugging Code

- [ ] Remove debug print statements before PR
- [ ] Remove commented-out code and unused variables
- [ ] No `#if 0` blocks in final code

## Testing

- [ ] Test new features in SITL
- [ ] Add unit tests for new algorithms

---

## Pre-Submission Commands

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
grep -n '[[:space:]]$' your_file.cpp
sed -i 's/[[:space:]]*$//' your_file.cpp
```

### Tabs Instead of Spaces
```bash
grep -n $'\t' your_file.cpp
expand -t 4 your_file.cpp > temp && mv temp your_file.cpp
```

### Line Endings
```bash
dos2unix your_file.cpp
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

- [Official ArduPilot Coding Style](https://ardupilot.org/dev/docs/code-style.html)
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/)

**Author:** Patrick Kelly (@Kuscko)
