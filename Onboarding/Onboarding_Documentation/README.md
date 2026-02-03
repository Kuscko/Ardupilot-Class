# Onboarding Documentation

## Getting Started with ArduPilot Onboarding

This guide is designed to help new team members ramp up quickly on ArduPilot, SITL, MAVLink, Lua scripting, and related tools. Follow these steps and document your findings for future onboarding.

### 1. ArduPilot Familiarization
- Main task: Develop an in-depth understanding of ArduPilot.
- Explore the [ArduPilot Plane Wiki](https://ardupilot.org/plane/index.html).
- Build the ArduPilot codebase in WSL/Linux. Document build steps, issues, and solutions.
- Locate where sensor drivers live in the ArduPilot codebase.
- Learn general EKF (Extended Kalman Filter) concepts relevant to ArduPilot.

### 2. SITL Mission Planning
- Create and run mission plans in SITL (Software In The Loop).
- Get familiar with parameters: TECS tuning, failsafes, Auto tune PIDs, Serial/hardware parameters.
- Document your test scenarios and parameter explorations in the SITL_Mission_Plans folder.

### 3. MAVLink & Mavlink Router
- Teach yourself about MAVLink protocol and Mavlink Router.
- Use the [MAVLink Common Messages Wiki](https://mavlink.io/en/messages/common.html).
- Document useful commands, message types, and router setup in the MAVLink_MavlinkRouter folder.

### 4. Lua Scripting in ArduPilot
- Learn how to load Lua scripts into ArduPilot.
- Create and run a Lua script in SITL.
- Document your Lua experiments and findings in the Lua_Scripts folder.

### 5. Installation & Troubleshooting
- Use and update installation scripts for ArduPilot (especially 4.5.7 branch).
- If installation fails, check for deprecated Python packages and update scripts as needed.
- Document all changes and troubleshooting steps in the Installation_Scripts folder.

### 6. Document Everything
- Take digital notes and create slides for onboarding others.
- Add all documentation, guides, and onboarding resources to this folder and Slides_Notes.

---
**Tip:** Anything you document will be valuable for onboarding others. Keep your notes clear and up to date.