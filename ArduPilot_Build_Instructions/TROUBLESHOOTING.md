# ArduPilot Build Troubleshooting Quick Reference

## Common Build Errors

### Error: "fatal: not a git repository"

**Fix:**

```bash
cd ~/ardupilot
# If directory doesn't exist:
git clone --recursive https://github.com/ArduPilot/ardupilot.git
```

---

### Error: "No such file or directory: submodule path"

**Fix:**

```bash
cd ~/ardupilot
git submodule update --init --recursive
```

---

### Error: "arm-none-eabi-g++ not found"

**Fix:**

```bash
cd ~/ardupilot
./Tools/environment_install/install-prereqs-ubuntu.sh -y
. ~/.profile
```

---

### Error: "ModuleNotFoundError: No module named 'pymavlink'"

**Fix:**

```bash
python3 -m pip install --user --upgrade pymavlink mavproxy
```

---

### Error: Build takes > 20 minutes

**Cause:** Building from Windows filesystem (`/mnt/c/`)

**Fix:**

```bash
pwd  # Should show /home/username/ardupilot, not /mnt/c/...
cd ~
git clone --recursive https://github.com/ArduPilot/ardupilot.git
cd ardupilot
git checkout Plane-4.5.7
git submodule update --init --recursive
```

---

### Error: "Waf: The wscript in '...' is unreadable"

**Fix:**

```bash
cd ~/ardupilot
./waf distclean
git checkout .
./waf configure --board sitl
```

---

### Error: X11/Display errors when starting SITL

- **WSLg (Windows 11):** Ensure DISPLAY is not overridden in `~/.bashrc`, then `source ~/.bashrc`. `echo $DISPLAY` should show `:0`.
- **VcXsrv (Windows 10):** See [setup_x_server.md](../Installation_Scripts/setup_x_server.md).
- **Run without GUI:**

```bash
Tools/autotest/sim_vehicle.py -v ArduPlane --console
# Omit --map flag
```

---

### Error: "ImportError: cannot import name 'mavutil'"

**Fix:**

```bash
python3 -m pip uninstall pymavlink mavproxy -y
python3 -m pip install --user pymavlink mavproxy
```

---

### Error: "Permission denied" when running scripts

**Fix:**

```bash
chmod +x Tools/autotest/sim_vehicle.py
chmod +x waf
```

---

## SITL Troubleshooting

### SITL won't start

1. Verify directory and build:

   ```bash
   cd ~/ardupilot
   ./waf plane
   ```

2. Verify MAVProxy is installed:

   ```bash
   python3 -m pip list | grep mavproxy
   ```

---

### "No GPS lock" in SITL

Normal: wait 10-30 seconds. If it persists:

```bash
Tools/autotest/sim_vehicle.py -v ArduPlane -L CMAC --console --map
```

---

### SITL map doesn't show aircraft

1. Check for "GPS: 3D Fix" in console
2. Zoom in on map
3. Restart SITL

---

### Cannot arm aircraft in SITL

Common PreArm causes:

- **"Need 3D Fix"** → Wait for GPS lock
- **"Compass not calibrated"** → Run `arm throttle force`
- **"RC not calibrated"** → Set `mode FBWA`

**Force arm (SITL only):**

```bash
arm throttle force
```

---

## Python Package Issues

### Deprecated package warnings

If warnings appear during installation but it completes, they are usually safe to ignore. For critical errors, check [ArduPilot Discourse](https://discuss.ardupilot.org/).

---

## Performance Issues

### Build is very slow (> 15 minutes)

- Verify building in WSL filesystem (`/home/username/ardupilot`, not `/mnt/c/`)
- 8GB+ RAM recommended; WSL2 required (not WSL1)

**Speed up builds:**

```bash
./waf plane -j4  # 4 CPU cores
./waf plane -j8  # 8 CPU cores
```

---

## Git Issues

### "Your local changes would be overwritten"

```bash
git stash        # stash changes
# or
git checkout .   # discard changes

git checkout Plane-4.5.7
```

---

### Wrong version checked out

```bash
git log -1
# Should show: commit 0358a9c210bc6c965006f5d6029239b7033616df

git fetch --tags
git checkout Plane-4.5.7
git submodule update --init --recursive
```

---

## Hardware Build Issues

### "Board not found" error

```bash
../waf list_boards | grep -i <part_of_board_name>
# Example:
../waf list_boards | grep -i cube
```

---

### Upload to hardware fails

```bash
ls -l /dev/ttyACM* /dev/ttyUSB*
sudo usermod -a -G dialout $USER
# Logout and login for changes to take effect
```

---

## When All Else Fails

### Complete clean and rebuild

```bash
cd ~/ardupilot
./waf distclean
git checkout .
git clean -fdx
git submodule update --init --recursive
./Tools/environment_install/install-prereqs-ubuntu.sh -y
. ~/.profile
python3 -m pip install --user --upgrade pymavlink mavproxy
./waf configure --board sitl
./waf plane
```

---

## Getting Help

1. **ArduPilot Discourse:** [discuss.ardupilot.org](https://discuss.ardupilot.org/)
2. **GitHub Issues:** [github.com/ArduPilot/ardupilot/issues](https://github.com/ArduPilot/ardupilot/issues)
3. **Dev Docs:** [ardupilot.org/dev](https://ardupilot.org/dev/)
4. **Discord:** [ardupilot.org/discord](https://ardupilot.org/discord)

Include: ArduPilot version, `git log -1` output, full error message, steps to reproduce, `lsb_release -a` output.

---

**Last Updated:** 2026-02-06
