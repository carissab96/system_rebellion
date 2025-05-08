#!/bin/bash

# Colors for our distinguished output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🧐 Sir Hawkington's Distinguished Nethogs Setup${NC}"
echo -e "${BLUE}===========================================${NC}"

# Check if nethogs is installed
if ! command -v nethogs &> /dev/null; then
    echo -e "${RED}🚨 Nethogs is not installed! Installing it...${NC}"
    sudo apt-get install nethogs -y
fi

# Create sudo config for nethogs
echo -e "${CYAN}📝 Creating sudo configuration for nethogs...${NC}"

# Create the sudoers.d file for nethogs
SUDO_FILE="/etc/sudoers.d/system_rebellion_nethogs"

# Check if we're running as root, otherwise use sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${CYAN}🔑 Requesting sudo privileges to create nethogs configuration...${NC}"
    # Create the sudoers file that allows the current user to run nethogs without password
    echo "$USER ALL=(ALL) NOPASSWD: /usr/sbin/nethogs, /usr/bin/nethogs" | sudo tee $SUDO_FILE > /dev/null
    
    # Set proper permissions
    sudo chmod 440 $SUDO_FILE
else
    # Create the sudoers file that allows the current user to run nethogs without password
    echo "$USER ALL=(ALL) NOPASSWD: /usr/sbin/nethogs, /usr/bin/nethogs" > $SUDO_FILE
    
    # Set proper permissions
    chmod 440 $SUDO_FILE
fi

echo -e "${GREEN}✅ Nethogs sudo configuration complete!${NC}"
echo -e "${PURPLE}🧐 Sir Hawkington has granted you the distinguished privilege of running nethogs without a password prompt.${NC}"
echo -e "${CYAN}ℹ️  You can now run 'sudo nethogs' without being prompted for a password.${NC}"
