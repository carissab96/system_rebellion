# System Rebellion - Distributed Wake Scripts 🚀

Orchestration scripts for starting/stopping the System Rebellion across 3 machines.

## Quick Start

### Wake the Rebellion
```bash
./wake-the-misfits.sh
```

### Shutdown the Rebellion
```bash
./shutdown-rebellion.sh
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DELL (192.168.1.127)                    │
│                   Master Control Station                    │
│                                                             │
│  • Runs wake-the-misfits.sh                                │
│  • Runs Frontend (Vite dev server)                         │
│  • Monitors all services                                    │
│  • Auto-restarts on crashes                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ SSH
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
┌──────────────────────┐                  ┌──────────────────────┐
│  IBM ThinkPad        │                  │  HP (192.168.1.199)  │
│  (192.168.1.216)     │                  │                      │
│                      │                  │  • Backend Server    │
│  • Redis Server      │                  │  • Uvicorn           │
│  • Port 6379         │                  │  • Port 8000         │
│  • Headless/TTY      │                  │  • i3 WM             │
└──────────────────────┘                  └──────────────────────┘
```

## Scripts Overview

### 1. `wake-the-misfits.sh` (Master Script)
**Run from:** Dell (192.168.1.127)

**What it does:**
- ✅ Connects to IBM → Starts Redis
- ✅ Connects to HP → Starts Backend
- ✅ Starts Frontend locally
- ✅ Monitors all services (checks every 10 seconds)
- ✅ Auto-restarts crashed services
- ✅ Beautiful status dashboard

**Usage:**
```bash
./wake-the-misfits.sh
```

**Hotkey:** `Super+Shift+W`

---

### 2. `wake-redis.sh` (IBM ThinkPad)
**Run on:** IBM ThinkPad (automatically via SSH)

**What it does:**
- Stops any existing Redis processes
- Starts Redis server
- Verifies Redis is responding
- Returns connection info

**Manual usage:**
```bash
ssh carissa@192.168.1.216 "bash /tmp/wake-redis.sh"
```

---

### 3. `wake-backend.sh` (HP)
**Run on:** HP (automatically via SSH)

**What it does:**
- Navigates to backend directory
- Activates Python venv
- Checks Redis connectivity
- Starts Uvicorn with auto-reload
- Runs on port 8000

**Manual usage:**
```bash
ssh carissa@192.168.1.199 "bash /tmp/wake-backend.sh"
```

---

### 4. `wake-frontend.sh` (Dell)
**Run on:** Dell (local)

**What it does:**
- Navigates to frontend directory
- Checks node_modules
- Starts Vite dev server
- Runs on port 5173

**Manual usage:**
```bash
./wake-frontend.sh
```

---

### 5. `shutdown-rebellion.sh` (Shutdown Script)
**Run from:** Dell (192.168.1.127)

**What it does:**
- ✅ Stops Frontend on Dell
- ✅ Stops Backend on HP
- ✅ Stops Redis on IBM
- ✅ Cleans all log files
- ✅ Removes PID files

**Usage:**
```bash
./shutdown-rebellion.sh
```

**Hotkey:** `Super+Shift+S`

---

## Features

### 🔄 Auto-Restart
If any service crashes, the monitor detects it and automatically restarts:
- **Redis** - Restarts on IBM ThinkPad
- **Backend** - Restarts on HP
- **Frontend** - Restarts on Dell

### 📊 Monitoring
Checks every 10 seconds:
- Redis ping test
- Backend health endpoint
- Frontend HTTP check

### 🧹 Log Cleanup
Logs are cleaned on shutdown to save space on IBM ThinkPad (70GB storage):
- `backend/logs/redis.log`
- `backend/logs/backend.log`
- `backend/logs/frontend.log`
- `backend/logs/master.log`

### 🎨 Beautiful Output
Color-coded status messages:
- 🔄 Blue = In progress
- ✅ Green = Success
- ⚠️ Yellow = Warning
- ❌ Red = Error

---

## Service URLs

After wake-up, access services at:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | React dev server |
| Backend | http://192.168.1.199:8000 | FastAPI server |
| API Docs | http://192.168.1.199:8000/docs | Swagger UI |
| Redis | redis://192.168.1.216:6379 | Redis server |

---

## Hotkey Setup

See [SETUP_HOTKEYS.md](./SETUP_HOTKEYS.md) for detailed instructions.

**Quick setup:**
1. Open XFCE Settings → Keyboard → Application Shortcuts
2. Add `Super+Shift+W` → `wake-the-misfits.sh`
3. Add `Super+Shift+S` → `shutdown-rebellion.sh`

---

## Troubleshooting

### Script won't run
```bash
chmod +x *.sh
```

### SSH connection fails
```bash
# Test connections
ssh carissa@192.168.1.216 "echo 'IBM OK'"
ssh carissa@192.168.1.199 "echo 'HP OK'"
```

### Service won't start
```bash
# Check logs
tail -f /home/carissab/Documents/system_rebellion/backend/logs/*.log
```

### Redis won't connect
```bash
# Test Redis from Dell
redis-cli -h 192.168.1.216 -p 6379 ping
```

### Backend won't start
```bash
# SSH to HP and check manually
ssh carissa@192.168.1.199
cd /home/carissa/Documents/system_rebellion/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Requirements

### Dell (Master)
- ✅ Passwordless SSH to IBM and HP
- ✅ xfce4-terminal
- ✅ curl
- ✅ Node.js and npm

### HP (Backend)
- ✅ Python 3.x with venv
- ✅ Uvicorn installed in venv
- ✅ curl

### IBM ThinkPad (Redis)
- ✅ Redis server installed
- ✅ Redis CLI

---

## Advanced Usage

### Run without monitoring
```bash
# Start services but don't monitor
./wake-the-misfits.sh &
# Press Ctrl+C immediately after services start
```

### Check service status manually
```bash
# Redis
ssh carissa@192.168.1.216 "redis-cli ping"

# Backend
curl http://192.168.1.199:8000/health

# Frontend
curl http://localhost:5173
```

### View logs in real-time
```bash
# All logs
tail -f backend/logs/*.log

# Specific service
tail -f backend/logs/backend.log
```

---

## Notes

- **Logs are temporary** - Cleaned on shutdown to save space
- **Auto-reload enabled** - Backend and Frontend reload on code changes
- **Safe to run multiple times** - Scripts clean up old processes first
- **Monitoring is optional** - Press Ctrl+C to stop (services keep running)

---

## File Structure

```
backend/scripts/
├── wake-the-misfits.sh      # Master orchestration script
├── wake-redis.sh            # IBM ThinkPad Redis startup
├── wake-backend.sh          # HP backend startup
├── wake-frontend.sh         # Dell frontend startup
├── shutdown-rebellion.sh    # Clean shutdown all services
├── SETUP_HOTKEYS.md         # Hotkey configuration guide
└── README.md                # This file
```

---

## Contributing

When adding new services:
1. Create a `wake-{service}.sh` script
2. Add to `wake-the-misfits.sh` main sequence
3. Add monitoring check to `monitor_services()`
4. Add shutdown to `shutdown-rebellion.sh`

---

**The Rebellion is Ready! 🚀**
