# HP Frontend Setup Guide

## Architecture:
- **Dell (192.168.1.127)**: Backend API + Database
- **HP**: Frontend dev server
- **ThinkPad (192.168.1.216)**: Redis

---

## Setup Steps on HP:

### 1. Clone & Checkout
```bash
cd ~/Documents
git clone git@github.com:hawkington-tech/system_rebellion.git
cd system_rebellion
git checkout distributed-mixin-implementation
git pull origin distributed-mixin-implementation
```

### 2. Install Dependencies
```bash
cd frontend
npm install
```

### 3. Configure Environment
```bash
# Copy HP-specific env file
cp .env.hp .env

# Verify Dell IP is correct (should be 192.168.1.127)
cat .env
```

### 4. Start Frontend Dev Server
```bash
npm run dev -- --host
```

This will start the frontend on: `http://[HP_IP]:5173`

### 5. Access from Any Machine
- From HP browser: `http://localhost:5173`
- From Dell browser: `http://[HP_IP]:5173`
- From any device on network: `http://[HP_IP]:5173`

---

## On Dell (Backend):

### 1. Start Backend
```bash
cd ~/Documents/system_rebellion/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**IMPORTANT**: `--host 0.0.0.0` allows HP to connect!

### 2. Verify Backend is Accessible
```bash
# From HP, test:
curl http://192.168.1.127:8000/health
```

---

## Troubleshooting:

### Frontend can't reach backend:
1. Check Dell backend is running with `--host 0.0.0.0`
2. Check firewall on Dell allows port 8000
3. Verify Dell IP: `ip addr show | grep "inet "`

### WebSocket connection fails:
1. Check `.env` has correct `VITE_WS_URL`
2. Backend must be running with `--host 0.0.0.0`
3. Check browser console for WebSocket errors

### Hot reload not working:
1. Vite config already has `host: true`
2. Try: `npm run dev -- --host 0.0.0.0`

---

## Network Layout:
```
┌─────────────────────────────────────────────┐
│  Local Network (192.168.1.x)                │
├─────────────────────────────────────────────┤
│                                             │
│  Dell (192.168.1.127)                       │
│  ├─ Backend API :8000                       │
│  ├─ PostgreSQL :5432                        │
│  └─ Agents (Sir Hawkington, VIC-20, etc)    │
│                                             │
│  HP (192.168.1.???)                         │
│  └─ Frontend Dev Server :5173               │
│                                             │
│  ThinkPad (192.168.1.216)                   │
│  └─ Redis :6379                             │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Quick Start Commands:

**On Dell:**
```bash
cd ~/Documents/system_rebellion/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**On HP:**
```bash
cd ~/Documents/system_rebellion/frontend
npm run dev -- --host
```

**Access:**
- Open browser to: `http://[HP_IP]:5173`
- Login and navigate to `/observatory`
