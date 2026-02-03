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

3. Install Ubuntu 22.04 LTS:
   - Open Microsoft Store
   - Search "Ubuntu 22.04 LTS"
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

## Step 3: Install Build Prerequisites

```bash
# Run the ArduPilot prerequisite installer
cd ~/ardupilot
./Tools/environment_install/install-prereqs-ubuntu.sh -y

# Reload your profile to apply environment changes
. ~/.profile

# Install Python MAVLink packages
python3 -m pip install --user --upgrade pymavlink mavproxy
```

This script installs:
- ARM cross-compiler toolchains
- Python development packages
- MAVProxy (ground control software)
- Other build dependencies

**Note for Ubuntu 24.04+ users:** If you encounter an error about `python-argparse` not being available, apply this fix before running the installer:

```bash
cd ~/ardupilot
sed -i 's/if \[ $RELEASE_CODENAME != "mantic" \]; then/if [ $RELEASE_CODENAME != "mantic" ] \&\& [ $RELEASE_CODENAME != "noble" ] \&\& [ $RELEASE_CODENAME != "oracular" ]; then/g' Tools/environment_install/install-prereqs-ubuntu.sh
```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for details.

---

## Step 4: Build ArduPilot for SITL

```bash
# Navigate to ArduPlane directory
cd ~/ardupilot/ArduPlane

# Configure for SITL (Software-In-The-Loop simulation)
../waf configure --board sitl

# Build ArduPlane
../waf plane
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

## Step 5: Build for Hardware (Optional)

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

## Step 6: Verify SITL Installation

```bash
# Start SITL to verify everything works
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
```

**Expected behavior:**
- Three windows should open: MAVProxy command prompt, console, and map
- After a few seconds, you should see "GPS: 3D Fix" in the console
- Map should show aircraft position

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

### Issue: Display/X11 Errors in SITL

**Symptoms:** Map window doesn't open, X11 errors

**Solution:**
Install X server for Windows:
- Download and install VcXsrv or Xming
- In WSL, add to `~/.bashrc`:
  ```bash
  export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
  ```
- Reload: `source ~/.bashrc`

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
- [Main Onboarding Guide](../../../Documents/ArduPilot_Onboarding_Guide.md)
- [ArduPilot GitHub](https://github.com/ArduPilot/ardupilot)
- [ArduPilot Discourse Forum](https://discuss.ardupilot.org/)

---

**Last Updated:** 2026-02-03
**ArduPilot Version:** Plane 4.5.7 (commit 0358a9c210bc)
