#!/bin/bash
# MAVProxy Installation Script
# Last Updated: 2026-02-06

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
VENV_PATH="$HOME/.venv-ardupilot"

echo -e "${GREEN}Installing MAVProxy and dependencies...${NC}"

# Update pip and install packages
echo -e "${BLUE}Installing packages...${NC}"
pip install --upgrade pip pymavlink mavproxy

# Install optional dependencies
echo -e "${BLUE}Installing optional modules...${NC}"
pip install --upgrade matplotlib scipy opencv-python

# Summary
echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "Virtual environment: $VENV_PATH"
echo ""
echo "To use MAVProxy:"
echo "  source ~/.venv-ardupilot/bin/activate"
echo "  mavproxy.py --version"
echo ""
echo "For auto-activation, add to ~/.bashrc:"
echo "  # Auto-activate ArduPilot virtual environment"
echo "  # Check if venv is actually activated (not just VIRTUAL_ENV set)"
echo "  if [ -f \"\$HOME/.venv-ardupilot/bin/activate\" ]; then"
echo "      # Check if the deactivate function exists (created by activate script)"
echo "      if ! type deactivate &> /dev/null; then"
echo "          source \"\$HOME/.venv-ardupilot/bin/activate\""
echo "      fi"
echo "  fi"
