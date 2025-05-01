#!/usr/bin/env python3
"""
System Rebellion Permission Setup Utility

This script helps set up the necessary permissions for System Rebellion
to make real-time system changes.
"""

import os
import sys
import subprocess
import getpass
from app.optimization.system_permissions import get_permission_summary, setup_permission_instructions

def print_header():
    """Print the header for the setup utility"""
    print("\n" + "=" * 80)
    print("SYSTEM REBELLION - PERMISSION SETUP UTILITY".center(80))
    print("=" * 80 + "\n")

def check_current_permissions():
    """Check and display current permission status"""
    print("Checking current permissions...\n")
    all_permissions, missing = get_permission_summary()
    
    if all_permissions:
        print("✅ All required permissions are available!")
        return True
    else:
        print("❌ Some required permissions are missing:")
        for perm in missing:
            print(f"  - {perm}")
        return False

def create_sudoers_file():
    """Create a sudoers file for System Rebellion"""
    username = getpass.getuser()
    sudoers_content = f"""# System Rebellion sudoers file
# Created by setup_permissions.py

# Allow {username} to run specific commands without password
{username} ALL=(ALL) NOPASSWD: /usr/sbin/sysctl, /usr/bin/tee, /sbin/blockdev, /usr/bin/renice
"""
    
    # Write to a temporary file
    temp_file = "/tmp/system_rebellion_sudoers"
    with open(temp_file, "w") as f:
        f.write(sudoers_content)
    
    print(f"\nCreated temporary sudoers file at {temp_file}")
    print("You will need to provide your sudo password to install it.")
    
    try:
        # Check the file with visudo
        subprocess.run(["sudo", "visudo", "-c", "-f", temp_file], check=True)
        
        # Install the file to /etc/sudoers.d/
        subprocess.run(["sudo", "install", "-m", "0440", temp_file, "/etc/sudoers.d/system_rebellion"], check=True)
        
        print("\n✅ Successfully installed sudoers file!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error installing sudoers file: {e}")
        return False
    finally:
        # Clean up temp file
        if os.path.exists(temp_file):
            os.unlink(temp_file)

def setup_group_permissions():
    """Set up group permissions for system access"""
    username = getpass.getuser()
    
    try:
        # Add user to necessary groups
        for group in ["sudo", "adm", "systemd-journal"]:
            try:
                subprocess.run(["sudo", "usermod", "-a", "-G", group, username], check=True)
                print(f"✅ Added user to {group} group")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to add user to {group} group")
        
        return True
    except Exception as e:
        print(f"❌ Error setting up group permissions: {e}")
        return False

def main():
    """Main function for the setup utility"""
    print_header()
    
    # Check current permissions
    has_permissions = check_current_permissions()
    if has_permissions:
        print("\nYour system is already properly configured for System Rebellion!")
        return 0
    
    # Ask if user wants to set up permissions
    print("\nWould you like to set up the required permissions? (y/n)")
    choice = input("> ").strip().lower()
    
    if choice != 'y':
        print("\nSetup cancelled. System Rebellion will run with limited functionality.")
        print("You can run this script again later to set up permissions.")
        return 0
    
    # Create sudoers file
    print("\n[1/2] Setting up sudo permissions...")
    sudoers_success = create_sudoers_file()
    
    # Set up group permissions
    print("\n[2/2] Setting up group permissions...")
    group_success = setup_group_permissions()
    
    # Final check
    print("\nFinal permission check:")
    final_check = check_current_permissions()
    
    if final_check:
        print("\n✅ Setup complete! System Rebellion can now make real-time system changes.")
        print("Please restart the System Rebellion backend for changes to take effect.")
        return 0
    else:
        print("\n⚠️ Some permissions could not be set up automatically.")
        print("You may need to manually configure your system.")
        print("\nManual setup instructions:")
        print(setup_permission_instructions())
        return 1

if __name__ == "__main__":
    sys.exit(main())
