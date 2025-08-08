// components/onboarding/utils/installCommands.ts

/**
 * Generates the appropriate installation command string based on the
 * detected operating system and the chosen installation method.
 *
 * @param os The detected OS ('windows', 'macos', 'linux').
 * @param method The installation method selected by the user.
 * @returns A string containing the shell command for installation.
 */
export const getInstallCommand = (os: string, method: string): string => {
    const commands: Record<string, Record<string, string>> = {
      windows: {
        installer: '# System Rebellion is currently in development\n# Windows installer will be available soon\n# For now, please use the web dashboard for system monitoring',
        manual: '# Development Preview:\n# 1. Install Python 3.8+ from python.org\n# 2. Contact support for early access agent\n# 3. Use web dashboard for monitoring until agent is ready'
      },
      macos: {
        homebrew: '# System Rebellion agent coming soon to Homebrew\n# For now, use the web dashboard for system monitoring\n# Early access available - contact support@hawkington-tech.com',
        installer: '# macOS installer in development\n# Web dashboard available now for system monitoring\n# Agent installation will be available in next release',
        manual: '# Development Preview:\n# 1. Ensure Python 3.8+ is installed\n# 2. Contact support for early access\n# 3. Use web dashboard for current monitoring'
      },
      linux: {
        apt: '# System Rebellion packages coming soon to official repositories\n# Current: Use web dashboard for monitoring\n# Early access: contact support@hawkington-tech.com',
        yum: '# RPM packages in development for RHEL/Fedora\n# Current: Use web dashboard for monitoring\n# Early access available - contact support',
        pacman: '# AUR package coming soon for Arch Linux\n# Current: Use web dashboard for monitoring\n# Early access available - contact support',
        script: '# Automated installer in development\n# Current: Use web dashboard for comprehensive monitoring\n# Early access: contact support@hawkington-tech.com'
      }
    };
  
    // Note: These are honest development-stage instructions that set proper expectations
    // and direct users to what's actually available (the web dashboard)
  
    return commands[os]?.[method] || '# System Rebellion is in active development\n# Web dashboard available now\n# Agent installation coming soon';
  };