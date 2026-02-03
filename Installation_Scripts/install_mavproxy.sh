#!/bin/bash
# MAVProxy Installation Script
# For use with ArduPilot SITL
# Last Updated: 2026-02-03

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Installing MAVProxy and dependencies...${NC}"

# Update pip
python3 -m pip install --user --upgrade pip

# Install MAVProxy and pymavlink
python3 -m pip install --user --upgrade pymavlink mavproxy

# Install optional dependencies for better functionality
echo -e "${YELLOW}Installing optional MAVProxy modules...${NC}"
python3 -m pip install --user --upgrade \
    matplotlib \
    scipy \
    opencv-python

echo -e "${GREEN}MAVProxy installation complete!${NC}"
echo ""
echo "Verify installation:"
echo "  mavproxy.py --version"
