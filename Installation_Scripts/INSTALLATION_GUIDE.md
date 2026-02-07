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

### 4. Install Prerequisites

```bash
cd ~/ardupilot
./Tools/environment_install/install-prereqs-ubuntu.sh -y
pip install --upgrade pip pymavlink mavproxy
```

### 5. Build ArduPlane

```bash
./waf configure --board sitl
./waf plane
```

### 6. Test SITL

```bash
source ~/.venv-ardupilot/bin/activate
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
```

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
python -c "import pymavlink; print('OK')"
mavproxy.py --version
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

### python-argparse Error

**Issue:** Package 'python-argparse' has no installation candidate

**Cause:** argparse is built into Python 3.2+. The separate package is obsolete.

**Solution:** The installation script automatically removes this. No action needed.

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
