#!/bin/bash
# ArduPilot Plane 4.5.7 Installation Script
# Target: Ubuntu 22.04 LTS (WSL2)
# Version: 1.0
# Last Updated: 2026-02-05

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Target version
ARDUPILOT_TAG="Plane-4.5.7"
ARDUPILOT_COMMIT="0358a9c210bc6c965006f5d6029239b7033616df"

# Virtual environment path
VENV_PATH="$HOME/.venv-ardupilot"

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
sudo apt install -y git python3 python3-pip python3-venv
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

# Step 5: Create and activate virtual environment
echo ""
echo "Step 5: Setting up Python virtual environment..."

# Check if venv exists and is valid
if [ -d "$VENV_PATH" ]; then
    if [ ! -f "$VENV_PATH/bin/activate" ]; then
        print_warning "Incomplete virtual environment found, removing..."
        rm -rf "$VENV_PATH"
    else
        print_warning "Virtual environment already exists at $VENV_PATH"
    fi
fi

if [ ! -d "$VENV_PATH" ]; then
    echo -e "${BLUE}Creating virtual environment at $VENV_PATH${NC}"
    python3 -m venv "$VENV_PATH"
    print_status "Virtual environment created"
fi

echo -e "${BLUE}Activating virtual environment...${NC}"
source "$VENV_PATH/bin/activate"
print_status "Virtual environment activated"

# Step 6: Patch install-prereqs-ubuntu.sh for venv compatibility
echo ""
echo "Step 6: Patching install script for virtual environment compatibility..."
INSTALL_SCRIPT="./Tools/environment_install/install-prereqs-ubuntu.sh"

# Detect Ubuntu version (for logging only)
UBUNTU_CODENAME=$(lsb_release -sc 2>/dev/null || echo "unknown")
print_status "Detected Ubuntu codename: $UBUNTU_CODENAME"

print_warning "Applying compatibility fixes..."

# Backup original script
cp "$INSTALL_SCRIPT" "$INSTALL_SCRIPT.backup"

# Fix 1: Remove python-argparse (deprecated package)
sed -i 's/python-argparse//g' "$INSTALL_SCRIPT"

# Fix 2: Remove --user flag from pip commands (conflicts with venv)
# Replace the PIP_USER_ARGUMENT variable to be empty instead of --user
sed -i 's/PIP_USER_ARGUMENT="--user"/PIP_USER_ARGUMENT=""/g' "$INSTALL_SCRIPT"
sed -i 's/PIP_USER_ARGUMENT=--user/PIP_USER_ARGUMENT=""/g' "$INSTALL_SCRIPT"
# Also catch direct --user usage
sed -i 's/pip3 install --user/pip3 install/g' "$INSTALL_SCRIPT"
sed -i 's/pip install --user/pip install/g' "$INSTALL_SCRIPT"

# Fix 3: Patch the conditional check to include current codename
sed -i "s/if \[ \$RELEASE_CODENAME != \"mantic\" \]; then/if [ \$RELEASE_CODENAME != \"mantic\" ] \&\& [ \$RELEASE_CODENAME != \"noble\" ] \&\& [ \$RELEASE_CODENAME != \"oracular\" ] \&\& [ \$RELEASE_CODENAME != \"$UBUNTU_CODENAME\" ]; then/g" "$INSTALL_SCRIPT"

print_status "Install script patched for virtual environment use"

# Step 7: Install prerequisites (Python packages will install to venv)
echo ""
echo "Step 7: Installing ArduPilot prerequisites..."
echo "This may take several minutes..."
echo -e "${BLUE}Note: Python packages will be installed to the virtual environment${NC}"
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

# Step 8: Install additional Python packages
echo ""
echo "Step 8: Installing additional Python packages..."
pip install --upgrade pip
pip install --upgrade pymavlink mavproxy
print_status "Additional Python packages installed"

# Step 9: Verify virtual environment packages
echo ""
echo "Step 9: Verifying Python packages in virtual environment..."
echo -e "${BLUE}Checking package locations:${NC}"
python -c "import pymavlink; print('pymavlink location:', pymavlink.__file__)"
print_status "Packages verified in virtual environment"

# Step 10: Build SITL
echo ""
echo "Step 10: Building ArduPlane for SITL..."
cd "$INSTALL_DIR"
echo "Configuring build system..."
./waf configure --board sitl

echo "Building (this may take 5-15 minutes on first build)..."
./waf plane
print_status "Build completed successfully"

# Step 11: Verify installation
echo ""
echo "Step 11: Verifying installation..."
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
echo "Virtual environment: $VENV_PATH"
echo ""
echo -e "${YELLOW}Important: Virtual Environment Setup${NC}"
echo "To use ArduPilot tools, activate the virtual environment:"
echo "  source ~/.venv-ardupilot/bin/activate"
echo ""
echo "For automatic activation, add to your ~/.bashrc:"
echo "  if [ -f \"\$HOME/.venv-ardupilot/bin/activate\" ] && [ -z \"\$VIRTUAL_ENV\" ]; then"
echo "      source \"\$HOME/.venv-ardupilot/bin/activate\""
echo "  fi"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment (or add auto-activation to ~/.bashrc)"
echo "  2. Test SITL:"
echo "     cd ~/ardupilot"
echo "     Tools/autotest/sim_vehicle.py -v ArduPlane --console --map"
echo ""
echo "  3. Review onboarding documentation"
echo "  4. Try example mission plans and Lua scripts"
echo ""
print_status "Happy flying!"
