#!/bin/bash
# ArduPilot Plane 4.5.7 Installation Script
# Target: Ubuntu 22.04 LTS (WSL2)
# Last Updated: 2026-02-06

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
VENV_PATH="$HOME/.venv-ardupilot"
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
echo ""
echo "Step 2: Installing basic dependencies..."
sudo apt install -y git python3 python3-pip python3-venv
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

# Step 5: Create and activate virtual environment
echo ""
echo "Step 5: Setting up Python virtual environment..."

# Remove incomplete venv if found
[ -d "$VENV_PATH" ] && [ ! -f "$VENV_PATH/bin/activate" ] && rm -rf "$VENV_PATH"

# Create venv if needed
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
    print_status "Virtual environment created"
else
    print_warning "Using existing virtual environment"
fi

source "$VENV_PATH/bin/activate"
print_status "Virtual environment activated"

# Step 6: Patch install script for venv compatibility
echo ""
echo "Step 6: Patching install script for venv compatibility..."
INSTALL_SCRIPT="./Tools/environment_install/install-prereqs-ubuntu.sh"
UBUNTU_CODENAME=$(lsb_release -sc 2>/dev/null || echo "unknown")
print_status "Detected Ubuntu: $UBUNTU_CODENAME"

# Backup original
cp "$INSTALL_SCRIPT" "$INSTALL_SCRIPT.backup"

# Apply fixes
sed -i 's/python-argparse//g' "$INSTALL_SCRIPT"
sed -i 's/PIP_USER_ARGUMENT="--user"/PIP_USER_ARGUMENT=""/g' "$INSTALL_SCRIPT"
sed -i 's/pip3 install --user/pip3 install/g' "$INSTALL_SCRIPT"
sed -i 's/pip install --user/pip install/g' "$INSTALL_SCRIPT"
sed -i "s/if \[ \$RELEASE_CODENAME != \"mantic\" \]; then/if [ \$RELEASE_CODENAME != \"mantic\" ] \&\& [ \$RELEASE_CODENAME != \"noble\" ] \&\& [ \$RELEASE_CODENAME != \"$UBUNTU_CODENAME\" ]; then/g" "$INSTALL_SCRIPT"

print_status "Install script patched"

# Step 7: Install prerequisites
echo ""
echo "Step 7: Installing ArduPilot prerequisites..."
echo "This may take several minutes..."
./Tools/environment_install/install-prereqs-ubuntu.sh -y
print_status "Prerequisites installed"

# Reload shell profile
[ -f "$HOME/.profile" ] && . "$HOME/.profile"
[ -f "$HOME/.bashrc" ] && . "$HOME/.bashrc"

# Step 8: Install additional Python packages
echo ""
echo "Step 8: Installing additional Python packages..."
pip install --upgrade pip pymavlink mavproxy
print_status "Python packages installed"

# Step 9: Verify installation
echo ""
echo "Step 9: Verifying Python packages..."
python -c "import pymavlink; print('pymavlink:', pymavlink.__file__)"
print_status "Packages verified"

# Step 10: Build SITL
echo ""
echo "Step 10: Building ArduPlane for SITL..."
cd "$INSTALL_DIR"
./waf configure --board sitl
./waf plane
print_status "Build completed"

# Step 11: Verify binary
echo ""
echo "Step 11: Verifying installation..."
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
echo "Virtual environment:     $VENV_PATH"
echo ""
echo -e "${YELLOW}To use ArduPilot:${NC}"
echo "  source ~/.venv-ardupilot/bin/activate"
echo ""
echo -e "${YELLOW}For auto-activation, add to ~/.bashrc:${NC}"
echo "  # Auto-activate ArduPilot virtual environment"
echo "  # Check if venv is actually activated (not just VIRTUAL_ENV set)"
echo "  if [ -f \"\$HOME/.venv-ardupilot/bin/activate\" ]; then"
echo "      # Check if the deactivate function exists (created by activate script)"
echo "      if ! type deactivate &> /dev/null; then"
echo "          source \"\$HOME/.venv-ardupilot/bin/activate\""
echo "      fi"
echo "  fi"
echo ""
echo -e "${YELLOW}Test SITL:${NC}"
echo "  cd ~/ardupilot"
echo "  Tools/autotest/sim_vehicle.py -v ArduPlane --console --map"
echo ""
print_status "Happy flying!"
