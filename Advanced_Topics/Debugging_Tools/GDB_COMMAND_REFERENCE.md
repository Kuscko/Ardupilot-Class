# GDB Command Reference for ArduPilot

Quick reference guide for debugging ArduPilot with GDB (GNU Debugger).

---

## Starting GDB

### SITL with GDB
```bash
# Start SITL with GDB
cd ~/ardupilot/ArduPlane
sim_vehicle.py --gdb

# Or manually
gdb --args build/sitl/bin/arduplane --model quadplane
```

### Hardware with GDB Server
```bash
# On target (if gdbserver available)
gdbserver :2345 /path/to/arduplane

# On host
arm-none-eabi-gdb build/target/bin/arduplane
(gdb) target remote hostname:2345
```

---

## Basic Commands

| Command | Short | Description | Example |
|---------|-------|-------------|---------|
| `run` | `r` | Start program | `r` |
| `continue` | `c` | Continue execution | `c` |
| `next` | `n` | Step over (next line) | `n` |
| `step` | `s` | Step into function | `s` |
| `finish` | `fin` | Run until function returns | `fin` |
| `quit` | `q` | Exit GDB | `q` |
| `help` | `h` | Show help | `h breakpoints` |

---

## Breakpoints

### Setting Breakpoints
```gdb
# Break at function
(gdb) break AP_AHRS::update
(gdb) b Plane::update_flight_mode

# Break at file:line
(gdb) break Plane.cpp:123
(gdb) b ArduPlane.cpp:456

# Break at address
(gdb) break *0x08001234

# Conditional breakpoint
(gdb) break Plane::update if altitude > 100

# Temporary breakpoint (delete after hit)
(gdb) tbreak main
```

### Managing Breakpoints
```gdb
# List breakpoints
(gdb) info breakpoints
(gdb) i b

# Delete breakpoint
(gdb) delete 1          # Delete breakpoint #1
(gdb) d 1

# Delete all breakpoints
(gdb) delete
(gdb) d

# Disable/enable breakpoint
(gdb) disable 1
(gdb) enable 1

# Clear breakpoint at location
(gdb) clear Plane::update
```

---

## Inspecting Variables

### Print Variables
```gdb
# Print variable
(gdb) print altitude
(gdb) p altitude

# Print with format
(gdb) p/x altitude      # Hexadecimal
(gdb) p/d altitude      # Decimal
(gdb) p/t altitude      # Binary
(gdb) p/f altitude      # Float

# Print structure
(gdb) print gps
(gdb) p *gps_ptr        # Dereference pointer

# Print array
(gdb) print array[0]@10 # Print first 10 elements
```

### Display (Auto-print)
```gdb
# Display variable on every stop
(gdb) display altitude
(gdb) disp altitude

# Display expression
(gdb) display gps.num_sats

# List displays
(gdb) info display

# Delete display
(gdb) delete display 1
```

### Examine Memory
```gdb
# Examine memory
(gdb) x/10x 0x20000000  # 10 hex words at address
(gdb) x/s string_ptr    # As string
(gdb) x/i $pc           # As instruction at PC
```

---

## Call Stack

### Backtrace
```gdb
# Show call stack
(gdb) backtrace
(gdb) bt

# Show all frames
(gdb) bt full

# Show N frames
(gdb) bt 5
```

### Frame Navigation
```gdb
# Select frame
(gdb) frame 0
(gdb) f 0

# Move up/down stack
(gdb) up
(gdb) down

# Frame info
(gdb) info frame
(gdb) info locals
(gdb) info args
```

---

## Watchpoints

### Set Watchpoints
```gdb
# Watch variable (break on write)
(gdb) watch altitude

# Watch expression
(gdb) watch gps.num_sats > 10

# Read watchpoint (break on read)
(gdb) rwatch altitude

# Access watchpoint (break on read or write)
(gdb) awatch altitude
```

---

## Control Flow

### Stepping
```gdb
# Step one line (step over)
(gdb) next
(gdb) n

# Step into function
(gdb) step
(gdb) s

# Step one instruction
(gdb) nexti
(gdb) ni

# Step out of function
(gdb) finish
(gdb) fin

# Continue to location
(gdb) until Plane.cpp:100
```

### Continue
```gdb
# Continue execution
(gdb) continue
(gdb) c

# Continue until breakpoint N
(gdb) continue 5
```

---

## Threads

### Thread Commands
```gdb
# List threads
(gdb) info threads

# Switch thread
(gdb) thread 2

# Apply command to all threads
(gdb) thread apply all bt

# Break on thread
(gdb) break Plane::update thread 2
```

---

## Source Code

### Viewing Source
```gdb
# List source code
(gdb) list
(gdb) l

# List function
(gdb) list AP_AHRS::update

# List file:line
(gdb) list Plane.cpp:100

# Show current line
(gdb) list

# Set listsize
(gdb) set listsize 20
```

### Search Source
```gdb
# Search forward
(gdb) search pattern

# Search backward
(gdb) reverse-search pattern
```

---

## Debugging ArduPilot-Specific

### Common ArduPilot Breakpoints
```gdb
# Setup phase
(gdb) break AP_HAL::Scheduler::init
(gdb) break Plane::setup

# Main loop
(gdb) break Plane::loop
(gdb) break Plane::update

# EKF
(gdb) break NavEKF3::UpdateFilter

# GPS
(gdb) break AP_GPS::update

# RC Input
(gdb) break RC_Channels::read_input

# Mode changes
(gdb) break Plane::set_mode
```

### Print ArduPilot Objects
```gdb
# AHRS
(gdb) p *ahrs
(gdb) p ahrs->get_position()

# GPS
(gdb) p *gps._drivers[0]
(gdb) p gps.num_sensors()

# Battery
(gdb) p battery.voltage()

# Mode
(gdb) p control_mode
(gdb) p mode_auto
```

---

## Advanced Commands

### Conditional Breaks
```gdb
# Break if condition true
(gdb) break Plane::update if gps.num_sats < 6

# Modify breakpoint condition
(gdb) condition 1 altitude > 100
```

### Commands on Breakpoint
```gdb
# Execute commands when breakpoint hit
(gdb) commands 1
> silent
> printf "Altitude: %f\n", altitude
> continue
> end
```

### Scripting
```gdb
# Source GDB script
(gdb) source debug_script.gdb

# Define command
(gdb) define print_pos
> p ahrs->get_position()
> end
```

### Save/Restore
```gdb
# Save breakpoints
(gdb) save breakpoints bp.gdb

# Restore breakpoints
(gdb) source bp.gdb
```

---

## Useful Settings

```gdb
# Disable pagination
(gdb) set pagination off

# Print arrays nicely
(gdb) set print pretty on

# Set print limit
(gdb) set print elements 200

# Disable confirmation
(gdb) set confirm off

# Save history
(gdb) set history save on
(gdb) set history filename ~/.gdb_history
```

---

## Example Debugging Session

```gdb
# Start GDB with SITL
$ cd ~/ardupilot/ArduPlane
$ sim_vehicle.py --gdb

# Set breakpoints
(gdb) break Plane::update
(gdb) break AP_GPS::update if num_sats > 0

# Run
(gdb) run

# When breakpoint hit
Breakpoint 1, Plane::update ()

# Print variables
(gdb) p control_mode
$1 = 0

(gdb) p ahrs->get_position()
$2 = {lat = -353632610, lng = 1491652370}

# Continue
(gdb) continue

# Modify and test
(gdb) set variable altitude = 100.0
(gdb) continue

# Backtrace on crash
(gdb) bt
#0  Plane::update () at Plane.cpp:123
#1  0x08001234 in main_loop ()
#2  0x08005678 in main ()

# Examine crash location
(gdb) frame 0
(gdb) list
(gdb) p variable_that_crashed

# Fix and rebuild (outside GDB)
# Restart debugging
```

---

## Debugging Crashes

### Catch Signals
```gdb
# Catch segfault
(gdb) catch signal SIGSEGV

# Catch all signals
(gdb) catch signal all

# Info on signals
(gdb) info signals
```

### Core Dump Analysis
```bash
# Generate core dump
ulimit -c unlimited
./arduplane
# (crash happens)

# Load core dump
gdb arduplane core
(gdb) bt
(gdb) info registers
```

---

## Tips and Tricks

### Pretty Printers
```gdb
# Enable STL pretty printers (Python-based)
(gdb) python import sys
(gdb) python sys.path.insert(0, '/path/to/pretty-printers')
(gdb) python from libstdcxx.v6.printers import register_libstdcxx_printers
(gdb) python register_libstdcxx_printers(None)
```

### TUI Mode
```gdb
# Text UI mode (split screen)
(gdb) tui enable
(gdb) layout src      # Source code
(gdb) layout asm      # Assembly
(gdb) layout split    # Both
(gdb) layout regs     # Registers

# Disable TUI
(gdb) tui disable
```

### Logging
```gdb
# Log output to file
(gdb) set logging on
(gdb) set logging file debug.log
# ... debug commands ...
(gdb) set logging off
```

---

## Common Workflows

### Debug GPS Issue
```gdb
(gdb) break AP_GPS::update
(gdb) run
# When hit:
(gdb) p *_drivers[0]
(gdb) p num_sensors()
(gdb) p state[0].status
(gdb) continue
```

### Debug EKF Problem
```gdb
(gdb) break NavEKF3::UpdateFilter
(gdb) run
# When hit:
(gdb) p _gps_check_fail_status
(gdb) p _control_status
(gdb) continue
```

### Debug Parameter Issue
```gdb
(gdb) break AP_Param::load_all
(gdb) run
# When hit:
(gdb) step  # Step through loading
(gdb) p _var_info[i]
```

---

## Resources

- [GDB Manual](https://sourceware.org/gdb/current/onlinedocs/gdb/)
- [GDB Quick Reference](https://darkdust.net/files/GDB%20Cheat%20Sheet.pdf)
- [Debugging with GDB](https://www.gnu.org/software/gdb/documentation/)

---

**Author:** Patrick Kelly (@Kuscko)
**Version:** 1.0
**Last Updated:** 2026-02-03
