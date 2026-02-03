# ArduPilot Build Troubleshooting Quick Reference

## Common Build Errors

### Error: "fatal: not a git repository"

**Cause:** Not in the ardupilot directory or repo not cloned properly

**Fix:**
```bash
cd ~/ardupilot
# If directory doesn't exist, clone it:
git clone --recursive https://github.com/ArduPilot/ardupilot.git
```

---

### Error: "No such file or directory: submodule path"

**Cause:** Git submodules not initialized

**Fix:**
```bash
cd ~/ardupilot
git submodule update --init --recursive
```

---

### Error: "Package 'python-argparse' has no installation candidate"

**Cause:** Ubuntu 24.04+ no longer includes `python-argparse` as a separate package (it's part of Python standard library)

**Fix:**

Apply patch before running prerequisites installer:

```bash
cd ~/ardupilot

# Backup the original script
cp Tools/environment_install/install-prereqs-ubuntu.sh Tools/environment_install/install-prereqs-ubuntu.sh.backup

# Apply the fix
sed -i 's/if \[ $RELEASE_CODENAME != "mantic" \]; then/if [ $RELEASE_CODENAME != "mantic" ] \&\& [ $RELEASE_CODENAME != "noble" ] \&\& [ $RELEASE_CODENAME != "oracular" ]; then/g' Tools/environment_install/install-prereqs-ubuntu.sh

# Now run the installer
./Tools/environment_install/install-prereqs-ubuntu.sh -y
```

**Note:** This fix is automatically applied if you use the `install_ardupilot_plane_4.5.7.sh` script.

---

### Error: "arm-none-eabi-g++ not found"

**Cause:** Cross-compiler not installed

**Fix:**
```bash
cd ~/ardupilot
./Tools/environment_install/install-prereqs-ubuntu.sh -y
. ~/.profile
```

---

### Error: "ModuleNotFoundError: No module named 'pymavlink'"

**Cause:** Python MAVLink packages not installed

**Fix:**
```bash
python3 -m pip install --user --upgrade pymavlink mavproxy
```

---

### Error: Build takes > 20 minutes

**Cause:** Building from Windows filesystem (/mnt/c/)

**Fix:**
```bash
# Check current location
pwd

# If shows /mnt/c/..., move to WSL filesystem:
cd ~
git clone --recursive https://github.com/ArduPilot/ardupilot.git
cd ardupilot
git checkout Plane-4.5.7
git submodule update --init --recursive
```

---

### Error: "Waf: The wscript in '...' is unreadable"

**Cause:** Corrupted WAF or incorrect directory

**Fix:**
```bash
cd ~/ardupilot
./waf distclean
git status  # Check for uncommitted changes
git checkout .  # Reset to clean state
./waf configure --board sitl
```

---

### Error: X11/Display errors when starting SITL

**Cause:** No X server for graphical output

**Fix:**

**Option 1: Install X Server (Recommended)**
1. Download and install VcXsrv: https://sourceforge.net/projects/vcxsrv/
2. Run XLaunch with default settings
3. Add to `~/.bashrc`:
   ```bash
   export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
   ```
4. Reload: `source ~/.bashrc`

**Option 2: Run SITL without GUI**
```bash
Tools/autotest/sim_vehicle.py -v ArduPlane --console
# Omit --map flag
```

---

### Error: "ImportError: cannot import name 'mavutil'"

**Cause:** MAVProxy or pymavlink version conflict

**Fix:**
```bash
python3 -m pip uninstall pymavlink mavproxy -y
python3 -m pip install --user pymavlink mavproxy
```

---

### Error: "Permission denied" when running scripts

**Cause:** Scripts not executable

**Fix:**
```bash
chmod +x Tools/autotest/sim_vehicle.py
chmod +x waf
```

---

## SITL Troubleshooting

### SITL won't start

**Check:**
1. Are you in the correct directory?
   ```bash
   cd ~/ardupilot/ArduPlane
   ```

2. Did the build succeed?
   ```bash
   ../waf plane
   ```

3. Is MAVProxy installed?
   ```bash
   python3 -m pip list | grep mavproxy
   ```

---

### "No GPS lock" in SITL

**Normal behavior:** Wait 10-30 seconds for simulated GPS to lock

**If persists:**
```bash
# Restart SITL
# Check console for errors
# Try different start location:
Tools/autotest/sim_vehicle.py -v ArduPlane -L CMAC --console --map
```

---

### SITL map doesn't show aircraft

**Check:**
1. Is GPS locked? Look for "GPS: 3D Fix" in console
2. Is map zoomed out too far? Zoom in on map
3. Try restarting SITL

---

### Cannot arm aircraft in SITL

**Check console for PreArm messages:**

Common causes:
- **"PreArm: Need 3D Fix"** → Wait for GPS lock
- **"PreArm: Compass not calibrated"** → Run `arm throttle force`
- **"PreArm: RC not calibrated"** → Set flight mode: `mode FBWA`

**Force arm (SITL only):**
```bash
arm throttle force
```

---

## Python Package Issues

### Deprecated package warnings

**If you see warnings about deprecated packages during installation:**

1. Note which packages are deprecated
2. Check ArduPilot GitHub issues for known solutions
3. Update installation script if needed

**Common deprecated packages (as of 2024-2025):**
- Some older pip packages may show deprecation warnings
- Usually safe to ignore if installation completes
- For critical errors, check ArduPilot Discourse forum

---

## Performance Issues

### Build is very slow (> 15 minutes)

**Checklist:**
- [ ] Building in WSL filesystem? (`pwd` should show `/home/username/ardupilot`)
- [ ] Sufficient RAM? (8GB+ recommended)
- [ ] WSL2 enabled? (not WSL1)

**Speed up builds:**
```bash
# Use parallel compilation
../waf plane -j4  # Uses 4 CPU cores

# For systems with more cores:
../waf plane -j8
```

---

## Git Issues

### "Your local changes would be overwritten"

**Cause:** Modified files in repo

**Fix:**
```bash
# Stash changes
git stash

# Or discard changes
git checkout .

# Then checkout branch/tag
git checkout Plane-4.5.7
```

---

### Wrong version checked out

**Verify version:**
```bash
git log -1
# Should show: commit 0358a9c210bc6c965006f5d6029239b7033616df
```

**Fix if wrong:**
```bash
git fetch --tags
git checkout Plane-4.5.7
git submodule update --init --recursive
```

---

## Hardware Build Issues

### "Board not found" error

**Cause:** Invalid board name

**Fix:**
```bash
# List all available boards
../waf list_boards | grep -i <part_of_board_name>

# Example: Find Cube boards
../waf list_boards | grep -i cube
```

---

### Upload to hardware fails

**Common causes:**
1. Flight controller not connected or recognized
2. Wrong USB permissions
3. Bootloader mode not enabled

**Fix:**
```bash
# Check USB permissions
ls -l /dev/ttyACM* /dev/ttyUSB*

# Add user to dialout group
sudo usermod -a -G dialout $USER
# Logout and login for changes to take effect
```

---

## When All Else Fails

### Nuclear option: Complete clean and rebuild

```bash
cd ~/ardupilot

# 1. Complete clean
./waf distclean

# 2. Reset git repository
git checkout .
git clean -fdx

# 3. Update submodules
git submodule update --init --recursive

# 4. Reinstall prerequisites
./Tools/environment_install/install-prereqs-ubuntu.sh -y
. ~/.profile

# 5. Reinstall Python packages
python3 -m pip install --user --upgrade pymavlink mavproxy

# 6. Rebuild
cd ArduPlane
../waf configure --board sitl
../waf plane
```

---

## Getting Help

If you encounter issues not covered here:

1. **Check ArduPilot Discourse:** https://discuss.ardupilot.org/
2. **Search GitHub Issues:** https://github.com/ArduPilot/ardupilot/issues
3. **Review Dev Docs:** https://ardupilot.org/dev/
4. **Ask on Discord:** https://ardupilot.org/discord

When asking for help, include:
- ArduPilot version (Plane 4.5.7)
- Output of: `git log -1`
- Full error message
- Steps to reproduce
- OS/WSL version: `lsb_release -a`

---

**Last Updated:** 2026-02-03
