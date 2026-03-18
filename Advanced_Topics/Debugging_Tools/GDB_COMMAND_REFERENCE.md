# GDB Command Reference for ArduPilot

Quick reference for debugging ArduPilot with GDB.

---

## Starting GDB

```bash
# SITL with GDB
cd ~/ardupilot/ArduPlane
sim_vehicle.py --gdb

# Or manually
gdb --args build/sitl/bin/arduplane --model quadplane
```

```bash
# Hardware with GDB server
gdbserver :2345 /path/to/arduplane           # On target
arm-none-eabi-gdb build/target/bin/arduplane # On host
(gdb) target remote hostname:2345
```

---

## Basic Commands

| Command    | Short | Description                   | Example          |
| ---------- | ----- | ----------------------------- | ---------------- |
| `run`      | `r`   | Start program                 | `r`              |
| `continue` | `c`   | Continue execution            | `c`              |
| `next`     | `n`   | Step over (next line)         | `n`              |
| `step`     | `s`   | Step into function            | `s`              |
| `finish`   | `fin` | Run until function returns    | `fin`            |
| `quit`     | `q`   | Exit GDB                      | `q`              |
| `help`     | `h`   | Show help                     | `h breakpoints`  |

---

## Breakpoints

```gdb
# Break at function
(gdb) break AP_AHRS::update
(gdb) b Plane::update_flight_mode

# Break at file:line
(gdb) break Plane.cpp:123

# Break at address
(gdb) break *0x08001234

# Conditional breakpoint
(gdb) break Plane::update if altitude > 100

# Temporary breakpoint (delete after hit)
(gdb) tbreak main

# List / delete / disable / enable
(gdb) info breakpoints
(gdb) delete 1
(gdb) disable 1
(gdb) enable 1
(gdb) clear Plane::update
```

---

## Inspecting Variables

```gdb
# Print variable
(gdb) print altitude
(gdb) p/x altitude      # Hexadecimal
(gdb) p/f altitude      # Float
(gdb) p *gps_ptr        # Dereference pointer
(gdb) print array[0]@10 # Print first 10 elements

# Display (auto-print on every stop)
(gdb) display altitude
(gdb) display gps.num_sats
(gdb) info display
(gdb) delete display 1

# Examine memory
(gdb) x/10x 0x20000000  # 10 hex words at address
(gdb) x/s string_ptr    # As string
(gdb) x/i $pc           # As instruction at PC
```

---

## Call Stack

```gdb
(gdb) backtrace          # Show call stack
(gdb) bt full            # All frames with locals
(gdb) bt 5               # Show 5 frames

# Frame navigation
(gdb) frame 0
(gdb) up
(gdb) down
(gdb) info frame
(gdb) info locals
(gdb) info args
```

---

## Watchpoints

```gdb
(gdb) watch altitude               # Break on write
(gdb) watch gps.num_sats > 10      # Watch expression
(gdb) rwatch altitude              # Break on read
(gdb) awatch altitude              # Break on read or write
```

---

## Stepping and Continue

```gdb
(gdb) next                # Step over
(gdb) step                # Step into
(gdb) nexti               # Step one instruction
(gdb) finish              # Step out of function
(gdb) until Plane.cpp:100 # Continue to line
(gdb) continue
(gdb) continue 5          # Continue until breakpoint N
```

---

## Threads

```gdb
(gdb) info threads
(gdb) thread 2
(gdb) thread apply all bt
(gdb) break Plane::update thread 2
```

---

## Source Code

```gdb
(gdb) list
(gdb) list AP_AHRS::update
(gdb) list Plane.cpp:100
(gdb) set listsize 20
(gdb) search pattern
(gdb) reverse-search pattern
```

---

## ArduPilot-Specific Breakpoints

```gdb
# Setup phase
(gdb) break Plane::setup

# Main loop
(gdb) break Plane::loop
(gdb) break Plane::update

# EKF
(gdb) break NavEKF3::UpdateFilter

# GPS
(gdb) break AP_GPS::update

# Mode changes
(gdb) break Plane::set_mode
```

```gdb
# Print ArduPilot objects
(gdb) p *ahrs
(gdb) p ahrs->get_position()
(gdb) p *gps._drivers[0]
(gdb) p battery.voltage()
(gdb) p control_mode
```

---

## Advanced Commands

```gdb
# Commands on breakpoint hit
(gdb) commands 1
> silent
> printf "Altitude: %f\n", altitude
> continue
> end

# Modify variable
(gdb) set variable altitude = 100.0

# Call function
(gdb) call some_function()

# Save/restore breakpoints
(gdb) save breakpoints bp.gdb
(gdb) source bp.gdb
```

---

## Useful Settings

```gdb
(gdb) set pagination off
(gdb) set print pretty on
(gdb) set print elements 200
(gdb) set confirm off
(gdb) set history save on
(gdb) set history filename ~/.gdb_history
```

---

## Crash Analysis

```gdb
# Catch segfault
(gdb) catch signal SIGSEGV

# Core dump
(gdb) core arduplane core
(gdb) bt
(gdb) info registers
```

```bash
# Generate core dump
ulimit -c unlimited
./arduplane
gdb arduplane core
```

---

## TUI Mode

```gdb
(gdb) tui enable
(gdb) layout src      # Source code
(gdb) layout asm      # Assembly
(gdb) layout split    # Both
(gdb) layout regs     # Registers
(gdb) tui disable
```

---

## Common Workflows

### Debug GPS Issue

```gdb
(gdb) break AP_GPS::update
(gdb) run
(gdb) p *_drivers[0]
(gdb) p state[0].status
```

### Debug EKF Problem

```gdb
(gdb) break NavEKF3::UpdateFilter
(gdb) run
(gdb) p _gps_check_fail_status
(gdb) p _control_status
```

---

- [GDB Manual](https://sourceware.org/gdb/current/onlinedocs/gdb/)
- [GDB Quick Reference](https://darkdust.net/files/GDB%20Cheat%20Sheet.pdf)

**Author:** Patrick Kelly (@Kuscko)
