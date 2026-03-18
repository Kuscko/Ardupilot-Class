# Code Contribution Workflow

Complete workflow for contributing code to ArduPilot: fork, branch, commit, PR, review.

## Key Concepts

### Fork and Branch Workflow

1. **Fork** - Create your copy of ardupilot/ardupilot on GitHub
2. **Clone** - Clone your fork locally
3. **Branch** - Create feature branches for each change
4. **Commit** - Make commits with clear messages
5. **Push** - Push to your fork
6. **Pull Request** - Open PR from your fork to ardupilot/master

### Code Style Requirements

- **Indentation:** 4 spaces (no tabs)
- **Braces:** Opening brace on same line (K&R style)
- **Naming:** CamelCase for classes, snake_case for functions/variables
- **Line length:** Maximum 120 characters

### Commit Message Format

```
Component: Brief summary of change (50 chars or less)

More detailed explanation. Wrap at 72 characters.
Reference any related issues: #1234
```

Examples:
- `AP_NavEKF: Fix GPS glitch handling in EKF3`
- `Plane: Add support for new flight mode AUTO_THERMAL`

## Hands-On Practice

### Exercise 1: Fork and Clone Repository

```bash
# 1. Fork ardupilot/ardupilot on GitHub (use Fork button)

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/ardupilot.git
cd ardupilot

# 3. Add upstream remote
git remote add upstream https://github.com/ArduPilot/ardupilot.git

# 4. Verify remotes
git remote -v
# Should show:
# origin    https://github.com/YOUR_USERNAME/ardupilot.git (fetch)
# origin    https://github.com/YOUR_USERNAME/ardupilot.git (push)
# upstream  https://github.com/ArduPilot/ardupilot.git (fetch)
# upstream  https://github.com/ArduPilot/ardupilot.git (push)
```

### Exercise 2: Create Feature Branch

```bash
# 1. Update master from upstream
git checkout master
git pull upstream master

# 2. Create feature branch
git checkout -b feature/improve-ekf-gps-handling

# 3. Check what changed
git status
git diff
```

### Exercise 3: Commit Changes

```bash
# Stage specific files (avoid git add -A)
git add libraries/AP_NavEKF3/AP_NavEKF3_core.cpp
git add libraries/AP_NavEKF3/AP_NavEKF3_core.h

# Commit with meaningful message
git commit -m "AP_NavEKF3: Improve GPS glitch detection

Add additional checks for GPS position jumps to reduce false
positives in GPS glitch detection.

Tested in SITL with GPS noise injection."

# Push to your fork
git push origin feature/improve-ekf-gps-handling
```

### Exercise 4: Create Pull Request

1. Go to your fork on GitHub
2. Click "Compare & pull request"
3. Fill out PR template with description, testing performed, related issues
4. Submit and wait for CI checks
5. Respond to reviewer feedback

### Exercise 5: Code Style Check

```bash
sudo apt-get install astyle
./Tools/scripts/build_astyle.sh

# Commit any style fixes
git add .
git commit -m "AP_NavEKF3: Fix code style"
git push origin feature/improve-ekf-gps-handling
```

## Common Issues

### PR Fails CI Checks

```bash
git checkout master
git pull upstream master
git checkout feature/improve-ekf-gps-handling
git rebase master
git push origin feature/improve-ekf-gps-handling --force-with-lease

./Tools/scripts/build_astyle.sh
./waf configure --board sitl
./waf plane
```

### Merge Conflicts

```bash
git checkout master
git pull upstream master
git checkout feature/improve-ekf-gps-handling
git rebase master
git add <resolved-files>
git rebase --continue
git push origin feature/improve-ekf-gps-handling --force-with-lease
```

## Pull Request Checklist

- [ ] Code follows ArduPilot style guidelines
- [ ] Commit messages are clear and descriptive
- [ ] Changes tested in SITL
- [ ] Documentation updated (if adding features)
- [ ] No unnecessary files committed (.vscode, personal configs)
- [ ] Related issues referenced
- [ ] All CI checks pass

---

- [ArduPilot Contributing Guide](https://ardupilot.org/dev/docs/contributing.html)
- [ArduPilot Coding Style](https://ardupilot.org/dev/docs/coding-style.html)
- [Git and GitHub Guide](https://ardupilot.org/dev/docs/git-and-github.html)
