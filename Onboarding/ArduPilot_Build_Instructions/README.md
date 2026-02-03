# ArduPilot Build Instructions — Agent Onboarding

## Purpose
This document provides agent-style onboarding instructions for building the ArduPilot codebase (Plane 4.5.7) in WSL/Linux, including troubleshooting and documenting any changes required for the 4.5.7 branch.

## Agent Instructions & TODO List

### 1. Environment Setup
- [ ] Install WSL2 and Ubuntu 22.04 LTS on Windows
- [ ] Update and upgrade packages (`sudo apt update && sudo apt upgrade -y`)
- [ ] Install build dependencies: `git`, `python3`, `python3-pip`
- [ ] Clone ArduPilot repo, checkout Plane-4.5.7 tag, and update submodules
- [ ] Run `install-prereqs-ubuntu.sh` and install Python packages (`pymavlink`, `mavproxy`)

### 2. Building ArduPilot
- [ ] Build for SITL: `./waf configure --board sitl` and `./waf plane`
- [ ] Build for hardware (if needed): `./waf configure --board <BOARD>`
- [ ] Document any build errors and solutions

### 3. Troubleshooting & Documentation
- [ ] If installation fails, check for deprecated Python packages and update scripts as needed
- [ ] Document any changes made to installation scripts or build process for 4.5.7
- [ ] Add troubleshooting notes for common build issues (see onboarding guide Appendix B)

### 4. References
- [ArduPilot Build Instructions](https://ardupilot.org/dev/docs/building-setup-linux.html)
- [Onboarding Guide: Environment Setup & Troubleshooting](../../../../Documents/ArduPilot_Onboarding_Guide.md)

---
**Keep this README up to date as you work through the onboarding process.**