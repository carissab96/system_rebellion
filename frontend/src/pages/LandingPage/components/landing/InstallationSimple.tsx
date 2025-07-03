// src/components/landing/InstallationSimple.tsx
import React, { useState } from 'react';

interface InstallCommand {
  platform: 'linux' | 'macos' | 'windows';
  name: string;
  command: string;
  description: string;
}

const installCommands: InstallCommand[] = [
  {
    platform: 'linux',
    name: 'Linux',
    command: 'curl -sSL install.hti.dev/linux | bash',
    description: 'Works on Ubuntu, CentOS, RHEL, and most distributions'
  },
  {
    platform: 'macos',
    name: 'macOS',
    command: 'brew install hti-monitoring\n# or\ncurl -sSL install.hti.dev/macos | bash',
    description: 'Homebrew or direct installation'
  },
  {
    platform: 'windows',
    name: 'Windows',
    command: 'iwr install.hti.dev/windows | iex\n# or download installer\nwinget install HTI.Monitoring',
    description: 'PowerShell or Windows Package Manager'
  }
];

export const InstallationSimple: React.FC = () => {
  const [selectedPlatform, setSelectedPlatform] = useState<'linux' | 'macos' | 'windows'>('linux');
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const command = installCommands.find(cmd => cmd.platform === selectedPlatform)?.command;
    if (command) {
      try {
        await navigator.clipboard.writeText(command);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (err) {
        console.error('Failed to copy command:', err);
      }
    }
  };

  const selectedCommand = installCommands.find(cmd => cmd.platform === selectedPlatform);

  return (
    <section id="installation" className="installation-simple">
      <div className="installation-container">
        <h2 className="installation-title">
          One Command. Immediate Intelligence.
        </h2>
        <p className="installation-subtitle">
          No complex configuration. No enterprise bullshit. Just intelligent monitoring.
        </p>
        
        <div className="platform-selector">
          {installCommands.map((cmd) => (
            <button
              key={cmd.platform}
              type="button"
              className={`platform-tab ${selectedPlatform === cmd.platform ? 'active' : ''}`}
              onClick={() => setSelectedPlatform(cmd.platform)}
            >
              {cmd.name}
            </button>
          ))}
        </div>

        <div className="installation-block">
          <div className="command-header">
            <span className="command-platform">{selectedCommand?.name}</span>
            <button
              type="button"
              className="copy-button"
              onClick={handleCopy}
              title="Copy command"
            >
              {copied ? '✓ Copied!' : '📋 Copy'}
            </button>
          </div>
          
          <div className="command-block">
            <pre className="command-text">{selectedCommand?.command}</pre>
          </div>
          
          <p className="command-description">
            {selectedCommand?.description}
          </p>
        </div>

        <div className="installation-features">
          <div className="feature-grid">
            <div className="feature-item">
              <h4>🚀 Instant Setup</h4>
              <p>Running and analyzing in under 60 seconds</p>
            </div>
            <div className="feature-item">
              <h4>🔌 Zero Configuration</h4>
              <p>Works with existing infrastructure out of the box</p>
            </div>
            <div className="feature-item">
              <h4>🧠 Immediate Intelligence</h4>
              <p>AI agents start learning your system immediately</p>
            </div>
          </div>
        </div>

        <div className="installation-note">
          <p>
            <strong>What happens next:</strong> Sir Hawkington begins system analysis, 
            Meth Snail starts optimization profiling, and the Hamsters prepare for rapid response. 
            You'll see intelligent insights within minutes, not days.
          </p>
        </div>
      </div>
    </section>
  );
};