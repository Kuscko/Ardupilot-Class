# X Server Setup for WSL2 - ArduPilot SITL

WSL2 requires an X server to display graphical windows (map, console) for ArduPilot SITL.

**Last Updated:** 2026-02-06
**Tested:** Ubuntu 22.04 & 24.04 LTS on WSL2

---

## Recommended: WSLg (Windows 11 / WSL 2.0+)

**WSLg is the easiest and most reliable option.** It's built into Windows 11 and WSL 2.0+ with zero configuration.

### Check if WSLg is Available

```bash
echo $DISPLAY
# Should show: :0 or :1

wsl.exe --version
# WSLg version should be listed
```

If you see a DISPLAY value, **you're done!** WSLg is working.

### Using WSLg

**No configuration needed!** Just run SITL:

```bash
cd ~/ardupilot
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
```

You should see 3 windows:
1. ArduPlane terminal (simulator)
2. MAVProxy console (command interface)
3. Map window (aircraft position)

### Important: Don't Override DISPLAY

If your `~/.bashrc` has this line, **comment it out** to use WSLg:

```bash
# Comment this out to use WSLg:
# export DISPLAY=$(grep -m 1 nameserver /etc/resolv.conf | awk '{print $2}'):0
```

WSLg automatically sets DISPLAY to `:0` - don't override it!

---

## Alternative: VcXsrv (Windows 10 / Advanced Users)

**Only use if:**
- Running Windows 10 (no WSLg support)
- Need specific X server features
- WSLg isn't working for some reason

### Installation

**1. Download and Install VcXsrv**
- Download: https://sourceforge.net/projects/vcxsrv/
- Install latest version

**2. Configure VcXsrv with Correct Settings**

**CRITICAL:** VcXsrv MUST be started with `-listen tcp` flag for WSL2:

#### Option A: Command Line (Quick Test)

Open PowerShell and run:
```powershell
& "C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl -ac -listen tcp
```

#### Option B: Create Config File (Recommended)

Save this as `config.xlaunch`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<XLaunch WindowMode="MultiWindow" ClientMode="NoClient" LocalClient="False" Display="0" LocalProgram="xcalc" RemoteProgram="xterm" RemotePassword="" PrivateKey="" RemoteHost="" RemoteUser="" XDMCPHost="" XDMCPBroadcast="False" XDMCPIndirect="False" Clipboard="True" ClipboardPrimary="True" ExtraParams="-listen tcp" Wgl="True" DisableAC="True" XDMCPTerminate="False"/>
```

Double-click to launch VcXsrv with correct settings.

#### Option C: Desktop Shortcut

Right-click Desktop → New → Shortcut

**Target:**
```
"C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl -ac -listen tcp
```

**Name:** `VcXsrv for WSL2`

**3. Configure Windows Firewall**

VcXsrv needs firewall access. In PowerShell (as Administrator):

```powershell
New-NetFirewallRule -DisplayName "VcXsrv" -Direction Inbound -Program "C:\Program Files\VcXsrv\vcxsrv.exe" -Action Allow
```

Or manually:
1. Windows Security → Firewall & network protection
2. "Allow an app through firewall"
3. Click "Change settings"
4. Add `C:\Program Files\VcXsrv\vcxsrv.exe`
5. **Check BOTH** Private and Public networks

**4. Configure WSL2**

Add to `~/.bashrc`:

```bash
# VcXsrv X Server (only use if NOT using WSLg)
export DISPLAY=$(grep -m 1 nameserver /etc/resolv.conf | awk '{print $2}'):0
```

Reload:
```bash
source ~/.bashrc
```

**5. Test Connection**

```bash
# Check DISPLAY is set correctly
echo $DISPLAY
# Should show: 10.x.x.x:0 or similar Windows host IP

# Test with xeyes
sudo apt install -y x11-apps
xeyes
```

If the eyes window appears, VcXsrv is working!

### Auto-start VcXsrv on Windows Boot

1. Press `Win + R`, type `shell:startup`, press Enter
2. Copy your `config.xlaunch` or shortcut to this folder
3. VcXsrv will start automatically on login

---

## Troubleshooting

### MAVProxy Modules Not Loading (console, map)

**Error:**
```
Failed to load module: No module named 'console'
Failed to load module: No module named 'map'
```

**Cause:** wxPython is not accessible in the virtual environment.

**Fix:**
```bash
# Add system packages to venv
cd ~/.venv-ardupilot
echo "import site; site.addsitedir('/usr/lib/python3/dist-packages')" > lib/python3.12/site-packages/system_packages.pth

# Verify wxPython is accessible
source ~/.venv-ardupilot/bin/activate
python -c "import wx; print('wxPython version:', wx.__version__)"
```

If wxPython is not installed:
```bash
sudo apt install -y python3-wxgtk4.0
```

**This fix is now included in the install script!**

---

### "cannot open display" or "Can't open display"

**Error:**
```
xterm: Xt error: Can't open display: 10.255.255.254:0
```

**Causes:**
1. X server (VcXsrv or WSLg) is not running
2. DISPLAY variable is not set correctly
3. Firewall blocking connection (VcXsrv only)
4. VcXsrv started without `-listen tcp` flag

**Diagnosis:**

```bash
# Check DISPLAY variable
echo $DISPLAY

# For WSLg, should show: :0
# For VcXsrv, should show: 10.x.x.x:0

# Test connection (install if needed)
sudo apt install -y netcat-openbsd
nc -zv 10.255.255.254 6000  # For VcXsrv only

# Try a simple GUI app
xeyes  # or xclock
```

**Fix for WSLg:**

```bash
# Make sure DISPLAY override is commented out in ~/.bashrc
# WSLg sets it automatically to :0
source ~/.bashrc
echo $DISPLAY  # Should show :0
```

**Fix for VcXsrv:**

1. **Verify VcXsrv is running:**
   - Look for "X" icon in Windows system tray (bottom-right)
   - Check Task Manager for `vcxsrv.exe`

2. **Restart VcXsrv with `-listen tcp`:**
   - Close VcXsrv (right-click system tray icon → Exit)
   - Start with correct flags (see VcXsrv section above)

3. **Check VcXsrv logs:**
   - VcXsrv logs should show: `DISPLAY=10.x.x.x:0.0` (NOT `127.0.0.1:0.0`)
   - If showing localhost, restart with `-listen tcp`

4. **Reset DISPLAY:**
   ```bash
   source ~/.bashrc
   echo $DISPLAY
   # Should show Windows host IP: 10.x.x.x:0
   ```

5. **Check firewall** (see VcXsrv section above)

---

### Only One Window Opens (Not All Three)

**Symptoms:**
- Only ArduPlane terminal appears
- Map and console windows don't open

**Cause:** MAVProxy modules (console, map) failed to load.

**Fix:** See "MAVProxy Modules Not Loading" section above.

---

### Windows Firewall Blocking (VcXsrv only)

**Symptoms:**
- VcXsrv is running
- DISPLAY is set correctly
- Connection still refused

**Test:**
```bash
nc -zv $(echo $DISPLAY | cut -d: -f1) 6000
# If "Connection refused", firewall is blocking
```

**Fix:**

PowerShell (as Administrator):
```powershell
New-NetFirewallRule -DisplayName "VcXsrv" -Direction Inbound -Program "C:\Program Files\VcXsrv\vcxsrv.exe" -Action Allow
```

Or manually allow in Windows Security settings (see VcXsrv section).

---

### Blank or Frozen Windows

**Fix:**
1. Close all SITL windows
2. Restart X server (VcXsrv or restart WSL for WSLg)
3. Test with `xeyes` first
4. Re-run SITL

---

### VcXsrv Not Listening on Network

**Check VcXsrv logs** (in XLaunch window):

**Wrong (won't work with WSL2):**
```
winClipboardThreadProc - DISPLAY=127.0.0.1:0.0
```

**Correct:**
```
winClipboardThreadProc - DISPLAY=0.0.0.0:0.0
# or similar non-localhost address
```

**Fix:** Restart VcXsrv with `-listen tcp` flag (critical!)

---

## WSLg vs VcXsrv Comparison

| Feature | WSLg | VcXsrv |
|---------|------|--------|
| **Setup** | None - works out of box | Manual configuration required |
| **Performance** | Native integration | Good |
| **Compatibility** | Windows 11 / WSL 2.0+ | Windows 10/11 |
| **Reliability** | Very stable | Requires correct flags & firewall |
| **Audio Support** | Yes | No |
| **GPU Acceleration** | Yes (via DirectX) | Limited |
| **Recommended** | Yes (if available) | For Windows 10 only |

---

## Alternative: Run Without GUI

If GUI setup is problematic, run SITL without graphical windows:

```bash
# Console only (no map)
Tools/autotest/sim_vehicle.py -v ArduPlane --console

# Or no GUI at all (connect with ground station)
Tools/autotest/sim_vehicle.py -v ArduPlane
```

Connect from Windows using:
- Mission Planner
- QGroundControl
- MAVProxy on Windows

Connection: UDP `127.0.0.1:14550` or TCP `127.0.0.1:5760`

---

## Quick Reference

### WSLg (Recommended)
```bash
# Check if working
echo $DISPLAY  # Should show :0

# Run SITL
cd ~/ardupilot
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
```

### VcXsrv (Windows 10)
```powershell
# Windows: Start VcXsrv with correct flags
& "C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl -ac -listen tcp
```

```bash
# WSL: Configure and test
export DISPLAY=$(grep -m 1 nameserver /etc/resolv.conf | awk '{print $2}'):0
xeyes  # Test
cd ~/ardupilot
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
```

---

**Pro Tip:** If you're on Windows 11 with WSL 2.0+, just use WSLg. It's simpler, more reliable, and requires zero configuration!
