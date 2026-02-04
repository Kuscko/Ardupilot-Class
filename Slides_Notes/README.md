# ArduPilot Learning Resources & Quick Reference

## Overview

This module provides condensed reference materials, learning checklists, and presentation outlines for ArduPilot Plane 4.5.7 development. These resources help reinforce learning, serve as quick references during development, and facilitate knowledge sharing with team members.

**What's Included:**
- Quick reference cards for common tasks
- Learning checklists to track progress
- Presentation outlines for team knowledge sharing
- Visual diagrams and flowcharts
- Troubleshooting decision trees

## Prerequisites

These materials assume you have:

- Completed initial ArduPilot setup and SITL configuration
- Basic understanding of flight controller concepts
- Experience with at least one ArduPilot module (build, SITL, or parameters)

## What You'll Find

This module contains three main reference documents:

1. **Quick Reference Card** - Common commands, parameters, and workflows
2. **Learning Checklist** - Track your progress through ArduPilot topics
3. **Presentation Outline** - Structure for teaching ArduPilot to others

## Quick Reference Card

**[QUICK_REFERENCE_CARD.md](QUICK_REFERENCE_CARD.md)** provides one-page summaries of:

### Essential Commands

**SITL:**
```bash
sim_vehicle.py --console --map        # Start SITL with console and map
sim_vehicle.py -w                     # Wipe parameters to defaults
sim_vehicle.py --location CMAC        # Start at specific location
```

**MAVProxy:**
```bash
mode AUTO               # Switch to autonomous mode
arm throttle            # Arm vehicle
wp load mission.txt     # Load mission file
param set PARAM VALUE   # Set parameter
status                  # Check vehicle status
```

**Build:**
```bash
./waf configure --board sitl    # Configure for SITL
./waf plane                     # Build ArduPlane
./waf list_boards               # List available boards
```

### Critical Parameters

**Flight Control:**
- `ARMING_CHECK` - Pre-arm safety checks
- `TRIM_ARSPD_CM` - Target airspeed (cm/s)
- `WP_RADIUS` - Waypoint acceptance radius (m)
- `RTL_ALTITUDE` - Return-to-launch altitude (cm)

**TECS (Energy Management):**
- `TECS_PITCH_MAX/MIN` - Pitch limits (degrees)
- `TECS_CLMB_MAX` - Max climb rate (m/s)
- `TECS_SPDWEIGHT` - Speed vs altitude priority (0-2)

**EKF (State Estimation):**
- `EK3_ENABLE` - Enable EKF3 (1=enabled)
- `EK3_SRC1_POSXY` - Position source (3=GPS)
- `EK3_GPS_TYPE` - GPS usage mode

**Failsafes:**
- `FS_SHORT_ACTN` - Short failsafe action (0=continue, 1=RTL)
- `FS_LONG_ACTN` - Long failsafe action
- `BATT_FS_LOW_ACT` - Low battery action

### Common Workflows

**First Flight Checklist:**
1. Build and verify ArduPilot
2. Start SITL and check pre-arm status
3. Arm vehicle and test manual control
4. Load simple mission
5. Test AUTO mode
6. Verify RTL functionality

**Parameter Tuning:**
1. Load baseline parameters
2. Make incremental changes (one at a time)
3. Test in SITL
4. Analyze logs
5. Document changes and results
6. Repeat until satisfied

**Troubleshooting Steps:**
1. Check `status` command output
2. Review pre-arm checks
3. Verify sensor health (GPS, EKF, IMU)
4. Check parameter values
5. Review flight logs
6. Search ArduPilot forums/Discord

See **[QUICK_REFERENCE_CARD.md](QUICK_REFERENCE_CARD.md)** for complete reference.

## Learning Checklist

**[ONBOARDING_CHECKLIST.md](ONBOARDING_CHECKLIST.md)** helps you track progress through ArduPilot topics:

### Week 1: Environment Setup
- [ ] Install WSL2/Ubuntu
- [ ] Build ArduPilot from source
- [ ] Run first SITL simulation
- [ ] Understand MAVProxy basics
- [ ] Load and modify parameters

### Week 2: Core Concepts
- [ ] Study flight modes
- [ ] Learn EKF fundamentals
- [ ] Understand sensor drivers
- [ ] Explore codebase structure
- [ ] Read MAVLink messages

### Week 3: Mission Planning
- [ ] Create simple waypoint mission
- [ ] Test autonomous flight in SITL
- [ ] Tune TECS parameters
- [ ] Configure failsafes
- [ ] Analyze flight logs

### Week 4: Advanced Topics
- [ ] Write Lua script
- [ ] Set up mavlink-router
- [ ] Test GPS-denied scenarios
- [ ] Simulate sensor failures
- [ ] Optimize performance

### Weeks 5-8: Specialization
- [ ] Choose advanced topics based on project needs
- [ ] PID tuning for specific aircraft
- [ ] Custom hardware integration
- [ ] Companion computer setup
- [ ] Code contributions

The checklist includes estimated time for each task and links to relevant modules.

See **[ONBOARDING_CHECKLIST.md](ONBOARDING_CHECKLIST.md)** for complete checklist.

## Presentation Outline

**[ONBOARDING_PRESENTATION_OUTLINE.md](ONBOARDING_PRESENTATION_OUTLINE.md)** provides structure for teaching ArduPilot to new team members:

### Presentation Structure

**Session 1: Introduction (1 hour)**
- ArduPilot overview and history
- Supported vehicles and hardware
- Development environment setup
- First SITL demonstration

**Session 2: Core Architecture (1.5 hours)**
- Codebase structure
- Sensor driver architecture
- Flight mode system
- MAVLink communication
- EKF state estimation

**Session 3: Mission Planning (1.5 hours)**
- SITL demonstration
- Waypoint mission creation
- Flight modes walkthrough
- Parameter tuning basics
- Failsafe configuration

**Session 4: Advanced Development (2 hours)**
- Lua scripting examples
- Custom code modifications
- Debugging techniques
- Log analysis
- Contributing to ArduPilot

**Session 5: Hands-On Workshop (2-3 hours)**
- Build ArduPilot from source
- Create and run custom mission
- Tune parameters for scenario
- Debug simulated failures
- Q&A and troubleshooting

### Teaching Tips

**For Presenters:**
- Start with live SITL demo to build excitement
- Keep theory short, focus on hands-on practice
- Provide example missions and parameter files
- Share common pitfalls and solutions
- Encourage questions and experimentation

**For Learners:**
- Follow along with your own SITL instance
- Take notes on commands and parameters
- Ask questions when concepts are unclear
- Complete exercises between sessions
- Join ArduPilot Discord for community support

See **[ONBOARDING_PRESENTATION_OUTLINE.md](ONBOARDING_PRESENTATION_OUTLINE.md)** for complete presentation guide with slide suggestions.

## Using These Resources

### As a Learner

**Daily Reference:**
- Keep Quick Reference Card open during development
- Check off completed items in Learning Checklist
- Review troubleshooting flowcharts when stuck

**Progress Tracking:**
- Update checklist weekly
- Set realistic goals (2-3 topics per week)
- Don't rush - deep understanding takes time

**Knowledge Reinforcement:**
- Revisit reference materials regularly
- Practice commands until they become second nature
- Teach concepts to others to solidify learning

### As a Team Lead

**Onboarding New Members:**
- Share Presentation Outline before first meeting
- Walk through Quick Reference Card together
- Assign Learning Checklist as homework
- Schedule weekly check-ins to discuss progress

**Knowledge Sharing:**
- Use Presentation Outline for team meetings
- Create internal wiki pages from reference materials
- Record demo videos for asynchronous learning
- Encourage peer-to-peer teaching

**Team Standards:**
- Establish common parameter baselines
- Document team-specific workflows
- Share lessons learned and troubleshooting tips
- Maintain internal FAQ based on common questions

## Additional Reference Materials

### Visual Learning Aids

Consider creating (or requesting from community):
- ArduPilot architecture diagrams
- Flight mode state machine flowcharts
- Parameter tuning decision trees
- Sensor fusion visualization
- MAVLink message sequence diagrams

### Recommended External Resources

**Official Documentation:**
- [ArduPilot Docs](https://ardupilot.org/plane/) - Comprehensive user and developer guides
- [ArduPilot Wiki](https://ardupilot.org/dev/) - Developer documentation
- [MAVLink Guide](https://mavlink.io/en/) - Protocol specification

**Community Resources:**
- [ArduPilot Discord](https://ardupilot.org/discord) - Real-time help and discussion
- [Discourse Forums](https://discuss.ardupilot.org/) - Searchable Q&A archive
- [GitHub Repository](https://github.com/ArduPilot/ardupilot) - Source code and issues

**Video Tutorials:**
- [ArduPilot YouTube Channel](https://www.youtube.com/c/ArduPilot) - Official tutorials
- Conference talks on ArduPilot development
- Community-created walkthroughs

### Study Groups and Mentorship

**Finding Help:**
- Post questions on Discourse with clear problem descriptions
- Join Discord and ask in appropriate channels
- Search existing issues on GitHub
- Attend virtual or in-person ArduPilot meetups

**Giving Back:**
- Answer questions from newer learners
- Share your parameter files and missions
- Document solutions to problems you've solved
- Contribute to documentation or code

## Maintaining These Resources

### Keeping Materials Current

As ArduPilot evolves, update reference materials:
- Verify commands work with current version
- Update parameter names if changed
- Add new features to checklists
- Revise presentation outline based on feedback

### Customization for Your Team

Adapt materials to your specific needs:
- Add team-specific parameters to Quick Reference
- Include internal tools and workflows
- Highlight project-relevant topics in Checklist
- Tailor Presentation Outline to audience background

### Contributing Improvements

If you create valuable reference materials:
- Share on ArduPilot Discourse
- Submit to ArduPilot wiki
- Post in Discord for feedback
- Consider pull request to documentation repo

## Next Steps

After reviewing these reference materials:

1. **Bookmark Quick Reference** - Keep handy during development
2. **Print Learning Checklist** - Track progress physically
3. **Schedule Presentation** - Share knowledge with team
4. **Create Custom References** - Add project-specific notes
5. **Stay Connected** - Join ArduPilot community channels

### Suggested Learning Path

**Beginners:**
- Start with Quick Reference Card essentials
- Follow Learning Checklist week by week
- Ask questions early and often
- Complete all hands-on exercises

**Intermediate Users:**
- Use Quick Reference to reinforce knowledge
- Focus on advanced topics in Checklist
- Teach others using Presentation Outline
- Contribute to documentation

**Advanced Users:**
- Maintain custom reference materials for team
- Mentor new developers
- Present at meetups or conferences
- Contribute code and documentation to ArduPilot

---

**Remember:** Learning ArduPilot is a journey, not a destination. These reference materials are tools to support your continuous growth as an ArduPilot developer. Be patient with yourself, celebrate small victories, and stay curious!

---

**Additional Resources:**

- [ArduPilot Learning Pathway](https://ardupilot.org/dev/docs/learning-ardupilot-introduction.html) - Official learning guide
- [ArduPilot Glossary](https://ardupilot.org/plane/docs/common-glossary.html) - Terms and definitions
- [Contributing Guide](https://ardupilot.org/dev/docs/contributing.html) - How to give back

**Community:**

- [Discord](https://ardupilot.org/discord) - Real-time chat
- [Discourse Forums](https://discuss.ardupilot.org/) - Q&A and discussions
- [Developer Calls](https://ardupilot.org/dev/docs/dev-call.html) - Weekly online meetings
