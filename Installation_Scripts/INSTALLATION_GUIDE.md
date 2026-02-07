# Installation Guide

Complete step-by-step guide for ArduPilot Plane 4.5.7 installation.

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
sudo apt install -y git python3 python3-pip python3-venv
```

### 2. Clone Repository

```bash
cd ~
git clone --recursive https://github.com/ArduPilot/ardupilot.git
cd ardupilot
git checkout Plane-4.5.7
git submodule update --init --recursive
```

### 3. Create Virtual Environment

```bash
python3 -m venv ~/.venv-ardupilot
source ~/.venv-ardupilot/bin/activate
```

**Important:** Activate venv BEFORE installing prerequisites to ensure packages install in the venv.

### 4. Patch Prerequisites Script for venv Compatibility

```bash
cd ~/ardupilot

# Backup the original script
cp ./Tools/environment_install/install-prereqs-ubuntu.sh ./Tools/environment_install/install-prereqs-ubuntu.sh.backup

# Get Ubuntu codename
UBUNTU_CODENAME=$(lsb_release -sc)

# Apply patches for venv compatibility
sed -i 's/python-argparse//g' ./Tools/environment_install/install-prereqs-ubuntu.sh
sed -i 's/PIP_USER_ARGUMENT="--user"/PIP_USER_ARGUMENT=""/g' ./Tools/environment_install/install-prereqs-ubuntu.sh
sed -i 's/pip3 install --user/pip3 install/g' ./Tools/environment_install/install-prereqs-ubuntu.sh
sed -i 's/pip install --user/pip install/g' ./Tools/environment_install/install-prereqs-ubuntu.sh
sed -i "s/if \[ \$RELEASE_CODENAME != \"mantic\" \]; then/if [ \$RELEASE_CODENAME != \"mantic\" ] \&\& [ \$RELEASE_CODENAME != \"noble\" ] \&\& [ \$RELEASE_CODENAME != \"$UBUNTU_CODENAME\" ]; then/g" ./Tools/environment_install/install-prereqs-ubuntu.sh
```

### 5. Install Prerequisites

```bash
# Run the patched prerequisites installer
./Tools/environment_install/install-prereqs-ubuntu.sh -y

# Reload shell profile
source ~/.profile
source ~/.bashrc

# Install Python packages
pip install --upgrade pip pymavlink mavproxy
```

### 6. Configure GUI Module Support for MAVProxy

**CRITICAL:** MAVProxy console and map modules require wxPython, which is difficult to build from source. Instead, make system wxPython accessible to the virtual environment:

```bash
# Add system packages to venv path
echo "import site; site.addsitedir('/usr/lib/python3/dist-packages')" > ~/.venv-ardupilot/lib/python3.12/site-packages/system_packages.pth

# Verify wxPython is accessible
python -c "import wx; print('wxPython version:', wx.__version__)"
```

If wxPython is not found, install it:
```bash
sudo apt install -y python3-wxgtk4.0 python3-matplotlib python3-opencv
```

### 7. Build ArduPlane

```bash
cd ~/ardupilot
./waf configure --board sitl
./waf plane
```

### 8. Configure Display for GUI Windows

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

### 9. Test SITL

```bash
source ~/.venv-ardupilot/bin/activate
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
source ~/.venv-ardupilot/bin/activate
python -c "import pymavlink; print('pymavlink OK')"
python -c "import wx; print('wxPython OK')"
mavproxy.py --version
```

### Test MAVProxy Modules

```bash
python -c "from MAVProxy.modules import mavproxy_console; print('✓ Console module')"
python -c "from MAVProxy.modules import mavproxy_map; print('✓ Map module')"
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Permission denied | `chmod +x *.sh` |
| Running from /mnt/c/ | Move to WSL home: `cd ~` |
| Python packages fail | Activate venv: `source ~/.venv-ardupilot/bin/activate` |
| Submodule errors | `git submodule update --init --recursive` |
| Compiler not found | Re-run prerequisites script |
| MAVProxy modules not loading | See "MAVProxy Modules Not Loading" below |
| Only 1 window appears | See "Configure GUI Module Support" in Step 6 |
| Can't open display error | See [setup_x_server.md](setup_x_server.md) |

### python-argparse Error

**Issue:** Package 'python-argparse' has no installation candidate

**Cause:** argparse is built into Python 3.2+. The separate package is obsolete.

**Solution:** Apply the patch in Step 4 before running the prerequisites installer.

### MAVProxy Modules Not Loading

**Issue:**
```
Failed to load module: No module named 'console'
Failed to load module: No module named 'map'
```

**Cause:** wxPython is not accessible in the virtual environment.

**Solution:** Follow Step 6 to configure GUI module support. This creates a `.pth` file that makes system wxPython accessible to the venv.

### Only One SITL Window Opens

**Issue:** Only ArduPlane terminal appears, no console or map windows.

**Cause:** MAVProxy modules failed to load (see above).

**Solution:**
1. Follow Step 6 to configure GUI module support
2. Verify: `python -c "import wx"`
3. If wxPython not installed: `sudo apt install python3-wxgtk4.0`
4. Restart SITL

### WSL1 vs WSL2

**Always use WSL2.** WSL1 has slower performance and compatibility issues.

Check version:
```bash
wsl --list --verbose
```

Upgrade to WSL2 (Windows PowerShell as Admin):
```powershell
wsl --set-version Ubuntu-24.04 2
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
source ~/.venv-ardupilot/bin/activate
pip install --upgrade pymavlink mavproxy
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

**Last Updated:** 2026-02-06
**Target:** ArduPilot Plane 4.5.7
