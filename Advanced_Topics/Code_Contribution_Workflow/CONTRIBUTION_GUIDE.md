# ArduPilot Code Contribution Guide

## Overview

This guide covers the complete workflow for contributing code to the ArduPilot project, from forking the repository to getting your pull request merged.

---

## Prerequisites

Before contributing, ensure you have:
- Git installed and configured
- GitHub account created
- ArduPilot development environment set up
- Basic understanding of C++ and ArduPilot architecture

---

## Step 1: Fork and Clone

### Fork the Repository

1. Navigate to https://github.com/ArduPilot/ardupilot
2. Click "Fork" button (top right)
3. Select your GitHub account as the destination

### Clone Your Fork

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ardupilot.git
cd ardupilot

# Add upstream remote (original ArduPilot repository)
git remote add upstream https://github.com/ArduPilot/ardupilot.git

# Verify remotes
git remote -v
# Should show:
# origin    https://github.com/YOUR_USERNAME/ardupilot.git (fetch)
# origin    https://github.com/YOUR_USERNAME/ardupilot.git (push)
# upstream  https://github.com/ArduPilot/ardupilot.git (fetch)
# upstream  https://github.com/ArduPilot/ardupilot.git (push)
```

### Sync with Upstream

Always sync with upstream before creating a new branch:

```bash
# Fetch latest changes from upstream
git fetch upstream

# Switch to master branch
git checkout master

# Merge upstream changes
git merge upstream/master

# Push to your fork
git push origin master
```

---

## Step 2: Create a Feature Branch

Always create a new branch for your changes:

```bash
# Create and switch to new branch
git checkout -b my-new-feature

# Or separate commands:
# git branch my-new-feature
# git checkout my-new-feature
```

**Branch naming conventions:**
- `feature/description` - New features
- `fix/issue-number-description` - Bug fixes
- `docs/description` - Documentation only
- `refactor/description` - Code refactoring

**Examples:**
```bash
git checkout -b feature/add-terrain-avoidance
git checkout -b fix/3456-gps-glitch-handling
git checkout -b docs/update-lua-api
```

---

## Step 3: Make Changes

### Code Style Guidelines

ArduPilot follows strict code style conventions:

**Indentation:**
- Use 4 spaces (no tabs)
- Indent continuation lines by 4 spaces

**Braces:**
- Opening brace on same line as statement
- Closing brace on own line
- Always use braces, even for single-line blocks

**Naming Conventions:**
- Classes: `PascalCase` (e.g., `AP_AHRS`, `NavEKF3`)
- Functions: `snake_case` (e.g., `get_position()`, `update_nav()`)
- Member variables: `_prefixed_snake_case` (e.g., `_velocity`, `_gps_data`)
- Constants: `ALL_CAPS` (e.g., `MAX_SPEED`, `DEFAULT_ALT`)
- Enums: `PascalCase` with values in `ALL_CAPS`

**Example:**
```cpp
class AP_MyFeature {
public:
    // Constructor
    AP_MyFeature();

    // Public methods
    void init();
    void update(float dt);
    float get_value() const;

private:
    // Private member variables
    float _internal_value;
    uint32_t _last_update_ms;

    // Private methods
    void calculate_output();
};

void AP_MyFeature::update(float dt)
{
    // Check parameter validity
    if (dt < 0.0f) {
        return;
    }

    // Update internal state
    _internal_value += dt;
    _last_update_ms = AP_HAL::millis();

    // Complex calculations
    if (_internal_value > MAX_VALUE) {
        calculate_output();
    }
}
```

**Comments:**
- Use `//` for single-line comments
- Use `/* */` for multi-line comments
- Document complex algorithms
- Explain "why", not "what"

**Header Includes:**
- System headers first (`#include <stdio.h>`)
- Then library headers (`#include <AP_Math/AP_Math.h>`)
- Group by subsystem
- Alphabetize within groups

### Testing Your Changes

**SITL Testing (Required):**
```bash
# Build for SITL
cd ArduPlane
./waf configure --board=sitl
./waf plane

# Run SITL
Tools/autotest/sim_vehicle.py --console --map

# Test your changes thoroughly
# - Verify basic functionality
# - Test edge cases
# - Check for unintended side effects
```

**Hardware Testing (Recommended):**
- If possible, test on real hardware
- Use test bench before flight testing
- Document hardware test results

**Unit Tests:**
```bash
# Run existing unit tests
./waf tests

# Add unit tests for new features if applicable
```

---

## Step 4: Commit Your Changes

### Stage Changes

```bash
# Stage specific files
git add path/to/file.cpp path/to/file.h

# Check what will be committed
git status
git diff --cached
```

### Write Commit Message

**Commit message format:**
```
<subsystem>: <brief description>

<detailed description>

<optional additional details>
```

**Subsystem prefixes:**
- `Plane:` - ArduPlane specific
- `Copter:` - ArduCopter specific
- `Rover:` - ArduRover specific
- `Sub:` - ArduSub specific
- `AP_AHRS:` - AHRS library
- `AP_GPS:` - GPS library
- `AP_NavEKF3:` - EKF library
- `Tools:` - Build tools, scripts
- `Docs:` - Documentation

**Example commit messages:**

**Good:**
```bash
git commit -m "Plane: add terrain following for AUTO mode

This commit adds terrain following capability when in AUTO mode.
The aircraft will maintain a constant height above terrain using
rangefinder data when available, falling back to SRTM data.

Adds new parameter TERRAIN_FOLLOW for enabling/disabling.
```

**Bad:**
```
git commit -m "fixed bug"
git commit -m "WIP"
git commit -m "Updated files"
```

### Commit Guidelines

- One logical change per commit
- Keep commits focused and atomic
- Don't mix formatting changes with functional changes
- Reference issue numbers if applicable: `Fixes #1234`

---

## Step 5: Push to Your Fork

```bash
# Push your branch to your fork
git push origin my-new-feature

# If you've rebased and need to force push (use with caution)
git push origin my-new-feature --force-with-lease
```

---

## Step 6: Create Pull Request

### Via GitHub Website

1. Navigate to your fork on GitHub
2. Click "Compare & pull request" button
3. Select base repository: `ArduPilot/ardupilot`
4. Select base branch: `master`
5. Select your compare branch: `my-new-feature`
6. Fill out PR template (see PR_TEMPLATE.md)
7. Click "Create pull request"

### PR Title Format

```
<Subsystem>: <Brief description (max 72 characters)>
```

**Examples:**
```
Plane: add terrain following for AUTO mode
AP_GPS: fix SBP driver initialization bug
Copter: improve position controller stability
```

### PR Description

Use the provided PR template and include:
- **Summary:** What does this PR do?
- **Testing:** How was it tested?
- **Documentation:** Were docs updated?
- **Breaking Changes:** Any compatibility issues?
- **Related Issues:** Link to GitHub issues

---

## Step 7: Code Review Process

### What to Expect

1. **Automated Checks:** CI/CD will run automatically
   - Build tests for all platforms
   - Autotest suite
   - Code style checks

2. **Maintainer Review:** ArduPilot developers will review
   - Usually within 1-2 weeks
   - May request changes
   - May ask questions

3. **Revisions:** Be prepared to make changes
   - Address all review comments
   - Push new commits to same branch
   - PR will update automatically

### Responding to Review Comments

**Make requested changes:**
```bash
# Make changes to files
vim file.cpp

# Stage and commit
git add file.cpp
git commit -m "Address review feedback: improve error handling"

# Push to update PR
git push origin my-new-feature
```

**Rebasing (if requested):**
```bash
# Fetch latest upstream
git fetch upstream

# Rebase your branch
git rebase upstream/master

# Resolve any conflicts
# Fix conflicts in files, then:
git add <resolved-file>
git rebase --continue

# Force push (required after rebase)
git push origin my-new-feature --force-with-lease
```

---

## Step 8: PR Merge

Once approved:
- Maintainer will merge your PR
- Your changes become part of ArduPilot!
- PR will be closed automatically
- Delete your feature branch

```bash
# After PR is merged, sync your fork
git checkout master
git fetch upstream
git merge upstream/master
git push origin master

# Delete feature branch (optional)
git branch -d my-new-feature
git push origin --delete my-new-feature
```

---

## Best Practices

1. **Keep PRs Focused:**
   - One feature/fix per PR
   - Easier to review
   - Faster to merge

2. **Write Good Commit Messages:**
   - Explain the "why", not just the "what"
   - Reference issues and PRs
   - Follow established format

3. **Test Thoroughly:**
   - Test in SITL before PR
   - Test on hardware if possible
   - Include test results in PR

4. **Stay Up to Date:**
   - Regularly sync with upstream
   - Rebase if conflicts occur
   - Keep PR current

5. **Be Responsive:**
   - Respond to review comments promptly
   - Ask questions if unclear
   - Be professional and courteous

6. **Follow Code Style:**
   - Use code style checker
   - Match existing code style
   - See CODE_STYLE_CHECKLIST.md

---

## Common Issues and Solutions

### Merge Conflicts

**Cause:** Upstream master has changed since you branched

**Solution:**
```bash
git fetch upstream
git rebase upstream/master

# Resolve conflicts
# Edit conflicted files
git add <resolved-files>
git rebase --continue

git push origin my-new-feature --force-with-lease
```

### CI Failure

**Cause:** Build fails on some platforms

**Solution:**
1. Check CI logs for errors
2. Fix build issues locally
3. Test with: `./waf configure --board=<platform> && ./waf`
4. Push fix to PR

### Code Style Violations

**Cause:** Code doesn't follow ArduPilot style

**Solution:**
```bash
# Run code style checker
./Tools/scripts/check_code_style.sh file.cpp

# Fix issues
# Re-commit
```

---

## Resources

**Official Documentation:**
- [ArduPilot Contributing Guide](https://ardupilot.org/dev/docs/contributing.html)
- [Coding Style Guide](https://ardupilot.org/dev/docs/code-style.html)
- [Developer Wiki](https://ardupilot.org/dev/)

**Communication Channels:**
- [ArduPilot Discourse](https://discuss.ardupilot.org/)
- [Discord](https://ardupilot.org/discord)
- [GitHub Discussions](https://github.com/ArduPilot/ardupilot/discussions)

**Tools:**
- [GitHub PR Template](PR_TEMPLATE.md)
- [Code Style Checklist](CODE_STYLE_CHECKLIST.md)

---

**Author:** Patrick Kelly (@Kuscko)
**Version:** 2.0
**Last Updated:** 2026-02-03
