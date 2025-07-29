# system_rebellion_agent/permissions.py
import os
import platform
import subprocess
import sys
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

class SystemPermissions:
    """Handle cross-platform permission setup"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self.is_admin = self._check_admin_privileges()
        
    def _check_admin_privileges(self) -> bool:
        """Check if running with appropriate privileges"""
        if self.os_type == 'windows':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:  # Unix-like
            return os.geteuid() == 0
    
    def setup_permissions(self) -> dict:
        """Setup system permissions based on OS"""
        if self.os_type == 'windows':
            return self._setup_windows()
        elif self.os_type == 'darwin':  # macOS
            return self._setup_macos()
        elif self.os_type == 'linux':
            return self._setup_linux()
        else:
            return {'status': 'error', 'message': f'Unsupported OS: {self.os_type}'}
    
    def _setup_windows(self) -> dict:
        """Windows-specific setup"""
        try:
            # Enable WMI access
            subprocess.run(['wmic', 'process', 'where', 'name="wmiprvse.exe"', 'CALL', 'setpriority', '128'], check=True)
            
            # Set up scheduled task for agent
            task_xml = self._generate_windows_task_xml()
            task_path = Path.home() / 'SystemRebellion' / 'agent_task.xml'
            task_path.parent.mkdir(exist_ok=True)
            task_path.write_text(task_xml)
            
            subprocess.run(['schtasks', '/create', '/xml', str(task_path), '/tn', 'SystemRebellionAgent'], check=True)
            
            # Enable performance counter access
            subprocess.run(['lodctr', '/r'], check=True, shell=True)
            
            # Add firewall exception
            subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                'name="System Rebellion Agent"',
                'dir=in',
                'action=allow',
                'program=' + str(Path.home() / 'SystemRebellion' / 'agent.exe'),
                'enable=yes'
            ], check=True)
            
            return {'status': 'success', 'message': 'Windows permissions configured'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _setup_macos(self) -> dict:
        """macOS-specific setup"""
        try:
            # Create launch daemon
            plist_content = self._generate_macos_plist()
            plist_path = Path('/Library/LaunchDaemons/ai.systemrebellion.agent.plist')
            
            # Need sudo for /Library/LaunchDaemons
            with subprocess.Popen(['sudo', 'tee', str(plist_path)], 
                                stdin=subprocess.PIPE, 
                                stdout=subprocess.DEVNULL) as proc:
                proc.communicate(plist_content.encode())
            
            # Set correct permissions
            subprocess.run(['sudo', 'chmod', '644', str(plist_path)], check=True)
            subprocess.run(['sudo', 'chown', 'root:wheel', str(plist_path)], check=True)
            
            # Load the daemon
            subprocess.run(['sudo', 'launchctl', 'load', str(plist_path)], check=True)
            
            # Request accessibility permissions
            subprocess.run(['osascript', '-e', 
                'tell application "System Preferences" to reveal anchor "Privacy" of pane "com.apple.preference.security"'], 
                check=False)
            
            # Create agent directory
            agent_dir = Path.home() / 'Library' / 'SystemRebellion'
            agent_dir.mkdir(parents=True, exist_ok=True)
            
            return {'status': 'success', 'message': 'macOS permissions configured - please grant accessibility access'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _setup_linux(self) -> dict:
        """Linux-specific setup"""
        try:
            # Detect init system
            init_system = self._detect_init_system()
            
            if init_system == 'systemd':
                # Create systemd service
                service_content = self._generate_systemd_service()
                service_path = Path('/etc/systemd/system/system-rebellion-agent.service')
                
                # Write service file with sudo
                with subprocess.Popen(['sudo', 'tee', str(service_path)], 
                                    stdin=subprocess.PIPE, 
                                    stdout=subprocess.DEVNULL) as proc:
                    proc.communicate(service_content.encode())
                
                # Reload systemd and enable service
                subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
                subprocess.run(['sudo', 'systemctl', 'enable', 'system-rebellion-agent'], check=True)
                subprocess.run(['sudo', 'systemctl', 'start', 'system-rebellion-agent'], check=True)
                
            elif init_system == 'upstart':
                # Create upstart config
                upstart_content = self._generate_upstart_config()
                upstart_path = Path('/etc/init/system-rebellion-agent.conf')
                
                with subprocess.Popen(['sudo', 'tee', str(upstart_path)], 
                                    stdin=subprocess.PIPE, 
                                    stdout=subprocess.DEVNULL) as proc:
                    proc.communicate(upstart_content.encode())
                
                subprocess.run(['sudo', 'start', 'system-rebellion-agent'], check=True)
                
            else:
                # Fallback to init.d
                init_script = self._generate_init_script()
                init_path = Path('/etc/init.d/system-rebellion-agent')
                
                with subprocess.Popen(['sudo', 'tee', str(init_path)], 
                                    stdin=subprocess.PIPE, 
                                    stdout=subprocess.DEVNULL) as proc:
                    proc.communicate(init_script.encode())
                
                subprocess.run(['sudo', 'chmod', '+x', str(init_path)], check=True)
                subprocess.run(['sudo', 'update-rc.d', 'system-rebellion-agent', 'defaults'], check=True)
                subprocess.run(['sudo', 'service', 'system-rebellion-agent', 'start'], check=True)
            
            # Add user to necessary groups for hardware access
            username = os.environ.get('USER', '')
            if username:
                groups = ['disk', 'kmem', 'tty']
                for group in groups:
                    try:
                        subprocess.run(['sudo', 'usermod', '-a', '-G', group, username], check=False)
                    except:
                        pass  # Group might not exist on all distros
            
            # Create agent directory
            agent_dir = Path.home() / '.config' / 'system-rebellion'
            agent_dir.mkdir(parents=True, exist_ok=True)
            
            return {'status': 'success', 'message': f'Linux permissions configured ({init_system})'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _detect_init_system(self) -> str:
        """Detect the init system on Linux"""
        # Check for systemd
        if Path('/run/systemd/system').exists():
            return 'systemd'
        
        # Check for upstart
        if Path('/sbin/initctl').exists():
            try:
                subprocess.run(['/sbin/initctl', '--version'], 
                             capture_output=True, check=True)
                return 'upstart'
            except:
                pass
        
        # Default to sysvinit
        return 'sysvinit'
    
    def _generate_windows_task_xml(self) -> str:
        """Generate Windows Task Scheduler XML"""
        agent_path = Path.home() / 'SystemRebellion' / 'agent.exe'
        
        return f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>System Rebellion AI Agent - Persistent monitoring and optimization</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
      <Delay>PT30S</Delay>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>false</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>3</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{agent_path}</Command>
      <Arguments>--daemon</Arguments>
    </Exec>
  </Actions>
</Task>"""
    
    def _generate_macos_plist(self) -> str:
        """Generate macOS LaunchDaemon plist"""
        agent_path = Path.home() / 'Library' / 'SystemRebellion' / 'agent'
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.systemrebellion.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>{agent_path}</string>
        <string>--daemon</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
        <key>Crashed</key>
        <true/>
    </dict>
    <key>ProcessType</key>
    <string>Background</string>
    <key>Nice</key>
    <integer>10</integer>
    <key>StandardOutPath</key>
    <string>/var/log/system-rebellion-agent.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/system-rebellion-agent.error.log</string>
</dict>
</plist>"""
    
    def _generate_systemd_service(self) -> str:
        """Generate systemd service file"""
        agent_path = Path.home() / '.local' / 'bin' / 'system-rebellion-agent'
        
        return f"""[Unit]
Description=System Rebellion AI Agent
Documentation=https://systemrebellion.ai/docs
After=network.target

[Service]
Type=simple
ExecStart={agent_path} --daemon
Restart=always
RestartSec=10
User={os.environ.get('USER', 'nobody')}
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
StandardOutput=journal
StandardError=journal
SyslogIdentifier=system-rebellion

# Security settings
NoNewPrivileges=false
PrivateTmp=true
ProtectSystem=false
ProtectHome=false
ReadWritePaths=/home

[Install]
WantedBy=multi-user.target"""
    
    def _generate_upstart_config(self) -> str:
        """Generate Upstart configuration"""
        agent_path = Path.home() / '.local' / 'bin' / 'system-rebellion-agent'
        
        return f"""description "System Rebellion AI Agent"
author "Hawkington Technologies"

start on runlevel [2345]
stop on runlevel [!2345]

respawn
respawn limit 10 5

env USER={os.environ.get('USER', 'nobody')}
env HOME={Path.home()}

exec su -c "{agent_path} --daemon" $USER"""
    
    def _generate_init_script(self) -> str:
        """Generate SysV init script"""
        agent_path = Path.home() / '.local' / 'bin' / 'system-rebellion-agent'
        
        return f"""#!/bin/sh
### BEGIN INIT INFO
# Provides:          system-rebellion-agent
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: System Rebellion AI Agent
# Description:       Persistent AI monitoring and optimization agent
### END INIT INFO

DAEMON={agent_path}
NAME=system-rebellion-agent
DESC="System Rebellion AI Agent"
PIDFILE=/var/run/$NAME.pid
USER={os.environ.get('USER', 'nobody')}

. /lib/lsb/init-functions

case "$1" in
  start)
    log_daemon_msg "Starting $DESC" "$NAME"
    start-stop-daemon --start --quiet --pidfile $PIDFILE --make-pidfile \\
        --background --chuid $USER --exec $DAEMON -- --daemon
    log_end_msg $?
    ;;
  stop)
    log_daemon_msg "Stopping $DESC" "$NAME"
    start-stop-daemon --stop --quiet --pidfile $PIDFILE
    log_end_msg $?
    rm -f $PIDFILE
    ;;
  restart|force-reload)
    $0 stop
    $0 start
    ;;
  status)
    status_of_proc -p $PIDFILE "$DAEMON" "$NAME" && exit 0 || exit $?
    ;;
  *)
    echo "Usage: $0 {{start|stop|restart|force-reload|status}}" >&2
    exit 3
    ;;
esac

exit 0"""

# Convenience function for installation
# Convenience function for installation
def install_agent():
    """Main installation entry point"""
    perms = SystemPermissions()
    
    if not perms.is_admin:
        print("Administrator/root privileges required for installation.")
        print(f"Please run with: {'Administrator rights' if perms.os_type == 'windows' else 'sudo'}")
        return False
    
    print(f"Setting up System Rebellion Agent on {platform.system()}...")
    result = perms.setup_permissions()
    
    if result['status'] == 'success':
        print(f"✓ {result['message']}")
        
        # Create config file
        config_path = perms._get_config_path()
        if not config_path.exists():
            config_path.parent.mkdir(parents=True, exist_ok=True)
            default_config = {
                'agent_version': '1.0.0',
                'api_endpoint': 'https://api.systemrebellion.ai',
                'metrics_interval': 60,
                'log_level': 'INFO',
                'installed_at': datetime.now().isoformat()
            }
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
        
        print("✓ Configuration file created")
        print("\nInstallation complete! The agent will start automatically.")
        
        if perms.os_type == 'darwin':
            print("\n⚠️  IMPORTANT: Please grant accessibility permissions in System Preferences")
            print("   System Preferences → Security & Privacy → Privacy → Accessibility")
        
        return True
    else:
        print(f"✗ Installation failed: {result['message']}")
        return False

def check_permissions_status():
    """Check current permission status"""
    perms = SystemPermissions()
    status = {
        'os': platform.system(),
        'os_version': platform.version(),
        'is_admin': perms.is_admin,
        'agent_installed': False,
        'service_running': False,
        'permissions': {}
    }
    
    # Check if agent is installed
    if perms.os_type == 'windows':
        try:
            result = subprocess.run(['schtasks', '/query', '/tn', 'SystemRebellionAgent'], 
                                  capture_output=True, text=True)
            status['agent_installed'] = result.returncode == 0
            
            # Check if service is running
            result = subprocess.run(['tasklist', '/fi', 'imagename eq agent.exe'], 
                                  capture_output=True, text=True)
            status['service_running'] = 'agent.exe' in result.stdout
        except:
            pass
            
    elif perms.os_type == 'darwin':
        try:
            result = subprocess.run(['launchctl', 'list', 'ai.systemrebellion.agent'], 
                                  capture_output=True, text=True)
            status['agent_installed'] = result.returncode == 0
            status['service_running'] = 'PID' in result.stdout
        except:
            pass
            
    elif perms.os_type == 'linux':
        # Try systemd first
        try:
            result = subprocess.run(['systemctl', 'is-enabled', 'system-rebellion-agent'], 
                                  capture_output=True, text=True)
            status['agent_installed'] = result.returncode == 0
            
            result = subprocess.run(['systemctl', 'is-active', 'system-rebellion-agent'], 
                                  capture_output=True, text=True)
            status['service_running'] = result.stdout.strip() == 'active'
        except:
            # Try service command
            try:
                result = subprocess.run(['service', 'system-rebellion-agent', 'status'], 
                                      capture_output=True, text=True)
                status['agent_installed'] = 'not found' not in result.stderr
                status['service_running'] = 'running' in result.stdout.lower()
            except:
                pass
    
    # Check specific permissions
    status['permissions'] = perms._check_detailed_permissions()
    
    return status

def _get_config_path(self) -> Path:
    """Get platform-specific config path"""
    if self.os_type == 'windows':
        return Path.home() / 'AppData' / 'Roaming' / 'SystemRebellion' / 'config.json'
    elif self.os_type == 'darwin':
        return Path.home() / 'Library' / 'Application Support' / 'SystemRebellion' / 'config.json'
    else:  # Linux
        return Path.home() / '.config' / 'system-rebellion' / 'config.json'

def _check_detailed_permissions(self) -> dict:
    """Check detailed permissions for the current platform"""
    permissions = {
        'cpu_metrics': False,
        'memory_metrics': False,
        'disk_access': False,
        'network_access': False,
        'process_management': False
    }
    
    if self.os_type == 'windows':
        # Check WMI access
        try:
            import wmi
            c = wmi.WMI()
            c.Win32_Processor()
            permissions['cpu_metrics'] = True
            permissions['memory_metrics'] = True
        except:
            pass
        
        # Check disk access
        try:
            import psutil
            psutil.disk_usage('/')
            permissions['disk_access'] = True
        except:
            pass
            
    else:  # Unix-like
        # Check /proc access
        if Path('/proc/cpuinfo').exists() and os.access('/proc/cpuinfo', os.R_OK):
            permissions['cpu_metrics'] = True
        
        if Path('/proc/meminfo').exists() and os.access('/proc/meminfo', os.R_OK):
            permissions['memory_metrics'] = True
        
        # Check disk access
        try:
            import psutil
            psutil.disk_usage('/')
            permissions['disk_access'] = True
        except:
            pass
        
        # Check if can read network stats
        if Path('/proc/net/dev').exists() and os.access('/proc/net/dev', os.R_OK):
            permissions['network_access'] = True
        
        # Check process management (need root or specific capabilities)
        permissions['process_management'] = os.geteuid() == 0
    
    return permissions

def uninstall_agent():
    """Uninstall the System Rebellion agent"""
    perms = SystemPermissions()
    
    if not perms.is_admin:
        print("Administrator/root privileges required for uninstallation.")
        return False
    
    print(f"Uninstalling System Rebellion Agent from {platform.system()}...")
    
    try:
        if perms.os_type == 'windows':
            # Remove scheduled task
            subprocess.run(['schtasks', '/delete', '/tn', 'SystemRebellionAgent', '/f'], check=True)
            
            # Remove firewall rule
            subprocess.run(['netsh', 'advfirewall', 'firewall', 'delete', 'rule', 
                          'name="System Rebellion Agent"'], check=False)
            
            # Remove installation directory
            install_dir = Path.home() / 'SystemRebellion'
            if install_dir.exists():
                import shutil
                shutil.rmtree(install_dir)
                
        elif perms.os_type == 'darwin':
            # Stop and unload daemon
            subprocess.run(['sudo', 'launchctl', 'unload', 
                          '/Library/LaunchDaemons/ai.systemrebellion.agent.plist'], check=False)
            
            # Remove plist
            plist_path = Path('/Library/LaunchDaemons/ai.systemrebellion.agent.plist')
            if plist_path.exists():
                subprocess.run(['sudo', 'rm', str(plist_path)], check=True)
            
            # Remove installation directory
            install_dir = Path.home() / 'Library' / 'SystemRebellion'
            if install_dir.exists():
                import shutil
                shutil.rmtree(install_dir)
                
        elif perms.os_type == 'linux':
            # Try systemd first
            try:
                subprocess.run(['sudo', 'systemctl', 'stop', 'system-rebellion-agent'], check=False)
                subprocess.run(['sudo', 'systemctl', 'disable', 'system-rebellion-agent'], check=False)
                
                service_path = Path('/etc/systemd/system/system-rebellion-agent.service')
                if service_path.exists():
                    subprocess.run(['sudo', 'rm', str(service_path)], check=True)
                    subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            except:
                # Try init.d
                subprocess.run(['sudo', 'service', 'system-rebellion-agent', 'stop'], check=False)
                subprocess.run(['sudo', 'update-rc.d', '-f', 'system-rebellion-agent', 'remove'], check=False)
                
                init_path = Path('/etc/init.d/system-rebellion-agent')
                if init_path.exists():
                    subprocess.run(['sudo', 'rm', str(init_path)], check=True)
        
        # Remove config directory
        config_path = perms._get_config_path()
        if config_path.parent.exists():
            import shutil
            shutil.rmtree(config_path.parent)
        
        print("✓ System Rebellion Agent uninstalled successfully")
        return True
        
    except Exception as e:
        print(f"✗ Uninstallation failed: {str(e)}")
        return False

# Limited mode functions for restricted environments
class LimitedModePermissions:
    """Handle permissions for limited/restricted environments"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
        
    def setup_limited_mode(self) -> dict:
        """Setup agent in limited mode (no admin required)"""
        try:
            # Create user-local directories
            if self.os_type == 'windows':
                agent_dir = Path.home() / 'AppData' / 'Local' / 'SystemRebellion'
            else:
                agent_dir = Path.home() / '.local' / 'share' / 'system-rebellion'
            
            agent_dir.mkdir(parents=True, exist_ok=True)
            
            # Create limited config
            config = {
                'mode': 'limited',
                'capabilities': self._detect_limited_capabilities(),
                'api_endpoint': 'https://api.systemrebellion.ai',
                'metrics_interval': 300,  # Less frequent in limited mode
                'features': {
                    'read_only': True,
                    'recommendations_only': True,
                    'export_scripts': True,
                    'auto_actions': False
                }
            }
            
            config_path = agent_dir / 'config.json'
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Create user startup entry (no admin needed)
            if self.os_type == 'windows':
                self._create_windows_user_startup()
            elif self.os_type == 'darwin':
                self._create_macos_user_agent()
            else:
                self._create_linux_user_autostart()
            
            return {
                'status': 'success',
                'message': 'Limited mode configured - no admin rights required',
                'capabilities': config['capabilities']
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _detect_limited_capabilities(self) -> dict:
        """Detect what we can do without admin rights"""
        caps = {
            'cpu_usage': False,
            'memory_usage': False,
            'disk_usage': False,
            'network_stats': False,
            'process_list': False,
            'temperature': False
        }
        
        try:
            import psutil
            
            # Test each capability
            try:
                psutil.cpu_percent()
                caps['cpu_usage'] = True
            except:
                pass
                
            try:
                psutil.virtual_memory()
                caps['memory_usage'] = True
            except:
                pass
                
            try:
                psutil.disk_usage('/')
                caps['disk_usage'] = True
            except:
                pass
                
            try:
                psutil.net_io_counters()
                caps['network_stats'] = True
            except:
                pass
                
            try:
                list(psutil.process_iter(['pid', 'name']))
                caps['process_list'] = True
            except:
                pass
                
        except ImportError:
            logger.warning("psutil not available - very limited monitoring possible")
        
        return caps
    
    def _create_windows_user_startup(self):
        """Create Windows user startup entry"""
        startup_dir = Path.home() / 'AppData' / 'Roaming' / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
        
        batch_content = f"""@echo off
cd /d "{Path.home() / 'AppData' / 'Local' / 'SystemRebellion'}"
start /min python agent.py --limited-mode
"""
        
        batch_path = startup_dir / 'SystemRebellion.bat'
        batch_path.write_text(batch_content)
    
    def _create_macos_user_agent(self):
        """Create macOS user LaunchAgent"""
        agent_dir = Path.home() / 'Library' / 'LaunchAgents'
        agent_dir.mkdir(exist_ok=True)
        
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.systemrebellion.agent.limited</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{Path.home() / '.local' / 'share' / 'system-rebellion' / 'agent.py'}</string>
        <string>--limited-mode</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>"""
        
        plist_path = agent_dir / 'ai.systemrebellion.agent.limited.plist'
        plist_path.write_text(plist_content)
        
        # Load it for current user
        subprocess.run(['launchctl', 'load', str(plist_path)], check=False)
    
    def _create_linux_user_autostart(self):
        """Create Linux user autostart entry"""
        autostart_dir = Path.home() / '.config' / 'autostart'
        autostart_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_content = f"""[Desktop Entry]
Type=Application
Name=System Rebellion Agent (Limited Mode)
Comment=AI monitoring agent in limited mode
Exec={sys.executable} {Path.home() / '.local' / 'share' / 'system-rebellion' / 'agent.py'} --limited-mode
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Terminal=false
Categories=System;Monitor;"""
        
        desktop_path = autostart_dir / 'system-rebellion-limited.desktop'
        desktop_path.write_text(desktop_content)
        desktop_path.chmod(0o755)

# Main entry point
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='System Rebellion Agent Permissions Manager')
    parser.add_argument('action', choices=['install', 'uninstall', 'check', 'limited'],
                       help='Action to perform')
    parser.add_argument('--force', action='store_true',
                       help='Force operation without prompts')
    
    args = parser.parse_args()
    
    if args.action == 'install':
        success = install_agent()
        sys.exit(0 if success else 1)
        
    elif args.action == 'uninstall':
        if not args.force:
            response = input("Are you sure you want to uninstall System Rebellion Agent? [y/N]: ")
            if response.lower() != 'y':
                print("Uninstallation cancelled.")
                sys.exit(0)
        
        success = uninstall_agent()
        sys.exit(0 if success else 1)
        
    elif args.action == 'check':
        status = check_permissions_status()
        print("\nSystem Rebellion Agent Status:")
        print(f"OS: {status['os']} ({status['os_version']})")
        print(f"Admin privileges: {'Yes' if status['is_admin'] else 'No'}")
        print(f"Agent installed: {'Yes' if status['agent_installed'] else 'No'}")
        print(f"Service running: {'Yes' if status['service_running'] else 'No'}")
        
        print("\nPermissions:")
        for perm, granted in status['permissions'].items():
            print(f"  {perm}: {'✓' if granted else '✗'}")
        
    elif args.action == 'limited':
        print("Setting up System Rebellion Agent in limited mode...")
        limited = LimitedModePermissions()
        result = limited.setup_limited_mode()
        
        if result['status'] == 'success':
            print(f"✓ {result['message']}")
            print("\nAvailable capabilities in limited mode:")
            for cap, available in result['capabilities'].items():
                print(f"  {cap}: {'✓' if available else '✗'}")
        else:
            print(f"✗ Setup failed: {result['message']}")
            sys.exit(1)