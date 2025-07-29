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
        installer: 'Invoke-WebRequest -Uri https://systemrebellion.ai/download/windows/installer.exe -OutFile SystemRebellionInstaller.exe; .\\SystemRebellionInstaller.exe',
        manual: '# Download from: https://systemrebellion.ai/setup/windows\n# Run: Set-ExecutionPolicy RemoteSigned\n# Then: .\\setup-system-rebellion.ps1'
      },
      macos: {
        homebrew: 'brew tap hawkington/system-rebellion && brew install system-rebellion-agent && system-rebellion setup',
        installer: '# Download from: https://systemrebellion.ai/download/macos/SystemRebellion.dmg',
        manual: 'curl -sSL https://systemrebellion.ai/setup/macos | python3'
      },
      linux: {
        apt: 'sudo add-apt-repository ppa:hawkington/system-rebellion && sudo apt update && sudo apt install system-rebellion-agent',
        yum: 'sudo yum-config-manager --add-repo https://systemrebellion.ai/repo/rhel/system-rebellion.repo && sudo yum install system-rebellion-agent',
        pacman: 'yay -S system-rebellion-agent',
        script: 'curl -sSL https://systemrebellion.ai/setup/linux | sudo bash'
      }
    };
  
    // Note: I've slightly improved the original code by chaining commands with '&&' or ';'
    // for a better user experience, ensuring one step completes before the next begins.
  
    return commands[os]?.[method] || '# Instructions not available for this configuration';
  };