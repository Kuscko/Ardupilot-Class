# Building ArduPilot from Source

## Overview

Learn to build ArduPilot Plane 4.5.7 from source in WSL2/Ubuntu. Building from source allows you to customize features, contribute code, test the latest developments, and understand the ArduPilot architecture at a deeper level [1].

**Target Version:** Plane 4.5.7 (commit: 0358a9c210bc6c965006f5d6029239b7033616df)

## Prerequisites

Before starting, ensure you have:

- Windows 10/11 with Administrator access
- 10GB+ free disk space
- 8GB+ RAM recommended (16GB for smooth operation)
- Basic Linux command line knowledge
- Internet connection for downloading dependencies

## What You'll Learn

By completing this module, you will:

- Set up a WSL2 development environment on Windows
- Clone and configure the ArduPilot repository
- Build ArduPilot for SITL (Software-In-The-Loop) simulation
- Build ArduPilot for hardware targets (flight controllers)
- Troubleshoot common build errors
- Understand the WAF build system used by ArduPilot

## Getting Started

### Complete Build Instructions

See **[BUILD_GUIDE.md](BUILD_GUIDE.md)** for comprehensive step-by-step instructions covering:

- WSL2 installation and setup
- Installing build dependencies
- Cloning ArduPilot repository
- Configuring and building for SITL
- Building for hardware targets
- Verifying successful builds

**Estimated Time:** 1-2 hours (including downloads)

## Hands-On Practice

### Exercise 1: Build for SITL

Build ArduPilot for software simulation:

```bash
# Clone repository
cd ~
git clone https://github.com/ArduPilot/ardupilot.git
cd ardupilot

# Checkout Plane 4.5.7
git checkout Plane-4.5.7
git submodule update --init --recursive

# Configure for SITL
./waf configure --board sitl

# Build ArduPlane
./waf plane
```

**Expected Result:**
```
Build finished successfully
'build/sitl/bin/arduplane' -> 'ArduPlane/arduplane'
```

**Verify Build:**
```bash
cd ArduPlane
./arduplane --version
# Should show: ArduPlane V4.5.7 (Plane-4.5.7)
```

### Exercise 2: Build for Hardware

Build for a real flight controller:

```bash
# List available boards
./waf list_boards

# Configure for specific board (example: Pixhawk)
./waf configure --board Pixhawk1

# Build
./waf plane

# Find firmware
ls -lh build/Pixhawk1/bin/arduplane.apj
```

**Expected Result:** Firmware file created in `build/<BOARD>/bin/`

### Exercise 3: Clean and Rebuild

Practice cleaning and rebuilding:

```bash
# Clean build artifacts
./waf clean

# Reconfigure and build
./waf configure --board sitl
./waf plane
```

**Use Case:** Necessary after pulling code updates or changing boards.

## Key Concepts

### WAF Build System

ArduPilot uses WAF (Waf Build System) instead of Make. Key commands:

- `./waf configure --board <BOARD>` - Configure for target board
- `./waf list_boards` - List all supported boards
- `./waf plane` - Build ArduPlane
- `./waf copter` - Build ArduCopter
- `./waf rover` - Build ArduRover
- `./waf clean` - Remove build artifacts

**Source:** [ArduPilot WAF Documentation](https://ardupilot.org/dev/docs/waf.html) [2]

### Build Targets

| Target | Purpose | Build Command |
|--------|---------|---------------|
| SITL | Software simulation | `./waf configure --board sitl` |
| Pixhawk1 | Pixhawk flight controllers | `./waf configure --board Pixhawk1` |
| MatekH743 | Matek H743 boards | `./waf configure --board MatekH743` |
| CubeOrange | Hex Cube Orange | `./waf configure --board CubeOrange` |

Full board list: `./waf list_boards` or see [Supported Boards](https://ardupilot.org/plane/docs/common-autopilots.html) [3]

### Submodules

ArduPilot uses Git submodules for external libraries. Always update after checkout:

```bash
git submodule update --init --recursive
```

**Why:** Ensures all required libraries (MAVLink, drivers, etc.) are present.

## Common Issues

### Issue: Python Package Errors

**Symptom:** `ModuleNotFoundError` or `python-argparse` not found

**Solution:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions

### Issue: WAF Configuration Fails

**Symptom:** `./waf configure` reports missing tools

**Solution:**
```bash
# Install prerequisites
cd ardupilot/Tools/environment_install
./install-prereqs-ubuntu.sh -y
```

### Issue: Build Errors After Git Pull

**Symptom:** Build fails after `git pull`

**Solution:**
```bash
# Update submodules
git submodule update --init --recursive

# Clean and rebuild
./waf clean
./waf configure --board sitl
./waf plane
```

See **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** for comprehensive troubleshooting guide.

## Development Workflow

### Making Code Changes

1. Create feature branch: `git checkout -b my-feature`
2. Make code changes
3. Rebuild: `./waf plane`
4. Test in SITL: `cd ArduPlane && sim_vehicle.py`
5. Commit changes: `git commit -am "Description of changes"`

### Testing Changes

Always test in SITL before hardware:

```bash
cd ~/ardupilot/ArduPlane
sim_vehicle.py

# In MAVProxy console, test your changes
```

## Additional Resources

- **[ArduPilot Build Guide](https://ardupilot.org/dev/docs/building-setup-linux.html)** [1] - Official build instructions
- **[WAF Build System](https://ardupilot.org/dev/docs/waf.html)** [2] - WAF documentation
- **[Supported Boards](https://ardupilot.org/plane/docs/common-autopilots.html)** [3] - Hardware compatibility
- **[Developer Documentation](https://ardupilot.org/dev/)** [4] - Full developer docs
- **[Contributing Guide](https://ardupilot.org/dev/docs/contributing.html)** [5] - How to contribute code

### Community Support

- [ArduPilot Discord](https://ardupilot.org/discord) - Real-time chat support
- [Discourse Forums](https://discuss.ardupilot.org/) - Community Q&A
- [GitHub Issues](https://github.com/ArduPilot/ardupilot/issues) - Bug reports

## Next Steps

After successfully building ArduPilot:

1. **Run SITL** - Test your build in simulation ([SITL Guide](../SITL_Mission_Plans/))
2. **Explore Codebase** - Understand ArduPilot architecture ([Sensor Drivers](../Sensor_Drivers/))
3. **Make Contributions** - Learn the contribution workflow ([Advanced Topics](../Advanced_Topics/Code_Contribution_Workflow/))

---

**Sources:**

[1] https://ardupilot.org/dev/docs/building-setup-linux.html
[2] https://ardupilot.org/dev/docs/waf.html
[3] https://ardupilot.org/plane/docs/common-autopilots.html
[4] https://ardupilot.org/dev/
[5] https://ardupilot.org/dev/docs/contributing.html
