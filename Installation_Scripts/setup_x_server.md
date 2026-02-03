# X Server Setup for WSL2

## Why You Need This

SITL's map and console windows require a graphical display. WSL2 doesn't include a display server by default, so you need to install one on Windows.

## Option 1: VcXsrv (Recommended)

### Installation

1. **Download VcXsrv:**
   - Visit: https://sourceforge.net/projects/vcxsrv/
   - Download and install the latest version

2. **Configure VcXsrv:**
   - Launch XLaunch from Start Menu
   - Select "Multiple windows"
   - Display number: 0
   - Click "Next"
   - Select "Start no client"
   - Click "Next"
   - **IMPORTANT:** Check "Disable access control"
   - Click "Next", then "Finish"

3. **Configure WSL2:**

   Add to your `~/.bashrc`:
   ```bash
   export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
   ```

   Then reload:
   ```bash
   source ~/.bashrc
   ```

4. **Test the setup:**
   ```bash
   # Install xeyes test app
   sudo apt install x11-apps

   # Run test
   xeyes
   ```

   If a window with eyes appears, it works!

### Auto-start VcXsrv

To automatically start VcXsrv on Windows boot:

1. Press `Win + R`, type `shell:startup`, press Enter
2. Create a shortcut to `C:\Program Files\VcXsrv\vcxsrv.exe`
3. Right-click shortcut → Properties
4. Add to "Target" after the path: ` :0 -ac -terminate -lesspointer -multiwindow -clipboard -wgl`
5. Apply and OK

## Option 2: WSLg (Windows 11 only)

Windows 11 includes built-in WSLg (WSL GUI support). No additional setup needed if you're on Windows 11 with updated WSL.

Check if WSLg is available:
```bash
echo $DISPLAY
# If it shows something like :0 or :1, WSLg is active
```

## Option 3: Run SITL Without GUI

If you don't need the map window:

```bash
cd ~/ardupilot/ArduPlane
Tools/autotest/sim_vehicle.py -v ArduPlane --console
# Note: --map flag is omitted
```

You can still use Mission Planner or QGroundControl on Windows to connect to SITL via UDP.

## Troubleshooting

### Error: "cannot open display"

**Check:**
1. Is VcXsrv running? (Check system tray)
2. Is DISPLAY variable set?
   ```bash
   echo $DISPLAY
   ```
3. Is "Disable access control" checked in VcXsrv?

**Fix:**
```bash
# Add to ~/.bashrc if not already there
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
source ~/.bashrc
```

### VcXsrv blocks by Windows Firewall

1. Windows Security → Firewall & network protection
2. Allow an app through firewall
3. Find VcXsrv, ensure both Private and Public are checked

### Map window is blank or frozen

- Restart VcXsrv
- Restart SITL
- Check if X server is responding: `xeyes`

---

**Last Updated:** 2026-02-03
