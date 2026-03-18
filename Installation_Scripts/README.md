# ArduPilot Installation Scripts

Automated installation scripts for ArduPilot Plane 4.5.7 on Ubuntu 22.04 LTS (Jammy Jellyfish) (WSL2).

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
| Python 3.10 | With pip (system packages, no venv required) |
| ArduPilot | Plane 4.5.7 source code |
| Python packages | pymavlink, MAVProxy (via pip --user) |
| wxPython | python3-wxgtk4.0 (for MAVProxy console and map) |
| Libraries | libxml2, libxslt, git |

## Available Scripts

### install_ardupilot_plane_4.5.7.sh

Complete ArduPilot development environment setup.

```bash
chmod +x install_ardupilot_plane_4.5.7.sh
./install_ardupilot_plane_4.5.7.sh
```

### install_mavproxy.sh

Install or update MAVProxy only (run after the main script if needed).

```bash
chmod +x install_mavproxy.sh
./install_mavproxy.sh
```

## Verification

After installation:

```bash
# Verify version
cd ~/ardupilot
git log --oneline -1
# Expected: 0358a9c2 ArduPlane: update version to 4.5.7

# Test SITL
Tools/autotest/sim_vehicle.py -v ArduPlane --console --map
```

## Troubleshooting

### Permission Denied

```bash
chmod +x install_ardupilot_plane_4.5.7.sh
```

### Running from /mnt/c/

Don't build from Windows filesystem — it's very slow.

```bash
cd ~
```

### Commands Not Found (mavproxy.py, etc.)

Reload your shell profile to pick up the PATH set by the prereqs script:

```bash
source ~/.profile
```

### X Windows Don't Appear

1. Check X server is running
2. Verify: `echo $DISPLAY`
3. See [setup_x_server.md](setup_x_server.md)

### MAVProxy Console/Map Missing

wxPython is required. Install it:

```bash
sudo apt install -y python3-wxgtk4.0
```

## Documentation

- [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) - Complete manual installation steps
- [setup_x_server.md](setup_x_server.md) - X server configuration for WSL2

## Resources

- [ArduPilot Dev Docs](https://ardupilot.org/dev/)
- [MAVProxy Documentation](https://ardupilot.org/mavproxy/)
- [ArduPilot Discord](https://ardupilot.org/discord)
- [ArduPilot Forum](https://discuss.ardupilot.org/)

## Next Steps

1. Test SITL with different flight modes
2. Review onboarding documentation
3. Try example mission plans
4. Explore Lua scripting

---

**Last Updated:** 2026-03-17
**Version:** ArduPilot Plane 4.5.7
**Platform:** Ubuntu 22.04 LTS (Jammy Jellyfish)
