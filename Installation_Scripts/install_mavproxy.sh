#!/bin/bash
# MAVProxy Installation Script
# Target: Ubuntu 22.04 LTS (Jammy Jellyfish)
# Last Updated: 2026-03-17
#
# Use this script to install or upgrade MAVProxy after the main
# install_ardupilot_plane_4.5.7.sh has already run.

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}Installing MAVProxy and dependencies...${NC}"

# Update pip and install packages
echo -e "${BLUE}Installing packages...${NC}"
python3 -m pip install --user --upgrade pip pymavlink mavproxy

# Install optional dependencies
echo -e "${BLUE}Installing optional modules...${NC}"
python3 -m pip install --user --upgrade matplotlib scipy opencv-python

# Ensure wxPython is available (required for console and map modules)
if ! python3 -c "import wx" 2>/dev/null; then
    echo -e "${YELLOW}Installing wxPython via apt...${NC}"
    sudo apt install -y python3-wxgtk4.0
fi

# Summary
echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "To use MAVProxy:"
echo "  mavproxy.py --version"
echo ""
echo "To start SITL:"
echo "  cd ~/ardupilot"
echo "  Tools/autotest/sim_vehicle.py -v ArduPlane --console --map"
