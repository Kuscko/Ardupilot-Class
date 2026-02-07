# X Server Setup for WSL2

WSL2 requires an X server for SITL graphical windows (map and console).

## VcXsrv (Recommended)

### Installation

**1. Download and Install**
- Download from: https://sourceforge.net/projects/vcxsrv/
- Install latest version

**2. Configure VcXsrv**
- Launch XLaunch from Start Menu
- Select "Multiple windows"
- Display number: 0
- Click "Next"
- Select "Start no client"
- Click "Next"
- **IMPORTANT:** Check "Disable access control"
- Click "Next" → "Finish"

**3. Configure WSL2**

Add to `~/.bashrc`:
```bash
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
```

Reload:
```bash
source ~/.bashrc
```

**4. Test**

```bash
sudo apt install x11-apps
xeyes
```

If eyes window appears, it works!

### Auto-start VcXsrv

1. Press `Win + R`, type `shell:startup`, press Enter
2. Create shortcut to `C:\Program Files\VcXsrv\vcxsrv.exe`
3. Right-click shortcut → Properties
4. Add to Target: ` :0 -ac -terminate -lesspointer -multiwindow -clipboard -wgl`
5. Click OK

---

## WSLg (Windows 11)

Windows 11 includes built-in WSLg - no setup needed.

Check if active:
```bash
echo $DISPLAY
# Should show :0 or :1
```

---

## Run Without GUI

If you don't need the map window:

```bash
Tools/autotest/sim_vehicle.py -v ArduPlane --console
```

Use Mission Planner or QGroundControl on Windows to connect via UDP.

---

## Troubleshooting

### "cannot open display"

**Check:**
- Is VcXsrv running? (system tray)
- Is DISPLAY set? `echo $DISPLAY`
- Is "Disable access control" checked in VcXsrv?

**Fix:**
```bash
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
source ~/.bashrc
```

### Windows Firewall Blocking

1. Windows Security → Firewall & network protection
2. Allow an app through firewall
3. Find VcXsrv
4. Check both Private and Public

### Blank/Frozen Window

- Restart VcXsrv
- Restart SITL
- Test with `xeyes`

---

**Last Updated:** 2026-02-06
