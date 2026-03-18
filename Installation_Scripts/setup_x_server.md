# X Server Setup for WSL2 - ArduPilot SITL

WSL2 requires an X server to display graphical windows (map, console) for ArduPilot SITL.

**Last Updated:** 2026-02-06
**Tested:** Ubuntu 22.04 LTS on WSL2

---

## Recommended: WSLg (Windows 11 / WSL 2.0+)

WSLg is built into Windows 11 and WSL 2.0+ with zero configuration.

### Check if WSLg is Available

```bash
echo $DISPLAY
# Should show: :0 or :1

wsl.exe --version
# WSLg version should be listed
```

If you see a DISPLAY value, WSLg is working.

### Using WSLg

```bash
cd ~/ardupilot
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
```

You should see 3 windows: ArduPlane terminal, MAVProxy console, and map window.

### Important: Don't Override DISPLAY

If your `~/.bashrc` has this line, **comment it out** to use WSLg:

```bash
# Comment this out to use WSLg:
# export DISPLAY=$(grep -m 1 nameserver /etc/resolv.conf | awk '{print $2}'):0
```

---

## Alternative: VcXsrv (Windows 10 / Advanced Users)

Use only if running Windows 10 or WSLg is unavailable.

### Installation

**1. Download and Install VcXsrv**
- Download: https://sourceforge.net/projects/vcxsrv/

#### 2. Configure VcXsrv

VcXsrv MUST be started with `-listen tcp` for WSL2.

#### Option A: Command Line

```powershell
& "C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl -ac -listen tcp
```

#### Option B: Config File

Save as `config.xlaunch`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<XLaunch WindowMode="MultiWindow" ClientMode="NoClient" LocalClient="False" Display="0" LocalProgram="xcalc" RemoteProgram="xterm" RemotePassword="" PrivateKey="" RemoteHost="" RemoteUser="" XDMCPHost="" XDMCPBroadcast="False" XDMCPIndirect="False" Clipboard="True" ClipboardPrimary="True" ExtraParams="-listen tcp" Wgl="True" DisableAC="True" XDMCPTerminate="False"/>
```

#### Option C: Desktop Shortcut

Right-click Desktop → New → Shortcut

**Target:**
```
"C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl -ac -listen tcp
```

**3. Configure Windows Firewall**

PowerShell (as Administrator):

```powershell
New-NetFirewallRule -DisplayName "VcXsrv" -Direction Inbound -Program "C:\Program Files\VcXsrv\vcxsrv.exe" -Action Allow
```

Or: Windows Security → Firewall → Allow an app through firewall → add `vcxsrv.exe` with both Private and Public checked.

**4. Configure WSL2**

Add to `~/.bashrc`:

```bash
# VcXsrv X Server (only use if NOT using WSLg)
export DISPLAY=$(grep -m 1 nameserver /etc/resolv.conf | awk '{print $2}'):0
```

```bash
source ~/.bashrc
```

**5. Test Connection**

```bash
echo $DISPLAY
# Should show: 10.x.x.x:0

sudo apt install -y x11-apps
xeyes
```

### Auto-start VcXsrv on Windows Boot

1. Press `Win + R`, type `shell:startup`, press Enter
2. Copy `config.xlaunch` or shortcut to this folder

---

## Troubleshooting

### MAVProxy Modules Not Loading (console, map)

**Error:**
```
Failed to load module: No module named 'console'
Failed to load module: No module named 'map'
```

**Fix:**
```bash
sudo apt install -y python3-wxgtk4.0
```

---

### "cannot open display" or "Can't open display"

**Error:**
```
xterm: Xt error: Can't open display: 10.255.255.254:0
```

**Diagnosis:**

```bash
echo $DISPLAY

sudo apt install -y netcat-openbsd
nc -zv 10.255.255.254 6000  # For VcXsrv only

xeyes  # or xclock
```

**Fix for WSLg:**

```bash
# Make sure DISPLAY override is commented out in ~/.bashrc
source ~/.bashrc
echo $DISPLAY  # Should show :0
```

**Fix for VcXsrv:**

1. Verify VcXsrv is running (system tray "X" icon or Task Manager)
2. Restart VcXsrv with `-listen tcp` flag
3. Check logs: should show `DISPLAY=0.0.0.0:0.0`, NOT `127.0.0.1:0.0`
4. Check firewall (see VcXsrv section above)

---

### Only One Window Opens

**Cause:** MAVProxy modules (console, map) failed to load.

**Fix:** See "MAVProxy Modules Not Loading" section above.

---

### Windows Firewall Blocking (VcXsrv only)

**Test:**
```bash
nc -zv $(echo $DISPLAY | cut -d: -f1) 6000
# If "Connection refused", firewall is blocking
```

**Fix:**

```powershell
New-NetFirewallRule -DisplayName "VcXsrv" -Direction Inbound -Program "C:\Program Files\VcXsrv\vcxsrv.exe" -Action Allow
```

---

### Blank or Frozen Windows

1. Close all SITL windows
2. Restart X server
3. Test with `xeyes`
4. Re-run SITL

---

### VcXsrv Not Listening on Network

**Wrong (won't work with WSL2):**
```
winClipboardThreadProc - DISPLAY=127.0.0.1:0.0
```

**Correct:**
```
winClipboardThreadProc - DISPLAY=0.0.0.0:0.0
```

**Fix:** Restart VcXsrv with `-listen tcp` flag.

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

```bash
# Console only (no map)
Tools/autotest/sim_vehicle.py -v ArduPlane --console

# No GUI at all
Tools/autotest/sim_vehicle.py -v ArduPlane
```

Connect from Windows using Mission Planner, QGroundControl, or MAVProxy via UDP `127.0.0.1:14550` or TCP `127.0.0.1:5760`.

---

## Quick Reference

### WSLg (Recommended)
```bash
echo $DISPLAY  # Should show :0

cd ~/ardupilot
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
```

### VcXsrv (Windows 10)
```powershell
& "C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl -ac -listen tcp
```

```bash
export DISPLAY=$(grep -m 1 nameserver /etc/resolv.conf | awk '{print $2}'):0
xeyes  # Test
cd ~/ardupilot
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
```
