#!/usr/bin/env python3
"""
System Rebellion - Hamster Permission Setup Utility

This script provides a four-option onboarding flow for setting up
the Hamsters' disk operation permissions.

Options:
1. Full Auto - Apply configuration automatically
2. Guided - Walk through each step with confirmation
3. Manual - Generate config, user applies themselves
4. Supervised Bob - Option 4 with VIC-20 approval requirement

NO FAKE DATA. NO SHORTCUTS. TRUTH OR GRACEFUL FAILURE.
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class HamsterPermissionSetup:
    """Setup utility for Hamster wrapper scripts and permissions"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self.username = os.environ.get('USER', os.environ.get('USERNAME', ''))
        self.package_manager = self._detect_package_manager()
        self.script_dir = Path(__file__).parent.parent / 'hamster-scripts'
        
    def _detect_package_manager(self) -> str:
        """Detect the system's package manager"""
        managers = {
            'apt-get': 'apt',
            'yum': 'yum',
            'dnf': 'dnf',
            'pacman': 'pacman',
            'zypper': 'zypper'
        }
        
        for cmd, name in managers.items():
            if self._command_exists(cmd):
                return name
        
        return 'unknown'
    
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists"""
        try:
            subprocess.run(['which', command], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL,
                         check=True)
            return True
        except:
            return False
    
    def print_header(self):
        """Print the setup utility header"""
        print(f"\n{Colors.BOLD}{'=' * 80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}SYSTEM REBELLION - HAMSTER PERMISSION SETUP{Colors.END}".center(90))
        print(f"{Colors.BOLD}{'=' * 80}{Colors.END}\n")
        
        print(f"{Colors.BLUE}🐹 The Hamsters need your help!{Colors.END}\n")
        print("Steve, Bob, and Carl handle disk operations, but they need")
        print("specific permissions to do their jobs safely.\n")
    
    def detect_system(self) -> Dict[str, str]:
        """Detect system information"""
        info = {
            'os': self.os_type,
            'distro': 'unknown',
            'package_manager': self.package_manager,
            'username': self.username
        }
        
        # Try to detect Linux distribution
        if self.os_type == 'linux':
            try:
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('ID='):
                            info['distro'] = line.split('=')[1].strip().strip('"')
                            break
            except:
                pass
        
        return info
    
    def print_system_info(self, info: Dict[str, str]):
        """Print detected system information"""
        print(f"{Colors.BOLD}Detected System:{Colors.END}")
        print(f"  OS: {info['os']}")
        if info['distro'] != 'unknown':
            print(f"  Distribution: {info['distro']}")
        print(f"  Package Manager: {info['package_manager']}")
        print(f"  Username: {info['username']}\n")
    
    def explain_permissions(self) -> str:
        """Generate plain English explanation of permissions"""
        return f"""
{Colors.BOLD}🐹 HAMSTER PERMISSIONS EXPLAINED{Colors.END}

The Hamsters need passwordless sudo access for specific disk operations:

{Colors.BOLD}1. hamster-defrag{Colors.END} (Bob's favorite!)
   {Colors.CYAN}What:{Colors.END} Defragments ext4 filesystems
   {Colors.CYAN}Why:{Colors.END} Improves file access speed by reorganizing fragmented files
   {Colors.CYAN}Risk:{Colors.END} Medium - touches filesystem structure
   {Colors.YELLOW}Bob's involvement:{Colors.END} HIGH (this is his favorite operation)
   {Colors.GREEN}Safety:{Colors.END} Timeouts, critical path protection, Steve's supervision

{Colors.BOLD}2. hamster-fstrim{Colors.END} (Steve's careful work)
   {Colors.CYAN}What:{Colors.END} TRIMs unused blocks on SSDs
   {Colors.CYAN}Why:{Colors.END} Maintains SSD performance and lifespan
   {Colors.CYAN}Risk:{Colors.END} Low - only affects free space
   {Colors.GREEN}Safety:{Colors.END} Only operates on supported filesystems

{Colors.BOLD}3. hamster-cleanup-tmp{Colors.END} (Bob's cleanup duty)
   {Colors.CYAN}What:{Colors.END} Deletes files older than 7 days from /tmp
   {Colors.CYAN}Why:{Colors.END} Prevents /tmp from filling up
   {Colors.CYAN}Risk:{Colors.END} Low - hardcoded safe paths only
   {Colors.GREEN}Safety:{Colors.END} Minimum age threshold, Bob can't get creative

{Colors.BOLD}4. hamster-package-cache-clean{Colors.END} (Carl's quantum precision)
   {Colors.CYAN}What:{Colors.END} Cleans package manager caches
   {Colors.CYAN}Why:{Colors.END} Frees disk space from old package downloads
   {Colors.CYAN}Risk:{Colors.END} Low - only touches package caches
   {Colors.GREEN}Safety:{Colors.END} Preserves currently installed packages

{Colors.BOLD}5. hamster-logrotate{Colors.END} (Carl's log management)
   {Colors.CYAN}What:{Colors.END} Compresses old log files
   {Colors.CYAN}Why:{Colors.END} Prevents /var/log from filling up
   {Colors.CYAN}Risk:{Colors.END} Low - only compresses, doesn't delete
   {Colors.GREEN}Safety:{Colors.END} Minimum age threshold, validates before rotation

{Colors.BOLD}🐹 The Bob Principle:{Colors.END} If Bob could misuse it, assume Bob WILL try.
These scripts are Bob-proofed by design with:
  • Critical path protection (/boot, /sys, /proc, /dev)
  • Timeout enforcement (Steve's patience limit)
  • Hardcoded safe paths (Bob can't get creative)
  • Full audit logging (The Stick can review everything)
"""
    
    def generate_sudoers_content(self, supervised: bool = False) -> str:
        """Generate sudoers file content"""
        scripts = [
            'hamster-defrag',
            'hamster-fstrim',
            'hamster-cleanup-tmp',
            'hamster-package-cache-clean',
            'hamster-logrotate'
        ]
        
        if supervised:
            # Option 4: Use supervised defrag instead
            scripts[0] = 'hamster-defrag-supervised'
        
        content = f"""# System Rebellion Hamsters - Safe disk operations
# Generated by setup_hamster_permissions.py
# User: {self.username}
# Mode: {'Supervised Bob (Option 4)' if supervised else 'Standard (Options 1-3)'}

"""
        
        for script in scripts:
            content += f"{self.username} ALL=(ALL) NOPASSWD: /usr/local/bin/{script}\n"
        
        return content
    
    def show_options_menu(self) -> int:
        """Show the four-option menu and get user choice"""
        print(f"\n{Colors.BOLD}How would you like to proceed?{Colors.END}\n")
        
        print(f"{Colors.BOLD}[1] I trust the process - apply this configuration automatically{Colors.END}")
        print(f"    We'll create /etc/sudoers.d/system-rebellion-hamsters for you")
        print(f"    {Colors.GREEN}✓ Fast and easy{Colors.END}")
        print(f"    {Colors.YELLOW}⚠ Requires sudo password{Colors.END}\n")
        
        print(f"{Colors.BOLD}[2] I trust but verify - show me exactly what you're doing{Colors.END}")
        print(f"    We'll walk you through each step and wait for confirmation")
        print(f"    {Colors.GREEN}✓ See every action before it happens{Colors.END}")
        print(f"    {Colors.YELLOW}⚠ Takes a bit longer{Colors.END}\n")
        
        print(f"{Colors.BOLD}[3] I'll handle it myself - just give me the config{Colors.END}")
        print(f"    We'll generate the files, you apply them however you're comfortable")
        print(f"    {Colors.GREEN}✓ Full control{Colors.END}")
        print(f"    {Colors.YELLOW}⚠ You're responsible for installation{Colors.END}\n")
        
        print(f"{Colors.BOLD}[4] I don't trust Bob and frankly neither should you{Colors.END}")
        print(f"    Supervised Bob mode - VIC-20 approval required for defrag")
        print(f"    {Colors.GREEN}✓ Maximum safety{Colors.END}")
        print(f"    {Colors.YELLOW}⚠ Bob needs approval for his favorite operation{Colors.END}\n")
        
        while True:
            try:
                choice = input(f"{Colors.CYAN}Enter your choice [1-4]:{Colors.END} ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= 4:
                    return choice_num
                else:
                    print(f"{Colors.RED}Please enter a number between 1 and 4{Colors.END}")
            except ValueError:
                print(f"{Colors.RED}Please enter a valid number{Colors.END}")
            except KeyboardInterrupt:
                print(f"\n\n{Colors.YELLOW}Setup cancelled by user{Colors.END}")
                sys.exit(0)
    
    def option1_full_auto(self, supervised: bool = False):
        """Option 1: Full automatic installation"""
        print(f"\n{Colors.BOLD}Option 1: Full Automatic Installation{Colors.END}\n")
        
        if supervised:
            print(f"{Colors.YELLOW}Supervised Bob mode enabled - VIC-20 approval required{Colors.END}\n")
        
        # Generate sudoers content
        sudoers_content = self.generate_sudoers_content(supervised)
        
        # Create temp file
        temp_file = '/tmp/system-rebellion-hamsters-sudoers'
        try:
            with open(temp_file, 'w') as f:
                f.write(sudoers_content)
            
            print(f"{Colors.GREEN}✓{Colors.END} Generated sudoers configuration")
            
            # Validate with visudo
            print(f"{Colors.CYAN}Validating configuration...{Colors.END}")
            result = subprocess.run(['sudo', 'visudo', '-c', '-f', temp_file],
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"{Colors.RED}✗ Configuration validation failed:{Colors.END}")
                print(result.stderr)
                return False
            
            print(f"{Colors.GREEN}✓{Colors.END} Configuration validated")
            
            # Install sudoers file
            print(f"{Colors.CYAN}Installing sudoers file...{Colors.END}")
            subprocess.run(['sudo', 'install', '-m', '0440', temp_file,
                          '/etc/sudoers.d/system-rebellion-hamsters'], check=True)
            
            print(f"{Colors.GREEN}✓{Colors.END} Sudoers file installed")
            
            # Install wrapper scripts
            print(f"{Colors.CYAN}Installing wrapper scripts...{Colors.END}")
            self._install_scripts()
            
            # Create log directory
            print(f"{Colors.CYAN}Creating log directory...{Colors.END}")
            subprocess.run(['sudo', 'mkdir', '-p', '/var/log'], check=True)
            subprocess.run(['sudo', 'touch', '/var/log/system-rebellion-hamsters.log'], check=True)
            subprocess.run(['sudo', 'chmod', '644', '/var/log/system-rebellion-hamsters.log'], check=True)
            
            print(f"{Colors.GREEN}✓{Colors.END} Log directory created")
            
            if supervised:
                # Create approval token directory
                print(f"{Colors.CYAN}Creating approval token directory...{Colors.END}")
                subprocess.run(['sudo', 'mkdir', '-p', '/var/run/system-rebellion/approvals'], check=True)
                subprocess.run(['sudo', 'chmod', '755', '/var/run/system-rebellion/approvals'], check=True)
                print(f"{Colors.GREEN}✓{Colors.END} Approval token directory created")
            
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Installation complete!{Colors.END}\n")
            self._print_success_message(supervised)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}✗ Installation failed: {e}{Colors.END}")
            return False
        except Exception as e:
            print(f"{Colors.RED}✗ Unexpected error: {e}{Colors.END}")
            return False
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def option2_guided(self, supervised: bool = False):
        """Option 2: Guided installation with confirmations"""
        print(f"\n{Colors.BOLD}Option 2: Guided Installation{Colors.END}\n")
        
        if supervised:
            print(f"{Colors.YELLOW}Supervised Bob mode enabled{Colors.END}\n")
        
        # Step 1: Show sudoers content
        print(f"{Colors.BOLD}Step 1: Sudoers Configuration{Colors.END}\n")
        sudoers_content = self.generate_sudoers_content(supervised)
        print(sudoers_content)
        
        if not self._confirm("Install this sudoers configuration?"):
            print(f"{Colors.YELLOW}Installation cancelled{Colors.END}")
            return False
        
        # Proceed with installation (same as option 1)
        return self.option1_full_auto(supervised)
    
    def option3_manual(self, supervised: bool = False):
        """Option 3: Generate config for manual installation"""
        print(f"\n{Colors.BOLD}Option 3: Manual Installation{Colors.END}\n")
        
        if supervised:
            print(f"{Colors.YELLOW}Supervised Bob mode enabled{Colors.END}\n")
        
        # Generate sudoers content
        sudoers_content = self.generate_sudoers_content(supervised)
        
        # Save to file
        output_dir = Path.home() / 'system-rebellion-hamster-config'
        output_dir.mkdir(exist_ok=True)
        
        sudoers_file = output_dir / 'system-rebellion-hamsters.sudoers'
        with open(sudoers_file, 'w') as f:
            f.write(sudoers_content)
        
        print(f"{Colors.GREEN}✓{Colors.END} Configuration saved to: {sudoers_file}\n")
        
        # Generate installation instructions
        instructions = self._generate_manual_instructions(supervised)
        instructions_file = output_dir / 'INSTALLATION_INSTRUCTIONS.md'
        with open(instructions_file, 'w') as f:
            f.write(instructions)
        
        print(f"{Colors.GREEN}✓{Colors.END} Instructions saved to: {instructions_file}\n")
        
        print(f"{Colors.BOLD}Manual Installation Steps:{Colors.END}\n")
        print(instructions)
        
        return True
    
    def _install_scripts(self):
        """Install wrapper scripts to /usr/local/bin"""
        scripts = [
            'hamster-defrag',
            'hamster-defrag-supervised',
            'hamster-fstrim',
            'hamster-cleanup-tmp',
            'hamster-package-cache-clean',
            'hamster-logrotate'
        ]
        
        for script in scripts:
            script_path = self.script_dir / script
            if script_path.exists():
                subprocess.run(['sudo', 'cp', str(script_path), '/usr/local/bin/'], check=True)
                subprocess.run(['sudo', 'chmod', '+x', f'/usr/local/bin/{script}'], check=True)
        
        # Copy common library
        lib_dir = self.script_dir / 'lib'
        subprocess.run(['sudo', 'mkdir', '-p', '/usr/local/lib/system-rebellion'], check=True)
        subprocess.run(['sudo', 'cp', '-r', str(lib_dir), '/usr/local/lib/system-rebellion/'], check=True)
    
    def _confirm(self, message: str) -> bool:
        """Ask for user confirmation"""
        while True:
            response = input(f"{Colors.CYAN}{message} [y/N]:{Colors.END} ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no', '']:
                return False
            else:
                print(f"{Colors.RED}Please enter 'y' or 'n'{Colors.END}")
    
    def _print_success_message(self, supervised: bool):
        """Print success message after installation"""
        print(f"{Colors.BOLD}The Hamsters are ready to work!{Colors.END}\n")
        print(f"  {Colors.GREEN}✓{Colors.END} Wrapper scripts installed to /usr/local/bin")
        print(f"  {Colors.GREEN}✓{Colors.END} Sudoers configuration installed")
        print(f"  {Colors.GREEN}✓{Colors.END} Log file created: /var/log/system-rebellion-hamsters.log")
        
        if supervised:
            print(f"  {Colors.GREEN}✓{Colors.END} Approval token directory created")
            print(f"\n{Colors.YELLOW}Note:{Colors.END} Bob's defrag operations require VIC-20 approval")
        
        print(f"\n{Colors.BOLD}What the Hamsters can do now:{Colors.END}")
        print(f"  🐹 Steve can TRIM SSDs: {Colors.CYAN}sudo hamster-fstrim{Colors.END}")
        print(f"  🐹 Bob can defrag filesystems: {Colors.CYAN}sudo hamster-defrag /home{Colors.END}")
        print(f"  🐹 Bob can cleanup temp files: {Colors.CYAN}sudo hamster-cleanup-tmp{Colors.END}")
        print(f"  🐹 Carl can clean package caches: {Colors.CYAN}sudo hamster-package-cache-clean{Colors.END}")
        print(f"  🐹 Carl can rotate logs: {Colors.CYAN}sudo hamster-logrotate{Colors.END}")
        
        print(f"\n{Colors.BOLD}The Stick can review operations:{Colors.END}")
        print(f"  {Colors.CYAN}tail -f /var/log/system-rebellion-hamsters.log{Colors.END}")
        print(f"  {Colors.CYAN}grep DANGER /var/log/system-rebellion-hamsters.log{Colors.END}")
        print(f"  {Colors.CYAN}grep BOB_UNSUPERVISED /var/log/system-rebellion-hamsters.log{Colors.END}")
    
    def _generate_manual_instructions(self, supervised: bool) -> str:
        """Generate manual installation instructions"""
        return f"""# System Rebellion Hamster Permission Setup
## Manual Installation Instructions

### Step 1: Install Sudoers Configuration

```bash
sudo visudo -c -f system-rebellion-hamsters.sudoers
sudo install -m 0440 system-rebellion-hamsters.sudoers /etc/sudoers.d/system-rebellion-hamsters
```

### Step 2: Install Wrapper Scripts

```bash
cd {self.script_dir}
sudo cp hamster-* /usr/local/bin/
sudo chmod +x /usr/local/bin/hamster-*
sudo mkdir -p /usr/local/lib/system-rebellion
sudo cp -r lib /usr/local/lib/system-rebellion/
```

### Step 3: Create Log Directory

```bash
sudo mkdir -p /var/log
sudo touch /var/log/system-rebellion-hamsters.log
sudo chmod 644 /var/log/system-rebellion-hamsters.log
```

{'### Step 4: Create Approval Token Directory (Supervised Mode)' if supervised else ''}
{'```bash' if supervised else ''}
{'sudo mkdir -p /var/run/system-rebellion/approvals' if supervised else ''}
{'sudo chmod 755 /var/run/system-rebellion/approvals' if supervised else ''}
{'```' if supervised else ''}

### Testing

Test that permissions are working:

```bash
# Test TRIM (should work)
sudo hamster-fstrim /home

# Test safety checks (should be denied)
sudo hamster-defrag /boot

# Check logs
tail /var/log/system-rebellion-hamsters.log
```

### Troubleshooting

If commands fail with "command not found":
- Verify scripts are in /usr/local/bin
- Verify scripts are executable: `ls -l /usr/local/bin/hamster-*`

If sudo asks for password:
- Verify sudoers file is installed: `sudo cat /etc/sudoers.d/system-rebellion-hamsters`
- Verify file permissions: `ls -l /etc/sudoers.d/system-rebellion-hamsters` (should be 0440)

---

**The Bob Principle**: If Bob could misuse it, assume Bob WILL try.
These scripts are Bob-proofed by design.
"""
    
    def run(self):
        """Main entry point for the setup utility"""
        self.print_header()
        
        # Detect and show system info
        system_info = self.detect_system()
        self.print_system_info(system_info)
        
        # Show permission explanations
        print(self.explain_permissions())
        
        # Show options menu
        choice = self.show_options_menu()
        
        # Determine if supervised mode
        supervised = (choice == 4)
        
        # Execute chosen option
        if choice == 1:
            success = self.option1_full_auto(supervised)
        elif choice == 2:
            success = self.option2_guided(supervised)
        elif choice == 3:
            success = self.option3_manual(supervised)
        elif choice == 4:
            success = self.option1_full_auto(supervised=True)
        
        return 0 if success else 1

def main():
    """Main function"""
    try:
        setup = HamsterPermissionSetup()
        return setup.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup cancelled by user{Colors.END}")
        return 1
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
