# ArduPilot Build Guide — Plane 4.5.7

**Target Version:** Plane 4.5.7 (commit: 0358a9c210bc6c965006f5d6029239b7033616df)

---

## Prerequisites

- Windows 10/11 with WSL2 enabled
- 10GB+ free disk space
- 8GB+ RAM recommended

### Enable WSL2

1. Open PowerShell as Administrator:

   ```powershell
   wsl --install
   ```

2. Install Ubuntu 22.04 LTS from the Microsoft Store, then launch it and create a username/password.

---

## Step 1: Initial System Setup

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-pip
```

---

## Step 2: Clone ArduPilot Repository

```bash
cd ~
git clone --recursive https://github.com/ArduPilot/ardupilot.git
cd ardupilot
git fetch --tags
git checkout Plane-4.5.7
git log -1
# Should show: commit 0358a9c210bc6c965006f5d6029239b7033616df
git submodule update --init --recursive
```

> **CRITICAL:** Always clone and build inside the WSL filesystem (`~/ardupilot`), NOT under `/mnt/c/`.

---

## Step 3: Install Build Prerequisites

```bash
cd ~/ardupilot
./Tools/environment_install/install-prereqs-ubuntu.sh -y
source ~/.profile
source ~/.bashrc
pip3 install --user --upgrade pymavlink mavproxy
```

This installs ARM cross-compiler toolchains, Python development packages (including python3-wxgtk4.0), MAVProxy, and build tools.

---

## Step 4: Build ArduPilot for SITL

```bash
cd ~/ardupilot
./waf configure --board sitl
./waf plane
```

First build takes 5-15 minutes. Subsequent builds are incremental.

### Successful Build Output

```text
Build commands will be stored in build/sitl/compile_commands.json
'plane' finished successfully (XXX.XXXs)
```

Binary location: `~/ardupilot/build/sitl/bin/arduplane`

---

## Step 5: Configure Display (WSLg or VcXsrv)

**Windows 11 / WSL 2.0+ (WSLg):**

```bash
echo $DISPLAY  # Should show: :0

# Make sure this line is commented out in ~/.bashrc:
# export DISPLAY=$(grep -m 1 nameserver /etc/resolv.conf | awk '{print $2}'):0
```

**Windows 10 (VcXsrv):**

See [setup_x_server.md](../Installation_Scripts/setup_x_server.md).

---

## Step 6: Build for Hardware (Optional)

```bash
../waf list_boards
../waf configure --board CubeOrangePlus
../waf plane
```

Output: `~/ardupilot/build/CubeOrangePlus/bin/arduplane.apj`

### Common Hardware Boards

- `CubeOrangePlus` - Hex Cube Orange+
- `Pixhawk6X` - Holybro Pixhawk 6X
- `MatekH743` - Matek H743
- `KakuteH7` - Holybro Kakute H7

---

## Step 7: Verify SITL Installation

```bash
cd ~/ardupilot
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
```

Expected: three windows open (ArduPlane terminal, MAVProxy console, map), GPS 3D Fix after a few seconds.

- **Only 1 window opens:** wxPython not accessible. Run `sudo apt install -y python3-wxgtk4.0`.
- **"Can't open display" error:** See Step 5.

Press Ctrl+C to exit.

---

## Common Build Issues & Solutions

### Submodule Errors

```bash
cd ~/ardupilot
git submodule update --init --recursive
```

### Python Package Conflicts

```bash
python3 -m pip install --user --upgrade pymavlink mavproxy
# If issues persist:
python3 -m pip install --user --force-reinstall pymavlink mavproxy
```

### Slow Build Times

Verify you're in the WSL filesystem: `pwd` should show `/home/username/ardupilot`, not `/mnt/c/`.

### WAF Configuration Fails

```bash
./waf distclean
./Tools/environment_install/install-prereqs-ubuntu.sh -y
. ~/.profile
./waf configure --board sitl
```

### Permission Denied

```bash
chmod +x Tools/autotest/sim_vehicle.py
chmod +x waf
```

### Display/X11 Errors

**WSLg:** Ensure DISPLAY override is commented out in `~/.bashrc`, then `source ~/.bashrc`.

**VcXsrv:** See [setup_x_server.md](../Installation_Scripts/setup_x_server.md) — must start with `-listen tcp`.

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

```text
~/ardupilot/
├── ArduPlane/          # Plane-specific code
├── ArduCopter/         # Copter-specific code
├── libraries/          # Shared libraries (~80% of codebase)
│   ├── AP_GPS/
│   ├── AP_Baro/
│   ├── AP_Compass/
│   ├── AP_NavEKF3/
│   └── ...
├── Tools/
│   ├── autotest/       # SITL scripts
│   └── environment_install/
└── build/
    ├── sitl/
    └── [BOARD]/
```

---

## Next Steps

1. [ ] Start SITL and familiarize yourself with MAVProxy
2. [ ] Review [SITL Mission Plans](../SITL_Mission_Plans/)
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

**Last Updated:** 2026-03-17
**ArduPilot Version:** Plane 4.5.7 (commit 0358a9c210bc)
**Platform:** Ubuntu 22.04 LTS (Jammy Jellyfish) with Python 3.10
