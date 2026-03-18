#!/bin/bash
# ArduPilot Plane 4.5.7 Installation Script
# Target: Ubuntu 22.04 LTS (Jammy Jellyfish) (WSL2)
# Last Updated: 2026-03-17
#
# Ubuntu 22.04 (jammy) is natively supported by ArduPilot's install-prereqs-ubuntu.sh.
# No patching required. No virtual environment required.

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ARDUPILOT_TAG="Plane-4.5.7"
ARDUPILOT_COMMIT="0358a9c210bc6c965006f5d6029239b7033616df"
INSTALL_DIR="$HOME/ardupilot"

# Output functions
print_status() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}ArduPilot Plane 4.5.7 Installer${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

# Check if running in WSL
if ! grep -qi microsoft /proc/version 2>/dev/null; then
    print_warning "Not running in WSL. This script is optimized for WSL2."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
fi

# Check current directory
CURRENT_DIR=$(pwd)
if [[ $CURRENT_DIR == /mnt/c/* ]]; then
    print_error "Running from Windows filesystem (/mnt/c/)"
    print_error "Building from /mnt/c/ is SIGNIFICANTLY slower"
    print_warning "Please run from WSL home directory: cd ~"
    exit 1
fi

print_status "Running from WSL filesystem: $CURRENT_DIR"

# Step 1: Update system
echo ""
echo "Step 1: Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_status "System updated"

# Step 2: Install basic dependencies
# lsb-release is required by install-prereqs-ubuntu.sh
echo ""
echo "Step 2: Installing basic dependencies..."
sudo apt install -y git python3 python3-pip lsb-release
print_status "Basic dependencies installed"

# Step 3: Clone ArduPilot
echo ""
echo "Step 3: Checking for ArduPilot repository..."

if [ -d "$INSTALL_DIR" ]; then
    print_warning "Directory $INSTALL_DIR already exists"
    read -p "Remove and re-clone? (y/n) " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]] && rm -rf "$INSTALL_DIR"
fi

if [ ! -d "$INSTALL_DIR" ]; then
    git clone --recursive https://github.com/ArduPilot/ardupilot.git "$INSTALL_DIR"
    print_status "Repository cloned"
fi

cd "$INSTALL_DIR"
print_status "Using repository at $INSTALL_DIR"

# Step 4: Checkout Plane 4.5.7
echo ""
echo "Step 4: Checking out Plane 4.5.7..."
git fetch --tags
git checkout "$ARDUPILOT_TAG"
git submodule update --init --recursive

# Verify commit
CURRENT_COMMIT=$(git rev-parse HEAD)
if [[ $CURRENT_COMMIT == ${ARDUPILOT_COMMIT}* ]]; then
    print_status "Verified commit: $CURRENT_COMMIT"
else
    print_error "Commit mismatch! Expected: $ARDUPILOT_COMMIT, Got: $CURRENT_COMMIT"
    exit 1
fi

# Step 5: Install prerequisites
# On Ubuntu 22.04 (jammy), the ArduPilot prereqs script runs without modification.
# It natively handles: python-argparse exclusion, python3-wxgtk4.0 install, pip --user packages.
echo ""
echo "Step 5: Installing ArduPilot prerequisites..."
echo "This may take several minutes..."
./Tools/environment_install/install-prereqs-ubuntu.sh -y
print_status "Prerequisites installed"

# Reload shell profile
[ -f "$HOME/.profile" ] && . "$HOME/.profile"
[ -f "$HOME/.bashrc" ] && . "$HOME/.bashrc"

# Step 6: Install additional Python packages
# The prereqs script installs pymavlink and MAVProxy via pip --user.
# This step upgrades them to ensure the latest versions.
echo ""
echo "Step 6: Upgrading Python packages..."
python3 -m pip install --user --upgrade pymavlink mavproxy
print_status "Python packages upgraded"

# Step 7: Verify installation
echo ""
echo "Step 7: Verifying Python packages..."
python3 -c "import pymavlink; print('pymavlink:', pymavlink.__file__)"

# Verify wxPython (installed via apt by the prereqs script for jammy)
if python3 -c "import wx" 2>/dev/null; then
    print_status "wxPython accessible (required for MAVProxy console and map)"
else
    print_warning "wxPython not found - installing now..."
    sudo apt install -y python3-wxgtk4.0
fi

print_status "Packages verified"

# Step 8: Build SITL
echo ""
echo "Step 8: Building ArduPlane for SITL..."
cd "$INSTALL_DIR"
./waf configure --board sitl
./waf plane
print_status "Build completed"

# Step 9: Verify binary
echo ""
echo "Step 9: Verifying installation..."
BINARY_PATH="$INSTALL_DIR/build/sitl/bin/arduplane"
if [ ! -f "$BINARY_PATH" ]; then
    print_error "Binary not found at $BINARY_PATH"
    exit 1
fi
print_status "Binary verified: $BINARY_PATH"

# Installation complete
echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo "Installation directory:  $INSTALL_DIR"
echo "ArduPilot version:       $ARDUPILOT_TAG"
echo "Commit:                  $CURRENT_COMMIT"
echo ""
echo -e "${YELLOW}Configure Display (for GUI windows):${NC}"
echo "  WSLg (Windows 11) - No configuration needed! Already works."
echo "  XLaunch (Windows 10/11) - See setup_x_server.md"
echo ""
echo -e "${YELLOW}Test SITL:${NC}"
echo "  cd ~/ardupilot"
echo "  Tools/autotest/sim_vehicle.py -v ArduPlane --console --map"
echo ""
echo -e "${GREEN}Note: Verified working on Ubuntu 22.04 LTS (Jammy Jellyfish)${NC}"
echo ""
print_status "Happy flying!"
