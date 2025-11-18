#!/bin/bash
# setup-ssh-keys.sh - One-time setup for passwordless SSH
# Run this ONCE to set up SSH keys for all machines

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🔑 Setting up passwordless SSH for System Rebellion${NC}\n"

# Check if SSH key exists
if [ ! -f ~/.ssh/id_rsa ]; then
    echo -e "${YELLOW}No SSH key found. Generating new key...${NC}"
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
    echo -e "${GREEN}✅ SSH key generated${NC}\n"
else
    echo -e "${GREEN}✅ SSH key already exists${NC}\n"
fi

# Copy key to IBM ThinkPad
echo -e "${BLUE}📤 Copying SSH key to IBM ThinkPad (192.168.1.216)${NC}"
echo "You'll need to enter the password for carissa@192.168.1.216"
ssh-copy-id carissa@192.168.1.216

# Test IBM connection
echo -e "\n${BLUE}🧪 Testing IBM connection...${NC}"
if ssh -o BatchMode=yes carissa@192.168.1.216 "echo 'Success!'" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ IBM ThinkPad passwordless SSH working!${NC}\n"
else
    echo -e "${RED}❌ IBM ThinkPad passwordless SSH failed${NC}\n"
    exit 1
fi

# Copy key to HP
echo -e "${BLUE}📤 Copying SSH key to HP (192.168.1.199)${NC}"
echo "You'll need to enter the password for carissa@192.168.1.199"
ssh-copy-id carissa@192.168.1.199

# Test HP connection
echo -e "\n${BLUE}🧪 Testing HP connection...${NC}"
if ssh -o BatchMode=yes carissa@192.168.1.199 "echo 'Success!'" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ HP passwordless SSH working!${NC}\n"
else
    echo -e "${RED}❌ HP passwordless SSH failed${NC}\n"
    exit 1
fi

# Success banner
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║           🎉 SSH SETUP COMPLETE! 🎉                      ║"
echo "║                                                           ║"
echo "║   Passwordless SSH is now configured for:                ║"
echo "║   • IBM ThinkPad (192.168.1.216)                         ║"
echo "║   • HP (192.168.1.199)                                   ║"
echo "║                                                           ║"
echo "║   You can now run wake-the-misfits.sh                    ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"
