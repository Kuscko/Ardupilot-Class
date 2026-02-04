# Automated Installation Scripts

## Overview

These scripts automate the installation of ArduPilot Plane 4.5.7 development environment on Ubuntu 22.04/WSL2, including all dependencies, build tools, Python packages, and ground station software [1]. The scripts eliminate manual configuration steps and ensure consistent environment setup across different systems.

## Prerequisites

Before running installation scripts, ensure you have:

- Ubuntu 22.04 LTS (native Linux or WSL2 on Windows)
- Internet connection (downloads ~500MB of packages)
- Sudo privileges (for package installation)
- 10GB+ free disk space

## What You'll Learn

By completing this module, you will:

- Use automated scripts to set up ArduPilot development environment
- Understand what dependencies ArduPilot requires and why
- Configure X server for WSL2 to display SITL windows
- Troubleshoot common installation issues
- Verify successful installation and test your environment

## Quick Start

### Option 1: Complete Installation (Recommended)

This script installs everything needed for ArduPilot development:

```bash
cd ~/Desktop/Work/AEVEX/Installation_Scripts
chmod +x install_ardupilot_plane_4.5.7.sh
./install_ardupilot_plane_4.5.7.sh
```

**What it installs:**
- Build tools (gcc, g++, make, cmake)
- Python 3 and development packages
- ArduPilot build dependencies
- ArduPilot Plane 4.5.7 source code
- MAVProxy ground station
- pymavlink library
- Supporting Python packages

**Time:** 15-30 minutes (depending on connection speed)

### Option 2: Individual Components

Install only specific components:

```bash
# Install only MAVProxy
chmod +x install_mavproxy.sh
./install_mavproxy.sh
```

## Complete Installation Guide

See **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** for comprehensive step-by-step instructions covering:

- Pre-installation system preparation
- Running installation scripts
- Environment variable configuration
- Post-installation verification
- Troubleshooting failed installations

## Hands-On Practice

### Exercise 1: Fresh Installation

Perform a complete installation and verify success:

```bash
# Step 1: Run installer
cd ~/Desktop/Work/AEVEX/Installation_Scripts
./install_ardupilot_plane_4.5.7.sh

# Step 2: Reload shell environment
source ~/.bashrc

# Step 3: Verify ArduPilot installation
cd ~/ardupilot
git log --oneline -1
# Should show: 0358a9c2 ArduPlane: update version to 4.5.7

# Step 4: Verify MAVProxy
sim_vehicle.py --version
# Should show: sim_vehicle.py version ...

# Step 5: Test SITL
cd ~/ardupilot/ArduPlane
sim_vehicle.py
```

**Expected Result:** SITL starts successfully with console, map, and MAVProxy windows

### Exercise 2: Validate Python Environment

Check that all Python packages are correctly installed:

```bash
# List MAVLink-related packages
pip3 list | grep -E '(pymavlink|MAVProxy|dronekit)'

# Test pymavlink import
python3 -c "import pymavlink; print('pymavlink:', pymavlink.__version__)"

# Test MAVProxy import
python3 -c "from MAVProxy import mavproxy; print('MAVProxy installed')"
```

**Expected Output:**
```
pymavlink           2.4.xx
MAVProxy            1.8.xx
pymavlink: 2.4.xx
MAVProxy installed
```

### Exercise 3: Verify Build System

Test that the build system works correctly:

```bash
cd ~/ardupilot

# Check WAF is executable
./waf --version

# Configure for SITL
./waf configure --board sitl

# Build ArduPlane (tests compiler and dependencies)
./waf plane

# Verify build output
ls -lh build/sitl/bin/arduplane
```

**Expected Result:** Successfully configured and built ArduPlane binary

## X Server Setup for WSL2

Windows users running WSL2 need an X server to display SITL map and console windows.

### Quick Setup

1. Install VcXsrv or X410 on Windows
2. Configure DISPLAY variable in WSL2
3. Test X11 forwarding

See **[setup_x_server.md](setup_x_server.md)** for detailed instructions with screenshots.

### Verify X Server

Test that X11 forwarding works:

```bash
# Check DISPLAY variable is set
echo $DISPLAY
# Should show: localhost:0 or similar

# Test X11 with simple application
sudo apt-get install -y x11-apps
xeyes &
# Should display eyes window on Windows desktop
```

## Key Concepts

### ArduPilot Dependencies

The installation script installs several categories of dependencies [1]:

**Build Tools:**
- GCC/G++ compilers for C/C++ code
- Make and CMake for build automation
- WAF build system (included in ArduPilot)

**Python Environment:**
- Python 3.x interpreter
- pip package manager
- Development headers (python3-dev)

**ArduPilot-Specific:**
- pymavlink - MAVLink protocol library
- MAVProxy - Ground control station
- future, lxml - Python compatibility libraries

**System Libraries:**
- libxml2, libxslt - XML processing
- libtool, pkg-config - Build configuration
- git - Version control

### Installation Script Logic

The scripts handle several edge cases:

1. **Ubuntu Version Detection:** Checks Ubuntu version to avoid deprecated packages
2. **Package Availability:** Skips packages not available in newer Ubuntu versions
3. **Existing Installations:** Detects and updates existing ArduPilot installations
4. **Error Handling:** Continues even if individual package installations fail

## Script Contents

| Script | Purpose | Time | Components |
|--------|---------|------|------------|
| install_ardupilot_plane_4.5.7.sh | Complete environment setup | 15-30 min | All dependencies, ArduPilot source, MAVProxy |
| install_mavproxy.sh | MAVProxy only | 5 min | MAVProxy and pymavlink |

## Common Issues

### Issue: "python-argparse" package not found

**Symptom:** Installation script reports error about python-argparse

**Cause:** Package deprecated in Ubuntu 24.04+ (included in Python 3 by default)

**Solution:** Script automatically detects and skips this package on newer Ubuntu versions. No action required.

### Issue: X server windows don't appear (WSL2)

**Symptom:** SITL starts but no map or console windows appear

**Solutions:**
1. Verify X server is running on Windows
2. Check DISPLAY variable: `echo $DISPLAY`
3. Add to ~/.bashrc: `export DISPLAY=:0`
4. Reload shell: `source ~/.bashrc`
5. See [setup_x_server.md](setup_x_server.md) for complete guide

### Issue: "Permission denied" when running script

**Symptom:** Cannot execute installation script

**Solution:**
```bash
chmod +x install_ardupilot_plane_4.5.7.sh
./install_ardupilot_plane_4.5.7.sh
```

### Issue: pip install fails with "externally-managed-environment"

**Symptom:** pip reports environment is externally managed (Ubuntu 23.04+)

**Solutions:**
```bash
# Option 1: Use system package manager (preferred)
sudo apt-get install python3-pymavlink

# Option 2: Use virtual environment
python3 -m venv ~/ardupilot-env
source ~/ardupilot-env/bin/activate
pip3 install pymavlink MAVProxy

# Option 3: User install (if script doesn't already use --user)
pip3 install --user pymavlink MAVProxy
```

### Issue: MAVProxy commands not found after installation

**Symptom:** `sim_vehicle.py` or `mavproxy.py` not found

**Solution:**
```bash
# Add Python scripts to PATH
echo 'export PATH=$PATH:$HOME/.local/bin' >> ~/.bashrc
source ~/.bashrc

# Verify
which sim_vehicle.py
```

See **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** for complete troubleshooting guide.

## Post-Installation Verification

After installation, verify everything works:

```bash
# 1. Check ArduPilot version
cd ~/ardupilot
git log --oneline -1

# 2. Check build system
./waf configure --board sitl
./waf plane

# 3. Check Python packages
python3 -c "import pymavlink; print('OK')"

# 4. Run SITL test
cd ArduPlane
sim_vehicle.py --console --map
# Should start successfully
```

**All checks passed?** You're ready to start developing with ArduPilot!

## Additional Resources

### Official Documentation

- **[ArduPilot Linux Installation](https://ardupilot.org/dev/docs/building-setup-linux.html)** [1] - Official installation guide
- **[MAVProxy Installation](https://ardupilot.org/mavproxy/docs/getting_started/download_and_installation.html)** [2] - MAVProxy setup
- **[WSL2 Setup](https://learn.microsoft.com/en-us/windows/wsl/install)** [3] - Microsoft WSL2 documentation
- **[SITL Setup](https://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html)** [4] - SITL environment configuration

### Python Package Documentation

- **[pymavlink Documentation](https://www.ardusub.com/developers/pymavlink.html)** - Python MAVLink library
- **[MAVProxy Documentation](https://ardupilot.org/mavproxy/)** - Ground control station guide
- **[pip User Guide](https://pip.pypa.io/en/stable/user_guide/)** - Python package installation

### Community Support

- [ArduPilot Discord](https://ardupilot.org/discord) - Real-time installation help
- [Discourse Forums: Installation](https://discuss.ardupilot.org/c/installation/16) - Community Q&A
- [GitHub Issues](https://github.com/ArduPilot/ardupilot/issues) - Report installation bugs

## Next Steps

After successful installation:

1. **Build ArduPilot** - Compile from source ([Build Instructions](../ArduPilot_Build_Instructions/))
2. **Run SITL** - Test in simulation ([SITL Mission Plans](../SITL_Mission_Plans/))
3. **Explore Code** - Understand ArduPilot architecture ([Sensor Drivers](../Sensor_Drivers/))
4. **Learn MAVLink** - Master communication protocol ([MAVLink Guide](../MAVLink_MavlinkRouter/))

---

**Sources:**

[1] https://ardupilot.org/dev/docs/building-setup-linux.html
[2] https://ardupilot.org/mavproxy/docs/getting_started/download_and_installation.html
[3] https://learn.microsoft.com/en-us/windows/wsl/install
[4] https://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html
