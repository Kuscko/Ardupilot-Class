# Code Contribution Workflow

## Overview

Learn the complete workflow for contributing code to the ArduPilot project, from forking the repository to getting your pull request merged. This module covers Git workflows, code style requirements, testing procedures, and the code review process used by the ArduPilot development community [1].

**Important:** ArduPilot is a large open-source project with specific contribution guidelines. Following these practices ensures your contributions are reviewed efficiently and increases the likelihood of acceptance.

## Prerequisites

Before contributing code, you should have:

- Completed ArduPilot build setup and SITL configuration
- Experience building and testing ArduPilot locally
- Basic Git knowledge (commit, branch, push, pull)
- GitHub account with 2FA enabled
- Understanding of C++ programming basics
- Familiarity with ArduPilot architecture

## What You'll Learn

By completing this module, you will:

- Fork and clone the ArduPilot repository correctly
- Create feature branches and write meaningful commit messages
- Follow ArduPilot code style and naming conventions
- Run pre-commit checks and automated tests
- Create well-documented pull requests
- Participate effectively in code review
- Understand CI/CD checks and fix common failures
- Navigate the contribution review process

## Key Concepts

### Fork and Branch Workflow

ArduPilot uses the standard GitHub fork-and-branch workflow [1]:

1. **Fork** - Create your copy of ardupilot/ardupilot on GitHub
2. **Clone** - Clone your fork locally
3. **Branch** - Create feature branches for each change
4. **Commit** - Make commits with clear messages
5. **Push** - Push to your fork
6. **Pull Request** - Open PR from your fork to ardupilot/master

**Why Fork?** You don't have write access to the main repository, so you work in your fork and submit changes via pull requests.

### Code Style Requirements

ArduPilot enforces strict coding standards [2]:

- **Indentation:** 4 spaces (no tabs)
- **Braces:** Opening brace on same line (K&R style)
- **Naming:** CamelCase for classes, snake_case for functions/variables
- **Comments:** Doxygen-style for public APIs
- **Line length:** Maximum 120 characters

**Automated Checking:** The CI system runs `astyle` and other linters on all PRs.

### Commit Message Standards

Good commit messages are critical [3]:

```
Component: Brief summary of change (50 chars or less)

More detailed explanation of what changed and why. Wrap at 72
characters. Explain the problem this commit solves and how.

Reference any related issues: #1234
```

**Examples:**
- `AP_NavEKF: Fix GPS glitch handling in EKF3`
- `Plane: Add support for new flight mode AUTO_THERMAL`

### Testing Requirements

All contributions must include [4]:

- **SITL Testing:** Verify changes work in simulation
- **Hardware Testing:** Test on real hardware when applicable
- **Unit Tests:** Add tests for new functionality
- **Autotest:** Ensure existing autotests pass

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

# 2. Create feature branch with descriptive name
git checkout -b feature/improve-ekf-gps-handling

# 3. Make your changes (edit files)

# 4. Check what changed
git status
git diff
```

**Branch Naming:** Use descriptive names like `feature/add-xyz`, `bugfix/fix-abc`, or `docs/update-readme`.

### Exercise 3: Commit Changes

```bash
# 1. Stage specific files (avoid git add -A)
git add libraries/AP_NavEKF3/AP_NavEKF3_core.cpp
git add libraries/AP_NavEKF3/AP_NavEKF3_core.h

# 2. Commit with meaningful message
git commit -m "AP_NavEKF3: Improve GPS glitch detection

Add additional checks for GPS position jumps to reduce false
positives in GPS glitch detection. This prevents unnecessary
fallback to dead reckoning when GPS has temporary noise.

Tested in SITL with GPS noise injection."

# 3. Push to your fork
git push origin feature/improve-ekf-gps-handling
```

### Exercise 4: Create Pull Request

1. Go to your fork on GitHub
2. Click "Compare & pull request" button
3. Fill out PR template with:
   - Clear description of changes
   - Testing performed
   - Related issues
4. Submit PR and wait for CI checks
5. Respond to reviewer feedback

**Expected Timeline:** Initial review typically within 1-2 weeks for active PRs.

### Exercise 5: Code Style Check

```bash
# Install astyle (if not already installed)
sudo apt-get install astyle

# Check code style
./Tools/scripts/build_astyle.sh

# View any style issues
git diff

# If changes needed, commit them
git add .
git commit -m "AP_NavEKF3: Fix code style"
git push origin feature/improve-ekf-gps-handling
```

## Common Issues

### Issue: PR Fails CI Checks

**Symptoms:** Red X on GitHub PR, CI reports failures

**Common Causes:**
- Code style violations (astyle failures)
- Build errors on specific boards
- Failing unit tests or autotests
- Merge conflicts with master

**Solutions:**
```bash
# Update branch with latest master
git checkout master
git pull upstream master
git checkout feature/improve-ekf-gps-handling
git rebase master

# Fix conflicts if any, then
git push origin feature/improve-ekf-gps-handling --force-with-lease

# Run local checks before pushing
./Tools/scripts/build_astyle.sh
./waf configure --board sitl
./waf plane
```

### Issue: Merge Conflicts

**Symptoms:** GitHub shows "This branch has conflicts that must be resolved"

**Solution:**
```bash
# Rebase on latest master
git checkout master
git pull upstream master
git checkout feature/improve-ekf-gps-handling
git rebase master

# Resolve conflicts in editor, then
git add <resolved-files>
git rebase --continue
git push origin feature/improve-ekf-gps-handling --force-with-lease
```

### Issue: PR Review Requests Changes

**Symptoms:** Reviewer asks for modifications

**Best Practices:**
- Respond to all feedback comments
- Make requested changes in new commits (don't force-push immediately)
- Mark conversations as resolved when addressed
- Be respectful and professional
- Ask questions if requirements unclear

## Pull Request Checklist

Before submitting a PR, verify:

- [ ] Code follows ArduPilot style guidelines
- [ ] Commit messages are clear and descriptive
- [ ] Changes tested in SITL
- [ ] Changes tested on hardware (if applicable)
- [ ] Documentation updated (if adding features)
- [ ] No unnecessary files committed (.vscode, personal configs)
- [ ] PR description explains what, why, and how
- [ ] Related issues referenced
- [ ] All CI checks pass

## Additional Resources

- [ArduPilot Contributing Guide](https://ardupilot.org/dev/docs/contributing.html) [1] - Official contribution guidelines
- [ArduPilot Coding Style](https://ardupilot.org/dev/docs/coding-style.html) [2] - Style requirements
- [Git and GitHub Guide](https://ardupilot.org/dev/docs/git-and-github.html) [3] - Git workflow details
- [Testing Guide](https://ardupilot.org/dev/docs/testing-with-sitl.html) [4] - Testing requirements
- [Code Review Process](https://ardupilot.org/dev/docs/submitting-patches-back-to-master.html) [5] - Review workflow

### Community Resources

- [ArduPilot Discord](https://ardupilot.org/discord) - Get help with contributions
- [Developer Forums](https://discuss.ardupilot.org/c/development-team) - Development discussions
- [GitHub Discussions](https://github.com/ArduPilot/ardupilot/discussions) - Q&A and ideas

## Next Steps

After mastering the contribution workflow:

1. **Custom Build Configurations** - Learn to customize builds for specific needs
2. **Debugging Tools** - Master debugging techniques for development
3. **Testing & CI/CD** - Understand the automated testing infrastructure
4. **Review Open Issues** - Find issues to work on: https://github.com/ArduPilot/ardupilot/issues

---

**Sources:**

[1] https://ardupilot.org/dev/docs/contributing.html
[2] https://ardupilot.org/dev/docs/coding-style.html
[3] https://ardupilot.org/dev/docs/git-and-github.html
[4] https://ardupilot.org/dev/docs/testing-with-sitl.html
[5] https://ardupilot.org/dev/docs/submitting-patches-back-to-master.html
