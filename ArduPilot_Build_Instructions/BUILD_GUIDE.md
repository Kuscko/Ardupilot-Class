# ArduPilot Build Guide — Plane 4.5.7

## Quick Start Summary

This guide walks you through building ArduPilot Plane 4.5.7 from source in WSL2/Ubuntu.

**Target Version:** Plane 4.5.7 (commit: 0358a9c210bc6c965006f5d6029239b7033616df)

---

## Prerequisites

### Windows System Requirements
- Windows 10/11 with WSL2 enabled
- At least 10GB free disk space
- 8GB+ RAM recommended

### Enable WSL2

1. Open PowerShell as Administrator and run:
   ```powershell
   wsl --install
   ```

2. Or manually enable via Control Panel:
   - Control Panel → Programs → Turn Windows features on or off
   - Check "Windows Subsystem for Linux"
   - Restart when prompted

3. Install Ubuntu 24.04 LTS:
   - Open Microsoft Store
   - Search "Ubuntu 24.04 LTS"
   - Click Install
   - Launch Ubuntu and create username/password

---

## Step 1: Initial System Setup

Open your WSL2 Ubuntu terminal and run:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential build tools
sudo apt install -y git python3 python3-pip
```

---

## Step 2: Clone ArduPilot Repository

```bash
# Navigate to home directory (IMPORTANT: Do NOT use /mnt/c/)
cd ~

# Clone the repository
git clone --recursive https://github.com/ArduPilot/ardupilot.git

# Enter the directory
cd ardupilot

# Fetch all tags
git fetch --tags

# Checkout Plane 4.5.7
git checkout Plane-4.5.7

# Verify you're on the correct version
git log -1
# Should show: commit 0358a9c210bc6c965006f5d6029239b7033616df

# Update submodules
git submodule update --init --recursive
```

> **CRITICAL:** Always clone and build inside the WSL filesystem (`~/ardupilot`), NOT under `/mnt/c/`. Building from Windows-mounted drives is significantly slower.

---

## Step 3: Create Virtual Environment (Recommended)

Using a virtual environment isolates Python packages and prevents system conflicts:

```bash
# Create virtual environment
python3 -m venv ~/.venv-ardupilot

# Activate virtual environment
source ~/.venv-ardupilot/bin/activate
```

**For permanent activation**, add to `~/.bashrc`:
```bash
# Auto-activate ArduPilot virtual environment
if [ -f "$HOME/.venv-ardupilot/bin/activate" ]; then
    if ! type deactivate &> /dev/null; then
        source "$HOME/.venv-ardupilot/bin/activate"
    fi
fi
```

---

## Step 4: Patch Prerequisites Script

Patch the ArduPilot prerequisites script for venv compatibility:

```bash
cd ~/ardupilot

# Backup original script
cp ./Tools/environment_install/install-prereqs-ubuntu.sh ./Tools/environment_install/install-prereqs-ubuntu.sh.backup

# Get Ubuntu codename (noble for 24.04)
UBUNTU_CODENAME=$(lsb_release -sc)

# Apply patches
sed -i 's/python-argparse//g' ./Tools/environment_install/install-prereqs-ubuntu.sh
sed -i 's/PIP_USER_ARGUMENT="--user"/PIP_USER_ARGUMENT=""/g' ./Tools/environment_install/install-prereqs-ubuntu.sh
sed -i 's/pip3 install --user/pip3 install/g' ./Tools/environment_install/install-prereqs-ubuntu.sh
sed -i 's/pip install --user/pip install/g' ./Tools/environment_install/install-prereqs-ubuntu.sh
sed -i "s/if \[ \$RELEASE_CODENAME != \"mantic\" \]; then/if [ \$RELEASE_CODENAME != \"mantic\" ] \&\& [ \$RELEASE_CODENAME != \"noble\" ] \&\& [ \$RELEASE_CODENAME != \"$UBUNTU_CODENAME\" ]; then/g" ./Tools/environment_install/install-prereqs-ubuntu.sh
```

**What these patches do:**
- Remove obsolete `python-argparse` package
- Install packages in venv instead of `--user`
- Add support for Ubuntu 24.04 (noble)

---

## Step 5: Install Build Prerequisites

```bash
# Make sure venv is activated
source ~/.venv-ardupilot/bin/activate

# Run the patched prerequisites installer
cd ~/ardupilot
./Tools/environment_install/install-prereqs-ubuntu.sh -y

# Reload your profile to apply environment changes
source ~/.profile
source ~/.bashrc

# Install Python MAVLink packages
pip install --upgrade pip pymavlink mavproxy
```

This script installs:
- ARM cross-compiler toolchains
- Python development packages (including python3-wxgtk4.0)
- MAVProxy (ground control software)
- Build tools and libraries

---

## Step 6: Configure GUI Module Support

**CRITICAL for MAVProxy console and map windows:**

MAVProxy modules require wxPython, which is difficult to build from source. Instead, make the system wxPython accessible to your virtual environment:

```bash
# Add system packages to venv path
echo "import site; site.addsitedir('/usr/lib/python3/dist-packages')" > ~/.venv-ardupilot/lib/python3.12/site-packages/system_packages.pth

# Verify wxPython is accessible
python -c "import wx; print('wxPython version:', wx.__version__)"
```

**Expected output:** `wxPython version: 4.2.1`

If wxPython is not found:
```bash
sudo apt install -y python3-wxgtk4.0 python3-matplotlib python3-opencv
```

---

## Step 7: Build ArduPilot for SITL

```bash
# Navigate to ArduPilot directory
cd ~/ardupilot

# Configure for SITL (Software-In-The-Loop simulation)
./waf configure --board sitl

# Build ArduPlane
./waf plane
```

**First build will take 5-15 minutes.** Subsequent builds are much faster (incremental compilation).

### Successful Build Output

You should see:
```
Build commands will be stored in build/sitl/compile_commands.json
'plane' finished successfully (XXX.XXXs)
```

Binary location: `~/ardupilot/build/sitl/bin/arduplane`

---

## Step 8: Configure Display (WSLg or VcXsrv)

**For Windows 11 / WSL 2.0+ (Recommended - WSLg):**

WSLg works out of the box! Just make sure your `~/.bashrc` does NOT override DISPLAY:

```bash
# Verify DISPLAY is set automatically
echo $DISPLAY  # Should show: :0

# Make sure these lines are commented out in ~/.bashrc:
# export DISPLAY=$(grep -m 1 nameserver /etc/resolv.conf | awk '{print $2}'):0
```

**For Windows 10 (VcXsrv/XLaunch):**

See [setup_x_server.md](../Installation_Scripts/setup_x_server.md) for detailed VcXsrv configuration.

---

## Step 9: Build for Hardware (Optional)

To build for actual flight controller hardware:

```bash
# List available boards
../waf list_boards

# Configure for your board (example: CubeOrangePlus)
../waf configure --board CubeOrangePlus

# Build
../waf plane
```

Output location: `~/ardupilot/build/CubeOrangePlus/bin/arduplane.apj`

### Common Hardware Boards
- `CubeOrangePlus` - Hex Cube Orange+
- `Pixhawk6X` - Holybro Pixhawk 6X
- `MatekH743` - Matek H743 flight controller
- `KakuteH7` - Holybro Kakute H7

---

## Step 10: Verify SITL Installation

```bash
# Activate venv (if not already active)
source ~/.venv-ardupilot/bin/activate

# Start SITL to verify everything works
cd ~/ardupilot
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
```

**Expected behavior:**
- **Three windows** should open:
  1. ArduPlane terminal (simulator)
  2. MAVProxy console (command interface)
  3. Map window (aircraft position)
- After a few seconds: "GPS: 3D Fix" in the console
- Map shows aircraft at CMAC location

**If only 1 window opens:** MAVProxy modules failed to load. Go back to Step 6.

**If "Can't open display" error:** Check Step 8 for display configuration.

Press Ctrl+C to exit SITL.

---

## Common Build Issues & Solutions

### Issue: Submodule Errors

**Symptoms:** Build fails with missing headers or "No such file or directory"

**Solution:**
```bash
cd ~/ardupilot
git submodule update --init --recursive
```

### Issue: Python Package Conflicts

**Symptoms:** `ModuleNotFoundError` or version conflicts

**Solution:**
```bash
python3 -m pip install --user --upgrade pymavlink mavproxy
# If issues persist:
python3 -m pip install --user --force-reinstall pymavlink mavproxy
```

### Issue: Slow Build Times

**Symptoms:** Build takes more than 20 minutes

**Solution:**
- Verify you're building in WSL filesystem (`~/ardupilot`), NOT `/mnt/c/`
- Check location: `pwd` should show `/home/username/ardupilot`
- If in `/mnt/c/`, clone again in home directory

### Issue: WAF Configuration Fails

**Symptoms:** `./waf configure` fails with errors

**Solution:**
```bash
# Clean build directory
./waf distclean

# Re-run installation script
./Tools/environment_install/install-prereqs-ubuntu.sh -y

# Reload profile
. ~/.profile

# Try configure again
./waf configure --board sitl
```

### Issue: Permission Denied

**Symptoms:** Cannot execute scripts or binaries

**Solution:**
```bash
# Make scripts executable
chmod +x Tools/autotest/sim_vehicle.py
chmod +x waf
```

### Issue: MAVProxy Modules Not Loading

**Symptoms:**
```
Failed to load module: No module named 'console'
Failed to load module: No module named 'map'
```
Only ArduPlane terminal appears, no console or map windows.

**Solution:**
Follow Step 6 to configure GUI module support. This makes system wxPython accessible to the venv.

### Issue: Display/X11 Errors in SITL

**Symptoms:** "Can't open display" error

**Solution:**

**For Windows 11 (WSLg):**
```bash
# Make sure DISPLAY override is commented out in ~/.bashrc
source ~/.bashrc
echo $DISPLAY  # Should show :0
```

**For Windows 10 (VcXsrv):**
See [setup_x_server.md](../Installation_Scripts/setup_x_server.md) - VcXsrv must be started with `-listen tcp` flag for WSL2.

---

## Build Commands Reference

| Command | Purpose |
|---------|---------|
| `./waf configure --board sitl` | Configure for simulation |
| `./waf plane` | Build ArduPlane |
| `./waf copter` | Build ArduCopter |
| `./waf clean` | Clean build artifacts |
| `./waf distclean` | Complete clean (removes configuration) |
| `./waf list_boards` | Show available hardware boards |
| `./waf --help` | Show all build options |

---

## Directory Structure

```
~/ardupilot/
├── ArduPlane/          # Plane-specific code
├── ArduCopter/         # Copter-specific code
├── libraries/          # Shared libraries (~80% of codebase)
│   ├── AP_GPS/         # GPS drivers
│   ├── AP_Baro/        # Barometer drivers
│   ├── AP_Compass/     # Compass drivers
│   ├── AP_NavEKF3/     # Extended Kalman Filter
│   └── ...
├── Tools/              # Build and test tools
│   ├── autotest/       # SITL scripts
│   └── environment_install/  # Installation scripts
└── build/              # Build outputs
    ├── sitl/           # SITL binaries
    └── [BOARD]/        # Hardware binaries
```

---

## Next Steps

After successful build:
1. [ ] Start SITL and familiarize yourself with MAVProxy
2. [ ] Review [SITL Mission Plans](../SITL_Mission_Plans/) for flight testing
3. [ ] Explore parameter configuration with Mission Planner or QGroundControl
4. [ ] Try example [Lua Scripts](../Lua_Scripts/)

---

## Additional Resources

- [ArduPilot Dev Docs: Building the Code](https://ardupilot.org/dev/docs/building-the-code.html)
- [ArduPilot Dev Docs: SITL](https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html)
- [Main Onboarding Guide](../Onboarding_Documentation/ArduPilot_Onboarding_Guide.md)
- [ArduPilot GitHub](https://github.com/ArduPilot/ardupilot)
- [ArduPilot Discourse Forum](https://discuss.ardupilot.org/)

---

**Last Updated:** 2026-02-06
**ArduPilot Version:** Plane 4.5.7 (commit 0358a9c210bc)
**Verified:** Ubuntu 24.04 LTS with Python 3.12.3
