#!/bin/bash
# ArduPilot Plane 4.5.7 Installation Script
# Target: Ubuntu 22.04 LTS (WSL2)
# Version: 1.0
# Last Updated: 2026-02-03

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Target version
ARDUPILOT_TAG="Plane-4.5.7"
ARDUPILOT_COMMIT="0358a9c210bc6c965006f5d6029239b7033616df"

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}ArduPilot Plane 4.5.7 Installer${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if running in WSL
if ! grep -qi microsoft /proc/version 2>/dev/null; then
    print_warning "Not running in WSL. This script is optimized for WSL2 on Windows."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check current directory
CURRENT_DIR=$(pwd)
if [[ $CURRENT_DIR == /mnt/c/* ]]; then
    print_error "You are in the Windows filesystem (/mnt/c/)"
    print_error "Building from /mnt/c/ is SIGNIFICANTLY slower"
    print_warning "Please run this script from your WSL home directory"
    echo ""
    echo "Run these commands to move to WSL filesystem:"
    echo "  cd ~"
    echo "  bash /path/to/this/script.sh"
    exit 1
fi

print_status "Running from WSL filesystem: $CURRENT_DIR"

# Step 1: Update system
echo ""
echo "Step 1: Updating system packages..."
sudo apt update
sudo apt upgrade -y
print_status "System updated"

# Step 2: Install basic dependencies
echo ""
echo "Step 2: Installing basic dependencies..."
sudo apt install -y git python3 python3-pip
print_status "Basic dependencies installed"

# Step 3: Clone ArduPilot (if not already cloned)
echo ""
echo "Step 3: Checking for ArduPilot repository..."
INSTALL_DIR="$HOME/ardupilot"

if [ -d "$INSTALL_DIR" ]; then
    print_warning "Directory $INSTALL_DIR already exists"
    read -p "Remove and re-clone? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Removing existing directory..."
        rm -rf "$INSTALL_DIR"
    else
        print_status "Using existing directory"
        cd "$INSTALL_DIR"
    fi
fi

if [ ! -d "$INSTALL_DIR" ]; then
    echo "Cloning ArduPilot repository..."
    git clone --recursive https://github.com/ArduPilot/ardupilot.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    print_status "Repository cloned"
else
    cd "$INSTALL_DIR"
    print_status "Using existing repository"
fi

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
    print_error "Commit mismatch!"
    print_error "Expected: $ARDUPILOT_COMMIT"
    print_error "Got:      $CURRENT_COMMIT"
    exit 1
fi

# Step 5: Patch install-prereqs-ubuntu.sh for Ubuntu 24.04 compatibility
echo ""
echo "Step 5: Checking for Ubuntu 24.04 compatibility issues..."
INSTALL_SCRIPT="./Tools/environment_install/install-prereqs-ubuntu.sh"

# Detect Ubuntu version
UBUNTU_CODENAME=$(lsb_release -sc 2>/dev/null || echo "unknown")
print_status "Detected Ubuntu codename: $UBUNTU_CODENAME"

# Check if python-argparse fix is needed (Ubuntu 24.04 "noble" or newer)
if [ "$UBUNTU_CODENAME" = "noble" ] || [ "$UBUNTU_CODENAME" = "oracular" ]; then
    print_warning "Ubuntu 24.04+ detected - patching install script for python-argparse compatibility"

    # Backup original script
    cp "$INSTALL_SCRIPT" "$INSTALL_SCRIPT.backup"

    # Apply patch: exclude python-argparse for noble and newer releases
    # Find the line with mantic check and add noble to the exclusion
    sed -i 's/if \[ $RELEASE_CODENAME != "mantic" \]; then/if [ $RELEASE_CODENAME != "mantic" ] \&\& [ $RELEASE_CODENAME != "noble" ] \&\& [ $RELEASE_CODENAME != "oracular" ]; then/g' "$INSTALL_SCRIPT"

    print_status "Install script patched for Ubuntu 24.04+ compatibility"
else
    print_status "No compatibility patches needed for $UBUNTU_CODENAME"
fi

# Step 6: Install prerequisites
echo ""
echo "Step 6: Installing ArduPilot prerequisites..."
echo "This may take several minutes..."
./Tools/environment_install/install-prereqs-ubuntu.sh -y
print_status "Prerequisites installed"

# Reload profile
echo ""
echo "Reloading shell profile..."
if [ -f "$HOME/.profile" ]; then
    . "$HOME/.profile"
fi
if [ -f "$HOME/.bashrc" ]; then
    . "$HOME/.bashrc"
fi
print_status "Profile reloaded"

# Step 7: Install Python packages
echo ""
echo "Step 7: Installing Python MAVLink packages..."
python3 -m pip install --user --upgrade pymavlink mavproxy
print_status "Python packages installed"

# Step 8: Build SITL
echo ""
echo "Step 8: Building ArduPlane for SITL..."
cd "$INSTALL_DIR/ArduPlane"
echo "Configuring build system..."
../waf configure --board sitl

echo "Building (this may take 5-15 minutes on first build)..."
../waf plane
print_status "Build completed successfully"

# Step 9: Verify installation
echo ""
echo "Step 9: Verifying installation..."
BINARY_PATH="$INSTALL_DIR/build/sitl/bin/arduplane"
if [ -f "$BINARY_PATH" ]; then
    print_status "Binary found: $BINARY_PATH"
else
    print_error "Binary not found at expected location!"
    exit 1
fi

# Final summary
echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo "Installation directory: $INSTALL_DIR"
echo "ArduPilot version: $ARDUPILOT_TAG"
echo "Commit: $CURRENT_COMMIT"
echo ""
echo "Next steps:"
echo "  1. Test SITL:"
echo "     cd ~/ardupilot/ArduPlane"
echo "     Tools/autotest/sim_vehicle.py -v ArduPlane --console --map"
echo ""
echo "  2. Review onboarding documentation"
echo "  3. Try example mission plans and Lua scripts"
echo ""
print_status "Happy flying!"
