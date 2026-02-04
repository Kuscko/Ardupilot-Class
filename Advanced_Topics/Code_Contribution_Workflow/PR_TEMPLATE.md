# Pull Request Template

## Summary

<!-- Brief description of what this PR does -->

## Type of Change

<!-- Mark the relevant option with an 'x' -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test addition or modification

## Related Issues

<!-- Link to related GitHub issues -->
<!-- Example: Fixes #1234, Closes #5678 -->

Fixes #

## Motivation and Context

<!-- Why is this change required? What problem does it solve? -->

## Testing

<!-- Describe the testing performed to verify changes -->

### SITL Testing

- [ ] Tested in SITL
- [ ] Vehicle type tested: <!-- ArduPlane / ArduCopter / ArduRover / ArduSub -->
- [ ] Test scenario: <!-- Describe what you tested -->

**SITL Test Results:**
<!-- Paste SITL test results or describe behavior -->

```
# Example:
# Tested square pattern mission in SITL
# Aircraft completed mission successfully
# No errors in logs
```

### Hardware Testing

- [ ] Tested on hardware
- [ ] Flight controller: <!-- e.g., Pixhawk 4, Cube Orange -->
- [ ] Test scenario: <!-- Describe hardware test -->

**Hardware Test Results:**
<!-- Describe hardware test results if applicable -->

### Unit Tests

- [ ] Added unit tests for new code
- [ ] Existing unit tests pass
- [ ] Ran `./waf tests` successfully

## Screenshots / Videos

<!-- If applicable, add screenshots or video links -->

## Code Quality

### Pre-submission Checklist

- [ ] Code follows ArduPilot style guide
- [ ] Ran code style checker: `./Tools/scripts/check_code_style.sh`
- [ ] Code compiles without warnings
- [ ] Commit messages follow ArduPilot format
- [ ] No debug print statements left in code
- [ ] No commented-out code blocks

### Documentation

- [ ] Updated relevant documentation
- [ ] Added/updated code comments for complex logic
- [ ] Updated parameter documentation if parameters added/modified
- [ ] Updated library README if applicable

## Breaking Changes

<!-- Does this PR introduce breaking changes? If yes, describe them -->

- [ ] This PR introduces breaking changes
- [ ] Migration guide provided (if breaking changes)

**Breaking changes details:**
<!-- Describe what breaks and how to migrate -->

## Performance Impact

<!-- Does this change affect performance? -->

- [ ] No performance impact
- [ ] Performance improvement (describe below)
- [ ] Performance degradation (justify below)

**Performance notes:**
<!-- Describe performance impact -->

## Flash/RAM Impact

<!-- Estimate flash and RAM impact -->

- [ ] No significant flash/RAM impact
- [ ] Flash size increase: <!-- Estimate in KB -->
- [ ] RAM usage increase: <!-- Estimate in bytes -->

## Additional Notes

<!-- Any additional information reviewers should know -->

## Review Checklist

<!-- For reviewers -->

- [ ] Code reviewed for logic errors
- [ ] Style guide followed
- [ ] Tests adequate and passing
- [ ] Documentation sufficient
- [ ] No obvious performance issues
- [ ] Breaking changes documented

---

**Author:** <!-- Your name -->
**Date:** <!-- YYYY-MM-DD -->
