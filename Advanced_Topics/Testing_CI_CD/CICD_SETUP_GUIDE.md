# CI/CD Setup Guide for ArduPilot Development

**Author:** Patrick Kelly (@Kuscko)

---

## ArduPilot CI Pipeline

```
Code Change → Pre-commit Hooks → Push to GitHub → GitHub Actions
                                                         ↓
                                    Build Tests ← Style Checks
                                         ↓              ↓
                                    Unit Tests → Integration Tests
                                         ↓              ↓
                                    SITL Tests → Hardware Tests (if applicable)
                                         ↓
                                    Report Results
```

---

## Pre-Commit Hooks

### Method 1: Manual Hook Installation

```bash
cd ~/ardupilot

# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# ArduPilot pre-commit hook

echo "Running pre-commit checks..."

# Check for trailing whitespace
git diff-index --check --cached HEAD --
if [ $? -ne 0 ]; then
    echo "ERROR: Trailing whitespace detected"
    exit 1
fi

# Check for tabs (ArduPilot uses spaces)
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(cpp|h|py)$')
if [ -n "$FILES" ]; then
    for file in $FILES; do
        if grep -P '\t' "$file" > /dev/null; then
            echo "ERROR: Tab characters found in $file (use spaces)"
            exit 1
        fi
    done
fi

# Check C++ code style with astyle (if available)
if command -v astyle > /dev/null; then
    for file in $(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(cpp|h)$'); do
        # Check if file matches ArduPilot style
        astyle --dry-run --options=Tools/CodeStyle/astylerc < "$file" | diff -q - "$file" > /dev/null
        if [ $? -ne 0 ]; then
            echo "ERROR: $file does not match code style"
            echo "  Run: ./Tools/CodeStyle/run_astyle.sh"
            exit 1
        fi
    done
fi

# Check Python code style with flake8 (if available)
if command -v flake8 > /dev/null; then
    for file in $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$'); do
        flake8 "$file"
        if [ $? -ne 0 ]; then
            echo "ERROR: Python style check failed for $file"
            exit 1
        fi
    done
fi

echo "Pre-commit checks passed!"
exit 0
EOF

# Make executable
chmod +x .git/hooks/pre-commit
```

### Method 2: Python Pre-Commit Framework

```bash
# Install pre-commit framework
pip install pre-commit

# Create .pre-commit-config.yaml in ardupilot root
cat > ~/.pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
        exclude: '\.patch$'
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/PyCQA/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: ['--max-line-length=120', '--ignore=E501,W503']
        files: '\.py$'

  - repo: local
    hooks:
      - id: check-no-tabs
        name: Check for tabs
        entry: 'grep -P "\\t"'
        language: system
        files: '\.(cpp|h|py)$'
        pass_filenames: true
EOF

# Install hooks
cd ~/ardupilot
pre-commit install

# Run on all files (optional)
pre-commit run --all-files
```

### Check Commit Message Format

```bash
# .git/hooks/commit-msg
#!/bin/bash

COMMIT_MSG_FILE=$1
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# Check commit message format
# Format: "Component: Brief description"
if ! echo "$COMMIT_MSG" | grep -qE '^[A-Z][a-zA-Z0-9_]+: .+'; then
    echo "ERROR: Commit message must follow format: 'Component: Description'"
    echo "  Examples:"
    echo "    Plane: Fix altitude hold bug"
    echo "    AP_AHRS: Add EKF3 support"
    exit 1
fi

# Check message length (first line should be < 72 chars)
FIRST_LINE=$(echo "$COMMIT_MSG" | head -n1)
if [ ${#FIRST_LINE} -gt 72 ]; then
    echo "ERROR: First line of commit message too long (${#FIRST_LINE} > 72)"
    exit 1
fi

exit 0
```

### Prevent Committing Debug Code

```bash
# Add to pre-commit hook
# Check for debug statements
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(cpp|h|py)$')
for file in $FILES; do
    # Check for common debug patterns
    if grep -nE '(printf.*DEBUG|cout.*DEBUG|Serial\.println.*DEBUG)' "$file"; then
        echo "ERROR: Debug statement found in $file"
        echo "  Remove debug code before committing"
        exit 1
    fi
done
```

---

## GitHub Actions Workflows

ArduPilot's official CI workflows: `https://github.com/ArduPilot/ardupilot/tree/master/.github/workflows`

### Basic Build Test Workflow

Create `.github/workflows/build-test.yml`:

```yaml
name: Build and Test

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  build-sitl:
    runs-on: ubuntu-22.04

    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      with:
        submodules: recursive

    - name: Install dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y \
          build-essential \
          python3-dev \
          python3-pip \
          ccache \
          g++ \
          gawk \
          git \
          make \
          wget

        # Install Python dependencies
        pip3 install --user -U \
          pymavlink \
          MAVProxy \
          pyserial

    - name: Setup ccache
      uses: actions/cache@v3
      with:
        path: ~/.ccache
        key: ${{ runner.os }}-ccache-${{ github.sha }}
        restore-keys: |
          ${{ runner.os }}-ccache-

    - name: Build ArduPlane SITL
      run: |
        cd ArduPlane
        ../Tools/autotest/autotest.py --no-configure build.ArduPlane

    - name: Build ArduCopter SITL
      run: |
        cd ArduCopter
        ../Tools/autotest/autotest.py --no-configure build.ArduCopter
```

### Autotest Workflow

Create `.github/workflows/autotest.yml`:

```yaml
name: Autotest

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  autotest-plane:
    runs-on: ubuntu-22.04
    timeout-minutes: 60

    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      with:
        submodules: recursive

    - name: Install dependencies
      run: |
        # Add ArduPilot apt repository
        sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 0xB4711E8B
        sudo add-apt-repository -y ppa:ardupilot/ppa

        # Install packages
        sudo apt-get update
        sudo apt-get install -y \
          python3-matplotlib \
          python3-serial \
          python3-wxgtk4.0 \
          python3-wxtools \
          python3-lxml \
          python3-scipy \
          python3-opencv \
          xvfb

        # Install additional Python packages
        pip3 install --user \
          pymavlink \
          MAVProxy \
          pexpect

    - name: Run ArduPlane autotests
      run: |
        cd Tools/autotest
        # Run in headless mode with xvfb
        xvfb-run -a ./autotest.py --vehicle=Plane --timeout=3600

    - name: Upload test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: autotest-results
        path: |
          Tools/autotest/buildlogs/
          *.BIN
          *.tlog
```

### Code Style Check Workflow

Create `.github/workflows/style-check.yml`:

```yaml
name: Code Style Check

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  style-check:
    runs-on: ubuntu-22.04

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Install astyle
      run: |
        sudo apt-get update
        sudo apt-get install -y astyle=3.1-2

    - name: Check C++ code style
      run: |
        # Run astyle check
        ./Tools/CodeStyle/run_astyle.sh --dry-run

        # Check if any files would be modified
        git diff --exit-code
        if [ $? -ne 0 ]; then
          echo "Code style issues found. Run ./Tools/CodeStyle/run_astyle.sh"
          exit 1
        fi

    - name: Check for trailing whitespace
      run: |
        # Check for trailing whitespace
        if git grep -I -n -P '[ \t]+$' -- '*.cpp' '*.h' '*.py'; then
          echo "Trailing whitespace found"
          exit 1
        fi

    - name: Check for tabs
      run: |
        # Check for tabs in source files
        if git grep -I -n -P '\t' -- '*.cpp' '*.h'; then
          echo "Tabs found in source files (use spaces)"
          exit 1
        fi
```

### Unit Test Workflow

Create `.github/workflows/unit-tests.yml`:

```yaml
name: Unit Tests

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  unit-tests:
    runs-on: ubuntu-22.04

    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      with:
        submodules: recursive

    - name: Install dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y \
          build-essential \
          python3-dev \
          libgtest-dev

        # Build Google Test
        cd /usr/src/gtest
        sudo cmake CMakeLists.txt
        sudo make
        sudo cp lib/*.a /usr/lib

    - name: Build unit tests
      run: |
        ./waf configure --board=linux
        ./waf tests

    - name: Run unit tests
      run: |
        ./build/linux/tests/test_*
```

### Workflow Triggers

```yaml
# Trigger on push to specific branches
on:
  push:
    branches:
      - main
      - develop
    paths:
      - 'libraries/**'
      - 'ArduPlane/**'

# Trigger on pull requests
on:
  pull_request:
    types: [opened, synchronize, reopened]

# Trigger on schedule (nightly builds)
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

# Manual trigger
on:
  workflow_dispatch:
```

---

## Local Testing Setup

```bash
# 1. Build all vehicles
cd ~/ardupilot
./waf configure --board=sitl
./waf plane copter rover sub

# 2. Run unit tests
./waf tests
./build/sitl/tests/test_*

# 3. Run code style check
./Tools/CodeStyle/run_astyle.sh

# 4. Run specific autotest
cd Tools/autotest
./autotest.py --vehicle=Plane --test=Missions

# 5. Run all autotests (takes ~2 hours)
./autotest.py --vehicle=Plane
```

### Docker Testing Environment

```dockerfile
# Dockerfile for ArduPilot CI
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    ccache \
    g++ \
    gawk \
    git \
    make \
    python3-dev \
    python3-pip \
    wget

# Install Python packages
RUN pip3 install --user \
    pymavlink \
    MAVProxy \
    pyserial \
    empy

# Set up workspace
WORKDIR /ardupilot
COPY . .

# Configure ccache
ENV PATH="/usr/lib/ccache:${PATH}"
ENV CCACHE_DIR=/tmp/ccache

# Build
RUN ./waf configure --board=sitl && ./waf plane

# Run tests
CMD ["./Tools/autotest/autotest.py", "--vehicle=Plane"]
```

```bash
# Build Docker image
docker build -t ardupilot-ci .

# Run tests in Docker
docker run --rm -v $(pwd):/ardupilot ardupilot-ci
```

---

## ArduPilot CI Integration

ArduPilot's CI runs on every pull request:

1. **Build Tests**: Compile for all boards
2. **Unit Tests**: C++ unit tests
3. **SITL Tests**: Autotest suite
4. **Style Checks**: Code formatting
5. **Submodule Checks**: Verify submodules

### Viewing CI Results

1. Go to your PR on GitHub
2. Scroll to "Checks" section
3. Click on failing check for details
4. Review logs and fix issues

### Common CI Failures

```text
Build Failure:
Solution: Ensure code compiles locally first
./waf configure --board=sitl
./waf plane
```

```text
Style Check Failure:
Solution: Run astyle locally
./Tools/CodeStyle/run_astyle.sh
git add -u
git commit -m "Fix code style"
```

```text
Autotest Failure:
Solution: Run specific test locally
cd Tools/autotest
./autotest.py --vehicle=Plane --test=FailingTest --debug
```

---

## Best Practices

### Development Workflow

```text
1. Create feature branch
   git checkout -b feature/my-feature

2. Make changes and commit frequently
   git add .
   git commit -m "Component: Description"
   (Pre-commit hooks run automatically)

3. Test locally before pushing
   ./waf build
   ./waf tests
   ./Tools/autotest/autotest.py --vehicle=Plane

4. Push to fork
   git push origin feature/my-feature
   (GitHub Actions run automatically)

5. Monitor CI results
   Check GitHub Actions tab

6. Fix any issues
   git commit -m "Fix CI issues"
   git push

7. Create pull request when CI passes
```

### Performance Optimization

```bash
# Install ccache
sudo apt-get install ccache

# Configure git to use ccache
git config --global ccache.path /usr/lib/ccache
```

```yaml
- uses: actions/cache@v3
  with:
    path: |
      ~/.cache/pip
      ~/.ccache
    key: ${{ runner.os }}-build-${{ hashFiles('**/requirements.txt') }}
```

### Security Best Practices

1. Never commit secrets — use GitHub Secrets for API keys, add `.env` to `.gitignore`
2. Review third-party actions — only use trusted actions, pin to specific versions (not `@master`)
3. Limit permissions:

```yaml
permissions:
  contents: read
  pull-requests: write
```

### Debugging CI Failures

```yaml
- name: Debug
  if: failure()
  run: |
    cat /var/log/syslog
    dmesg
```

```yaml
- uses: actions/upload-artifact@v3
  if: always()
  with:
    name: debug-logs
    path: |
      *.log
      *.BIN
```

---

## Quick Reference

### Pre-Commit Hook Commands

```bash
# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files

# Update hooks
pre-commit autoupdate

# Skip hooks (emergency only)
git commit --no-verify
```

### GitHub Actions Commands

```bash
# View workflow runs
gh run list

# View specific run
gh run view RUN_ID

# Re-run failed jobs
gh run rerun RUN_ID

# Download artifacts
gh run download RUN_ID
```

### Local Testing Checklist

- [ ] Build all vehicles successfully
- [ ] Run unit tests (all pass)
- [ ] Run code style check (no issues)
- [ ] Run relevant autotests (all pass)
- [ ] Check for memory leaks (valgrind)
- [ ] Review code coverage
- [ ] Test on actual hardware (if possible)

---

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pre-Commit Framework](https://pre-commit.com/)
- [ArduPilot Testing Guide](TESTING_GUIDE.md)
- [ArduPilot Autotest Examples](example_autotest_custom.py)
