# Building ArduPilot from Source

Build ArduPilot Plane 4.5.7 from source in WSL2/Ubuntu 22.04.

**Target Version:** Plane 4.5.7 (commit: 0358a9c210bc6c965006f5d6029239b7033616df)

## Prerequisites

- Windows 10/11 with Administrator access
- 10GB+ free disk space
- 8GB+ RAM recommended
- Basic Linux command line knowledge

## Getting Started

See **[BUILD_GUIDE.md](BUILD_GUIDE.md)** for step-by-step instructions covering WSL2 setup, dependencies, cloning, SITL and hardware builds, and verification.

**Estimated Time:** 1-2 hours (including downloads)

---

## Hands-On Practice

### Exercise 1: Build for SITL

```bash
cd ~
git clone https://github.com/ArduPilot/ardupilot.git
cd ardupilot
git checkout Plane-4.5.7
git submodule update --init --recursive
./waf configure --board sitl
./waf plane
```

**Verify:**
```bash
cd ArduPlane
./arduplane --version
# Should show: ArduPlane V4.5.7 (Plane-4.5.7)
```

### Exercise 2: Build for Hardware

```bash
./waf list_boards
./waf configure --board Pixhawk1
./waf plane
ls -lh build/Pixhawk1/bin/arduplane.apj
```

### Exercise 3: Clean and Rebuild

```bash
./waf clean
./waf configure --board sitl
./waf plane
```

---

## Key Concepts

### WAF Build System

ArduPilot uses WAF instead of Make:

- `./waf configure --board <BOARD>` - Configure for target
- `./waf list_boards` - List supported boards
- `./waf plane` / `./waf copter` / `./waf rover` - Build firmware
- `./waf clean` - Remove build artifacts

See [ArduPilot WAF Documentation](https://ardupilot.org/dev/docs/waf.html).

### Build Targets

| Target | Purpose | Build Command |
|--------|---------|---------------|
| SITL | Software simulation | `./waf configure --board sitl` |
| Pixhawk1 | Pixhawk controllers | `./waf configure --board Pixhawk1` |
| MatekH743 | Matek H743 boards | `./waf configure --board MatekH743` |
| CubeOrange | Hex Cube Orange | `./waf configure --board CubeOrange` |

Full list: `./waf list_boards` or [Supported Boards](https://ardupilot.org/plane/docs/common-autopilots.html).

### Submodules

Always update after checkout:

```bash
git submodule update --init --recursive
```

---

## Common Issues

### Python Package Errors

**Symptom:** `ModuleNotFoundError`

**Solution:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### WAF Configuration Fails

```bash
cd ardupilot/Tools/environment_install
./install-prereqs-ubuntu.sh -y
```

### Build Errors After Git Pull

```bash
git submodule update --init --recursive
./waf clean
./waf configure --board sitl
./waf plane
```

See **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** for the full troubleshooting guide.

---

## Development Workflow

1. Create feature branch: `git checkout -b my-feature`
2. Make code changes
3. Rebuild: `./waf plane`
4. Test in SITL: `cd ArduPlane && sim_vehicle.py`
5. Commit: `git commit -am "Description"`

Always test in SITL before deploying to hardware.

---

## Additional Resources

- [ArduPilot Build Guide](https://ardupilot.org/dev/docs/building-setup-linux.html)
- [WAF Build System](https://ardupilot.org/dev/docs/waf.html)
- [Supported Boards](https://ardupilot.org/plane/docs/common-autopilots.html)
- [Developer Documentation](https://ardupilot.org/dev/)
- [Contributing Guide](https://ardupilot.org/dev/docs/contributing.html)
- [ArduPilot Discord](https://ardupilot.org/discord)
- [Discourse Forums](https://discuss.ardupilot.org/)

## Next Steps

1. **Run SITL** - Test your build ([SITL Guide](../SITL_Mission_Plans/))
2. **Explore Codebase** - Understand ArduPilot architecture ([Sensor Drivers](../Sensor_Drivers/))
3. **Contribute** - Learn the contribution workflow ([Advanced Topics](../Advanced_Topics/Code_Contribution_Workflow/))
