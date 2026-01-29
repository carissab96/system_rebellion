# Hamster Wrapper Scripts

Safe, auditable wrapper scripts for System Rebellion Hamster operations.

## Philosophy

**Defense in Depth**: These scripts provide permissions-level containment for the Hamsters' disk operations, complementing the agent-level supervision by Steve, VIC-20, and The Stick.

**NO FAKE DATA. NO SHORTCUTS. TRUTH OR GRACEFUL FAILURE.**

## Architecture

```
hamster-scripts/
├── lib/
│   └── hamster-common.sh       # Shared library (logging, token validation, safety checks)
├── hamster-defrag              # Unsupervised defrag (Option 1-3)
├── hamster-defrag-supervised   # VIC-20 supervised defrag (Option 4)
├── hamster-fstrim              # SSD TRIM operations
├── hamster-cleanup-tmp         # Temporary file cleanup
└── hamster-package-cache-clean # Package manager cache cleanup
```

## Scripts

### hamster-defrag
**Hamster**: Bob (his favorite!)  
**Purpose**: Defragment ext4 filesystems  
**Risk**: Medium - touches filesystem structure  
**Safety**:
- Skips critical paths (/boot, /sys, /proc, /dev)
- Enforces timeout (5-15 minutes based on size)
- Only operates on mounted ext4 filesystems
- Logs fragmentation before/after

**Usage**:
```bash
sudo hamster-defrag /home
```

### hamster-defrag-supervised
**Hamster**: Bob (under VIC-20's watchful eye)  
**Purpose**: Supervised defragmentation for Option 4 users  
**Risk**: Medium - but with approval tokens  
**Safety**:
- Requires valid VIC-20 approval token
- Token is single-use and time-limited
- All parameters validated against token
- Steve's review status checked
- Full audit trail

**Usage**:
```bash
# Called by agent with approval token in place
sudo hamster-defrag-supervised
```

### hamster-fstrim
**Hamster**: Steve (careful and methodical)  
**Purpose**: TRIM unused blocks on SSDs  
**Risk**: Low - only affects free space  
**Safety**:
- Only operates on filesystems that support TRIM
- Skips critical paths
- Can target specific mount or all supported filesystems

**Usage**:
```bash
# TRIM all supported filesystems
sudo hamster-fstrim

# TRIM specific mount
sudo hamster-fstrim /home
```

### hamster-cleanup-tmp
**Hamster**: Bob (he likes cleaning)  
**Purpose**: Remove old temporary files  
**Risk**: Low - hardcoded safe paths only  
**Safety**:
- Hardcoded paths prevent creative find usage
- Minimum age threshold (7 days)
- Only operates on: /tmp, /var/tmp, package caches

**Usage**:
```bash
# Clean files older than 7 days (default)
sudo hamster-cleanup-tmp

# Clean files older than 14 days
sudo hamster-cleanup-tmp 14
```

### hamster-package-cache-clean
**Hamster**: Carl (quantum precision)  
**Purpose**: Clean package manager caches  
**Risk**: Low - only touches package caches  
**Safety**:
- Auto-detects package manager (apt/yum/dnf/pacman/zypper)
- Preserves currently installed packages
- Logs size before/after

**Usage**:
```bash
sudo hamster-package-cache-clean
```

## Logging

All operations log to `/var/log/system-rebellion-hamsters.log` with:
- Timestamp
- Severity level (INFO, WARNING, DANGER, BOB_UNSUPERVISED, DENIED)
- Hamster attribution (STEVE, BOB, CARL, SYSTEM)
- Operation details

**Example log entries**:
```
[2026-01-29 10:25:00] [DANGER] [HAMSTER:BOB] Starting defrag on /home (timeout: 300s, Steve is watching)
[2026-01-29 10:30:00] [INFO] [HAMSTER:BOB] Defrag completed successfully on /home
[2026-01-29 10:30:00] [INFO] [HAMSTER:STEVE] Defrag effectiveness: 15.3% -> 2.1%
```

**The Stick can filter by severity**:
```bash
# See all dangerous operations
grep DANGER /var/log/system-rebellion-hamsters.log

# See when Bob was unsupervised
grep BOB_UNSUPERVISED /var/log/system-rebellion-hamsters.log

# See denied operations
grep DENIED /var/log/system-rebellion-hamsters.log
```

## VIC-20 Approval Tokens (Option 4)

For supervised mode, approval tokens are JSON files in `/var/run/system-rebellion/approvals/`:

```json
{
  "operation": "defrag",
  "mount": "/home",
  "approved_by": "vic20",
  "steve_reviewed": true,
  "max_duration": 300,
  "issued_at": "2026-01-29T10:21:00Z",
  "expires_at": "2026-01-29T10:26:00Z",
  "reason": "User reported slow file access on /home"
}
```

**Token properties**:
- Single-use (consumed after execution)
- Time-limited (5 minute expiry)
- Operation-specific (can't be reused for different operations)
- Includes Steve's review status
- Full audit trail

## Installation

These scripts are installed during System Rebellion onboarding based on the user's chosen trust level:

**Option 1**: Full auto - scripts installed automatically  
**Option 2**: Guided - user confirms each step  
**Option 3**: Manual - user installs themselves  
**Option 4**: Supervised Bob - supervised scripts used

### Manual Installation

```bash
# Make scripts executable
chmod +x hamster-*

# Install to system location
sudo cp -r hamster-scripts /usr/local/lib/system-rebellion/
sudo ln -s /usr/local/lib/system-rebellion/hamster-scripts/hamster-* /usr/local/bin/

# Create log directory
sudo mkdir -p /var/log
sudo touch /var/log/system-rebellion-hamsters.log
sudo chmod 644 /var/log/system-rebellion-hamsters.log

# Create approval token directory (for Option 4)
sudo mkdir -p /var/run/system-rebellion/approvals
sudo chmod 755 /var/run/system-rebellion/approvals
```

### Sudoers Configuration

Add to `/etc/sudoers.d/system-rebellion-hamsters`:

```bash
# System Rebellion Hamsters - Safe disk operations
# Replace <username> with actual username

<username> ALL=(ALL) NOPASSWD: /usr/local/bin/hamster-defrag
<username> ALL=(ALL) NOPASSWD: /usr/local/bin/hamster-defrag-supervised
<username> ALL=(ALL) NOPASSWD: /usr/local/bin/hamster-fstrim
<username> ALL=(ALL) NOPASSWD: /usr/local/bin/hamster-cleanup-tmp
<username> ALL=(ALL) NOPASSWD: /usr/local/bin/hamster-package-cache-clean
```

## Testing

Test scripts individually before deploying:

```bash
# Test logging (should create log entry)
sudo hamster-fstrim /home

# Check log
tail /var/log/system-rebellion-hamsters.log

# Test safety checks (should be denied)
sudo hamster-defrag /boot  # Should reject critical path

# Test supervised mode (should fail without token)
sudo hamster-defrag-supervised  # Should deny without approval token
```

## Security Considerations

🐹 **The Bob Principle**: If Bob could misuse it, assume Bob WILL try. These scripts are Bob-proofed by design.

✅ **What's Protected**:
- Critical system paths (/boot, /sys, /proc, /dev) are hardcoded as off-limits
- All operations have timeouts (no infinite runs)
- Wrapper scripts prevent argument injection attacks
- Single-use approval tokens prevent replay attacks
- Full audit trail for accountability
- Hardcoded safe paths (Bob can't get creative)
- Minimum age thresholds (Steve enforces limits)

⚠️ **What to Know**:
- Scripts run with sudo (necessary for disk operations)
- Bob's enthusiasm is contained by Steve's timeouts
- Option 4 users get VIC-20 approval requirement
- The Stick can review all operations in the log
- Defense in depth: permissions + agent logic + user choice

## Hamster Personalities

**Steve**: Careful, methodical, reviews Bob's proposals  
**Bob**: Enthusiastic, drunk, loves defrag, needs supervision  
**Carl**: Quantum precision, handles package management  

The scripts reflect their personalities while keeping operations safe.

## Support

For issues or questions:
- Check `/var/log/system-rebellion-hamsters.log` for operation details
- Verify sudoers configuration is correct
- Ensure scripts are executable (`chmod +x`)
- For Option 4 users, verify approval token directory exists

---

**Remember**: These scripts are the backup defense. The primary defense is the agent-level supervision by Steve, VIC-20, and The Stick. Defense in depth keeps Bob's enthusiasm productive and safe.
