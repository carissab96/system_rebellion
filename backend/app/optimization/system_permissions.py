import os
import subprocess
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger("SystemPermissions")

def check_sudo_access() -> bool:
    """Check if the current user has sudo access without password"""
    try:
        # Try to run a simple sudo command with -n flag (non-interactive)
        result = subprocess.run(
            ["sudo", "-n", "true"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            timeout=2
        )
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error checking sudo access: {str(e)}")
        return False

def check_required_permissions() -> Dict[str, bool]:
    """Check if we have all the required permissions for system tuning"""
    permissions = {
        "sudo_access": check_sudo_access(),
        "cpu_governor": False,
        "network_buffer": False,
        "disk_read_ahead": False,
        "io_scheduler": False,
        "swap_tendency": False,
        "cache_pressure": False,
        "memory_pressure": False,
        "process_priority": True  # Non-negative nice values don't require sudo
    }
    
    # Only check detailed permissions if we have sudo access
    if permissions["sudo_access"]:
        try:
            # Check CPU governor access
            cpu_gov_path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
            permissions["cpu_governor"] = os.path.exists(cpu_gov_path) and os.access(cpu_gov_path, os.R_OK)
            
            # Check sysctl parameters
            sysctl_params = {
                "network_buffer": ["net.core.rmem_max", "net.core.wmem_max"],
                "swap_tendency": ["vm.swappiness"],
                "cache_pressure": ["vm.vfs_cache_pressure"],
                "memory_pressure": ["vm.min_free_kbytes"]
            }
            
            for param_name, sysctl_keys in sysctl_params.items():
                all_exist = True
                for key in sysctl_keys:
                    try:
                        result = subprocess.run(
                            ["sysctl", key], 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            timeout=2
                        )
                        if result.returncode != 0:
                            all_exist = False
                            break
                    except Exception:
                        all_exist = False
                        break
                permissions[param_name] = all_exist
            
            # Check disk read-ahead and I/O scheduler
            # This is simplified and assumes /dev/sda exists
            permissions["disk_read_ahead"] = os.path.exists("/dev/sda")
            permissions["io_scheduler"] = os.path.exists("/sys/block/sda/queue/scheduler")
            
        except Exception as e:
            logger.error(f"Error checking detailed permissions: {str(e)}")
    
    return permissions

def get_permission_summary() -> Tuple[bool, List[str]]:
    """Get a summary of permissions and missing requirements"""
    permissions = check_required_permissions()
    
    # Check if we have all required permissions
    all_permissions = all(permissions.values())
    
    # List missing permissions
    missing = [perm for perm, has_access in permissions.items() if not has_access]
    
    return all_permissions, missing

def setup_permission_instructions() -> str:
    """Generate instructions for setting up required permissions"""
    all_permissions, missing = get_permission_summary()
    
    if all_permissions:
        return "System has all required permissions for auto-tuning."
    
    instructions = ["# System Rebellion Permission Setup", 
                   "The following permissions are required for auto-tuning to work properly:"]
    
    if "sudo_access" in missing:
        instructions.append("""
## Sudo Access
System Rebellion needs passwordless sudo access for certain system tuning operations.
To set this up, run:

```
sudo visudo
```

And add the following line at the end (replace 'username' with your actual username):
```
username ALL=(ALL) NOPASSWD: /usr/sbin/sysctl, /usr/bin/tee, /sbin/blockdev, /usr/bin/renice
```
""")
    
    if any(x in missing for x in ["cpu_governor", "io_scheduler"]):
        instructions.append("""
## CPU and I/O Access
For CPU governor and I/O scheduler access, you need to ensure the appropriate sysfs entries are accessible.
This typically requires root access or appropriate group permissions.
""")
    
    if any(x in missing for x in ["network_buffer", "swap_tendency", "cache_pressure", "memory_pressure"]):
        instructions.append("""
## Sysctl Parameters
For modifying kernel parameters, ensure sysctl is installed and accessible:

```
sudo apt-get install procps
```
""")
    
    return "\n".join(instructions)

if __name__ == "__main__":
    # When run directly, print permission status and setup instructions
    all_permissions, missing = get_permission_summary()
    
    print(f"Permission check complete. All permissions available: {all_permissions}")
    if not all_permissions:
        print(f"Missing permissions: {', '.join(missing)}")
        print("\nSetup instructions:")
        print(setup_permission_instructions())
