# ArduPilot Code Contribution Guide

## Fork and Branch

```bash
# Fork ardupilot on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ardupilot.git
cd ardupilot

# Add upstream remote
git remote add upstream https://github.com/ArduPilot/ardupilot.git

# Create feature branch
git checkout -b my-new-feature
```

## Make Changes

**Code style:**
- 4 spaces (no tabs)
- Opening brace on same line
- Descriptive variable names
- Comments for complex logic

**Example:**
```cpp
void MyClass::my_function(float param) {
    // Check parameter validity
    if (param < 0.0f) {
        return;
    }
    
    // Process data
    _internal_value = param * 2.0f;
}
```

## Commit

```bash
git add file.cpp
git commit -m "Plane: add new feature for navigation

This commit adds...
"
```

## Create Pull Request

```bash
git push origin my-new-feature
# Create PR on GitHub
```

**PR checklist:**
- [ ] Code follows style guide
- [ ] Commit message describes change
- [ ] Tested in SITL
- [ ] Documentation updated

**Author:** Patrick Kelly (@Kuscko)
