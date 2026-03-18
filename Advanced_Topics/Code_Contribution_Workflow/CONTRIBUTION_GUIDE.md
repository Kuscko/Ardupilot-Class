# ArduPilot Code Contribution Guide

Complete workflow for contributing code to ArduPilot, from forking to PR merge.

---

## Step 1: Fork and Clone

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ardupilot.git
cd ardupilot

# Add upstream remote
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

```bash
git fetch upstream
git checkout master
git merge upstream/master
git push origin master
```

---

## Step 2: Create a Feature Branch

```bash
git checkout -b my-new-feature
```

**Branch naming:**

- `feature/description` - New features
- `fix/issue-number-description` - Bug fixes
- `docs/description` - Documentation only
- `refactor/description` - Code refactoring

```bash
git checkout -b feature/add-terrain-avoidance
git checkout -b fix/3456-gps-glitch-handling
```

---

## Step 3: Make Changes

**Code style summary:**

- 4 spaces indentation (no tabs)
- Opening brace same line as statement
- Classes: `PascalCase` | Functions: `snake_case` | Members: `_prefixed_snake_case` | Constants: `ALL_CAPS`

```cpp
class AP_MyFeature {
public:
    AP_MyFeature();
    void init();
    void update(float dt);
    float get_value() const;

private:
    float _internal_value;
    uint32_t _last_update_ms;
    void calculate_output();
};

void AP_MyFeature::update(float dt)
{
    if (dt < 0.0f) {
        return;
    }
    _internal_value += dt;
    _last_update_ms = AP_HAL::millis();
    if (_internal_value > MAX_VALUE) {
        calculate_output();
    }
}
```

**SITL Testing (required):**

```bash
cd ArduPlane
./waf configure --board=sitl
./waf plane
Tools/autotest/sim_vehicle.py --console --map
```

**Unit tests:**

```bash
./waf tests
```

---

## Step 4: Commit Your Changes

```bash
# Stage specific files
git add path/to/file.cpp path/to/file.h
git status
git diff --cached
```

**Commit message format:**

```text
<subsystem>: <brief description>

<detailed description>
```

**Subsystem prefixes:**

`Plane:`, `Copter:`, `Rover:`, `Sub:`, `AP_AHRS:`, `AP_GPS:`, `AP_NavEKF3:`, `Tools:`, `Docs:`

**Good:**

```bash
git commit -m "Plane: add terrain following for AUTO mode

This commit adds terrain following capability when in AUTO mode.
The aircraft will maintain a constant height above terrain using
rangefinder data when available, falling back to SRTM data.

Adds new parameter TERRAIN_FOLLOW for enabling/disabling."
```

**Bad:**

```text
git commit -m "fixed bug"
git commit -m "WIP"
```

- One logical change per commit
- Reference issue numbers: `Fixes #1234`

---

## Step 5: Push to Your Fork

```bash
git push origin my-new-feature

# After rebase (use with caution)
git push origin my-new-feature --force-with-lease
```

---

## Step 6: Create Pull Request

1. Navigate to your fork on GitHub
2. Click "Compare & pull request"
3. Base: `ArduPilot/ardupilot` → `master`
4. Fill out PR template (see [PR_TEMPLATE.md](PR_TEMPLATE.md))

**PR title format:**

```text
<Subsystem>: <Brief description (max 72 characters)>
```

Examples:

```text
Plane: add terrain following for AUTO mode
AP_GPS: fix SBP driver initialization bug
```

---

## Step 7: Code Review

1. CI/CD runs automatically (builds, autotests, style checks)
2. Maintainer review typically within 1-2 weeks
3. Push new commits to same branch to address feedback

**Responding to feedback:**

```bash
vim file.cpp
git add file.cpp
git commit -m "Address review feedback: improve error handling"
git push origin my-new-feature
```

**Rebasing:**

```bash
git fetch upstream
git rebase upstream/master
# Resolve conflicts
git add <resolved-file>
git rebase --continue
git push origin my-new-feature --force-with-lease
```

---

## Step 8: After Merge

```bash
git checkout master
git fetch upstream
git merge upstream/master
git push origin master

# Delete feature branch
git branch -d my-new-feature
git push origin --delete my-new-feature
```

---

## Common Issues

### Merge Conflicts

```bash
git fetch upstream
git rebase upstream/master
git add <resolved-files>
git rebase --continue
git push origin my-new-feature --force-with-lease
```

### CI Failure

```bash
./Tools/scripts/build_astyle.sh
./waf configure --board=<platform> && ./waf
```

### Code Style Violations

```bash
./Tools/scripts/check_code_style.sh file.cpp
```

---

## Pull Request Checklist

- [ ] Code follows ArduPilot style guidelines (see [CODE_STYLE_CHECKLIST.md](CODE_STYLE_CHECKLIST.md))
- [ ] Commit messages are clear and descriptive
- [ ] Changes tested in SITL
- [ ] Documentation updated if adding features
- [ ] No unnecessary files committed (.vscode, personal configs)
- [ ] Related issues referenced
- [ ] All CI checks pass

---

- [ArduPilot Contributing Guide](https://ardupilot.org/dev/docs/contributing.html)
- [ArduPilot Coding Style](https://ardupilot.org/dev/docs/coding-style.html)
- [Git and GitHub Guide](https://ardupilot.org/dev/docs/git-and-github.html)

**Author:** Patrick Kelly (@Kuscko)
