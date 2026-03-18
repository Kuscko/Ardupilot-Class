# Installation Guide

Complete step-by-step guide for ArduPilot Plane 4.5.7 installation on Ubuntu 22.04 LTS (Jammy Jellyfish).

> **Platform note:** Ubuntu 22.04 (jammy) is natively supported by ArduPilot's `install-prereqs-ubuntu.sh`. No virtual environment or script patching is required.

## Automated Installation

**Recommended method:**

```bash
cd ~
chmod +x install_ardupilot_plane_4.5.7.sh
./install_ardupilot_plane_4.5.7.sh
```

Time: 15-30 minutes

---

## Manual Installation

For troubleshooting or custom setups:

### 1. System Setup

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-pip lsb-release
```

### 2. Clone Repository

```bash
cd ~
git clone --recursive https://github.com/ArduPilot/ardupilot.git
cd ardupilot
git checkout Plane-4.5.7
git submodule update --init --recursive
```

### 3. Install Prerequisites

Ubuntu 22.04 (jammy) is fully supported by ArduPilot's prereqs script — run it directly:

```bash
cd ~/ardupilot
./Tools/environment_install/install-prereqs-ubuntu.sh -y

# Reload shell profile
source ~/.profile
source ~/.bashrc
```

This installs all build tools, Python packages (pymavlink, MAVProxy), and `python3-wxgtk4.0` for MAVProxy's console and map windows.

### 4. Upgrade Python Packages

```bash
python3 -m pip install --user --upgrade pymavlink mavproxy
```

### 5. Build ArduPlane

```bash
cd ~/ardupilot
./waf configure --board sitl
./waf plane
```

### 6. Configure Display for GUI Windows

**For Windows 11 / WSL 2.0+ (WSLg):**

WSLg works out of the box - no configuration needed! Just make sure your `~/.bashrc` does NOT override the DISPLAY variable.

```bash
# Make sure these lines are commented out or not in ~/.bashrc:
# export DISPLAY=$(grep -m 1 nameserver /etc/resolv.conf | awk '{print $2}'):0

# WSLg automatically sets DISPLAY to :0
echo $DISPLAY  # Should show: :0
```

**For Windows 10 (VcXsrv/XLaunch):**

See [setup_x_server.md](setup_x_server.md) for detailed VcXsrv setup instructions.

### 7. Test SITL

```bash
cd ~/ardupilot
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
```

**Expected Result:**
- 3 windows should open: ArduPlane terminal, MAVProxy console, and Map
- After a few seconds: "GPS: 3D Fix" in console
- Map shows aircraft position

If only 1 window opens, see [setup_x_server.md](setup_x_server.md) for troubleshooting.

---

## Verification

### Check Version

```bash
cd ~/ardupilot
git log -1
# Expected commit: 0358a9c210bc6c965006f5d6029239b7033616df
```

### Check Binary

```bash
ls -lh ~/ardupilot/build/sitl/bin/arduplane
# Should be ~10-20MB
```

### Test Python Packages

```bash
python3 -c "import pymavlink; print('pymavlink OK')"
python3 -c "import wx; print('wxPython OK')"
mavproxy.py --version
```

### Test MAVProxy Modules

```bash
python3 -c "from MAVProxy.modules import mavproxy_console; print('✓ Console module')"
python3 -c "from MAVProxy.modules import mavproxy_map; print('✓ Map module')"
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Permission denied | `chmod +x *.sh` |
| Running from /mnt/c/ | Move to WSL home: `cd ~` |
| Submodule errors | `git submodule update --init --recursive` |
| Compiler not found | Re-run prerequisites script |
| Only 1 window appears | See "Only One SITL Window Opens" below |
| Can't open display error | See [setup_x_server.md](setup_x_server.md) |

### MAVProxy Modules Not Loading

**Issue:**

```text
Failed to load module: No module named 'console'
Failed to load module: No module named 'map'
```

**Cause:** `python3-wxgtk4.0` was not installed.

**Solution:**

```bash
sudo apt install -y python3-wxgtk4.0
```

This is normally handled automatically by `install-prereqs-ubuntu.sh` on jammy. If it was skipped, run the prereqs script again or install directly.

### Only One SITL Window Opens

**Issue:** Only ArduPlane terminal appears, no console or map windows.

**Cause:** MAVProxy failed to load `wx` (wxPython not installed).

**Solution:**

1. `sudo apt install -y python3-wxgtk4.0`
2. Verify: `python3 -c "import wx"`
3. Restart SITL

### WSL1 vs WSL2

**Always use WSL2.** WSL1 has slower performance and compatibility issues.

Check version:
```bash
wsl --list --verbose
```

Upgrade to WSL2 (Windows PowerShell as Admin):
```powershell
wsl --set-version Ubuntu-22.04 2
```

---

## Updates

### Update ArduPilot

```bash
cd ~/ardupilot
git fetch --all
git checkout Plane-4.5.7
git submodule update --init --recursive
```

### Update Python Packages

```bash
python3 -m pip install --user --upgrade pymavlink mavproxy
```

### Rebuild

```bash
cd ~/ardupilot
./waf clean
./waf plane
```

---

## Directory Structure

```
~/ardupilot/
├── ArduPlane/           # Plane-specific code
├── libraries/           # Shared libraries
├── Tools/
│   ├── autotest/
│   │   └── sim_vehicle.py
│   └── environment_install/
├── build/sitl/bin/
│   └── arduplane        # SITL binary
└── waf                  # Build system
```

---

## Next Steps

1. Test SITL and verify all windows open
2. Learn MAVProxy commands
3. Try flight modes: MANUAL, FBWA, RTL, AUTO
4. Create a simple mission plan
5. Explore Lua scripting

---

**Last Updated:** 2026-03-17
**Target:** ArduPilot Plane 4.5.7
**Platform:** Ubuntu 22.04 LTS (Jammy Jellyfish)
