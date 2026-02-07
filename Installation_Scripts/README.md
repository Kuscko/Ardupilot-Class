# ArduPilot Installation Scripts

Automated installation scripts for ArduPilot Plane 4.5.7 on Ubuntu 22.04/WSL2.

## Quick Start

```bash
cd ~
chmod +x install_ardupilot_plane_4.5.7.sh
./install_ardupilot_plane_4.5.7.sh
```

**Time:** 15-30 minutes

## Prerequisites

- Ubuntu 22.04 LTS (WSL2 recommended)
- Internet connection (~500MB download)
- Sudo privileges
- 10GB+ free disk space

## What Gets Installed

| Component | Description |
|-----------|-------------|
| Build tools | GCC, G++, Make, WAF |
| Python 3.10+ | With pip and venv |
| ArduPilot | Plane 4.5.7 source code |
| Python packages | pymavlink, MAVProxy |
| Libraries | libxml2, libxslt, git |

## Available Scripts

### install_ardupilot_plane_4.5.7.sh

Complete ArduPilot development environment setup.

```bash
chmod +x install_ardupilot_plane_4.5.7.sh
./install_ardupilot_plane_4.5.7.sh
```

### install_mavproxy.sh

Install or update MAVProxy only.

```bash
chmod +x install_mavproxy.sh
./install_mavproxy.sh
```

## Verification

After installation:

```bash
# Activate virtual environment
source ~/.venv-ardupilot/bin/activate

# Verify version
cd ~/ardupilot
git log --oneline -1
# Expected: 0358a9c2 ArduPlane: update version to 4.5.7

# Test SITL
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
```

## Virtual Environment

All Python packages are installed in an isolated virtual environment at `~/.venv-ardupilot`.

**Manual activation:**
```bash
source ~/.venv-ardupilot/bin/activate
```

**Auto-activation (add to ~/.bashrc):**
```bash
# Auto-activate ArduPilot virtual environment
# Check if venv is actually activated (not just VIRTUAL_ENV set)
if [ -f "$HOME/.venv-ardupilot/bin/activate" ]; then
    # Check if the deactivate function exists (created by activate script)
    if ! type deactivate &> /dev/null; then
        source "$HOME/.venv-ardupilot/bin/activate"
    fi
fi
```

## X Server (WSL2 Only)

For graphical SITL windows, you need an X server. See [setup_x_server.md](setup_x_server.md).

**Quick setup:**
1. Install VcXsrv on Windows
2. Add to ~/.bashrc:
   ```bash
   export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
   ```
3. Test with `xeyes`

## Troubleshooting

### Permission Denied
```bash
chmod +x install_ardupilot_plane_4.5.7.sh
```

### Running from /mnt/c/
Don't build from Windows filesystem - it's very slow.
```bash
cd ~
```

### Commands Not Found
Activate the virtual environment:
```bash
source ~/.venv-ardupilot/bin/activate
```

### X Windows Don't Appear
1. Check X server is running
2. Verify: `echo $DISPLAY`
3. See [setup_x_server.md](setup_x_server.md)

## Python 3.10.12 Compatibility

Python 3.10.12 (Ubuntu 22.04 default) is **fully compatible** with ArduPilot Plane 4.5.7.

- ArduPilot requires: Python 3.8.0+
- Your system has: Python 3.10.12 ✓

## Documentation

- [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) - Complete manual installation steps
- [setup_x_server.md](setup_x_server.md) - X server configuration for WSL2

## Resources

- [ArduPilot Dev Docs](https://ardupilot.org/dev/)
- [MAVProxy Documentation](https://ardupilot.org/mavproxy/)
- [ArduPilot Discord](https://ardupilot.org/discord)
- [ArduPilot Forum](https://discuss.ardupilot.org/)

## Next Steps

1. Activate virtual environment
2. Test SITL with different flight modes
3. Review onboarding documentation
4. Try example mission plans
5. Explore Lua scripting

---

**Last Updated:** 2026-02-06
**Version:** ArduPilot Plane 4.5.7
