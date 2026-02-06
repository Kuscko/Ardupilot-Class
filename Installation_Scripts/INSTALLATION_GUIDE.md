# Installation Scripts Guide

## Overview

This folder contains automated installation scripts and guides for setting up ArduPilot Plane 4.5.7 development environment.

## Quick Start

### Automated Installation

Run the main installation script in WSL2:

```bash
cd ~
# Download or copy the script to your WSL home directory
chmod +x install_ardupilot_plane_4.5.7.sh
./install_ardupilot_plane_4.5.7.sh
```

This script will:
- Update system packages
- Install dependencies
- Clone ArduPilot repository
- Checkout Plane 4.5.7
- Install prerequisites
- Build ArduPlane for SITL
- Verify installation

**Time estimate:** 15-30 minutes (depending on internet speed and system performance)

---

## Available Scripts

### 1. `install_ardupilot_plane_4.5.7.sh`

**Purpose:** Complete automated installation of ArduPilot Plane 4.5.7

**Usage:**
```bash
chmod +x install_ardupilot_plane_4.5.7.sh
./install_ardupilot_plane_4.5.7.sh
```

**What it does:**
- System updates
- Dependency installation
- Repository cloning
- Version checkout and verification
- Prerequisite installation
- SITL build

**Requirements:**
- Ubuntu 22.04 LTS (WSL2 recommended)
- Internet connection
- ~10GB disk space
- Sudo privileges

---

### 2. `install_mavproxy.sh`

**Purpose:** Install or update MAVProxy and Python dependencies

**Usage:**
```bash
chmod +x install_mavproxy.sh
./install_mavproxy.sh
```

**Use this when:**
- MAVProxy isn't working
- You need to update to latest MAVProxy version
- Python package conflicts occur

---

### 3. `setup_x_server.md`

**Purpose:** Guide for setting up X server for WSL2 graphical applications

**Follow this when:**
- SITL map window doesn't appear
- You get "cannot open display" errors
- You want graphical output from SITL

---

## Manual Installation Steps

If you prefer manual installation or need to troubleshoot:

### Step 1: System Setup
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-pip python3-venv
```

### Step 2: Clone Repository
```bash
cd ~
git clone --recursive https://github.com/ArduPilot/ardupilot.git
cd ardupilot
git fetch --tags
git checkout Plane-4.5.7
git submodule update --init --recursive
```

### Step 3: Create Virtual Environment
```bash
# Create and activate virtual environment BEFORE installing prerequisites
# This ensures all Python packages go into the venv
python3 -m venv ~/.venv-ardupilot
source ~/.venv-ardupilot/bin/activate
```

### Step 4: Install Prerequisites
```bash
cd ~/ardupilot
# With venv activated, all Python packages will install to venv
./Tools/environment_install/install-prereqs-ubuntu.sh -y
. ~/.profile

# Install additional packages
pip install --upgrade pip pymavlink mavproxy
```

### Step 5: Build
```bash
cd ~/ardupilot/ArduPlane
../waf configure --board sitl
../waf plane
```

### Step 6: Test
```bash
# Virtual environment should still be active from Step 3
# If not, activate it:
source ~/.venv-ardupilot/bin/activate

# Run SITL
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
```

---

## Common Installation Issues

### Issue: Script fails with "Permission denied"

**Fix:**
```bash
chmod +x *.sh
```

### Issue: "Not in WSL filesystem" warning

**Problem:** Running from `/mnt/c/` (Windows filesystem)

**Fix:** Move to WSL home directory:
```bash
cd ~
# Copy script here and run
```

### Issue: Python package installation fails

**Fix:** Use the virtual environment:
```bash
# Activate virtual environment
source ~/.venv-ardupilot/bin/activate

# Update pip and install packages
pip install --upgrade pip
pip install --upgrade pymavlink mavproxy
```

### Issue: Build fails with submodule errors

**Fix:**
```bash
cd ~/ardupilot
git submodule update --init --recursive
```

### Issue: "arm-none-eabi-g++ not found"

**Fix:**
```bash
cd ~/ardupilot
./Tools/environment_install/install-prereqs-ubuntu.sh -y
. ~/.profile
```

---

## Verifying Installation

### Check ArduPilot Version
```bash
cd ~/ardupilot
git log -1
# Should show commit: 0358a9c210bc6c965006f5d6029239b7033616df
```

### Check Binary Exists
```bash
ls -lh ~/ardupilot/build/sitl/bin/arduplane
# Should show the binary with size ~10-20MB
```

### Check MAVProxy
```bash
# Activate virtual environment
source ~/.venv-ardupilot/bin/activate

# Check MAVProxy version
mavproxy.py --version
# Should show MAVProxy version
```

### Test SITL
```bash
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
# Should start SITL with 3 windows
```

---

## Updating Installation

### Update ArduPilot Code
```bash
cd ~/ardupilot
git fetch --all
git checkout Plane-4.5.7
git submodule update --init --recursive
```

### Update Python Packages
```bash
# Activate virtual environment
source ~/.venv-ardupilot/bin/activate

# Update packages
pip install --upgrade pymavlink mavproxy
```

### Rebuild
```bash
cd ~/ardupilot/ArduPlane
../waf clean
../waf plane
```

---

## Python Package Reference

### Required Packages
- `pymavlink` - MAVLink message library
- `mavproxy` - Ground control station

### Optional Packages (for enhanced functionality)
- `matplotlib` - Plotting and visualization
- `scipy` - Scientific computing
- `opencv-python` - Computer vision (for some SITL features)

### Installation
```bash
# Activate virtual environment
source ~/.venv-ardupilot/bin/activate

# Required
pip install --upgrade pymavlink mavproxy

# Optional
pip install --upgrade matplotlib scipy opencv-python
```

---

## Known Issues and Solutions

### python-argparse Error

**Issue:** The ArduPilot install script fails with:

```text
Package 'python-argparse' has no installation candidate
```

**Cause:** The `argparse` module has been part of Python's standard library since Python 2.7 and Python 3.2. The separate `python-argparse` package is obsolete and no longer available in modern Python environments. This issue occurs regardless of Ubuntu version when using Python 3.4+.

**Solution:** The `install_ardupilot_plane_4.5.7.sh` script automatically removes `python-argparse` from the package list. If you're installing manually:

```bash
cd ~/ardupilot
# Backup the original script
cp Tools/environment_install/install-prereqs-ubuntu.sh Tools/environment_install/install-prereqs-ubuntu.sh.backup

# Remove python-argparse from the package list entirely
sed -i 's/python-argparse//g' Tools/environment_install/install-prereqs-ubuntu.sh

# Now run the install script
./Tools/environment_install/install-prereqs-ubuntu.sh -y
```

**Note:** This fix is automatically applied by the installation script regardless of your Ubuntu version, since the issue is related to Python version (3.4+), not the operating system.

### Deprecated Python Packages (2024-2025)

Some Python packages may show deprecation warnings during installation. This is normal and usually safe to ignore if the installation completes successfully.

**If installation fails due to deprecated packages:**
1. Check ArduPilot GitHub issues for known solutions
2. Visit ArduPilot Discourse forum
3. Update to latest supported packages

### WSL1 vs WSL2

**Always use WSL2** for ArduPilot development. WSL1 has:
- Slower filesystem performance
- Compatibility issues with some build tools
- No full Linux kernel support

**Check WSL version:**
```bash
wsl --list --verbose
# Should show VERSION 2
```

**Upgrade to WSL2:**
```powershell
# In Windows PowerShell (as Administrator)
wsl --set-version Ubuntu-22.04 2
```

---

## Directory Structure After Installation

```
~/ardupilot/
├── ArduPlane/              # Plane-specific code
├── libraries/              # Shared libraries
├── Tools/                  # Build and test tools
│   ├── autotest/           # SITL scripts
│   │   └── sim_vehicle.py  # Main SITL launcher
│   └── environment_install/
│       └── install-prereqs-ubuntu.sh
├── build/
│   └── sitl/
│       └── bin/
│           └── arduplane   # SITL binary
└── waf                     # Build system
```

---

## Next Steps After Installation

1. [ ] **Test SITL:** Start SITL and verify all windows open
2. [ ] **Learn MAVProxy:** Review MAVProxy commands
3. [ ] **Try Flight Modes:** Test MANUAL, FBWA, RTL, AUTO
4. [ ] **Review Parameters:** Explore parameter system
5. [ ] **Create Mission:** Build simple mission plan
6. [ ] **Try Lua Script:** Load and run example script

---

## Additional Resources

- [Main Build Guide](../ArduPilot_Build_Instructions/BUILD_GUIDE.md)
- [Troubleshooting Guide](../ArduPilot_Build_Instructions/TROUBLESHOOTING.md)
- [ArduPilot Onboarding Guide](../Onboarding_Documentation/ArduPilot_Onboarding_Guide.md)
- [ArduPilot Dev Docs](https://ardupilot.org/dev/)
- [ArduPilot Forum](https://discuss.ardupilot.org/)

---

**Last Updated:** 2026-02-05
**Target Version:** ArduPilot Plane 4.5.7
