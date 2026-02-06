#!/bin/bash
# MAVProxy Installation Script
# For use with ArduPilot SITL
# Last Updated: 2026-02-05

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

VENV_PATH="$HOME/.venv-ardupilot"

echo -e "${GREEN}Installing MAVProxy and dependencies...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${BLUE}Creating virtual environment at $VENV_PATH${NC}"
    python3 -m venv "$VENV_PATH"
else
    echo -e "${YELLOW}Virtual environment already exists at $VENV_PATH${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source "$VENV_PATH/bin/activate"

# Update pip in virtual environment
echo -e "${BLUE}Updating pip...${NC}"
pip install --upgrade pip

# Install MAVProxy and pymavlink
echo -e "${BLUE}Installing MAVProxy and pymavlink...${NC}"
pip install --upgrade pymavlink mavproxy

# Install optional dependencies for better functionality
echo -e "${YELLOW}Installing optional MAVProxy modules...${NC}"
pip install --upgrade \
    matplotlib \
    scipy \
    opencv-python

echo ""
echo -e "${GREEN}MAVProxy installation complete!${NC}"
echo ""
echo "Virtual environment location: $VENV_PATH"
echo ""
echo "To use MAVProxy:"
echo "  source ~/.venv-ardupilot/bin/activate"
echo "  mavproxy.py --version"
echo ""
echo "Or add auto-activation to ~/.bashrc (recommended):"
echo "  echo 'source ~/.venv-ardupilot/bin/activate' >> ~/.bashrc"
